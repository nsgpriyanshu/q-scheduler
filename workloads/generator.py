from __future__ import annotations

import random
from scheduler.core import Process


def generate_preset_workload(preset_name: str, seed: int = 42) -> list[Process]:
    """Generate preset process workloads based on scenario types."""
    rng = random.Random(seed)

    if preset_name == "CPU-Bound Heavy":
        # Long CPU bursts, few processes arriving together
        return [
            Process("P1", arrival_time=0.0, burst_time=18.0, priority=3, io_burst=1.0),
            Process("P2", arrival_time=2.0, burst_time=24.0, priority=2, io_burst=0.5),
            Process("P3", arrival_time=4.0, burst_time=15.0, priority=4, io_burst=1.0),
            Process("P4", arrival_time=5.0, burst_time=30.0, priority=1, io_burst=2.0),
            Process("P5", arrival_time=8.0, burst_time=12.0, priority=3, io_burst=0.0),
        ]
    elif preset_name == "I/O-Bound Interactive":
        # Short burst times, high IO, rapid arrivals
        return [
            Process("P1", arrival_time=0.0, burst_time=3.0, priority=2, io_burst=8.0),
            Process("P2", arrival_time=1.0, burst_time=2.0, priority=1, io_burst=10.0),
            Process("P3", arrival_time=1.5, burst_time=4.0, priority=3, io_burst=6.0),
            Process("P4", arrival_time=2.0, burst_time=1.5, priority=2, io_burst=12.0),
            Process("P5", arrival_time=3.0, burst_time=3.5, priority=1, io_burst=9.0),
            Process("P6", arrival_time=4.0, burst_time=2.5, priority=4, io_burst=7.0),
        ]
    elif preset_name == "Bursty Mixed":
        # High variance in burst times (mix of tiny & huge tasks)
        return [
            Process("P1", arrival_time=0.0, burst_time=2.0, priority=3, io_burst=1.0),
            Process("P2", arrival_time=1.0, burst_time=22.0, priority=2, io_burst=2.0),
            Process("P3", arrival_time=2.0, burst_time=3.0, priority=1, io_burst=1.0),
            Process("P4", arrival_time=3.0, burst_time=28.0, priority=4, io_burst=3.0),
            Process("P5", arrival_time=4.0, burst_time=1.0, priority=2, io_burst=0.5),
            Process("P6", arrival_time=6.0, burst_time=5.0, priority=3, io_burst=1.0),
        ]
    elif preset_name == "Priority Skewed":
        # Diverse priorities, crucial for testing priority preemption
        return [
            Process("P1", arrival_time=0.0, burst_time=10.0, priority=4, io_burst=1.0),
            Process("P2", arrival_time=1.0, burst_time=6.0, priority=1, io_burst=0.0),  # High prio
            Process("P3", arrival_time=2.0, burst_time=14.0, priority=5, io_burst=2.0), # Low prio
            Process("P4", arrival_time=3.0, burst_time=4.0, priority=2, io_burst=1.0),
            Process("P5", arrival_time=6.0, burst_time=8.0, priority=1, io_burst=0.0),  # High prio
        ]
    elif preset_name == "Uniform Balanced":
        # Equal burst times and steady arrival steps
        return [
            Process(f"P{i+1}", arrival_time=float(i * 2), burst_time=8.0, priority=2, io_burst=1.0)
            for i in range(5)
        ]
    else:  # Standard default benchmark
        return [
            Process("P1", arrival_time=0.0, burst_time=7.0, priority=3),
            Process("P2", arrival_time=2.0, burst_time=4.0, priority=1),
            Process("P3", arrival_time=4.0, burst_time=1.0, priority=4),
            Process("P4", arrival_time=5.0, burst_time=4.0, priority=2),
        ]


def generate_random_workload(
    count: int = 6,
    arrival_max: float = 10.0,
    burst_min: float = 1.0,
    burst_max: float = 20.0,
    seed: int = 42,
) -> list[Process]:
    """Generate a pseudo-random workload with configurable bounds."""
    rng = random.Random(seed)
    processes = []

    for i in range(count):
        pid = f"P{i+1}"
        arrival = round(rng.uniform(0, arrival_max), 1)
        burst = round(rng.uniform(burst_min, burst_max), 1)
        prio = rng.randint(1, 5)
        io_b = round(rng.uniform(0, burst * 0.5), 1)
        processes.append(
            Process(pid=pid, arrival_time=arrival, burst_time=burst, priority=prio, io_burst=io_b)
        )

    processes.sort(key=lambda p: p.arrival_time)
    return processes
