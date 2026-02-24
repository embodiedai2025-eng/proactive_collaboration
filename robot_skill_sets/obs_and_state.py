import math
import pprint
import time
from collections import deque

# import keyboard
import numpy as np
from ultilities import parse_reachable_points
from unity.ue_api import (
    get_object_info,
    get_object_neighbors,
    get_reachable_points,
    get_robot_obs,
    get_robot_status,
    move_object,
    pick_up,
    robot_setup,
    robot_teleport,
    scene_reset,
    select_scene,
)


def single_robot_observation(robot_name):
    """
    Gather observation data for a single robot, including the list of objects it observes, 
    detailed information about those objects, and the neighbors of those objects.

    Args:
    robot_name (str): The name of the robot for which observations are being gathered.

    Returns:
    tuple: A tuple containing:
        - obj_list (list): A list of objects observed by the robot.
        - obj_infos (dict): A dictionary containing information about the observed objects.
        - objs_neighbors (dict): A dictionary containing the neighbors of the observed objects.
    """
    # Create a dictionary to hold the robot list with the robot name
    robot_input = {"robot_list": [robot_name]}

    # Get the list of objects observed by the robot
    obs = get_robot_obs(robot_input)
    observed_objects = obs.get(robot_name)

    # Create input for fetching object details using the observed objects
    if observed_objects is not None:
        observed_objects = list(set(observed_objects))
        object_input = {"object_list": observed_objects}

        # Fetch detailed information about the observed objects
        object_infos = get_object_info(object_input)

        # Fetch the neighbors of the observed objects
        object_neighbors = get_object_neighbors(object_input)
    else:
         object_infos = {}
         object_neighbors = {}
    return observed_objects, object_infos, object_neighbors

def single_robot_state(robot_name, step_size=0.2):
    """
    Retrieve the current state of a robot, including its location, possible next movement points,
    and whether it is holding an object.

    Args:
    robot_name (str): The name of the robot whose state is being retrieved.
    step_size (float): The maximum step size for the robot to move (default 0.2 meters).

    Returns:
    tuple: A tuple containing:
        - robot_state (dict): A dictionary containing the robot's current state information.
        - next_points (set): A set of 3D points the robot can potentially move to based on its current location.
        - is_hold (dict): The current status of the robot, including whether it is holding an object.
    """
    # Fetch the current state of the robot (e.g., its location)
    state_input = {"object_list": [robot_name]}
    robot_state = get_object_info(state_input)

    # Extract the 2D location (x, z) of the robot
    robot_location_2d = (robot_state[robot_name]['location'][0], robot_state[robot_name]['location'][2])

    # Retrieve the set of reachable points for the robot
    reachable_points_gt = get_reachable_points()["reachable_point"]
    reachable_points_2d = parse_reachable_points(reachable_points_gt)

    # Initialize a set to store the potential next points for the robot
    next_points = set()

    # Identify the next points that the robot can potentially move to based on the step size
    for point in reachable_points_2d:
        if np.linalg.norm(np.array(point) - np.array(robot_location_2d)) < step_size:
            next_points.add((point[0], robot_state[robot_name]['location'][1], point[1]))

    # Fetch the robot's holding status (whether it is currently holding an object)
    robot_status_input = {"robot_list": [robot_name]}
    robot_status = get_robot_status(robot_status_input)

    return robot_state, next_points, robot_status

if __name__ == '__main__':
    robot_pool = {
        "Robot_1": {
        "type": "ManipulaTHOR",
        "name": "Robot_1",
        "init_location": [-3.216, 0.90,-3.064],
        "init_rotation": [0, -90, 0],
        "arm_length":1,
        "robot_high":0.5,
        "robot_low": 0.2,
        "strength":80
        },
        "Robot_2": {
            "type": "StretchRE",
            "name": "Robot_2",
            "init_location": [-3.216, 0.90, -1.609],
            "init_rotation": [0, -90, 0]
        },
        "Robot_0": {
        "type": "LoCoBot",
        "name": "Robot_0",
        "init_location": [-5.9592, 0.90, -0.201],
        "init_rotation": [0, 180, 0]
        }
    }
    select_scene('0')
    time.sleep(2)
    robot_setup(robot_pool)

    current_info = {}
    for robot in robot_pool: 
            current_info[robot] = {}
             # update observations(seen objects//object locations//object related locations)
            current_info[robot]["seen_object_list"], current_info[robot]["object_locations"], current_info[robot]["object_neighbors"] = single_robot_observation(robot)
            # update states infos(current location rotation//reachable points// action status(is hold or not))
            current_info[robot]["current_position"], current_info[robot]["reachable_points"], current_info[robot]["self_status"] = single_robot_state(robot)

    pprint.pprint(current_info)