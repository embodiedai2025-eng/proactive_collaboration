# Helpers (Lightweight Reusable Modules)

This folder contains small, reusable helpers extracted from `utilities` and adapted to work
without depending on the full `utilities/env.py` architecture.

## Modules

- `api_client.py`
  - Minimal HTTP client wrappers for common endpoints.
- `parsers.py`
  - `parse_coordinates_from_string`
  - `parse_reachable_points`
  - `parse_relations`
  - `relation_to_str`
  - `get_2d_distance`
- `spatial.py`
  - `is_point_in_quadrilateral`
  - `get_nearest_edge_point`
  - `obs_get_nearest_edge_point_list`
  - `turn_to_target`
- `navigation.py`
  - `goto_point`
  - `goto_object`
  - `goto_room` (requires caller-provided `room_anchor_map`)
- `examples/action_workflows/example_pull_then_pick.py`
  - End-to-end usage example that only depends on these helper modules (run from repo root; see top-level `README.md`).

## Design scope

- Keep utilities easy to copy/reuse.
- Avoid planner/team-scheduler/full framework dependencies.
- Return compact results (`ok`, `reason`, `detail`) for navigation helpers.
