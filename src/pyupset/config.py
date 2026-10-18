"""Per-call plot configuration and default style."""

from dataclasses import dataclass
from typing import Any
import math

from matplotlib.colors import is_color_like

DEFAULT_CONFIG: dict[str, Any] = {
    "colors": {"matrix": None, "intersections": None, "sets": "#8a97a0"},
    "figsize": None,
    "marker_size": 150.0,
    "line_width": 2.5,
    "wspace": 0.12,
    "hspace": 0.08,
    "font_size": 10.0,
}


@dataclass(frozen=True)
class PlotConfiguration:
    colors: dict[str, Any]
    figsize: tuple[float, float] | None
    marker_size: float
    line_width: float
    wspace: float
    hspace: float
    font_size: float

    @classmethod
    def from_kwargs(cls, kwargs: dict[str, Any]) -> "PlotConfiguration":
        unknown = kwargs.keys() - DEFAULT_CONFIG.keys()
        if unknown:
            raise TypeError(f"Unknown plot options: {', '.join(sorted(unknown))}")
        values = {**DEFAULT_CONFIG, **kwargs}
        colors = values["colors"]
        if isinstance(colors, dict):
            if colors.keys() - DEFAULT_CONFIG["colors"].keys():
                raise ValueError(
                    "colors keys must be 'matrix', 'intersections', 'sets'"
                )
            colors = {**DEFAULT_CONFIG["colors"], **colors}
        else:
            colors = dict.fromkeys(DEFAULT_CONFIG["colors"], colors)
        if not all(color is None or is_color_like(color) for color in colors.values()):
            raise ValueError("colors must contain valid matplotlib colors")
        values["colors"] = colors
        if values["figsize"] is not None:
            try:
                width, height = values["figsize"]
                values["figsize"] = (float(width), float(height))
                if not all(math.isfinite(v) and v > 0 for v in values["figsize"]):
                    raise ValueError
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError(
                    "figsize must contain two positive finite numbers"
                ) from exc
        for name in ("marker_size", "line_width", "wspace", "hspace", "font_size"):
            try:
                value = float(values[name])
                if not math.isfinite(value) or value < 0:
                    raise ValueError
                if name in ("marker_size", "font_size") and value == 0:
                    raise ValueError
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError(f"{name} must be a valid nonnegative number") from exc
            values[name] = value
        return cls(**values)
