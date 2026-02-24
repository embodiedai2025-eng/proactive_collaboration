import math
import pprint
import time
from collections import deque

#from oracle import Oracle
from ultilities import get_2d_distance, parse_coordinates_from_string, turn_to_target
from unity.ue_api import (
    get_object_info,
    get_object_type,
    get_reachable_points,
    get_robot_status,
    move_object,
    pick_up,
    place_object,
    pull_object,
    robot_setup,
    robot_teleport,
    scene_reset,
    select_scene,
)

# from ultilities import get_2d_distance


def robot_go_to_point(robotName, robot_current_position, robot_current_rotation, target_position):# in list form
    """robot action GoToPoint

        Args:
            target position(list) :[0, 0, 0] 
        Returns:
           next_location, next_rotation
    """
    turn_to_target_input = turn_to_target(robotName, robot_current_position, robot_current_rotation, target_position)
    next_location = target_position
    next_rotation = turn_to_target_input[robotName]['rotation']
    robot_teleport(turn_to_target_input)
    go  = {
            robotName:
            {
                "location": next_location,
                "rotation": next_rotation
            }
        }
    robot_teleport(go)
    return next_location, next_rotation

def robot_pick_obj(robot_name, object_name): 
    """
    Attempts to pick up an object by checking several conditions:
    1. If the object is pickable.
    2. If the robot has a hand and is not holding another object.
    3. If the object is within the robot's arm reach.
    4. If the object is at an acceptable height.
    If all conditions are met, the robot will proceed to pick up the object.

    Args:
    - robot_name (str): The name of the robot.
    - object_name (str): The name of the object to pick up.

    Returns:
    - tuple: (result (bool), reason (str))
    """

    # Check if the object is pickable (must be "PickUpableObjects")
    object_type = get_object_type({"object_list": [object_name]})['data'].get(object_name)
    if object_type != "PickUpableObjects":
        return False, "Object can't be picked up"  # Failure if object is not pickable
    
    # Retrieve robot status to check hand availability and whether it's holding an object
    robot_status = get_robot_status({"robot_list": [robot_name]})
    robot_hand_status = robot_status[robot_name].get('hand')  
    robot_is_holding = robot_status[robot_name].get('isHold')  

    # Retrieve robot's arm length and height limits for pickup
    arm_length = float(robot_status[robot_name].get('armLength'))  
    # robot_high = float(robot_status[robot_name].get('robotHigh'))  
    # robot_low = float(robot_status[robot_name].get('robotLow'))  

    # Check if robot has a hand and if it's holding an object
    if robot_hand_status == 'False':  
        return False, "Robot can't pick up (no hand)"
    if robot_is_holding == 'True':  
        return False, "Robot is holding an item"

    # Check if the object is within the robot's arm reach (2D distance)
    robot_and_object_info = get_object_info({"object_list": [object_name, robot_name]})
    object_location = robot_and_object_info[object_name].get('location')  
    robot_location = robot_and_object_info[robot_name].get('location')  
    if get_2d_distance(object_location, robot_location) > arm_length:  
        return False, "Out of arm range"  # Failure if object is out of reach

    # Check if the object's height is within the robot's allowable height range
    # if object_location[1] > robot_high:  # Too high
    #     return False, "Object is too high"
    # if object_location[1] < robot_low:  # Too low
    #     return False, "Object is too low"

    # Simulate the robot picking up the object
    robot_pickup = {robot_name: {"object_name": object_name}}  
    pick_up(robot_pickup)  # Simulate the pickup action
    
    return True, "None"  # Success if all conditions are met

