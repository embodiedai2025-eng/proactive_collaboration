from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans"]
    plt.rcParams["font.size"] = 12
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.labelsize"] = 13
    plt.rcParams["xtick.labelsize"] = 12
    plt.rcParams["ytick.labelsize"] = 12
    plt.rcParams["legend.fontsize"] = 12

    categories = ["Fixed", "Responsive", "Proactive"]
    success = np.array([0.45, 0.55, 0.90])
    avg_time = np.array([931, 894, 735])

    y = np.arange(len(categories))

    fig = plt.figure(figsize=(18, 5.2), dpi=150)
    outer = fig.add_gridspec(1, 3, width_ratios=[1, 1, 1], wspace=0.25)
    inner = outer[0, 0:2].subgridspec(1, 3, width_ratios=[1.0, 0.38, 1.0], wspace=0.02)
    ax_l = fig.add_subplot(inner[0, 0])
    ax_mid = fig.add_subplot(inner[0, 1], sharey=ax_l)
    ax_r = fig.add_subplot(inner[0, 2], sharey=ax_l)
    ax_bar = fig.add_subplot(outer[0, 2])

    c_success = "#6f8fb2"
    c_time = "#ffbd8f"
    c_bar = "#8fc4e8"

    bars_l = ax_l.barh(y, success, height=0.35, color=c_success, edgecolor="none")
    ax_l.set_xlim(1.0, 0.0)
    ax_l.set_xticks([1.0, 0.0])
    ax_l.set_title("Success Rate (%)", pad=10)
    ax_l.text(-0.08, 1.02, "a", transform=ax_l.transAxes, fontsize=16, fontweight="bold", va="bottom", ha="left")
    ax_l.axvline(0.0, color="#5c5c5c", lw=1)

    for rect, val in zip(bars_l, success):
        y0 = rect.get_y() + rect.get_height() / 2
        ax_l.text(val + 0.03, y0, f"{val:.2f}", va="center", ha="right", fontsize=12, fontweight="bold")

    ax_mid.set_axis_off()
    for yi, name in zip(y, categories):
        ax_mid.text(0.5, yi, name, ha="center", va="center", fontsize=13, fontweight="bold")

    bars_r = ax_r.barh(y, avg_time, height=0.35, color=c_time, edgecolor="none")
    ax_r.set_xlim(600, 950)
    ax_r.set_xticks([600, 950])
    ax_r.set_title("Average Time (s) (Lower is Better)", pad=10)
    ax_r.axvline(600, color="#5c5c5c", lw=1)

    for rect, val in zip(bars_r, avg_time):
        y0 = rect.get_y() + rect.get_height() / 2
        ax_r.text(val + 10, y0, f"{int(val)}", va="center", ha="left", fontsize=12, fontweight="bold")

    for ax in (ax_l, ax_r):
        ax.set_yticks(y)
        ax.set_yticklabels([""] * len(categories))
        ax.tick_params(axis="y", length=0)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)

    ax_l.invert_yaxis()

    bar_heights = np.array([9 / 11, 11 / 18, 18 / 20])
    x_bar = np.arange(len(categories))
    ax_bar.bar(x_bar, bar_heights, width=0.5, color=c_bar, edgecolor="none")
    ax_bar.set_xticks(x_bar)
    ax_bar.set_xticklabels(categories)
    ax_bar.set_ylim(0, 1.05)
    ax_bar.set_ylabel("Conditional Success Rate")
    ax_bar.spines["top"].set_visible(False)
    ax_bar.spines["right"].set_visible(False)
    ax_bar.text(-0.15, 1.02, "b", transform=ax_bar.transAxes, fontsize=16, fontweight="bold", va="bottom", ha="left")

    for xi, h in zip(x_bar, bar_heights):
        ax_bar.text(xi, h + 0.02, f"{h:.2f}", ha="center", va="bottom", fontsize=12)

    handles = [
        plt.Rectangle((0, 0), 1, 1, color=c_success),
        plt.Rectangle((0, 0), 1, 1, color=c_time),
        plt.Rectangle((0, 0), 1, 1, color=c_bar),
    ]
    fig.legend(
        handles,
        ["Success Rate", "Average Time", "Conditional Success Rate (Suff. Team)"],
        loc="lower center",
        ncol=3,
        frameon=False,
    )
    fig.subplots_adjust(bottom=0.18)

    for ext in ("png", "pdf"):
        out = out_dir / f"main_figure_5.{ext}"
        fig.savefig(out, bbox_inches="tight")
        print(f"Saved: {out}")


if __name__ == "__main__":
    main()

