from __future__ import annotations

from typing import Any
from scheduler.core import Process, build_result, ResultList


def fcfs(processes: list[Process]) -> ResultList:
    """First-Come, First-Served CPU Scheduling."""
    ordered = sorted([p.copy() for p in processes], key=lambda p: (p.arrival_time, p.pid))
    current_time = 0.0
    results: list[dict[str, Any]] = []
    timeline: list[dict[str, Any]] = []

    for process in ordered:
        if current_time < process.arrival_time:
            timeline.append({"pid": "IDLE", "start": current_time, "end": process.arrival_time})
            current_time = process.arrival_time

        start_time = current_time
        completion_time = start_time + process.burst_time
        results.append(build_result(process, start_time, completion_time, context_switches=0))
        timeline.append({"pid": process.pid, "start": start_time, "end": completion_time})
        current_time = completion_time

    results.sort(key=lambda item: item["pid"])
    return ResultList(results, timeline=timeline)