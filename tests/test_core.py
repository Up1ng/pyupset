from collections import Counter
from itertools import product

import numpy as np
import pandas as pd
import pytest

from pyupset.core import compute
from pyupset.validation import validate


@pytest.mark.parametrize("sort_by", ["degree", "size"])
def test_exact_counts_against_independent_counter(sort_by):
    rng = np.random.default_rng(42)
    values = rng.integers(0, 2, size=(1003, 5))
    names = list("ABCDE")
    frame = pd.DataFrame(values, columns=names)
    result = compute(validate(frame, names), sort_by)
    expected = Counter(tuple(bool(v) for v in row) for row in values)
    actual = dict(zip(map(tuple, result.membership), result.sizes))
    assert actual == expected
    np.testing.assert_array_equal(result.set_sizes, values.sum(axis=0))
    assert sum(result.sizes) == len(frame)
    assert len(set(result.members)) == len(expected)
    if sort_by == "degree":
        assert list(result.membership.sum(axis=1)) == sorted(
            result.membership.sum(axis=1)
        )
    else:
        assert list(result.sizes) == sorted(result.sizes, reverse=True)


def test_all_combinations_and_deterministic_ties():
    combinations = list(product([False, True], repeat=4))
    frame = pd.DataFrame(combinations[::-1], columns=list("ABCD"))
    result = compute(validate(frame, list("ABCD")))
    assert result.membership.tolist() == [
        list(row) for row in sorted(combinations, key=sum)
    ]
    assert result.members[0] == ()
    assert result.sizes.tolist() == [1] * 16


def test_unobserved_combinations_are_not_created():
    result = compute(validate(pd.DataFrame({"A": [1, 1], "B": [0, 0]}), ["A", "B"]))
    assert result.members == (("A",),)
    assert result.sizes.tolist() == [2]


@pytest.mark.parametrize("values", [[True, False], [1, 0], [1.0, 0.0]])
def test_binary_types(values):
    assert validate(pd.DataFrame({"A": values}), ["A"]).data["A"].dtype == bool


def test_nullable_boolean_and_numeric():
    frame = pd.DataFrame(
        {
            "A": pd.Series([True, False], dtype="boolean"),
            "B": pd.Series([0, 1], dtype="Int64"),
        }
    )
    assert compute(validate(frame, ["A", "B"])).sizes.tolist() == [1, 1]


@pytest.mark.parametrize(
    "values", [[0, 2], ["0", "1"], ["yes", "no"], [0, np.nan], [True, pd.NA]]
)
def test_invalid_values(values):
    with pytest.raises(ValueError, match="column 'A'"):
        validate(pd.DataFrame({"A": values}), ["A"])


@pytest.mark.parametrize(
    "frame,sets,error",
    [
        ([], ["A"], TypeError),
        (pd.DataFrame({"A": [1]}), ["B"], KeyError),
        (pd.DataFrame({"A": [1]}), [], ValueError),
        (pd.DataFrame({"A": [1]}), ["A", "A"], ValueError),
        (pd.DataFrame({"A": [1]}), "A", TypeError),
        (pd.DataFrame({"A": [1]}), [1], TypeError),
        (pd.DataFrame([[1, 0]], columns=["A", "A"]), ["A"], ValueError),
    ],
)
def test_invalid_structure(frame, sets, error):
    with pytest.raises(error):
        validate(frame, sets)


def test_auto_detection_ignores_metadata():
    frame = pd.DataFrame(
        {"A": [1, 0], "B": [True, False], "name": ["x", "y"], "age": [20, 30]}
    )
    assert validate(frame, None).sets == ("A", "B")
    with pytest.raises(ValueError, match="at least one"):
        validate(frame[["name", "age"]], None)


def test_no_input_mutation_and_single_set():
    frame = pd.DataFrame(
        {"A": [1, 1, 0], "metadata": [None, "x", "y"]}, index=[4, 4, 8]
    )
    original = frame.copy(deep=True)
    result = compute(validate(frame, ["A"]), "size")
    assert result.members == (("A",), ())
    assert result.sizes.tolist() == [2, 1]
    pd.testing.assert_frame_equal(frame, original)


def test_invalid_sort():
    with pytest.raises(ValueError, match="sort_by"):
        compute(validate(pd.DataFrame({"A": [1]}), ["A"]), "unknown")
