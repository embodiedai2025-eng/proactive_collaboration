import difflib
import json
import re
import time

# from llm import get_embedding
from env import Env, get_moving_direction

# from sklearn.metrics.pairwise import cosine_similarity


COMMANDS = ["explore", "gopick", "gopull", "goplace", "exit", "request_new_member"]


def modify_actions(actions, item_mapper, rooms):
    modified_actions = {}
    for robot_name, action in actions.items():
        modified_actions[robot_name] = process_actions(action, item_mapper, rooms)
    return modified_actions


def get_robot_observation(robot, env, item_mapper):
    observation = env.get_observation(robot.name)
    observation = process_observation(observation, item_mapper)
    robot.observation, new_obj_dict = robot.get_observation(observation)
    # TODO: Update room and coordinate
    robot.coordinate = env.get_current_coordinate(robot.name)
    return new_obj_dict


def build_robot_from_config(
    robot_config: dict, ROOMS=["bedroom"], TALK_ALGORITHM="plan"
):
    from robot import Robot

    if robot_config["strength"] > 0:
        manipulation_str = (
            f""", manipulation_capacity: Yes, max_force: {robot_config["strength"]}N"""
        )
    else:
        manipulation_str = ", manipulation_capacity: No, max_force: 0"
    robot = Robot(
        name=robot_config["name"],
        capacity=f"""height: {robot_config["robot_high"]}cm {manipulation_str}""",
        room_list=ROOMS,
        manipulation_capacity=robot_config["strength"] > 0,
        comm_mode=TALK_ALGORITHM,
    )
    return robot


def init_robot_pool_and_team_from_config(env_robot_pool, env_robot_team, ROOMS):
    robot_pool = []
    robot_team = []
    # init robot pool
    for _, robot_config in env_robot_pool.items():
        robot = build_robot_from_config(robot_config, ROOMS)
        robot_pool.append(robot)
    # init robot team
    robot_team = [r for r in robot_pool if r.name in env_robot_team]
    # remove robot team from robot pool
    robot_pool = [r for r in robot_pool if r not in robot_team]
    return robot_pool, robot_team


def init_config(dataset_index: int, dataset_dir: str, remote_url: str):
    """
    Init the environment, robot pool, robot team, rooms from the config file.
    Args:
        dataset_index (int): The index of the dataset in the config file.
        dataset_dir (str): The path to the dataset file.
        remote_url (str): The remote URL for the environment API. Must be provided.
    Returns:
        env (Env): The environment object.
        robot_pool (list[Robot]): The robot pool.
        robot_team (list[Robot]): The robot team.
        ROOMS (list): The list of room names.
    """
    # Set remote URL (required) - MUST be done before any imports that use ue_api functions
    if remote_url is None:
        raise ValueError("remote_url must be provided")
    # Import and set URL before creating Env object
    from robot_skill_sets.unity.ue_api import set_remote_url
    set_remote_url(remote_url)
    
    with open(dataset_dir, "r") as f:
        config = json.load(f)[dataset_index]
        env_robot_pool = config["robot_pool"]  # dict
        env_robot_team = config["robot_team"]  # dict
        misplaced_objects = config["misplaced_objects"]  # list
        misplaced_object_locations = config["object_locations"]  # list[dict]
        scene_index = config["scene_index"]  # int
    with open("scene_room.json", "r") as f:
        scene_room = json.load(f)
        rooms = scene_room[str(scene_index)]
    robot_pool, robot_team = init_robot_pool_and_team_from_config(
        env_robot_pool, env_robot_team, rooms
    )
    env = Env(env_robot_pool, env_robot_team)
    env.rooms = rooms
    env.init_scene(scene_index)
    time.sleep(1)
    env.init_misplaced_objects(misplaced_objects, misplaced_object_locations)
    time.sleep(1)
    env.set_robot(env_robot_team)
    return env, robot_pool, robot_team, rooms, misplaced_objects


