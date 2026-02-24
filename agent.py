import json
import random

from llm import chat_completion, completion
from prompts import (
    action_prompt_template,
    comm_task_evaluation_prompt,
    communication_goal_update_prompt,
    communication_plan_prompt,
    communication_prompt,
    failed_reflection_prompt,
    misplaced_detect_prompt,
    misplaced_object_container_reason_prompt,
    pull_purpose_prompt,
    success_reflection_prompt,
)
from tools import (
    COMMANDS,
    get_closest_match,
    get_moving_direction,
    parse_json_from_response,
    process_actions,
)


class Agent:
    def __init__(self, robot_name, model="gpt-4o") -> None:
        self.model = model
        self.robot_name = robot_name
        self.memory = []

    def format_prompt(self, prompt_template: str, **kwargs) -> str:
        return prompt_template.format(**kwargs)


class CommunicationAgent(Agent):
    def __init__(self, robot_name, all_rooms, mode="Act", model="gpt-4o") -> None:
        super().__init__(robot_name, model)
        self.phase = 0  # 0: Plan, 1: Goal Update
        if "plan" in mode.lower():
            self.mode = "Plan_then_Act"
        elif "act" in mode.lower():
            self.mode = "Act"
        else:
            raise (f"Invalid mode {self.mode}.")

        self.plan_prompt = communication_plan_prompt
        self.communicate_prompt = communication_prompt
        self.goal_update_prompt = communication_goal_update_prompt
        self.all_rooms = all_rooms
        self.purpose = None
        self.goal = {}

    def update_robot_state(
        self,
        subtask,
        misplaced_obj_and_container,
        teammates,
        collaboration_list,
        explored_rooms,
        unexplored_rooms,
    ):
        self.subtask = subtask
        self.misplaced_obj_and_container = misplaced_obj_and_container
        self.teammates = teammates
        self.collaboration_list = collaboration_list
        self.explored_rooms = explored_rooms
        self.unexplored_rooms = [
            room for room in unexplored_rooms if room not in explored_rooms
        ]

    def plan(
        self,
        current_status,
        task_progress,
        last_subtask,
        action_history,
        dialogue_history,
        robot_pool,
        purpose,
    ):
        self.phase = 1
        self.facts = None
        plan_prompt = self.format_prompt(
            self.plan_prompt,
            robot_name=self.robot_name,
            current_status=current_status,
            task_progress=task_progress,
            current_subtask=last_subtask,
            action_history=action_history,
            dialogue_history=dialogue_history,
            # robot_pool=robot_pool,
            goal=purpose,
            all_rooms=self.all_rooms,
        )
        response = completion(plan_prompt)["response"].lower()
        facts = parse_json_from_response(response, "facts")
        plan = parse_json_from_response(response, "plan")
        if isinstance(plan, str):
            communication_goal = [plan]
        if isinstance(facts, str):
            facts = [facts]
        else:
            communication_goal = plan
        if len(communication_goal) == 0:
            self.goal = [
                "No communication goal. Try to answer teammates' messages to promote cooperation"
            ]
            return []
        if "none" in communication_goal[0] or "None" in communication_goal[0]:
            self.goal = [
                "No communication goal. Try to answer teammates' messages to promote cooperation"
            ]
            return []
        else:
            self.goal = communication_goal
            self.facts = facts
            goal_str = ""
            for g in communication_goal:
                goal_str += f"{str(g)}\n"
        # Only print brief summary if purpose exists
        if goal_str.strip():
            print(f"{self.robot_name} purpose: {goal_str.strip()}")
            return communication_goal

    def communicate(
        self,
        current_status,
        task_progress,
        last_subtask,
        action_history,
        dialogue_history,
        robot_pool,
    ):
        dialogue_history = "\n".join(self.memory)
        communication_goal_str = ""
        for g in self.goal:
            communication_goal_str += f"{str(g)}\n"
        facts_str = ""
        if self.facts:
            for f in self.facts:
                facts_str += f"{str(f)}\n"
            facts_str = "\n".join(str(self.facts))
        communicate_prompt = self.format_prompt(
            self.communicate_prompt,
            robot_name=self.robot_name,
            current_status=current_status,
            task_progress=task_progress,
            current_subtask=last_subtask,
            action_history=action_history,
            dialogue_history=dialogue_history,
            communication_goal=communication_goal_str,
            # robot_pool=robot_pool,
            facts=facts_str,
            all_rooms=self.all_rooms,
        )
        response = completion(communicate_prompt)["response"]

        messages = [{"role": "user", "content": communicate_prompt}]
        for i in range(5):
            contents = parse_json_from_response(response, "contents")

            if isinstance(contents, list):
                if len(contents) == 0:
                    contents.append({
                        "receiver": ["None"],
                        "message": "None"
                    })
                    break

                if isinstance(contents[0], dict):
                    break

            else:
                print(f"\n Wrong format contents: {contents}")
                messages.append({"role": "assistant", "content": response})
                guidence_str = (
                    f"Your last answer: {contents} not fit the format. 'contents' is a list of json!\n Check your output format, and try again.")
                messages.append({"role": "user", "content": guidence_str})
                response = chat_completion(messages, 0.7)["response"] 
        return contents


    def goal_update(
        self,
        current_status,
        task_progress,
        last_subtask,
        action_history,
        dialogue_history,
        robot_pool,
    ):
        if self.goal == []:
            return []
        communication_goal_str = ""
        for g in self.goal:
            communication_goal_str += f"{str(g)}\n"
        facts_str = ""
        for f in self.facts:
            facts_str += f"{str(f)}\n"
        dialogue_history = "\n".join(self.memory)
        goal_update_prompt = self.format_prompt(
            self.goal_update_prompt,
            robot_name=self.robot_name,
            current_status=current_status,
            task_progress=task_progress,
            current_subtask=last_subtask,
            action_history=action_history,
            dialogue_history=dialogue_history,
            communication_goal=communication_goal_str,
            # robot_pool=robot_pool,
            facts=facts_str,
            all_rooms=self.all_rooms,
        )
        response = completion(goal_update_prompt)["response"]
        facts = parse_json_from_response(response, "facts")
        updated_goals = parse_json_from_response(response, "plan")
        self.goal = updated_goals
        self.facts = facts
        goal_str = ""
        for g in updated_goals:
            goal_str += f"{str(g)}\n"
        # Only print brief summary if purpose exists
        if goal_str.strip():
            print(f"{self.robot_name} updated purpose: {goal_str.strip()}")
        return updated_goals

    def act(
        self,
        current_status,
        task_progress,
        last_subtask,
        action_history,
        dialogue_history,
        robot_pool,
    ):
        if len(self.memory) > 20:
            self.memory = self.memory[-20:]
        if self.mode == "Plan_then_Act":
            if self.phase == 0:
                if self.purpose is None:
                    self.purpose = [
                        " No special goal. Response to other's request. Prioritize your task first, then assist teammates if necessary. "
                    ]
                _ = self.plan(
                    current_status,
                    task_progress,
                    last_subtask,
                    action_history,
                    dialogue_history,
                    robot_pool,
                    self.purpose,
                )
            elif self.phase == 1:
                if self.purpose is not None:
                    _ = self.goal_update(
                        current_status,
                        task_progress,
                        last_subtask,
                        action_history,
                        dialogue_history,
                        robot_pool,
                    )
            else:
                raise (f"Agent is in an invalid phase {self.phase}.")
            return self.communicate(
                current_status,
                task_progress,
                last_subtask,
                action_history,
                dialogue_history,
                robot_pool,
            )
        elif self.mode == "Act":
            return self.communicate(
                current_status,
                task_progress,
                last_subtask,
                action_history,
                dialogue_history,
                robot_pool,
            )