def robot_place_obj(robot_name, target_receiver):
    """
    Attempts to place an object in a specified location by checking several conditions:
    1. If the robot has a hand and is holding an object.
    2. If the object is placeable (receptacle).
    3. If the object is within the robot's arm reach.
    4. If the object is within the robot's allowable height range.
    If all conditions are met, the robot will proceed to place the object.

    Args:
    - robot_name (str): The name of the robot.
    - target_receiver (str): The name of the target receiver (location or container) where the object will be placed.

    Returns:
    - tuple: (result (bool), reason (str))
    """
    
    # Retrieve robot status to check hand availability and whether it's holding an object
    robot_status = get_robot_status({"robot_list": [robot_name]})
    robot_hand_status = robot_status[robot_name].get('hand')  
    robot_is_holding = robot_status[robot_name].get('isHold')  

    # Retrieve the robot's arm reach and height limits for placing objects
    arm_length = float(robot_status[robot_name].get('armLength'))  

    # Check if robot has a hand and is holding an object
    if robot_hand_status == 'False':
        return False, "Robot can't Place (no hand)"
    if robot_is_holding == 'False':
        return False, "Robot is not holding an item"

    # Check if the target receiver is placeable (receptacle)
    data = get_object_type({"object_list": [target_receiver]})['data']
    if data.get(target_receiver + "Placeable") != "True":  
        return False, "Target receiver is not receptacle"

    # Get available placement points for the object in the target receiver
    edge_points_list = parse_coordinates_from_string(data.get(target_receiver + "EdgePoints"))
    place_points_list = parse_coordinates_from_string(data.get(target_receiver + "PutPoints"))

    # Check if the object is within the robot's arm reach (2D distance)
    robot_location = get_object_info({"object_list": [robot_name]})[robot_name].get('location')  
    target_location = next((point for point in edge_points_list if get_2d_distance(point, robot_location) < 2 * arm_length), robot_location)  

    # If no valid placement location is found, return failure
    if target_location == robot_location:
        return False, "Too far"

    # Place the object at the nearest valid locations
    target_put_location = min(place_points_list, key=lambda point: get_2d_distance(point, robot_location))  
    # print("#############")
    # print(target_put_location)
    # print("#############")
    # Simulate placing the object
    robot_place = {robot_name: {"object_name": robot_status[robot_name].get('Holding'), "target_location": target_put_location, "target_rotation": [0, 0, 0]}}
    place_object(robot_place)

    return True, "None"  # Success

def robot_pull_obj(robot_name_list, moveable_object_name, needed_force, direction):
    """
    Attempts to pull a moveable object by checking several conditions:
    1. If the object is moveable (of type "MoveableObjects").
    2. If each robot in the robot list has a hand and is not holding another object.
    3. If the robot is within arm reach of the object.
    4. If the total strength of the robots is sufficient to pull the object.

    If all conditions are met, the robots will attempt to pull the object in the specified direction.

    Args:
    - robot_name_list (list): List of robot names attempting to pull the object.
    - moveable_object_name (str): The name of the moveable object to pull.
    - needed_force (float): The total force required to pull the object.
    - direction (str): The direction in which to pull the object.

    Returns:
    - tuple: (result (bool), reason (str), reason_details (str))
    """
    # Initialize result, reason, and reason_details
    result = False
    reason = ""
    reason_details = {}

    # Step 1: Check if the object is moveable (must be "MoveableObjects")
    data = get_object_type({"object_list": [moveable_object_name]})['data']
    object_type = data.get(moveable_object_name)
    if object_type != "MoveableObjects":
        return result, "Object can't be moved", reason_details  # Failure if not moveable

    # Step 2: Calculate total strength of robots
    joint_force = 0
    for robot_name in robot_name_list:
        # Retrieve robot status (hand availability, holding status, strength)
        robot_status = get_robot_status({"robot_list": [robot_name]})
        robot_hand_status = robot_status[robot_name].get('hand')  
        robot_is_holding = robot_status[robot_name].get('isHold')  
        robot_strength = float(robot_status[robot_name].get('strength'))

        # Check if robot has a hand and isn't holding an object
        if robot_hand_status == 'False':
            reason_details[robot_name] = f"{robot_name} can't pull (no hand);"
            continue
        if robot_is_holding == 'True':
            reason_details[robot_name] =  f"{robot_name} is holding an item;"
            continue

        # Get available edge points and check if the object is within arm reach
        edge_points_list = parse_coordinates_from_string(data.get(moveable_object_name + "EdgePoints"))
        robot_location = get_object_info({"object_list": [robot_name]})[robot_name].get('location')
        target_location = next((point for point in edge_points_list if get_2d_distance(point, robot_location) < 2 * float(robot_status[robot_name].get('armLength'))), robot_location)

        if target_location == robot_location:
            reason_details[robot_name] =  f"{robot_name} is too far away;"
            continue

        # Accumulate robot strength
        joint_force += robot_strength
        reason_details[robot_name] =  f"{robot_name} has strength {robot_strength};"

    # Step 3: Check if total strength is enough
    if joint_force < needed_force:
        return False, "Lack of strength", reason_details

    # Step 4: Attempt to pull the object in the specified direction
    pullInfos = {
        "robot_list": robot_name_list,
        "object_name": moveable_object_name,
        "direction": direction
    }
    reason = pull_object(pullInfos)['result']
    if reason != 'Success':
        return False, reason, reason_details  # Failure if pull fails

    return True, reason, reason_details  # Success



