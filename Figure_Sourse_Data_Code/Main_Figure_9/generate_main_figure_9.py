from pathlib import Path

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.family"] = "Arial"
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 11

FONT_SIZE_TITLE = 14
FONT_SIZE_LABEL = 12
FONT_SIZE_TICK = 11
FONT_SIZE_ANNOTATION = 8
FONT_SIZE_LEGEND = 10
FONT_SIZE_SUBPLOT_LABEL = 20

COLOR_SR = "#E04A4A"
COLOR_PS = "#F5A938"
COLOR_TS = "#9585C9"
COLOR_AS = "#5BA5ED"

COLOR_RADAR_1 = "#ADADAD"
COLOR_RADAR_2 = COLOR_TS
COLOR_RADAR_3 = COLOR_SR
colors_radar = [COLOR_RADAR_1, COLOR_RADAR_2, COLOR_RADAR_3]

COLOR_HIGHLIGHT = "#E8F4E8"

methods = ["baseline1", "baseline2", "baseline3", "Ours"]

data_fixed = {
    "SR": [0.97, 25.55, 28.75, 48.05],
    "PS": [11.85, 55.37, 58.03, 70.45],
    "TS": [1467.49, 1198.97, 1110.92, 924.18],
    "AS": [5137.86, 3939.63, 3479.88, 2473.87],
}

data_responsive = {
    "SR": [3.19, 27.78, 36.94, 56.11],
    "PS": [19.11, 59.62, 64.10, 79.59],
    "TS": [1463.62, 1171.33, 1040.77, 851.07],
    "AS": [6342.63, 5426.06, 4456.87, 2995.72],
}

data_proactive = {
    "SR": [3.33, 29.31, 37.92, 70.28],
    "PS": [23.53, 59.18, 65.61, 85.71],
    "TS": [1459.24, 1123.27, 1033.18, 780.33],
    "AS": [7439.34, 5806.01, 5123.83, 2335.26],
}

paradigms = ["Fixed", "Responsive", "Proactive"]
all_data = [data_fixed, data_responsive, data_proactive]

improvement = {
    "SR": [(p - r) / r * 100 if r != 0 else 0 for p, r in zip(data_proactive["SR"], data_responsive["SR"])],
    "PS": [(p - r) / r * 100 if r != 0 else 0 for p, r in zip(data_proactive["PS"], data_responsive["PS"])],
    "TS": [(r - p) / r * 100 for r, p in zip(data_responsive["TS"], data_proactive["TS"])],
    "AS": [(r - p) / r * 100 for r, p in zip(data_responsive["AS"], data_proactive["AS"])],
}

comm_methods = ["Round-Robin Broadcast", "Round-Robin Selective", "Ours"]
comm_data = {
    "Round-Robin Broadcast": {"SR": 55.28, "PS": 76.71, "TS": 1001.40, "AS": 2712.42},
    "Round-Robin Selective": {"SR": 59.03, "PS": 78.61, "TS": 936.31, "AS": 2457.78},
    "Ours": {"SR": 70.28, "PS": 85.71, "TS": 780.33, "AS": 2335.26},
}

fig = plt.figure(figsize=(18, 11))
gs = gridspec.GridSpec(
    2,
    3,
    figure=fig,
    height_ratios=[0.85, 0.95],
    width_ratios=[1, 1, 1],
    hspace=0.20,
    wspace=0.25,
)

axes_a = [fig.add_subplot(gs[0, i]) for i in range(3)]
x = np.arange(len(methods))
width = 0.35

