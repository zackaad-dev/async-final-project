# Asynchronous Perceptron — CHP/ACT Implementation

An asynchronous hardware implementation of a single-layer perceptron using Communicating Hardware Processes (CHP) within the ACT toolset. Built for the 02211 Research Topics in Computer Architecture course at DTU.

## What This Is

A single perceptron unit that computes:

```
y = step( w₀·x₀ + w₁·x₁ + ... + wₙ·xₙ )
```

Each stage (input, weight multiplication, accumulation, thresholding, output) runs as an independent asynchronous process communicating via bundled-data channels. No global clock — each process fires when its input data arrives.

## Architecture

```
Source(x₀) → weight_mul → ┐
Source(x₁) → weight_mul → ┤
Source(x₂) → weight_mul → ┼→ accumulator → threshold → sink
Source(x₃) → weight_mul → ┤
  ...                      ┘
```

The accumulator uses a parallel receive across all weighted inputs, meaning it fires in a single synchronisation event regardless of how many inputs there are.

## Project Structure

```
async-final-project/
├── src/
│   ├── components.act       # source, sink, adder (from Lab 2)
│   ├── neuron.act            # weight_mul, accumulator, threshold
│   ├── top_n2.act            # End-to-end wiring, N=2
│   ├── top_n3.act            # N=3
│   ├── top_n4.act            # N=4
│   └── top_n5.act            # N=5
├── test/
│   ├── test_threshold.act    # Standalone threshold tests
│   ├── test_neuron_n2.act    # Full pipeline testbenches
│   └── test_neuron.scr       # actsim script (advance 100)
├── data/
│   └── results.csv           # Collected latency measurements
├── plots/
│   └── latency_vs_inputs.py  # Matplotlib plot script
├── report/
│   ├── main.tex              # IEEE-style report (scrartcl)
│   └── figures/
│       ├── latency_vs_inputs.pdf
│       └── latency_vs_inputs.png
├── devlog.md                 # Development log
└── README.md                 # This file
```

## Components

| Process         | Description                               | Channel Type |
| --------------- | ----------------------------------------- | ------------ |
| `source_val<V>` | Continuously emits constant value V       | `bd<8>`      |
| `weight_mul_1`  | Identity (×1)                             | `bd<8>`      |
| `weight_mul_2`  | Left shift (×2)                           | `bd<8>`      |
| `weight_mul_3`  | Shift-and-add (×3)                        | `bd<8>`      |
| `accumulator_N` | Parallel receive of N inputs, outputs sum | `bd<8>`      |
| `threshold<T>`  | Outputs 1 if input ≥ T, else 0            | `bd<8>`      |
| `sink`          | Logs received values                      | `bd<8>`      |

## Key Result

End-to-end latency is **constant at 40 simulation steps** for N=2 through N=5. The parallel receive in the accumulator means adding more inputs does not increase the number of sequential pipeline stages.

## Running

```bash
# Simulate a configuration (e.g. N=2)
actsim src/top_n2.act neuron_n2 < test/test_neuron.scr

# Generate the latency plot
cd plots && python3 latency_vs_inputs.py
```

## Test Configurations

| N   | Weights       | Inputs        | Expected Sum | Threshold | Output |
| --- | ------------- | ------------- | ------------ | --------- | ------ |
| 2   | 3, 1          | 2, 4          | 10           | 5         | 1      |
| 3   | 3, 1, 2       | 2, 4, 3       | 16           | 5         | 1      |
| 4   | 3, 1, 2, 1    | 2, 4, 3, 5    | 21           | 5         | 1      |
| 5   | 3, 1, 2, 1, 2 | 2, 4, 3, 5, 1 | 23           | 5         | 1      |

## Course

02211 Research Topics in Computer Architecture, Technical University of Denmark (DTU), Spring 2026.
