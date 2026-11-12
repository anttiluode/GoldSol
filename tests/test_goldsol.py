import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"experiments"))
from jitter import make,simulate,schedule,score,match_counts,SLOTS,INTERVENTIONS
from history import make_state,trial,HISTORIES,settle,Net,RELAY

class GoldSol(unittest.TestCase):
 def test_same_input_seeds_reproducible(self):
  self.assertEqual(schedule(101,1),schedule(101,1))
  self.assertNotEqual(schedule(101,1),schedule(102,1))
 def test_matched_event_score(self):
  self.assertEqual(match_counts([4,8,16],[5,8,19],0,1),
                   {"matched":2,"world_events":3,"misses":1,"extra_predictions":1})
 def test_clean_baseline_native_and_window(self):
  for model in ("gn","window"):
   with self.subTest(model=model):
    d=simulate(schedule(0,0),model,"off",0)
    s=score(d)
    self.assertEqual(s["errors_after_warmup"],0)
    self.assertEqual(s["misses"],0)
    self.assertEqual(s["extra_predictions"],0)
 def test_clean_omission_detects_and_adapts(self):
  for model in ("gn","window"):
   with self.subTest(model=model):
    d=score(simulate(schedule(0,0,True),model,"off",0),True)
    self.assertTrue(d["errors_near_change"]>0)
    self.assertTrue(d["recovered_after_change"])
 def test_no_ext_route_matches_baseline(self):
  beats=schedule(13,1)
  a=simulate(beats,"gn","off",0)
  b=simulate(beats,"gn","bias",0)
  self.assertEqual(a,b)
 def test_all_variants_have_distinct_names(self):
  names=[x[0] for x in INTERVENTIONS]
  self.assertEqual(len(names),len(set(names)))
 def test_relay_history_ablation_runs(self):
  base=settle(Net([RELAY]))
  row=trial(base,"single",8,-10)
  self.assertIn("history_swap_recovered_baseline",row)
  self.assertIn("pipe_swap_recovered_baseline",row)
  self.assertIn("pre_variance",row)
 def test_short_history_effect_caused_by_pipe_not_hist_buffer(self):
  base=settle(Net([RELAY]))
  for kind in ("single","train_8","train_12","train_16"):
   for mag in (-13.5,-11,-8):
    with self.subTest(kind=kind,mag=mag):
     row=trial(base,kind,2,mag)
     self.assertTrue(row["changed_firing"])
     self.assertFalse(row["history_swap_recovered_baseline"])
     self.assertTrue(row["pipe_swap_recovered_baseline"])
  for kind in ("single","train_8","train_12","train_16"):
   with self.subTest(kind=kind,gap=4):
    self.assertFalse(trial(base,kind,4,-11)["changed_firing"])

if __name__=="__main__":unittest.main()