class ActionAgent(Agent):
    def __init__(self, robot_name, model="gpt-4o") -> None:
        super().__init__(robot_name, model)
        self.action_prompt = action_prompt_template

    def act(
        self,
        current_status,
        task_progress,
        current_subtask,
        action_history,
        dialogue_history,
        action_space,
        scene_graph,
        misplaced_objects,
        item_mapper,
        rooms
    ):
        action_space_str = "\n".join(action_space)
        prompt = self.format_prompt(
            self.action_prompt,
            robot_name=self.robot_name,
            current_status=current_status,
            task_progress=task_progress,
            current_subtask=current_subtask,
            action_history=action_history,
            # dialogue_history=dialogue_history,
            action_space=action_space_str,
        )
        action_space_ = [a for a in action_space if a != "\n"]
        if len(action_space_) == 0:
            return "[wait]"
        # Action Space is usually long and doesn't change much, skip printing

        messages = [{"role": "user", "content": prompt}]
        response = completion(prompt)["response"]
        for i in range(5):
            action = parse_json_from_response(response, "action")
            try:
                action = process_actions(action, item_mapper, rooms, False)
            except Exception as e:  
                print(f"Error: {e}")
            action = get_closest_match(action, action_space)
            if action.strip().lower() in action_space:
                break
            else:
                print(f"\n Wrong action: {action}")
                messages.append({"role": "assistant", "content": response})
                guidence_str = (
                    f"Your last answer action: {action} \nNot find in action space. \nYou should keep '[]' and '<>' in your output and replace content within it, eg. [explore] <roomA>, [gopick] <apple>, [goplace] <table>, [gopull] <bed>, [stop]\nTry again."
                )
                messages.append({"role": "user", "content": guidence_str})
                response = chat_completion(messages, 0.7)["response"]
            
            if i == 4:
                action = "[wait]"

        if "pull" in action:
            if len(misplaced_objects) == 0:
                action = "[wait]"
            else:
                try:
                    movable_object = action.split("<")[1].split(">")[0]
                except Exception as e:
                    print(f"Error: {e}")
                    movable_object = action.split(" ")[1].split(" ")[0]
                misplaced_objects_str = "\n".join(misplaced_objects)
                prompt = self.format_prompt(
                    pull_purpose_prompt,
                    robot_name=self.robot_name,
                    action=action,
                    dialogue_history=dialogue_history,
                    action_history=action_history,
                    possible_object=misplaced_objects_str,
                )
                messages = [{"role": "user", "content": prompt}]
                response = completion(prompt)["response"]
                for i in range(5):
                    trapped_object = parse_json_from_response(response, "target_object")
                    
                    # Validate: if None, try to get from misplaced_objects
                    if trapped_object is None:
                        print(f"\n Warning: trapped_object is None from LLM response. Attempting to select from misplaced_objects.")
                        if misplaced_objects:
                            trapped_object = random.choice(misplaced_objects)
                            print(f"Selected random object from misplaced_objects: {trapped_object}")
                        else:
                            print(f"Error: misplaced_objects is empty, cannot determine trapped_object")
                            break
                    
                    # Check if trapped_object is valid and in misplaced_objects
                    if trapped_object and trapped_object in misplaced_objects:
                        break
                    else:
                        print(f"\n Wrong trapped_object: {trapped_object}")
                        messages.append({"role": "assistant", "content": response})
                        guidence_str = (
                            f"Your last answer object: {trapped_object},  not in possible object. "
                            f"Please return a valid object name from the possible object list. "
                            f"The target_object field CANNOT be null, None, or empty.")
                        messages.append({"role": "user", "content": guidence_str})
                        response = chat_completion(messages, 0.7)["response"]

                    if i == 4:
                        # Final fallback: use random choice if still not valid
                        if misplaced_objects:
                            trapped_object = random.choice(misplaced_objects)
                            print(f"Final fallback: selected random object from misplaced_objects: {trapped_object}")
                        else:
                            # If no misplaced objects available, cannot determine trapped_object
                            print(f"Warning: No misplaced objects available, cannot determine trapped_object")
                            trapped_object = None
                
                # Final validation: if still None, raise error
                if trapped_object is None:
                    raise ValueError(f"Cannot determine trapped_object for pulling {movable_object}. No valid objects available.")
                
                direction = get_moving_direction(item_mapper.get_env_object_id(movable_object), item_mapper.get_env_object_id(trapped_object))
                action = f"[gopull] <{movable_object}> {str(direction)}"
        
        print(f"{self.robot_name} action: {action}")
        return action


