from scheduler.core import Process
from scheduler.fcfs import fcfs


def test_fcfs_basic():
    processes = [
        Process("P1", 0, 5),
        Process("P2", 1, 3),
        Process("P3", 2, 8),
    ]

    results = fcfs(processes)

    assert results[0]["pid"] == "P1"
    assert results[1]["pid"] == "P2"
    assert results[2]["pid"] == "P3"

    assert results[0]["waiting_time"] == 0
    assert results[1]["waiting_time"] == 4
    assert results[2]["waiting_time"] == 6

    assert results[0]["turnaround_time"] == 5
    assert results[1]["turnaround_time"] == 7
    assert results[2]["turnaround_time"] == 14


def test_sjf_basic():
    from scheduler.sjf import sjf

    processes = [
        Process("P1", 0, 5),
        Process("P2", 1, 3),
        Process("P3", 2, 8),
    ]

    results = sjf(processes)

    assert [r["pid"] for r in results] == ["P1", "P2", "P3"]
    assert results[0]["waiting_time"] == 0
    assert results[1]["waiting_time"] == 4
    assert results[2]["waiting_time"] == 6


def test_priority_basic():
    from scheduler.priority import priority

    processes = [
        Process("P1", 0, 5, priority=2),
        Process("P2", 1, 3, priority=1),
        Process("P3", 2, 8, priority=3),
    ]

    results = priority(processes)

    assert [r["pid"] for r in results] == ["P1", "P2", "P3"]
    assert results[0]["priority"] == 2
    assert results[1]["priority"] == 1


def test_round_robin_basic():
    from scheduler.round_robin import round_robin

    processes = [
        Process("P1", 0, 5),
        Process("P2", 1, 3),
        Process("P3", 2, 8),
    ]

    results = round_robin(processes, quantum=2)

    assert len(results) == 3
    assert {r["pid"] for r in results} == {"P1", "P2", "P3"}
    assert all("completion_time" in r for r in results)