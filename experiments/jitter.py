"""GoldSol J1: frozen-architecture signal_in perturbations under phase jitter.

Goal: test *whether*, not assume that, GN27's extra signal_in port yields
better tolerance than the checkerboard-free window relay. Original models are
imported without modifications. All connections into signal_in are implemented
in the experiment harness; they are NOT supported as native Net edges yet.

Preregistered settings below are evaluated on fixed development seeds and
separate held-out seeds. No per-seed tuning. A low error count is meaningless
if the model fails to detect a real permanent omission, hence the control.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from gn27 import Net, Beats, RELAY, settle
from window import WindowNet

SLOTS=(0,12,20)
START=40
PERIOD=32
LAPS=22
TICKS=START+PERIOD*LAPS+24
SCORE_END=START+PERIOD*LAPS # do not score post-stream omissions
SCORE_START=START+PERIOD*6
CHANGE_LAP=12
INTERVENTIONS=[
  ("original_gn","gn", "off",0.0),
  ("simple_window","window","off",0.0),
  ("signal_in_world_pos_0.25","gn","world",0.25),
  ("signal_in_world_neg_0.25","gn","world",-0.25),
  ("signal_in_world_pos_0.75","gn","world",0.75),
  ("signal_in_world_neg_0.75","gn","world",-0.75),
  ("signal_in_prediction_pos_0.25","gn","prediction",0.25),
  ("signal_in_prediction_neg_0.25","gn","prediction",-0.25),
  ("signal_in_error_pos_0.25","gn","error",0.25),
  ("signal_in_error_neg_0.25","gn","error",-0.25),
  ("signal_in_bias_pos_0.20","gn","bias",0.20),
  ("signal_in_bias_neg_0.20","gn","bias",-0.20),
]
DEV_SEEDS=(11,19,23)
TEST_SEEDS=(101,103,107,109)

def schedule(seed=0,jitter=0,change=False):
    """Nominal expected beat times; the harness only determines world inputs."""
    rng=np.random.default_rng(seed)
    beats=[]
    for lap in range(LAPS):
        slots=[s for s in SLOTS if not (change and lap>=CHANGE_LAP and s==20)]
        for s in slots:
            beats.append(START+lap*PERIOD+s+int(rng.integers(-jitter,jitter+1)))
    return beats

def make(model):
    # 1 world source, 8 ring cells, XOR comparator, 10 native units.
    edges=[(1+i,1+(i+1)%8,-6.0,0) for i in range(8)]
    edges += [(0,9,-4.5,0),(1,9,-4.5,0),(9,3,-6.0,0)]
    if model=="gn":
        return settle(Net([RELAY]*10,edges))
    if model=="window":
        return WindowNet([RELAY]*10,edges)
    raise ValueError(model)

def simulate(beats,model="gn",route="off",gain=0.,track=False):
    net=make(model)
    det=Beats(10)
    pulses=set()
    for beat in beats:
        pulses.update((beat-4,beat-3))
    history_low=0;history_total=0
    for t in range(TICKS):
        sp=np.zeros(10)
        if t in pulses:sp[0]=-10.0
        ext=None
        if model=="gn" and route!="off":
            ext=np.zeros(10)
            # net.sent[0,j] is the source beat wire from *previous* step.
            # Therefore all routes are strictly causal by at least one tick.
            if route=="world":ext[9]=gain*net.sent[0,0]
            elif route=="prediction":ext[9]=gain*net.sent[0,1]
            elif route=="error":ext[9]=gain*net.sent[0,9]
            elif route=="bias":ext[9]=gain
            else:raise ValueError(route)
        det.see(net.step(ext=ext,sp_ext=sp),t)
        if track and model=="gn" and t>=SCORE_START:
            history_low+=int((net.var<=0.1).sum())
            history_total+=10
    d={"world":det.ev[0],"prediction":det.ev[1],"error":det.ev[9]}
    if track:d["var_below_target"]=history_low;d["var_total"]=history_total
    return d

def match_counts(world,pred,after,tolerance=1,before=None):
    w=[x for x in world if x>=after and (before is None or x<before)]
    p=[x for x in pred if x>=after and (before is None or x<before)]
    i=j=good=0
    while i<len(w) and j<len(p):
        if abs(w[i]-p[j])<=tolerance:
            good+=1;i+=1;j+=1
        elif w[i]<p[j]:i+=1
        else:j+=1
    return {"matched":good,"world_events":len(w),
            "misses":len(w)-good,"extra_predictions":len(p)-good}

def score(d,change=False):
    late=[t for t in d["error"] if SCORE_START<=t<SCORE_END]
    details=match_counts(d["world"],d["prediction"],SCORE_START,1,SCORE_END)
    details["errors_after_warmup"]=len(late)
    if change:
        change_at=START+PERIOD*CHANGE_LAP
        details["errors_near_change"]=sum(change_at<=t<min(SCORE_END,change_at+3*PERIOD) for t in d["error"])
        # Exclude transition, require exact late phase memory for clean-world control.
        late_at=START+18*PERIOD
        w={t for t in d["world"] if late_at<=t<SCORE_END}
        p={t for t in d["prediction"] if late_at<=t<SCORE_END}
        details["recovered_after_change"]=bool(w==p and details["errors_near_change"]>0)
    return details

def run_suite(seeds=DEV_SEEDS,jitter=1):
    result=[]
    for name,model,route,gain in INTERVENTIONS:
        jittered=[score(simulate(schedule(seed,jitter),model,route,gain))
                  for seed in seeds]
        clean_change=score(simulate(schedule(0,0,True),model,route,gain),True)
        clean_stable=score(simulate(schedule(0,0,False),model,route,gain))
        row={
           "name":name,"model":model,"route":route,"gain":gain,
           "jitter":jitter,"seeds":list(seeds),
           "jitter_error_counts":[x["errors_after_warmup"] for x in jittered],
           "jitter_error_mean":round(sum(x["errors_after_warmup"] for x in jittered)/len(jittered),3),
           "jitter_match_misses":[x["misses"] for x in jittered],
           "jitter_prediction_extras":[x["extra_predictions"] for x in jittered],
           "clean_stable_errors":clean_stable["errors_after_warmup"],
           "clean_change_detected":clean_change["errors_near_change"]>0,
           "clean_change_recovered":clean_change["recovered_after_change"],
           "clean_change_errors":clean_change["errors_near_change"],
        }
        result.append(row)
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",default="-")
    args=parser.parse_args()
    reports={"protocol":"GN27 unchanged; one-wire XOR ring; 32-tick period; jittered 3-event world; routed external ext only for GN",
             "interventions":INTERVENTIONS,
             "dev_seeds":DEV_SEEDS,"heldout_seeds":TEST_SEEDS,
             "development_jitter1":run_suite(DEV_SEEDS,1),
             "heldout_jitter1":run_suite(TEST_SEEDS,1),
             "heldout_jitter2":run_suite(TEST_SEEDS,2)}
    out=json.dumps(reports,indent=2)
    if args.output=="-":print(out)
    else:
       target=Path(args.output);target.parent.mkdir(parents=True,exist_ok=True)
       target.write_text(out+"\n")
       print("Wrote",target)
    for name in ("development_jitter1","heldout_jitter1","heldout_jitter2"):
       print("\n"+name)
       for row in reports[name]:
          print(f"  {row['name']:34} errors {row['jitter_error_mean']:5.1f} "
                f"miss {sum(row['jitter_match_misses']):3} extra {sum(row['jitter_prediction_extras']):3} "
                f"clean {row['clean_stable_errors']:2} detects {row['clean_change_detected']} "
                f"adapts {row['clean_change_recovered']}")
if __name__=="__main__":main()