class ObservationAgent(Agent):
    def __init__(self, robot_name, model="gpt-4o") -> None:
        super().__init__(robot_name, model)
        self.misplaced_detect_prompt = misplaced_detect_prompt
        self.misplaced_object_container_reason_prompt = (
            misplaced_object_container_reason_prompt
        )

    def detect_misplaced(self, new_observation: dict):
        """
        Args:
            new_observation (dict): The new observation from the robot.
                eg. {"objetc_name": "description",}
        Returns:
            misplaced_obj (list): A list of new findings of misplaced objects.
                eg. ["object_name1", "object_name2"]
        """
        obs_str = ""
        for obj, info in new_observation.items():
            description = info["description"]
            obs_str += f"{obj} - {description}\n"
        prompt = self.format_prompt(
            self.misplaced_detect_prompt,
            obj_and_description=obs_str,
        )
        response = completion(prompt)["response"]
        misplaced_obj = parse_json_from_response(response, "misplaced_object")
        return misplaced_obj

    def reason_container(self, obj_and_container, known_obj):
        """
        Args:
            obj_and_container (dict): all misplaced objects found by the robot and it container.
                eg. {"object_name1": ["container1", "container2",], "object_name2": []}
            known_obj (list): known obj find by the robot
                eg. ["object_name1", "object_name2", ]
        Returns:
            updated_obj_and_contarin (dict): updated misplaced objects and container.
                eg. {"object_name1": ["container1", "container2", "new_cintainer_1"], "object_name2": ["new_container_2"]}
        """
        prompt = self.format_prompt(
            self.misplaced_object_container_reason_prompt,
            obj_and_container=json.dumps(obj_and_container, indent=4),
            known_container=known_obj,
        )
        response = completion(prompt)["response"]
        updated_obj_and_container = parse_json_from_response(
            response, "updated_obj_and_container"
        )
        return updated_obj_and_container

    def act(
        self,
        obj_and_container: dict,
        new_observation: dict,
        placeable_objects: list[str],
    ):
        """
        Args:
            obj_and_container (dict): all misplaced objects found by the robot and it container.
                eg. {"object_name1": ["container1", "container2",], "object_name2": []}
            new_observation (ObservationMessage): The new observation from the robot.
                eg. {"objetc_name": "description",}
            placeable_objects (list[str]): all placeable objects known
        Returns:
            updated_obj_and_container (dict): updated misplaced objects and container.
                eg. {"object_name1": ["container1", "container2", "new_cintainer_1"], "object_name2": ["new_container_2"]}
        """
        detect_misplaced_obj_flag = False
        update_container_flag = False
        message = ""

        # Filter out pickable objects
        new_observation_pickable = {}
        for obj, info in new_observation.items():
            if "PickUpableObjects" in info["type"]:
                new_observation_pickable[obj] = info

        new_misplaced_obj = {}
        # detect misplaced objects
        if len(new_observation_pickable.keys()) != 0:
            new_misplaced_obj = self.detect_misplaced(new_observation_pickable)  # list
            if isinstance(new_misplaced_obj, str):
                if "none" in new_misplaced_obj.lower():
                    new_misplaced_obj = []
            elif isinstance(new_misplaced_obj, list):
                if len(new_misplaced_obj) != 0:
                    detect_misplaced_obj_flag = True
                    message += f"Find misplaced objects: {new_misplaced_obj}. "

        # add new misplaced objects to obj_and_container
        for obj in new_misplaced_obj:
            if obj not in obj_and_container:
                obj_and_container[obj] = []

        # Reason about container
        if len(obj_and_container) != 0:
            updated_obj_and_container = self.reason_container(
                obj_and_container, placeable_objects
            )
            # Ensure updated_obj_and_container is a dict, fallback to empty dict if parsing failed
            if not isinstance(updated_obj_and_container, dict):
                updated_obj_and_container = {}
            
            # CRITICAL FIX: Ensure all objects from obj_and_container are preserved in updated_obj_and_container
            # If reason_container didn't return some objects, preserve them with their original containers
            for obj, containers in obj_and_container.items():
                if obj not in updated_obj_and_container:
                    # Object was in input but not in output - preserve it with original containers
                    updated_obj_and_container[obj] = containers
            
            # Filter the update container
            for obj, container in updated_obj_and_container.items():
                if len(container) != 0:
                    obj = get_closest_match(obj, obj_and_container.keys())
                    if container != obj_and_container[obj]:
                        update_container_flag = True
                        for c in container:
                            if c not in obj_and_container[obj]:
                                message += f"Find new container for object {obj}: {c}\n"
        else:
            updated_obj_and_container = {}

        return (
            detect_misplaced_obj_flag,
            update_container_flag,
            updated_obj_and_container,
            message,
        )


