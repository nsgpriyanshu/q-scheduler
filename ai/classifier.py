from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any
from scheduler.core import Process


@dataclass
class WorkloadFeatures:
    num_processes: int
    mean_burst: float
    burst_std: float
    burst_cv: float
    io_ratio: float
    priority_std: float
    arrival_span: float


def extract_features(processes: list[Process]) -> WorkloadFeatures:
    """Extract workload characteristics and statistics."""
    if not processes:
        return WorkloadFeatures(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    n = len(processes)
    bursts = [p.burst_time for p in processes]
    mean_burst = sum(bursts) / n

    if n > 1:
        variance_burst = sum((b - mean_burst) ** 2 for b in bursts) / (n - 1)
        burst_std = math.sqrt(variance_burst)
    else:
        burst_std = 0.0

    burst_cv = (burst_std / mean_burst) if mean_burst > 0 else 0.0

    io_bursts = [p.io_burst for p in processes]
    mean_io = sum(io_bursts) / n
    io_ratio = (mean_io / mean_burst) if mean_burst > 0 else 0.0

    priorities = [p.priority for p in processes]
    mean_prio = sum(priorities) / n
    if n > 1:
        prio_var = sum((p - mean_prio) ** 2 for p in priorities) / (n - 1)
        priority_std = math.sqrt(prio_var)
    else:
        priority_std = 0.0

    arrivals = [p.arrival_time for p in processes]
    arrival_span = max(arrivals) - min(arrivals)

    return WorkloadFeatures(
        num_processes=n,
        mean_burst=round(mean_burst, 2),
        burst_std=round(burst_std, 2),
        burst_cv=round(burst_cv, 2),
        io_ratio=round(io_ratio, 2),
        priority_std=round(priority_std, 2),
        arrival_span=round(arrival_span, 2),
    )


def classify_workload(processes: list[Process]) -> dict[str, Any]:
    """Classify workload characteristics and return chosen policy with decision tree trace."""
    feats = extract_features(processes)

    decision_nodes = [
        {
            "id": "root",
            "name": "Workload Analyzer",
            "condition": f"Processes: {feats.num_processes}, Mean Burst: {feats.mean_burst}",
            "status": "evaluated",
        }
    ]

    # Rule 1: Priority Spread Check
    if feats.priority_std > 1.0:
        decision_nodes.append(
            {
                "id": "prio_branch",
                "name": "Priority Diversity Check",
                "condition": f"Priority Std ({feats.priority_std}) > 1.0",
                "result": "True -> High Priority Skew",
                "status": "selected",
            }
        )
        selected_policy = "Priority Preemptive"
        reasoning = f"High priority variation (std = {feats.priority_std:.2f}) requires priority preemption."
        dynamic_quantum = 2.0
    # Rule 2: High Burst Variation
    elif feats.burst_cv > 0.5:
        decision_nodes.append(
            {
                "id": "cv_branch",
                "name": "Burst Variance Check",
                "condition": f"Burst CV ({feats.burst_cv}) > 0.5",
                "result": "True -> Heterogeneous Bursts",
                "status": "selected",
            }
        )
        selected_policy = "SRTF"
        reasoning = f"High burst variation (CV = {feats.burst_cv:.2f}). SRTF minimizes queue delay for short tasks."
        dynamic_quantum = max(1.0, round(feats.mean_burst * 0.4, 1))
    # Rule 3: Interactive / I/O Heavy or Short Round Robin
    elif feats.io_ratio > 0.25 or feats.mean_burst <= 6.0:
        decision_nodes.append(
            {
                "id": "rr_branch",
                "name": "Responsiveness / Short Burst Check",
                "condition": f"I/O Ratio ({feats.io_ratio}) > 0.25 OR Mean Burst ({feats.mean_burst}) <= 6.0",
                "result": "True -> Interactive Workload",
                "status": "selected",
            }
        )
        selected_policy = "Round Robin"
        dynamic_quantum = max(1.0, round(feats.mean_burst * 0.5, 1))
        reasoning = f"Interactive/Short burst profile (Mean = {feats.mean_burst}). Round Robin with Quantum = {dynamic_quantum} selected."
    # Rule 4: Uniform / FCFS or SJF
    else:
        decision_nodes.append(
            {
                "id": "uniform_branch",
                "name": "Uniform Long Burst Check",
                "condition": "Low variance, low priority skew",
                "result": "True -> Homogeneous CPU-Bound",
                "status": "selected",
            }
        )
        selected_policy = "SJF"
        dynamic_quantum = 2.0
        reasoning = "Homogeneous CPU-bound workload. Non-preemptive Shortest Job First selected to minimize context switching."

    return {
        "features": feats,
        "selected_policy": selected_policy,
        "reasoning": reasoning,
        "dynamic_quantum": dynamic_quantum,
        "decision_tree": decision_nodes,
    }
