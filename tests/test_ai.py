from ai.feature_extractor import extract_workload_features
from ai.classifier import classify_workload, WorkloadPredictor
from scheduler.core import Process


def test_feature_extractor():
    processes = [
        Process("P1", arrival_time=0.0, burst_time=5.0, priority=2),
        Process("P2", arrival_time=1.0, burst_time=15.0, priority=4),
        Process("P3", arrival_time=2.0, burst_time=2.0, priority=1),
    ]

    feats = extract_workload_features(processes)

    assert feats.num_processes == 3
    assert feats.mean_burst == 7.33
    assert feats.arrival_span == 2.0
    assert feats.priority_range == 3
    assert feats.cv_burst > 0.0


def test_ai_classifier_prediction():
    predictor = WorkloadPredictor()
    processes = [
        Process("P1", arrival_time=0.0, burst_time=2.0, priority=1),
        Process("P2", arrival_time=1.0, burst_time=20.0, priority=3),
        Process("P3", arrival_time=2.0, burst_time=1.0, priority=2),
    ]

    res = predictor.predict(processes)

    assert "predicted_algorithm" in res
    assert "confidence_percent" in res
    assert "feature_importances" in res
    assert res["confidence_percent"] > 0.0


def test_classify_workload_helper():
    processes = [
        Process("P1", arrival_time=0.0, burst_time=10.0, priority=2),
        Process("P2", arrival_time=1.0, burst_time=4.0, priority=1),
    ]

    info = classify_workload(processes)

    assert "selected_policy" in info
    assert "confidence" in info
    assert "reasoning" in info
