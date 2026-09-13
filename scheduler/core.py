from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Callable, Any, List


class ResultList(list):
    """Custom list subclass that holds timeline and metadata while behaving as a standard list."""
    def __init__(self, iterable=(), timeline: list[dict[str, Any]] | None = None, **kwargs):
        super().__init__(iterable)
        self.timeline: list[dict[str, Any]] = timeline if timeline is not None else []
        for k, v in kwargs.items():
            setattr(self, k, v)


@dataclass
class Process:
    pid: str
    arrival_time: float
    burst_time: float
    priority: int = 0
    io_burst: float = 0.0
    cpu_burst_history: list[float] = field(default_factory=list)
    remaining_time: float | None = None
    state: str = "ready"
    ready_time: float | None = None

    def __post_init__(self) -> None:
        self.arrival_time = float(self.arrival_time)
        self.burst_time = float(self.burst_time)
        self.priority = int(self.priority)
        self.io_burst = float(self.io_burst)
        if self.remaining_time is None:
            self.remaining_time = self.burst_time
        else:
            self.remaining_time = float(self.remaining_time)
        if self.ready_time is None:
            self.ready_time = self.arrival_time

    def copy(self) -> Process:
        return Process(
            pid=self.pid,
            arrival_time=self.arrival_time,
            burst_time=self.burst_time,
            priority=self.priority,
            io_burst=self.io_burst,
            cpu_burst_history=list(self.cpu_burst_history),
            remaining_time=self.burst_time,
            state="ready",
            ready_time=self.arrival_time,
        )


def build_result(process: Process, start_time: float, completion_time: float, context_switches: int = 0) -> dict[str, Any]:
    return {
        "pid": process.pid,
        "arrival_time": process.arrival_time,
        "burst_time": process.burst_time,
        "priority": process.priority,
        "io_burst": process.io_burst,
        "start_time": start_time,
        "completion_time": completion_time,
        "waiting_time": max(0.0, start_time - process.arrival_time),
        "turnaround_time": max(0.0, completion_time - process.arrival_time),
        "response_time": max(0.0, start_time - process.arrival_time),
        "context_switches": context_switches,
    }


def summarize_results(results: list[dict[str, Any]] | ResultList | dict[str, Any], timeline: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Compute aggregate performance metrics for a scheduler result list."""
    if isinstance(results, dict):
        timeline = results.get("timeline", timeline)
        results_list = results.get("results", [])
    else:
        results_list = results
        if timeline is None:
            timeline = getattr(results, "timeline", None)

    if not results_list:
        return {
            "count": 0,
            "avg_waiting_time": 0.0,
            "avg_turnaround_time": 0.0,
            "avg_response_time": 0.0,
            "max_waiting_time": 0.0,
            "total_burst_time": 0.0,
            "completion_time": 0.0,
            "cpu_utilization": 0.0,
            "throughput": 0.0,
            "total_context_switches": 0,
            "fairness_index": 1.0,
        }

    min_arrival = min(item["arrival_time"] for item in results_list)
    max_completion = max(item["completion_time"] for item in results_list)
    total_span = max(1e-6, max_completion - min_arrival)

    avg_waiting_time = sum(item["waiting_time"] for item in results_list) / len(results_list)
    avg_turnaround_time = sum(item["turnaround_time"] for item in results_list) / len(results_list)
    avg_response_time = sum(item["response_time"] for item in results_list) / len(results_list)
    max_waiting_time = max(item["waiting_time"] for item in results_list)
    total_burst_time = sum(item["burst_time"] for item in results_list)

    total_context_switches = sum(item.get("context_switches", 0) for item in results_list)
    if timeline:
        switches = 0
        last_pid = None
        for slice_info in timeline:
            if slice_info.get("pid") != last_pid and last_pid is not None and slice_info.get("pid") != "IDLE":
                switches += 1
            last_pid = slice_info.get("pid")
        total_context_switches = max(total_context_switches, switches)

    cpu_utilization = min(100.0, (total_burst_time / total_span) * 100.0)
    throughput = len(results_list) / total_span

    wait_times = [item["waiting_time"] for item in results_list]
    sum_w = sum(wait_times)
    sum_w_sq = sum(w ** 2 for w in wait_times)
    if sum_w_sq == 0:
        fairness_index = 1.0
    else:
        fairness_index = (sum_w ** 2) / (len(results_list) * sum_w_sq)

    return {
        "count": len(results_list),
        "avg_waiting_time": avg_waiting_time,
        "avg_turnaround_time": avg_turnaround_time,
        "avg_response_time": avg_response_time,
        "max_waiting_time": max_waiting_time,
        "total_burst_time": total_burst_time,
        "completion_time": max_completion,
        "cpu_utilization": round(cpu_utilization, 2),
        "throughput": round(throughput, 4),
        "total_context_switches": total_context_switches,
        "fairness_index": round(fairness_index, 3),
    }


def compare_schedulers(
    schedulers: dict[str, Callable[[list[Process]], Any]],
    processes: list[Process],
) -> dict[str, dict[str, Any]]:
    """Run several scheduler functions on copies of the workload and summarize them."""
    summary: dict[str, dict[str, Any]] = {}

    for name, scheduler in schedulers.items():
        proc_copies = [p.copy() for p in processes]
        res = scheduler(proc_copies)
        summary[name] = summarize_results(res)

    return summary
