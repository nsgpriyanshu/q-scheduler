from __future__ import annotations

from collections import deque
from typing import Any
from scheduler.core import Process, ResultList


def round_robin(processes: list[Process], quantum: float = 2.0) -> ResultList:
    """Round Robin CPU scheduling with timeline tracking."""
    if quantum <= 0:
        raise ValueError("Quantum must be positive")

    procs = [p.copy() for p in processes]
    procs.sort(key=lambda p: (p.arrival_time, p.pid))
    
    current_time = 0.0
    ready_queue: deque[Process] = deque()
    unallocated = list(procs)
    
    completed: list[dict[str, Any]] = []
    timeline: list[dict[str, Any]] = []
    first_start: dict[str, float] = {}
    context_switches: dict[str, int] = {p.pid: 0 for p in procs}

    while unallocated and unallocated[0].arrival_time <= current_time:
        ready_queue.append(unallocated.pop(0))

    last_pid: str | None = None

    while ready_queue or unallocated:
        if not ready_queue:
            current_time = unallocated[0].arrival_time
            while unallocated and unallocated[0].arrival_time <= current_time:
                ready_queue.append(unallocated.pop(0))

        current_proc = ready_queue.popleft()

        if current_proc.pid not in first_start:
            first_start[current_proc.pid] = current_time

        if last_pid is not None and last_pid != current_proc.pid:
            context_switches[current_proc.pid] += 1

        last_pid = current_proc.pid

        exec_time = min(quantum, current_proc.remaining_time)
        start_t = current_time
        current_time += exec_time
        current_proc.remaining_time -= exec_time

        timeline.append({"pid": current_proc.pid, "start": start_t, "end": current_time})

        while unallocated and unallocated[0].arrival_time <= current_time:
            ready_queue.append(unallocated.pop(0))

        if current_proc.remaining_time > 1e-9:
            ready_queue.append(current_proc)
        else:
            comp_t = current_time
            turnaround_t = comp_t - current_proc.arrival_time
            waiting_t = turnaround_t - current_proc.burst_time
            response_t = first_start[current_proc.pid] - current_proc.arrival_time

            completed.append(
                {
                    "pid": current_proc.pid,
                    "arrival_time": current_proc.arrival_time,
                    "burst_time": current_proc.burst_time,
                    "priority": current_proc.priority,
                    "start_time": first_start[current_proc.pid],
                    "completion_time": comp_t,
                    "waiting_time": max(0.0, waiting_t),
                    "turnaround_time": max(0.0, turnaround_t),
                    "response_time": max(0.0, response_t),
                    "context_switches": context_switches[current_proc.pid],
                }
            )

    completed.sort(key=lambda item: item["pid"])
    return ResultList(completed, timeline=timeline)
