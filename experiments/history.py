"""GoldSol H1: does a native 1.6 GN relay's input-response band depend on recent history?

Uses the original unmodified GN27 net. A control relay is given the same
settle duration and probe, but no conditioning beats. The conditioned relay
gets identical-magnitude -10 two-tick pulses at prespecified prior times.
A counterfactual swaps its 50-tick history with the quiet control's history
while preserving the four-tick pipeline, to localize cause of any difference.

The history-swap is a causal laboratory ablation, NOT proposed native wiring.
"""
from __future__ import annotations
import copy,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from gn27 import Net, RELAY, settle

MAGNITUDES=(-14,-13.5,-13,-12.5,-12,-11.5,-11,-10.5,-10,-9.5,-9,-8.5,-8,-7.5)
GAPS=(2,4,8,16,32,64)
# The last conditioning pulse starts at t=72 and lasts through t=73.
HISTORIES={
 "quiet":(),
 "train_8":tuple(range(24,73,8)),
 "train_12":tuple(range(24,73,12)),
 "train_16":tuple(range(24,73,16)),
 "single":(72,)
}

def probe(net,mag):
    """First beat in next 18 ticks, and complete readout trace."""
    onsets=[];own_trace=[];prev=True
    for t in range(20):
        sp=np.array([mag if t<2 else 0.])
        own=float(net.step(sp_ext=sp)[0])
        loud=own>3
        if loud and not prev:onsets.append(t)
        prev=loud
        own_trace.append(round(own,6))
    return {"beats":onsets,"peak":max(own_trace),
            "trace":own_trace}

def make_state(base,starts,gap):
    net=copy.deepcopy(base)
    end=74+gap
    active={k for s in starts for k in (s,s+1)}
    for t in range(end):
        net.step(sp_ext=np.array([-10.0 if t in active else 0.]))
    return net

def trial(base,history,gap,mag):
    quiet=make_state(base,(),gap)
    conditioned=make_state(base,HISTORIES[history],gap)
    q_before={"quiet":int(quiet.q[0]),"conditioned":int(conditioned.q[0])}
    variance_before={"quiet":float(quiet.var[0]),"conditioned":float(conditioned.var[0])}
    hybrid=copy.deepcopy(conditioned)
    hybrid.hist[:]=quiet.hist
    hybrid.count=quiet.count
    pipe_hybrid=copy.deepcopy(conditioned)
    pipe_hybrid.pipe[:]=quiet.pipe
    # In all three, the same probe input is applied, no direct output edit.
    a=probe(quiet,mag)
    b=probe(conditioned,mag)
    c=probe(hybrid,mag)
    p=probe(pipe_hybrid,mag)
    return {
      "control_beats":a["beats"],"history_beats":b["beats"],
      "hybrid_beats":c["beats"],"pipe_swapped_beats":p["beats"],
      "control_peak":round(a["peak"],5),
      "history_peak":round(b["peak"],5),
      "hybrid_peak":round(c["peak"],5),
      "pipe_swapped_peak":round(p["peak"],5),
      "pre_q":q_before,
      "pre_variance":{k:round(v,6) for k,v in variance_before.items()},
      "changed_firing":bool(a["beats"])!=bool(b["beats"]),
      "changed_onset":a["beats"]!=b["beats"],
      "history_swap_recovered_baseline":c["beats"]==a["beats"],
      "pipe_swap_recovered_baseline":p["beats"]==a["beats"]
    }

def sweep():
    base=settle(Net([RELAY]))
    cases=[]
    for name in ("single","train_8","train_12","train_16"):
        for gap in GAPS:
            for mag in MAGNITUDES:
                row=trial(base,name,gap,mag)
                row.update({"history":name,"gap":gap,"probe":mag})
                cases.append(row)
    differ=[x for x in cases if x["changed_firing"]]
    time=[x for x in cases if x["changed_onset"]]
    return {
      "protocol":"Unchanged GN27 relay c=1.6; matched quiet control; 2-tick -10 conditioning beats; history-swap causal ablation",
      "n_cases":len(cases),
      "different_firing":len(differ),
      "different_onset":len(time),
      "swap_restores_baseline_when_changed":sum(x["history_swap_recovered_baseline"] for x in time),
      "pipe_swap_restores_baseline_when_changed":sum(x["pipe_swap_recovered_baseline"] for x in time),
      "examples":time[:35],
      "all_cases":cases
    }

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--output",default="-")
    args=p.parse_args()
    result=sweep()
    doc=json.dumps(result,indent=2)
    if args.output=="-":print(doc)
    else:
        out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(doc+"\n")
        print("Wrote",out)
    print(f"History responses: {result['different_firing']}/{result['n_cases']} firing changed, "
          f"{result['different_onset']} onset changed, "
          f"{result['swap_restores_baseline_when_changed']} history swaps, "
          f"{result['pipe_swap_restores_baseline_when_changed']} pipe swaps matched quiet response")
    for row in result["examples"][:15]:
        print("DIFF",row["history"],row["gap"],row["probe"],
              row["control_beats"],row["history_beats"],"hist_swap",row["hybrid_beats"],
              "pipe_swap",row["pipe_swapped_beats"],
              "q",row["pre_q"],"var",row["pre_variance"])
