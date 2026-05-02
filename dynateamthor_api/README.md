# DynaTeamTHOR User-Friendly HTTP API Kit

This standalone folder is the **user-friendly HTTP API kit** for the updated DynaTeamTHOR build.
It focuses on practical usage: docs, connectivity checks, reusable helpers, and runnable examples.

The major user-friendly change is runtime listener configuration (URL/port) instead of script edits + repackaging for every endpoint test cycle.

## Folder map

- `docs/`
  - `http_api_reference.md`: complete HTTP endpoint reference, including the runtime listener URL/port configuration notes.
- `scripts/`
  - `check_http_api.py`: connectivity check, payload printer, RGB/depth/top-down capture validation.
  - `scripts/obs_captures/`: PNG output from `check_http_api.py` when saving is enabled (created on first write; see below).
- `helpers/`
  - Lightweight reusable modules: API client, parsers, spatial helpers, and navigation helpers.
- `examples/`
  - `basic_api_usage.py`: minimal scene setup and query flow.
  - `action_workflows/`: complete action workflows such as pull, pick, and place.
  - `dataset_initialization/`: initialize a live THOR scene from dataset records.

## Quick start

Run full HTTP connectivity check:

```bash
python dynateamthor_api/scripts/check_http_api.py --base-url http://127.0.0.1:1212/
```

By default, **`check_http_api.py` decodes and writes PNG snapshots** from `get_obs` (RGB, and depth when the server returns it) and from `get_topdown_image` under:

`dynateamthor_api/scripts/obs_captures/`

Use **`--no-save-obs`** to skip writing those files (faster runs, no images on disk—this is why the folder may stay empty). Increase **`--timeout`** if Unity is slow to respond. Other useful flags: **`--print-payloads`** (dump JSON templates and exit), **`--no-obs-extended`** (lighter RGBD sweep), **`--topdown-current-only`** / **`--topdown-scenes`** (control the top-down scene sweep). Run **`--help`** on the script for the full list.

Initialize environment from one dataset item:

```bash
python dynateamthor_api/examples/dataset_initialization/init_from_dataset.py --scene 0 --index 59 --init-env --base-url http://127.0.0.1:1212/
```

Run minimal API usage example:

```bash
python dynateamthor_api/examples/basic_api_usage.py --base-url http://127.0.0.1:1212/
```

Run action workflow example (no `utilities/env.py` dependency):

```bash
python dynateamthor_api/examples/action_workflows/example_pull_then_pick.py --base-url http://127.0.0.1:1212/
```

## Runtime listener configuration

The new DynaTeamTHOR user-friendly version resolves the HTTP listener URL in two different ways:

- **Graphical builds** (`Windows` / `macOS` / desktop `Linux`): a startup window asks for the full listener URL (or default). There is no fixed port in this Python kit—always match `--base-url` to what you confirm in that window.
- **Headless / server builds** (`Application.isBatchMode`): there is no UI. Configure the listener via `--http-url`, `--http-port`, `THOR_HTTP_URL`, or `THOR_HTTP_PORT` on the simulator process (see the parent bundle’s `../README.md` for details and examples).

For the full v1.2 distribution layout and platform folders, read **`../README.md`** next to this folder.

Use the same base URL in every command, for example:

```bash
--base-url http://127.0.0.1:1212/
```

The URL must include `http://` and should end with `/`.

## Standalone note

This folder does not depend on the old `utilities/env.py` framework. Keep the folder next to your working directory, run commands from its parent directory, and point `--base-url` to the listener URL you configured (startup dialog on graphical builds, or CLI/env on headless builds—see the parent bundle’s `../README.md`).