def clean_string(input_str):
    # xx_xx
    pattern = r"(\w+)_\w+"
    # Keep only the part before _
    cleaned_str = re.sub(pattern, r"\1", input_str)
    return cleaned_str


def parse_json_from_response(raw_str, key):
    """Parse a JSON string and return the value of a specified key.
    Args:
        raw_str (str): Raw response from LLM. Parse JSON string.
        key (str): Key to extract from the JSON string.
    Returns:
        Any: Value of the specified key in the JSON string.
    Examples:
        raw_str = xxxx ```json{"name": "Alice", "age": 25}```xxx
        name = parse_json_str(raw_str, "name") # "Alice"
    """
    try:
        cleaned_str = (
            raw_str.split("```json")[1].split("```")[0].strip()
        )  # Extract JSON string
    except Exception as e:
        print(f"Error cleaning JSON string: {e}")
        return raw_str
    try:
        json_obj = json.loads(cleaned_str)
        return json_obj[key]
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        # [{...}]
        if cleaned_str.startswith("["):  # Handle list
            return clean_string[1:][:-1]
        return cleaned_str



def robot_name_formulation(robot_name):
    """Formulate the robot name for the API request.
    Args:
        robot_name (str): The name of the robot.
    Returns:
        str: The formulated robot name.
    Examples:
        robot_name = "robot_1"
        formulated_name = robot_name_formulation(robot_name) # "Robot_1"
    """
    robot_index = "".join(filter(str.isdigit, robot_name))
    return f"Robot_{robot_index}"


def get_closest_match(target, options):
    """
    Use difflib to get the closest match to the target from a list of options.
    Args:
        target (str): The target string to match.
        options (list): A list of strings to match against.
    Returns:
        str: The closest match to the target from the list of options.
    """
    matches = difflib.get_close_matches(target, options, n=1)
    return matches[0] if matches else target


class ItemMapper:
    def __init__(self):
        self.forward_map = {}  # complex -> simple
        self.reverse_map = {}  # simple -> complex
        self.counter = {}

    def get_simple_id(self, complex_name):
        if complex_name in self.forward_map:
            return self.forward_map[complex_name]

        base_name = complex_name.split("_")[0].lower()

        # If this is the first occurrence of the item, initialize counter
        if base_name not in self.counter:
            self.counter[base_name] = 1
        else:
            self.counter[base_name] += 1

        # Generate mapped name (e.g., pillow_01, pillow_02)
        mapped_name = f"{base_name}_{self.counter[base_name]}"

        # Update forward and reverse mappings
        self.forward_map[complex_name] = mapped_name
        self.reverse_map[mapped_name] = complex_name

        return mapped_name

    def get_env_object_id(self, mapped_name):
        mapped_name = mapped_name.lower()
        # Remove leading 0 from 01 in pillow_01
        parts = mapped_name.split("_")
        if len(parts) == 2:
            base_name, number = parts
            number = str(int(number))
            mapped_name = f"{base_name}_{number}"
        if mapped_name in self.reverse_map:
            return self.reverse_map[mapped_name]
        else:
            mapped_name = get_closest_match(mapped_name, self.reverse_map.keys())
            if mapped_name in self.reverse_map:
                return self.reverse_map[mapped_name]
        return None


