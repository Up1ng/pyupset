from io import BytesIO
from unittest.mock import patch

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
from matplotlib.axes import Axes
from matplotlib.colors import to_rgba
from matplotlib.figure import Figure

import pyupset
from pyupset.config import DEFAULT_CONFIG


def test_plot_contract_layout_and_counts():
    frame = pd.DataFrame({"A": [1, 1, 1, 0], "B": [0, 0, 1, 1]})
    original = frame.copy(deep=True)
    fig, axes = pyupset.plot(frame, sets=["A", "B"], sort_by="size")
    assert isinstance(fig, Figure)
    assert set(axes) == {"matrix", "intersections", "sets"}
    assert all(isinstance(ax, Axes) and ax.figure is fig for ax in axes.values())
    assert [bar.get_width() for bar in axes["intersections"].containers[0]] == [2, 1, 1]
    assert [bar.get_height() for bar in axes["sets"].containers[0]] == [3, 2]
    assert axes["sets"].get_position().y0 > axes["matrix"].get_position().y1
    assert axes["intersections"].get_position().x0 > axes["matrix"].get_position().x1
    assert list(axes["matrix"].collections[0].get_offsets()) != []
    assert axes["matrix"].get_shared_x_axes().joined(axes["matrix"], axes["sets"])
    assert (
        axes["matrix"].get_shared_y_axes().joined(axes["matrix"], axes["intersections"])
    )
    pd.testing.assert_frame_equal(frame, original)
    axes["intersections"].set_title("Custom title")
    for fmt in ("png", "pdf"):
        output = BytesIO()
        fig.savefig(output, format=fmt)
        assert len(output.getvalue()) > 1000


@pytest.mark.parametrize("names", [["A"], ["A", "B", "C"]])
def test_empty_data_contract(names):
    fig, axes = pyupset.plot(pd.DataFrame(columns=names), sets=names)
    assert set(axes) == {"matrix", "intersections", "sets"}
    assert [text.get_text() for text in fig.texts] == ["No data to plot"]
    fig.canvas.draw()


def test_rows_outside_every_set():
    fig, axes = pyupset.plot(pd.DataFrame({"A": [0, 0], "B": [0, 0]}))
    assert axes["intersections"].containers[0][0].get_width() == 2
    assert axes["matrix"].collections[1].get_offsets().shape == (0, 2)
    assert [bar.get_height() for bar in axes["sets"].containers[0]] == [0, 0]
    fig.canvas.draw()


def test_options_are_independent_between_calls():
    frame = pd.DataFrame({"A": [1, 0]})
    first, axes = pyupset.plot(
        frame, colors={"sets": "red"}, figsize=(8, 5), marker_size=90
    )
    second, other = pyupset.plot(frame)
    np.testing.assert_array_equal(first.get_size_inches(), [8, 5])
    assert axes["sets"].patches[0].get_facecolor() == to_rgba("red")
    assert other["sets"].patches[0].get_facecolor() == to_rgba(
        DEFAULT_CONFIG["colors"]["sets"]
    )
    assert first is not second
    assert DEFAULT_CONFIG["colors"]["sets"] != "red"


@pytest.mark.parametrize(
    "options,error",
    [
        ({"sort_by": "bad"}, ValueError),
        ({"unknown": 1}, TypeError),
        ({"colors": {"bad": "red"}}, ValueError),
        ({"colors": "not-a-color"}, ValueError),
        ({"figsize": (0, 3)}, ValueError),
        ({"figsize": (3,)}, ValueError),
        ({"marker_size": -1}, ValueError),
        ({"hspace": float("nan")}, ValueError),
    ],
)
def test_bad_options_do_not_leak_figures(options, error):
    before = plt.get_fignums()
    with pytest.raises(error):
        pyupset.plot(pd.DataFrame({"A": [1]}), ["A"], **options)
    assert plt.get_fignums() == before


def test_memory_error_is_preserved():
    with patch("pyupset.api.compute", side_effect=MemoryError("allocation failed")):
        with pytest.raises(MemoryError, match="Not enough memory") as error:
            pyupset.plot(pd.DataFrame({"A": [1]}), ["A"])
    assert isinstance(error.value.__cause__, MemoryError)


def test_render_failure_closes_figure():
    with patch(
        "matplotlib.axes.Axes.scatter", side_effect=RuntimeError("render failed")
    ):
        with pytest.raises(RuntimeError, match="render failed"):
            pyupset.plot(pd.DataFrame({"A": [1]}), ["A"])
    assert plt.get_fignums() == []


def test_matplotlib_style_is_respected():
    with plt.style.context("dark_background"):
        fig, _ = pyupset.plot(pd.DataFrame({"A": [1]}))
        assert fig.get_facecolor() == to_rgba("black")


def test_matrix_membership_matches_bar_rows_and_degree_colors():
    frame = pd.DataFrame({"A": [1, 1, 1, 0], "B": [0, 0, 1, 1]})
    _, axes = pyupset.plot(frame, ["A", "B"], sort_by="size")
    inactive, active = axes["matrix"].collections[:2]
    assert len(inactive.get_offsets()) == 6
    # Rows: A only (2 observations), B only (1), A and B (1).
    np.testing.assert_array_equal(
        active.get_offsets(), [[0, 0], [1, 1], [0, 2], [1, 2]]
    )
    bars = axes["intersections"].containers[0]
    np.testing.assert_allclose(active.get_facecolors()[0], bars[0].get_facecolor())
    np.testing.assert_allclose(active.get_facecolors()[2], bars[2].get_facecolor())
    assert bars[0].get_facecolor() != bars[2].get_facecolor()
    assert [label.get_text() for label in axes["intersections"].texts] == [
        "2",
        "1",
        "1",
    ]


def test_percent_axis_tracks_changed_count_limits():
    fig, axes = pyupset.plot(pd.DataFrame({"A": [1] * 20}))
    axes["intersections"].set_xlim(0, 10)
    fig.canvas.draw()
    percent = axes["intersections"].child_axes[0]
    np.testing.assert_allclose(percent.get_xlim(), [0, 50])
    # The returned mapping still gives all three primary axes.
    assert len(fig.axes) == 3
