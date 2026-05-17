"""
APEX-Sched — generate_dataset.py
Generates a synthetic process scheduling dataset with realistic distributions.

Workload types:
  cpu_heavy  — long bursts, low I/O, tight deadlines
  io_heavy   — short bursts, frequent I/O interrupts, relaxed deadlines
  mixed      — realistic blend of both

Each row = one scheduling decision snapshot.
Label = process index the SJF oracle would dispatch next.

Output: dataset.csv  (~12 000+ rows)
        dataset_stats.txt  (distribution summary)
"""

# pyrefly: ignore [missing-import]
import numpy as np
import pandas as pd
import random
import json
from collections import deque

SEED = 42
np.random.seed(SEED)
random.seed(SEED)

NUM_SCENARIOS   = 1200   # scheduling scenarios
MAX_PROCESSES   = 8      # max processes per scenario
MIN_PROCESSES   = 3
TICK_RESOLUTION = 1      # ms per tick


# ── Workload distributions ────────────────────────────────────────────────────

WORKLOAD_PROFILES = {
    "cpu_heavy": dict(
        burst_mu=3.0, burst_sigma=0.9,   # log-normal params → mean ~25 ms
        io_prob=0.10,                     # 10% chance I/O bound
        arrival_rate=0.4,                 # Poisson λ (processes/tick)
        deadline_slack_min=1.5,           # deadline = burst * slack
        deadline_slack_max=3.0,
        weight=0.35,
    ),
    "io_heavy": dict(
        burst_mu=1.6, burst_sigma=0.7,   # shorter bursts
        io_prob=0.75,
        arrival_rate=0.7,
        deadline_slack_min=3.0,
        deadline_slack_max=8.0,
        weight=0.30,
    ),
    "mixed": dict(
        burst_mu=2.2, burst_sigma=0.85,
        io_prob=0.40,
        arrival_rate=0.55,
        deadline_slack_min=2.0,
        deadline_slack_max=5.0,
        weight=0.35,
    ),
}


# ── Process generation ────────────────────────────────────────────────────────

def sample_burst(mu, sigma):
    """Log-normal burst time — always positive, right-skewed like real workloads."""
    return max(1, int(np.random.lognormal(mu, sigma)))


