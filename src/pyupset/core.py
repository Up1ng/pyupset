"""Vectorized, exact (exclusive) intersection counts."""

import numpy as np

from .models import InputDataFrame, IntersectionMatrix


def compute(data: InputDataFrame, sort_by: str = "degree") -> IntersectionMatrix:
    if sort_by not in ("degree", "size"):
        raise ValueError("sort_by must be 'degree' or 'size'")
    counts = data.data.groupby(list(data.sets), sort=True, observed=True).size()
    membership = counts.index.to_frame(index=False).to_numpy(dtype=bool)
    sizes = counts.to_numpy(dtype=np.int64)
    if sort_by == "size":
        order = np.argsort(-sizes, kind="stable")
    else:
        order = np.argsort(membership.sum(axis=1), kind="stable")
    membership = membership[order]
    return IntersectionMatrix(
        sets=data.sets,
        members=tuple(
            tuple(name for name, active in zip(data.sets, row) if active)
            for row in membership
        ),
        membership=membership,
        sizes=sizes[order],
        set_sizes=data.data.sum().to_numpy(dtype=np.int64),
    )
