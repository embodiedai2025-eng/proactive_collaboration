from .spatial import obs_get_nearest_edge_point_list, turn_to_target


def goto_point(client, robot_name: str, target_loc: list[float]) -> dict:
    """
    Lightweight navigation helper:
    - query robot pose
    - rotate toward target
    - teleport to target point
    """
    info = client.get_object_info([robot_name])
    if robot_name not in info:
        return {"ok": False, "reason": f"Robot '{robot_name}' not found.", "detail": {}}

    robot_loc = info[robot_name]["location"]
    robot_rot = info[robot_name]["rotation"]
    facing_rot = turn_to_target(robot_loc, robot_rot, target_loc)
    teleport_body = {robot_name: {"location": target_loc, "rotation": facing_rot}}
    resp = client.robot_teleport(teleport_body)
    return {"ok": True, "reason": "teleported", "detail": resp}


def goto_object(
    client,
    robot_name: str,
    object_name: str,
    avoid_locs: list[list[float]] | None = None,
) -> dict:
    """
    Navigate robot to a nearest edge point of object, then face the object.
    """
    avoid_locs = avoid_locs or []
    infos = client.get_object_info([robot_name, object_name])
    if robot_name not in infos:
        return {"ok": False, "reason": f"Robot '{robot_name}' not found.", "detail": infos}
    if object_name not in infos:
        return {"ok": False, "reason": f"Object '{object_name}' not found.", "detail": infos}

    object_type_data = client.get_object_type([object_name]).get("data", {})
    edge_key = object_name + "EdgePoints"
    if edge_key not in object_type_data:
        return {"ok": False, "reason": f"Missing {edge_key} in object_type response.", "detail": object_type_data}

    robot_loc = infos[robot_name]["location"]
    target_loc = obs_get_nearest_edge_point_list(robot_loc, object_type_data, object_name, avoid_locs)

    goto_res = goto_point(client, robot_name, target_loc)
    if not goto_res["ok"]:
        return goto_res

    updated = client.get_object_info([robot_name, object_name])
    new_robot_loc = updated[robot_name]["location"]
    new_robot_rot = updated[robot_name]["rotation"]
    object_loc = updated[object_name]["location"]
    face_rot = turn_to_target(new_robot_loc, new_robot_rot, object_loc)
    face_resp = client.robot_teleport({robot_name: {"location": new_robot_loc, "rotation": face_rot}})

    return {
        "ok": True,
        "reason": "arrived_and_facing_target",
        "detail": {
            "target_loc": target_loc,
            "goto_response": goto_res["detail"],
            "face_response": face_resp,
        },
    }


def goto_room(client, robot_name: str, room_name: str, room_anchor_map: dict[str, list[float]]) -> dict:
    """
    Navigate by predefined room anchor points.
    Keeps this helper architecture-light and environment-agnostic.
    """
    if room_name not in room_anchor_map:
        return {"ok": False, "reason": f"Room '{room_name}' not in room_anchor_map.", "detail": {}}
    return goto_point(client, robot_name, room_anchor_map[room_name])

