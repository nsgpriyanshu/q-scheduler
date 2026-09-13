from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any
import numpy as np
import pandas as pd
from scheduler.core import Process


@dataclass
class WorkloadFeatureVector:
    num_processes: int
    mean_burst: float
    std_burst: float
    cv_burst: float
    priority_std: float
    priority_range: int
    arrival_span: float
    arrival_rate: float
    io_ratio: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "num_processes": self.num_processes,
            "mean_burst": self.mean_burst,
            "std_burst": self.std_burst,
            "cv_burst": self.cv_burst,
            "priority_std": self.priority_std,
            "priority_range": self.priority_range,
            "arrival_span": self.arrival_span,
            "arrival_rate": self.arrival_rate,
            "io_ratio": self.io_ratio,
        }

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([self.to_dict()])

    def to_numpy(self) -> np.ndarray:
        return np.array(list(self.to_dict().values()), dtype=float).reshape(1, -1)


def extract_workload_features(processes: list[Process]) -> WorkloadFeatureVector:
    """Extract statistical feature vector from a list of Process objects for ML model prediction."""
    if not processes:
        return WorkloadFeatureVector(0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.0)

    n = len(processes)
    bursts = [p.burst_time for p in processes]
    mean_burst = float(np.mean(bursts))
    std_burst = float(np.std(bursts, ddof=1)) if n > 1 else 0.0
    cv_burst = float(std_burst / mean_burst) if mean_burst > 0 else 0.0

    priorities = [p.priority for p in processes]
    priority_std = float(np.std(priorities, ddof=1)) if n > 1 else 0.0
    priority_range = int(max(priorities) - min(priorities))

    arrivals = [p.arrival_time for p in processes]
    arrival_span = float(max(arrivals) - min(arrivals))
    arrival_rate = float(n / arrival_span) if arrival_span > 0 else float(n)

    io_bursts = [p.io_burst for p in processes]
    mean_io = float(np.mean(io_bursts))
    io_ratio = float(mean_io / mean_burst) if mean_burst > 0 else 0.0

    return WorkloadFeatureVector(
        num_processes=n,
        mean_burst=round(mean_burst, 2),
        std_burst=round(std_burst, 2),
        cv_burst=round(cv_burst, 2),
        priority_std=round(priority_std, 2),
        priority_range=priority_range,
        arrival_span=round(arrival_span, 2),
        arrival_rate=round(arrival_rate, 2),
        io_ratio=round(io_ratio, 2),
    )
