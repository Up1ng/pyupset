"""Render a horizontal UpSet using public matplotlib APIs."""

import numpy as np
from numpy.typing import ArrayLike, NDArray
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator, PercentFormatter

from .config import PlotConfiguration
from .layout import create_layout
from .models import IntersectionMatrix

# The reference uses a sequential blue palette for intersection degree.
DEGREE_COLORS = ("#4a9bf2", "#2276dc", "#1558b0", "#0f4183", "#0a2a55")


def render(
    data: IntersectionMatrix, config: PlotConfiguration
) -> tuple[Figure, dict[str, Axes]]:
    fig, axes = create_layout(config, len(data.sets), len(data.sizes))
    try:
        matrix, intersections, sets = (
            axes["matrix"],
            axes["intersections"],
            axes["sets"],
        )
        if not data.sizes.size:
            for ax in axes.values():
                ax.set_axis_off()
            fig.text(0.5, 0.5, "No data to plot", ha="center", va="center")
            return fig, axes

        ink = plt.rcParams["text.color"]
        muted, grid = "#8a97a0", "#e8ebed"
        xs, ys = np.arange(len(data.sets)), np.arange(len(data.sizes))
        degrees = data.membership.sum(axis=1)

        def degree_color(degree: int) -> str:
            return (
                DEGREE_COLORS[min(degree, len(DEGREE_COLORS)) - 1] if degree else muted
            )

        row_colors = [degree_color(int(d)) for d in degrees]
        dot_colors = config.colors["matrix"]
        bar_colors = config.colors["intersections"]
        # Keep marker diameter below the row/column pitch for dense diagrams.
        height = fig.get_figheight() * 72 * matrix.get_position().height
        width = fig.get_figwidth() * 72 * matrix.get_position().width
        marker_size = min(
            config.marker_size, (0.65 * min(height / len(ys), width / len(xs))) ** 2
        )
        for row in ys[::2]:
            for ax in (matrix, intersections):
                ax.axhspan(row - 0.5, row + 0.5, color="#f4f6f7", zorder=0)
        for x in xs:
            matrix.axvline(float(x), color=grid, linewidth=0.8, zorder=0.5)
            sets.axvline(float(x), color=grid, linewidth=0.8, zorder=0.5)
        # Inactive cells stay visible as light gray dots, as in the lab reference.
        matrix.scatter(
            np.tile(xs, len(ys)),
            np.repeat(ys, len(xs)),
            s=marker_size,
            color="#e1e5e8",
            zorder=1,
        )
        rows, columns = np.nonzero(data.membership)
        matrix.scatter(
            columns,
            rows,
            s=marker_size,
            color=dot_colors or [row_colors[row] for row in rows],
            zorder=3,
        )
        active = data.membership.any(axis=1)
        low = data.membership.argmax(axis=1)
        high = len(data.sets) - 1 - data.membership[:, ::-1].argmax(axis=1)
        matrix.hlines(
            ys[active],
            low[active],
            high[active],
            colors=dot_colors or [row_colors[row] for row in ys[active]],
            linewidth=config.line_width,
            zorder=2,
        )
        matrix.set_xticks(
            xs, labels=data.sets, rotation=45, ha="right", rotation_mode="anchor"
        )
        matrix.set_yticks(ys, labels=[str(row + 1) for row in ys])
        matrix.set_xlim(-0.5, len(xs) - 0.5)
        matrix.set_ylim(len(ys) - 0.5, -0.5)
        matrix.set_ylabel("Set combinations", color=muted)
        matrix.tick_params(axis="x", pad=8)

        bars = intersections.barh(
            ys,
            data.sizes,
            height=0.62,
            color=bar_colors or row_colors,
            zorder=3,
        )
        intersections.set_xlim(0, float(max(data.sizes)) * 1.20)
        intersections.bar_label(bars, padding=5, fontsize=config.font_size, color=ink)
        intersections.set_xlabel("Intersection size", labelpad=8)
        intersections.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=4))
        intersections.grid(axis="x", color=grid, linewidth=0.8)
        intersections.tick_params(axis="y", left=False, labelleft=False)
        total = int(data.sizes.sum())

        def to_percent(values: ArrayLike) -> NDArray[np.float64]:
            return np.asarray(values, dtype=np.float64) / total * 100

        def to_count(values: ArrayLike) -> NDArray[np.float64]:
            return np.asarray(values, dtype=np.float64) * total / 100

        percent = intersections.secondary_xaxis(
            "top",
            functions=(to_percent, to_count),
        )
        percent.xaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=0))
        percent.xaxis.set_major_locator(MaxNLocator(nbins=4))
        percent.set_xlabel(
            "Share of all observations",
            color=muted,
            fontsize=config.font_size,
            labelpad=8,
        )
        percent.tick_params(length=0, labelsize=config.font_size, colors=muted)
        percent.spines["top"].set_visible(False)

        sets.bar(xs, data.set_sizes, width=0.55, color=config.colors["sets"], zorder=3)
        sets.set_ylabel("Set size", color=muted)
        sets.yaxis.set_major_locator(MaxNLocator(integer=True, nbins=4))
        sets.tick_params(axis="x", bottom=False, labelbottom=False)
        sets.grid(axis="y", color=grid, linewidth=0.8)
        sets.margins(y=0.14)
        for name, ax in axes.items():
            for side, spine in ax.spines.items():
                spine.set_visible(
                    (name == "sets" and side == "left")
                    or (name == "intersections" and side == "bottom")
                )
                spine.set_color(grid)
            ax.set_axisbelow(True)
            ax.xaxis.label.set_fontsize(config.font_size)
            ax.yaxis.label.set_fontsize(config.font_size)
            ax.tick_params(labelsize=config.font_size, length=0, colors=muted)
        matrix.tick_params(axis="x", colors=ink)
        # A figure legend uses the empty top-right cell without adding an Axes.
        if dot_colors is None or bar_colors is None:
            position = intersections.get_position()
            handles = [
                Line2D(
                    [],
                    [],
                    linestyle="",
                    marker="o",
                    markersize=8,
                    color=degree_color(int(d)),
                    label=f"{d} set" if d == 1 else f"{d} sets",
                )
                for d in sorted(set(degrees))
            ]
            fig.legend(
                handles=handles,
                title="Sets in combination",
                frameon=False,
                loc="upper left",
                bbox_to_anchor=(position.x0, 0.87),
                borderaxespad=0,
                fontsize=config.font_size,
                title_fontsize=config.font_size,
                labelcolor=ink,
            )
        return fig, axes
    except BaseException:
        plt.close(fig)
        raise
