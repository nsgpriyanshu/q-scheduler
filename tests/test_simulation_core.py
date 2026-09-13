from scheduler.core import Process, compare_schedulers, summarize_results
from scheduler.fcfs import fcfs


def test_process_model_and_summary_metrics():
    processes = [
        Process("P1", 0, 5),
        Process("P2", 1, 3),
        Process("P3", 2, 8),
    ]

    result = fcfs(processes)
    summary = summarize_results(result)

    assert result[0]["pid"] == "P1"
    assert result[1]["waiting_time"] == 4
    assert result[2]["turnaround_time"] == 14
    assert summary["avg_waiting_time"] == 10 / 3
    assert summary["avg_turnaround_time"] == 26 / 3
    assert summary["avg_response_time"] == 10 / 3


def test_compare_schedulers_on_same_workload():
    processes = [
        Process("P1", 0, 5),
        Process("P2", 1, 3),
        Process("P3", 2, 8),
    ]

    metrics = compare_schedulers({"fcfs": fcfs}, processes)

    assert set(metrics.keys()) == {"fcfs"}
    assert metrics["fcfs"]["avg_waiting_time"] == 10 / 3
    assert metrics["fcfs"]["avg_turnaround_time"] == 26 / 3
