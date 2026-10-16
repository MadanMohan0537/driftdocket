"""Deterministic synthetic monthly demand data."""
from random import Random
from .monitor import Batch

def month(seed: int, label: str, shift: float=0, error: float=.04, mature: bool=True) -> Batch:
    r=Random(seed); n=120
    temp=[15+r.gauss(0,3)+shift for _ in range(n)]
    promo=[1.0 if r.random()<(.12+shift/20) else 0.0 for _ in range(n)]
    actual=[max(0, .04*t+.28*p+r.gauss(0,.03)) for t,p in zip(temp,promo)]
    pred=[max(0,a+r.gauss(0,error)) for a in actual]
    outcomes:list[float|None]=actual if mature else [a if i%5==0 else None for i,a in enumerate(actual)]
    ages=[45 if mature else (45 if i%5==0 else 8) for i in range(n)]
    return Batch(label,{"temperature":temp,"promotion":promo},pred,outcomes,ages)

def year() -> list[Batch]:
    rows=[]
    for i in range(12):
        shift=max(0,i-6)*1.2
        rows.append(month(100+i,f"2026-{i+1:02d}",shift=shift,error=.04 if i<9 else .22,mature=i<11))
    return rows
