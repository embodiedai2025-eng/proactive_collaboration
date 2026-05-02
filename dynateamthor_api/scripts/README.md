# Scripts

- `check_http_api.py`: end-to-end HTTP API connectivity check and payload template printer.

Run from the repository root:

```bash
python dynateamthor_api/scripts/check_http_api.py --base-url http://127.0.0.1:1212/
```

## Saved images (`obs_captures`)

Unless you pass **`--no-save-obs`**, the checker **writes PNG files** next to this folder:

`dynateamthor_api/scripts/obs_captures/`

That includes **`get_obs`** RGB (and depth when returned) and **`get_topdown_image`** RGB from the configured scene sweep. With **`--no-save-obs`**, nothing is written here (normal if you want a quick connectivity pass without artifacts).

## Related flags (see `--help`)

| Flag | Purpose |
|------|---------|
| `--no-save-obs` | Do not decode/write PNGs under `obs_captures/`. |
| `--timeout SEC` | Per-request timeout (raise if Unity is slow). |
| `--print-payloads` | Print built-in JSON payload templates and exit. |
| `--no-obs-extended` | Only single-robot RGBD check, not multi-robot + multi-angle. |
| `--topdown-current-only` | One top-down capture for the loaded scene (no `select_scene` sweep). |
| `--topdown-scenes SPEC` | Which scene ids to sweep (default `0-9`). |
| `--topdown-settle SEC` | Wait after each `select_scene` before top-down capture. |
