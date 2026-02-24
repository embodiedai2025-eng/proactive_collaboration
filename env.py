import concurrent.futures
import copy
import json
import os
import pprint
import random
import sys
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

from termcolor import colored

# Add the directory containing 'ultilities.py' to the sys.path
script_dir = os.path.dirname(
    os.path.abspath(__file__)
)  # Get the current script's directory
module_dir = os.path.join(
    script_dir, "robot_skill_sets"
)  # The folder where 'ultilities.py' is located
sys.path.append(module_dir)


from constants import EDGES, EXPLOREPOINTS
from robot_skill_sets.actions import (
    robot_go_to_point,
    robot_pick_obj,
    robot_place_obj,
    robot_pull_obj,
)
from robot_skill_sets.obs_and_state import single_robot_observation, single_robot_state
from robot_skill_sets.sub_skill_executor import (
    robot_go_to_obj_path,
    robot_go_to_point_path,
)
from robot_skill_sets.ultilities import (
    get_2d_distance,
    get_moving_direction,
    get_nearest_edge_point,
    is_point_in_quadrilateral,
    obs_get_nearest_edge_point_list,
    parse_coordinates_from_string,
    parse_relations,
    relation_to_str,
    turn_to_target,
)
from robot_skill_sets.unity.ue_api import (
    get_object_info,
    get_object_neighbors,
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


class Env:
    def __init__(self, robot_pool, robot_team, scene_index="0"):
        self.scene_index = copy.deepcopy(scene_index)
        self.robot_pool = copy.deepcopy(robot_pool)  # with identities and locations
        self.robot_team = copy.deepcopy(robot_team)  # only names
        self.robot_map = {}
        self.rooms = ['bedroom', 'kitchen','livingroom','diningroom','bathroom', 'office', 'hallway']
        # count of planned actions
        self.action_step = 0
        # sum of every robot path
        self.total_route_step = 0
        # sum of max time cost in each planed actions 
        self.total_time_step = 0
        # max time step cost of robots in current action step
        self.this_actions_time_step = 0

        self.team_each_time_step = {}
        for robot in robot_pool:
            self.robot_map[robot] = {}
            self.robot_map[robot]["robot_plan"] = ""
            self.robot_map[robot]["robot_route"] = []
            self.robot_map[robot]["robot_explore_map"] = copy.deepcopy(
                EXPLOREPOINTS.get(self.scene_index)
            )
            self.robot_map[robot]["robot_room"] = ""

            if robot_pool[robot].get("speed"):
                self.robot_map[robot]["robot_speed"] = robot_pool[robot].get("speed")
            else:
                self.robot_map[robot]["robot_speed"] = 200

    def co_act(self, robot_action: dict):
        """
        Return the robot action
        Args:
            robot_action (dict): {robot_name: action, ...}
        Returns:
            action_result (dict): {robot_name: {flag, message, observation}, ...}
        """
        self.action_step += 1
        self.this_actions_time_step = 5
        self.total_route_step += 5 * len(robot_action)
        
        pull_object_and_robot = defaultdict(list)  # {object_name: robot_list}
        pull_object_robot_direction = {}           # {object_name: direction}
        action_result = {}                         # {robot_name: {flag, message, observation}}

        lock = threading.Lock()

        # Phase 1: Collect all [gopull] action information
        for robot, action in robot_action.items():
            action = action.strip()
            if action.startswith("[gopull]"):
                object_name = action.split("<")[1].split(">")[0]
                direction = action.split("[")[2].split("]")[0]
                direction = [int(x.strip()) for x in direction.split(",")]

                # Thread-safe update of pull_object_and_robot and pull_object_robot_direction
                with lock:
                    pull_object_and_robot[object_name].append(robot)
                    if object_name not in pull_object_robot_direction:
                        pull_object_robot_direction[object_name] = direction

        # Phase 2: Execute all actions in parallel
        def execute_non_gopull_action(robot, action):
            """Execute non-[gopull] actions and return results."""
            flag = False
            message = None
            observation = None

            if action.startswith("[explore]"):
                room = action.split("<")[1].split(">")[0]
                if room not in self.rooms:
                    flag = False
                    message = f"{room} is not exist."
                else:
                    flag, observation = self.explore(robot, room)
                    if not flag:
                        message = "on the way"

            elif action.startswith("[gopick]"):
                object_name = action.split("<")[1].split(">")[0]
                flag, message, observation = self.go_pick_obj(robot, object_name)

            elif action.startswith("[goplace]"):
                object_name = action.split("<")[1].split(">")[0]
                flag, message, observation = self.go_place_obj(robot, object_name)

            elif action.startswith("[request_new_member]"):
                flag = True
                message = None
                observation = None

            elif action.startswith("[wait]"):
                self.robot_map[robot]["robot_plan"] = "[wait]"
                flag = True
                message = None
                observation = None

            else:
                flag = False
                message = "Invalid action"
                observation = None

            return robot, {
                "flag": flag,
                "message": message,
                "observation": observation,
            }

        def execute_joint_gopull(object_name, robot_list, direction):
            """Execute [gopull] actions and return results."""
            joint_go_pull_ret = self.joint_go_pull(robot_list, object_name, direction)
            results = {}
            for robot in robot_list:
                ret = joint_go_pull_ret.get(robot, {})
                flag = ret.get('flag', False)
                goto_flag = ret.get('goto_flag', False)
                message = ret.get('message', '')
                observation = ret.get("obs", None)
                if not goto_flag:
                    message = "on the way"
                results[robot] = {
                    "flag": flag,
                    "message": message,
                    "observation": observation,
                }
            return results

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []

            # Submit all non-[gopull] action execution tasks
            for robot, action in robot_action.items():
                action = action.strip()
                if not action.startswith("[gopull]"):
                    futures.append(executor.submit(execute_non_gopull_action, robot, action))

            # Submit all [gopull] action execution tasks
            for object_name, robot_list in pull_object_and_robot.items():
                direction = pull_object_robot_direction[object_name]
                futures.append(executor.submit(execute_joint_gopull, object_name, robot_list, direction))

            # Collect results from all tasks
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if isinstance(result, tuple):
                    # Non-[gopull] action results
                    robot, action_info = result
                    action_result[robot] = action_info
                elif isinstance(result, dict):
                    # [gopull] action results
                    action_result.update(result)

        self.total_time_step += self.this_actions_time_step

        self.team_each_time_step[self.total_time_step] = {}
        self.team_each_time_step[self.total_time_step]['robot_team'] = copy.deepcopy(self.robot_team)
        self.team_each_time_step[self.total_time_step]['member_count'] = len(self.robot_team)
        self.team_each_time_step[self.total_time_step]['action_step'] = self.action_step
        self.team_each_time_step[self.total_time_step]['action'] = robot_action
        self.team_each_time_step[self.total_time_step]['total_route_step'] = self.total_route_step
        
        # Print concise summary instead of full pprint
        actions_str = ", ".join([f"{r}: {a}" for r, a in robot_action.items()])
        print(colored(f"TimeStep {self.total_time_step}: Team={self.robot_team}, Count={len(self.robot_team)}, ActionStep={self.action_step}, RouteStep={self.total_route_step}", 'cyan'))
        print(colored(f"Actions: {actions_str}", 'cyan'))
        return action_result


    def init_scene(self, scene_idx):
        self.scene_index = scene_idx
        for robot in self.robot_pool:
            self.robot_map[robot]["robot_explore_map"] = copy.deepcopy(
                EXPLOREPOINTS.get(self.scene_index)
            )
        select_scene(scene_idx)

    def init_misplaced_objects(self, object_list: list, locations: list, random_idx = 0):
        """
        Initializes misplaced objects by randomly assigning them to locations.

        Args:
            object_list (list): List of objects to be misplaced.
            locations (list): List of dictionaries, where each dictionary represents a location.

        Returns:
            str: "successful" if the operation is completed.
        """
        if random_idx:
            if len(object_list) > len(locations):
                raise ValueError("Not enough locations to assign all objects.")

            move_input = {}

            for obj in object_list:
                random_location = random.choice(locations)  # Select a random location.
                locations.remove(
                    random_location
                )  # Remove the selected location from the list.
                move_input[obj] = random_location  # Assign the location to the object.

            move_object(
                move_input
            )  # Assuming move_object is defined elsewhere in your code.
            # Removed verbose pprint - move_input and robot_pool info not needed in logs
            return "successful", move_input
        else:
            if len(object_list) > len(locations):
                raise ValueError("Not enough locations to assign all objects.")

            move_input = {}
            idx = 0
            for obj in object_list:
                fix_location = locations[idx]
                move_input[obj] = fix_location  # Assign the location to the object.
                idx += 1
            move_object(
                move_input
            )  # Assuming move_object is defined elsewhere in your code.
            # Removed verbose pprint - move_input and robot_pool info not needed in logs
            return "successful", move_input

    def set_robot(self, robot_name_list):
        """
        Set up a new team of robots.

        Args:
            robot_name_list (list): A list of robot names to form the new team, e.g., ["Robot_0", "Robot_1"].

        Returns:
            str:
                - "successful" if the team is set up correctly.
                - An error message indicating the wrong robot name if a provided name is not in the robot pool.
        """
        selected_robots = {}
        for name in robot_name_list:
            if name in self.robot_pool:
                selected_robots[name] = self.robot_pool[name]
            else:
                return "wrong robot name " + name
        robot_setup(selected_robots)
        for name in robot_name_list:
            _ = self.get_current_coordinate(name)
        self.robot_team = robot_name_list
        return "successful"

    def get_observation(self, robot_name):
        """
        Returns an observation message for a given robot in the team, detailing the objects it can see,
        their locations, and the relationships to those objects.

        Args:
            robot_name (str): The name of the robot requesting the observation.

        Returns:
            dict:
                - A dictionary containing details about the observed objects, including:
                    - "coordinate": [x, y, z], the object's location.
                    - "description": Relationship description of the object (e.g., on/between).
                    - "type": A list of types (e.g., "pick", "place", or "Unknown").
                - If the robot name is invalid, returns {"error": "Invalid robot name"}.
        """
        if robot_name in self.robot_team:
            # Step 1: Retrieve robot's observed objects, their locations, and neighboring objects
            seen_object_list, object_locations, object_neighbors = (
                single_robot_observation(robot_name)
            )

            if not seen_object_list:
                return {}

            # Step 2: Parse relationships between objects
            relations = parse_relations(object_neighbors)

            # Step 3: Retrieve object types
            object_type_meta = get_object_type({"object_list": seen_object_list}).get(
                "data", {}
            )

            # Step 4: Prepare the result dictionary
            res = {}
            # default_room = "Bedroom"  # Configurable default room

            for key in seen_object_list:
                if key not in {"error_info", "is_success", robot_name}:
                    placeable = object_type_meta.get(key + "Placeable", "False")
                    obj_type = [object_type_meta.get(key, "Unknown")]
                    if placeable == "True":
                        obj_type.append("Placeable")

                    res[key] = {
                        # "room": default_room,  # Replace with dynamic assignment if available
                        "coordinate": object_locations[key]["location"],
                        "description": relation_to_str([key], {key: relations[key]}),
                        "type": obj_type,
                    }

            return res
        else:
            return {"error": "Invalid robot name"}

    def get_reasonable_actions(self, robot_name, object_name_list):
        """
        Determines reasonable actions a robot can perform on a list of objects based on their types,
        locations, and the robot's arm length.

        Args:
            robot_name (str): The name of the robot performing the actions.
            object_name_list (list): A list of object names to evaluate actions for.

        Returns:
            dict: A dictionary where each key is an object name, and the value is a list of
                actions the robot can perform on that object. Possible actions include:
                - "pick": If the object is pick-up-able and within arm's reach.
                - "pull": If the object is movable and within arm's reach.
                - "place": If the object is placeable and within arm's reach.
        """
        arm_length = float(self.get_robot_arm_length(robot_name))
        robot_infos = get_object_info({"object_list": [robot_name]})
        objects_infos = get_object_info({"object_list": object_name_list})
        robot_location = robot_infos[robot_name].get("location")
        res = {}
        object_type_input = {"object_list": object_name_list}
        meta_type = get_object_type(object_type_input).get("data")
        for object_name in object_name_list:
            object_location = objects_infos[object_name].get("location")
            edge_points_list = parse_coordinates_from_string(
                meta_type[object_name + "EdgePoints"]
            )
            object_type = meta_type.get(object_name)
            object_placeable = meta_type[object_name + "Placeable"]
            res[object_name] = []
            # res[object_name]["type"] = object_type
            # res[object_name]["placeable"] = object_placeable
            if object_type == "PickUpableObjects":
                if get_2d_distance(object_location, robot_location) > arm_length:
                    pass
                else:
                    res[object_name].append("pick")
            if object_type == "MoveableObjects":
                target_location = next(
                    (
                        point
                        for point in edge_points_list
                        if get_2d_distance(point, robot_location) < float(arm_length)
                    ),
                    robot_location,
                )
                if target_location == robot_location:
                    pass
                else:
                    res[object_name].append("pull")
            if object_placeable == "True":
                target_location = next(
                    (
                        point
                        for point in edge_points_list
                        if get_2d_distance(point, robot_location) < float(arm_length)
                    ),
                    robot_location,
                )
                if target_location == robot_location:
                    pass
                else:
                    res[object_name].append("place")
        return res

    def get_robot_room(self, robot_name):
        """
        Determines the current room of a given robot based on its coordinates.

        Args:
            robot_name (str): The name of the robot whose room is being determined.

        Returns:
            str: The name of the room the robot is in. Possible values:
                - Room name (e.g., "Bedroom", "Kitchen") if the robot's coordinates match a defined quadrilateral.
                - "hallway" if the robot is not within any defined room quadrilateral.
            ROOMS =["Kitchen", "livingroom", "bedroom", "bathroom", "office", "Hallway", "DiningRoom"]
        """
        self.robot_map[robot_name]["robot_room"] = ""
        corridinate = self.get_current_coordinate(robot_name)
        for key in EDGES.get(self.scene_index):
            if is_point_in_quadrilateral(
                EDGES[self.scene_index].get(key), [corridinate[0], corridinate[2]]
            ):
                self.robot_map[robot_name]["robot_room"] = key
                return key
        self.robot_map[robot_name]["robot_room"] = "hallway"
        return "hallway"

    ## updated 12 20
    def get_object_room(self, object_name):
        """
        Determines the current room of a given object based on its coordinates.

        Args:
            object_name (str): The name of the object whose room is being determined.

        Returns:
            str: The name of the room the object is in. Possible values:
                - A defined room name (e.g., "Kitchen", "livingroom", "bedroom", "bathroom", "office", "Hallway", "DiningRoom")
                if the object's coordinates match a defined quadrilateral.
                - "hallway" if the object is not within any defined room quadrilateral.
                - "hallway" if the object is not found in the environment (e.g., being held by a robot).
        Notes:
            ROOMS = ["Kitchen", "livingroom", "bedroom", "bathroom", "office", "Hallway", "DiningRoom"]
        """
        if object_name is None:
            return "hallway"
        
        state_input = {"object_list": [object_name]}
        try:
            object_state = get_object_info(state_input)
            # Check if the object exists in the returned state
            if object_name not in object_state:
                print(f"Warning: Object {object_name} not found in environment state. It may be held by a robot or not visible.")
                return "hallway"
            
            coordinate = object_state[object_name]["location"]
        except (KeyError, TypeError) as e:
            print(f"Warning: Failed to get location for object {object_name}: {e}. It may be held by a robot or not visible.")
            return "hallway"

        # Check each defined room polygon to see if the object's position falls inside it.
        for room_name in EDGES.get(self.scene_index, {}):
            if is_point_in_quadrilateral(
                EDGES[self.scene_index].get(room_name), [coordinate[0], coordinate[2]]
            ):
                return room_name
        # If no matching room is found, return "hallway".
        return "hallway"

    def get_current_coordinate(self, robot_name):
        """
        Retrieves the current coordinates of the specified robot.

        Returns:
            list: A list of [x, y, z] coordinates representing the robot's current location.
        """
        state_input = {"object_list": [robot_name]}
        robot_state = get_object_info(state_input)
        self.robot_pool[robot_name]["init_location"] = robot_state[robot_name][
            "location"
        ]
        self.robot_pool[robot_name]["init_rotation"] = robot_state[robot_name][
            "rotation"
        ]
        return robot_state[robot_name]["location"]

    def get_robot_arm_length(self, robot_name):
        """
        Retrieves the length of the robot's arm.

        Returns:
            float: The length of the robot's arm. Returns 0 if the robot does not have a hand.
        """
        robot_status_input = {"robot_list": [robot_name]}
        robot_status = get_robot_status(robot_status_input)
        if robot_status[robot_name]["hand"] != "True":
            return 0
        else:
            return robot_status[robot_name]["armLength"]

    ## updated 12 20
    def go_pick_obj(self, robot_name, object_name):
        """
        Navigate the specified robot towards a given object and attempt to pick it up.

        Args:
            robot_name (str): The name of the robot that will move and attempt to pick the object.
            object_name (str): The name of the object the robot should retrieve.

        Returns:
            tuple:
                - is_success (bool): True if the robot successfully picked the object; otherwise, False.
                - reason (str): A message explaining the outcome (e.g., "picked successfully" or "on the way to object").
                - obs (dict): Observation details collected during the navigation (and potentially the pickup).

        Notes:
            This function first attempts to navigate the robot to the object. If navigation is successful,
            it then attempts to pick the object up. If the navigation is not yet successful, it provides
            an intermediate status message.
        """
        flag, obs = self.goto_object(robot_name, object_name)
        self.robot_map[robot_name]["robot_plan"] = "[gopick] <" + object_name + ">"
        if flag == True:
            is_success, reason = robot_pick_obj(robot_name, object_name)
            return is_success, reason, obs
        return flag, "on the way to object", obs

    ## updated 12 20
    def go_place_obj(self, robot_name, target_receiver):
        """
        Navigate the specified robot towards a target receiver object and attempt to place an item onto it.

        Args:
            robot_name (str): The name of the robot performing the placement action.
            target_receiver (str): The name of the object that will receive the placed item.

        Returns:
            tuple:
                - is_success (bool): True if the robot successfully placed the object onto the target_receiver; otherwise False.
                - reason (str): A message explaining the outcome (e.g., "placed successfully", "on the way to object").
                - obs (ObservationMessage): Observation details collected during the navigation and placement process.

        Notes:
            This function:
            1. Uses `goto_object` to navigate the robot to the target receiver's location.
            2. If navigation is successful, it calls `robot_place_obj` to attempt the placement.
            3. If navigation fails or is incomplete, it returns the current navigation status and observations.
        """
        flag, obs = self.goto_object(robot_name, target_receiver)
        self.robot_map[robot_name]["robot_plan"] = (
            "[goplaceto] <" + target_receiver + ">"
        )
        if flag == True:
            is_success, reason = robot_place_obj(robot_name, target_receiver)
            if is_success == True:
                print(f"Robot {robot_name} placed object {target_receiver} successfully at time step {self.total_time_step + self.this_actions_time_step}")
            return is_success, reason, obs
        return flag, "on the way to target_receiver", obs

    def goto_object(self, robot_name, object_name):
        """
        Navigate the robot to the specified object and return the result.

        Args:
            robot_name (str): The name of the robot performing the navigation.
            object_name (str): The name of the object to which the robot will navigate.

        Returns:
            tuple:
                - flag (bool): Indicates whether the robot successfully reached the target navigation point.
                - message (ObservationMessage): Details of observations during the navigation process.
        """
        self.robot_map[robot_name]["robot_plan"] = "[goto] <" + object_name + ">"
        # self.robot_map[robot_name]['robot_route'] = robot_go_to_obj_path(robot_name, object_name)
        InfoInput = {"object_list": [robot_name, object_name]}
        infos = get_object_info(InfoInput)
        robot_loc = infos[robot_name]["location"]

        # get robot team location list
        teammateInput = {"object_list": self.robot_team}
        teammateinfos = get_object_info(teammateInput)
        teammate_loc_list = []
        for robot_teammate in self.robot_team:
            if robot_teammate != robot_name:
                # teammate_loc_list.append(teammateinfos[robot_teammate]["location"])
                # Add target point
                if len(self.robot_map[robot_teammate]["robot_route"]) >= 1:
                    teammate_loc_list.append(
                        self.robot_map[robot_teammate]["robot_route"][-1]
                    )
        target_loc = obs_get_nearest_edge_point_list(
            robot_loc, object_name, teammate_loc_list
        )
        flag, accumulated_message = self.goto_point(robot_name, target_loc)
        # turn to obj
        object_position = infos[object_name]["location"]
        # object_position = get_nearest_edge_point(infos[robot_name]['location'], object_name)
        robot_teleport(
            turn_to_target(
                robot_name,
                self.robot_pool[robot_name]["init_location"],
                self.robot_pool[robot_name]["init_rotation"],
                object_position,
            )
        )
        return flag, accumulated_message

    ## updated 12 20
    def joint_goto_object(self, robot_list, object_name):
        robots_infos_input = {"object_list": robot_list}
        robots_infos = get_object_info(robots_infos_input)

        object_loc_input = {"object_list": [object_name]}
        object_infos = get_object_info(object_loc_input)
        object_loc = object_infos[object_name]["location"]

        avoiding_point_list = []
        target_locs = {}
        for robot_name in robot_list:
            robot_loc = robots_infos[robot_name]["location"]
            target_loc = obs_get_nearest_edge_point_list(
                robot_loc, object_name, avoiding_point_list
            )
            avoiding_point_list.append(target_loc.copy())
            target_locs[robot_name] = target_loc

        ret = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_robot = {
                executor.submit(
                    self.goto_point, robot_name, target_locs[robot_name]
                ): robot_name
                for robot_name in robot_list
            }

            for future in concurrent.futures.as_completed(future_to_robot):
                robot_name = future_to_robot[future]
                flag, accumulated_message = future.result()

                ret[robot_name] = {
                    "goto_flag": flag,
                    "obs": copy.deepcopy(accumulated_message),
                }

                # After successful navigation, make the robot face the target object
                if flag:
                    robot_teleport(
                        turn_to_target(
                            robot_name,
                            self.robot_pool[robot_name]["init_location"],
                            self.robot_pool[robot_name]["init_rotation"],
                            object_loc,
                        )
                    )

        return ret

    def goto_point(self, robot_name, target_loc):
        """
        Navigate the robot to a specific target location, step by step, and gather observation messages.

        Args:
            robot_name (str): The name of the robot performing the navigation.
            target_loc (list): The target location [x, y, z] to which the robot navigates.

        Returns:
            tuple:
                - flag (bool): Indicates whether the robot has reached the target location.
                - accumulated_message (dict): A dictionary containing observation messages during the navigation.
        """
        step = 0
        flag = False
        accumulated_message = {}
        # self.refresh_robot(robot_name)
        self.robot_map[robot_name]["robot_route"] = robot_go_to_point_path(
            robot_name, target_loc
        )
        self.robot_map[robot_name]["robot_route"].pop(0)
        for _ in range(self.robot_map[robot_name]["robot_speed"]):
            step += 1
            if len(self.robot_map[robot_name]["robot_route"]) <= 1:
                # accumulated_obs
                currentObs = self.get_observation(robot_name)
                for key in currentObs:
                    accumulated_message[key] = currentObs[key]
                flag = True
                break
                # return True, accumulated_message
            else:
                target_position = self.robot_map[robot_name]["robot_route"].pop(0)
                next_position, next_rotation = robot_go_to_point(
                    robot_name,
                    self.robot_pool[robot_name]["init_location"],
                    self.robot_pool[robot_name]["init_rotation"],
                    target_position,
                )
                self.robot_pool[robot_name]["init_location"] = next_position
                self.robot_pool[robot_name]["init_rotation"] = next_rotation
                currentObs = self.get_observation(robot_name)
                for key in currentObs:
                    accumulated_message[key] = currentObs[key]
        
        # update step counts
        if step > self.this_actions_time_step:
            self.this_actions_time_step = step
        self.total_route_step += step

        return flag, accumulated_message

    def goto_room(self, robot_name, room_name):
        """
        Navigate the robot to a specific room by determining the target location based on the room name.

        Args:
            robot_name (str): The name of the robot performing the navigation.
            room_name (str): The name of the room to which the robot navigates.

        Returns:
            tuple:
                - flag (bool): Indicates whether the robot has reached the target location.
                - accumulated_message (dict): A dictionary containing observation messages during the navigation.
        """
        target_loc = EXPLOREPOINTS.get(self.scene_index)[room_name][0]
        return self.goto_point(robot_name, target_loc)

    def pick(self, robot_name, object_name):
        """Pick object_name and return flag and message
        Args:
            robot_name (str): name of the robot
            object_name (str): name of the object to pick
        Returns:
            flag (bool): flag to indicate if the robot has finished the target navigation point
            message (str): message to be sent
        """
        self.robot_map[robot_name]["robot_plan"] = "[pick] <" + object_name + ">"
        return robot_pick_obj(robot_name, object_name)

    def place(self, robot_name, target_receiver):
        """Place object_name and return flag and message
        Args:
            robot_name (str): name of the robot
            object_name (str): name of the object to place
        Returns:
            flag (bool): flag to indicate if the robot has finished the target navigation point
            message (str): message to be sent
        """
        self.robot_map[robot_name]["robot_plan"] = "[place] <" + target_receiver + ">"
        return robot_place_obj(robot_name, target_receiver)

    ## updated 12 20
    def joint_go_pull(
        self, robot_list: list, object_name: str, direction: list = [1, 0, 0]
    ):
        """
        Coordinate a group of robots to navigate to a target object and jointly pull it in the specified direction.

        Args:
            robot_list (list of str): A list of robot names that will participate in the operation.
            object_name (str): The name of the target object that the robots will jointly pull.
            direction (list of float): A 3D vector specifying the pulling direction, e.g., [1, 0, 0] for pulling along the x-axis.

        Returns:
            dict: A dictionary containing the status and messages for each robot involved in the operation.
                Example structure:
                {
                    "robot1": { "flag": True, "message": "Pull completed successfully"},
                    "robot2": { 'flag': False,
                                'goto_flag': True,
                                'message': 'Partner(s) on the way',
                                'obs': {'ArmChair_01': {}}
                }

        Notes:
            - Each robot will first navigate to the target object in parallel using `joint_goto_object`.
            - If all robots successfully reach the target, they will jointly pull the object in the specified direction.
            - If some robots fail to navigate to the target, the function will return their statuses and messages accordingly.
        """
        # Mark each robot's plan for pulling
        for robot_name in robot_list:
            self.robot_map[robot_name]["robot_plan"] = "[gopull] <" + object_name + ">"

        # Step 1: Parallel navigation to the target object
        go_result = self.joint_goto_object(robot_list, object_name)
        ret = copy.deepcopy(go_result)
        is_go_success = True

        # Step 2: Check if all robots have successfully navigated to the target
        for robot_name in go_result:
            if not go_result[robot_name]["goto_flag"]:
                is_go_success = False
                break

        if not is_go_success:
            # If any robot fails to navigate, update the return messages
            for robot_name in ret:
                ret[robot_name]["flag"] = False
                if ret[robot_name]["goto_flag"]:
                    ret[robot_name]["message"] = "Partner(s) on the way"
                else:
                    ret[robot_name]["message"] = "On the way to object"
        else:
            # Step 3: If all robots successfully reached the target, jointly pull the object
            flag, message = self.joint_pull(robot_list, object_name, direction)
            for robot_name in ret:
                ret[robot_name]["flag"] = flag
                ret[robot_name]["message"] = message

        return ret

    def pull(self, robot_name, object_name, direction):
        """Pull object_name in direction and return flag and message
        Args:
            object_name (str): name of the object to pull
            direction (list): direction to pull
        Returns:
            flag (bool): flag to indicate if the robot has finished the target navigation point
            message (str): message to be sent
        """
        self.robot_map[robot_name]["robot_plan"] = "[pull] <" + object_name + ">"
        robot_name_list = [robot_name]
        flag, message = self.joint_pull(robot_name_list, object_name, direction)
        return flag, message

    def joint_pull(self, robot_list: list, object_name, direction: list = [1, 0, 0]):
        """Pull object_name in direction and return flag and message
        Args:
            object_name (str): name of the object to pull
            direction (list): direction to pull
        Returns:
            flag (bool): flag to indicate if the robot has finished the target navigation point
            message (str): message to be sent
        """
        needed_force = 120
        for robot_name in robot_list:
            self.robot_map[robot_name]["robot_plan"] = "[pull] <" + object_name + ">"
        direction_string = f"({direction[0]},{direction[1]},{direction[2]})"
        flag, message, details = robot_pull_obj(
            robot_list, object_name, needed_force, direction_string
        )
        message += ";"
        for robot_name in robot_list:
            if details.get(robot_name) is not None:
                message += details.get(robot_name)
        return flag, message

    def explore(self, robot_name, room_name):
        """
        Directs the robot to explore a specified room by visiting exploration points within it.

        Returns:
            tuple:
                - flag (bool): Indicates whether the robot has finished exploring all points in the room.
                - message (dict): A dictionary containing messages or observations gathered during exploration.
        """
        self.robot_map[robot_name]["robot_plan"] = "[explore] <" + room_name + ">"
        flag = False
        accumulated_message = {}
        if len(self.robot_map[robot_name]["robot_explore_map"][room_name]) <= 0:
            return True, accumulated_message
        else:
            robot_loc = self.get_current_coordinate(robot_name)
            candidate_explor_points = self.robot_map[robot_name]["robot_explore_map"][
                room_name
            ]
            mindistance = 100000
            # target_loc = candidate_explor_points[0]
            for point in candidate_explor_points:
                dis = get_2d_distance(point, robot_loc)
                if dis < mindistance:
                    target_loc = point.copy()
                    mindistance = dis
            flag, accumulated_message = self.goto_point(robot_name, target_loc)
            if flag:
                # safe remive item
                self.robot_map[robot_name]["robot_explore_map"][room_name] = [loc for loc in self.robot_map[robot_name]["robot_explore_map"][room_name] if loc != target_loc]
                if len(self.robot_map[robot_name]["robot_explore_map"][room_name]) >= 1:
                    flag = False
                accumulated_message = self.check_arround(robot_name, accumulated_message)
        return flag, accumulated_message

    def check_arround(self, robot_name, up_to_now_messages):
        """
        Checks the surroundings of the robot by rotating its view in multiple directions and updating observed messages.

        Args:
            robot_name (str): The name of the robot performing the check.
            up_to_now_messages (dict): The dictionary containing messages or observations gathered so far.

        Returns:
            dict: Updated dictionary with additional observations from checking the surroundings.
        """
        state_input = {"object_list": [robot_name]}
        robot_state = get_object_info(state_input)
        location = robot_state[robot_name]["location"]
        rotation = robot_state[robot_name]["rotation"]
        for degree in [0, 45, 90, 135, 180, -45, -90, -135]:
            teleport_action = {
                robot_name: {
                    "location": location,
                    "rotation": [rotation[0], degree, rotation[2]],
                }
            }
            robot_teleport(teleport_action)
            currentObs = self.get_observation(robot_name)
            for key in currentObs:
                up_to_now_messages[key] = currentObs[key]
        return up_to_now_messages

    def check_result(self, object_list):
        state_input = {"object_list": object_list}
        object_neighbors = get_object_neighbors(state_input)
        relations = parse_relations(object_neighbors)
        return object_neighbors, relations


if __name__ == "__main__":
    pass
    # def check_explore(room_name):
    #     select_scene("0")
    #     time.sleep(3)
    #     robot_pool = {
    #         "Robot_1": {
    #             "type": "ManipulaThor",
    #             "name": "Robot_1",
    #             "init_location": [-3.216, 0.90, -3.064],
    #             "init_rotation": [0, -90, 0],
    #             "arm_length": 1,
    #             "robot_high": 0.5,
    #             "robot_low": 0.2,
    #             "strength": 80,
    #         },
    #         "Robot_2": {
    #             "type": "StretchRE",
    #             "name": "Robot_2",
    #             "init_location": [-3.216, 0.90, -1.609],
    #             "init_rotation": [0, -90, 0],
    #             "arm_length": 1,
    #             "robot_high": 0.5,
    #             "robot_low": 0.2,
    #             "strength": 80,
    #         },
    #         "Robot_0": {
    #             "type": "LoCoBot",
    #             "name": "Robot_0",
    #             "init_location": [-5.9592, 0.90, -0.201],
    #             "init_rotation": [0, 180, 0],
    #             "arm_length": 1,
    #             "robot_high": 0.5,
    #             "robot_low": 0.2,
    #             "strength": 80,
    #         },
    #     }
    #     robot_team = ["Robot_0", "Robot_1"]
    #     check_env = Env(robot_pool, robot_team)
    #     with open("config.json", "r") as f:
    #         config = json.load(f)[2]
    #         env_robot_pool = config["robot_pool"]  # dict
    #         env_robot_team = config["robot_team"]  # dict
    #         env_scene_index = config["scene_index"]  # string
    #         env_object_list = config["misplaced_objects"]
    #         object_locations = config["object_locations"]
    #     check_env.set_robot(robot_team)
    #     check_env.init_misplaced_objects(env_object_list, object_locations)
    #     pprint.pprint(check_env.get_observation("Robot_0"))
    #     pprint.pprint(check_env.get_current_coordinate("Robot_0"))
    #     Index = True
    #     time.sleep(1)
    #     # while(Index):
    #     #     still_going, message = check_env.goto_object("Robot_0","Painting_01")
    #     #     pprint.pprint(message)
    #     #     pprint.pprint(check_env.robot_plans["Robot_0"])
    #     #     pprint.pprint(check_env.robot_routes["Robot_0"])
    #     #     time.sleep(0.5)
    #     #     Index = not still_going
    #     # time.sleep(10)
    #     Index = True
    #     while Index:
    #         still_going, message = check_env.explore("Robot_0", room_name)
    #         print(still_going)
    #         pprint.pprint(message)
    #         # pprint.pprint(check_env.robot_plans["Robot_0"])
    #         # pprint.pprint(check_env.robot_explore_plans["Robot_0"])
    #         time.sleep(0.5)
    #         Index = not still_going
    #     pprint.pprint(check_env.goto_room("Robot_0", room_name))

    # def check_object_room(obj_name):
    #     select_scene("0")
    #     time.sleep(3)
    #     robot_pool = {
    #         "Robot_1": {
    #             "type": "ManipulaThor",
    #             "name": "Robot_1",
    #             "init_location": [-3.216, 0.90, -3.064],
    #             "init_rotation": [0, -90, 0],
    #             "arm_length": 1,
    #             "robot_high": 0.5,
    #             "robot_low": 0.2,
    #             "strength": 80,
    #         },
    #         "Robot_2": {
    #             "type": "StretchRE",
    #             "name": "Robot_2",
    #             "init_location": [-3.216, 0.90, -1.609],
    #             "init_rotation": [0, -90, 0],
    #             "arm_length": 1,
    #             "robot_high": 0.5,
    #             "robot_low": 0.2,
    #             "strength": 80,
    #         },
    #         "Robot_0": {
    #             "type": "LoCoBot",
    #             "name": "Robot_0",
    #             "init_location": [-5.9592, 0.90, -0.201],
    #             "init_rotation": [0, 180, 0],
    #             "arm_length": 1,
    #             "robot_high": 0.5,
    #             "robot_low": 0.2,
    #             "strength": 80,
    #         },
    #     }
    #     robot_team = ["Robot_0", "Robot_1"]
    #     check_env = Env(robot_pool, robot_team)
    #     print(check_env.get_object_room(obj_name))

    # def check_joint_goto_obj(obj_name):
    #     select_scene("0")
    #     time.sleep(3)
    #     robot_pool = {
    #         "Robot_1": {
    #             "type": "ManipulaThor",
    #             "name": "Robot_1",
    #             "init_location": [-3.216, 0.90, -3.064],
    #             "init_rotation": [0, -90, 0],
    #             "arm_length": 1,
    #             "robot_high": 0.5,
    #             "robot_low": 0.2,
    #             "strength": 80,
    #         },
    #         "Robot_2": {
    #             "type": "StretchRE",
    #             "name": "Robot_2",
    #             "init_location": [-3.216, 0.90, -1.609],
    #             "init_rotation": [0, -90, 0],
    #             "arm_length": 1,
    #             "robot_high": 0.5,
    #             "robot_low": 0.2,
    #             "strength": 80,
    #         },
    #         "Robot_0": {
    #             "type": "LoCoBot",
    #             "name": "Robot_0",
    #             "init_location": [-5.9592, 0.90, -0.201],
    #             "init_rotation": [0, 180, 0],
    #             "arm_length": 1,
    #             "robot_high": 0.5,
    #             "robot_low": 0.2,
    #             "strength": 80,
    #         },
    #     }
    #     robot_team = ["Robot_0", "Robot_1"]
    #     check_env = Env(robot_pool, robot_team)  # check_explore('livingroom')
    #     check_env.set_robot(robot_team)
    #     pprint.pprint(check_env.joint_goto_object(robot_team, obj_name))

    # def check_joint_go_pull(obj_name, direction):
    #     select_scene("0")
    #     time.sleep(3)
    #     robot_pool = {
    #         "Robot_1": {
    #             "type": "ManipulaThor",
    #             "name": "Robot_1",
    #             "init_location": [-3.216, 0.90, -3.064],
    #             "init_rotation": [0, -90, 0],
    #             "arm_length": 1,
    #             "robot_high": 0.5,
    #             "robot_low": 0.2,
    #             "strength": 30,
    #             "speed": 100,
    #         },
    #         "Robot_2": {
    #             "type": "StretchRE",
    #             "name": "Robot_2",
    #             "init_location": [-3.216, 0.90, -1.609],
    #             "init_rotation": [0, -90, 0],
    #             "arm_length": 1,
    #             "robot_high": 0.5,
    #             "robot_low": 0.2,
    #             "strength": 80,
    #             "speed": 40,
    #         },
    #         "Robot_0": {
    #             "type": "LoCoBot",
    #             "name": "Robot_0",
    #             "init_location": [-5.9592, 0.90, -0.201],
    #             "init_rotation": [0, 180, 0],
    #             "arm_length": 1,
    #             "robot_high": 0.5,
    #             "robot_low": 0.2,
    #             "strength": 80,
    #             "speed": 100,
    #         },
    #     }
    #     robot_team = ["Robot_0", "Robot_1"]
    #     check_env = Env(robot_pool, robot_team)  # check_explore('livingroom')
    #     check_env.set_robot(robot_team)
    #     pprint.pprint(check_env.joint_go_pull(robot_team, obj_name, direction))


    # def check_co_act():
    #     select_scene("0")
    #     time.sleep(3)
    #     robot_pool = {
    #         "Robot_1": {
    #             "type": "ManipulaThor",
    #             "name": "Robot_1",
    #             "init_location": [-3.216, 0.90, -3.064],
    #             "init_rotation": [0, -90, 0],
    #             "arm_length": 1,
    #             "robot_high": 2,
    #             "robot_low": 0.2,
    #             "strength": 30,
    #             "speed": 100,
    #         },
    #         "Robot_2": {
    #             "type": "StretchRE",
    #             "name": "Robot_2",
    #             "init_location": [-3.216, 0.90, -1.609],
    #             "init_rotation": [0, -90, 0],
    #             "arm_length": 1,
    #             "robot_high": 2,
    #             "robot_low": 0.2,
    #             "strength": 80,
    #             "speed": 40,
    #         },
    #         "Robot_0": {
    #             "type": "LoCoBot",
    #             "name": "Robot_0",
    #             "init_location": [-5.9592, 0.90, -0.201],
    #             "init_rotation": [0, 180, 0],
    #             "arm_length": 1,
    #             "robot_high": 2,
    #             "robot_low": 0.2,
    #             "strength": 80,
    #             "speed": 100,
    #         },
    #     }
    #     robot_team = ["Robot_0", "Robot_1", "Robot_2"]
    #     check_env = Env(robot_pool, robot_team)  # check_explore('livingroom')
    #     check_env.set_robot(robot_team)
    #     act_input = {
    #         "Robot_0": "[gopick] <RemoteControl_01>",
    #         "Robot_1": "[gopull] <Sofa_01>",
    #         "Robot_2": "[gopull] <Bed_01>",
    #     }
    #     pprint.pprint(check_env.co_act(act_input))
    # check_co_act()
    # # select_scene("0")
    # # time.sleep(3)
    # # robot_pool = {
    # #     "Robot_1": {
    # #         "type": "ManipulaThor",
    # #         "name": "Robot_1",
    # #         "init_location": [-3.216, 0.90, -3.064],
    # #         "init_rotation": [0, -90, 0],
    # #         "arm_length": 1,
    # #         "robot_high": 0.5,
    # #         "robot_low": 0.2,
    # #         "strength": 800,
    # #     },
    # #     "Robot_2": {
    # #         "type": "StretchRE",
    # #         "name": "Robot_2",
    # #         "init_location": [-3.216, 0.90, -1.609],
    # #         "init_rotation": [0, -90, 0],
    # #         "arm_length": 1,
    # #         "robot_high": 0.5,
    # #         "robot_low": 0.2,
    # #         "strength": 800,
    # #     },
    # #     "Robot_0": {
    # #         "type": "LoCoBot",
    # #         "name": "Robot_0",
    # #         "init_location": [-5.9592, 0.90, -0.201],
    # #         "init_rotation": [0, 180, 0],
    # #         "arm_length": 1,
    # #         "robot_high": 0.5,
    # #         "robot_low": 0.2,
    # #         "strength": 80,
    # #     },
    # # }
    # # robot_team = ["Robot_0", "Robot_1", "Robot_2"]
    # # check_env = Env(robot_pool, robot_team)
    # # check_env.set_robot(robot_team)
    # # robot_actions = {
    # #     "Robot_0": "[goto] <Pillow_11>",
    # #     "Robot_2": "[goto] <Bed_01>",
    # #     "Robot_1": "[goto] <Bed_01>",
    # # }
    # # # Run the act function with the robot actions
    # # result = check_env.act(robot_actions)

    # # print()

    # # # Print the result of each robot's action
    # # for robot, action_result in result.items():
    # #     pprint.pprint(action_result)
    # #     print()
    # # robot_actions = {
    # #     "Robot_0": "[goto] <Pillow_11>",
    # #     "Robot_2": "[pull] <Bed_01>",
    # #     "Robot_1": "[pull] <Bed_01>",
    # # }
    # # result = check_env.act(robot_actions)
    # # # result["Robot_0"]['flag']== False
    # # for i in range(7):
    # #     robot_actions = {
    # #         "Robot_0": "[goto] <Pillow_11>",
    # #         "Robot_2": "[pull] <Bed_01>",
    # #         "Robot_1": "[pull] <Bed_01>",
    # #     }
    # #     result = check_env.act(robot_actions)

    # #     print()

    # #     # Print the result of each robot's action
    # #     for robot, action_result in result.items():
    # #         pprint.pprint(action_result)
    # #         print()

    # # robot_actions = {
    # #     "Robot_0": "[pick] <Pillow_11>",
    # #     "Robot_2": "[pull] <Bed_01>",
    # #     "Robot_1": "[pull] <Bed_01>",
    # # }
    # # result = check_env.act(robot_actions)

    # # print()

    # # # Print the result of each robot's action
    # # for robot, action_result in result.items():
    # #     pprint.pprint(action_result)
    # #     print()

    # # robot_actions = {
    # #     "Robot_0": "[goto] <Bed_01>",
    # #     "Robot_2": "[pull] <Bed_01>",
    # #     "Robot_1": "[pull] <Bed_01>",
    # # }
    # # result = check_env.act(robot_actions)

    # # print()

    # # # Print the result of each robot's action
    # # for robot, action_result in result.items():
    # #     pprint.pprint(action_result)
    # #     print()

    # # robot_actions = {
    # #     "Robot_0": "[place] <Bed_01>",
    # #     "Robot_2": "[pull] <Bed_01>",
    # #     "Robot_1": "[pull] <Bed_01>",
    # # }
    # # result = check_env.act(robot_actions)

    # # print()

    # # # Print the result of each robot's action
    # # for robot, action_result in result.items():
    # #     pprint.pprint(action_result)
    # #     print()

    # # #pprint.pprint(check_env.joint_pull(["Robot_1", "Robot_2"], "Bed_01", [1, 0, 0]))
    # # pprint.pprint(check_env.get_reasonable_actions("Robot_0", ["Bed_01", "Pillow_11","CD_01"]))
    # # robot_team = ["Robot_0", "Robot_2"]
    # # check_env.set_robot(robot_team)
