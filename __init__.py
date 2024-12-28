"""
@author: shinich39
@title: view-recommendations
@nickname: view-recommendations
@version: 1.0.0
@description: Load model generation data from civitai
"""

import os
import json
import traceback
import requests

from server import PromptServer
from aiohttp import web

WEB_DIRECTORY = "./js"
__DIRNAME = os.path.dirname(os.path.abspath(__file__))
CKPT_DATA_PATH = os.path.join(__DIRNAME, "ckpt_latest.json")
CKPT_REPO_URL = "https://github.com/shinich39/civitai-checkpoint-json"
CKPT_DATA_URL = "https://raw.githubusercontent.com/shinich39/civitai-checkpoint-json/refs/heads/main/dist/latest.json"
CKPT_INFO_URL = "https://raw.githubusercontent.com/shinich39/civitai-checkpoint-json/refs/heads/main/dist/info.json"
LORA_DATA_PATH = os.path.join(__DIRNAME, "lora_latest.json")
LORA_REPO_URL = "https://github.com/shinich39/civitai-lora-json"
LORA_DATA_URL = "https://raw.githubusercontent.com/shinich39/civitai-lora-json/refs/heads/main/dist/latest.json"
LORA_INFO_URL = "https://raw.githubusercontent.com/shinich39/civitai-lora-json/refs/heads/main/dist/info.json"
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

def get_ckpt_json():
  data = {}
  # Read data
  if os.path.exists(CKPT_DATA_PATH) == False:
    # print(f"[comfyui-view-recommendations] ckpt_latest.json not found")
    with open(CKPT_DATA_PATH, "w") as f:
      f.write(json.dumps(data, indent=2))
      f.close()
  else:
    # print(f"[comfyui-view-recommendations] Read previous latest.json ")
    with open(CKPT_DATA_PATH, "r") as file:
      data = json.load(file)

  # Check updatedAt
  prev_time = None
  if "updatedAt" in data:
    prev_time = data["updatedAt"]

  # print(f"[comfyui-view-recommendations] {prev_time}")

  # Download data
  try:
    info_res = requests.get(CKPT_INFO_URL)
    info_data = json.loads(info_res.text)
    next_time = info_data["updatedAt"]
    if prev_time == None or prev_time != next_time:
      print(f"[comfyui-view-recommendations] new civitai-checkpoint-json update found. {prev_time} != {next_time}")
      print(f"[comfyui-view-recommendations] Downloading ckpt_latest.json...")

      # Update
      next_res = requests.get(CKPT_DATA_URL)
      next_data = json.loads(next_res .text)
      
      # print(f"[comfyui-view-recommendations] {next_data}")
      
      with open(CKPT_DATA_PATH, "w+") as f:
        f.write(json.dumps(next_data))
        f.close()

      data = next_data
    else:
      # print(f"[comfyui-view-recommendations] civitai-checkpoint-json not updated yet")
      pass
  except Exception:
    print(f"Failed to connect to {CKPT_INFO_URL}")

  return data

def get_lora_json():
  data = {}
  # Read data
  if os.path.exists(LORA_DATA_PATH) == False:
    # print(f"[comfyui-view-recommendations] lora_latest.json not found")
    with open(LORA_DATA_PATH, "w") as f:
      f.write(json.dumps(data, indent=2))
      f.close()
  else:
    # print(f"[comfyui-view-recommendations] Read previous latest.json ")
    with open(LORA_DATA_PATH, "r") as file:
      data = json.load(file)

  # Check updatedAt
  prev_time = None
  if "updatedAt" in data:
    prev_time = data["updatedAt"]

  # print(f"[comfyui-view-recommendations] {prev_time}")

  # Download data
  try:
    info_res = requests.get(LORA_INFO_URL)
    info_data = json.loads(info_res.text)
    next_time = info_data["updatedAt"]
    if prev_time == None or prev_time != next_time:
      print(f"[comfyui-view-recommendations] new civitai-lora-json update found. {prev_time} != {next_time}")
      print(f"[comfyui-view-recommendations] Downloading lora_latest.json...")

      # Update
      next_res = requests.get(LORA_DATA_URL)
      next_data = json.loads(next_res .text)
      
      # print(f"[comfyui-view-recommendations] {next_data}")
      
      with open(LORA_DATA_PATH, "w+") as f:
        f.write(json.dumps(next_data))
        f.close()

      data = next_data
    else:
      # print(f"[comfyui-view-recommendations] civitai-lora-json not updated yet")
      pass
  except Exception:
    print(f"Failed to connect to {LORA_INFO_URL}")

  return data

@PromptServer.instance.routes.get("/shinich39/comfyui-view-recommendations/load")
async def load(request):
  try:
    res = {
      "ckpt": get_ckpt_json(),
      "lora": get_lora_json(),
    }

    return web.json_response(res)
  except Exception:
    print(traceback.format_exc())
    return web.Response(status=400)

