# Examples

- `basic_api_usage.py`: minimal scene setup and query flow for first-time users.
- `dataset_initialization/`: initialize a live scene from proactive-style dataset items.
- `action_workflows/example_pull_then_pick.py`: multi-step pull, pick, and place workflow using reusable helpers.

Run from the parent directory:

```bash
python dynateamthor_api/examples/basic_api_usage.py --base-url http://127.0.0.1:1212/
python dynateamthor_api/examples/action_workflows/example_pull_then_pick.py --base-url http://127.0.0.1:1212/
python dynateamthor_api/examples/dataset_initialization/init_from_dataset.py --scene 0 --index 59 --init-env --base-url http://127.0.0.1:1212/
```
