import math
import pprint
import time
from collections import deque

from oracle import Oracle
from ultilities import (
    get_2d_distance,
    get_nearest_edge_point,
    parse_coordinates_from_string,
    turn_to_target,
)
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


def robot_go_to_obj_path(robotName, objectName):
    rechable_json = get_reachable_points({"step_size": 0.1})
    reachable_points = rechable_json["reachable_point"]
    agent = Oracle(reachable_points, 0.1, 0.2)
    InfoInput = {
    "object_list":[robotName, objectName]
    }
    infos = get_object_info(InfoInput)
    robot_loc = infos[robotName]['location']
    # target_loc = infos[objectName]['location']
    # nearest for big objs
    target_loc = get_nearest_edge_point(robot_loc, objectName)
    track = [
        robot_loc,
        target_loc
        ]
    # path = agent.get_path( position, target_loc)
    # pprint.pprint(path)
    path = agent.get_whole_path(robot_loc, track)
    # pprint.pprint(path)
    return path

def robot_go_to_point_path(robotName, point_loc):
    rechable_json = get_reachable_points({"step_size": 0.1})
    reachable_points = rechable_json["reachable_point"]
    agent = Oracle(reachable_points, 0.1, 0.2)
    InfoInput = {
    "object_list":[robotName]
    }
    infos = get_object_info(InfoInput)
    robot_loc = infos[robotName]['location']
    # target_loc = infos[objectName]['location']
    # nearest for big objs
    target_loc = point_loc
    track = [
        robot_loc,
        target_loc
        ]
    # path = agent.get_path( position, target_loc)
    # pprint.pprint(path)
    path = agent.get_whole_path(robot_loc, track)
    # pprint.pprint(path)
    return path

# def robot_go_to_room(robotName, roomName)

def explore_room(robotName, key_points, roomName = "Bedroom"):
    rechable_json = get_reachable_points(0.1)
    reachable_points = rechable_json["reachable_point"]
    agent = Oracle(reachable_points, 0.1, 0.2)
    InfoInput = {
    "object_list":[robotName]
    }
    infos = get_object_info(InfoInput)
    robot_loc = infos[robotName]
    track = key_points
    path = agent.get_whole_path(robot_loc, track)
    pprint.pprint(path)
    return path, key_points

if __name__ == '__main__':
    getObjectType = {
    "object_list":["Toilet_01","Bed_01"]
}
    pprint.pprint(get_object_type(getObjectType)['data']["Toilet_01" + "EdgePoints"])