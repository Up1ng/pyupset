"""Run: python examples/basic.py (writes PNG and PDF to examples/output)."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

import pyupset


def main() -> None:
    data = pd.DataFrame(
        {
            "Web": [1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1],
            "Mobile": [0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1],
            "Email": [0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1],
            "Paid": [0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1],
        }
    )
    fig, axes = pyupset.plot(
        data,
        sets=list(data.columns),
        sort_by="size",
    )
    fig.suptitle("How your customers overlap", x=0.13, ha="left")
    output = Path(__file__).parent / "output"
    output.mkdir(exist_ok=True)
    for extension in ("png", "pdf"):
        fig.savefig(output / f"upset.{extension}", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    main()
