from __future__ import annotations

from typing import Any
from scheduler.core import Process, build_result, ResultList


def sjf(processes: list[Process]) -> ResultList:
    """Shortest Job First non-preemptive scheduling."""
    ready = [p.copy() for p in processes]
    current_time = 0.0
    results: list[dict[str, Any]] = []
    timeline: list[dict[str, Any]] = []

    while ready:
        available = [p for p in ready if p.arrival_time <= current_time]
        if not available:
            next_process = min(ready, key=lambda p: (p.arrival_time, p.pid))
            timeline.append({"pid": "IDLE", "start": current_time, "end": next_process.arrival_time})
            current_time = next_process.arrival_time
            available = [p for p in ready if p.arrival_time <= current_time]

        chosen = min(available, key=lambda p: (p.burst_time, p.arrival_time, p.pid))
        ready.remove(chosen)

        if current_time < chosen.arrival_time:
            current_time = chosen.arrival_time

        start_time = current_time
        completion_time = start_time + chosen.burst_time
        results.append(build_result(chosen, start_time, completion_time, context_switches=0))
        timeline.append({"pid": chosen.pid, "start": start_time, "end": completion_time})
        current_time = completion_time

    results.sort(key=lambda item: item["pid"])
    return ResultList(results, timeline=timeline)
