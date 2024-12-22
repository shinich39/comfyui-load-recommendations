"use strict";

import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

const NODE_TYPE = "ViewRecommendations";
const MIN_LABEL_LENGTH = 10;
const KEYS = [
  ["seed",      `${"Seed".padEnd(MIN_LABEL_LENGTH, " ")}: `],
  ["steps",     `${"Steps".padEnd(MIN_LABEL_LENGTH, " ")}: `],
  ["cfg",       `${"CFG scale".padEnd(MIN_LABEL_LENGTH, " ")}: `],
  ["sampler",   `${"Sampler".padEnd(MIN_LABEL_LENGTH, " ")}: `],
  ["scheduler", `${"Scheduler".padEnd(MIN_LABEL_LENGTH, " ")}: `],
  ["strength",  `${"Denoising strength".padEnd(MIN_LABEL_LENGTH, " ")}: `],
  ["pp",        `\n${"Positive prompt".padEnd(MIN_LABEL_LENGTH, " ")}:\n`],
  ["np",        `\n${"Negative prompt".padEnd(MIN_LABEL_LENGTH, " ")}:\n`],
];

const CKPT_TYPES = [
  "CheckpointLoaderSimple",
  "Load Checkpoint",
  "CheckpointLoader|pysssss",
  "Checkpoint Loader", // WAS
];

let loadedData;

async function load() {
  const response = await api.fetchApi(`/shinich39/comfyui-view-recommendations/load`, {
    method: "GET",
    headers: { "Content-Type": "application/json", },
  });

  if (response.status !== 200) {
    throw new Error(response.statusText);
  }

  const d = await response.json();

  return d;
}

function findData(ckptName) {
  const filename = ckptName.split(".").slice(0, ckptName.split(".").length - 1).join(".");
  if (!loadedData) {
    return;
  }

  const versionData = loadedData.data.find((d) => d.filenames.indexOf(filename) > -1);
  if (!versionData) {
    return;
  }

  return versionData;
}

function getCkptNodes() {
  let nodes = [];
  for (const node of app.graph._nodes) {
    if (node.type === "SimpleCheckpoint") {
      nodes.push(node);
    }
  }
  return nodes;
}

function createNote(str, x, y) {
  let newNode = LiteGraph.createNode("Note");
  newNode.pos = [x, y];
  newNode.size = [512, 384];
  newNode.widgets[0].value = str;
  app.canvas.graph.add(newNode, false);
  app.canvas.selectNode(newNode);
  return newNode;
}

app.registerExtension({
	name: `shinich39.${NODE_TYPE}`,
  setup() {
    load().then((res) => loadedData = res);
  },
  async beforeRegisterNodeDef(nodeType, nodeData, app) {
		const isCkpt = CKPT_TYPES.indexOf(nodeType.comfyClass) > -1;
    if (isCkpt) {
      const origGetExtraMenuOptions = nodeType.prototype.getExtraMenuOptions;
      nodeType.prototype.getExtraMenuOptions = function (_, options) {
        const r = origGetExtraMenuOptions ? origGetExtraMenuOptions.apply(this, arguments) : undefined;

        try {
          const ckptWidget = this.widgets.find((w) => w.name == "ckpt_name");
          if (!ckptWidget) {
            return r;
          }
  
          const ckptName = ckptWidget.value;
          const data = findData(ckptName);
          const dataLen = data?.metadata.length || 0;
          const metadata = data?.metadata || [];

          let optionIndex = options.findIndex((o) => o?.content === "Properties");
          if (optionIndex > -1) {
            let newOptions = [
              {
                content: "View Recommendations",
                disabled: dataLen == 0,
                submenu: {
                  options: metadata.map((d, i) => {
                    return {
                      content: `${i}`,
                      callback: () => {
                        let str = "";
                        str += `${"URL".padEnd(MIN_LABEL_LENGTH, " ")}: https://civitai.com/models/${data.modelId}?modelVersionId=${data.versionId}\n`;
                        str += `${"Model".padEnd(MIN_LABEL_LENGTH, " ")}: ${data.modelName}\n`;
                        str += `${"Version".padEnd(MIN_LABEL_LENGTH, " ")}: ${data.versionName}\n`;
                        str += `${"Updated".padEnd(MIN_LABEL_LENGTH, " ")}: ${new Date(data.updatedAt).toISOString().split('T')[0]}\n`;

                        if (d.w && d.h) {
                          str += `${"Size".padEnd(MIN_LABEL_LENGTH, " ")}: ${d.w}x${d.h}\n`;
                        }

                        for (const [key, label] of KEYS) {
                          if (d[key]) {
                            str += `${label}${d[key]}\n`;
                          }
                        }
                        
                        createNote(str, this.pos[0] + this.size[0] + 16, this.pos[1]);
                      }
                    }
                  })
                }
              }
            ];
            
            options.splice(
              optionIndex,
              0,
              ...newOptions
            );
          }
        } catch(err) {
          console.error(err);
        }

        return r;
      } 
    }
	},
});