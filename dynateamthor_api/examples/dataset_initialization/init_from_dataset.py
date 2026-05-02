#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any


THIS_DIR = Path(__file__).resolve().parent
DATASETS_DIR = THIS_DIR / "datasets"
REPO_ROOT = THIS_DIR.parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def dataset_file_for_scene(scene_id: int) -> Path:
    if scene_id < 0:
        raise ValueError("scene_id must be >= 0")
    return DATASETS_DIR / f"dataset_s{scene_id}_72.json"


def load_dataset(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Expected top-level JSON list, got: {type(data).__name__}")
    return data


def load_scene_dataset(scene_id: int) -> list[dict[str, Any]]:
    return load_dataset(dataset_file_for_scene(scene_id))


def select_dataset_item(scene_id: int, index: int) -> tuple[Path, list[dict[str, Any]], dict[str, Any], int]:
    dataset_path = dataset_file_for_scene(scene_id)
    items = load_dataset(dataset_path)
    if not items:
        raise ValueError(f"Dataset has no items: {dataset_path}")
    idx = max(0, min(index, len(items) - 1))
    return dataset_path, items, items[idx], idx


def extract_init_payload(dataset_item: dict[str, Any]) -> dict[str, Any]:
    robot_pool = dataset_item.get("robot_pool", {})
    robot_team = dataset_item.get("robot_team", [])
    misplaced_objects = dataset_item.get("misplaced_objects", [])
    object_locations = dataset_item.get("object_locations", [])

    selected_robots = {}
    for name in robot_team:
        if name in robot_pool:
            selected_robots[name] = robot_pool[name]

    move_payload = {}
    pair_count = min(len(misplaced_objects), len(object_locations))
    for i in range(pair_count):
        move_payload[misplaced_objects[i]] = object_locations[i]

    return {
        "scene_id": int(dataset_item.get("scene_index", 0)),
        "robot_pool": robot_pool,
        "robot_team": robot_team,
        "selected_robots": selected_robots,
        "misplaced_objects": misplaced_objects,
        "object_locations": object_locations,
        "move_payload": move_payload,
    }


def init_env_from_dataset_item(
    base_url: str,
    dataset_item: dict[str, Any],
    settle_seconds: float = 1.0,
    scene_reset_first: bool = False,
) -> dict[str, Any]:
    from dynateamthor_api.helpers.api_client import ApiClient

    payload = extract_init_payload(dataset_item)
    client = ApiClient(base_url=base_url, timeout=45)

    scene_id = payload["scene_id"]
    selected_robots = payload["selected_robots"]
    move_payload = payload["move_payload"]

    if scene_reset_first:
        client.scene_reset()
        time.sleep(0.5)

    select_ret = client.select_scene(scene_id)
    if settle_seconds > 0:
        time.sleep(settle_seconds)

    moved_ok = 0
    moved_fail = 0
    move_errors: dict[str, str] = {}
    if move_payload:
        try:
            batch_ret = client.move_object(move_payload)
            if batch_ret.get("is_success") is True:
                moved_ok = len(move_payload)
            else:
                raise RuntimeError(str(batch_ret))
        except Exception:
            for obj_name, obj_payload in move_payload.items():
                try:
                    ret = client.move_object({obj_name: obj_payload})
                    if ret.get("is_success") is True:
                        moved_ok += 1
                    else:
                        moved_fail += 1
                        move_errors[obj_name] = str(ret.get("error_info", "Unknown"))
                except Exception as e:
                    moved_fail += 1
                    move_errors[obj_name] = str(e)

    setup_ret = client.robot_setup(selected_robots) if selected_robots else {"success": False, "message": "Empty robot team"}
    return {
        "scene_id": scene_id,
        "select_scene": select_ret,
        "robot_setup": setup_ret,
        "robot_count": len(selected_robots),
        "object_count": len(move_payload),
        "moved_ok": moved_ok,
        "moved_fail": moved_fail,
        "move_errors": move_errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize THOR environment from one dataset item.")
    parser.add_argument("--scene", type=int, default=0, help="Scene id for dataset file name.")
    parser.add_argument("--index", type=int, default=0, help="Record index in dataset file.")
    parser.add_argument("--base-url", default="http://127.0.0.1:1212/", help="THOR HTTP base URL.")
    parser.add_argument("--init-env", action="store_true", help="Apply selected dataset item to environment.")
    parser.add_argument("--settle-seconds", type=float, default=1.0, help="Wait time after select_scene.")
    args = parser.parse_args()

    dataset_path, items, dataset_item, idx = select_dataset_item(args.scene, args.index)
    payload = extract_init_payload(dataset_item)

    print(f"dataset_path: {dataset_path}")
    print(f"item_count: {len(items)}")
    print(f"selected_item_index: {idx}")
    print(f"scene_id: {payload['scene_id']}")
    print(f"robot_team_count: {len(payload['robot_team'])}")
    print(f"object_pair_count: {len(payload['move_payload'])}")

    if args.init_env:
        result = init_env_from_dataset_item(args.base_url, dataset_item, args.settle_seconds)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
