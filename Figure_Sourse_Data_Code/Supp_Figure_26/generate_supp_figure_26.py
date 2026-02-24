import re
from collections import defaultdict
from pathlib import Path

import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt


EMBEDDED_DATASET = {
    "team_number_time_step": {
        "95": {
            "action": {
                "Robot_0": "[exit]",
                "Robot_1": "[explore] <bathroom>",
                "Robot_2": "[exit]",
                "Robot_3": "[explore] <diningroom>",
                "Robot_4": "[explore] <bathroom>",
                "Robot_5": "[explore] <bedroom>",
                "Robot_6": "[explore] <bathroom>",
                "Robot_7": "[explore] <livingroom>",
                "Robot_8": "[explore] <bathroom>",
                "Robot_9": "[explore] <bathroom>",
            }
        },
        "169": {
            "action": {
                "Robot_1": "[gopick] <Statue_01>",
                "Robot_3": "[gopick] <WateringCan_01>",
                "Robot_4": "[explore] <bedroom>",
                "Robot_5": "[explore] <livingroom>",
                "Robot_6": "[gopick] <SoapBottle_01>",
                "Robot_7": "[gopick] <ToiletPaper_01>",
                "Robot_8": "[gopick] <WateringCan_01>",
                "Robot_9": "[explore] <bedroom>",
            }
        },
        "252": {
            "action": {
                "Robot_9": "[gopick] <Pillow_01>",
                "Robot_4": "[explore] <livingroom>",
                "Robot_2": "[gopick] <RemoteControl_01>",
                "Robot_8": "[gopick] <Newspaper_01>",
                "Robot_0": "[gopick] <RemoteControl_01>",
                "Robot_3": "[explore] <bedroom>",
                "Robot_1": "[explore] <diningroom>",
                "Robot_7": "[gopull] <Sofa_01> [0, 0, 1]",
                "Robot_5": "[explore] <livingroom>",
                "Robot_6": "[gopull] <Sofa_01> [0, 0, 1]",
            }
        },
        "310": {
            "action": {
                "Robot_9": "[gopull] <Bed_01> [1, 0, 0]",
                "Robot_4": "[explore] <diningroom>",
                "Robot_2": "[gopick] <RemoteControl_01>",
                "Robot_8": "[explore] <bedroom>",
                "Robot_0": "[explore] <diningroom>",
                "Robot_3": "[explore] <diningroom>",
                "Robot_1": "[goplace] <SideTable_01>",
                "Robot_7": "[gopick] <ToiletPaper_01>",
                "Robot_5": "[explore] <diningroom>",
                "Robot_6": "[gopick] <SoapBottle_01>",
            }
        },
        "398": {
            "action": {
                "Robot_9": "[exit]",
                "Robot_4": "[explore] <bedroom>",
                "Robot_2": "[explore] <bedroom>",
                "Robot_8": "[explore] <bedroom>",
                "Robot_0": "[goplace] <Chair_01>",
                "Robot_3": "[explore] <bedroom>",
                "Robot_1": "[gopick] <Cup_01>",
                "Robot_7": "[explore] <bedroom>",
                "Robot_5": "[exit]",
                "Robot_6": "[explore] <bedroom>",
            }
        },
        "496": {
            "action": {
                "Robot_4": "[exit]",
                "Robot_2": "[gopick] <CreditCard_01>",
                "Robot_8": "[goplace] <DiningTable_01>",
                "Robot_0": "[gopick] <Bread_01>",
                "Robot_3": "[goplace] <CounterTop_05>",
                "Robot_1": "[goplace] <CounterTop_04>",
                "Robot_7": "[goplace] <CounterTop_01>",
                "Robot_6": "[goplace] <SideTable_01>",
            }
        },
        "562": {
            "action": {
                "Robot_2": "[goplace] <Bed_01>",
                "Robot_8": "[gopick] <Pan_01>",
                "Robot_0": "[goplace] <CounterTop_04>",
                "Robot_3": "[gopick] <Pillow_02>",
                "Robot_1": "[gopick] <Pan_01>",
                "Robot_7": "[exit]",
                "Robot_6": "[gopick] <Pan_01>",
            }
        },
        "587": {
            "action": {
                "Robot_9": "[gopull] <Bed_01> [0, 0, 1]",
                "Robot_8": "[gopick] <Cloth_01>",
                "Robot_0": "[gopick] <Pan_01>",
                "Robot_3": "[gopull] <Bed_01> [0, 0, 1]",
                "Robot_1": "[gopick] <Pan_01>",
                "Robot_2": "[gopull] <Bed_01> [1, 0, 0]",
                "Robot_6": "[goplace] <CounterTop_02>",
            }
        },
        "646": {
            "action": {
                "Robot_9": "[exit]",
                "Robot_8": "[goplace] <CounterTop_05>",
                "Robot_0": "[exit]",
                "Robot_3": "[gopick] <CD_01>",
                "Robot_1": "[exit]",
                "Robot_2": "[gopick] <Pillow_01>",
                "Robot_6": "[gopick] <ToiletPaper_02>",
            }
        },
        "742": {
            "action": {
                "Robot_8": "[gopick] <CD_01>",
                "Robot_3": "[goplace] <CounterTop_04>",
                "Robot_2": "[goplace] <Sofa_01>",
                "Robot_6": "[goplace] <Sofa_01>",
            }
        },
        "837": {
            "action": {
                "Robot_8": "[gopick] <SprayBottle_01>",
                "Robot_3": "[gopick] <AlarmClock_01>",
                "Robot_2": "[gopick] <Pillow_02>",
                "Robot_6": "[gopick] <CellPhone_01>",
            }
        },
        "930": {
            "action": {
                "Robot_8": "[goplace] <CounterTop_02>",
                "Robot_3": "[goplace] <SideTable_01>",
                "Robot_2": "[goplace] <Sofa_01>",
                "Robot_6": "[goplace] <SideTable_01>",
            }
        },
    },
    "temporal_step": 930,
}


