# Method and limitations

## Reproducible study

The CLI generates twelve monthly batches of 120 demand observations. Later months receive a temperature/promotion distribution shift; the final labelled months also receive a seeded prediction-error increase. The last month has delayed outcomes. The same random seeds always recreate the study.

Predeclared thresholds are PSI 0.20, KS 0.25, MAE increase 0.12, at least 30 labels, and outcome age of at least 30 days. The monitor reports the number of months between the first feature warning and first confirmed performance-decay ticket.

## P1 delayed-label attribution

Only predictions whose outcomes both exist and reach the same maturity horizon enter performance comparisons. A seeded incomplete cohort must not produce `OPEN_RETRAIN_TICKET`. This prevents the specific false alert caused by missing labels; it does not remove outcome-dependent selection bias among labels that do mature.

## Limitations

- Synthetic results establish code behavior, not real-world model quality.
- Feature association is not causal attribution.
- PSI depends on bins and reference choice; KS sensitivity scales with sample size.
- Multiple features are tested without false-discovery correction.
- MAE is the only performance metric.
- Cost uses configured hours and rates, not cloud billing.
- There is no persistent scheduler, dashboard, authenticated GitHub write, or champion-challenger training job.
- Outcome delay may be informative; equally mature cohorts can still differ systematically.
