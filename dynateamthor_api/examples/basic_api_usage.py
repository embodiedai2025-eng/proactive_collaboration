#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Minimal example: connect to DynaTeamTHOR, select a scene, set up one robot,
then query object and robot information.
"""

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dynateamthor_api.helpers.api_client import ApiClient


ROBOT_SETUP = {
    "robot_0": {
        "type": "ManipulaTHOR",
        "name": "Robot_0",
        "init_location": [-3.216, 0.90, -3.064],
        "init_rotation": [0, -90, 0],
        "strength": 80,
    }
}


def print_json(title: str, data: dict) -> None:
    print(f"\n[{title}]")
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Minimal DynaTeamTHOR HTTP API usage example.")
    parser.add_argument("--base-url", default="http://127.0.0.1:1212/")
    parser.add_argument("--scene-id", type=int, default=0)
    parser.add_argument("--timeout", type=int, default=20)
    args = parser.parse_args()

    client = ApiClient(args.base_url, timeout=args.timeout)

    print_json("select_scene", client.select_scene(args.scene_id))
    print_json("robot_setup", client.robot_setup(ROBOT_SETUP))
    print_json("get_object_info", client.get_object_info(["Robot_0", "Bed_01", "Pillow_01"]))
    print_json("robot_status", client.get_robot_status(["Robot_0"]))
    print_json("get_obs", client.get_obs(["Robot_0"]))


if __name__ == "__main__":
    main()
