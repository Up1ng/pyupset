"""Data passed between validation, computation and rendering."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from numpy.typing import NDArray


@dataclass(frozen=True)
class InputDataFrame:
    data: pd.DataFrame
    sets: tuple[str, ...]


@dataclass(frozen=True)
class IntersectionMatrix:
    sets: tuple[str, ...]
    members: tuple[tuple[str, ...], ...]
    membership: NDArray[np.bool_]
    sizes: NDArray[np.int64]
    set_sizes: NDArray[np.int64]
