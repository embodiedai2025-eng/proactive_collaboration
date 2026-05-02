#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import base64
import json
import time
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import requests

HEADERS = {"Content-Type": "application/json"}
REMOTE_URL = "http://127.0.0.1:1212/"
REQUEST_TIMEOUT = 8
# Upper bound on longest image edge when omitting image_width/image_height (Unity matches displayCamera aspect).
OBS_IMAGE_MAX_EDGE = 1280
# Top-down capture (Display 1 in Unity = target_display 0); longest edge cap for HD output.
TOPDOWN_IMAGE_MAX_EDGE = 1920

SETUP_PAYLOAD = {
    "robot_0": {
        "type": "LoCoBot",
        "name": "Robot_0",
        "init_location": [-5.9592, 0.90, -0.201],
        "init_rotation": [0, 180, 0],
        "arm_length": 1,
        "robot_high": 0.5,
        "robot_low": 0.2,
        "strength": 80,
    },
    "robot_1": {
        "type": "ManipulaTHOR",
        "name": "Robot_1",
        "init_location": [-3.216, 0.90, -3.064],
        "init_rotation": [0, -90, 0],
    },
    "robot_2": {
        "type": "ManipulaTHOR",
        "name": "Robot_2",
        "init_location": [-3.216, 0.90, -1.609],
        "init_rotation": [0, -90, 0],
    },
}
TELEPORT_PAYLOAD = {
    "Robot_1": {"location": [0.712, 0.882, 0.316], "rotation": [0, -90, 0]},
    "Robot_0": {"location": [2.94, 1.25, 0.82], "rotation": [0, -90, 0]}
}
MOVE_OBJECT_PAYLOAD = {
    "Cup_01": {"init_location": [5, 1.2, -4.3], "init_rotation": [0, 0, 0]}
}
OBJECT_INFO_PAYLOAD = {"object_list": ["Fridge_01", "Robot_0"]}
REACHABLE_POINTS_PAYLOAD = {"step_size": 0.1}
PICK_UP_PAYLOAD = {"Robot_0": {"object_name": "Pillow_01"}}
GET_OBS_PAYLOAD = {"robot_list": ["Robot_1"]}
# displayCamera RGB + depth (PNG base64). Omit image_width/height so Unity uses displayCamera pixel aspect (same FOV as in-editor) and image_max_edge for clarity.
GET_OBS_RGBD_PAYLOAD = {
    "robot_list": ["Robot_1"],
    "include_observation_image": True,
    "include_depth": True,
    "image_max_edge": 1280,
}
# One request: RGBD for every robot that has displayCamera (after robot_setup)
GET_OBS_RGBD_MULTI_ROBOT_PAYLOAD = {
    "robot_list": ["Robot_0", "Robot_1", "Robot_2"],
    "include_observation_image": True,
    "include_depth": True,
    "image_max_edge": 1280,
}
OBJECT_NEIGHBORS_PAYLOAD = {"object_list": ["Pillow_01", "Pillow_02", "AlarmClock_01"]}
ROBOT_STATUS_PAYLOAD = {"robot_list": ["Robot_1", "Robot_0", "Robot_2"]}
OBJECT_TYPE_PAYLOAD = {"object_list": ["Toilet_01", "Bed_01", "AlarmClock_01"]}
PLACE_OBJECT_PAYLOAD = {
    "Robot_0": {
        "object_name": "Pillow_01",
        "target_location": [-4.59, 0.91, -2.4],
        "target_rotation": [0, 0, 0],
    }
}
JOINT_PULL_PAYLOAD = {"robot_list": ["Robot_1", "Robot_2"], "object_name": "Bed_01", "direction": "(1,0,0)"}
SCENE_RESET_PAYLOAD = {}
SELECT_SCENE_PAYLOAD = {"scene_id": 5}
# Top-down RGB from scene camera named like *TopDown* on given Unity target_display (0 = Inspector "Display 1").
GET_TOPDOWN_IMAGE_PAYLOAD = {
    "target_display": 0,
    "image_max_edge": 1920,
}


@dataclass
class ApiResult:
    name: str
    path: str
    status: str
    detail: str


def set_remote_url(remote_url: str) -> None:
    global REMOTE_URL
    REMOTE_URL = remote_url


def set_request_timeout(timeout: int) -> None:
    global REQUEST_TIMEOUT
    REQUEST_TIMEOUT = timeout


