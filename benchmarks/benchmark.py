"""Measure computation and complete canvas rendering separately on 1M rows."""

import argparse
from time import perf_counter

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pyupset.config import PlotConfiguration
from pyupset.core import compute
from pyupset.rendering import render
from pyupset.validation import validate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=1_000_000)
    parser.add_argument("--sets", type=int, default=8)
    args = parser.parse_args()
    names = [f"Set {i + 1}" for i in range(args.sets)]
    data = pd.DataFrame(
        np.random.default_rng(42).integers(0, 2, (args.rows, args.sets), dtype=np.int8),
        columns=names,
    )
    start = perf_counter()
    result = compute(validate(data, names), "degree")
    computation = perf_counter() - start
    start = perf_counter()
    fig, _ = render(result, PlotConfiguration.from_kwargs({}))
    fig.canvas.draw()
    rendering = perf_counter() - start
    plt.close(fig)
    assert int(result.sizes.sum()) == args.rows
    print(f"Rows: {args.rows:,}; sets: {args.sets}; intersections: {len(result.sizes)}")
    print(f"Validation + computation: {computation:.3f}s (target <=3s)")
    print(f"Rendering including canvas draw: {rendering:.3f}s (target <=5s)")
    if computation > 3 or rendering > 5:
        raise SystemExit("Performance target exceeded on this machine")


if __name__ == "__main__":
    main()
