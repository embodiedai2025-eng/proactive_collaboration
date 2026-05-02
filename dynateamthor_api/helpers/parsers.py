import ast
import math
import re


def parse_coordinates_from_string(input_str: str) -> list[list[float]]:
    """Parse '(x, y, z) ; (x, y, z) ...' into [[x, y, z], ...]."""
    cleaned = input_str.strip().replace(" ;", ";").replace("; ", ";")
    coordinates = re.findall(r"\((-?\d+\.\d+),\s*(-?\d+\.\d+),\s*(-?\d+\.\d+)\)", cleaned)
    return [[float(x), float(y), float(z)] for x, y, z in coordinates]


def parse_reachable_points(raw_reachable_points: list[str]) -> set[tuple[float, float]]:
    """Convert reachable point strings into 2D (x, z) tuples."""
    reachable_points: set[tuple[float, float]] = set()
    for point in raw_reachable_points:
        x, _y, z = ast.literal_eval(point)
        reachable_points.add((x, z))
    return reachable_points


def parse_relations(object_neighbors: dict) -> dict:
    """Build simple on/between relations from neighbor rays."""
    relations = {}
    for obj, neighbors in object_neighbors.items():
        if obj in ["error_info", "is_success", "success", "message"]:
            continue

        on_relations = set()
        between_relations = set()

        for rel_pos, neighbor in neighbors.items():
            rel_pos_tuple = tuple(map(float, rel_pos.strip("()").split(",")))
            if rel_pos_tuple == (0.0, -1.0, 0.0):
                on_relations.add(neighbor)

            for other_rel_pos, other_neighbor in neighbors.items():
                if neighbor == other_neighbor or other_neighbor == obj:
                    continue
                other_rel_pos_tuple = tuple(map(float, other_rel_pos.strip("()").split(",")))
                if rel_pos_tuple[0] == -other_rel_pos_tuple[0] and rel_pos_tuple[1:] == other_rel_pos_tuple[1:]:
                    between_relations.add(tuple(sorted([neighbor, other_neighbor])))
                if rel_pos_tuple[2] == -other_rel_pos_tuple[2] and rel_pos_tuple[:2] == other_rel_pos_tuple[:2]:
                    between_relations.add(tuple(sorted([neighbor, other_neighbor])))

        relations[obj] = {"on": list(on_relations), "between": list(between_relations)}
    return relations


def relation_to_str(_objects: list[str], relation_dict: dict) -> str:
    """Render compact human-readable relation summary."""
    object_str = ""
    for obj, relations in relation_dict.items():
        if relations["on"]:
            object_str += f"{obj} is on "
            for on_obj in relations["on"]:
                object_str += f"{on_obj}"
                if on_obj != relations["on"][-1]:
                    object_str += ", "
            object_str += ". "
        if relations["between"]:
            for between_objs in relations["between"]:
                object_str += f"{obj} is between {between_objs[0]} and {between_objs[1]}. "
    return object_str.strip()


def get_2d_distance(point1: list[float], point2: list[float]) -> float:
    x1, _, z1 = point1
    x2, _, z2 = point2
    return math.sqrt((x2 - x1) ** 2 + (z2 - z1) ** 2)

