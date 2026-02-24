#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/8/14 16:15
# @Author  : dby
# @File    : ue_api.py
# @Software: PyCharm
# import os
# os.environ['NO_PROXY'] = '127.0.0.1,localhost'

import base64
import pprint
import time
from io import BytesIO

import cv2
import matplotlib.pyplot as plt
import numpy as np
import requests

# import torch
from flask import Flask, jsonify, request
from PIL import Image
import json

from tenacity import retry, stop_after_attempt, wait_random_exponential

app = Flask(__name__)

# REMOTE_URL must be set via set_remote_url() function before use
REMOTE_URL = None

HEADERS = {"Content-Type": "application/json"}
INFO_DATA = {"ID": -1, "ImageSize": [-1, -1]}

def set_remote_url(remote_url):
    """Set the REMOTE_URL for API calls.
    
    This function sets REMOTE_URL in all possible module instances to handle
    different import paths (unity.ue_api vs robot_skill_sets.unity.ue_api).
    """
    import sys
    global REMOTE_URL
    
    if remote_url is None:
        raise ValueError("remote_url cannot be None")
    
    # Set in current module (preserve original URL format)
    REMOTE_URL = remote_url
    
    # Also set in all possible module instances (handle different import paths)
    module_names = [
        'unity.ue_api',
        'robot_skill_sets.unity.ue_api',
    ]
    
    for module_name in module_names:
        if module_name in sys.modules:
            module = sys.modules[module_name]
            if hasattr(module, 'REMOTE_URL'):
                module.REMOTE_URL = remote_url
    
    # Verify it was set correctly
    if REMOTE_URL is None:
        raise RuntimeError("Failed to set REMOTE_URL")

def _check_remote_url():
    """Check if REMOTE_URL is set, raise error if not.
    
    This function checks REMOTE_URL in the current module and all possible
    module instances to handle different import paths.
    """
    import sys
    global REMOTE_URL
    
    # Check current module first
    if REMOTE_URL is not None:
        return
    
    # Check all possible module instances
    module_names = [
        'unity.ue_api',
        'robot_skill_sets.unity.ue_api',
    ]
    
    for module_name in module_names:
        if module_name in sys.modules:
            module = sys.modules[module_name]
            if hasattr(module, 'REMOTE_URL') and module.REMOTE_URL is not None:
                # Sync to current module
                REMOTE_URL = module.REMOTE_URL
                return
    
    # If still None, raise error
    raise ValueError(
        "REMOTE_URL is not set. Please call set_remote_url() first. "
        "This should be done in init_config() before creating the Env object."
    )
# RGB_DATA = {
#     "ID": -1,
#     "ImageSize": [300, 300]
# }
# GATE_INIT_DICT = {"x": -469, "y": 673, "z": 168}
# AGENTS_NAME = ["BP_Player_C_1", "BP_Dogbot_C_1", "BP_Soldier_C_0", "BP_Soldier_C_1"]

@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(5))
def select_scene(contant = 5,suffix="v1/env/select_scene"):
    _check_remote_url()
    if REMOTE_URL.endswith('/'):
        remote_url = REMOTE_URL + suffix
    else:
        remote_url = REMOTE_URL + '/' + suffix
    scene_id = int(contant) if isinstance(contant, (str, float)) else contant
    json_data = {
        "scene_id": scene_id
    }
    with requests.post(remote_url, json=json_data, headers=HEADERS, timeout=20) as response:
        if response.status_code >= 400:
            error_msg = f"HTTP {response.status_code} error from {remote_url}"
            try:
                error_response = response.json()
                error_msg += f"\nResponse: {error_response}"
            except (json.JSONDecodeError, ValueError):
                error_msg += f"\nResponse text: {response.text[:500]}"
            error_msg += f"\nRequest JSON: {json_data}"
            raise requests.exceptions.HTTPError(error_msg, response=response)
        
        if not response.text:
            raise ValueError(f"Empty response from {remote_url}. Status code: {response.status_code}")
        try:
            return response.json()
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON response from {remote_url}. "
                f"Status code: {response.status_code}, "
                f"Response text: {response.text[:200]}, "
                f"Error: {str(e)}"
            ) from e


@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(5))
def scene_reset(suffix="v1/env/scene_reset"):
    _check_remote_url()
    remote_url = REMOTE_URL + suffix
    json_data = {
    }   
    with requests.post(remote_url, json=json_data, headers=HEADERS, timeout=20) as response:
        response.raise_for_status()
        if not response.text:
            raise ValueError(f"Empty response from {remote_url}. Status code: {response.status_code}")
        try:
            return response.json()
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON response from {remote_url}. "
                f"Status code: {response.status_code}, "
                f"Response text: {response.text[:200]}, "
                f"Error: {str(e)}"
            ) from e

setup = {
    "robot_0": {
        "type": "LoCoBot",
        "name": "Robot_0",
        "init_location": [-5.9592, 0.90, -0.201],
        "init_rotation": [0, 180, 0],
        "arm_length":1,
        "robot_high":0.5,
        "robot_low": 0.2,
        "strength":80
    },
    "robot_1": {
        "type": "ManipulaTHOR",
        "name": "Robot_1",
        "init_location": [-3.216, 0.90,-3.064],
        "init_rotation": [0, -90, 0]
    },
    "robot_2": {
        "type": "ManipulaTHOR",
        "name": "Robot_2",
        "init_location": [-3.216, 0.90, -1.609],
        "init_rotation": [0, -90, 0]
    }
    
}