for idx, (ax1, data, paradigm) in enumerate(zip(axes_a, all_data, paradigms)):
    bars1 = ax1.bar(
        x - width / 2,
        data["SR"],
        width,
        label="%SR",
        color=COLOR_SR,
        edgecolor="white",
        linewidth=0.5,
    )
    bars2 = ax1.bar(
        x + width / 2,
        data["PS"],
        width,
        label="%PS",
        color=COLOR_PS,
        edgecolor="white",
        linewidth=0.5,
    )

    if idx == 0:
        ax1.set_ylabel("%SR / %PS (↑)", fontsize=FONT_SIZE_LABEL, color="#444444")
    ax1.set_xticks(x)
    ax1.set_xticklabels(methods, fontsize=FONT_SIZE_TICK, rotation=15)
    ax1.tick_params(axis="y", labelcolor="#444444", labelsize=FONT_SIZE_TICK)
    ax1.set_ylim(0, 105)

    for bar in bars1:
        height = bar.get_height()
        ax1.annotate(
            f"{height:.1f}",
            xy=(bar.get_x() + bar.get_width() / 4, height),
            xytext=(0, 2),
            textcoords="offset points",
            ha="left",
            va="bottom",
            fontsize=FONT_SIZE_ANNOTATION,
            color=COLOR_SR,
            rotation=45,
        )

    for bar in bars2:
        height = bar.get_height()
        ax1.annotate(
            f"{height:.1f}",
            xy=(bar.get_x() + bar.get_width() / 4, height),
            xytext=(0, 2),
            textcoords="offset points",
            ha="left",
            va="bottom",
            fontsize=FONT_SIZE_ANNOTATION,
            color=COLOR_PS,
            rotation=45,
        )

    ax2 = ax1.twinx()
    ax2.plot(
        x,
        data["TS"],
        "o-",
        color=COLOR_TS,
        linewidth=2,
        markersize=6,
        label="#TS",
        markerfacecolor="white",
        markeredgewidth=1.5,
    )
    ax2.plot(
        x,
        data["AS"],
        "s-",
        color=COLOR_AS,
        linewidth=2,
        markersize=6,
        label="#AS",
        markerfacecolor="white",
        markeredgewidth=1.5,
    )

    if idx == 2:
        ax2.set_ylabel("#TS / #AS (↓)", fontsize=FONT_SIZE_LABEL, color="#444444")
    ax2.tick_params(axis="y", labelcolor="#444444", labelsize=FONT_SIZE_TICK)
    ax2.set_ylim(16000, 0)

    for i, (ts, as_val) in enumerate(zip(data["TS"], data["AS"])):
        ax2.annotate(
            f"{ts:.0f}",
            xy=(i, ts),
            xytext=(0, -8),
            textcoords="offset points",
            ha="center",
            va="top",
            fontsize=FONT_SIZE_ANNOTATION,
            color=COLOR_TS,
        )
        ax2.annotate(
            f"{as_val:.0f}",
            xy=(i, as_val),
            xytext=(-8, 0),
            textcoords="offset points",
            ha="right",
            va="center",
            fontsize=FONT_SIZE_ANNOTATION,
            color=COLOR_AS,
        )

    ax1.set_title(f"{paradigm} Paradigm", fontsize=FONT_SIZE_TITLE, pad=10)
    ax1.yaxis.grid(True, linestyle="--", alpha=0.4, color="#CCCCCC")
    ax1.set_axisbelow(True)
    ax1.axvspan(2.5, 3.5, alpha=0.10, color=COLOR_HIGHLIGHT)

handles_a = [
    plt.Rectangle((0, 0), 1, 1, color=COLOR_SR, label="%SR"),
    plt.Rectangle((0, 0), 1, 1, color=COLOR_PS, label="%PS"),
    plt.Line2D(
        [0],
        [0],
        color=COLOR_TS,
        marker="o",
        markersize=6,
        markerfacecolor="white",
        markeredgewidth=1.5,
        label="#TS",
    ),
    plt.Line2D(
        [0],
        [0],
        color=COLOR_AS,
        marker="s",
        markersize=6,
        markerfacecolor="white",
        markeredgewidth=1.5,
        label="#AS",
    ),
]
fig.legend(
    handles=handles_a,
    labels=["%SR ↑", "%PS ↑", "#TS ↓", "#AS ↓"],
    loc="upper center",
    ncol=4,
    fontsize=FONT_SIZE_LEGEND,
    framealpha=0.9,
    bbox_to_anchor=(0.5, 0.935),
)
fig.text(0.08, 0.90, "a", fontsize=FONT_SIZE_SUBPLOT_LABEL, fontweight="bold", va="top")

ax_b = fig.add_subplot(gs[1, 0:2])
x_b = np.arange(len(methods))
width_b = 0.18

