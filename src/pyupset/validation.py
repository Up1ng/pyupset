"""Validate membership data without changing the caller's DataFrame."""

import pandas as pd
from pandas.api.types import is_bool_dtype, is_numeric_dtype

from .models import InputDataFrame


def _binary(column: pd.Series) -> bool:
    return bool(
        (is_bool_dtype(column.dtype) or is_numeric_dtype(column.dtype))
        and not column.isna().any()
        and column.isin([0, 1]).all()
    )


def validate(data: pd.DataFrame, sets: list[str] | None) -> InputDataFrame:
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")
    if not data.columns.is_unique:
        raise ValueError("DataFrame column names must be unique")
    if sets is None:
        sets = [
            name
            for name in data.columns
            if isinstance(name, str) and _binary(data[name])
        ]
    if not isinstance(sets, list) or not all(isinstance(s, str) for s in sets):
        raise TypeError("sets must be a list of column names (strings)")
    if not sets:
        raise ValueError("sets must contain at least one binary column")
    if len(sets) != len(set(sets)):
        raise ValueError("sets must not contain duplicate column names")
    missing = [name for name in sets if name not in data.columns]
    if missing:
        raise KeyError(f"Set columns not found: {missing}")
    for name in sets:
        column = data[name]
        if column.isna().any():
            raise ValueError(f"Set column {name!r} contains missing values (NaN/NA)")
        if not column.empty and not _binary(column):
            raise ValueError(
                f"Set column {name!r} must contain binary numeric 0/1 or boolean values"
            )
    return InputDataFrame(data.loc[:, sets].astype(bool), tuple(sets))