class RelfectionAgent(Agent):
    def __init__(self, robot_name, model="gpt-4o") -> None:
        super().__init__(robot_name, model)
        self.success_reflection_prompt = success_reflection_prompt
        self.failed_reflection_prompt = failed_reflection_prompt

    def act(
        self,
        task_progress,
        subtask,
        current_state,
        dialogue,
        action,
        flag,
        action_history,
        feedback=None,
    ):
        if flag:
            reflection_prompt = self.format_prompt(
                self.success_reflection_prompt,
                robot_name=self.robot_name,
                current_state=current_state,
                dialogue_history="\n".join(dialogue),
                action=action,
            )
            response = completion(reflection_prompt)["response"]
            comm_flag = parse_json_from_response(response, "comm_flag")
            comm_goal = parse_json_from_response(response, "comm_goal")

        else:
            reflection_prompt = self.format_prompt(
                self.failed_reflection_prompt,
                robot_name=self.robot_name,
                subtask=subtask,
                task_progress=task_progress,
                action_history=action_history,
                action=action,
                feedback=feedback,
            )
            response = completion(reflection_prompt)["response"]
            reflection = parse_json_from_response(response, "reflection")
            solution = parse_json_from_response(response, "solution")
            comm_flag = parse_json_from_response(response, "comm_flag")
            comm_goal = f"{reflection} - {solution}"
        comm_flag = True if "yes" in comm_flag.lower() else False
        return comm_flag, comm_goal


