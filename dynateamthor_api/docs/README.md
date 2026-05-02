# Documentation

This folder contains the user-facing documentation for the standalone DynaTeamTHOR user-friendly HTTP API kit.

## Reading Path

1. Start with [`../README.md`](../README.md) for the package layout and common commands.
2. Read [`http_api_reference.md`](http_api_reference.md) sections 2-5 to understand listener configuration, URL rules, client calls, and response schemas.
3. Use section 6 of [`http_api_reference.md`](http_api_reference.md) as the endpoint-by-endpoint reference.
4. Use sections 7-10 when validating connectivity, debugging errors, or checking implementation details.

## Main Document

- [`http_api_reference.md`](http_api_reference.md)
  - Runtime HTTP listener URL/port configuration.
  - Request/response conventions.
  - All routes covered by `scripts/check_http_api.py`.
  - Connectivity test commands and payload notes.
  - Error catalog and implementation notes from the Unity source.

## Endpoint Quick Index

| Area | Endpoint |
|---|---|
| Environment setup | `POST /v1/env/select_scene` |
| Environment setup | `POST /v1/env/scene_reset` |
| Robot setup | `POST /v1/env/robot_setup` |
| Robot motion | `POST /v1/agent/robot_teleport` |
| Object placement | `POST /v1/env/move_object` |
| Object info | `POST /v1/info/get_object_info` |
| Navigation support | `POST /v1/info/get_reachable_points` |
| Manipulation | `POST /v1/agent/pick` |
| Manipulation | `POST /v1/agent/place` |
| Manipulation | `POST /v1/agent/joint_pull` |
| Observation | `POST /v1/env/get_obs` |
| Observation | `POST /v1/env/get_topdown_image` |
| Scene relations | `POST /v1/info/get_object_neighbors` |
| Robot info | `POST /v1/info/robot_status` |
| Object metadata | `POST /v1/info/object_type` (missing scene objects are omitted from `data`; see §6.13 / §10.5 in `http_api_reference.md`) |

## Useful Commands

Print request payload templates:

```bash
python dynateamthor_api/scripts/check_http_api.py --print-payloads
```

Run the connectivity suite:

```bash
python dynateamthor_api/scripts/check_http_api.py --base-url http://127.0.0.1:1212/ --timeout 15
```
