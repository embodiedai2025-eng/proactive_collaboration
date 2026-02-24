import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.legend_handler import HandlerTuple

PLOTTING_DATA = {
    "initial_team_size": {
        "autogen_rr": {
            1: {"FINAL_strict_success": 0.4537037037037037, "FINAL_temporal_step": 1073.7407407407406},
            2: {"FINAL_strict_success": 0.42592592592592593, "FINAL_temporal_step": 1130.5833333333333},
            3: {"FINAL_strict_success": 0.5185185185185185, "FINAL_temporal_step": 1061.0277777777778},
            4: {"FINAL_strict_success": 0.5740740740740741, "FINAL_temporal_step": 965.8611111111111},
            5: {"FINAL_strict_success": 0.6666666666666666, "FINAL_temporal_step": 888.1018518518518},
            6: {"FINAL_strict_success": 0.6822429906542056, "FINAL_temporal_step": 888.0373831775701},
        },
        "mhrc": {
            1: {"FINAL_strict_success": 0.5462962962962963, "FINAL_temporal_step": 1047.8333333333333},
            2: {"FINAL_strict_success": 0.5277777777777778, "FINAL_temporal_step": 1062.4537037037037},
            3: {"FINAL_strict_success": 0.5370370370370371, "FINAL_temporal_step": 1007.0648148148148},
            4: {"FINAL_strict_success": 0.6203703703703703, "FINAL_temporal_step": 922.9907407407408},
            5: {"FINAL_strict_success": 0.6296296296296297, "FINAL_temporal_step": 903.9814814814815},
            6: {"FINAL_strict_success": 0.6388888888888888, "FINAL_temporal_step": 867.1203703703703},
        },
        "h_team": {
            1: {"FINAL_strict_success": 0.5092592592592593, "FINAL_temporal_step": 1057.148148148148},
            2: {"FINAL_strict_success": 0.49074074074074076, "FINAL_temporal_step": 1066.0833333333333},
            3: {"FINAL_strict_success": 0.5925925925925926, "FINAL_temporal_step": 965.6851851851852},
            4: {"FINAL_strict_success": 0.6203703703703703, "FINAL_temporal_step": 890.1666666666666},
            5: {"FINAL_strict_success": 0.6574074074074074, "FINAL_temporal_step": 830.7962962962963},
            6: {"FINAL_strict_success": 0.6759259259259259, "FINAL_temporal_step": 807.9722222222222},
        },
        "ours": {
            1: {"FINAL_strict_success": 0.6944444444444444, "FINAL_temporal_step": 876.4907407407408},
            2: {"FINAL_strict_success": 0.6759259259259259, "FINAL_temporal_step": 819.6481481481482},
            3: {"FINAL_strict_success": 0.7129629629629629, "FINAL_temporal_step": 805.0648148148148},
            4: {"FINAL_strict_success": 0.6759259259259259, "FINAL_temporal_step": 795.5092592592592},
            5: {"FINAL_strict_success": 0.7407407407407407, "FINAL_temporal_step": 736.7592592592592},
            6: {"FINAL_strict_success": 0.7222222222222222, "FINAL_temporal_step": 648.5092592592592},
        },
    },
    "missed_num": {
        "autogen_rr": {
            2: {"FINAL_strict_success": 0.7037037037037037, "FINAL_temporal_step": 851.0246913580247},
            3: {"FINAL_strict_success": 0.5740740740740741, "FINAL_temporal_step": 949.0987654320987},
            4: {"FINAL_strict_success": 0.47530864197530864, "FINAL_temporal_step": 1081.9197530864199},
            5: {"FINAL_strict_success": 0.45962732919254656, "FINAL_temporal_step": 1124.3167701863354},
        },
        "mhrc": {
            2: {"FINAL_strict_success": 0.691358024691358, "FINAL_temporal_step": 882.1604938271605},
            3: {"FINAL_strict_success": 0.6419753086419753, "FINAL_temporal_step": 912.4320987654321},
            4: {"FINAL_strict_success": 0.46296296296296297, "FINAL_temporal_step": 1014.1543209876543},
            5: {"FINAL_strict_success": 0.5370370370370371, "FINAL_temporal_step": 1065.5493827160494},
        },
        "h_team": {
            2: {"FINAL_strict_success": 0.7222222222222222, "FINAL_temporal_step": 812.5864197530864},
            3: {"FINAL_strict_success": 0.6296296296296297, "FINAL_temporal_step": 914.395061728395},
            4: {"FINAL_strict_success": 0.47530864197530864, "FINAL_temporal_step": 1011.1234567901234},
            5: {"FINAL_strict_success": 0.5370370370370371, "FINAL_temporal_step": 1007.1296296296297},
        },
        "ours": {
            2: {"FINAL_strict_success": 0.8148148148148148, "FINAL_temporal_step": 678.2283950617284},
            3: {"FINAL_strict_success": 0.7469135802469136, "FINAL_temporal_step": 735.7777777777778},
            4: {"FINAL_strict_success": 0.6172839506172839, "FINAL_temporal_step": 804.0185185185185},
            5: {"FINAL_strict_success": 0.6358024691358025, "FINAL_temporal_step": 903.2962962962963},
        },
    },
    "trapped_num": {
        "autogen_rr": {
            0: {"FINAL_strict_success": 0.7361111111111112, "FINAL_temporal_step": 768.0185185185185},
            1: {"FINAL_strict_success": 0.5092592592592593, "FINAL_temporal_step": 1067.875},
            2: {"FINAL_strict_success": 0.413953488372093, "FINAL_temporal_step": 1169.0837209302326},
        },
        "mhrc": {
            0: {"FINAL_strict_success": 0.7546296296296297, "FINAL_temporal_step": 783.75},
            1: {"FINAL_strict_success": 0.5879629629629629, "FINAL_temporal_step": 1019.0694444444445},
            2: {"FINAL_strict_success": 0.4074074074074074, "FINAL_temporal_step": 1102.9027777777778},
        },
        "h_team": {
            0: {"FINAL_strict_success": 0.7638888888888888, "FINAL_temporal_step": 715.3101851851852},
            1: {"FINAL_strict_success": 0.5879629629629629, "FINAL_temporal_step": 973.5555555555555},
            2: {"FINAL_strict_success": 0.4212962962962963, "FINAL_temporal_step": 1120.0601851851852},
        },
        "ours": {
            0: {"FINAL_strict_success": 0.7824074074074074, "FINAL_temporal_step": 604.9166666666666},
            1: {"FINAL_strict_success": 0.7268518518518519, "FINAL_temporal_step": 840.8194444444445},
            2: {"FINAL_strict_success": 0.6018518518518519, "FINAL_temporal_step": 895.2546296296297},
        },
    },
}

