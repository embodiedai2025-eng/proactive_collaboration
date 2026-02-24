import math

from agent import (
    ActionAgent,
    CommunicationAgent,
    ObservationAgent,
    ProgressAgent,
    RelfectionAgent,
)


class Robot:
    # class variable，for robot_id count
    # instance_count = 0

    def __init__(
        self,
        name,
        capacity,
        room_list,
        manipulation_capacity,
        comm_mode="Plan_then_Act",
    ):
        # self.name = f"Robot_{Robot.instance_count}"
        # Robot.instance_count += 1
        self.step = 0
        self.comm_step = 1
        self.last_subtask = None
        self.complete_misplaced_task = []
        self.name = name
        self.coordinate = [0, 0, 0]
        self.holding_object = None
        self.distance = 2
        self.capacity = capacity
        self.scene_graph = {}  # update when observe eg. {'object1': {'room': 'living room', 'coordinate': [x, y, z]}, ...}
        self.room = None
        self.observation = "Don't have observation now. Because I just begin of work."  # update when observe
        self.manipulation_capacity = manipulation_capacity
        self.misplaced_obj_and_container = {}
        self.moveable_objects = []  # Objects that can be moved
        self.pickable_objects = []  # Only pickable objects can be picked up
        self.placeable_objects = []  # Only placeable objects can be placed on  
        self.teammates = None
        self.pool_teammates = None
        # 'collaboration_list': A list of robots collaborating on the same task, either handling the same object or working on different aspects of the same object.
        # Example: [{'name': 'robot1', 'task': 'go to pick misplaced object A'}, {'name': 'robot2', 'task': 'go to pull bed so that A could be pick'}] indicates that robot1 and robot2 are both working on handle same misplaced object.
        self.collaboration_list = []
        # update only when other robot have confirmed the room is explored. You can't update this when you are assigned to explore a room.
        self.explored_rooms = []
        self.unexplored_rooms = room_list
        # Agents
        self.communication_agent = CommunicationAgent(self.name, room_list, comm_mode)
        self.action_agent = ActionAgent(self.name)
        self.observation_agent = ObservationAgent(self.name)
        self.reflection_agent = RelfectionAgent(self.name)
        self.progress_agent = ProgressAgent(self.name)
        # action_hostory
        self.action_history = [
            "Step_0 - [Join the team] - Entreing house from the main door."
        ]

    def get_observation(self, observation: dict):
        """
        Args:
            observation (dict): observation from the environment. eg. {'object1': {'room': 'living room', 'coordinate': [x, y, z]}, 'description':'x', ...}
        Returns:
            observation_str (str): observation in natural language
            new_obj (dict): new object that observed in this observation
        """
        new_obj = {
            obj: observation[obj] for obj in observation if obj not in self.scene_graph
        }
        # update scene_graph
        for obj in new_obj.keys():
            self.scene_graph[obj] = new_obj[obj]
            # update pickable_objects and placeable_objects
            if "PickUpableObjects" in new_obj[obj]["type"]:
                self.pickable_objects.append(obj)
            if "Placeable" in new_obj[obj]["type"]:
                self.placeable_objects.append(obj)
            if "MoveableObjects" in new_obj[obj]["type"]:
                self.moveable_objects.append(obj)

        # get observation_str
        if len(new_obj.keys()) != 0:
            observation_str = (
                f"I observed the following new objects: {', '.join(new_obj.keys())}."
            )
            description_str = ""
            for obj in new_obj.keys():
                if (
                    (new_obj[obj]["description"] != "")
                    and ("StaticObjects" not in new_obj[obj]["type"])
                    and ("None" not in new_obj[obj]["type"])
                ):
                    description_str += new_obj[obj]["description"]
            if description_str != "":
                observation_str += f" {description_str}"
        else:
            observation_str = f"Nothing new observed."
        return observation_str, new_obj

    def get_action_space(self, env, mapper):
        action_space = []
        if len(self.unexplored_rooms) != 0:
            explore_actions = [f"[explore] <{room}>" for room in self.unexplored_rooms]
            action_space.extend(explore_actions)
            action_space.append("\n")

        all_objects = list(
            set(self.pickable_objects + self.placeable_objects + self.moveable_objects)
        )
        if self.manipulation_capacity and len(all_objects) != 0:
            if self.holding_object is None:
                # pick action
                if len(self.misplaced_obj_and_container) > 0:
                    misplaced_objects = list(self.misplaced_obj_and_container.keys())
                    misplaced_goto_actions = [
                        f"[gopick] <{obj}>" for obj in misplaced_objects
                    ]
                    action_space.extend(misplaced_goto_actions)
                    action_space.append("\n")

                if len(self.moveable_objects) > 0:
                    movable_goto_actions = [
                        f"[gopull] <{obj}>" for obj in self.moveable_objects
                    ]
                    action_space.extend(movable_goto_actions)
                    action_space.append("\n")
        
            else:
                # place action
                if len(self.placeable_objects) != 0:
                    place_actions = [
                        f"[goplace] <{self.holding_object}> <{obj}>"
                        for obj in self.placeable_objects
                    ]
                    action_space.extend(place_actions)
                    action_space.append("\n")

        # Only allow exit if robot is not holding any object
        if self.holding_object is None:
            action_space.append("[exit]")
        return action_space

    def get_object_can_manipulate(self):
        object_can_manipulate = []
        for obj in self.scene_graph.keys():
            distance = self.get_distance_with_target_object(obj)
            if distance < self.distance:
                object_can_manipulate.append(obj)
        return object_can_manipulate

    def get_distance_with_target_object(self, target_object):
        if target_object not in self.scene_graph:
            raise ("Not in scene graph")
        robot_coordinate_2d = self.coordinate[:3:2]
        obj_coordinate_2d = self.scene_graph[target_object]["coordinate"][:3:2]
        return math.dist(robot_coordinate_2d, obj_coordinate_2d)

    def get_current_state(self):
        # Format teammates' capacity as natural language
        teammates_info = "\n   -" + "\n   -".join(self.teammates)
        # Format collaboration list
        collaboration_info = []
        collaboration_info.append("I am collaborating with the following teammates:")
        for collaborator in self.collaboration_list:
            collaboration_info.append(collaborator["name"])
        collaboration_info.append(".")
        for collaborator in self.collaboration_list:
            collaboration_info.append(
                f"{collaborator['name']}'s subtask is {collaborator['task']}."
            )
        collaboration_info = (
            " ".join(collaboration_info)
            if len(self.collaboration_list) != 0
            else "No collaboration information available."
        )
        state_report = f"""
- Current Comm Step: {self.comm_step}
- Current Step: {self.step}
- Current Room: {self.room}
- Your Unique Capacity: {self.capacity}
- Teammates: {teammates_info}
"""
        return state_report.strip()

    def get_action_history(self):
        action_info = (
            "\n " + " \n ".join(self.action_history)
            if self.action_history
            else "No actions taken yet."
        )
        return action_info

    def get_last_subtask(self):
        if self.last_subtask:
            return self.last_subtask
        else:
            return "Don't have any task now."

    def get_misplaced_object(self):
        misplaced_objects_info = []
        misplaced_objects_str = ""
        if len(self.misplaced_obj_and_container) != 0:
            misplaced_objects_str += "Not finished subtasks:\n"
            for obj, containers in self.misplaced_obj_and_container.items():
                if obj not in self.scene_graph:
                    continue
                if containers:
                    containers_room_str = ""
                    for container in containers:
                        if container not in self.scene_graph:
                            continue
                        containers_room_str += (
                            f"{container} in {self.scene_graph[container]['room']}; "
                        )
                    misplaced_objects_info.append(
                        f"Misplaced object: {obj} in {self.scene_graph[obj]['room']}, Possible target position: {containers_room_str}\n"
                    )
                else:
                    misplaced_objects_info.append(
                        f"Misplaced object: {obj} in {self.scene_graph[obj]['room']}, Continue explore to find possible target position:\n"
                    )
            misplaced_objects_str = ". ".join(misplaced_objects_info) + "."
        else:
            misplaced_objects_str = "No misplaced object information available.\n"

        complete_info = (
            "Those object have placed in right way before by team:"
            + ", ".join(self.complete_misplaced_task)
            if self.complete_misplaced_task
            else "No Task Complete."
        )
        return misplaced_objects_str + complete_info

    def get_exploration_progress(self):
        exploration_info = ""
        if self.explored_rooms:
            exploration_info = f"Explored rooms: {', '.join(self.explored_rooms)}.\n"
        else:
            exploration_info = "No room has been explored yet.\n"
        if self.unexplored_rooms:
            exploration_info += (
                f"Not explored rooms: {', '.join(self.unexplored_rooms)}.\n"
            )
        else:
            exploration_info += " All rooms have been explored.\n"
        return exploration_info

    def get_task_progress(self):
        exploration_progress = self.get_exploration_progress()
        misplaced_objects = self.get_misplaced_object()
        if self.manipulation_capacity:
            # Object Holding
            holding_info = (
                f"[{self.holding_object}]"
                if self.holding_object
                else "holding nothing.\n"
            )
        else:
            holding_info = "No hand. Holding nothing."
        return exploration_progress + ";\n" + misplaced_objects + ";\n" + holding_info

    def get_communication_history(self):
        communication_history = "\n".join(self.communication_agent.memory)
        return communication_history


