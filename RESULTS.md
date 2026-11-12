# GoldSol — measured results, 12 November 2026

Status: **completed first J1/H1 experiment and causal follow-up**. The complete deterministic output is generated in GitHub Actions as results/jitter.json and results/history.json. No result here establishes improved jitter tolerance from GN27's slow state.

## What is being compared

The same 10-node one-wire architecture: one world-input relay, eight ring relays (32 ticks per revolution), one unsigned XOR receiver whose output feeds ring node 3. Original GN27 and Opus's checkerboard-free window neuron are the two fixed baselines. All native GN27 equations and original tap table remain unchanged.

Experiment J1 adds ONLY a causal previous-step readout to the original GN's comparator signal_in channel, using chosen gains. This extra route is implemented in the experiment harness; it is not itself a native GN27 graph edge. No external circuit calculates the Boolean mismatch.

### J1: selected held-out results

For each jittered run: 22 laps, three nominal world phases 0, 12, 20, warm-up of six laps. Four held-out random seeds (101, 103, 107, 109). Shown as **mean error spikes per run** and **total missed/extra predicted beats summed across four runs**, with ±1-tick tolerance for matching source and prediction.

| Model / added signal_in route | ±1 jitter: error mean | ±1: missed / extra | ±2 jitter: error mean | ±2: missed / extra |
|---|---:|---:|---:|---:|
| GN27 unchanged | 52.0 | 34 / 35 | 60.5 | 80 / 79 |
| Window control | 50.0 | 36 / 38 | 60.8 | 81 / 82 |
| GN, world wire +0.25 | 50.0 | 35 / 35 | 59.5 | 82 / 78 |
| GN, world wire −0.25 | 50.2 | 38 / 38 | 60.0 | 82 / 81 |
| GN, world wire +0.75 | 50.2 | 35 / 35 | 59.8 | 82 / 78 |
| GN, world wire −0.75 | **43.8** | **37 / 36** | 59.5 | 82 / 81 |
| GN, prediction wire +0.25 | 51.5 | 34 / 36 | 60.2 | 85 / 84 |
| GN, prediction wire −0.25 | 51.0 | 36 / 38 | 61.0 | 81 / 80 |
| GN, error wire +0.25 | 51.2 | 32 / 34 | 59.0 | 85 / 81 |
| GN, error wire −0.25 | 50.2 | 37 / 38 | 60.2 | 82 / 82 |
| GN, constant bias +0.20 | 50.2 | 40 / 39 | 59.0 | 83 / 79 |
| GN, constant bias −0.20 | 52.0 | 34 / 33 | 59.2 | 82 / 78 |

**Interpretation:** world-wire gain −0.75 sharply reduces error **spike count** for ±1 jitter but increases missing actual source events from 34 to 37 and extra predictions from 35 to 36. It does not deliver a predictive improvement under the joint criterion. Error-wire gain +0.25 produces small ±1 improvements in matching (32 missed/34 extra) but performs *worse* at ±2 (85 missed/81 extra), and is not established as a robust gain. None of these interventions consistently solves jitter across both noise levels.

Every tested setting retained zero post-warmup errors for the perfectly clean unchanging stream, and detected and ultimately adapted to a permanent phase-20 omission in the separate clean change control. **That control is necessary but insufficient**: a setting can pass it while struggling with jitter.

Development seeds were 11,19,23; held-out seeds were 101,103,107,109. No claim of statistical significance, exhaustive optimization, or generalization to new period lengths is made. These are deterministic simulator comparisons.

### H1: conditioning versus unchanged probe

Four conditioning histories (one -10 pulse or trains every 8, 12, 16 ticks), six gaps (2,4,8,16,32,64 ticks), 14 probe strengths (-14 to -7.5): **336 matched comparisons** against a quiet settled relay at Constant Signal 1.6.

- **12/336** conditioned probes changed whether the original GN unit fired, relative to its quiet control. Every difference occurred at gap 2 ticks, for probe strengths -13.5, -11 and -8 across each of the four conditioning histories.
- At gaps 4 through 64 ticks there were **0** differences in the observed firing/onset under this finite sweep.
- Replacing the conditioned unit's 50-tick variance history buffer with the quiet control's buffer restored its original quiet-control response in **0/12** changed cases.
- Replacing its **four-tick feedback pipeline** with the quiet control's pipeline restored the quiet-control response in **12/12** changed cases.

The branch-state history is not causing these measured differences. For the single-pulse case, the pre-probe variance was identical in both conditions (0.140625) and both were above 0.1. Train histories have different variance numbers but remain on the damp branch; the history swap did not repair the firing changes. Pre-probe square size q was 52 in both conditions for the 12 changed cases, even though the underlying pipeline values differ.

**Causal interpretation:** A short-lived GN state carried inside its four-tick feedback pipeline is necessary for the 12 observed probe differences in this intervention. Restoring the quiet pipeline is sufficient to abolish them, while exchanging the 50-tick history is not. This does **not** prove that GN has long-lived useful adaptive timing, or that the window neuron (which also has a four-step delay) cannot show related short-lag behavior. It also does not prove the 50-tick history never matters in other operating regimes (notably Constant Signal 1.0 clock mode).

### What this says about the apparent GN "flicker"

A c=1.6 GN receiver is not numerically static between beats, but GN-specific resting dynamics do not automatically yield an advantage. The isolated unit has state sensitivity at a two-tick recovery interval, and that sensitivity vanishes at the larger tested intervals. How exactly it changes the nonlinear firing-band boundary should be probed by matching the receiver's current internal phase/pipeline rather than attributing every disagreement to variance "fatigue".

It would be wrong to conclude from these results that (i) variance memory solves jitter, (ii) fewer discrepancy spikes imply more accurate prediction, or (iii) this particular relay-regime sensitivity is a new kind of temporal learning.

## Tests and files

- experiments/jitter.py: full development and held-out intervention matrix; machine-generated jitter.json
- experiments/history.py: 336 conditioning probes and two invasive state-swap ablations; machine-generated history.json
- tests/test_goldsol.py: clean-stream, omission control, deterministic seeds and explicit 12-case pipeline-vs-history regression
- Original gn27.py and taps.json remain unchanged; window.py copied unchanged from Opus
- GitHub Actions runs the small suite on CPU and uploads full JSON under the name goldsol-experimental-data.

## What would qualify as the next discovery?

A delay-independent, phase-tolerant mechanism should **beat the matched window control** in actual prediction accuracy on unseen jittered patterns, including an explicit permanent change, without merely suppressing the error readout. If the four-tick pipeline's residual state is to be exploited, design the experiment so that the same instantaneous input is probed at several controlled internal pipeline phases, then compare to a window unit given equal temporal memory and tuning budget.

There is a clean next *mechanism* test: map the receiver's firing probability over input amplitude versus the four pipeline coordinates, and ask whether phase-aware native gating stabilizes mismatch detection against ±1 tick jitter. That is a proposal, not a demonstrated outcome.
