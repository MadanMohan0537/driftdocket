import unittest
from dataclasses import replace
from driftdocket.fixtures import month, year
from driftdocket.monitor import Batch, DriftMonitor, TicketPolicy, alert_lead_month, ks, psi

class MonitorTests(unittest.TestCase):
    def setUp(self): self.ref=month(1,"ref"); self.monitor=DriftMonitor(self.ref)
    def test_psi_same_zero(self): self.assertAlmostEqual(psi([1,2,3]*20,[1,2,3]*20),0)
    def test_psi_detects_shift(self): self.assertGreater(psi(list(range(100)),list(range(100,200))),.2)
    def test_ks_same_zero(self): self.assertEqual(ks([1,2,3],[1,2,3]),0)
    def test_ks_detects_shift(self): self.assertEqual(ks([1,2,3],[8,9,10]),1)
    def test_empty_psi_rejected(self):
        with self.assertRaises(ValueError): psi([], [1])
    def test_empty_ks_rejected(self):
        with self.assertRaises(ValueError): ks([], [1])
    def test_batch_alignment(self):
        with self.assertRaises(ValueError): Batch("x",{"a":[1]},[1,2],[1,2],[1,2])
    def test_reference_maturity_required(self):
        with self.assertRaises(ValueError): DriftMonitor(month(1,"x",mature=False))
    def test_schema_mismatch(self):
        b=month(2,"x"); bad=replace(b,features={"other":b.predictions})
        with self.assertRaises(ValueError): self.monitor.analyze(bad)
    def test_stable_no_action(self): self.assertEqual(self.monitor.analyze(month(2,"x")).action,"NO_ACTION")
    def test_shift_before_decay_monitors(self): self.assertEqual(self.monitor.analyze(month(2,"x",shift=6)).action,"MONITOR")
    def test_decay_opens_ticket(self): self.assertEqual(self.monitor.analyze(month(2,"x",shift=6,error=.3)).action,"OPEN_RETRAIN_TICKET")
    def test_delayed_labels_wait(self): self.assertEqual(self.monitor.analyze(month(2,"x",shift=6,error=.3,mature=False)).action,"WAIT_FOR_LABELS")
    def test_ticket_has_cost(self): self.assertIn("$241.20",self.monitor.analyze(month(2,"x",shift=6,error=.3)).issue_body())
    def test_ticket_has_evidence(self): self.assertIn("mature labels",self.monitor.analyze(month(2,"x",shift=6,error=.3)).issue_body())
    def test_cost_configuration(self):
        m=DriftMonitor(self.ref,TicketPolicy(engineer_hours=1,hourly_engineer_cost=50,training_hours=1,hourly_compute_cost=2))
        self.assertEqual(m.analyze(month(2,"x")).estimated_cost,52)
    def test_ranked_findings(self):
        fs=self.monitor.analyze(month(2,"x",shift=6)).findings
        self.assertGreaterEqual(max(fs[0].psi,fs[0].ks),max(fs[-1].psi,fs[-1].ks))
    def test_year_has_12_months(self): self.assertEqual(len(year()),12)
    def test_delayed_label_false_alert_avoided(self):
        d=self.monitor.analyze(month(4,"x",shift=0,error=.4,mature=False))
        self.assertNotEqual(d.action,"OPEN_RETRAIN_TICKET")
    def test_lead_time(self):
        ds=[self.monitor.analyze(b) for b in year()]
        self.assertIsNotNone(alert_lead_month(ds))
    def test_no_lead_without_warning(self):
        self.assertIsNone(alert_lead_month([self.monitor.analyze(month(2,"x"))]))

if __name__=="__main__": unittest.main()
