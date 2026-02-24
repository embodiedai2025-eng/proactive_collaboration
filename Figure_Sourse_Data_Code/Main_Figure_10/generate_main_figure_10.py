from pathlib import Path

import plotly.graph_objects as go


BASE_DIR = Path(__file__).resolve().parent

UNIFIED_COLORS = {
    "Capability Deficit": "#D32F2F",
    "Coordination Breakdown": "#F57C00",
    "Reasoning Error": "#FFC107",
    "Success": "#86CFA5",
}


FIG_10A_WIDTH = 2450
FIG_10A_HEIGHT = int(FIG_10A_WIDTH * 6 / 44)

PARADIGMS = ["Fixed", "Responsive", "Proactive"]
CAPABILITY_DEFICIT = [9, 2, 0]
COORDINATION_BREAKDOWN = [1, 5, 1]
REASONING_ERROR = [1, 2, 1]
SUCCESS = [9, 11, 18]


def make_figure_10a() -> None:
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=PARADIGMS,
            x=CAPABILITY_DEFICIT,
            name="Capability<br>Deficit",
            orientation="h",
            marker_color=UNIFIED_COLORS["Capability Deficit"],
            legendgroup="bar",
        )
    )
    fig.add_trace(
        go.Bar(
            y=PARADIGMS,
            x=COORDINATION_BREAKDOWN,
            name="Coordination<br>Breakdown",
            orientation="h",
            marker_color=UNIFIED_COLORS["Coordination Breakdown"],
            legendgroup="bar",
        )
    )
    fig.add_trace(
        go.Bar(
            y=PARADIGMS,
            x=REASONING_ERROR,
            name="Reasoning<br>Error",
            orientation="h",
            marker_color=UNIFIED_COLORS["Reasoning Error"],
            legendgroup="bar",
        )
    )
    fig.add_trace(
        go.Bar(
            y=PARADIGMS,
            x=SUCCESS,
            name="Success",
            orientation="h",
            marker_color=UNIFIED_COLORS["Success"],
            legendgroup="bar",
        )
    )

    fig.update_layout(
        barmode="stack",
        bargap=0.55,
        xaxis=dict(
            domain=[0, 1],
            range=[0, 22],
            dtick=2,
            title_text="Number of Episodes",
            title_font=dict(size=24, color="black"),
            showgrid=True,
            gridcolor="rgba(0,0,0,0.15)",
            zeroline=False,
        ),
        yaxis=dict(
            domain=[0, 1],
            categoryorder="array",
            categoryarray=["Proactive", "Responsive", "Fixed"],
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=24, family="Arial Black"),
        ),
        font=dict(family="Arial", size=24),
        width=FIG_10A_WIDTH,
        height=FIG_10A_HEIGHT,
        margin=dict(l=15, r=12, t=20, b=28),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=True,
        legend=dict(
            orientation="v",
            x=1,
            y=1,
            xanchor="right",
            yanchor="top",
            bgcolor="rgba(255,255,255,0.9)",
            font=dict(size=24),
            tracegroupgap=12,
            itemwidth=40,
            itemsizing="constant",
        ),
    )
    fig.update_xaxes(showticklabels=True)
    fig.update_yaxes(showticklabels=True)

    fig.write_image(
        str(BASE_DIR / "main_figure_10_a.pdf"),
        width=FIG_10A_WIDTH,
        height=FIG_10A_HEIGHT,
        scale=1,
    )
    fig.write_image(
        str(BASE_DIR / "main_figure_10_a.png"),
        width=FIG_10A_WIDTH,
        height=FIG_10A_HEIGHT,
        scale=1,
    )


COLORS = {
    "root": "#e0e0e0",
    "Success": UNIFIED_COLORS["Success"],
    "Failure": "#8B0000",
    "Capability Deficit": UNIFIED_COLORS["Capability Deficit"],
    "Coordination Breakdown": UNIFIED_COLORS["Coordination Breakdown"],
    "Reasoning Error": UNIFIED_COLORS["Reasoning Error"],
    "Consensus Misalignment": "#e1bee7",
    "Deadlock": "#9e9e9e",
    "Action Sync Failure": "#90caf9",
    "Semantic Misjudgment": "#b3e5fc",
    "Context Loss": "#64b5f6",
    "Reflection Error": "#ffcc80",
    "Fabrication": "#a5d6a7",
}

FIXED = {
    "total": 374 + 346,
    "failure": 374,
    "success": 346,
    "cap_def": 127,
    "coord_break": 221,
    "reasoning": 26,
    "consensus": 95,
    "deadlock": 109,
    "joint_sync": 17,
    "semantic": 3,
    "context_loss": 12,
    "reflection": 8,
    "affordance": 3,
}

RESPONSIVE = {
    "total": 316 + 404,
    "failure": 316,
    "success": 404,
    "cap_def": 49,
    "coord_break": 235,
    "reasoning": 32,
    "consensus": 149,
    "deadlock": 59,
    "joint_sync": 27,
    "semantic": 2,
    "context_loss": 12,
    "reflection": 16,
    "affordance": 2,
}

