import re
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


EMBEDDED_DATASET = {
    "team_number_time_step": {
        "95": {"member_count": 10},
        "169": {"member_count": 8},
        "252": {"member_count": 10},
        "310": {"member_count": 10},
        "398": {"member_count": 10},
        "496": {"member_count": 8},
        "562": {"member_count": 7},
        "587": {"member_count": 7},
        "646": {"member_count": 7},
        "742": {"member_count": 4},
        "837": {"member_count": 4},
        "930": {"member_count": 4},
    },
    "place_object_time_step": {
        "statue_1": 276,
        "remotecontrol_1": 354,
        "newspaper_1": 413,
        "wateringcan_1": 417,
        "cup_1": 440,
        "toiletpaper_2": 462,
        "creditcard_1": 509,
        "bread_1": 531,
        "soapbottle_1": 578,
        "pan_1": 578,
        "cloth_1": 630,
        "cd_1": 658,
        "pillow_2": 696,
        "toiletpaper_1": 742,
        "spraybottle_1": 861,
        "alarmclock_1": 873,
        "cellphone_1": 873,
        "pillow_1": 930,
    },
    "temporal_step": 930,
}


def extract_team_dynamics(dataset):
    team_steps = dataset["team_number_time_step"]
    sorted_steps = sorted(team_steps.items(), key=lambda x: int(x[0]))

    temporal_steps = [0]
    team_sizes = []

    first_time = int(sorted_steps[0][0])
    first_size = sorted_steps[0][1]["member_count"]
    team_sizes.append(first_size)
    temporal_steps.append(first_time)
    team_sizes.append(first_size)

    for i in range(1, len(sorted_steps)):
        prev_time = int(sorted_steps[i - 1][0])
        current_time = int(sorted_steps[i][0])
        prev_size = sorted_steps[i - 1][1]["member_count"]
        current_size = sorted_steps[i][1]["member_count"]

        temporal_steps.append(prev_time)
        team_sizes.append(prev_size)
        temporal_steps.append(prev_time)
        team_sizes.append(current_size)
        temporal_steps.append(current_time)
        team_sizes.append(current_size)

    last_time = int(sorted_steps[-1][0])
    last_size = sorted_steps[-1][1]["member_count"]
    final_temporal = dataset.get("temporal_step", last_time)
    if last_time < final_temporal:
        temporal_steps.append(final_temporal)
        team_sizes.append(last_size)

    place_times = dataset["place_object_time_step"]
    task_completions = []
    for t in sorted(set(place_times.values())):
        count = sum(1 for time in place_times.values() if time <= t)
        task_completions.append({"time": t, "count": count})

    return temporal_steps, team_sizes, task_completions, place_times


def plot_figure1(dataset, output_pdf=None):
    if output_pdf is None:
        output_pdf = Path(__file__).resolve().parent / "supp_figure_25.pdf"
    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 7,
            "axes.labelsize": 8,
            "axes.titlesize": 9,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 7,
            "axes.linewidth": 0.5,
            "grid.linewidth": 0.25,
            "lines.linewidth": 1.0,
            "patch.linewidth": 0.5,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )

    colors = {"blue": "#3B75AF", "orange": "#EF8636", "gray": "#7F7F7F"}
    temporal_steps, team_sizes, task_completions, place_times = extract_team_dynamics(dataset)

    fig, ax1 = plt.subplots(figsize=(7.08, 2.8))
    ax1.plot(
        temporal_steps,
        team_sizes,
        color=colors["blue"],
        linewidth=1.5,
        label="Team Size",
        drawstyle="steps-post",
        zorder=2,
    )

    if temporal_steps and team_sizes:
        ax1.plot(
            temporal_steps[-1],
            team_sizes[-1],
            marker="^",
            markersize=6,
            color="black",
            linestyle="None",
            zorder=5,
            label="All Tasks Complete",
        )

    ax1.set_xlabel("Temporal Step", fontweight="bold")
    ax1.set_ylabel("Active Agents", color=colors["blue"], fontweight="bold")
    ax1.tick_params(axis="y", labelcolor=colors["blue"])
    ax1.set_ylim(0, 11)
    ax1.set_xlim(0, 950)
    ax1.grid(True, axis="y", linestyle="--", linewidth=0.25, alpha=0.5)

    ax2 = ax1.twinx()
    comp_times = [0] + [t["time"] for t in task_completions]
    comp_counts = [0] + [t["count"] for t in task_completions]
    ax2.plot(
        comp_times,
        comp_counts,
        color=colors["orange"],
        linewidth=1.5,
        marker="o",
        markersize=3,
        label="Completed Tasks",
        zorder=2,
    )

    objects_by_time = defaultdict(list)
    for name, time in place_times.items():
        clean = re.sub(r"_\d+", "", name).replace("_", " ").title()
        clean = clean.replace("Remotecontrol", "Remote").replace("Toiletpaper", "Toilet Paper")
        objects_by_time[time].append(clean)

    for time in sorted(objects_by_time.keys()):
        count = sum(1 for t in place_times.values() if t <= time)
        objs = objects_by_time[time]
        label_text = objs[0] + ("..." if len(objs) > 1 else "")
        xytext = (10, 10) if count < 5 else (-15, 10) if count < 12 else (-20, 5)
        ha = "left" if count < 5 else "right"
        ax2.annotate(
            label_text,
            xy=(time, count),
            xytext=xytext,
            textcoords="offset points",
            fontsize=5.5,
            color="#333333",
            ha=ha,
            va="center",
            bbox={"boxstyle": "round,pad=0.1", "fc": "white", "ec": "none", "alpha": 0.7},
            arrowprops={"arrowstyle": "-", "color": colors["gray"], "linewidth": 0.5},
        )

    ax2.set_ylabel("Tasks Completed", color=colors["orange"], fontweight="bold")
    ax2.tick_params(axis="y", labelcolor=colors["orange"])
    ax2.set_ylim(0, 20)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="lower right", frameon=True, framealpha=0.9)

    plt.title("Multi-Agent Team Dynamics and Task Progression", fontweight="bold", pad=10)
    plt.tight_layout()
    plt.savefig(output_pdf, bbox_inches="tight", format="pdf")
    plt.close()
    print(f"[OK] Saved {output_pdf}")


if __name__ == "__main__":
    plot_figure1(EMBEDDED_DATASET)
