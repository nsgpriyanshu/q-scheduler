from __future__ import annotations

from typing import Any
from scheduler.core import Process, ResultList


def srtf(processes: list[Process], context_switch_cost: float = 0.0) -> ResultList:
    """Shortest Remaining Time First (SRTF) Preemptive CPU Scheduling."""
    procs = [p.copy() for p in processes]
    n = len(procs)
    completed_count = 0
    current_time = 0.0

    timeline: list[dict[str, Any]] = []
    first_start: dict[str, float] = {}
    completion_times: dict[str, float] = {}
    context_switches: dict[str, int] = {p.pid: 0 for p in procs}

    active_proc: Process | None = None

    while completed_count < n:
        arrived = [p for p in procs if p.arrival_time <= current_time and p.remaining_time > 0]

        if not arrived:
            future_arrivals = [p.arrival_time for p in procs if p.remaining_time > 0]
            if future_arrivals:
                next_time = min(future_arrivals)
                timeline.append({"pid": "IDLE", "start": current_time, "end": next_time})
                current_time = next_time
            continue

        chosen = min(arrived, key=lambda p: (p.remaining_time, p.arrival_time, p.pid))

        if active_proc is not None and active_proc.pid != chosen.pid:
            context_switches[chosen.pid] += 1
            current_time += context_switch_cost

        if chosen.pid not in first_start:
            first_start[chosen.pid] = current_time

        active_proc = chosen

        future_arrivals = [p.arrival_time for p in procs if p.arrival_time > current_time and p.remaining_time > 0]
        if future_arrivals:
            next_arrival = min(future_arrivals)
            time_slice = min(chosen.remaining_time, next_arrival - current_time)
            time_slice = max(1.0, time_slice) if time_slice <= 0 else time_slice
        else:
            time_slice = chosen.remaining_time

        start_t = current_time
        current_time += time_slice
        chosen.remaining_time -= time_slice

        timeline.append({"pid": chosen.pid, "start": start_t, "end": current_time})

        if chosen.remaining_time <= 1e-9:
            chosen.remaining_time = 0.0
            completion_times[chosen.pid] = current_time
            completed_count += 1
            active_proc = None

    results: list[dict[str, Any]] = []
    for p in processes:
        comp_t = completion_times[p.pid]
        start_t = first_start[p.pid]
        turnaround_t = comp_t - p.arrival_time
        waiting_t = turnaround_t - p.burst_time
        response_t = start_t - p.arrival_time

        results.append(
            {
                "pid": p.pid,
                "arrival_time": p.arrival_time,
                "burst_time": p.burst_time,
                "priority": p.priority,
                "start_time": start_t,
                "completion_time": comp_t,
                "waiting_time": max(0.0, waiting_t),
                "turnaround_time": max(0.0, turnaround_t),
                "response_time": max(0.0, response_t),
                "context_switches": context_switches[p.pid],
            }
        )

    results.sort(key=lambda item: item["pid"])
    return ResultList(results, timeline=timeline)