def generate_processes(profile_name, n_processes, start_tick=0):
    """
    Generate n_processes with arrival times following a Poisson process.
    Returns list of process dicts.
    """
    p = WORKLOAD_PROFILES[profile_name]
    processes = []
    tick = start_tick

    for pid in range(n_processes):
        inter_arrival = max(0, int(np.random.exponential(1.0 / p["arrival_rate"])))
        tick += inter_arrival

        burst = sample_burst(p["burst_mu"], p["burst_sigma"])
        io_bound = int(np.random.random() < p["io_prob"])

        # I/O bound processes have shorter effective bursts
        if io_bound:
            burst = max(1, burst // 2)

        slack = np.random.uniform(p["deadline_slack_min"], p["deadline_slack_max"])
        deadline = tick + int(burst * slack)

        processes.append({
            "pid":          f"P{pid+1}",
            "workload":     profile_name,
            "arrival_time": tick,
            "burst_time":   burst,
            "remaining_burst": burst,
            "io_bound":     io_bound,
            "deadline":     deadline,
            "priority":     random.randint(1, 5),   # static priority 1=highest
        })

    return processes


# ── SJF Oracle ────────────────────────────────────────────────────────────────

def sjf_oracle(ready_queue):
    """
    Non-preemptive SJF: pick the process with smallest remaining burst.
    Returns index in ready_queue of the chosen process.
    Tie-break: earliest arrival time, then lowest pid number.
    """
    if not ready_queue:
        return None
    chosen_idx = min(
        range(len(ready_queue)),
        key=lambda i: (
            ready_queue[i]["remaining_burst"],
            ready_queue[i]["arrival_time"],
            int(ready_queue[i]["pid"][1:]),
        )
    )
    return chosen_idx


# ── Feature engineering ───────────────────────────────────────────────────────

def compute_features(proc, current_tick, queue_depth, queue_avg_burst):
    """
    Derive engineered features for one process at a given tick.
    These are the features the ML model sees.
    """
    waiting_time      = max(0, current_tick - proc["arrival_time"])
    slack_time        = max(0, proc["deadline"] - current_tick)
    urgency_score     = (
        slack_time / proc["remaining_burst"]
        if proc["remaining_burst"] > 0 else 999.0
    )
    wait_ratio        = (
        waiting_time / (waiting_time + proc["remaining_burst"] + 1e-6)
    )
    burst_ratio       = (
        proc["remaining_burst"] / (queue_avg_burst + 1e-6)
    )
    deadline_pressure = 1.0 / (slack_time + 1)  # higher = more urgent

    return {
        "pid":               proc["pid"],
        "workload":          proc["workload"],
        "arrival_time":      proc["arrival_time"],
        "burst_time":        proc["burst_time"],
        "remaining_burst":   proc["remaining_burst"],
        "waiting_time":      waiting_time,
        "io_bound":          proc["io_bound"],
        "priority":          proc["priority"],
        "deadline":          proc["deadline"],
        "slack_time":        slack_time,
        "urgency_score":     round(urgency_score, 4),
        "wait_ratio":        round(wait_ratio, 4),
        "burst_ratio":       round(burst_ratio, 4),
        "deadline_pressure": round(deadline_pressure, 4),
        "queue_depth":       queue_depth,
        "queue_avg_burst":   round(queue_avg_burst, 2),
        "current_tick":      current_tick,
    }


# ── Scenario simulation ───────────────────────────────────────────────────────

_decision_counter = 0   # global unique decision ID


def simulate_scenario(profile_name, n_processes):
    """
    Simulate one scheduling scenario end-to-end.
    At each tick where a scheduling decision is made, record a row per
    ready process, marking which one the SJF oracle chose (label=1).

    Returns list of row dicts.
    """
    global _decision_counter
    processes   = generate_processes(profile_name, n_processes)
    tick        = 0
    completed   = []
    rows        = []
    arrived     = []
    pending     = sorted(processes, key=lambda p: p["arrival_time"])

    while pending or arrived:
        # Admit newly arrived processes into the ready queue
        while pending and pending[0]["arrival_time"] <= tick:
            arrived.append(pending.pop(0))

        if not arrived:
            # CPU idle — jump to next arrival
            tick = pending[0]["arrival_time"]
            continue

        # Compute queue stats for feature engineering
        queue_depth    = len(arrived)
        queue_avg_burst = np.mean([p["remaining_burst"] for p in arrived])

        # SJF oracle picks the next process
        chosen_idx = sjf_oracle(arrived)

        # Build one row per process in the ready queue
        decision_id = f"{profile_name}_d{_decision_counter:06d}"
        _decision_counter += 1
        for i, proc in enumerate(arrived):
            feat = compute_features(proc, tick, queue_depth, queue_avg_burst)
            feat["label"] = 1 if i == chosen_idx else 0
            feat["scenario_id"] = decision_id
            rows.append(feat)

        # Run chosen process for its full remaining burst (non-preemptive)
        chosen = arrived.pop(chosen_idx)
        tick  += chosen["remaining_burst"]
        chosen["remaining_burst"]   = 0
        chosen["completion_time"]   = tick
        chosen["turnaround_time"]   = tick - chosen["arrival_time"]
        chosen["actual_wait_time"]  = chosen["turnaround_time"] - chosen["burst_time"]
        completed.append(chosen)

    return rows, completed


# ── Build full dataset ────────────────────────────────────────────────────────

def build_dataset(num_scenarios=NUM_SCENARIOS):
    all_rows = []
    profiles = list(WORKLOAD_PROFILES.keys())
    weights  = [WORKLOAD_PROFILES[p]["weight"] for p in profiles]

    print(f"Generating {num_scenarios} scenarios...")

    for i in range(num_scenarios):
        profile    = random.choices(profiles, weights=weights)[0]
        n_procs    = random.randint(MIN_PROCESSES, MAX_PROCESSES)
        rows, _    = simulate_scenario(profile, n_procs)
        all_rows.extend(rows)

        if (i + 1) % 200 == 0:
            print(f"  {i+1}/{num_scenarios} done  ({len(all_rows):,} rows so far)")

    df = pd.DataFrame(all_rows)

    # Reorder columns cleanly
    col_order = [
        "scenario_id", "workload", "pid", "current_tick",
        "arrival_time", "burst_time", "remaining_burst",
        "waiting_time", "io_bound", "priority", "deadline",
        "slack_time", "urgency_score", "wait_ratio", "burst_ratio",
        "deadline_pressure", "queue_depth", "queue_avg_burst",
        "label",
    ]
    df = df[col_order]
    return df


# ── Validation & stats ────────────────────────────────────────────────────────

def print_stats(df):
    lines = []
    lines.append("=" * 60)
    lines.append("APEX-Sched Dataset Summary")
    lines.append("=" * 60)
    lines.append(f"Total rows        : {len(df):,}")
    lines.append(f"Positive labels   : {df['label'].sum():,}  ({df['label'].mean()*100:.1f}%)")
    lines.append(f"Unique scenarios  : {df['scenario_id'].nunique():,}")
    lines.append("")
    lines.append("Workload distribution:")
    for wl, cnt in df["workload"].value_counts().items():
        lines.append(f"  {wl:<12} {cnt:>6,} rows  ({cnt/len(df)*100:.1f}%)")
    lines.append("")
    lines.append("Feature stats (positive label rows only):")
    pos = df[df["label"] == 1]
    for col in ["remaining_burst", "waiting_time", "urgency_score",
                "deadline_pressure", "queue_depth"]:
        lines.append(
            f"  {col:<22} mean={pos[col].mean():.3f}  std={pos[col].std():.3f}"
            f"  min={pos[col].min():.1f}  max={pos[col].max():.1f}"
        )
    lines.append("")
    lines.append("I/O bound %  (all rows) :")
    lines.append(f"  {df['io_bound'].mean()*100:.1f}%")
    lines.append("=" * 60)

    report = "\n".join(lines)
    print(report)
    return report


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    df = build_dataset(NUM_SCENARIOS)

    out_csv  = "dataset.csv"
    out_stat = "dataset_stats.txt"

    df.to_csv(out_csv, index=False)
    print(f"\nSaved: {out_csv}  ({len(df):,} rows)")

    report = print_stats(df)
    with open(out_stat, "w") as f:
        f.write(report)
    print(f"Saved: {out_stat}")

    # Quick sanity check — every scenario must have exactly one label=1
    check = df.groupby("scenario_id")["label"].sum()
    bad   = (check != 1).sum()
    if bad == 0:
        print("\nSanity check PASSED — every decision snapshot has exactly one label.")
    else:
        print(f"\nWARNING: {bad} snapshots have != 1 label. Check oracle logic.")