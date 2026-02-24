from llm import completion
from prompts import dispatch_robot_prompt
from tools import parse_json_from_response
from termcolor import colored

class DispatchRobot():
    def get_dispatched_list(self, robot_name, message, robot_pool):
        robot_list = None
        robot_pool_info = ""
        for robot in robot_pool:
            robot_pool_info += f"name: {robot.name}, {robot.capacity}\n"
        prompt = dispatch_robot_prompt.format(request_message=message, robot_pool=robot_pool_info)
        response = completion(prompt)["response"]  
        robot_list = parse_json_from_response(response, "robot_list")
        if isinstance(robot_list, str):
            robot_list = [robot_list]
            
        if len(robot_list) == 0:
            print(colored(f"{robot_name} Failed in request new member: {robot_list};\nmessage:{message}", "yellow"))
            return None
        elif "none" in robot_list[0].lower():
            print(colored(f"{robot_name} Failed in request new member: {robot_list};\nmessage:{message}", "yellow"))
            return None
        else:
            print(colored(f"{robot_name} request to dispatch robots: {robot_list};\nmessage:{message}", "yellow"))
            return robot_list
    
    def get_robot_by_name(self, robot_name, all_robots):
        for robot in all_robots:
            if robot.name == robot_name:
                return robot
        return None

    def dispatch_robot(self, request_name, message, robot_list, env, robot_pool, robot_team):
        for robot_name in robot_list:
            dispatched_robot = self.get_robot_by_name(robot_name, all_robots=robot_pool)
            if dispatched_robot is None:
                print(f"Robot {robot_name} not found in the robot_pool.")
                continue
            # set env
            env.robot_team.append(dispatched_robot.name)
            env.robot_team = list(set(env.robot_team))
            env.set_robot(env.robot_team)
            # set robot info
            dispatched_robot.communication_agent.memory.append(
                f"receive_from_{request_name}: {message}"
            )
            dispatched_robot.scene_graph = robot_team[0].scene_graph
            dispatched_robot.pickable_objects = robot_team[0].pickable_objects
            dispatched_robot.placeable_objects = robot_team[0].placeable_objects
            dispatched_robot.moveable_objects = robot_team[0].moveable_objects
            dispatched_robot.misplaced_obj_and_container = robot_team[0].misplaced_obj_and_container
            dispatched_robot.last_subtask = f"Help {request_name} with his ask for help."
            # update teammates
            dispatched_robot.teammates = robot_team[0].teammates

            # comm purpose
            dispatched_robot.communication_agent.purpose = f"1. Broadcast the coming of i join the team. 2. offer help to the {request_name}"
            # update robot_team and robot_pool
            robot_team.append(dispatched_robot)
            robot_team = list(set(robot_team))
            robot_pool = [r for r in robot_pool if r not in robot_team]
            print(f"Team: {len(robot_team)}, Pool: {len(robot_pool)}")
        return robot_pool, robot_team

    def update_teammates_info(self, robot_pool, robot_team):
        pool_teammates = []
        for robot in robot_pool:
            pool_teammates.append(f"name:{robot.name}, {robot.capacity}")
        
        for robot in robot_team:
            teammates = []
            for r in robot_team:
                if r.name != robot.name:
                    teammates.append(f"name: {r.name}, {r.capacity}")
            robot.teammates = teammates
            robot.pool_teammates = "; ".join(pool_teammates)
       

            
