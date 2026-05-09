# devlog.md — Async Perceptron Project

---

## Session 1 — Project Setup & Lab 2 Integration

**Status:** ✅ Complete

### What happened

- Initialised repo (`async-final-project`)
- Ported `source`, `sink`, and `adder` from Lab 2 into `src/components.act`
- Ran standalone sanity tests for all three — verified they compile and simulate correctly in actsim

### Notes

- Lab 2 components required no changes — channel type `bd<8>` and CHP patterns carry over directly
- `adder` will be the backbone of the accumulator logic

---

## Session 2 — weight_mul Implementation

**Status:** ✅ Complete

### What happened

- Decided to start with small, manageable weights to keep shift-and-add trivial
- Implemented three variants:
  - `weight_mul_1` — identity (no shift needed, `R ! x`)
  - `weight_mul_2` — single left shift (`R ! (x << 1)`)
  - `weight_mul_3` — shift-and-add (`R ! ((x << 1) + x)`)

### Design decision

Shift-and-add chosen over a general multiplier to avoid complex hardware. Keeps the design in scope and is representative enough for the report.

### Parameters at this point

```
Weights available: 1, 2, 3
Channel type: bd<8>
```

---

## Session 3 — Accumulator Implementation

**Status:** ✅ Complete

### What happened

- Implemented two accumulator variants:
  - `accumulator_2` — parallel receive from 2 weighted inputs, sends sum
  - `accumulator_3` — parallel receive from 3 weighted inputs, sends sum
- Both use comma-separated receives to block until all inputs arrive simultaneously

### CHP pattern used

```act
*[ W0?w0, W1?w1 ; R!(w0+w1) ]   // N=2 example
```

### Notes

- Parallel receive is key to async correctness — accumulator does not fire until all weight_mul processes have produced output
- This is the behavior to highlight in the report under "async advantage"

---

## Session 4 — Testing weight_mul & Accumulator

**Status:** ✅ Tests passed

### What happened

- Wrote testbenches for `weight_mul_1`, `weight_mul_2`, `weight_mul_3`
- Wrote testbenches for `accumulator_2` and `accumulator_3`
- All sinks received expected values

### Verification

| Component     | Input   | Expected Output | Actual |
| ------------- | ------- | --------------- | ------ |
| weight_mul_1  | 5       | 5               | ✅     |
| weight_mul_2  | 5       | 10              | ✅     |
| weight_mul_3  | 5       | 15              | ✅     |
| accumulator_2 | 6, 4    | 10              | ✅     |
| accumulator_3 | 6, 4, 2 | 12              | ✅     |

---

## Session 5 — Dataflow Design & Threshold

**Status:** ✅ Complete

### What happened

- Designed full perceptron dataflow diagram
- Architecture: `source → weight_mul → accumulator → threshold → sink`
- Implemented threshold process with `pint T` parameter for easy reconfiguration:

```act
defproc threshold (pint T; bd<8> L, R) {
  int<8> x;
  chp {
    *[ L?x ; [ x >= T -> R ! 1 [] x < T -> R ! 0 ] ]
  }
}
```

- Tested threshold standalone: `source_val<10>` with `threshold<5>` → sink receives `1` ✅
- Added `accumulator_4` and `accumulator_5` following the same parallel-receive pattern

---

## Session 6 — End-to-End Wiring (top_n2 through top_n5)

**Status:** ✅ All configurations verified

### What happened

- Wired `top_n2.act` as the first end-to-end test
- Pipeline: sources → weight_muls → accumulator → threshold → sink
- Verified sink receives `1` — pipeline works end-to-end
- Repeated for `top_n3.act`, `top_n4.act`, `top_n5.act`

### Test configurations

| N   | Weights       | Inputs        | Expected Σ | Threshold | Output |
| --- | ------------- | ------------- | ---------- | --------- | ------ |
| 2   | 3, 1          | 2, 4          | 10         | 5         | 1 ✅   |
| 3   | 3, 1, 2       | 2, 4, 3       | 16         | 5         | 1 ✅   |
| 4   | 3, 1, 2, 1    | 2, 4, 3, 5    | 21         | 5         | 1 ✅   |
| 5   | 3, 1, 2, 1, 2 | 2, 4, 3, 5, 1 | 23         | 5         | 1 ✅   |

---

## Session 7 — Cycle Count Collection & Plot Generation

**Status:** ✅ Complete

### Measurement method

For each N ∈ {2, 3, 4, 5}:

1. Ran `actsim` with `advance 100` test script
2. Recorded the first simulation timestamp where the sink prints `Received: 1`
3. Used that timestamp as the end-to-end latency

### Results from actsim logs

```text
--- N=2 ---  [40] <sk> Received: 1
--- N=3 ---  [40] <sk> Received: 1
--- N=4 ---  [40] <sk> Received: 1
--- N=5 ---  [40] <sk> Received: 1
```

### Recorded data (`data/results.csv`)

```csv
n_inputs,weights,test_inputs,expected_sum,threshold,expected_output,actual_output,latency_steps
2,"3,1","2,4",10,5,1,1,40
3,"3,1,2","2,4,3",16,5,1,1,40
4,"3,1,2,1","2,4,3,5",21,5,1,1,40
5,"3,1,2,1,2","2,4,3,5,1",23,5,1,1,40
```

### Plot generation

```bash
./.venv/bin/pip install matplotlib
./.venv/bin/python3 plots/latency_vs_inputs.py
```

Generated `report/figures/latency_vs_inputs.pdf` and `latency_vs_inputs.png`.

### Key finding

Latency is **constant at 40 simulation steps** across all N=2..5. This is because the accumulator uses a parallel receive (comma-separated channels), so all weighted inputs are consumed in a single synchronisation event. Increasing N widens the parallel rendezvous but does not add sequential pipeline stages. The end-to-end latency is determined by pipeline depth (source → weight_mul → accumulator → threshold → sink), not pipeline width.

---

## TODO

- [ ] Add a test case where threshold output = 0 (sum < T)
- [ ] Add a boundary test case where sum = T exactly
- [ ] Consider a second plot: measured flat line vs. hypothetical sequential accumulation
- [ ] Write report (data-driven: anchor on plots, write around them)
- [ ] Build oral presentation slides
- [ ] Add references to report (ACT docs, async neural network hardware papers)
- [ ] Uncomment and include architecture diagram in LaTeX

---

## Parameters (final)

| Parameter            | Value                              |
| -------------------- | ---------------------------------- |
| Channel type         | `bd<8>`                            |
| Weights implemented  | 1, 2, 3                            |
| Threshold T          | 5 (configurable via `pint`)        |
| Accumulator variants | N=2, N=3, N=4, N=5                 |
| Synthesis target     | CHP simulation only (PRS deferred) |

---

## Reproduction

```bash
# Compile and simulate N=2 testbench
actsim test/test_neuron_n2.act neuron_n2

# Generate plot
./.venv/bin/python3 plots/latency_vs_inputs.py
```
