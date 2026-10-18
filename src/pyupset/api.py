"""Public stateless API."""

from typing import Any

import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .config import PlotConfiguration
from .core import compute
from .rendering import render
from .validation import validate


def plot(
    data: pd.DataFrame,
    sets: list[str] | None = None,
    sort_by: str = "degree",
    **kwargs: Any,
) -> tuple[Figure, dict[str, Axes]]:
    """Plot observed exclusive intersections of binary DataFrame columns.

    ``degree`` orders intersections by ascending number of sets; ``size``
    orders them by descending count. Ties use lexicographic binary membership
    in the supplied set order. The all-false combination is included if observed.

    Optional style keys: colors (one color or a dict with matrix/intersections/
    sets keys), figsize, marker_size, line_width, wspace, hspace, font_size.
    Without figsize, the figure size adapts to the number of sets/intersections.
    Colors default to a blue scale by degree with gray inactive matrix dots.
    With sets=None, numeric/boolean binary columns are detected automatically.
    NaN/NA in explicitly selected columns raises ValueError. The input is never
    modified. Empty input produces a figure containing "No data to plot".
    """
    try:
        config = PlotConfiguration.from_kwargs(kwargs)
        validated = validate(data, sets)
        result = compute(validated, sort_by)
        return render(result, config)
    except MemoryError as exc:
        raise MemoryError(
            "Not enough memory to compute or render the UpSet plot"
        ) from exc
