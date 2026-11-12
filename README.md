# GoldSol — does the original geometric neuron earn its complexity?

**12 November 2026.** Independent scientific follow-up to the Opus/Sol/Gemini debate over GeometricNeuronV27, GN-XOR and the one-wire self-writing rhythm memory.

**The question here is deliberately harder than XOR:** Can the native GN27 slow state or its signal_in port improve a temporal prediction task compared with the minimal window neuron, without hiding mistakes by suppressing every error?

## Result of this first GoldSol round

**The targeted jitter rescue did not succeed.** Across 12 fixed choices (unchanged GN, window baseline, and 10 signal_in variants), none produced a consistent improvement in both prediction correspondence and discrepancy activity at held-out ±1/±2-tick jitter. For example, world-beat input routed into GN's signal_in at gain -0.75 reduced ±1 error spikes from 52.0 to 43.8 per run but increased cumulative source/prediction misses from 34 to 37 and extra predictions from 35 to 36. This is not a demonstrated predictive gain. Clean-stream behavior and permanent-omission detection remained functional.

**The isolated history test identified a real but short effect.** In 336 identical-probe comparisons, 12 firing outcomes differed after conditioning; all occurred at a two-tick recovery gap. Swapping the 50-tick variance history restored **0/12**, while swapping the four-tick internal feedback pipeline restored **12/12**. No measured firing differences appeared at gaps of four ticks or longer in this probe grid.

These are simulator results, not a proof that GN's history is universally short or that the checkerboard's only role is a fault. The four-tick pipeline also exists as an abstract delay in the matched window model, and no jitter advantage unique to GN27 has yet been demonstrated.

**[Read the measured results and causal limitations](RESULTS.md)** · [View the latest CI](https://github.com/anttiluode/GoldSol/actions)

## What is established before this repository

From [KultaaVaiKatinkultaa](https://github.com/anttiluode/KultaaVaiKatinkultaa) and [KultaaVaiKatinkultaaOpus](https://github.com/anttiluode/KultaaVaiKatinkultaaOpus):

- One native XOR error node feeding back to an 8-relay ring toggles remembered events: the same error pulse writes a missing slot or suppresses an obsolete one. 255/255 nonempty eight-slot, four-tick-grid patterns eventually settle.
- The 25-line checkerboard-free [window.py](window.py) relay reproduces the same 255/255 result. It is a serious control, not a competitor to dismiss.
- In Opus's 33-pattern benchmark, one-wire GN27 gets 31/33 memory-exact, signed-pair GN27 22/33; either circuit with the window model gets 33/33 on **memory versus emitted source**, although the original source fails to encode some requested close-spaced pulses.
- ±1 tick timing jitter destroys clean error silence.
- The nine-relay GN-only leak is **not caused by crossing the variance=0.1 damp/amplify boundary**: the switch was never observed in the measured interval, and forcing the damp branch didn't repair it.
- GN27's c=1.0 **autonomous clock** is a genuine capability absent from that particular window model (six beats spaced 59 ticks apart in 360 ticks), but it has not yet been turned into better jitter tolerance.

These are previous results, not outcomes claimed for GoldSol.

## GoldSol's two experiments

### J1 — Honest signal_in experiment

[experiments/jitter.py](experiments/jitter.py) holds the **one-wire XOR ring fixed**: eight relays, world source, XOR error comparator, 32-tick period, -6 ring and feedback edges, -4.5 comparator edges.

World streams have three events at phases 0, 12 and 20 per period. Over 22 laps, inputs receive separately seeded jitter of ±1 or ±2 ticks. Score only after six warm-up laps. **A real omission control** then permanently removes the phase-20 event at lap 12 of a clean input stream. An intervention that merely silences errors is a failure if it cannot detect and adapt to the omission.

Prespecified candidates route *existing previous-step beat wires* to the comparator's original signal_in port (the 50-tick history read channel), using gains ±0.25 and ±0.75 on the world wire, ±0.25 on prediction or error wires, and constant biases ±0.20. These are **external test-harness routes**, not built-in GN27 cable connections, not weight learning, and not evidence of a complete native physical circuit. No Boolean mismatch is computed in the routing. The rest of the GN27 equations and splitter samples remain unchanged.

Each setting is compared to unchanged GN27 and the unchanged window-neuron one-wire ring. Development seeds: 11, 19, 23; evaluation seeds: 101, 103, 107, 109. All settings are reported, not only the best. No iterative parameter tuning on the held-out seeds is intended.

Report the number of error spikes, world-to-memory coincidence misses (±1 tick tolerance), extra predictions, and whether the same architecture still detects and corrects a **real** permanent missing event. Low error activity alone is not a valid success criterion. We also test no-jitter stable input.

### H1 — Is the GN relay actually history dependent?

[experiments/history.py](experiments/history.py) uses a single native relay (c=1.6) and measures its response to **exactly the same two-tick test pulse** after different histories:

- quiet baseline;
- one prior -10 event;
- repeated -10 events every 8, 12 or 16 ticks;
- gaps of 2, 4, 8, 16, 32 or 64 ticks between conditioning and probe;
- 14 fixed test pulse strengths spanning -14 to -7.5.

It records readout spike/onset changes, current square size q and variance. **Two separate causal ablations** exchange either the conditioned relay's 50-tick history buffer or its four-tick feedback pipeline with the matching quiet relay. Neither swap is proposed as native wiring; both deliberately edit state for diagnosis.

If the conditioned and quiet units behave identically, that is evidence against useful history dependence in the tested relay range. When they differ, the two state swaps distinguish short feedback-pipeline effects from 50-tick history effects in the selected regime. They do not automatically establish a useful computational advantage.

## What counts as real gold?

A GN-specific timing mechanism must simultaneously:

1. Reduce false mismatch events or improve correspondence on held-out jittered streams.
2. Retain sensitivity to a genuinely changed world rhythm and successfully revise the memory.
3. Beat the unchanged GN27 one-wire circuit and a properly matched simple-window control under the same input budget.
4. Not rely on an externally computed error that secretly performs the learning operation.
5. Survive more than one convenient timing phase, pattern density, and random seed.

Even a positive result here is a **proof-of-mechanism in a simulator** until compared with a fair time-tolerant digital baseline and independently replicated. The original checkerboard's historical importance does not entitle it to an unmeasured advantage.

## Reproduce

Python 3.11+, NumPy. CPU only; no cloud model inference or training.

    pip install -r requirements.txt
    python -m unittest discover -s tests -v
    python experiments/jitter.py --output results/jitter.json
    python experiments/history.py --output results/history.json

The GitHub Actions job executes these commands and attaches the machine-generated result JSON. Source files gn27.py and taps.json were copied unchanged from the [Sol comparison repository](https://github.com/anttiluode/KultaaVaiKatinkultaa), which retained the V27 numerical core; window.py is the unchanged reference from Opus.

## Repositories and provenance

Original lineage: [GeometricNeuronSurfaceListener](https://github.com/anttiluode/GeometricNeuronSurfaceListener) → [GeometricNeuronV27](https://github.com/anttiluode/GeometricNeuronV27) → [GN-XOR](https://github.com/anttiluode/GN-XOR) → [KultaaVaiKatinkultaa (Sol)](https://github.com/anttiluode/KultaaVaiKatinkultaa) and [KultaaVaiKatinkultaaOpus (Opus)](https://github.com/anttiluode/KultaaVaiKatinkultaaOpus) → **GoldSol**.

The repository title is a challenge. Negative findings count as progress.
