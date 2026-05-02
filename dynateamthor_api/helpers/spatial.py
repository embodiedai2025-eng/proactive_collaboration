import math

from .parsers import get_2d_distance, parse_coordinates_from_string


def is_point_in_quadrilateral(points: list[list[float]], point: list[float]) -> bool:
    """Check whether 2D point [x, z] lies in a 4-point polygon [x, z]."""
    if len(points) != 4:
        raise ValueError("Exactly 4 points are required.")

    x, y = point[0], point[1]
    inside = False
    n = len(points)
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        intersects = ((y1 > y) != (y2 > y)) and (
            x < (x2 - x1) * (y - y1) / ((y2 - y1) if (y2 - y1) != 0 else 1e-9) + x1
        )
        if intersects:
            inside = not inside
    return inside


def get_nearest_edge_point(robot_loc: list[float], object_type_data: dict, object_name: str) -> list[float]:
    edge_points = parse_coordinates_from_string(object_type_data[object_name + "EdgePoints"])
    minima = float("inf")
    res = edge_points[0]
    for point in edge_points:
        dis = get_2d_distance(point, robot_loc)
        if dis < minima:
            minima = dis
            res = point
    return res


def obs_get_nearest_edge_point_list(
    robot_loc: list[float], object_type_data: dict, object_name: str, avoid_loc_list: list[list[float]]
) -> list[float]:
    if not avoid_loc_list:
        return get_nearest_edge_point(robot_loc, object_type_data, object_name)

    edge_points = parse_coordinates_from_string(object_type_data[object_name + "EdgePoints"])
    min_distance = float("inf")
    closest_point = edge_points[0]

    for point in edge_points:
        is_valid = True
        for avoid_loc in avoid_loc_list:
            if get_2d_distance(point, avoid_loc) < 0.5:
                is_valid = False
                break
        if is_valid:
            distance = get_2d_distance(point, robot_loc)
            if distance < min_distance:
                min_distance = distance
                closest_point = point

    return closest_point


def turn_to_target(robot_position: list[float], robot_rotation: list[float], target_position: list[float]) -> list[float]:
    """Return new euler rotation with yaw facing target (x-z plane)."""
    dx = target_position[0] - robot_position[0]
    dz = target_position[2] - robot_position[2]
    target_angle = math.degrees(math.atan2(dx, dz))
    target_rotation = robot_rotation.copy()
    target_rotation[1] = target_angle
    return target_rotation

