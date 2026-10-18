# Contributing to PyUpSet

A useful chart starts with a real question. Tell us what you're exploring,
share a small example, or suggest a change that would help your workflow.

## Share feedback

[Open an issue](https://github.com/Up1ng/pyupset/issues/new/choose) for a bug,
a feature request, or a visualization you'd like to see.
For bugs, include a small reproducible example, your package versions,
and the result you expected. Use synthetic data when sharing an example.

## Work on the code

```bash
git clone https://github.com/Up1ng/pyupset.git
cd pyupset
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

Before opening a pull request, run:

```bash
python -m pytest
python -m mypy src/pyupset
python -m black --check src tests examples/basic.py benchmarks
```

Keep changes focused. Explain what the change helps users do and include
an example or screenshot for visual changes.

## Project direction

The current release focuses on DataFrame input, clear static charts,
and matplotlib customization. Future directions include more visual themes,
richer annotations, and interactive exploration.
