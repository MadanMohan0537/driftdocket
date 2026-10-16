# Feature backlog

| Priority | Feature | User problem | Behavior | Dependencies | Success test | Risks / tradeoffs | Status |
|---|---|---|---|---|---|---|---|
| P0 | Drift-to-decision workflow | Owners discover decay too late | Rank PSI/KS evidence, gate on performance, cost a ticket | Python stdlib | Seeded decay opens one evidence-backed decision | Fixed thresholds need calibration | Shipped |
| P1 | Delayed-label attribution | Missing labels resemble deterioration | Compare only equally mature cohorts and expose maturity counts | Outcome timestamps | Zero performance tickets below 30 mature labels | Delay may be outcome-dependent | Shipped |
| P1 | False-alarm budget | Many correlated features create alert noise | Calibrate thresholds with block bootstrap and cap expected monthly alarms | Historical windows | Held-out stable year remains within alarm budget | May delay rare-shift detection | Planned |
| P1 | Decision follow-through | Tickets do not prove retraining helped | Track accept/defer/reject and post-retrain impact | Ticket state, outcome metrics | Every ticket has disposition and measured result | Attribution confounded by other changes | Planned |
| P2 | Sensor fault versus behavior shift | Broken pipelines trigger needless retraining | Rank freshness, missingness, range, and contract evidence before retrain | Data contracts, freshness telemetry | Seeded faults recommend repair, not retraining | Fault and behavior shift can coexist | Planned |
| P2 | Champion-challenger gate | Retraining can make performance worse | Train candidate and promote only on temporal holdout | Training pipeline, artifact registry | Inferior challenger cannot ship | Extra compute and operational complexity | Explored |
| P2 | Outcome-delay selection audit | Mature labels may not represent all predictions | Model maturity probability and report weighted sensitivity | Cohort covariates | Seeded informative delay is detected | Weighting increases variance | Explored |
| P3 | Drift budget portfolio | Teams cannot compare urgency across models | Allocate alert/retrain budget by impact and uncertainty | Model registry, business value | Highest expected-loss model ranks first | Monetary estimates can dominate safety concerns | Explored |
| P3 | Counterfactual cause probes | Ranked correlations are mistaken for causes | Replay predictions while perturbing one plausible driver | Feature transformation rules | Known synthetic driver ranks above correlates | Unrealistic perturbations mislead | Explored |
| P3 | Ticket deduplication and cooldown | One incident creates repeated monthly tickets | Merge windows into an incident with recovery criteria | Durable incident state | Sustained shift produces one active ticket | Can hide distinct concurrent failures | Explored |