PROACTIVE = {
    "total": 214 + 506,
    "failure": 214,
    "success": 506,
    "cap_def": 38,
    "coord_break": 141,
    "reasoning": 35,
    "consensus": 78,
    "deadlock": 27,
    "joint_sync": 36,
    "semantic": 3,
    "context_loss": 16,
    "reflection": 15,
    "affordance": 1,
}


def _hex_to_rgba(hex_c: str, alpha: float = 0.65) -> str:
    hex_c = hex_c.lstrip("#")
    r, g, b = int(hex_c[0:2], 16), int(hex_c[2:4], 16), int(hex_c[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def build_sankey_data(mode_name: str, d: dict):
    nodes = [
        mode_name,
        "Failure",
        "Success",
        "Capability<br>Deficit",
        "Coordination<br>Breakdown",
        "Reasoning<br>Error",
        "Consensus<br>Misalignment",
        "Deadlock",
        "Action Sync<br>Failure",
        "Semantic<br>Misjudgment",
        "Context<br>Loss",
        "Reflection<br>Error",
        "Fabrication",
    ]
    node_colors = [
        COLORS["root"],
        COLORS["Failure"],
        COLORS["Success"],
        COLORS["Capability Deficit"],
        COLORS["Coordination Breakdown"],
        COLORS["Reasoning Error"],
        COLORS["Consensus Misalignment"],
        COLORS["Deadlock"],
        COLORS["Action Sync Failure"],
        COLORS["Semantic Misjudgment"],
        COLORS["Context Loss"],
        COLORS["Reflection Error"],
        COLORS["Fabrication"],
    ]

    links = [
        (0, 1, d["failure"]),
        (0, 2, d["success"]),
        (1, 3, d["cap_def"]),
        (1, 4, d["coord_break"]),
        (1, 5, d["reasoning"]),
        (4, 6, d["consensus"]),
        (4, 7, d["deadlock"]),
        (4, 8, d["joint_sync"]),
        (5, 9, d["semantic"]),
        (5, 10, d["context_loss"]),
        (5, 11, d["reflection"]),
        (5, 12, d["affordance"]),
    ]
    source = [i[0] for i in links]
    target = [i[1] for i in links]
    value = [i[2] for i in links]
    link_colors = [_hex_to_rgba(node_colors[t]) for t in target]

    node_x = [0.0, 0.18, 0.18, 0.42, 0.42, 0.42, 0.92, 0.92, 0.92, 0.92, 0.92, 0.92, 0.92]
    node_y = [0.5, 0.75, 0.25, 0.90, 0.5, 0.10, 0.90, 0.75, 0.60, 0.45, 0.32, 0.20, 0.06]

    node_dict = dict(
        label=[""] * len(nodes),
        x=node_x,
        y=node_y,
        customdata=node_colors,
        pad=20,
        thickness=16,
        line=dict(width=0.5, color="rgba(0,0,0,0.2)"),
        color=node_colors,
    )
    link_dict = dict(source=source, target=target, value=value, color=link_colors)
    return node_dict, link_dict, nodes, node_x, node_y


def make_figure_10b() -> None:
    fig = go.Figure()
    annotations = []
    configs = [
        ("Fixed", FIXED, 0.0, 0.334),
        ("Responsive", RESPONSIVE, 0.333, 0.667),
        ("Proactive", PROACTIVE, 0.666, 1.0),
    ]

    for mode_name, data, x_min, x_max in configs:
        node_dict, link_dict, nodes, node_x, node_y = build_sankey_data(mode_name, data)
        fig.add_trace(
            go.Sankey(
                domain=dict(x=[x_min, x_max], y=[0, 1]),
                node=node_dict,
                link=link_dict,
                arrangement="fixed",
                valueformat="d",
                valuesuffix="",
            )
        )
        for i in range(1, len(nodes)):
            x_paper = x_min + (node_x[i] - 0.02) * (x_max - x_min)
            y_paper = 1.0 - node_y[i]
            annotations.append(
                dict(
                    x=x_paper,
                    y=y_paper,
                    xref="paper",
                    yref="paper",
                    xanchor="right",
                    yanchor="middle",
                    text=nodes[i],
                    showarrow=False,
                    font=dict(family="Arial", size=24),
                    bgcolor="rgba(255,255,255,0.65)",
                    borderpad=3,
                )
            )
        annotations.append(
            dict(
                x=(x_min + x_max) / 2,
                y=0.02,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text=f"<b>{mode_name}</b>",
                showarrow=False,
                font=dict(family="Arial", size=24),
            )
        )

    fig_w, fig_h = 2450, 700
    fig.update_layout(
        title=None,
        font=dict(family="Arial", size=24),
        width=fig_w,
        height=fig_h,
        margin=dict(l=15, r=12, t=20, b=28),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        annotations=annotations,
    )
    fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
    fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False)

    fig.write_image(str(BASE_DIR / "main_figure_10_b.pdf"), width=fig_w, height=fig_h, scale=1)
    fig.write_image(str(BASE_DIR / "main_figure_10_b.png"), width=fig_w, height=fig_h, scale=1)


def main() -> None:
    make_figure_10a()
    make_figure_10b()
    print("Done. Generated main_figure_10_a/main_figure_10_b into:", BASE_DIR)


if __name__ == "__main__":
    main()