COLORS = {
    "Explore": "#4E9F9F",
    "Pick": "#4E79A7",
    "Place": "#59A14F",
    "Pull": "#F28E2B",
    "Exit": "#E15759",
    "Idle": "#F0F0F0",
}


def get_clean_object_name(full_name):
    base = re.sub(r"[_\d]+$", "", full_name)
    mapping = {
        "CounterTop": "Counter",
        "SideTable": "SideTbl",
        "DiningTable": "Dining",
        "RemoteControl": "Remote",
        "ToiletPaper": "T-Paper",
        "SprayBottle": "Spray",
        "WateringCan": "WaterCan",
        "SoapBottle": "Soap",
        "AlarmClock": "Alarm",
        "CreditCard": "Card",
        "CellPhone": "Phone",
        "Newspaper": "News",
        "Chair": "Chair",
        "Bread": "Bread",
        "Sofa": "Sofa",
        "Bed": "Bed",
        "Cup": "Cup",
        "Pan": "Pan",
        "Cloth": "Cloth",
        "Statue": "Statue",
        "Pillow": "Pillow",
        "CD": "CD",
    }
    return mapping.get(base, base[:7] if len(base) > 7 else base)


def extract_gantt_data(dataset):
    team_steps = dataset["team_number_time_step"]
    robot_activities = defaultdict(list)
    all_robots = [f"Robot_{i}" for i in range(10)]
    sorted_steps = sorted(team_steps.items(), key=lambda x: int(x[0]))
    final_time = dataset.get("temporal_step", 930)
    prev_t = 0

    def get_action_info(action_str):
        if "[gopick]" in action_str:
            return "Pick", COLORS["Pick"]
        if "[goplace]" in action_str:
            return "Place", COLORS["Place"]
        if "[gopull]" in action_str:
            return "Pull", COLORS["Pull"]
        if "[explore]" in action_str:
            return "Explore", COLORS["Explore"]
        if "[exit]" in action_str:
            return "Exit", COLORS["Exit"]
        return "Idle", COLORS["Idle"]

    for t_str, data in sorted_steps:
        current_time = int(t_str)
        duration = current_time - prev_t
        if duration > 0:
            actions = data["action"]
            for robot in all_robots:
                raw_act = actions.get(robot, "[idle]")
                act_type, color = get_action_info(raw_act)
                robot_activities[robot].append(
                    {
                        "start": prev_t,
                        "duration": duration,
                        "type": act_type,
                        "color": color,
                        "raw": raw_act,
                    }
                )
        prev_t = current_time

    if prev_t < final_time:
        last_actions = sorted_steps[-1][1]["action"]
        for robot in all_robots:
            raw_act = last_actions.get(robot, "[idle]")
            act_type, color = get_action_info(raw_act)
            robot_activities[robot].append(
                {
                    "start": prev_t,
                    "duration": final_time - prev_t,
                    "type": act_type,
                    "color": color,
                    "raw": raw_act,
                }
            )

    return robot_activities, all_robots


