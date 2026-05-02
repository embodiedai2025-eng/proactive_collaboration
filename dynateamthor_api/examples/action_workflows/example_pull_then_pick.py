#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example: move blockers first, then pick and place target object.

This script intentionally uses only lightweight helpers and direct HTTP API wrappers.
It does NOT depend on utilities/env.py.
"""

import argparse
import json
import os
import sys
import time
from copy import deepcopy

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from dynateamthor_api.helpers.api_client import ApiClient
from dynateamthor_api.helpers.navigation import goto_object


SETUP_PAYLOAD = {
    "robot_0": {
        "type": "ManipulaTHOR",
        "name": "Robot_0",
        "init_location": [-3.216, 0.90, -3.064],
        "init_rotation": [0, -90, 0],
        "strength": 80,
    },
    "robot_1": {
        "type": "ManipulaTHOR",
        "name": "Robot_1",
        "init_location": [-3.216, 0.90, -1.609],
        "init_rotation": [0, -90, 0],
        "strength": 80,
    },
}

PILLOW_INIT_PAYLOAD = {
    "Pillow_01": {
        "init_location": [-5.914, 0.7, -2.5],
        "init_rotation": [0.0, 90.0, 0.0],
    }
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Pull-then-pick demo without Env framework.")
    parser.add_argument("--base-url", default="http://127.0.0.1:1212/")
    parser.add_argument("--scene-id", type=int, default=0)
    parser.add_argument("--target-name", default="Pillow_01", help="Object to pick after pulling blocker.")
    parser.add_argument("--receiver-name", default="Bed_01", help="Where to place target object.")
    parser.add_argument("--moveable-object-name", default="Bed_01", help="Object to jointly pull.")
    parser.add_argument(
        "--pull-direction",
        default="(1,0,0)",
        help='Hardcoded pull direction string, e.g. "(0,0,-1)".',
    )
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument(
        "--sleep-between",
        type=float,
        default=1.0,
        metavar="SEC",
        help="Sleep time in seconds between major steps for clearer visualization.",
    )
    args = parser.parse_args()
    sleep_between = max(0.0, args.sleep_between)

    client = ApiClient(args.base_url, timeout=args.timeout)

    print(f"[1] select_scene -> {args.scene_id}")
    print(client.select_scene(args.scene_id))
    time.sleep(sleep_between)

    print("[2] robot_setup")
    print(client.robot_setup(deepcopy(SETUP_PAYLOAD)))
    time.sleep(sleep_between)

    print("[3] move_object -> reset Pillow_01 init pose")
    print(client.move_object(deepcopy(PILLOW_INIT_PAYLOAD)))
    time.sleep(sleep_between)

    print("[4] goto blocker with both robots")
    print("  Robot_0:", goto_object(client, "Robot_0", args.moveable_object_name))
    print("  Robot_1:", goto_object(client, "Robot_1", args.moveable_object_name))
    time.sleep(sleep_between)

    print(f"[5] joint_pull {args.moveable_object_name} direction={args.pull_direction}")
    pull_resp = client.joint_pull(["Robot_0", "Robot_1"], args.moveable_object_name, args.pull_direction)
    print(json.dumps(pull_resp, ensure_ascii=False, indent=2))
    time.sleep(sleep_between)

    print(f"[6] goto target object {args.target_name} with Robot_0")
    print(goto_object(client, "Robot_0", args.target_name))
    time.sleep(sleep_between)

    print(f"[7] pick {args.target_name}")
    pick_resp = client.pick("Robot_0", args.target_name)
    print(json.dumps(pick_resp, ensure_ascii=False, indent=2))
    time.sleep(sleep_between)

    print(f"[8] goto receiver {args.receiver_name}")
    goto_receiver = goto_object(client, "Robot_0", args.receiver_name)
    print(goto_receiver)
    time.sleep(sleep_between)

    print(f"[9] place onto {args.receiver_name}")
    info = client.get_object_type([args.receiver_name]).get("data", {})
    put_points_key = args.receiver_name + "PutPoints"
    if put_points_key in info and info[put_points_key]:
        # Minimal parser for first put point: "(x, y, z) ; ..."
        first_point = info[put_points_key].split(";")[0].strip()
        xyz = [float(x.strip()) for x in first_point.strip("()").split(",")]
        place_resp = client.place("Robot_0", args.target_name, xyz, [0, 0, 0])
        print(json.dumps(place_resp, ensure_ascii=False, indent=2))
    else:
        print("No PutPoints found; skip place call.")


if __name__ == "__main__":
    main()
