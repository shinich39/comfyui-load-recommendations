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
DATA_PATH = os.path.join(__DIRNAME, "latest.json")
REPO_URL = "https://github.com/shinich39/civitai-metadata-json"
DATA_URL = "https://raw.githubusercontent.com/shinich39/civitai-metadata-json/refs/heads/main/dist/latest.json"
INFO_URL = "https://raw.githubusercontent.com/shinich39/civitai-metadata-json/refs/heads/main/dist/info.json"
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

@PromptServer.instance.routes.get("/shinich39/comfyui-view-recommendations/load")
async def load(request):
  try:
    data = {}

    # Read data
    if os.path.exists(DATA_PATH) == False:
      # print(f"[comfyui-view-recommendations] latest.json not found")
      with open(DATA_PATH, "w") as f:
        f.write(json.dumps(data, indent=2))
        f.close()
    else:
      # print(f"[comfyui-view-recommendations] Read previous latest.json ")
      with open(DATA_PATH, "r") as file:
        data = json.load(file)

    # Check updatedAt
    prev_time = None
    if "updatedAt" in data:
      prev_time = data["updatedAt"]

    # print(f"[comfyui-view-recommendations] {prev_time}")

    # Download data
    try:
      info_res = requests.get(INFO_URL)
      info_data = json.loads(info_res.text)
      next_time = info_data["updatedAt"]
      if prev_time == None or prev_time != next_time:
        print(f"[comfyui-view-recommendations] new civitai-metadata-json update found. {prev_time} != {next_time}")
        print(f"[comfyui-view-recommendations] Downloading new metadata...")

        # Update
        next_res = requests.get(DATA_URL)
        next_data = json.loads(next_res .text)
        
        # print(f"[comfyui-view-recommendations] {next_data}")
        
        with open(DATA_PATH, "w+") as f:
          f.write(json.dumps(next_data))
          f.close()

        data = next_data
      else:
        # print(f"[comfyui-view-recommendations] civitai-metadata-json not updated yet")
        pass
    except Exception:
      print(f"Failed to connect to {INFO_URL}")
  
    return web.json_response(data)
  except Exception:
    print(traceback.format_exc())
    return web.Response(status=400)