if __name__ == '__main__':
    def check_pick_up():
        robot_pool = {
            "Robot_1": {
            "type": "ManipulaTHOR",
            "name": "Robot_1",
            "init_location": [-3.216, 0.90,-3.064],
            "init_rotation": [0, -90, 0]
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
            "init_rotation": [0, 180, 0],
            "arm_length":2,
            "robot_high":2,
            "robot_low": 0,
            "strength":80            
            }
        }
        select_scene('0')
        time.sleep(2)
        robot_setup(robot_pool)

        moveObjects = {
            "Robot_1":
            {
                "init_location":[-2.716, 0.9, -3.064],
                "init_rotation" : [0.0, 270.0, 0.0]
            },
            "Robot_2":
            {
                "init_location":[-2.716, 0.9, -1.609],
                "init_rotation" : [0.0, 270.0, 0.0]
            },
            "Robot_0":
            {
                "init_location":[-5.608, 0.90, -2.101],
                "init_rotation" : [0.0, -180, 0.0]
            }
        }
        move_object(moveObjects)
        pull_object()
        pprint.pprint(robot_pick_obj("Robot_1", "Pillow_11"))
        pprint.pprint(robot_pick_obj("Robot_2", "Pillow_11"))
        pprint.pprint(robot_pick_obj("Robot_0", "Pillow_11"))
        # pick_up(robotPickup)

    def check_place_obj():
        check_pick_up()
        pprint.pprint(robot_place_obj("Robot_1", "Bed_01"))
        pprint.pprint(robot_place_obj("Robot_2", "Bed_01"))
        pprint.pprint(robot_place_obj("Robot_0", "Bed_01"))

    def check_pull_obj():
        robot_pool = {
            "Robot_1": {
            "type": "ManipulaTHOR",
            "name": "Robot_1",
            "init_location": [-3.216, 0.90,-3.064],
            "init_rotation": [0, -90, 0],
            "arm_length":2,
            "strength":100 
            },
            "Robot_2": {
                "type": "StretchRE",
                "name": "Robot_2",
                "init_location": [-3.216, 0.90, -1.609],
                "init_rotation": [0, -90, 0],
                "arm_length":2,
            "strength":70 
            
            },
            "Robot_0": {
            "type": "LoCoBot",
            "name": "Robot_0",
            "init_location": [-5.9592, 0.90, -0.201],
            "init_rotation": [0, 180, 0],
            "arm_length":2,
            "robot_high":2,
            "robot_low": 0,
            "strength":100            
            }
        }
        select_scene('0')
        time.sleep(2)
        robot_setup(robot_pool)
        robot_name_list = ['Robot_1', 'Robot_2']
        moveable_object_name = 'Bed_01'
        needed_force = 40
        direction = '(1,0,0)'
        pprint.pprint(robot_pull_obj(robot_name_list, moveable_object_name, needed_force, direction))
        time.sleep(1)
        robot_name_list = ['Robot_1', 'Robot_2']
        moveable_object_name = 'Bed_01'
        needed_force = 1000
        direction = '(-1,0,0)'
        pprint.pprint(robot_pull_obj(robot_name_list, moveable_object_name, needed_force, direction))

    check_pull_obj()
    #pprint.pprint(get_robot_status({"robot_list": ["Robot_0"]}))