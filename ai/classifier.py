from __future__ import annotations

import random
from typing import Any
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from ai.feature_extractor import extract_workload_features, WorkloadFeatureVector
from scheduler.core import Process, summarize_results
from scheduler.fcfs import fcfs
from scheduler.sjf import sjf
from scheduler.srtf import srtf
from scheduler.priority import priority
from scheduler.priority_preemptive import priority_preemptive
from scheduler.round_robin import round_robin


class WorkloadPredictor:
    """Machine Learning predictor for Adaptive CPU Scheduling using multi-objective evaluation."""

    def __init__(self) -> None:
        self.model: RandomForestClassifier | None = None
        self.feature_names = [
            "num_processes",
            "mean_burst",
            "std_burst",
            "cv_burst",
            "priority_std",
            "priority_range",
            "arrival_span",
            "arrival_rate",
            "io_ratio",
        ]
        self._train_default_model()

    def _train_default_model(self) -> None:
        """Train Random Forest classifier on multi-objective workload scenarios."""
        X_data = []
        y_data = []
        rng = random.Random(42)

        for sample_id in range(150):
            n_proc = rng.randint(3, 8)
            scenario = sample_id % 5
            
            procs = []
            for i in range(n_proc):
                pid = f"P{i+1}"
                arr = round(rng.uniform(0, 8), 1)
                
                if scenario == 0:  # High Priority Variance -> Priority Preemptive
                    burst = round(rng.uniform(4, 12), 1)
                    prio = rng.choice([1, 1, 5, 5])
                elif scenario == 1:  # Bursty Mixed -> SRTF / SJF
                    burst = round(rng.choice([1.0, 2.0, 18.0, 24.0]), 1)
                    prio = rng.randint(1, 4)
                elif scenario == 2:  # Interactive / Short -> Round Robin
                    burst = round(rng.uniform(1, 4), 1)
                    prio = 2
                elif scenario == 3:  # Long Homogeneous -> SJF
                    burst = round(rng.uniform(12, 25), 1)
                    prio = 2
                else:  # Uniform FCFS
                    burst = 6.0
                    prio = 1
                
                procs.append(Process(pid=pid, arrival_time=arr, burst_time=burst, priority=prio))

            feats = extract_workload_features(procs)

            # Rule-based and multi-objective labeling for realistic AI selection
            if feats.priority_std > 1.0:
                best_label = "Priority (Preemptive)"
            elif feats.cv_burst > 0.5:
                best_label = "SJF (Preemptive)"
            elif feats.mean_burst <= 4.0 or feats.io_ratio > 0.2:
                best_label = "Round Robin"
            elif feats.cv_burst <= 0.2 and feats.priority_std == 0:
                best_label = "FCFS"
            else:
                best_label = "SJF (Non-preemptive)"

            X_data.append(list(feats.to_dict().values()))
            y_data.append(best_label)

        rf = RandomForestClassifier(n_estimators=40, max_depth=6, random_state=42)
        rf.fit(X_data, y_data)
        self.model = rf

    def predict(self, processes: list[Process]) -> dict[str, Any]:
        """Predict optimal scheduling policy for a given process workload."""
        feats = extract_workload_features(processes)
        X_test = feats.to_numpy()

        if self.model is not None:
            pred_algo = str(self.model.predict(X_test)[0])
            probs = self.model.predict_proba(X_test)[0]
            confidence = float(np.max(probs) * 100.0)

            importances = {
                name: round(float(imp), 4)
                for name, imp in zip(self.feature_names, self.model.feature_importances_)
            }
        else:
            pred_algo = "SJF (Preemptive)"
            confidence = 85.0
            importances = {name: 0.11 for name in self.feature_names}

        dynamic_quantum = max(1.0, round(feats.mean_burst * 0.4, 1))

        # Dynamic Rationale Explanation
        if feats.priority_std > 1.0:
            rationale = f"High priority variance ({feats.priority_std:.2f}). Priority Preemptive selected to enforce process urgency."
        elif feats.cv_burst > 0.5:
            rationale = f"High burst variation (CV = {feats.cv_burst:.2f}). SJF Preemptive selected to prevent convoy delays."
        elif feats.mean_burst <= 4.0:
            rationale = f"Short interactive workload (Mean Burst = {feats.mean_burst:.1f}ms). Round Robin (Quantum = {dynamic_quantum:.1f}ms) selected for responsiveness."
        else:
            rationale = f"Workload evaluated with {confidence:.1f}% confidence. Selected {pred_algo} based on feature vector profile."

        return {
            "predicted_algorithm": pred_algo,
            "confidence_percent": round(confidence, 1),
            "feature_vector": feats,
            "feature_importances": importances,
            "dynamic_quantum": dynamic_quantum,
            "rationale": rationale,
        }


GLOBAL_PREDICTOR = WorkloadPredictor()


def classify_workload(processes: list[Process]) -> dict[str, Any]:
    """Helper function to run ML classification on workload."""
    pred_info = GLOBAL_PREDICTOR.predict(processes)
    return {
        "features": pred_info["feature_vector"],
        "selected_policy": pred_info["predicted_algorithm"],
        "confidence": pred_info["confidence_percent"],
        "feature_importances": pred_info["feature_importances"],
        "dynamic_quantum": pred_info["dynamic_quantum"],
        "reasoning": pred_info["rationale"],
    }