def plot_figure2(dataset, output_pdf=None):
    if output_pdf is None:
        output_pdf = Path(__file__).resolve().parent / "supp_figure_26.pdf"
    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 7,
            "axes.labelsize": 8,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 7,
            "axes.linewidth": 0.5,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )

    robot_activities, all_robots = extract_gantt_data(dataset)
    fig, ax = plt.subplots(figsize=(7.08, 5.5))
    bar_height = 10
    y_spacing = 14
    y_ticks, y_labels = [], []

    for i, robot in enumerate(all_robots):
        y_idx = len(all_robots) - 1 - i
        y = y_idx * y_spacing
        y_ticks.append(y + bar_height / 2)
        y_labels.append(robot.replace("Robot_", "R"))

        for seg in robot_activities[robot]:
            if seg["type"] == "Idle":
                continue
            ax.broken_barh(
                [(seg["start"], seg["duration"])],
                (y, bar_height),
                facecolors=seg["color"],
                edgecolor="white",
                linewidth=0.2,
            )

            if seg["duration"] > 45 and seg["type"] in ["Pick", "Place", "Pull"]:
                mid_x = seg["start"] + seg["duration"] / 2
                mid_y = y + bar_height / 2
                obj_name = ""
                if "<" in seg["raw"]:
                    match = re.search(r"<(\w+)", seg["raw"])
                    if match:
                        obj_name = get_clean_object_name(match.group(1))
                ax.text(
                    mid_x,
                    mid_y,
                    f"{seg['type']}\n{obj_name}",
                    ha="center",
                    va="center",
                    color="white",
                    fontsize=6.5,
                    fontweight="bold",
                )

    success_events = [
        (276, "Robot_1"),
        (354, "Robot_0"),
        (413, "Robot_7"),
        (417, "Robot_1"),
        (440, "Robot_6"),
        (462, "Robot_3"),
        (496, "Robot_8"),
        (509, "Robot_0"),
        (531, "Robot_2"),
        (578, "Robot_6"),
        (630, "Robot_8"),
        (658, "Robot_6"),
        (696, "Robot_3"),
        (742, "Robot_2"),
        (861, "Robot_6"),
        (873, "Robot_3"),
        (873, "Robot_8"),
        (930, "Robot_2"),
    ]
    for time, r_name in success_events:
        r_idx = int(r_name.split("_")[1])
        y_idx = len(all_robots) - 1 - r_idx
        y_pos = y_idx * y_spacing + bar_height + 2
        ax.plot(
            time,
            y_pos,
            marker="*",
            markersize=6.5,
            color="#FFD700",
            markeredgecolor="black",
            markeredgewidth=0.4,
            zorder=10,
            clip_on=False,
        )

    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels, fontsize=9)
    ax.set_xlabel("Temporal Step", fontweight="bold", fontsize=10)
    ax.tick_params(axis="x", labelsize=9)
    ax.set_xlim(0, 930)
    ax.set_ylim(-5, len(all_robots) * y_spacing + 5)

    legend_handles = [
        mpatches.Patch(color=COLORS["Explore"], label="Explore"),
        mpatches.Patch(color=COLORS["Pick"], label="Pick"),
        mpatches.Patch(color=COLORS["Place"], label="Place"),
        mpatches.Patch(color=COLORS["Pull"], label="Pull"),
        mpatches.Patch(color=COLORS["Exit"], label="Exit"),
        mlines.Line2D(
            [],
            [],
            color="white",
            marker="*",
            markerfacecolor="#FFD700",
            markeredgecolor="black",
            markersize=8,
            label="Success",
        ),
    ]
    ax.legend(handles=legend_handles, loc="upper center", bbox_to_anchor=(0.5, 1.15), ncol=6, frameon=False, fontsize=9)

    plt.tight_layout()
    plt.savefig(output_pdf, bbox_inches="tight", format="pdf")
    plt.close()
    print(f"[OK] Saved {output_pdf}")


if __name__ == "__main__":
    plot_figure2(EMBEDDED_DATASET)