if __name__ == "__main__":
    # Example Usage
    # robot = Robot(name="robot1", capacity="height: 150cm, width: 50cm, manipulation_capacity: high, max_force: 200N")
    # robot.teammates = [
    #     {"name": "robot1", "capacity": {"height": "150cm", "width": "50cm", "manipulation_capacity": "high", "max_force": "200N"}, "task": "misplaced_object_search", "last_update": "step4"},
    #     {"name": "robot2", "capacity": {"height": "120cm", "width": "40cm", "manipulation_capacity": "medium", "max_force": "150N"}, "task": "container_retrieval", "last_update": "step5"}
    # ]
    # robot.misplaced_obj_and_container = {'obj_1': ['container1', 'container2'], 'obj_2': []}
    # robot.explored_rooms = ['living room', 'kitchen']
    # robot.unexplored_rooms = ['bathroom']
    # robot.subtask = "misplaced_object_search"
    # robot.collaboration_list = [{'name': 'robot1', 'task': 'misplaced_object_search'}, {'name': 'robot2', 'task': 'container_retrieval'}]

    # # Generate the state report for a given time step, location, observation, and action
    # step = 6
    # location = "living room"
    # observation = "Object 1 appears to be misplaced near the kitchen counter."
    # action = robot.action_history.append("Approaching the object.")

    # state_report = robot.get_current_state(step, location, observation)
    # print(state_report)

    # robot1 = Robot(capacity="height: 150cm, width: 50cm, manipulation_capacity: yes, max_force: 200N" , room_list = ["living room", "kitchen", "bed room"], manipulation_capacity=True)
    # robot2 = Robot(capacity="height: 120cm, width: 40cm, manipulation_capacity: no, max_force: 0N", room_list=["living room", "kitchen", "bed room"], manipulation_capacity=False)
    # print(robot1.get_current_state(1, "living room", "Object 1 appears to be misplaced near the kitchen counter."))

    # robot1 = Robot(capacity="height: 150cm, width: 50cm, manipulation_capacity: yes, max_force: 200N" , room_list = ["living room", "kitchen", "bed room"], manipulation_capacity=True)
    # robot1.scene_graph = {'pillow': {'room': 'living room', 'location': [1, 2, 3]}, 'book': {'room': 'living room', 'location': [2, 3, 4]}}
    # print(robot1.get_action_space())

    # robot2 = Robot(capacity="height: 120cm, width: 40cm, manipulation_capacity: no, max_force: 0N", room_list=["living room", "kitchen", "bed room"], manipulation_capacity=False)
    # robot2.scene_graph = {'table': {'room': 'kitchen', 'location': [1, 2, 3]}, 'chair': {'room': 'kitchen', 'location': [2, 3, 4]}}
    # print(robot2.get_action_space())

    # robot2 = Robot(capacity="height: 120cm, width: 40cm, manipulation_capacity: no, max_force: 0N", room_list=["living room", "kitchen", "bed room"], manipulation_capacity=True)
    # robot2.scene_graph = {'table': {'room': 'kitchen', 'location': [1, 2, 3]}, 'chair': {'room': 'kitchen', 'location': [2, 3, 4]}}
    # print(robot2.get_action_space())

    robot1 = Robot(
        capacity="height: 150cm, width: 50cm, manipulation_capacity: yes, max_force: 200N",
        room_list=["living room", "kitchen", "bed room"],
        manipulation_capacity=True,
    )
    observation = robot1.get_observation(
        {
            "Bed_01": {
                "coordinate": [-4.768, -0.00172480335, -2.009],
                "description": "",
                "room": "Bedroom",
                "type": ["MoveableObjects", "Placeable"],
            },
            "Pillow_11": {
                "coordinate": [-5.952654, 0.325500578, -2.78952885],
                "description": "Pillow_11 is on Floor_dc55730e. Pillow_11 is "
                "between Bed_01 and Walls.",
                "room": "Bedroom",
                "type": ["PickUpableObjects"],
            },
            "WindowSill_01": {
                "coordinate": [-2.49, 0.7392, -3.6323998],
                "description": "WindowSill_01 is on Floor_dc55730e. ",
                "room": "Bedroom",
                "type": ["StaticObjects"],
            },
        }
    )
    print(observation)

    print(robot1.get_current_state())