bars_sr = ax_b.bar(
    x_b - 1.5 * width_b,
    improvement["SR"],
    width_b,
    label="%SR ↑",
    color=COLOR_SR,
    edgecolor="white",
    linewidth=0.5,
)
bars_ps = ax_b.bar(
    x_b - 0.5 * width_b,
    improvement["PS"],
    width_b,
    label="%PS ↑",
    color=COLOR_PS,
    edgecolor="white",
    linewidth=0.5,
)
bars_ts = ax_b.bar(
    x_b + 0.5 * width_b,
    improvement["TS"],
    width_b,
    label="#TS ↓",
    color=COLOR_TS,
    edgecolor="white",
    linewidth=0.5,
)
bars_as = ax_b.bar(
    x_b + 1.5 * width_b,
    improvement["AS"],
    width_b,
    label="#AS ↓",
    color=COLOR_AS,
    edgecolor="white",
    linewidth=0.5,
)


def add_labels(bars, color, ax):
    for bar in bars:
        height = bar.get_height()
        va = "bottom" if height >= 0 else "top"
        offset = 1 if height >= 0 else -1
        ax.annotate(
            f"{height:.1f}%",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, offset * 3),
            textcoords="offset points",
            ha="center",
            va=va,
            fontsize=FONT_SIZE_ANNOTATION,
            color=color,
            rotation=45,
        )


add_labels(bars_sr, COLOR_SR, ax_b)
add_labels(bars_ps, COLOR_PS, ax_b)
add_labels(bars_ts, COLOR_TS, ax_b)
add_labels(bars_as, COLOR_AS, ax_b)

ax_b.axhline(y=0, color="#333333", linestyle="-", linewidth=0.8)
ax_b.set_ylabel("Improvement Rate (%)", fontsize=FONT_SIZE_LABEL)
ax_b.set_xticks(x_b)
ax_b.set_xticklabels(methods, fontsize=FONT_SIZE_TICK)
ax_b.tick_params(axis="y", labelsize=FONT_SIZE_TICK)
leg_b = ax_b.legend(
    loc="upper center",
    bbox_to_anchor=(0.5, 1.00),
    ncol=4,
    fontsize=FONT_SIZE_LEGEND,
    framealpha=0.9,
    title="Improvement: Responsive to Proactive (positive = better)",
)
leg_b.get_title().set_fontsize(FONT_SIZE_TITLE - 1)
ax_b.yaxis.grid(True, linestyle="--", alpha=0.4, color="#CCCCCC")
ax_b.set_axisbelow(True)
ax_b.axvspan(2.55, 3.45, alpha=0.10, color=COLOR_HIGHLIGHT)

y_min = min(
    min(improvement["SR"]),
    min(improvement["PS"]),
    min(improvement["TS"]),
    min(improvement["AS"]),
)
y_max = max(
    max(improvement["SR"]),
    max(improvement["PS"]),
    max(improvement["TS"]),
    max(improvement["AS"]),
)
ax_b.set_ylim(y_min - 5, y_max + 5)
ax_b.set_xlim(-0.5, len(methods) - 0.5)

fig.text(0.08, 0.48, "b", fontsize=FONT_SIZE_SUBPLOT_LABEL, fontweight="bold", va="top")

ax_c = fig.add_subplot(gs[1, 2], polar=True)
pos = ax_c.get_position()
ax_c.set_position([pos.x0, pos.y0 - 0.02, pos.width, pos.height])


def normalize_data(raw_values, methods_seq, directions):
    normalized = {m: [] for m in methods_seq}
    min_norm, max_norm = 0.35, 0.95

    for i in range(len(directions)):
        values = [raw_values[m][i] for m in methods_seq]
        min_val, max_val = min(values), max(values)

        for m in methods_seq:
            val = raw_values[m][i]
            if max_val == min_val:
                norm_val = max_norm
            else:
                ratio = (val - min_val) / (max_val - min_val)
                if not directions[i]:
                    ratio = 1 - ratio
                norm_val = min_norm + ratio * (max_norm - min_norm)
            normalized[m].append(norm_val)
    return normalized


metrics_radar = ["SR (%↑)", "PS (%↑)", "TS (↓)", "AS (↓)"]
directions = [True, True, False, False]
raw_values = {
    m: [comm_data[m]["SR"], comm_data[m]["PS"], comm_data[m]["TS"], comm_data[m]["AS"]]
    for m in comm_methods
}
normalized = normalize_data(raw_values, comm_methods, directions)

num_vars = len(metrics_radar)
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
angles += angles[:1]

alphas = [0.10, 0.12, 0.20]
linewidths = [1.8, 1.8, 2.5]
linestyles = ["--", "-.", "-"]
markers = ["s", "^", "o"]

