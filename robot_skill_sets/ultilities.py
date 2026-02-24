import json
import math
import os
import pprint
import re
import time

import cv2
import matplotlib.path as mpath
import numpy as np
from unity.ue_api import (
    get_object_info,
    get_object_type,
    get_reachable_points,
    getApple,
    move_object,
    moveApple,
    robot_setup,
    robot_teleport,
    scene_reset,
    select_scene,
    setup,
    stepsize,
    teleport,
)


def get_moving_direction(Moveable_object, trapped_object):
    if trapped_object is None:
        raise ValueError("trapped_object cannot be None in get_moving_direction")
    
    getObjectType = {"object_list": [Moveable_object]}
    edge_points = parse_coordinates_from_string(
        get_object_type(getObjectType)["data"][Moveable_object + "EdgePoints"]
    )

    getObjectLoc = {"object_list": [trapped_object]}
    object_state = get_object_info(getObjectLoc)[trapped_object]
    trapped_location = object_state["location"]

    # Initialize movement direction
    movement_direction = [0, 0, 0]

    # Check x direction
    all_x_greater = all(
        edge_point[0] > trapped_location[0] for edge_point in edge_points
    )
    all_x_lesser = all(
        edge_point[0] < trapped_location[0] for edge_point in edge_points
    )

    if all_x_greater:
        movement_direction = [1, 0, 0]  # Move in the positive x direction
    elif all_x_lesser:
        movement_direction = [-1, 0, 0]  # Move in the negative x direction

    # Check z direction
    all_z_greater = all(
        edge_point[2] > trapped_location[2] for edge_point in edge_points
    )
    all_z_lesser = all(
        edge_point[2] < trapped_location[2] for edge_point in edge_points
    )

    if all_z_greater:
        movement_direction = [0, 0, 1]  # Move in the positive z direction
    elif all_z_lesser:
        movement_direction = [0, 0, -1]  # Move in the negative z direction

    return movement_direction


def is_point_in_quadrilateral(points, point):
    """
    Check if a point is inside a quadrilateral defined by four points.
    :param points: Four vertices of the quadrilateral, in list form [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    :param point: Point to check [x, y]
    :return: True if point is inside the quadrilateral, False otherwise
    """
    if len(points) != 4:
        raise ValueError("Must provide four points to define a quadrilateral")

    # Ensure points are arranged clockwise or counterclockwise (simple implementation, assumes user input is correct)
    polygon = mpath.Path(points)
    return polygon.contains_point(point)


def obs_get_nearest_edge_point_list(robot_loc, object_name, avoid_loc_list):
    if avoid_loc_list == []:
        return get_nearest_edge_point(robot_loc, object_name)

    getObjectType = {"object_list": [object_name]}
    edge_points = parse_coordinates_from_string(
        get_object_type(getObjectType)["data"][object_name + "EdgePoints"]
    )
    # Initialize min_distance to infinity
    min_distance = float("inf")
    closest_point = edge_points[0]

    for point in edge_points:
        # Check validity of the point
        is_valid = True
        for avoid_loc in avoid_loc_list:
            if get_2d_distance(point, avoid_loc) < 0.5:
                is_valid = False
                break

        # Update closest point if valid and distance is smaller
        if is_valid:
            distance = get_2d_distance(point, robot_loc)
            if distance < min_distance:
                min_distance = distance
                closest_point = point

    return closest_point


def get_nearest_edge_point(robot_loc, object_name):
    getObjectType = {"object_list": [object_name]}
    edge_points = parse_coordinates_from_string(
        get_object_type(getObjectType)["data"][object_name + "EdgePoints"]
    )
    minima = 1000
    res = edge_points[0]
    for point in edge_points:
        dis = get_2d_distance(point, robot_loc)
        if dis < minima:
            minima = dis
            res = point
    return res


def relation_to_str(objects, relation_dict: dict):
    object_str = ""
    # for obj in objects:
    #     object_str += f"{obj}"
    #     if obj != objects[-1]:
    #         object_str += ", "
    #     else:
    #         object_str += ". "
    for obj, relations in relation_dict.items():
        if relations["on"]:
            object_str += f"{obj} is on "
            for on_obj in relations["on"]:
                object_str += f"{on_obj}"
                if on_obj != relations["on"][-1]:
                    object_str += ", "
            object_str += ". "
        if relations["between"]:
            for between_objs in relations["between"]:
                object_str += (
                    f"{obj} is between {between_objs[0]} and {between_objs[1]}."
                )

    return object_str


