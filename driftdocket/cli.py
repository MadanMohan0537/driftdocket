import argparse, json
from pathlib import Path
from .fixtures import month, year
from .monitor import DriftMonitor, alert_lead_month

def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("--output",type=Path,default=Path("drift-report.json")); args=p.parse_args()
    monitor=DriftMonitor(month(1,"reference"))
    decisions=[monitor.analyze(b) for b in year()]
    report={"product":"DriftDocket","months":[{"month":d.month,"action":d.action,"mature_labels":d.mature_labels,
      "performance_drop":d.performance_drop,"estimated_cost":d.estimated_cost,
      "features":[{"name":f.feature,"psi":f.psi,"ks":f.ks} for f in d.findings]} for d in decisions],
      "alert_lead_months":alert_lead_month(decisions),
      "tickets":[d.issue_body() for d in decisions if d.action=="OPEN_RETRAIN_TICKET"]}
    args.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"months":len(decisions),"tickets":len(report["tickets"]),"alert_lead_months":report["alert_lead_months"]},indent=2))
if __name__=="__main__": main()
