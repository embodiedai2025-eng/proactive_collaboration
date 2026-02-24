import json

import os
from itertools import combinations
from pprint import pprint
from typing import Dict, List, Tuple

import tiktoken
from dotenv import load_dotenv

from dispatch_robot import DispatchRobot
from robot import Robot
from tools import parse_json_from_response, robot_name_formulation

load_dotenv()
model_name = os.getenv("MODEL", "gpt-4o")
try:
    encoder = tiktoken.encoding_for_model(model_name)
except:
    encoder = tiktoken.encoding_for_model('gpt-4o')

def get_token_length(text:str):
    return len(encoder.encode(text))

dispatch_robot = DispatchRobot()

class MultiRobotCommunicator:
    """Handles communication among multiple robots by maintaining dialogue history, managing communication counts,
    and sending messages based on CommunicationAgent's actions."""

    def __init__(
        self,
        robots: List[Robot],
        robot_pool: List[Robot],
        env,
        step: int,
        debug=True,
    ):
        """
        Args:
            robots (List[Robot]): List of robot instances
            debug (bool): Debug flag
        """
        self.robots = robots  # List of robot instances
        self.communication_cost = 0
        self.robot_pool = robot_pool
        self.all_robots = robots + robot_pool
        self.robot_names = [
            robot.name for robot in robots
        ]  # List of participating robot names
        self.env = env
        self.step = step
        self.comm_counts = {
            tuple(sorted(pair)): 0 for pair in combinations(self.robot_names, 2)
        }  # Count of communications per robot pair
        self.max_comm = 10  # Max rounds allowed per robot pair (1-2-1-2 is 3 rounds)
        self.num_robot_pairs = len(self.comm_counts)
        self.max_iter_factor = 1
        self.debug = debug
        self.current_round_response = {name: [] for name in self.robot_names}
    
    def add_robot(self, dispatched_robot_list:List[str]):
        self.robot_names.extend(dispatched_robot_list)
        self.robot_names = list(set(self.robot_names))
        new_comm_pairs_list = list(combinations(self.robot_names, 2))
        new_comm_pairs_list = [tuple(sorted(pair)) for pair in new_comm_pairs_list]
        for pair in new_comm_pairs_list:
            if pair not in self.comm_counts:
                self.comm_counts[pair] = 0
        
        for robot_name in dispatched_robot_list:
            self.current_round_dialogue[robot_name] = []

        robot_pairs = len(new_comm_pairs_list)
        max_iterations = int(
            robot_pairs * self.max_comm * self.max_iter_factor
        )
        return self.robot_names, robot_pairs, max_iterations

    def communicate(self):
        """Manages the communication process among robots based on CommunicationAgent's actions.

        Returns:
            current_round_dialogue (dict): Dialogue history for each robot in the current round.
            comm_counts (dict): Communication counts for each robot pair.
        """
        self.current_round_dialogue = {
            name: [] for name in self.robot_names
        }  # Initialize dialogue for the current round


        for robot in self.robots:
            robot.communication_agent.memory.append(f"Comm Step_{self.step}")

        # Initialize communication queue
        communication_queue = []
        for robot in self.robots:
            if robot.communication_agent.purpose:
                communication_queue.append(robot.name)
            
        # communication_queue = self.robot_names.copy()  
        max_iterations = int(
            self.num_robot_pairs * self.max_comm * self.max_iter_factor
        )

        iteration = 0
        while communication_queue and iteration < max_iterations:
            current_robot = communication_queue.pop(0)
            communication_agent = self.get_robot_by_name(
                current_robot
            ).communication_agent

            # Call the CommunicationAgent's act method to get messages
            robot = self.get_robot_by_name(current_robot)
            if robot is None:
                print(f"Robot {current_robot} not found in the robot team.")
                continue

            messages = communication_agent.act(
                robot.get_current_state(),
                                robot.get_task_progress(),
                                robot.get_last_subtask(),
                                robot.get_action_history(),
                                robot.get_communication_history(),
                                robot.pool_teammates
            )

            # Get current purpose for this robot
            purpose_str = ""
            if communication_agent.goal:
                purpose_parts = []
                for g in communication_agent.goal:
                    if isinstance(g, list) and len(g) >= 2:
                        purpose_parts.append(f"[{g[0]}, {g[1]}] {g[2] if len(g) > 2 else ''}")
                    else:
                        purpose_parts.append(str(g))
                purpose_str = " | ".join(purpose_parts)

            # Collect all messages for batch printing
            message_summaries = []
            for m in messages:
                receivers = m.get("receiver", ["None"])
                message = m.get("message", "None")

                if isinstance(receivers, str):
                    receivers = [receivers]

                if receivers == ["None"] or message == "None":
                    if purpose_str:
                        message_summaries.append(f"{current_robot} [purpose: {purpose_str}]: [silent]")
                    else:
                        message_summaries.append(f"{current_robot}: [silent]")
                else:
                    # Format receiver list
                    if "everyone" in receivers[0].lower():
                        receiver_str = "[everyone]"
                    elif "request_new_member" in receivers[0].lower():
                        receiver_str = "[request_new_member]"
                    else:
                        receiver_str = ", ".join(receivers)
                    
                    if purpose_str:
                        message_summaries.append(f"{current_robot} [purpose: {purpose_str}] -> {receiver_str}: {message}")
                    else:
                        message_summaries.append(f"{current_robot} -> {receiver_str}: {message}")
            
            # Batch print all messages for this robot
            if message_summaries and self.debug:
                print(" | ".join(message_summaries))
            
            # Process messages
            for m in messages:
                receivers = m.get("receiver", ["None"])
                message = m.get("message", "None")

                if isinstance(receivers, str):
                    receivers = [receivers]

                if receivers == ["None"] or message == "None":
                    continue

                # Update sender's memory with the sent message
                communication_agent.memory.append(f"send_to_{receivers}: {message}")
                self.current_round_dialogue[current_robot].append(
                    f"send_to_[{receivers}]: {message}"
                )

                if "everyone" in receivers[0].lower():
                    self.broadcast_message(current_robot, message, communication_queue)
                    continue
                
                if "request_new_member" in receivers[0].lower():
                    dispatched_robot_list = dispatch_robot.get_dispatched_list(current_robot, message, self.robot_pool)
                    if dispatched_robot_list:
                        self.robot_names, self.num_robot_pairs, max_iterations= self.add_robot(dispatched_robot_list)
                        receivers = dispatched_robot_list
                        robot_pool, robot_team = dispatch_robot.dispatch_robot(current_robot, message, dispatched_robot_list, self.env, self.robot_pool, self.robots)
                        self.robot_pool = robot_pool
                        self.robots = robot_team
                        dispatch_robot.update_teammates_info(self.robot_pool, self.robots)
                    else:
                        continue

                for receiver in receivers:
                    if "none" in receiver.lower():
                        continue

                    if receiver in self.robot_names:
                        self.update_dialogue_and_queue(
                            current_robot, receiver, message, communication_queue
                        )
                    else:
                        if self.debug:
                            print(
                                f"Receiver {receiver} not found in the robot team."
                            )
                            # filter num in the receiver
                            index = "".join(filter(str.isdigit, receiver))
                            suspected_receiver = f"Robot_{index}"
                            if suspected_receiver in self.robot_names:
                                print(f"Receiver {receiver} is probably {suspected_receiver}, send to suspected_receiver")
                                self.update_dialogue_and_queue(
                                    current_robot, suspected_receiver, message, communication_queue
                                )
                            else:
                                print(f"Receiver {receiver} is not in the robot team, skip")

            iteration += 1

        if iteration >= max_iterations:
            if self.debug:
                print("Communication iterations exceeded the maximum limit.")

        return (
            self.robots,
            self.robot_pool,
            self.current_round_dialogue,
            self.comm_counts,
        )

    def broadcast_message(
        self, current_robot: str, message: str, communication_queue: List[str]
    ):
        """Broadcast message to all other robots."""
        for other_robot in self.robot_names:
            if other_robot != current_robot:
                self.update_dialogue_and_queue(
                    current_robot, other_robot, message, communication_queue
                )

    def update_dialogue_and_queue(
        self,
        current_robot: str,
        receiver: str,
        message: str,
        communication_queue: List[str],
    ):
        """Update dialogue and queue for a robot pair, checking communication limits."""
        pair = tuple(sorted([current_robot, receiver]))
        if pair not in self.comm_counts:
            return 
        self.comm_counts[pair] += 1  # Increment communication count for the robot pair

        # Check if the communication count exceeds max_comm
        if self.comm_counts[pair] > self.max_comm:
            if self.debug:
                msg_preview = message[:50] + "..." if len(message) > 50 else message
                print(f"Comm limit: {current_robot} <-> {receiver} (msg: {msg_preview})")
            return

        # Update sender's dialogue history is already handled in communicate()

        # Update receiver's memory with the received message
        receiver_agent = self.get_robot_by_name(receiver).communication_agent
        if receiver_agent is None:
            print(f"Receiver {receiver} not found in the robot team.")
            return 
        receiver_agent.memory.append(f"received_from_[{current_robot}]: {message}")

        self.communication_cost += get_token_length(message)
        # Update current round dialogue
        self.current_round_dialogue[receiver].append(
            f"received_from_[{current_robot}]: {message}"
        )

        # Add receiver to the communication queue if not already present
        if receiver not in communication_queue:
            communication_queue.append(receiver)

    def get_robot_by_name(self, name: str) -> "Robot":
        """Retrieve a robot instance by its name."""
        for robot in self.all_robots:
            if robot.name == name:
                return robot
        return None

    def __enter__(self):
        if self.debug:
            print("Enter the communicator...")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.debug:
            print("Exit the communicator...")
        del self



