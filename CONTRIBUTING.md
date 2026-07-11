# Contributing

## Development setup

```bash
python3 -m pip install -r requirements-research.txt
cd dashboard
npm ci
```

## Checks

Run the complete Python suite and dashboard syntax checks before opening a
change for review:

```bash
python3 -m unittest discover -s tests
node --check dashboard/static/app.js
cd dashboard && npm test
```

## Data fidelity

- Do not infer values that the available source data cannot support.
- Keep unsupported fields blank and document the missing source requirement.
- Keep synthetic outputs under `data/mock/` and observed-data outputs outside
  that directory.
- Label selected-source ratios as observed coverage rather than global market
  coverage.

## Pull requests

Keep changes scoped, include the validation commands used, and state any data
source or methodology change that could alter historical results.