class ProgressAgent(Agent):
    def __init__(self, robot_name, model="gpt-4o"):
        super().__init__(robot_name, model)
        self.comm_task_evaluation_prompt = comm_task_evaluation_prompt

    def after_comm(
        self,
        current_status,
        task_progress,
        last_subtask,
        action_history,
        dialogue_history,
    ):
        prompt = self.format_prompt(
            self.comm_task_evaluation_prompt,
            robot_name=self.robot_name,
            current_status=current_status,
            task_progress=task_progress,
            last_subtask=last_subtask,
            action_history=action_history,
            dialogue_history=dialogue_history,
        )
        response = completion(prompt)["response"]
        try:
            response = response.split("```json")[1].split("```")[0]
        except Exception as e:
            print(f"Error: {e}")
            response = response
        self.memory.append(response)
        return response


if __name__ == "__main__":
    observation_agent = ObservationAgent("robot_1")
    # Generate test data for misplaced object detection
    new_observation = {
        "pillow_1": {"description": "Found on the floor near bed_2."},
        "cd_1": {"description": "Found on desk_1."},
        "book_1": {"description": "Found on the floor"},
        "plate_1": {"description": "Found on bed_2."},
        "toy_1": {"description": "Found on the sofa."},
    }

    # Test data for reasoning about containers
    # obj_and_container = {
    #     "book_1": ["table_1"],
    #     "pillow": [],
    # }
    obj_and_container = {}
    known_obj = ["bed_1", "table_1", "coffe_table_2"]
    response = observation_agent.act(obj_and_container, new_observation, known_obj)
    print(response)
