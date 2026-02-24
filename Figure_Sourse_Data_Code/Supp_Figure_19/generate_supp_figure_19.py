import matplotlib
matplotlib.use("Agg")

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from cycler import cycler


def filter_turning_points(data: pd.DataFrame) -> pd.DataFrame:
    return data[(data["member_count"].diff() != 0) | (data["member_count"].diff(-1) != 0)]


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    data_original = {
        "0": {"member_count": 2},
        "54": {"member_count": 2},
        "134": {"member_count": 2},
        "217": {"member_count": 3},
        "317": {"member_count": 3},
        "342": {"member_count": 2},
        "470": {"member_count": 2},
        "529": {"member_count": 3},
        "611": {"member_count": 3},
        "623": {"member_count": 1},
        "639": {"member_count": 1},
    }
    data_additional = {
        "0": {"member_count": 2},
        "83": {"member_count": 2},
        "164": {"member_count": 4},
        "264": {"member_count": 4},
        "395": {"member_count": 4},
        "535": {"member_count": 4},
        "622": {"member_count": 4},
        "661": {"member_count": 4},
        "735": {"member_count": 3},
        "751": {"member_count": 3},
    }
    data_more = {
        "0": {"member_count": 6},
        "92": {"member_count": 6},
        "187": {"member_count": 6},
        "306": {"member_count": 6},
        "406": {"member_count": 6},
        "503": {"member_count": 6},
        "631": {"member_count": 6},
        "751": {"member_count": 6},
        "816": {"member_count": 6},
        "868": {"member_count": 6},
        "931": {"member_count": 6},
        "947": {"member_count": 6},
    }
    data_corrected_latest = {
        "0": {"member_count": 2},
        "83": {"member_count": 3},
        "180": {"member_count": 6},
        "267": {"member_count": 6},
        "395": {"member_count": 5},
        "495": {"member_count": 4},
        "590": {"member_count": 4},
        "662": {"member_count": 4},
        "667": {"member_count": 4},
        "672": {"member_count": 4},
        "677": {"member_count": 4},
        "682": {"member_count": 4},
        "687": {"member_count": 4},
        "692": {"member_count": 4},
        "697": {"member_count": 4},
        "702": {"member_count": 4},
        "707": {"member_count": 4},
        "712": {"member_count": 4},
        "717": {"member_count": 4},
        "722": {"member_count": 4},
        "727": {"member_count": 4},
        "732": {"member_count": 4},
        "737": {"member_count": 5},
        "742": {"member_count": 6},
        "747": {"member_count": 6},
        "752": {"member_count": 6},
        "792": {"member_count": 6},
        "797": {"member_count": 6},
        "802": {"member_count": 6},
        "807": {"member_count": 6},
        "812": {"member_count": 6},
        "817": {"member_count": 6},
        "822": {"member_count": 6},
        "827": {"member_count": 6},
        "832": {"member_count": 6},
        "863": {"member_count": 5},
        "955": {"member_count": 5},
        "1067": {"member_count": 4},
    }

    df_original = pd.DataFrame.from_dict(data_original, orient="index")
    df_additional = pd.DataFrame.from_dict(data_additional, orient="index")
    df_more = pd.DataFrame.from_dict(data_more, orient="index")
    df_corrected_latest = pd.DataFrame.from_dict(data_corrected_latest, orient="index")

    df_original.index = df_original.index.astype(int)
    df_additional.index = df_additional.index.astype(int)
    df_more.index = df_more.index.astype(int)
    df_corrected_latest.index = df_corrected_latest.index.astype(int)

    turning_points_original = filter_turning_points(df_original).sort_index()
    turning_points_additional = filter_turning_points(df_additional).sort_index()
    turning_points_more = filter_turning_points(df_more).sort_index()
    turning_points_corrected_latest = filter_turning_points(df_corrected_latest).sort_index()

    plt.rcParams["axes.prop_cycle"] = cycler(color=["#D62728", "#FF1493", "#1F77B4", "#17BECF"])
    plt.figure(figsize=(10, 5))

    plt.step(
        turning_points_original.index,
        turning_points_original["member_count"],
        where="post",
        markersize=6,
        label="Proactive-OURS",
        linestyle="--",
        linewidth=3,
    )
    plt.step(
        turning_points_additional.index,
        turning_points_additional["member_count"],
        where="post",
        markersize=6,
        label="Proactive-OURS(Saperate)",
        linestyle="-.",
        linewidth=3,
        alpha=0.6,
    )
    plt.step(
        turning_points_more.index,
        turning_points_more["member_count"],
        where="post",
        markersize=6,
        label="All-in-OURS(Action)",
        linestyle="-.",
        linewidth=3,
        alpha=0.6,
    )
    plt.step(
        turning_points_corrected_latest.index,
        turning_points_corrected_latest["member_count"],
        where="post",
        markersize=6,
        label="Proactive-EMOS",
        linestyle="--",
        linewidth=3,
        alpha=0.6,
    )

    last_points = [
        (turning_points_original.index[-1], turning_points_original.iloc[-1]["member_count"]),
        (turning_points_additional.index[-1], turning_points_additional.iloc[-1]["member_count"]),
        (turning_points_more.index[-1], turning_points_more.iloc[-1]["member_count"]),
        (
            turning_points_corrected_latest.index[-1],
            turning_points_corrected_latest.iloc[-1]["member_count"],
        ),
    ]
    for x_last, y_last in last_points:
        plt.scatter(x_last, y_last, color="black", s=50, marker="^", zorder=5)

    plt.scatter([], [], color="black", s=50, label="Task Complete", marker="^", zorder=5)
    plt.title("Working Team Member Count", fontsize=16)
    plt.xlabel("Temporal Step", fontsize=14)
    plt.ylabel("Member Count", fontsize=14)

    x_ticks = range(
        0,
        max(
            turning_points_original.index.max(),
            turning_points_additional.index.max(),
            turning_points_more.index.max(),
            turning_points_corrected_latest.index.max(),
        )
        + 1,
        100,
    )
    plt.xlim(0)
    plt.xticks(x_ticks, fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.legend(fontsize=10, loc="best")
    plt.tight_layout()
    png_path = out_dir / "supp_figure_19.png"
    pdf_path = out_dir / "supp_figure_19.pdf"
    plt.savefig(png_path, dpi=300)
    plt.savefig(pdf_path)
    print(f"Saved: {png_path}")
    print(f"Saved: {pdf_path}")


if __name__ == "__main__":
    main()