def process_actions(action: str, mapper: ItemMapper, rooms: list, if_env_name=True):
    """
    Process the actions string to match the expected format.
    Args:
        action (str): The input action string. eg. "[goto] <room>"
        mapper (ItemMapper): The item mapper object.
        rooms (list): A list of room names.
    """
    try:
        command = action.split("]")[0].split("[")[1].strip().lower()
    except Exception as e:
        print(f"Error processing action: {e}")
        command = action.split(" ")[0].strip().lower()
    if command not in COMMANDS:
        command = get_closest_match(command, COMMANDS)

    room = None
    if "explore" in command:
        try:
            room = action.split("<")[1].split(">")[0].lower()
        except Exception as e:
            print(f"Error processing action: {e}")
            room = action.split(" ")[1].split(" ")[0].lower()
        if room not in rooms:
            room = get_closest_match(room, rooms)
            # if room not in rooms:
            #     room_embedding = 

    object_name = None
    if "pick" in command or "pull" in command:
        try:
            object_name = action.split("<")[1].split(">")[0].lower()
        except Exception as e:
            print(f"Error processing action: {e}")
            object_name = action.split(" ")[1].split(" ")[0].lower()
        if if_env_name:
            object_name = mapper.get_env_object_id(object_name)

    direction = None
    if if_env_name:
        if "pull" in command:
            try:
                direction = action.split("[")[2].split("]")[0].lower()
            except Exception as e:
                print(f"Error processing action: {e}")
                direction = action.split(" ")[2].split(" ")[0].lower()

    target_position = None
    if "place" in command:
        try:
            target_position = action.split("<")[2].split(">")[0].lower()
        except Exception as e:
            print(f"Error processing action: {e}")
            target_position = action.split(" ")[2].split(" ")[0].lower()
        if if_env_name:
            target_position = mapper.get_env_object_id(target_position)

    processed_input = f"[{command}]"
    if room:
        processed_input += f" <{room}>"
    if object_name:
        processed_input += f" <{object_name}>"
    if direction:
        processed_input += f" [{direction}]"
    if target_position:
        processed_input += f" <{target_position}>"
    return processed_input


def process_observation(observation: dict, mapper: ItemMapper):
    """
    Process the observation dict, replace object names with mapped names.
    Args:
        observation (dict[ObservationMessage]): The observation dict. eg. {'Apple_e01': {'room': 'kitchen', 'coordinate': [1,2,3], 'description': 'Apple_e01 is between the Sink_0a and the Stove_a1.'}}
        mapper (ItemMapper): The item mapper object.
    Returns:
        processed_observation (dict[ObservationMessage])
    """
    processed_observation = {}
    if isinstance(observation, str):
        return {}
    for object_name, object_info in observation.items():
        if "No objects" in object_info:
            continue
        mapped_name = mapper.get_simple_id(object_name)
        # process disctiption, delete all the id next _xxx
        description = object_info["description"]
        description = description.replace(object_name, mapped_name)
        description = clean_string(description)
        processed_observation[mapped_name] = object_info
        processed_observation[mapped_name]["description"] = description
    return processed_observation


if __name__ == "__main__":
    mapper = ItemMapper()

    # Map to simplified name
    complex_name = "Pillow_0e1"
    mapped_name = mapper.get_simple_id(complex_name)
    print(f"{complex_name} mapped to {mapped_name}")

    # complex_name = "Pillow_0e1"
    # mapped_name = mapper.get_simple_id(complex_name)
    # print(f"{complex_name} mapped to {mapped_name}")

    # # Reverse lookup
    # reverse_name = mapper.get_env_object_id("Pillow_01")
    # print(f"{mapped_name} maps back to {reverse_name}")

    # print(
    #     process_actions(
    #         "[go to] <pillo_01>", mapper, ["living room", "kitchen", "bedroom"]
    #     )
    # )
    # import pprint
    # pprint.pprint(
    #     process_observation(
    #         {
    #             "CounterTop_01": {
    #                 "coordinate": [-0.6359999, 0.0, -1.6824],
    #                 "description": "",
    #                 "room": "Bedroom",
    #             },
    #             "Floor_dc55730e": {
    #                 "coordinate": [0.0, 0.0, 0.0],
    #                 "description": "",
    #                 "room": "Bedroom",
    #             },
    #             "Sink_f9ec8510": {
    #                 "coordinate": [-0.702, 1.03632176, -1.8876],
    #                 "description": "Sink_f9ec8510 is on "
    #                 "CounterTop_01. Sink_f9ec8510 is "
    #                 "between Toilet_01 and Walls.",
    #                 "room": "Bedroom",
    #             },
    #         },
    #         mapper,
    #     )
    # )
    print(process_actions("goplace apple_1 table_1", mapper, ["bedroom"]))

