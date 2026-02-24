#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/9/11 21:04
# @Author  : dby
# @File    : oracle.py
# @Software: PyCharm
import math
import pprint
from collections import deque

import numpy as np
from unity.ue_api import (
    get_object_info,
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


class Oracle:
    def __init__(self, reachable_points, grid_size=0.1, step_size=0.2):
        self.raw_reachable_points = reachable_points
        self.grid_size = grid_size
        self.step_size = step_size
        assert self.step_size > self.grid_size, "step_size should be larger than grid_size"
        self.reachable_points = self.parse_reachable_points()
        self.path_record = []

    def parse_reachable_points(self):
        reachable_points = set()
        for point in self.raw_reachable_points:
            point = eval(point) # (x, y, z)
            x, y, z = point
            reachable_points.add((x, z))
            # reachable_points.add(point)
        return reachable_points

    def shortest_path(self, start, end):
        start = tuple(start)
        # grid = self.reachable_points
        # Define four directions of movement
        dx = [self.grid_size, -self.grid_size, 0, 0]
        dy = [0, 0, self.grid_size, -self.grid_size]

        def is_valid(x, y):
            # Check if (x, y) is a valid point in the grid and is reachable
            return (np.round(x, 3), np.round(y, 3)) in self.reachable_points
            # return 0 <= x < len(grid) and 0 <= y < len(grid[0]) and grid[x][y] == 0

        queue = deque([(start[0], start[1], 0)])  # (x, y, distance)
        # Create a dictionary to track the parent of each node
        parent = {}
        # Create a set to track visited nodes
        visited = set()
        visited.add((start[0], start[1]))
        while queue:
            x, y, distance = queue.popleft()
            if (x, y) == end:
                # Found the end point, backtrack the path and record
                path = [(x, y)]
                while (x, y) != start:
                    x, y = parent[(x, y)]
                    path.append((x, y))
                path.reverse()
                return path  # Return the distance and path of the shortest path
            for i in range(4):
                new_x, new_y = x + dx[i], y + dy[i]
                new_x, new_y = np.round(new_x, 3), np.round(new_y, 3)
                if is_valid(new_x, new_y) and (new_x, new_y) not in visited:
                    queue.append((new_x, new_y, distance + 1))
                    visited.add((new_x, new_y))
                    parent[(new_x, new_y)] = (x, y)
        return []  # If path not found, return empty path

    def get_regularized_pos(self, position):
        r_pos = [np.round(np.round(a / self.grid_size) * self.grid_size, 3) for a in position]
        return r_pos

    def get_nearest_reachable_point(self, position):
        approx_target = None
        least_dist = 1e10
        for p in self.reachable_points:
            dist = np.linalg.norm(np.array(p) - np.array(position))
            if dist < least_dist:
                least_dist = dist
                approx_target = p
        return approx_target
    
    def get_nearest_connected_reachable_point(self, position, start):
        start = self.get_nearest_reachable_point(start)
        approx_target = None
        least_dist = 1e10
        for p in self.reachable_points:
            dist = np.linalg.norm(np.array(p) - np.array(position))
            if dist < least_dist and self.shortest_path(start, p) != [] :
                least_dist = dist
                approx_target = p
        return approx_target

    def get_key_points(self, path, start_point, end_point):
        key_points = []
        curr_point = start_point
        for i in range(len(path) - 1):
            next_point = path[i + 1]
            this_point = path[i]
            if np.linalg.norm(np.array(next_point) - np.array(curr_point)) > self.step_size:
                key_points.append(this_point)
                curr_point = this_point
            else:
                continue
        key_points.append(list(end_point))
        return key_points

    def get_path(self, position, target_loc):
        reg_agent_position = self.get_regularized_pos(position[:3])
        reg_target_loc = self.get_regularized_pos(target_loc[:3])

        agent_x, agent_y, agent_z = reg_agent_position
        target_x, target_y, target_z = reg_target_loc

        target_x, target_z = self.get_nearest_connected_reachable_point((target_x, target_z),(agent_x, agent_z))

        path = self.shortest_path((agent_x, agent_z), (target_x, target_z))
        # print("#### path ####")
        # print(path)
        path = [[point[0], agent_y, point[1]] for point in path]
        if len(path)!= 0 and path[0] == reg_agent_position:
            path = path[1:]  # remove the start point

        self.path_record = path
        # key_points = self.get_key_points(path, (agent_x, agent_z), (target_x, target_z))
        key_points = self.get_key_points(path, reg_agent_position, (target_x, agent_y, target_z))
        # because the path must have the same y as the agent

        return key_points

    def get_whole_path(self, start, route):
        key_points = self.get_path(start, route[0])
        # pprint.pprint(key_points)
        for i in range(len(route)):
            if i != 0:
                new_points = self.get_path(key_points[len(key_points)-1],route[i])
                for points in new_points:
                    key_points.append(points)
        return key_points
            

if __name__ == '__main__':
    # rechable_json = get_reachable_points(stepsize)
    # reachable_points = rechable_json["reachable_point"]
    # target_loc = [5 ,1.2,-4.3]
    # agent = Oracle(reachable_points, 0.1, 0.2)
    # position = [2.94,1.25,0.82]
    # track = [[-5.5,0.1,3.0],
    #     [-4.0,0.1,3.0],
    #     [-3.0,0.1,-3.5],
    #     [-2.0,0.1,-5.5],
    #     [-1.0,0.1,-1.5],
    #     [0.0,0.1,-2.0],
    #     [1.0,0.1,-5.0],
    #     [2.0,0.1,-5.0],
    #     [3.0,0.1,-5.5],
    #     [4.0,0.1,-6.0],
    #     [5.0,0.1,-5.5],
    #     [6.0,0.1,-5.5],
    #     [5 ,1.2,-4.3]
    #     ]
    # # path = agent.get_path( position, target_loc)
    # # pprint.pprint(path)
    # path = agent.get_whole_path(position, track)
    # pprint.pprint(path)

    rechable_json = get_reachable_points(stepsize)
    reachable_points = rechable_json["reachable_point"]
    agent = Oracle(reachable_points, 0.1, 0.2)
    position = get_object_info({"object_list":["Robot_0"]})["Robot_0"]['location']
    target_loc = get_object_info({"object_list":["Pillow_11"]})["Pillow_11"]['location']
    print(position, target_loc)
    track = [
        [-5.95,0.9,0.18],
        [-5.95,0.9,-0.38],
        [-3.3,0.9,-0.08],
        [-3.349,0.9,-2.265],
        [-2.81,0.9,-2.265],
        [-0.9,0.9,-3]
        ]
    # path = agent.get_path( position, target_loc)
    # pprint.pprint(path)
    path = agent.get_whole_path(position, track)
    pprint.pprint(path)

    # pprint.pprint(agent.reachable_points)