def _post(path: str, payload: Dict, name: str, timeout: Optional[int] = None) -> ApiResult:
    url = REMOTE_URL.rstrip("/") + "/" + path.lstrip("/")
    to = REQUEST_TIMEOUT if timeout is None else timeout
    try:
        response = requests.post(url, json=payload, headers=HEADERS, timeout=to)
        detail = response.text[:180].replace("\n", " ")
        return ApiResult(name=name, path=path, status=f"HTTP_{response.status_code}", detail=detail)
    except requests.exceptions.RequestException as exc:
        return ApiResult(name=name, path=path, status="CONNECT_ERR", detail=str(exc))


def robot_setup(payload: Optional[Dict] = None) -> ApiResult:
    return _post("v1/env/robot_setup", deepcopy(payload or SETUP_PAYLOAD), "robot_setup")


def robot_teleport(payload: Optional[Dict] = None) -> ApiResult:
    return _post("v1/agent/robot_teleport", deepcopy(payload or TELEPORT_PAYLOAD), "robot_teleport")


def move_object(payload: Optional[Dict] = None) -> ApiResult:
    return _post("v1/env/move_object", deepcopy(payload or MOVE_OBJECT_PAYLOAD), "move_object")


def get_object_info(payload: Optional[Dict] = None) -> ApiResult:
    return _post("v1/info/get_object_info", deepcopy(payload or OBJECT_INFO_PAYLOAD), "get_object_info")


def get_reachable_points(payload: Optional[Dict] = None) -> ApiResult:
    return _post("v1/info/get_reachable_points", deepcopy(payload or REACHABLE_POINTS_PAYLOAD), "get_reachable_points")


def pick_up(payload: Optional[Dict] = None) -> ApiResult:
    return _post("v1/agent/pick", deepcopy(payload or PICK_UP_PAYLOAD), "pick_up")


def get_robot_obs(payload: Optional[Dict] = None) -> ApiResult:
    return _post("v1/env/get_obs", deepcopy(payload or GET_OBS_PAYLOAD), "get_robot_obs")


def get_robot_obs_rgbd(payload: Optional[Dict] = None) -> ApiResult:
    """get_obs with displayCamera RGB + depth PNG (base64)."""
    return _post("v1/env/get_obs", deepcopy(payload or GET_OBS_RGBD_PAYLOAD), "get_robot_obs_rgbd")


def get_topdown_image(payload: Optional[Dict] = None) -> ApiResult:
    """Top-down RGB PNG (base64) from v1/env/get_topdown_image (large payload; long timeout)."""
    body = deepcopy(payload or GET_TOPDOWN_IMAGE_PAYLOAD)
    body["image_max_edge"] = TOPDOWN_IMAGE_MAX_EDGE
    return _post(
        "v1/env/get_topdown_image",
        body,
        "get_topdown_image",
        max(REQUEST_TIMEOUT, 120),
    )


def obs_captures_dir() -> Path:
    """Directory where decoded observation PNGs are written."""
    return Path(__file__).resolve().parent / "obs_captures"


def _safe_filename_part(name: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)


def _verify_png_base64(b64: str) -> Tuple[bool, str]:
    if not b64 or not isinstance(b64, str):
        return False, "missing or not a string"
    try:
        raw = base64.b64decode(b64, validate=False)
    except Exception as exc:
        return False, f"base64 decode failed: {exc}"
    if len(raw) < 32:
        return False, f"decoded too short ({len(raw)} bytes)"
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        return False, "decoded bytes are not a PNG signature"
    return True, f"PNG ok, {len(raw)} bytes"


