<p align="center">
  <img src="docs/assets/hero.svg" alt="PyUpSet — See where your data overlaps" width="100%">
</p>

<p align="center">
  <a href="https://github.com/Up1ng/pyupset/actions/workflows/ci.yml"><img src="https://github.com/Up1ng/pyupset/actions/workflows/ci.yml/badge.svg" alt="Tests"></a>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python 3.10+">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-2276dc" alt="MIT license"></a>
</p>

<p align="center">
  <strong>Beautiful UpSet plots. Straight from your DataFrame.</strong><br>
  Turn overlapping groups into a picture you can understand, customize, and share.
</p>

<p align="center">
  <a href="#get-started">Get started</a> ·
  <a href="examples/quickstart.ipynb">Try the notebook</a> ·
  <a href="docs/guide.md">User guide</a> ·
  <a href="https://github.com/Up1ng/pyupset/issues">Share an idea</a>
</p>

## Your groups. Their intersections. The full picture.

Which customers use both web and mobile? Which genes appear across conditions?
How do your research cohorts overlap?

PyUpSet puts set sizes, exact intersections, and percentages in one clear chart —
using the pandas and matplotlib workflow you already know.

<p align="center">
  <img src="examples/output/upset.png" alt="PyUpSet chart showing overlapping customer groups, colored by the number of groups in each intersection" width="860">
</p>

## Built for the way you work

- **DataFrame in, chart out.** Pass your membership columns and start exploring.
- **Readable by default.** Aligned panels, degree colors, counts, and percentages.
- **Make it yours.** Standard matplotlib objects, custom colors, and PNG or PDF export.
- **Keep your data local.** Runs in Python or Jupyter on your own machine.

## Get started

Requires Python 3.10 or newer.

```bash
pip install "git+https://github.com/Up1ng/pyupset.git@v0.1.0"
```

```python
import pandas as pd
import matplotlib.pyplot as plt
import pyupset

customers = pd.DataFrame({
    "Web":    [1, 1, 1, 0, 1, 0],
    "Mobile": [1, 0, 1, 1, 0, 1],
    "Email":  [1, 1, 0, 1, 0, 0],
    "Paid":   [1, 0, 1, 0, 0, 1],
})

fig, axes = pyupset.plot(customers, sets=list(customers.columns), sort_by="size")
plt.show()
```

Use `0/1` or `True/False` columns: one row per observation, one column per group.

## From exploration to your next report

Sort by intersection size with `sort_by="size"`, or by the number of groups with
`sort_by="degree"`. Adjust the chart with familiar matplotlib commands:

```python
axes["intersections"].set_xlabel("Customers")
fig.savefig("customer-overlap.png", dpi=300, bbox_inches="tight")
fig.savefig("customer-overlap.pdf", bbox_inches="tight")
```

For colors, sizing, and more examples, see the [user guide](docs/guide.md)
or open the [quickstart notebook](examples/quickstart.ipynb).

## Build with us

PyUpSet is open source and at the beginning of its journey.
Have a dataset, a use case, or an idea for a better chart?
[Open an issue](https://github.com/Up1ng/pyupset/issues/new/choose) — we'd like to hear it.

Star the repository to follow the project. Contributions are welcome:
[here's how to get involved](CONTRIBUTING.md).

<p align="center">
  Built with pandas, NumPy &amp; matplotlib. Released under the <a href="LICENSE">MIT license</a>.
</p>