@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(5))
def robot_setup(contant=setup, suffix="v1/env/robot_setup"):
    _check_remote_url()
    remote_url = REMOTE_URL + suffix
    json = contant
    with requests.post(remote_url, json=json, headers=HEADERS, timeout=20) as response:
        return response.json()


teleport = {
    "robot_1":
    {
         "location": [0.712,0.882,0.316],
         "rotation": [0,-90,0]
     },
    "robot_0":
    {
         "location": [2.94,1.25,0.82],
         "rotation": [0,-90,0]
     },
    "Hum":
    {
        "init_location": [4.374, 0.90, 0],
        "init_rotation": [0, 0, 0]
    }
}

@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(5))
def robot_teleport(contant = teleport, suffix="v1/agent/robot_teleport"):
    _check_remote_url()
    remote_url = REMOTE_URL + suffix
    json = contant
    with requests.post(remote_url, json=json, headers=HEADERS, timeout=20) as response:
        return response.json()
    

moveApple = {
     "apple_0":
    {
         "init_location":[5 ,1.2,-4.3],
         "init_rotation" : [0,0,0]
    },
    "Hum":
    {
         "init_location":[0.4 ,0.92, -0.02],
         "init_rotation" : [0,0,0]
    }
}

@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(5))
def move_object(contant=moveApple, suffix = "v1/env/move_object"):
    _check_remote_url()
    remote_url = REMOTE_URL + suffix
    json = contant
    with requests.post(remote_url, json=json, headers=HEADERS, timeout=20) as response:
        return response.json()

getApple = {
    "object_list":["fridge_16","Robot_0"]
}

@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(5))
def get_object_info(contant = getApple, suffix = "v1/info/get_object_info"):
    _check_remote_url()
    remote_url = REMOTE_URL + suffix
    json = contant
    with requests.post(remote_url, json=json, headers=HEADERS, timeout=20) as response:
        return response.json()

stepsize = {
    "step_size": 0.1
}
@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(5))
def get_reachable_points(contant = stepsize, suffix = "v1/info/get_reachable_points"):
    _check_remote_url()
    remote_url = REMOTE_URL + suffix
    json = contant
    with requests.post(remote_url, json=json, headers=HEADERS, timeout=20) as response:
        return response.json()

robotPickup = {
        "Robot_0":
        {
            "object_name": "pillow_11",
        }
    }

@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(5))
def pick_up(contant = robotPickup, suffix = "v1/agent/pick"):
    _check_remote_url()
    remote_url = REMOTE_URL + suffix
    json = contant
    with requests.post(remote_url, json=json, headers=HEADERS, timeout=20) as response:
        return response.json()

robot_list = {
    "robot_list":["Robot_1"]
}
@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(5))
def get_robot_obs(contant = robot_list, suffix = "v1/env/get_obs"):
    _check_remote_url()
    remote_url = REMOTE_URL + suffix
    json = contant
    with requests.post(remote_url, json=json, headers=HEADERS, timeout=20) as response:
        return response.json()

getNeighbor = {
    "object_list":["Pillow_11","Pillow_02","AlarmClock_01"]
}
@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(5))
def get_object_neighbors(contant = getNeighbor, suffix = "v1/info/get_object_neighbors"):
    _check_remote_url()
    remote_url = REMOTE_URL + suffix
    json = contant
    with requests.post(remote_url, json=json, headers=HEADERS, timeout=20) as response:
        return response.json()


getRobotStatus = {
    "robot_list":["Robot_1","Robot_0","Robot_2"]
}
@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(5))
def get_robot_status(contant = getRobotStatus, suffix = "v1/info/robot_status"):
    _check_remote_url()
    remote_url = REMOTE_URL + suffix
    json = contant
    with requests.post(remote_url, json=json, headers=HEADERS, timeout=20) as response:
        return response.json()


getObjectType = {
    "object_list":["Toilet_01","Bed_01","AlarmClock_01"]
}
@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(5))
def get_object_type(contant = getObjectType, suffix = "v1/info/object_type"):
    _check_remote_url()
    remote_url = REMOTE_URL + suffix
    json = contant
    with requests.post(remote_url, json=json, headers=HEADERS, timeout=20) as response:
        return response.json()
    

placeLocatioin =   {
        "Robot_0":
        {
            "object_name": "Pillow_11",
            "target_location": [-4.59, 0.91, -2.4],
            "target_rotation": [0,0,0]
        }
    }
@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(5))
def place_object(contant = placeLocatioin, suffix = "v1/agent/place"):
    _check_remote_url()
    remote_url = REMOTE_URL + suffix
    json = contant
    with requests.post(remote_url, json=json, headers=HEADERS, timeout=20) as response:
        return response.json()


pullInfos = {
  "robot_list": ["Robot_1", "Robot_2"],
  "object_name": "Bed_01",
  "direction": "(1,0,0)"
}
@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(5))
def pull_object(contant = pullInfos, suffix = "v1/agent/joint_pull"):
    _check_remote_url()
    remote_url = REMOTE_URL + suffix
    json = contant
    with requests.post(remote_url, json=json, headers=HEADERS, timeout=20) as response:
        return response.json()
    

if __name__ == '__main__':
    # obs = get_robot_obs()
    # pprint.pprint(obs)
    # # time.sleep(1)
    # # scene_reset()
    # time.sleep(2)
    
    # # robot_teleport()
    # # robot_comm()
    # move_object()
    # locations = get_object_info()
    # pick_up()
    # pprint.pprint(locations)
    # get_robot_status()
    pprint.pprint(get_object_neighbors())
    

  