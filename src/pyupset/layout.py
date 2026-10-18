"""Horizontal UpSet layout matching the lab2 reference."""

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .config import PlotConfiguration


def create_layout(
    config: PlotConfiguration, n_sets: int, n_intersections: int
) -> tuple[Figure, dict[str, Axes]]:
    figsize = config.figsize or (
        max(9.0, min(24.0, 6.0 + 0.65 * n_sets)),
        max(6.5, min(24.0, 3.7 + 0.42 * n_intersections)),
    )
    fig = plt.figure(figsize=figsize)
    grid = fig.add_gridspec(
        2,
        2,
        width_ratios=[max(2.6, 0.55 * n_sets), 3.7],
        height_ratios=[1.8, max(1.8, 0.42 * n_intersections)],
        wspace=config.wspace,
        hspace=config.hspace,
        left=0.13,
        right=0.96,
        bottom=0.20,
        top=0.87,
    )
    sets = fig.add_subplot(grid[0, 0])
    matrix = fig.add_subplot(grid[1, 0], sharex=sets)
    intersections = fig.add_subplot(grid[1, 1], sharey=matrix)
    return fig, {"matrix": matrix, "intersections": intersections, "sets": sets}