for idx, method in enumerate(comm_methods):
    values = normalized[method].copy()
    values += values[:1]

    label = "Autonomous Need-Driven (Ours)" if method == "Ours" else method
    ax_c.plot(
        angles,
        values,
        marker=markers[idx],
        linewidth=linewidths[idx],
        label=label,
        color=colors_radar[idx],
        linestyle=linestyles[idx],
        markersize=8 if method == "Ours" else 6,
    )
    ax_c.fill(angles, values, alpha=alphas[idx], color=colors_radar[idx])

ax_c.set_xticks(angles[:-1])
ax_c.set_xticklabels([])

label_positions = {
    "SR (%↑)": (angles[0], 1.23, "center"),
    "PS (%↑)": (angles[1], 1.17, "center"),
    "TS (↓)": (angles[2], 1.17, "center"),
    "AS (↓)": (angles[3], 1.14, "center"),
}
for label, (angle, radius, ha_align) in label_positions.items():
    ax_c.text(
        angle,
        radius,
        label,
        size=FONT_SIZE_TICK,
        ha=ha_align,
        va="center",
        fontweight="normal",
    )

ax_c.set_ylim(0, 1.05)
ax_c.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
ax_c.set_yticklabels(["20%", "40%", "60%", "80%", "100%"], size=FONT_SIZE_ANNOTATION, color="#777777")
leg_c = ax_c.legend(
    loc="upper right",
    bbox_to_anchor=(1.25, 1.10),
    fontsize=FONT_SIZE_ANNOTATION + 1,
    frameon=True,
    fancybox=True,
    shadow=False,
    edgecolor="#CCCCCC",
    title="Communication (outer = better)",
)
leg_c.get_title().set_fontsize(FONT_SIZE_TITLE - 2)


def add_radar_annotations(ax, angle_seq, data, normed, methods_seq, colors):
    position_config = {
        0: [
            (0.20, 0.0, "left", "center"),
            (0.10, -0.05, "left", "center"),
            (-0.10, 0.05, "right", "center"),
        ],
        1: [
            (-0.20, 0.0, "right", "center"),
            (0.20, 0.0, "left", "center"),
            (0.0, 0.06, "center", "bottom"),
        ],
        2: [
            (-0.20, 0.0, "right", "center"),
            (-0.10, -0.05, "right", "center"),
            (0.10, 0.05, "left", "center"),
        ],
        3: [
            (-0.20, 0.0, "right", "center"),
            (0.02, -0.01, "left", "top"),
            (0.0, 0.07, "center", "bottom"),
        ],
    }

    for idx, method in enumerate(methods_seq):
        raw_vals = [data[method]["SR"], data[method]["PS"], data[method]["TS"], data[method]["AS"]]
        norm_vals = normed[method]
        color = colors[idx]

        for i, (angle, raw_val, norm_val) in enumerate(zip(angle_seq[:-1], raw_vals, norm_vals)):
            text = f"{raw_val:.1f}" if i < 2 else f"{int(raw_val)}"
            angle_off, r_off, ha, va = position_config[i][idx]
            r_pos = norm_val + r_off
            angle_pos = angle + angle_off
            fontsize = FONT_SIZE_ANNOTATION + 1 if method == "Ours" else FONT_SIZE_ANNOTATION
            fontweight = "bold" if method == "Ours" else "normal"

            ax.annotate(
                text,
                xy=(angle_pos, r_pos),
                fontsize=fontsize,
                fontweight=fontweight,
                color=color,
                ha=ha,
                va=va,
                bbox=dict(
                    boxstyle="round,pad=0.12",
                    facecolor="white",
                    edgecolor=color,
                    alpha=0.88,
                    linewidth=0.5,
                ),
            )


add_radar_annotations(ax_c, angles, comm_data, normalized, comm_methods, colors_radar)
fig.text(0.67, 0.48, "c", fontsize=FONT_SIZE_SUBPLOT_LABEL, fontweight="bold", va="top")

out_dir = Path(__file__).resolve().parent
png_path = out_dir / "main_figure_9.png"
pdf_path = out_dir / "main_figure_9.pdf"

plt.savefig(png_path, dpi=200, bbox_inches="tight", facecolor="white", edgecolor="none")
plt.savefig(pdf_path, bbox_inches="tight", facecolor="white", edgecolor="none")
plt.close(fig)

print(f"Saved: {png_path}")
print(f"Saved: {pdf_path}")
