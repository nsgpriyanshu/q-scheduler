from __future__ import annotations

from typing import Any
from ai.classifier import classify_workload
from scheduler.core import Process, ResultList
from scheduler.fcfs import fcfs
from scheduler.sjf import sjf
from scheduler.srtf import srtf
from scheduler.priority import priority
from scheduler.priority_preemptive import priority_preemptive
from scheduler.round_robin import round_robin


def adaptive_scheduler(processes: list[Process]) -> ResultList:
    """Adaptive CPU Scheduler (Q-Scheduler).

    Analyzes workload features, predicts the optimal scheduling policy,
    and executes it with tuned parameters.
    """
    proc_copies = [p.copy() for p in processes]
    classification = classify_workload(proc_copies)
    policy_name = classification["selected_policy"]
    quantum = classification["dynamic_quantum"]

    if policy_name == "SRTF":
        res = srtf(proc_copies)
    elif policy_name == "Priority Preemptive":
        res = priority_preemptive(proc_copies)
    elif policy_name == "Round Robin":
        res = round_robin(proc_copies, quantum=quantum)
    elif policy_name == "SJF":
        res = sjf(proc_copies)
    elif policy_name == "Priority":
        res = priority(proc_copies)
    else:
        res = fcfs(proc_copies)

    return ResultList(
        res,
        timeline=res.timeline,
        policy_used=policy_name,
        classification=classification,
    )
