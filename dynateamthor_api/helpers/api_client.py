from typing import Any

import requests


class ApiClient:
    def __init__(self, base_url: str, timeout: int = 20):
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout
        self.headers = {"Content-Type": "application/json"}

    def post(self, path: str, payload: dict, timeout: int | None = None) -> dict:
        url = self.base_url + path.lstrip("/")
        resp = requests.post(url, json=payload, headers=self.headers, timeout=timeout or self.timeout)
        resp.raise_for_status()
        return resp.json()

    # Convenience wrappers
    def select_scene(self, scene_id: int) -> dict:
        return self.post("v1/env/select_scene", {"scene_id": scene_id}, timeout=max(self.timeout, 90))

    def scene_reset(self) -> dict:
        return self.post("v1/env/scene_reset", {})

    def robot_setup(self, payload: dict) -> dict:
        return self.post("v1/env/robot_setup", payload)

    def robot_teleport(self, payload: dict) -> dict:
        return self.post("v1/agent/robot_teleport", payload)

    def move_object(self, payload: dict) -> dict:
        return self.post("v1/env/move_object", payload)

    def get_object_info(self, object_list: list[str]) -> dict:
        return self.post("v1/info/get_object_info", {"object_list": object_list})

    def get_object_type(self, object_list: list[str]) -> dict:
        return self.post("v1/info/object_type", {"object_list": object_list})

    def get_object_neighbors(self, object_list: list[str]) -> dict:
        return self.post("v1/info/get_object_neighbors", {"object_list": object_list})

    def get_reachable_points(self, step_size: float = 0.1) -> dict:
        return self.post("v1/info/get_reachable_points", {"step_size": step_size})

    def get_robot_status(self, robot_list: list[str]) -> dict:
        return self.post("v1/info/robot_status", {"robot_list": robot_list})

    def get_obs(self, robot_list: list[str], **extra: Any) -> dict:
        payload: dict = {"robot_list": robot_list}
        payload.update(extra)
        return self.post("v1/env/get_obs", payload)

    def pick(self, robot_name: str, object_name: str) -> dict:
        return self.post("v1/agent/pick", {robot_name: {"object_name": object_name}})

    def place(self, robot_name: str, object_name: str, target_location: list[float], target_rotation: list[float]) -> dict:
        return self.post(
            "v1/agent/place",
            {
                robot_name: {
                    "object_name": object_name,
                    "target_location": target_location,
                    "target_rotation": target_rotation,
                }
            },
        )

    def joint_pull(self, robot_list: list[str], object_name: str, direction: str) -> dict:
        return self.post(
            "v1/agent/joint_pull",
            {"robot_list": robot_list, "object_name": object_name, "direction": direction},
        )