def check_get_obs_rgbd(
    payload: Optional[Dict] = None,
    save_images: bool = True,
    capture_label: str = "",
) -> bool:
    """POST get_obs with image flags and verify rgb_base64 + depth_base64 per robot.

    capture_label: optional tag in filenames, e.g. 'allrobots' or 'Robot_1_yaw90'.
    Returns True if every requested robot has valid rgb+depth PNGs.
    """
    path = "v1/env/get_obs"
    body = deepcopy(payload or GET_OBS_RGBD_PAYLOAD)
    body["image_max_edge"] = OBS_IMAGE_MAX_EDGE
    url = REMOTE_URL.rstrip("/") + "/" + path.lstrip("/")
    timeout = max(REQUEST_TIMEOUT, 45)
    capture_dir = obs_captures_dir()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    label_tag = f"_{_safe_filename_part(capture_label)}" if capture_label else ""

    print("-" * 80)
    print(f"[GetObs RGB + Depth (displayCamera){(' — ' + capture_label) if capture_label else ''}]")
    print(
        f"  image_max_edge={OBS_IMAGE_MAX_EDGE}  (no fixed width/height => server uses displayCamera aspect)"
    )
    print(f"POST {url}  (timeout={timeout}s)")
    try:
        resp = requests.post(url, json=body, headers=HEADERS, timeout=timeout)
    except requests.exceptions.RequestException as exc:
        print(f"  FAIL  CONNECT_ERR  {exc}")
        return False

    print(f"  HTTP_{resp.status_code}")
    if resp.status_code >= 400:
        print(f"  FAIL  {resp.text[:500]}")
        return False

    try:
        data = resp.json()
    except json.JSONDecodeError as exc:
        print(f"  FAIL  invalid JSON: {exc}")
        return False

    obs_img = data.get("observation_images")
    if not isinstance(obs_img, dict):
        print("  FAIL  missing or invalid 'observation_images' object")
        return False

    robots = body.get("robot_list") or []
    all_ok = True
    for name in robots:
        entry = obs_img.get(name)
        if not isinstance(entry, dict):
            print(f"  FAIL  robot {name!r}: no entry in observation_images")
            all_ok = False
            continue
        if entry.get("error"):
            print(f"  FAIL  robot {name!r}: server error {entry.get('error')}")
            all_ok = False
            continue
        rgb = entry.get("rgb_base64")
        dep = entry.get("depth_base64")
        ok_r, msg_r = _verify_png_base64(rgb)
        ok_d, msg_d = _verify_png_base64(dep)
        print(f"  robot {name!r}: rgb  -> {'OK' if ok_r else 'FAIL'}  {msg_r}")
        print(f"  robot {name!r}: depth -> {'OK' if ok_d else 'FAIL'}  {msg_d}")
        if save_images and (ok_r or ok_d):
            capture_dir.mkdir(parents=True, exist_ok=True)
            safe = _safe_filename_part(name)
            if ok_r:
                try:
                    rgb_path = capture_dir / f"{stamp}{label_tag}_{safe}_rgb.png"
                    rgb_path.write_bytes(base64.b64decode(rgb, validate=False))
                    print(f"  saved rgb  -> {rgb_path}")
                except Exception as exc:
                    print(f"  WARN  could not save rgb for {name!r}: {exc}")
                    all_ok = False
            if ok_d:
                try:
                    dep_path = capture_dir / f"{stamp}{label_tag}_{safe}_depth.png"
                    dep_path.write_bytes(base64.b64decode(dep, validate=False))
                    print(f"  saved depth -> {dep_path}")
                except Exception as exc:
                    print(f"  WARN  could not save depth for {name!r}: {exc}")
                    all_ok = False
        if not ok_r or not ok_d:
            if entry.get("depth_error"):
                print(f"  robot {name!r}: depth_error field: {entry.get('depth_error')}")
            all_ok = False

    if data.get("is_success") is not True:
        print(f"  WARN  is_success={data.get('is_success')!r}")
    print(f"  RESULT  {'PASS' if all_ok else 'FAIL'}")
    return all_ok


def check_get_obs_rgbd_extended(save_images: bool = True) -> bool:
    """Multi-robot RGBD capture + Robot_1 at several yaws (teleport) for comparison.

    Note: Unity encodes the depth RenderTexture as RGB PNG; it is not a raw depth map,
    so the saved depth image may look like false-color or low contrast — that is expected
    from the current server implementation.
    """
    overall = True
    print("=" * 80)
    print("[GetObs extended: all robots + multi-angle Robot_1]")
    print(
        "  Hint: depth PNG is a visualization of the depth buffer, not metric depth values."
    )

    if not check_get_obs_rgbd(
        payload=deepcopy(GET_OBS_RGBD_MULTI_ROBOT_PAYLOAD),
        save_images=save_images,
        capture_label="allrobots",
    ):
        overall = False

    r1 = deepcopy(TELEPORT_PAYLOAD.get("Robot_1"))
    if not isinstance(r1, dict) or "location" not in r1:
        print("  SKIP  multi-angle: TELEPORT_PAYLOAD has no Robot_1 location")
        return overall

    loc = list(r1["location"])
    base_rot = list(r1.get("rotation", [0, -90, 0]))
    yaws = (-120, -60, 0, 60, 120)

    for yaw in yaws:
        rot = [float(base_rot[0]), float(yaw), float(base_rot[2])]
        teleport_body = {"Robot_1": {"location": loc, "rotation": rot}}
        print(f"  teleport Robot_1 yaw={yaw} ...")
        tr = robot_teleport(teleport_body)
        if tr.status != "HTTP_200":
            print(f"  WARN  teleport failed: {tr.status} {tr.detail}")
            overall = False
            continue
        payload = deepcopy(GET_OBS_RGBD_PAYLOAD)
        payload["robot_list"] = ["Robot_1"]
        if not check_get_obs_rgbd(
            payload=payload,
            save_images=save_images,
            capture_label=f"Robot_1_yaw{yaw}",
        ):
            overall = False

    print("=" * 80)
    print(f"[GetObs extended] FINAL  {'PASS' if overall else 'FAIL'}")
    return overall


