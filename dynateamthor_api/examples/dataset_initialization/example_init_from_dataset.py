#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json

try:
    from .init_from_dataset import extract_init_payload, init_env_from_dataset_item, select_dataset_item
except ImportError:
    from init_from_dataset import extract_init_payload, init_env_from_dataset_item, select_dataset_item



def main() -> None:
    parser = argparse.ArgumentParser(
        description="Example: initialize environment from one dataset item "
        "(proactive-style: select_scene -> move_object -> robot_setup)."
    )
    parser.add_argument("--scene", type=int, default=0, help="Dataset file scene id.")
    parser.add_argument("--index", type=int, default=59, help="Item index in dataset (default picks a richer sample).")
    parser.add_argument("--base-url", default="http://127.0.0.1:1212/", help="THOR HTTP base URL.")
    parser.add_argument("--settle-seconds", type=float, default=1.0, help="Wait time after select_scene.")
    args = parser.parse_args()

    dataset_path, items, dataset_item, idx = select_dataset_item(args.scene, args.index)
    payload = extract_init_payload(dataset_item)

    print(f"[example] dataset_path={dataset_path}")
    print(f"[example] item_count={len(items)}")
    print(f"[example] selected_item_index={idx}")
    print(f"[example] scene_id={payload['scene_id']}")
    print(f"[example] robot_team={payload['robot_team']}")
    print(f"[example] misplaced_objects={payload['misplaced_objects']}")

    result = init_env_from_dataset_item(
        base_url=args.base_url,
        dataset_item=dataset_item,
        settle_seconds=args.settle_seconds,
    )
    print("[example] init_result:")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
