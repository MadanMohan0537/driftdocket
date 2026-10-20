# Model Drift Retraining Decisions

[![CI](https://github.com/MadanMohan0537/model-drift-retraining-decisions/actions/workflows/ci.yml/badge.svg)](https://github.com/MadanMohan0537/model-drift-retraining-decisions/actions/workflows/ci.yml)

**Turn model drift into a reviewable decision: measure which inputs moved, wait for mature labels before claiming the model got worse, and draft a retraining ticket with evidence and cost only when the error budget is actually exceeded.**

A dependency-free Python MVP. The package and CLI are still called `driftdocket` (`python -m driftdocket.cli`, and the `driftdocket` console script).

## Problem and who it's for

Feature drift is cheap to detect and easy to overreact to. Labels often arrive late. A naive monitor compares young, incomplete cohorts with mature history and mistakes missing outcomes for model decay. ML engineers, on-call data scientists, and the product or program owners who approve retraining spend need a monitor that separates "something moved" from "accuracy dropped".

## Approach

1. Score each feature against a reference distribution with the Population Stability Index (PSI) and the Kolmogorov–Smirnov (KS) distance. The default warnings are PSI 0.20 and KS 0.25.
2. Track which outcomes exist and which have reached the configured maturity age (default 30 days).
3. Apply the mean absolute error (MAE) budget only when at least 30 labels are mature. The default budget is an MAE increase of 0.12 over the reference cohort.
4. Choose one of four actions: `NO_ACTION`, `MONITOR`, `WAIT_FOR_LABELS`, or `OPEN_RETRAIN_TICKET`.
5. A ticket carries the evidence, the rationale, and an estimated compute and engineering cost from configured hours and rates.

```text
monthly batch -> PSI/KS findings -> maturity gate -> MAE policy -> decision
                                                              -> ticket / report
```

## What exists today

The generator builds twelve months of synthetic demand batches, 120 rows each, with temperature and promotion features. The baseline is a standalone reference batch (`month(1, "reference")`). From August 2026 the feature distributions shift; October, November, and December also raise prediction noise. December keeps every fifth outcome. The same seeds always recreate the run. The generator has no seasonal cycle.

`python -m driftdocket.cli` on that year prints 12 months, 2 tickets, and `alert_lead_months` of 8:

- The tickets are October and November 2026 (`OPEN_RETRAIN_TICKET`).
- The first feature warning is February 2026 (`MONITOR`), eight months before the October ticket. February, March, and April warn while the seeded shift is still zero, because temperature PSI crosses 0.20 against the reference sample. August and September are the first seeded distribution shifts; they stay on `MONITOR` because mature-cohort MAE stays inside the 0.12 budget. The lead-time number is that index gap. It shows how `alert_lead_month` is calculated.
- In December only 24 of 120 outcomes are present (every fifth row). Those 24 are 45 days old, and the other 96 outcomes are missing, so the mature count is 24 and the action is `WAIT_FOR_LABELS`.
- Delayed-label tests use that same 24-of-120 pattern. Large prediction error with incomplete outcomes returns `WAIT_FOR_LABELS` and opens no ticket. The same error with all 120 labels mature returns `OPEN_RETRAIN_TICKET`.
- Ticket evidence is the moved features ranked by max(PSI, KS). The rationale names the strongest observed shift. That rank is an association.
- 21 unit tests in `tests/test_monitor.py`. `.github/workflows/ci.yml` is configured to run them on Python 3.11, 3.12, and 3.13.

## How success would be measured

| Measure | Status |
|---|---|
| Performance tickets opened with fewer than 30 mature labels | Not yet measured on a live model. In this code, fewer than 30 mature labels always returns `WAIT_FOR_LABELS`, and the delayed-label tests cover that path on the fixture. |
| Lead time from first drift warning to confirmed decay | Not yet measured on a real model. The synthetic year reports 8 (`alert_lead_months`), including February–April warnings that fire with no seeded shift. |
| Unnecessary retraining runs avoided | Not yet measured |
| Reviewer agreement with the recommended action | Not yet measured |

## Limitations

- The dataset is deterministic and synthetic.
- Ranked features are PSI/KS associations, not causal proof.
- PSI binning is reference-based, and KS results have no multiple-testing correction.
- Each ticket is a Markdown string inside the JSON report (`drift-report.json`). Nothing is filed in an issue tracker.
- Production use would need durable storage, data contracts, authentication, real cost telemetry, and monitoring for label delay that depends on the outcome.

See [docs/METHOD.md](docs/METHOD.md) and [docs/BACKLOG.md](docs/BACKLOG.md).

## Quick start

Requires Python 3.11+. The monitor and CLI use the Python standard library only: no credentials, paid APIs, or network calls. `pip` may still download a build backend if setuptools is not already installed.

```bash
git clone https://github.com/MadanMohan0537/model-drift-retraining-decisions.git
cd model-drift-retraining-decisions
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
python -m driftdocket.cli --output drift-report.json
```

## Deployment

Cloudflare Workers is the planned target and is not configured yet. This repository is not deployed.

What is needed before a Worker can run:

- `wrangler.toml`
- a Worker entry point
- Python Workers, or a JavaScript/TypeScript port of the `driftdocket` package

When that config is in place, deploy with:

```bash
npx wrangler deploy
```

## License

MIT. See [LICENSE](LICENSE).
