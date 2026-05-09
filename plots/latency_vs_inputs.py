#!/usr/bin/env python3
"""
Plot: Latency vs. Number of Inputs for Async Perceptron
-------------------------------------------------------
Reads data/results.csv and produces figures/latency_vs_inputs.pdf

Usage:
    python3 plots/latency_vs_inputs.py

CSV format expected:
    n_inputs,weights,test_inputs,expected_sum,threshold,expected_output,actual_output,latency_steps
"""

import csv
import matplotlib.pyplot as plt
import os

# ─── Config ──────────────────────────────────────────────────────────────────
CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'results.csv')
OUT_DIR  = os.path.join(os.path.dirname(__file__), '..', 'report', 'figures')
OUT_FILE = os.path.join(OUT_DIR, 'latency_vs_inputs.pdf')

# ─── Read data ───────────────────────────────────────────────────────────────
n_values = []
latency_values = []

with open(CSV_PATH, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        n = int(row['n_inputs'])
        latency = int(row['latency_steps'])
        n_values.append(n)
        latency_values.append(latency)

print(f"Loaded {len(n_values)} data points:")
for n, lat in zip(n_values, latency_values):
    print(f"  N={n}: {lat} steps")

# ─── Plot ────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(5, 3.5))

ax.plot(n_values, latency_values, 'o-', color='#2563eb', linewidth=2, markersize=8, 
        markerfacecolor='#3b82f6', markeredgecolor='#1d4ed8', markeredgewidth=1.5)

# Annotate each point
for n, lat in zip(n_values, latency_values):
    ax.annotate(f'{lat}', (n, lat), textcoords="offset points", 
                xytext=(0, 12), ha='center', fontsize=9, color='#1e3a5f')

ax.set_xlabel('Number of Inputs ($N$)', fontsize=11)
ax.set_ylabel('Latency (simulation steps)', fontsize=11)
ax.set_title('End-to-End Latency vs. Input Count', fontsize=12, fontweight='bold')

ax.set_xticks(n_values)
ax.grid(True, alpha=0.3, linestyle='--')
ax.set_xlim(min(n_values) - 0.5, max(n_values) + 0.5)

# Add a bit of margin above highest point
y_margin = max(latency_values) * 0.15
ax.set_ylim(0, max(latency_values) + y_margin)

fig.tight_layout()

# ─── Save ────────────────────────────────────────────────────────────────────
os.makedirs(OUT_DIR, exist_ok=True)
fig.savefig(OUT_FILE, dpi=300, bbox_inches='tight')
print(f"\nSaved: {OUT_FILE}")

# Also save PNG for quick preview
fig.savefig(OUT_FILE.replace('.pdf', '.png'), dpi=150, bbox_inches='tight')
print(f"Saved: {OUT_FILE.replace('.pdf', '.png')}")

plt.close()
