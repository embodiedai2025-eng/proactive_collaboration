from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt


def draw_nature_comms_gantt_flat_final():
    out_dir = Path(__file__).resolve().parent
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans"]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 6.5), sharex=True)

    c_nav = "#80cdc1"
    c_comm = "#fdae61"
    c_act = "#2c7bb6"
    c_fail = "#d7191c"
    c_misalign = "#9e0142"
    c_wait = "#f0f0f0"
    c_hatch = "#555555"

    y_stretch = 0
    y_aliengo = 12
    y_car = 24
    bar_height = 8
    fs_title = 18
    fs_axis = 14
    fs_tick = 14
    fs_annot = 13
    fs_legend = 13

    t_p_stretch_join = 70
    t_p_act_start = 145
    t_p_act_duration = 75
    t_p_end_plot = t_p_act_start + t_p_act_duration

    ax1.broken_barh([(0, 24)], (y_car, bar_height), facecolors=c_nav)
    ax1.broken_barh([(24, 43)], (y_car, bar_height), facecolors=c_comm)
    ax1.broken_barh([(67, 33)], (y_car, bar_height), facecolors=c_wait, hatch="///", edgecolor=c_hatch)
    ax1.broken_barh([(100, 45)], (y_car, bar_height), facecolors=c_comm)
    ax1.broken_barh([(145, 61)], (y_car, bar_height), facecolors=c_wait, hatch="///", edgecolor=c_hatch)
    ax1.broken_barh([(206, 64)], (y_car, bar_height), facecolors=c_comm)
    ax1.broken_barh([(270, 50)], (y_car, bar_height), facecolors=c_wait, hatch="///", edgecolor=c_hatch)
    ax1.broken_barh([(320, 60)], (y_car, bar_height), facecolors=c_act)

    ax1.broken_barh([(0, 24)], (y_aliengo, bar_height), facecolors=c_nav)
    ax1.broken_barh([(24, 43)], (y_aliengo, bar_height), facecolors=c_comm)
    ax1.broken_barh([(67, 33)], (y_aliengo, bar_height), facecolors=c_fail, label="Physical Failure")
    ax1.broken_barh([(100, 45)], (y_aliengo, bar_height), facecolors=c_comm)
    ax1.broken_barh([(145, 61)], (y_aliengo, bar_height), facecolors=c_misalign, hatch="XX", edgecolor="white")
    ax1.broken_barh([(206, 64)], (y_aliengo, bar_height), facecolors=c_comm)
    ax1.broken_barh([(270, 110)], (y_aliengo, bar_height), facecolors=c_nav)

    ax1.broken_barh([(155, 51)], (y_stretch, bar_height), facecolors=c_misalign, hatch="XX", edgecolor="white")
    ax1.broken_barh([(206, 64)], (y_stretch, bar_height), facecolors=c_comm)
    ax1.broken_barh([(270, 50)], (y_stretch, bar_height), facecolors=c_nav, label="Nav")
    ax1.broken_barh([(320, 60)], (y_stretch, bar_height), facecolors=c_act)

    for y_pos in [y_car, y_stretch]:
        ax1.annotate(
            "",
            xy=(385, y_pos + bar_height / 2),
            xytext=(380, y_pos + bar_height / 2),
            arrowprops=dict(arrowstyle="->", color=c_act, lw=3),
        )

    ax1.annotate(
        "Fail: Move Cart\n(1:40)",
        xy=(100, 12),
        xytext=(100, -15),
        arrowprops=dict(facecolor=c_fail, shrink=0.05, width=2.5, headwidth=10, edgecolor="none"),
        fontsize=fs_annot,
        color=c_fail,
        fontweight="bold",
        ha="center",
        va="top",
    )
    ax1.annotate(
        "",
        xy=(145, -2),
        xytext=(206, -2),
        arrowprops=dict(arrowstyle="|-|, widthA=0.5, widthB=0.5", color=c_misalign, lw=2.5),
    )
    ax1.text(
        (145 + 206) / 2,
        -15,
        "Misaligned Action\n(Lack of Coordination)",
        ha="center",
        fontsize=fs_annot,
        color=c_misalign,
        fontweight="bold",
        va="top",
    )
    ax1.set_yticks([y_stretch + 4, y_aliengo + 4, y_car + 4])
    ax1.set_yticklabels(["Stretch\n(Helper)", "AlienGo", "Car"], fontsize=fs_tick, fontweight="bold")
    ax1.set_title(
        "Responsive Paradigm: Failure $\\to$ Sync Comm $\\to$ Misalignment $\\to$ Recovery",
        loc="left",
        fontsize=fs_title,
        fontweight="bold",
        pad=10,
    )
    ax1.set_ylim(-35, 65)
    ax1.spines["right"].set_visible(False)
    ax1.spines["top"].set_visible(False)

    ax2.broken_barh([(0, 19)], (y_car, bar_height), facecolors=c_nav)
    ax2.broken_barh([(19, 76)], (y_car, bar_height), facecolors=c_comm)
    ax2.broken_barh([(95, 50)], (y_car, bar_height), facecolors=c_wait, hatch="///", edgecolor=c_hatch)
    ax2.broken_barh([(145, t_p_act_duration)], (y_car, bar_height), facecolors=c_act)

    ax2.broken_barh([(0, 19)], (y_aliengo, bar_height), facecolors=c_nav)
    ax2.broken_barh([(19, 76)], (y_aliengo, bar_height), facecolors=c_comm)
    ax2.broken_barh([(95, 125)], (y_aliengo, bar_height), facecolors=c_nav)

    ax2.broken_barh([(t_p_stretch_join, 25)], (y_stretch, bar_height), facecolors=c_comm)
    ax2.broken_barh([(95, 50)], (y_stretch, bar_height), facecolors=c_nav)
    ax2.broken_barh([(145, t_p_act_duration)], (y_stretch, bar_height), facecolors=c_act)

    for y_pos in [y_car, y_stretch]:
        ax2.annotate(
            "",
            xy=(t_p_end_plot + 5, y_pos + bar_height / 2),
            xytext=(t_p_end_plot, y_pos + bar_height / 2),
            arrowprops=dict(arrowstyle="->", color=c_act, lw=3),
        )

    ax2.annotate(
        "Conflict Anticipated\n(0:19)",
        xy=(19, y_car + bar_height),
        xytext=(19, 42),
        arrowprops=dict(facecolor="blue", shrink=0.05, width=2.5, headwidth=10, edgecolor="none"),
        fontsize=fs_annot,
        color="blue",
        fontweight="bold",
        ha="left",
        va="bottom",
    )
    ax2.annotate(
        "Recruited & Informed\n(1:10)",
        xy=(70, 0),
        xytext=(70, -18),
        arrowprops=dict(facecolor="#d95f02", shrink=0.05, width=2.5, headwidth=10, edgecolor="none"),
        fontsize=fs_annot,
        color="#d95f02",
        fontweight="bold",
        ha="center",
        va="top",
    )
    ax2.annotate(
        "",
        xy=(145, -5),
        xytext=(320, -5),
        arrowprops=dict(arrowstyle="<->", color="purple", lw=3),
    )
    ax2.text(
        (145 + 320) / 2,
        -18,
        "Performance Gap: ~175s\n(Due to Misalignment)",
        ha="center",
        fontsize=fs_annot,
        color="purple",
        fontweight="bold",
        va="top",
    )
    ax2.set_yticks([y_stretch + 4, y_aliengo + 4, y_car + 4])
    ax2.set_yticklabels(["Stretch\n(Helper)", "AlienGo", "Car"], fontsize=fs_tick, fontweight="bold")
    ax2.set_title(
        "Proactive Paradigm: Anticipation $\\to$ Direct Coordination",
        loc="left",
        fontsize=fs_title,
        fontweight="bold",
        pad=10,
    )
    ax2.set_xlabel("Task Execution Time (seconds)", fontsize=fs_axis, fontweight="bold")
    ax2.set_ylim(-35, 65)
    ax2.spines["right"].set_visible(False)
    ax2.spines["top"].set_visible(False)

    ax1.grid(True, axis="x", linestyle=":", color="gray", alpha=0.5)
    ax2.grid(True, axis="x", linestyle=":", color="gray", alpha=0.5)

    legend_elements = [
        mpatches.Patch(facecolor=c_nav, label="Nav/Explore"),
        mpatches.Patch(facecolor=c_comm, label="Communication"),
        mpatches.Patch(facecolor=c_act, label="Collaborate"),
        mpatches.Patch(facecolor=c_fail, label="Failure"),
        mpatches.Patch(facecolor=c_misalign, hatch="XX", edgecolor="white", label="Misaligned Action"),
        mpatches.Patch(facecolor=c_wait, hatch="///", edgecolor=c_hatch, label="Wait/Observe"),
    ]
    ax1.legend(
        handles=legend_elements,
        loc="upper right",
        ncol=3,
        fontsize=fs_legend,
        frameon=True,
        framealpha=0.95,
        edgecolor="#cccccc",
        borderpad=0.5,
    )

    plt.xlim(-10, 400)
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.3)

    plt.savefig(out_dir / "main_figure_7.pdf", format="pdf", bbox_inches="tight", dpi=300)
    plt.savefig(out_dir / "main_figure_7.png", format="png", bbox_inches="tight", dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    draw_nature_comms_gantt_flat_final()