def round_robin_communicate(robot_team:list[Robot], comm_step:int, debug=True):
    def update_dialogue(robot:Robot, receiver_robot:Robot, message:str):
        receiver_robot.communication_agent.memory.append(f"receive_from_[{robot.name}]: {message}")

    def broadcast_message(robot, message):
        for other_robot in robot_team:
            if other_robot.name != robot.name:
                update_dialogue(robot, other_robot, message)
    
    robot_name_list = [robot.name for robot in robot_team]

    for robot in robot_team:
        robot.communication_agent.memory.append(f"Comm Step_{comm_step}")
    
    for robot in robot_team:
        messages = robot.communication_agent.act(
            robot.get_current_state(),
                                robot.get_task_progress(),
                                robot.get_last_subtask(),
                                robot.get_action_history(),
                                robot.get_communication_history(),
                                robot.pool_teammates
        )
        # Collect messages for batch printing
        if debug:
            msg_list = []
            for m in messages:
                receivers = m.get("receiver", ["None"])
                message = m.get("message", "None")
                if isinstance(receivers, str):
                    receivers = [receivers]
                if receivers == ["None"] or message == "None":
                    msg_list.append(f"{robot.name}: [silent]")
                else:
                    if "everyone" in receivers[0].lower():
                        receiver_str = "[everyone]"
                    elif "request_new_member" in receivers[0].lower():
                        receiver_str = "[request_new_member]"
                    else:
                        receiver_str = ", ".join(receivers)
                    msg_preview = message[:60] + "..." if len(message) > 60 else message
                    msg_list.append(f"{robot.name} -> {receiver_str}: {msg_preview}")
            if msg_list:
                print(" | ".join(msg_list))
        
        # Process messages
        for m in messages:
            receivers = m.get("receiver", ["None"])
            message = m.get("message", "None")

            if receivers == ["None"] or message == "None":
                continue

            robot.communication_agent.memory.append(f"send_to_[{receivers}]: {message}")
            
            if "everyone" in receivers:
                broadcast_message(robot, message)
            
            else:
                for receiver in receivers:
                    receiver = robot_name_formulation(receiver)
                    if receiver in robot_name_list:
                        receiver_robot = [r for r in robot_team if r.name == receiver][0]
                        update_dialogue(robot, receiver_robot, message)
                    else:
                        print(f"Receiver {receiver} not found in the robot team.")