def check_get_topdown_image(
    save_images: bool = True,
    *,
    filename_tag: str = "",
    print_banner: bool = True,
) -> bool:
    """POST v1/env/get_topdown_image and verify rgb_base64 PNG.

    filename_tag: optional segment in saved filename, e.g. \"scene3\" -> \"*_scene3_topdown_display1_rgb.png\".
    """
    path = "v1/env/get_topdown_image"
    body = deepcopy(GET_TOPDOWN_IMAGE_PAYLOAD)
    body["image_max_edge"] = TOPDOWN_IMAGE_MAX_EDGE
    url = REMOTE_URL.rstrip("/") + "/" + path.lstrip("/")
    timeout = max(REQUEST_TIMEOUT, 120)
    capture_dir = obs_captures_dir()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    safe_tag = _safe_filename_part(filename_tag) if filename_tag else ""
    tag_part = f"{safe_tag}_" if safe_tag else ""

    if print_banner:
        print("=" * 80)
        print("[Top-down image (Display 1 => target_display 0)]")
        print(
            f"  image_max_edge={TOPDOWN_IMAGE_MAX_EDGE}  camera name must contain 'TopDown' on that display"
        )
    print(f"POST {url}  (timeout={timeout}s)")
    try:
        resp = requests.post(url, json=body, headers=HEADERS, timeout=timeout)
    except requests.exceptions.RequestException as exc:
        print(f"  FAIL  CONNECT_ERR  {exc}")
        return False

    print(f"  HTTP_{resp.status_code}")
    if resp.status_code >= 400:
        print(f"  FAIL  {resp.text[:500]}")
        return False

    try:
        data = resp.json()
    except json.JSONDecodeError as exc:
        print(f"  FAIL  invalid JSON: {exc}")
        return False

    if data.get("is_success") is not True:
        print(f"  FAIL  is_success={data.get('is_success')!r} error_info={data.get('error_info')!r}")
        return False

    cam_name = data.get("camera_name", "?")
    w, h = data.get("width"), data.get("height")
    print(f"  camera_name={cam_name!r} size={w}x{h}")

    rgb = data.get("rgb_base64")
    ok_r, msg_r = _verify_png_base64(rgb)
    print(f"  rgb -> {'OK' if ok_r else 'FAIL'}  {msg_r}")

    if save_images and ok_r:
        capture_dir.mkdir(parents=True, exist_ok=True)
        try:
            out = capture_dir / f"{stamp}_{tag_part}topdown_display1_rgb.png"
            out.write_bytes(base64.b64decode(rgb, validate=False))
            print(f"  saved -> {out}")
        except Exception as exc:
            print(f"  WARN  save failed: {exc}")
            return False

    print(f"  RESULT  {'PASS' if ok_r else 'FAIL'}")
    return ok_r


def parse_topdown_scene_ids(spec: str) -> List[int]:
    """Parse e.g. \"0-9\", \"0,2,5\", or \"5\" into a list of scene ids."""
    s = spec.strip()
    if not s:
        return list(range(10))
    if "-" in s and "," not in s:
        a, b = s.split("-", 1)
        lo, hi = int(a.strip()), int(b.strip())
        if hi < lo:
            lo, hi = hi, lo
        return list(range(lo, hi + 1))
    return [int(x.strip()) for x in s.split(",") if x.strip()]


