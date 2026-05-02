# DynaTeamTHOR HTTP API Reference

This document is a **source-derived**, implementation-level API reference for the HTTP routes currently covered by:

- `scripts/check_http_api.py`

Primary source files used to compile this document:

- `ControllerCoreCode/GameInitializer.cs`
- `ControllerCoreCode/RestfulApiManagement.cs`
- `ControllerCoreCode/ObjectController.cs`

The goal here is clarity **without dropping any details**. It is written for the user-friendly DynaTeamTHOR build where the HTTP listener URL/port can be configured at runtime.

---

## How to use this reference

- For listener URL/port setup, read sections 2-3.
- For client request conventions and response schemas, read sections 4-5.
- For endpoint request/response details, use section 6.
- For connectivity validation commands, use section 7.
- For debugging and source-level behavior, use appendices A-B.

## Endpoint groups

| Group | Routes |
|---|---|
| Environment | `/v1/env/select_scene`, `/v1/env/scene_reset`, `/v1/env/robot_setup`, `/v1/env/move_object` |
| Agent actions | `/v1/agent/robot_teleport`, `/v1/agent/pick`, `/v1/agent/place`, `/v1/agent/joint_pull` |
| Observation | `/v1/env/get_obs`, `/v1/env/get_topdown_image` |
| Information | `/v1/info/get_object_info`, `/v1/info/get_reachable_points`, `/v1/info/get_object_neighbors`, `/v1/info/robot_status`, `/v1/info/object_type` |

---

## Table of contents