if __name__ == "__main__":
    # Create three robots with their respective capacities
    robot1 = Robot(
        capacity="height: 150cm, width: 50cm, manipulation_capacity: Yes, max_force: 200N"
    )
    robot1.location = "Living Room"
    robot1.observation = "I find one sofa and a table"
    robot2 = Robot(
        capacity="height: 120cm, width: 40cm, manipulation_capacity: No, max_force: 0"
    )
    robot2.location = "Living Room"
    robot2.observation = "I find one sofa and a table"
    robot3 = Robot(
        capacity="height: 120cm, width: 40cm, manipulation_capacity: Yes, max_force: 150N"
    )
    robot3.location = "Living Room"
    robot3.observation = "I find one sofa and a table"

    communicator = MultiRobotCommunicator([robot1, robot2, robot3], step=1)
    current_round_dialogue, comm_cost = communicator.communicate()

    action_space = [
        "[explore] <living_room>",
        "[explore] <kitchen>",
        "[explore] <bed_room>",
        "[pull] <sofa> <direction> (direction should be a vector, e.g., [1, 0, 0] means pull the sofa to the positive x-axis, [0, 0, -1] means pull the sofa to the negative z-axis)",
    ]

    robot_1_dialogue = current_round_dialogue[robot1.name]
    action_1 = robot1.action_agent.act(
        robot1.get_current_state(), robot_1_dialogue, action_space
    )

    robot_2_dialogue = current_round_dialogue[robot2.name]
    action_2 = robot2.action_agent.act(
        robot2.get_current_state(), robot_2_dialogue, action_space
    )

    robot_3_dialogue = current_round_dialogue[robot3.name]
    action_3 = robot3.action_agent.act(
        robot3.get_current_state(), robot_3_dialogue, action_space
    )
    
    # Print concise actions
    print(f"Actions: {robot1.name}: {action_1}, {robot2.name}: {action_2}, {robot3.name}: {action_3}")