def capture_topdown_for_scenes(
    scene_ids: List[int],
    save_images: bool = True,
    settle_seconds: float = 1.5,
    select_timeout: Optional[int] = None,
) -> bool:
    """select_scene for each id, then get_topdown_image (Display 1 / target_display 0)."""
    overall = True
    to = max(REQUEST_TIMEOUT, 90) if select_timeout is None else select_timeout

    print("=" * 80)
    print(f"[Top-down sweep: scene_id in {scene_ids}]")
    print(f"  select_scene timeout={to}s  settle_after_load={settle_seconds}s")
    print(
        f"  image_max_edge={TOPDOWN_IMAGE_MAX_EDGE}  (override with --topdown-max-edge)"
    )

    for sid in scene_ids:
        print("-" * 80)
        print(f"  >>> scene_id={sid}  POST v1/env/select_scene")
        res = _post("v1/env/select_scene", {"scene_id": sid}, "select_scene", timeout=to)
        if res.status != "HTTP_200":
            print(f"  FAIL  select_scene  {res.status}  {res.detail}")
            overall = False
            continue
        if settle_seconds > 0:
            time.sleep(settle_seconds)
        if not check_get_topdown_image(
            save_images=save_images,
            filename_tag=f"scene{sid}",
            print_banner=False,
        ):
            overall = False

    print("=" * 80)
    print(f"[Top-down sweep] FINAL  {'PASS' if overall else 'FAIL'}")
    return overall


def get_object_neighbors(payload: Optional[Dict] = None) -> ApiResult:
    return _post(
        "v1/info/get_object_neighbors",
        deepcopy(payload or OBJECT_NEIGHBORS_PAYLOAD),
        "get_object_neighbors",
    )


def get_robot_status(payload: Optional[Dict] = None) -> ApiResult:
    return _post("v1/info/robot_status", deepcopy(payload or ROBOT_STATUS_PAYLOAD), "get_robot_status")


def get_object_type(payload: Optional[Dict] = None) -> ApiResult:
    return _post("v1/info/object_type", deepcopy(payload or OBJECT_TYPE_PAYLOAD), "get_object_type")


def place_object(payload: Optional[Dict] = None) -> ApiResult:
    return _post("v1/agent/place", deepcopy(payload or PLACE_OBJECT_PAYLOAD), "place_object")


def pull_object(payload: Optional[Dict] = None) -> ApiResult:
    return _post("v1/agent/joint_pull", deepcopy(payload or JOINT_PULL_PAYLOAD), "pull_object")


def scene_reset(payload: Optional[Dict] = None) -> ApiResult:
    return _post("v1/env/scene_reset", deepcopy(payload or SCENE_RESET_PAYLOAD), "scene_reset")


def select_scene(payload: Optional[Dict] = None) -> ApiResult:
    return _post("v1/env/select_scene", deepcopy(payload or SELECT_SCENE_PAYLOAD), "select_scene")


def build_payload_templates() -> Dict[str, Dict]:
    return {
        "v1/env/robot_setup": deepcopy(SETUP_PAYLOAD),
        "v1/agent/robot_teleport": deepcopy(TELEPORT_PAYLOAD),
        "v1/env/move_object": deepcopy(MOVE_OBJECT_PAYLOAD),
        "v1/info/get_object_info": deepcopy(OBJECT_INFO_PAYLOAD),
        "v1/info/get_reachable_points": deepcopy(REACHABLE_POINTS_PAYLOAD),
        "v1/agent/pick": deepcopy(PICK_UP_PAYLOAD),
        "v1/env/get_obs": deepcopy(GET_OBS_PAYLOAD),
        "v1/env/get_obs_rgbd": deepcopy(GET_OBS_RGBD_PAYLOAD),
        "v1/env/get_obs_rgbd_multi": deepcopy(GET_OBS_RGBD_MULTI_ROBOT_PAYLOAD),
        "v1/info/get_object_neighbors": deepcopy(OBJECT_NEIGHBORS_PAYLOAD),
        "v1/info/robot_status": deepcopy(ROBOT_STATUS_PAYLOAD),
        "v1/info/object_type": deepcopy(OBJECT_TYPE_PAYLOAD),
        "v1/agent/place": deepcopy(PLACE_OBJECT_PAYLOAD),
        "v1/agent/joint_pull": deepcopy(JOINT_PULL_PAYLOAD),
        "v1/env/scene_reset": deepcopy(SCENE_RESET_PAYLOAD),
        "v1/env/select_scene": deepcopy(SELECT_SCENE_PAYLOAD),
        "v1/env/get_topdown_image": deepcopy(GET_TOPDOWN_IMAGE_PAYLOAD),
    }