def parse_relations(object_neighbors):
    relations = {}

    for obj, neighbors in object_neighbors.items():
        if obj in ["error_info", "is_success"]:  # Skip non-object keys
            continue

        on_relations = set()
        between_relations = set()

        for rel_pos, neighbor in neighbors.items():
            # Convert string positions to tuples
            rel_pos_tuple = tuple(map(float, rel_pos.strip("()").split(",")))

            # Check "on" relation: y-axis is -1
            if rel_pos_tuple == (0.0, -1.0, 0.0):
                on_relations.add(neighbor)

            # Check "between" relation: Opposite x or z axis
            for other_rel_pos, other_neighbor in neighbors.items():
                if neighbor == other_neighbor or other_neighbor == obj:
                    continue

                other_rel_pos_tuple = tuple(
                    map(float, other_rel_pos.strip("()").split(","))
                )

                # Opposite x-axis
                if (
                    rel_pos_tuple[0] == -other_rel_pos_tuple[0]
                    and rel_pos_tuple[1:] == other_rel_pos_tuple[1:]
                ):
                    between_relations.add(tuple(sorted([neighbor, other_neighbor])))

                # Opposite z-axis
                if (
                    rel_pos_tuple[2] == -other_rel_pos_tuple[2]
                    and rel_pos_tuple[:2] == other_rel_pos_tuple[:2]
                ):
                    between_relations.add(tuple(sorted([neighbor, other_neighbor])))

        relations[obj] = {
            "on": list(on_relations),
            "between": list(between_relations),
        }

    return relations


def parse_coordinates_from_string(input_str):
    """
    Parses a string of 3D coordinates into a list of lists of floats.

    The input string is expected to contain tuples of coordinates, separated by semicolons.
    Each tuple is in the format "(x, y, z)" where x, y, and z are floating-point numbers.

    Args:
    - input_str (str): A string containing 3D coordinates separated by semicolons.

    Returns:
    - list: A list of lists, where each inner list contains three floats representing a 3D coordinate.
    """

    # Step 1: Clean the input string (remove extra spaces and ensure format)
    input_str = input_str.strip().replace(" ;", ";").replace("; ", ";")

    # Step 2: Use regex to extract all tuples of 3D coordinates (x, y, z)
    coordinates = re.findall(
        r"\((-?\d+\.\d+),\s*(-?\d+\.\d+),\s*(-?\d+\.\d+)\)", input_str
    )
    # 'coordinates' now holds a list of tuples in the format: [('x1', 'y1', 'z1'), ('x2', 'y2', 'z2'), ...]

    # Step 3: Convert the string values of coordinates into floats and store them in a list
    coordinate_list = [[float(x), float(y), float(z)] for x, y, z in coordinates]
    # Each tuple ('x', 'y', 'z') is converted into a list of floats [x, y, z]

    return coordinate_list  # Return the list of coordinates


def turn_to_target(agent, robot_position, robot_rotation, target_position):
    # robot_position = 6d array
    if target_position and robot_position:
        dx = target_position[0] - robot_position[0]
        dz = target_position[2] - robot_position[2]
        target_angle = math.degrees(math.atan2(dx, dz))
        target_rotation = robot_rotation.copy()
        target_rotation[1] = target_angle
        # action = ('agent_control', 'turn', {'agent_ids': [self.agent_idx], 'pitch': 0, 'yaw': -target_angle})
        teleport_action = {
            agent: {"location": robot_position[:3], "rotation": target_rotation}
        }
        # robot_teleport(teleport_action)
        return teleport_action


def get_2d_distance(point1, point2):
    """
    Calculate the 2D distance (x, z) between two 3D points.

    Args:
    point1 (list): The first point [x1, y1, z1]
    point2 (list): The second point [x2, y2, z2]

    Returns:
    float: The 2D distance between the points based on x and z coordinates.
    """
    x1, _, z1 = point1  # Unpack the x, y, z components, ignore y
    x2, _, z2 = point2  # Unpack the x, y, z components, ignore y

    # Calculate the 2D distance (only using x and z components)
    distance = math.sqrt((x2 - x1) ** 2 + (z2 - z1) ** 2)
    return distance


def parse_reachable_points(raw_reachable_points):
    """
    Parse the raw reachable points data and extract the 2D coordinates (x, z) for each point.

    Args:
    raw_reachable_points (list): A list of raw points, where each point is a string representing a tuple (x, y, z).

    Returns:
    set: A set containing the 2D coordinates (x, z) of each reachable point.
    """
    reachable_points = set()

    # Iterate over the raw reachable points
    for point in raw_reachable_points:
        # Convert the string representation of the point into an actual tuple
        point = eval(point)  # Assumes point is a string like "(x, y, z)"

        # Extract x, y, z coordinates (we will only use x and z for 2D movement)
        x, y, z = point

        # Add the (x, z) coordinates to the set of reachable points
        reachable_points.add((x, z))

    return reachable_points


if __name__ == "__main__":
    # robot_name = 'Robot_1'
    # object_name = 'Bed_01'
    # object_name2 = 'Pillow_11'
    # pprint.pprint(get_moving_direction(object_name, object_name2))
    # InfoInput = {
    #             "object_list":[ robot_name, object_name]
    #             }
    # infos = get_object_info(InfoInput)
    # robot_position = infos[robot_name]['location']
    # robot_rotation = infos[robot_name]['rotation']
    # object_name = 'Bed_01'
    # target_location = infos[object_name]['location']
    # pprint.pprint(turn_to_target(robot_name, robot_position, robot_rotation, target_location))
    # robot_teleport(turn_to_target(robot_name, robot_position, robot_rotation, target_location))
    object_name = "Bed_01"
    object_name2 = "Pillow_11"
    pprint.pprint(get_moving_direction(object_name, object_name2))
