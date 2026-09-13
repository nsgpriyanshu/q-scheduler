from __future__ import annotations

from typing import Any
import pandas as pd

from scheduler.core import Process, summarize_results
from scheduler.fcfs import fcfs
from scheduler.sjf import sjf
from scheduler.srtf import srtf
from scheduler.priority import priority
from scheduler.priority_preemptive import priority_preemptive
from scheduler.round_robin import round_robin


def run_target_simulations(processes: list[Process], quantum: float = 2.0) -> dict[str, dict[str, Any]]:
    """Run simulations for FCFS, SJF (Non-preemptive & Preemptive), Priority (Non-preemptive & Preemptive), and Round Robin."""
    schedulers = {
        "FCFS": lambda procs: fcfs(procs),
        "SJF (Non-preemptive)": lambda procs: sjf(procs),
        "SJF (Preemptive)": lambda procs: srtf(procs),
        "Priority (Non-preemptive)": lambda procs: priority(procs),
        "Priority (Preemptive)": lambda procs: priority_preemptive(procs),
        "Round Robin": lambda procs: round_robin(procs, quantum=quantum),
    }

    simulation_data: dict[str, dict[str, Any]] = {}

    for name, runner in schedulers.items():
        proc_copies = [p.copy() for p in processes]
        res = runner(proc_copies)
        
        if isinstance(res, dict):
            results = res.get("results", [])
            timeline = res.get("timeline", [])
        else:
            results = res
            timeline = getattr(res, "timeline", [])

        summary = summarize_results(results, timeline)
        
        simulation_data[name] = {
            "results": results,
            "timeline": timeline,
            "summary": summary,
        }

    return simulation_data


def run_all_simulations(processes: list[Process], quantum: float = 2.0) -> dict[str, dict[str, Any]]:
    """Backward compatible helper function for running simulations."""
    return run_target_simulations(processes, quantum=quantum)


def build_comparison_dataframe(simulations: dict[str, dict[str, Any]]) -> pd.DataFrame:
    """Build comparison DataFrame from simulation results."""
    rows = []
    for name, data in simulations.items():
        summary = data["summary"]
        rows.append(
            {
                "Algorithm": name,
                "Avg Waiting Time": summary["avg_waiting_time"],
                "Avg Turnaround Time": summary["avg_turnaround_time"],
                "Avg Response Time": summary["avg_response_time"],
                "CPU Utilization (%)": summary["cpu_utilization"],
                "Throughput (proc/sec)": summary["throughput"],
                "Context Switches": summary["total_context_switches"],
            }
        )

    return pd.DataFrame(rows)
