# Dataset Initialization Examples

This folder is for **initializing the live THOR environment from dataset items**.
It is not just for loading JSON files.

The intended flow matches the proactive implementation idea:

1. `select_scene(scene_id)`
2. `move_object(...)` using dataset `misplaced_objects` + `object_locations`
3. `robot_setup(...)` using dataset `robot_pool` + `robot_team`

## Included datasets

- Source: `proactive/proactive/datasets/*.json`
- Local copy: `dynateamthor_api/examples/dataset_initialization/datasets/`
- Files: `dataset_s0_72.json` ... `dataset_s9_72.json`

## Main scripts

- `init_from_dataset.py`:
  - Core helpers to pick one dataset item and initialize environment from that item.
  - CLI mode supports both preview and real init.
- `example_init_from_dataset.py`:
  - End-to-end runnable example with default richer dataset item (`scene=0`, `index=59`).

## Run examples

Preview selected item metadata only:

```bash
python dynateamthor_api/examples/dataset_initialization/init_from_dataset.py --scene 0 --index 59
```

Initialize environment from selected item:

```bash
python dynateamthor_api/examples/dataset_initialization/init_from_dataset.py --scene 0 --index 59 --init-env --base-url http://127.0.0.1:1212/
```

One-command end-to-end example:

```bash
python dynateamthor_api/examples/dataset_initialization/example_init_from_dataset.py --scene 0 --index 59 --base-url http://127.0.0.1:1212/
```

## Reusable functions

You can import these from `init_from_dataset.py`:

- `select_dataset_item(scene_id, index)`
- `extract_init_payload(dataset_item)`
- `init_env_from_dataset_item(base_url, dataset_item, settle_seconds=1.0)`

Minimal code snippet:

```python
from dynateamthor_api.examples.dataset_initialization.init_from_dataset import (
    select_dataset_item,
    init_env_from_dataset_item,
)

_, _, dataset_item, _ = select_dataset_item(scene_id=0, index=59)
result = init_env_from_dataset_item("http://127.0.0.1:1212/", dataset_item, settle_seconds=1.0)
print(result)
```
