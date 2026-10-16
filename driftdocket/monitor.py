"""Dependency-free drift statistics and decision policy."""
from __future__ import annotations
from dataclasses import dataclass
from math import log, sqrt
from statistics import mean
from typing import Iterable

EPS = 1e-6

def _edges(values: list[float], bins: int) -> list[float]:
    ordered = sorted(values)
    return [ordered[min(len(ordered)-1, int(i*len(ordered)/bins))] for i in range(1, bins)]

def _shares(values: list[float], edges: list[float]) -> list[float]:
    counts = [0] * (len(edges)+1)
    for value in values:
        counts[sum(value > edge for edge in edges)] += 1
    return [max(EPS, count/len(values)) for count in counts]

def psi(reference: list[float], current: list[float], bins: int = 10) -> float:
    if not reference or not current: raise ValueError("samples must be non-empty")
    edges = _edges(reference, bins)
    expected, actual = _shares(reference, edges), _shares(current, edges)
    return sum((a-e)*log(a/e) for e,a in zip(expected, actual))

def ks(reference: list[float], current: list[float]) -> float:
    if not reference or not current: raise ValueError("samples must be non-empty")
    points = sorted(set(reference+current))
    return max(abs(sum(x<=p for x in reference)/len(reference)-sum(x<=p for x in current)/len(current)) for p in points)

@dataclass(frozen=True)
class Batch:
    month: str
    features: dict[str, list[float]]
    predictions: list[float]
    outcomes: list[float | None]
    outcome_ages_days: list[int]

    def __post_init__(self) -> None:
        n=len(self.predictions)
        if not n or len(self.outcomes)!=n or len(self.outcome_ages_days)!=n or any(len(v)!=n for v in self.features.values()):
            raise ValueError("all batch columns must be aligned and non-empty")

@dataclass(frozen=True)
class TicketPolicy:
    psi_warning: float = .20
    ks_warning: float = .25
    mae_drop: float = .12
    min_mature_labels: int = 30
    maturity_days: int = 30
    training_hours: float = 2.0
    hourly_compute_cost: float = .60
    engineer_hours: float = 3.0
    hourly_engineer_cost: float = 80.0

@dataclass(frozen=True)
class Finding:
    feature: str
    psi: float
    ks: float

@dataclass(frozen=True)
class Decision:
    month: str
    findings: tuple[Finding, ...]
    mature_labels: int
    immature_labels: int
    mae: float | None
    baseline_mae: float | None
    performance_drop: float | None
    action: str
    reason: str
    estimated_cost: float

    def issue_body(self) -> str:
        moved=", ".join(f"{f.feature} (PSI {f.psi:.3f}, KS {f.ks:.3f})" for f in self.findings) or "none"
        perf="unavailable" if self.performance_drop is None else f"{self.performance_drop:.3f}"
        return (f"## Drift decision: {self.month}\n\n**Action:** {self.action}\n\n"
                f"**Evidence:** moved features: {moved}; mature labels: {self.mature_labels}; "
                f"immature labels: {self.immature_labels}; MAE increase: {perf}.\n\n"
                f"**Rationale:** {self.reason}\n\n**Estimated retraining cost:** ${self.estimated_cost:.2f}\n")

class DriftMonitor:
    def __init__(self, reference: Batch, policy: TicketPolicy = TicketPolicy()) -> None:
        self.reference, self.policy = reference, policy
        mature = self._mature_pairs(reference)
        if len(mature) < policy.min_mature_labels: raise ValueError("reference lacks mature labels")
        self.baseline_mae = mean(abs(p-o) for p,o in mature)

    def _mature_pairs(self, batch: Batch) -> list[tuple[float,float]]:
        return [(p,float(o)) for p,o,age in zip(batch.predictions,batch.outcomes,batch.outcome_ages_days)
                if o is not None and age >= self.policy.maturity_days]

    def analyze(self, batch: Batch) -> Decision:
        if set(batch.features) != set(self.reference.features): raise ValueError("feature schema mismatch")
        findings=tuple(sorted((Finding(name,psi(self.reference.features[name], vals),ks(self.reference.features[name], vals))
                               for name,vals in batch.features.items()), key=lambda x:max(x.psi,x.ks), reverse=True))
        moved=tuple(f for f in findings if f.psi>=self.policy.psi_warning or f.ks>=self.policy.ks_warning)
        mature=self._mature_pairs(batch)
        labelled=sum(o is not None for o in batch.outcomes)
        current_mae=mean(abs(p-o) for p,o in mature) if mature else None
        drop=None if current_mae is None else current_mae-self.baseline_mae
        cost=self.policy.training_hours*self.policy.hourly_compute_cost+self.policy.engineer_hours*self.policy.hourly_engineer_cost
        if len(mature) < self.policy.min_mature_labels:
            action="WAIT_FOR_LABELS"
            reason="Feature drift is an early warning, but equally mature outcome evidence is insufficient."
        elif drop is not None and drop >= self.policy.mae_drop:
            action="OPEN_RETRAIN_TICKET"
            cause=moved[0].feature if moved else "unobserved factors"
            reason=f"Performance deteriorated on mature cohorts; strongest observed shift is {cause}."
        elif moved:
            action="MONITOR"
            reason="Inputs moved but mature-cohort performance remains within budget."
        else:
            action="NO_ACTION"
            reason="Neither feature drift nor mature-cohort performance crossed policy thresholds."
        return Decision(batch.month,moved,len(mature),labelled-len(mature),current_mae,self.baseline_mae,drop,action,reason,cost)

def alert_lead_month(decisions: Iterable[Decision]) -> int | None:
    rows=list(decisions)
    warning=next((i for i,d in enumerate(rows) if d.findings),None)
    decay=next((i for i,d in enumerate(rows) if d.action=="OPEN_RETRAIN_TICKET"),None)
    return None if warning is None or decay is None else decay-warning