0. [How to use this reference](#how-to-use-this-reference)
0. [Endpoint groups](#endpoint-groups)
1. [Scope and how to read this doc](#1-scope-and-how-to-read-this-doc)
2. [Server startup and communication window](#2-server-startup-and-communication-window)
3. [URL rules and listener behavior](#3-url-rules-and-listener-behavior)
4. [Client call conventions](#4-client-call-conventions)
5. [Response conventions and status codes](#5-response-conventions-and-status-codes)
6. [Endpoint reference (test-covered routes)](#6-endpoint-reference-test-covered-routes)
7. [Testing utilities and payload templates](#7-testing-utilities-and-payload-templates)
8. [Out of scope](#8-out-of-scope)
9. [Appendix A: Error catalog from source](#9-appendix-a-error-catalog-from-source)
10. [Appendix B: Deep implementation notes](#10-appendix-b-deep-implementation-notes)

---

## 1. Scope and how to read this doc

### 1.1 Included

This reference includes routes invoked by `scripts/check_http_api.py`:

- `POST /v1/env/robot_setup`
- `POST /v1/agent/robot_teleport`
- `POST /v1/env/move_object`
- `POST /v1/info/get_object_info`
- `POST /v1/info/get_reachable_points`
- `POST /v1/agent/pick`
- `POST /v1/agent/place`
- `POST /v1/agent/joint_pull`
- `POST /v1/env/get_obs`
- `POST /v1/env/get_topdown_image`
- `POST /v1/info/get_object_neighbors`
- `POST /v1/info/robot_status`
- `POST /v1/info/object_type`
- `POST /v1/env/select_scene`
- `POST /v1/env/scene_reset`

### 1.2 Notation used

- **Request JSON**: structural shape expected by server code.
- **Success response (shape)**: stable keys observed from implementation.
- **Error behavior**: messages emitted by code (`throw`, catch-serialization, and inline error keys).
- `error_info: "Null"` and `message: "null"` are **literal strings**, not JSON null.

### 1.3 Important compatibility note

This codebase mixes two success schemas:

- `success` + `message`
- `is_success` + `error_info`

Clients should handle both.

---

## 2. Server startup and communication window

Server startup is controlled by `GameInitializer`.

### 2.1 Runtime URL configuration UI (the communication window)

If inspector field `inputUrlFromWindow` is enabled and URL is not configured yet, Unity shows an `OnGUI` window:

- Title: **HTTP Listener URL**
- Prompt: **Input URL (must include http:// and trailing /):**
- Text field for URL input
- Buttons:
  - **Start**: validate + start listener
  - **Use Default**: reset text field to `defaultUrl`
- Error line appears under buttons when validation/start fails (`startupError`)

### 2.2 Relevant inspector/runtime fields

| Field | Meaning |
|---|---|
| `inputUrlFromWindow` | Show startup URL window vs auto-start from default |
| `defaultUrl` | Default listener URL (example `http://127.0.0.1:1212/`) |
| `stopListenerAfterSceneChange` | If true, select/reset scene handlers may stop+close listener |
| `configuredUrl` / `urlConfigured` | Internal state for persisted URL in current session |

### 2.3 Startup flow

1. `Awake()` enforces singleton (`DontDestroyOnLoad`).
2. If URL already configured and listener not listening: `StartHttpListener(configuredUrl)`.
3. In batch/headless mode, resolve URL from command-line args, environment variables, then `defaultUrl`.
4. Else if `inputUrlFromWindow` is true: show window and wait for `Start`.
5. Else normalize `defaultUrl`; if valid, start listener.
6. On success: `listener.Prefixes.Add(url)`, `listener.Start()`, then async accept loop (`HandleIncomingConnections()`).

### 2.4 Headless/runtime URL priority

In `Application.isBatchMode`, URL resolution order is:

| Priority | Source | Example |
|---|---|---|
| 1 | `--http-url` | `--http-url http://127.0.0.1:1212/` |
| 2 | `--http-port` | `--http-port 1212` |
| 3 | `THOR_HTTP_URL` | `THOR_HTTP_URL=http://127.0.0.1:1212/` |
| 4 | `THOR_HTTP_PORT` | `THOR_HTTP_PORT=1212` |
| 5 | `defaultUrl` inspector value | `http://127.0.0.1:1212/` |

`--http-url` and `--http-port` accept both `--key=value` and `--key value` forms. Port values must be in `1-65535`. When a port is provided without a URL, the runtime builds `http://0.0.0.0:{port}/`, which is useful for headless/container deployments.

### 2.5 Lifecycle

- `OnApplicationQuit()` stops/closes listener.
- Duplicate `GameInitializer` instances are destroyed.

---

## 3. URL rules and listener behavior

URL normalization (`TryNormalizeListenerUrl`) enforces:

1. URL must be non-empty.
2. URL must start with `http://`.
3. URL is forced to end with `/`.
4. URI must parse as absolute `http` URI.

### 3.1 Typical startup errors

| Message | Cause |
|---|---|
| `URL cannot be empty.` | Blank input |
| `Only http:// URL is supported by HttpListener in this setup.` | Wrong scheme prefix |
| `Invalid URL format.` | URI parse failure |
| `Only http scheme is supported.` | Non-http scheme |
| `Failed to start HttpListener: ...` | Port conflict, permission, bind issue |

### 3.2 Prefix and path composition

If base URL is `http://127.0.0.1:1212/`, full route is:

- `http://127.0.0.1:1212/v1/...`

No extra slash insertion is needed if base already has trailing slash.

---

## 4. Client call conventions

### 4.1 HTTP method and headers

- Method: `POST`
- Header: `Content-Type: application/json`

Most request parsers in `RestfulApiManagement` check `request.ContentType == "application/json"` exactly. To avoid avoidable failures, send exactly `Content-Type: application/json` rather than variants such as `application/json; charset=utf-8`.

### 4.1.1 Route matching

`GameInitializer` routes by exact `request.Url.AbsolutePath` string comparisons. Use the documented path exactly, including the leading `/v1/...` path and no trailing slash unless documented. The routing loop only handles `POST`; other methods are not dispatched by these handlers.

### 4.2 Timeout guidance

| Endpoint class | Suggested timeout |
|---|---|
| Lightweight JSON calls | 8-10 s |
| `get_obs` with image payloads | >= 45 s |
| `get_topdown_image` | >= 120 s |
| `select_scene` (load operation) | >= 60-90 s |

### 4.3 Minimal examples

**curl (Windows PowerShell continuation style):**

```bash
curl -s -X POST "http://127.0.0.1:1212/v1/env/get_obs" ^
  -H "Content-Type: application/json" ^
  -d "{\"robot_list\":[\"Robot_1\"]}"
```

**Python:**

```python
import requests

BASE = "http://127.0.0.1:1212/"
r = requests.post(
    BASE.rstrip("/") + "/v1/env/get_obs",
    json={"robot_list": ["Robot_1"]},
    headers={"Content-Type": "application/json"},
    timeout=30,
)
r.raise_for_status()
print(r.json())
```

---

## 5. Response conventions and status codes

### 5.1 Success schema A

```json
{ "success": true, "message": "null" }
```

Used by routes including `robot_setup`, `scene_reset`, `select_scene`, and `get_reachable_points` (with string-valued success/message in that endpoint).

### 5.2 Success schema B

```json
{ "is_success": true, "error_info": "Null" }
```

Used by many env/agent/info handlers.

### 5.3 HTTP status usage

- **200**: success (or inline per-robot errors embedded in body for some image calls)
- **400**: explicit validation errors in selected routes (`select_scene` missing field)
- **500**: exception path

### 5.4 Image fields

- `rgb_base64`, `depth_base64`: Base64-encoded PNG bytes.
- Depth image is rendered depth visualization, not guaranteed metric depth map.

---

## 6. Endpoint reference (test-covered routes)

### 6.1 `POST /v1/env/robot_setup`

**Purpose**

Spawn/update robots from a top-level map (`robot_0`, `robot_1`, ...). Server may remove existing `Robot_*` objects not included in setup (`RemoveUnusedRobots`).

**Request JSON (per robot config)**

| Field | Type | Required | Notes |
|---|---|---|---|
| `type` | string | yes | Example: `LoCoBot`, `ManipulaTHOR` |
| `name` | string | yes | Runtime object name |
| `init_location` | `[x,y,z]` | yes | Initial position |
| `init_rotation` | `[x,y,z]` | yes | Initial euler rotation (deg) |
| `arm_length` | number | optional | Defaults to `"0.7"` in logic |
| `strength` | number | optional | Defaults to `"50"` in logic; user-defined capability value for client-side task rules |
| `robot_low` | number | optional | Defaults to `"0"` |
| `robot_high` | number | optional | Defaults to `"1"` |

**Strength configuration note**

`strength` is useful for personalized robot/team configuration. In the current environment-side logic, there is no fixed rule that blocks moving or pulling a moveable object when the combined `strength` of selected robots is below some threshold. If a task needs that constraint, implement it in the Python request/client layer before calling action endpoints. For example, a client can read or store each robot's `strength`, compare the sum against a task-specific object requirement, and decide whether to send `/v1/agent/joint_pull` or another action request.

**Success response**

```json
{ "success": true, "message": "null" }
```

**Error response**

```json
{ "success": false, "message": "<exception message>" }
```

**Implementation note**

`robot_setup` calls `RemoveUnusedRobots(validRobotNames)` after processing the request. Any existing scene object whose name starts with `Robot_` and is not included as a configured robot name in this request may be destroyed.

---

### 6.2 `POST /v1/agent/robot_teleport`

**Purpose**

Teleport one or more robots to absolute position and rotation.

**Request JSON**

Top-level map: `robotName -> { location, rotation }`.

| Field | Type |
|---|---|
| `location` | `[x,y,z]` |
| `rotation` | `[x,y,z]` |

**Success response (typical)**

```json
{ "is_success": true, "error_info": "Null" }
```

**Error response notes**

Some catch paths may serialize `success` instead of `is_success` in this codebase family; robust clients should check both.

---

### 6.3 `POST /v1/env/move_object`

**Purpose**

Teleport existing objects by name. Also toggles active state of children under `PickUpableObjects` based on provided keys (server-side behavior).

**Request JSON**

Top-level map: `objectName -> { init_location, init_rotation }`.

| Field | Type |
|---|---|
| `init_location` | `[x,y,z]` |
| `init_rotation` | `[x,y,z]` |

**Success response**

```json
{ "is_success": true, "error_info": "Null" }
```

**Error response**

```json
{ "success": false, "message": "<exception message>" }
```

---

### 6.4 `POST /v1/info/get_object_info`

**Purpose**

Return pose metadata for requested object names. Implemented by `ObjectController.GetObjInfo`.

**Request JSON**

| Field | Type |
|---|---|
| `object_list` | `string[]` |

**Success response shape**

Top-level includes:

- `is_success: true`
- `error_info: "Null"`

For each found object key, value has exactly:

| Key | Type | Meaning |
|---|---|---|
| `name` | string | `GameObject.name` |
| `location` | number[3] | `[x,y,z]` world position |
| `rotation` | number[3] | euler angles `[x,y,z]` |

**Not-found behavior**

- Missing objects are omitted (warning in Unity log).
- No per-object error key is emitted.

**Special mode: `"all"`**

If `object_list` is non-empty and first value is `"all"`, server enumerates all scene `GameObject`s and returns synthetic keys:

- `"object 0 name"`, `"object 1 name"`, ...

Each synthetic entry still contains `name`, `location`, `rotation`.

---

### 6.5 `POST /v1/info/get_reachable_points`

**Purpose**

Return reachable points sampled at step size.

**Request JSON**

| Field | Type |
|---|---|
| `step_size` | number |

**Success response (actual key/value style)**

```json
{
  "reachable_point": ["(x,y,z)", "..."],
  "success": "true",
  "message": "null"
}
```

Note that `success` and `message` are strings.

---

### 6.6 `POST /v1/agent/pick`

**Purpose**

Pick an object by name using a robot.

**Request JSON**

Top-level map: `robotName -> { object_name }`.

| Field | Type |
|---|---|
| `object_name` | string |

**Success response**

```json
{ "is_success": true, "error_info": "Null" }
```

---

### 6.7 `POST /v1/agent/place`

**Purpose**

Place currently held object at target pose.

**Request JSON**

Top-level map: `robotName -> { object_name, target_location, target_rotation }`.

| Field | Type |
|---|---|
| `object_name` | string |
| `target_location` | `[x,y,z]` |
| `target_rotation` | `[x,y,z]` |

**Success response**

```json
{ "is_success": true, "error_info": "Null" }
```

---

### 6.8 `POST /v1/agent/joint_pull`

**Purpose**

Execute joint pull interaction with one or more robots (`robot_list`). Distinct from `/v1/agent/pull` route.

**Request JSON**

| Field | Type |
|---|---|
| `robot_list` | `string[]` |
| `object_name` | string |
| `direction` | string (e.g. `"(1,0,0)"`) |

**Success response**

```json
{
  "result": "Success",
  "is_success": true,
  "error_info": "Null"
}
```

`result` is runtime-dependent (e.g., `Wrong Direction`, `Success`, etc.).

**Strength and moveable-object constraints**

This endpoint does not enforce a built-in "combined robot strength must be high enough" policy for moveable objects. Treat `strength` as a configurable robot attribute that your Python client can use for higher-level planning, team selection, or task validation before sending the `joint_pull` request.

---

### 6.9 `POST /v1/env/get_obs`

**Purpose**

Return per-robot visible objects; optionally attach RGB/depth images from each robot's `displayCamera`.

#### 6.9.1 Semantic observation mode

**Request JSON**

| Field | Type |
|---|---|
| `robot_list` | `string[]` |

**Success response (typical shape)**

```json
{
  "Robot_1": ["ObjectA", "ObjectB"],
  "is_success": true,
  "error_info": "Null"
}
```

Each robot key holds string array (possibly empty).

#### 6.9.2 Image mode (RGB and optional depth)

**Optional request fields**

| Field | Type | Meaning |
|---|---|---|
| `include_observation_image` | bool | Must be true to include `rgb_base64` |
| `include_depth` | bool | If true, include `depth_base64` (if capture succeeds) |
| `image_max_edge` | int | Max long edge clamp `[64, 8192]` |
| `image_width`, `image_height` | int | If both > 0, force size; otherwise derived from camera/aspect |

**Success response additions**

Top-level includes `observation_images`:

- `observation_images[robotName].width`
- `observation_images[robotName].height`
- `observation_images[robotName].rgb_base64` (if successful)
- `observation_images[robotName].depth_base64` (if depth requested and successful)
- `observation_images[robotName].error` (inline per-robot image error)
- `observation_images[robotName].depth_error` (inline depth-specific error)

**Inline image error possibilities** (still HTTP 200 in global success path)

- `CameraController not found on getObj.`
- `Robot '{name}' not found.`
- `'displayCamera' not found on robot.`
- `Camera missing on displayCamera.`
- `Failed to capture RGB.`
- `Failed to capture depth.` (in `depth_error`)

**Edge case**

If `envController.GetRobotsObs(...)` returns null/empty, server returns minimal envelope:

```json
{ "is_success": true, "error_info": "Null" }
```

(no per-robot semantic keys).

---

### 6.10 `POST /v1/env/get_topdown_image`

**Purpose**

Capture top-down RGB image from active, enabled camera whose name contains `TopDown` and whose `targetDisplay` matches requested display index.

**Request JSON** (all optional; `{}` allowed)

| Field | Type | Notes |
|---|---|---|
| `target_display` | int | Zero-based (`0` == Unity Inspector Display 1) |
| `image_max_edge` | int | Long-edge cap; server default 1920, clamped |
| `image_width`, `image_height` | int | If both >0, force size |

**Success response**

```json
{
  "is_success": true,
  "error_info": "Null",
  "target_display": 0,
  "camera_name": "TopDownCamera",
  "width": 1548,
  "height": 1155,
  "rgb_base64": "<base64 PNG>"
}
```

**Error response examples**

```json
{
  "is_success": false,
  "error_info": "No active enabled Camera with 'TopDown' in its name for target_display=..."
}
```

Other known error_info values:

- `GameObject 'getObj' not found; cannot capture.`
- `CameraController not found on 'getObj'.`
- `Failed to capture top-down RGB PNG.`

---

### 6.11 `POST /v1/info/get_object_neighbors`

**Purpose**

Estimate object neighbors using 6-direction raycasts from target object's `mesh` collider center. Implemented by `ObjectController.GetObjNeighbors` + `FindNeighborsWithRaycast`.

**Request JSON**

| Field | Type |
|---|---|
| `object_list` | `string[]` |

**Response shape**

Top-level:

- `is_success: true`
- `error_info: "Null"`

For each found object, value is a flat map:

- key = direction string (`Vector3.ToString()`)
- value = neighbor object name

Typical direction keys:

- `(0.0, 0.0, 1.0)` forward
- `(0.0, 0.0, -1.0)` back
- `(-1.0, 0.0, 0.0)` left
- `(1.0, 0.0, 0.0)` right
- `(0.0, 1.0, 0.0)` up
- `(0.0, -1.0, 0.0)` down

**Algorithm summary**

1. Find child `mesh`.
2. Require `Collider` on `mesh`.
3. Use `meshCollider.bounds.center` as ray origin.
4. For each of 6 directions, `Physics.RaycastAll(..., maxDistance)`.
5. Sort hits by distance.
6. First valid hit per direction is stored; if hit object is named `mesh`, parent name is used.

**maxDistance**

- `ObjectController.maxDistance` default: `1f`.

**Missing object behavior**

- If target object name not found: omitted from output (warning only).
- If mesh/collider missing: output for that object may be empty `{}`.

---

### 6.12 `POST /v1/info/robot_status`

**Purpose**

Return robot status map for requested robots. Data comes from `ObjectController.OneRobotStatus`.

**Request JSON**

| Field | Type |
|---|---|
| `robot_list` | `string[]` |

**Success response**

- One nested object per found robot name
- plus top-level `is_success` and `error_info`

Potential per-robot keys (if available):

- `hand`
- `handPosition`
- `isHold`
- `Holding`
- `robotType`
- `armLength`
- `strength`
- `robotLow`
- `robotHigh`

Details in [Appendix B](#104-get_robot_status--objectcontrolleronerobotstatus).

---

### 6.13 `POST /v1/info/object_type`

**Purpose**

Return object type and placeability metadata map via `ObjectController.GetObjectType`.

**Request JSON**

| Field | Type |
|---|---|
| `object_list` | `string[]` |

**Success response**

```json
{
  "data": { "Bed_01": "<type>" },
  "is_success": true,
  "error_info": "Null"
}
```

`data` may be empty. Actual key set can include:

- `{objectName}`
- `{objectName}Placeable`
- `{objectName}PutPoints`
- `{objectName}EdgePoints`

**Missing objects (Unity `ObjectController.GetObjectType`, patched)**

If a name in `object_list` does not exist in the current scene (`GameObject.Find` returns null), that name is **skipped**: no keys are added to `data` for it, and the call still succeeds when all names are missing (`data` may be `{}`). This matches the behavior of `get_object_info` for absent objects. Unity logs a warning: `Object '…' not found in the scene.` — clients that need type/edge data must check that expected keys (e.g. `{objectName}EdgePoints`) are present.

Details in [Appendix B](#105-get_object_type--objectcontrollergetobjecttype).

---

### 6.14 `POST /v1/env/select_scene`

**Purpose**

Load scene by integer `scene_id` through `EnvController.SelectScene`.

**Request JSON**

| Field | Type |
|---|---|
| `scene_id` | int |

**Success response**

```json
{ "success": true, "message": "null" }
```

**Validation failure**

- Missing `scene_id` -> HTTP 400:

```json
{ "success": false, "message": "Missing required field 'scene_id'." }
```

**Operational note**

After scene switch, wait ~1-2 s (or more on heavy scenes) before follow-up calls like `get_topdown_image`/`robot_setup`.

---

### 6.15 `POST /v1/env/scene_reset`

**Purpose**

Reset current scene (`EnvController.SceneReset`).

**Request JSON**

- `{}` is sufficient.

**Success response**

```json
{ "success": true, "message": "null" }
```

---

## 7. Testing utilities and payload templates

`scripts/check_http_api.py` provides:

- reusable endpoint wrappers
- end-to-end connectivity run
- optional RGB/depth/topdown image decoding & save to `scripts/obs_captures/`
- topdown multi-scene sweep (default `0-9`)

### 7.1 Print payload templates

```bash
python dynateamthor_api/scripts/check_http_api.py --print-payloads
```

### 7.2 Run connectivity suite

```bash
python dynateamthor_api/scripts/check_http_api.py --base-url http://127.0.0.1:1212/ --timeout 15
```

### 7.3 Useful flags

| Flag | Meaning |
|---|---|
| `--obs-max-edge N` | `image_max_edge` for `get_obs` image mode |
| `--topdown-max-edge N` | `image_max_edge` for `get_topdown_image` |
| `--topdown-scenes SPEC` | Scene ids for select+topdown sweep (`0-9`, `0,2,5`, etc.) |
| `--topdown-settle SEC` | Sleep after each `select_scene` |
| `--topdown-current-only` | Skip sweep; capture current scene topdown only |
| `--no-save-obs` | Do not write PNG files |
| `--no-obs-extended` | Skip extended multi-robot/multi-yaw obs run |

---

## 8. Out of scope

The following routes exist in `GameInitializer` routing but are not in this connectivity-test document:

- `/v1/env/pause`
- `/v1/env/resume`
- `/v1/info/get_communication_status`
- `/v1/info/get_robot_rgbd`
- `/v1/agent/robot_move`
- `/v1/agent/robot_rotate`
- `/v1/agent/pull`
- `/v1/env/add_object`
- `/v1/env/disable_object`
- `/v1/info/is_object_in_view`
- `/shut_down`

Also present: `/select_task_type` placeholder branch (no handling logic in shown code path).

`/shut_down` sets the server loop flag to stop, but it is not included in the user-facing scripts because it is operational/destructive for an interactive session.

---

## 9. Appendix A: Error catalog from source

This catalog is derived from source code throw/catch and known inline error fields. Runtime `ex.Message` can vary by underlying exception.

### 9.1 URL/listener startup errors (`GameInitializer`)

| Message | Where it originates | Typical cause |
|---|---|---|
| `URL cannot be empty.` | `TryNormalizeListenerUrl` | Empty input |
| `Only http:// URL is supported by HttpListener in this setup.` | `TryNormalizeListenerUrl` | URL does not start with `http://` |
| `Invalid URL format.` | `TryNormalizeListenerUrl` | Parse failure |
| `Only http scheme is supported.` | `TryNormalizeListenerUrl` | Non-http scheme |
| `Failed to start HttpListener: ...` | `StartHttpListener` catch | Port in use / permission / bind issue |
| `Invalid --http-port. Expected 1-65535.` | `TryResolveHeadlessListenerUrl` | Headless command-line port is missing/invalid |
| `Invalid THOR_HTTP_PORT. Expected 1-65535.` | `TryResolveHeadlessListenerUrl` | Headless environment port is missing/invalid |
| `Invalid --http-url: ...` | `TryResolveHeadlessListenerUrl` | Headless command-line URL failed normalization |
| `Invalid THOR_HTTP_URL: ...` | `TryResolveHeadlessListenerUrl` | Headless environment URL failed normalization |

### 9.2 JSON request content-type errors (`RestfulApiManagement.ToDict`)

| Condition | Exception |
|---|---|
| `request.ContentType != "application/json"` | `NotSupportedException("Only JSON payload is supported.")` |

Depending on caller catch policy, this usually propagates as HTTP 500 with serialized message.

Some newer image/top-down helpers use a more permissive JSON parser that allows empty bodies or `application/json` with parameters, but the core route handlers still use the strict parser above. For consistent behavior across endpoints, send exact `application/json`.

### 9.3 Route-specific documented errors

#### `select_scene`

| Condition | HTTP | Body |
|---|---|---|
| Missing `scene_id` | 400 | `success: false`, `message: Missing required field 'scene_id'.` |
| Other exception | 500 | `success: false`, `message: <ex.Message>` |

#### `get_object_neighbors` / `robot_status` / `object_type`

| Condition | HTTP | Body/Message |
|---|---|---|
| Missing/invalid list field | 500 | `is_success: false`, `error_info: Missing or invalid ...` |
| list field not JArray | 500 | `is_success: false`, `error_info: '... must be a valid JArray.'` |
| `getObj` missing | 500 | `Robot object 'getObj' not found in the scene.` |
| `ObjectController` missing | 500 | `ObjectController component not found on the 'getObj' GameObject.` |
| `GetObjectType` internal failure | 500 | `Error occurred while fetching object type: ...` |
| `object_list` name not in scene | 200 | `is_success: true`; **no** entries in `data` for that name (object omitted). See §6.13. |

#### `get_obs`

| Condition | HTTP | Body |
|---|---|---|
| Missing/invalid `robot_list` | 500 | `is_success: false`, `error_info: Missing or invalid 'robot_list'...` |
| `robot_list` not JArray | 500 | `is_success: false`, `error_info: 'robot_list' must be a valid JArray.` |
| `getObj` missing | 500 | `Robot object 'getObj' not found in the scene.` |
| `EnvController` missing | 500 | Message text currently says `RobotController component not found on the 'getObj' GameObject.` |
| per-robot image capture issues | 200 | Inline `observation_images[robot].error/depth_error` |

Inline image error values seen in code:

- `CameraController not found on getObj.`
- `Robot '{name}' not found.`
- `'displayCamera' not found on robot.`
- `Camera missing on displayCamera.`
- `Failed to capture RGB.`
- `Failed to capture depth.`

#### `get_topdown_image`

| Condition | HTTP | `error_info` |
|---|---|---|
| No TopDown camera matching target display | 500 | `No active enabled Camera with 'TopDown' in its name for target_display=...` |
| `getObj` missing | 500 | `GameObject 'getObj' not found; cannot capture.` |
| no `CameraController` on `getObj` | 500 | `CameraController not found on 'getObj'.` |
| capture returned empty | 500 | `Failed to capture top-down RGB PNG.` |
| generic exception | 500 | `<ex.Message>` |

#### `joint_pull`

| Condition | HTTP | Body |
|---|---|---|
| Missing `robot_list` / `object_name` / `direction` | 500 | `is_success: false`, `error_info: Missing or invalid ...` |
| invalid `robot_list` type | 500 | `'robot_list' must be a valid JArray.` |
| `getObj`/component missing | 500 | same family as env errors |

#### Additional (not in test suite, but present in source)

- `RobotsCommunicateApi` may emit:
  - `GameObject '{robotName}' not found.`
  - `RobotController component not found on '{robotName}'.`

### 9.4 Generic catch fallback patterns

Most handlers serialize one of:

```json
{ "is_success": false, "error_info": "<ex.Message>" }
```

or

```json
{ "success": false, "message": "<ex.Message>" }
```

or occasionally

```json
{ "success": false, "error_info": "<ex.Message>" }
```

Clients should parse defensively.

---

## 10. Appendix B: Deep implementation notes

### 10.1 `get_object_info` internals (`ObjectController.GetObjInfo`)

- Normal mode (`object_list[0] != "all"`):
  - `GameObject.Find(objectName)` per request item.
  - Found -> add `name/location/rotation`.
  - Not found -> warning log; no response entry.
- `"all"` mode:
  - Iterates all `GameObject`s (`FindObjectsOfType<GameObject>()`).
  - Response keys become synthetic (`object {i} name`), while nested `name` is real object name.
- Catch block logs and returns partial map built so far.

### 10.2 `get_object_neighbors` internals (`FindNeighborsWithRaycast`)

1. require child named `mesh`
2. require `Collider` on `mesh`
3. origin = `meshCollider.bounds.center`
4. raycast in 6 axis directions with `Physics.RaycastAll`
5. sort hits by distance ascending
6. ignore self hit
7. if hit object is named `mesh`, use parent object name
8. first qualifying hit in each direction is stored

No hit in direction => no key for that direction.

### 10.3 `get_obs` image sizing behavior

`RestfulApiManagement.GetRobotsObs`:

- If both `image_width` and `image_height` are positive, that explicit size is used.
- Else `ComputeImageCaptureSize(...)` derives size from camera dimensions/aspect and clamps by `image_max_edge`.
- `image_max_edge` default 1920, clamped to [64, 8192].

### 10.4 `get_robot_status` (`ObjectController.OneRobotStatus`)

Potential keys and generation rules:

| Key | Rule |
|---|---|
| `hand` | `"True"` if child `Hand` exists, else `"False"` |
| `handPosition` | Included when hand exists, formatted string `(x, y, z)` |
| `isHold` | `"True"` if hand has children; else `"False"` |
| `Holding` | Concatenated child names (no separator) if holding |
| `robotType` | `RobotController.robotType` |
| `armLength` | `RobotController.armLength` |
| `strength` | `RobotController.strength`; configurable robot capability value, suitable for Python-side custom task constraints |
| `robotLow` | `RobotController.robotLow` |
| `robotHigh` | `RobotController.robotHigh` |

If robot object is missing, that robot is skipped. If `RobotController` missing on found object, exception may bubble to API catch.

The environment does not use `strength` to enforce a universal movement threshold for moveable objects. If your experiment needs rules such as "two robots can pull this object only when their strength sum is >= required_strength", keep that rule in the Python client or planner and call the HTTP API only after the rule passes.

### 10.5 `get_object_type` (`ObjectController.GetObjectType`)

For each request object name, returns multiple keys in `data`:

| Key | Meaning |
|---|---|
| `{objectName}` | parent object name or `"None"` |
| `{objectName}Placeable` | `"True"` if child `putPoints` exists; else `"False"` |
| `{objectName}PutPoints` | concatenated `putPoints` child positions (` ; ` separator) |
| `{objectName}EdgePoints` | concatenated sampled renderer-bound points (` ; ` separator) |

**Absent objects:** If `GameObject.Find(objectName)` fails, that object is **not** represented in `data` (no `{objectName}` nor derived keys). The request still returns success when the list is valid; only genuine errors in `GetObjectType` (other than missing `GameObject`) surface as HTTP 500 via the API catch path.

**Client note:** Helpers such as `helpers/navigation.py` / `helpers/spatial.py` expect keys like `{objectName}EdgePoints`. Verify the key exists before parsing when the object may be absent from the scene.

### 10.6 `get_obs` empty semantic payload behavior

If `envController.GetRobotsObs(robotNameList)` returns null or empty, response is minimal:

```json
{ "is_success": true, "error_info": "Null" }
```

No per-robot semantic keys are included in this branch.

---

*Document version: aligned with `scripts/check_http_api.py` and Unity scripts under `ControllerCoreCode` at the time of writing. Runtime behavior can change with future code revisions.*