def run_connectivity_check(
    save_obs_images: bool = True,
    obs_extended: bool = True,
    *,
    topdown_current_only: bool = False,
    topdown_scene_ids: Optional[List[int]] = None,
    topdown_settle_seconds: float = 1.5,
) -> None:
    normal_calls: List[Callable[[], ApiResult]] = [
        robot_setup,
        robot_teleport,
        pick_up,
        place_object,
        move_object,
        get_object_info,
        get_reachable_points,
        get_robot_obs,
        get_object_neighbors,
        get_robot_status,
        get_object_type,
        pull_object,
    ]
    # Keep destructive endpoints at the end. Run select_scene before scene_reset
    # because scene_reset may stop the listener in current Unity implementation.
    destructive_calls: List[Callable[[], ApiResult]] = [select_scene, scene_reset]

    print(f"Base URL: {REMOTE_URL}")
    print(f"Timeout: {REQUEST_TIMEOUT}s")
    print("-" * 80)

    print("[Normal Endpoints]")
    for call in normal_calls:
        result = call()
        print(f"{result.path:35s}  {result.status:12s}  {result.detail}")

    if obs_extended:
        check_get_obs_rgbd_extended(save_images=save_obs_images)
    else:
        check_get_obs_rgbd(save_images=save_obs_images)

    if topdown_current_only:
        check_get_topdown_image(save_images=save_obs_images)
    else:
        ids = topdown_scene_ids if topdown_scene_ids is not None else list(range(10))
        capture_topdown_for_scenes(
            ids,
            save_images=save_obs_images,
            settle_seconds=topdown_settle_seconds,
        )

    print("-" * 80)
    print("[Destructive Endpoints]")
    for call in destructive_calls:
        result = call()
        print(f"{result.path:35s}  {result.status:12s}  {result.detail}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Standalone UE API connectivity test with reusable per-endpoint functions.")
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:1212/",
        help="Unity HTTP base URL, e.g. http://127.0.0.1:1212/",
    )
    parser.add_argument("--timeout", type=int, default=8, help="Request timeout in seconds.")
    parser.add_argument(
        "--print-payloads",
        action="store_true",
        help="Print all request payload templates and exit.",
    )
    parser.add_argument(
        "--no-save-obs",
        action="store_true",
        help="Do not decode/write get_obs RGB/depth PNGs to scripts/obs_captures.",
    )
    parser.add_argument(
        "--no-obs-extended",
        action="store_true",
        help="Only run single-robot get_obs RGBD (Robot_1), not multi-robot + multi-angle.",
    )
    parser.add_argument(
        "--obs-max-edge",
        type=int,
        default=1280,
        metavar="N",
        help="Pass image_max_edge to get_obs (longest side cap; width/height follow displayCamera aspect when omitted).",
    )
    parser.add_argument(
        "--topdown-max-edge",
        type=int,
        default=1920,
        metavar="N",
        help="Pass image_max_edge to get_topdown_image (HD cap; longest side).",
    )
    parser.add_argument(
        "--topdown-current-only",
        action="store_true",
        help="Only capture one top-down for the current scene (no select_scene sweep).",
    )
    parser.add_argument(
        "--topdown-scenes",
        default="0-9",
        metavar="SPEC",
        help='Scene ids for top-down sweep after select_scene each: \"0-9\", \"0,2,5\", etc. Default: 0-9.',
    )
    parser.add_argument(
        "--topdown-settle",
        type=float,
        default=1.5,
        metavar="SEC",
        help="Seconds to wait after each select_scene before get_topdown_image (Unity load).",
    )
    args = parser.parse_args()

    global OBS_IMAGE_MAX_EDGE
    OBS_IMAGE_MAX_EDGE = max(64, args.obs_max_edge)
    global TOPDOWN_IMAGE_MAX_EDGE
    TOPDOWN_IMAGE_MAX_EDGE = max(64, args.topdown_max_edge)

    set_remote_url(args.base_url)
    set_request_timeout(args.timeout)

    if args.print_payloads:
        print(json.dumps(build_payload_templates(), indent=2, ensure_ascii=False))
        return

    sweep_ids = parse_topdown_scene_ids(args.topdown_scenes)

    run_connectivity_check(
        save_obs_images=not args.no_save_obs,
        obs_extended=not args.no_obs_extended,
        topdown_current_only=args.topdown_current_only,
        topdown_scene_ids=sweep_ids,
        topdown_settle_seconds=max(0.0, args.topdown_settle),
    )


if __name__ == "__main__":
    main()