COLOR_MAP = {
    "autogen_rr": "#A9D0F5",
    "mhrc": "#7B68EE",
    "h_team": "#F4A460",
    "ours": "#D62728",
}


def plot_two_metrics_adjusted(data_dict, color_map, title, left_max, left_low, right_max, right_low, save_path):
    methods = list(color_map.keys())
    all_x = set()
    for m in methods:
        all_x.update(data_dict[m].keys())
    sorted_x = sorted(all_x)
    x_index = np.arange(len(sorted_x))

    fig, ax_left = plt.subplots(figsize=(10, 6))
    ax_right = ax_left.twinx()

    total_methods = len(methods)
    bar_width = 0.8 / total_methods
    handles_for_legend = []

    for i, method in enumerate(methods):
        success_vals = []
        step_vals = []
        for x in sorted_x:
            metrics = data_dict[method].get(x, {})
            success_vals.append(metrics.get("FINAL_strict_success", 0.0))
            step_vals.append(metrics.get("FINAL_temporal_step", 0.0))

        offset = i * bar_width
        bars = ax_left.bar(
            x_index + offset,
            success_vals,
            width=bar_width,
            label=f"{method}_bar",
            color=color_map[method],
            alpha=0.6,
        )
        line = ax_right.plot(
            x_index + (total_methods * bar_width) / 2,
            step_vals,
            marker="o",
            label=f"{method}_line",
            color=color_map[method],
        )[0]
        handles_for_legend.append((bars, line, method))

    group_center = x_index + (total_methods * bar_width) / 2
    ax_left.set_xticks(group_center)
    ax_left.set_xticklabels([str(x) for x in sorted_x])

    ax_left.set_ylabel("%SR", fontsize=12)
    ax_right.set_ylabel("#TS", fontsize=12)

    custom_handles = []
    custom_labels = []
    for bars, line, method in handles_for_legend:
        custom_handles.append((bars, line))
        custom_labels.append(method)

    ax_left.legend(
        custom_handles,
        custom_labels,
        handler_map={tuple: HandlerTuple(ndivide=None)},
        loc="upper center",
        bbox_to_anchor=(0.5, 1.15),
        ncol=min(len(methods), 4),
        fontsize=10,
    )

    ax_left.set_title(title, fontsize=14)
    ax_left.set_ylim(left_low, left_max)
    ax_right.set_ylim(right_low, right_max)
    ax_right.invert_yaxis()

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(save_path, dpi=300)
    plt.close(fig)


def main():
    output_dir = os.path.dirname(os.path.abspath(__file__))
    figure_specs = [
        ("initial_team_size", "Initial Team Size", 0.9, 0.4, 2000, 600, "supp_figure_17_a.png"),
        ("missed_num", "Missed Object Num", 0.95, 0.4, 2000, 600, "supp_figure_17_b.png"),
        ("trapped_num", "Trapped Object Num", 0.95, 0.3, 2000, 600, "supp_figure_17_c.png"),
    ]

    for key, title, left_max, left_low, right_max, right_low, filename in figure_specs:
        save_path = os.path.join(output_dir, filename)
        plot_two_metrics_adjusted(
            data_dict=PLOTTING_DATA[key],
            color_map=COLOR_MAP,
            title=title,
            left_max=left_max,
            left_low=left_low,
            right_max=right_max,
            right_low=right_low,
            save_path=save_path,
        )
        print(f"Saved: {save_path}")


if __name__ == "__main__":
    main()
