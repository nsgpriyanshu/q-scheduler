# Architecture Overview: Q-Shedular

## 1. Project Purpose

This project implements **Q-Shedular**, an AI-powered adaptive CPU scheduler that selects the best scheduling policy based on workload characteristics. It compares adaptive AI scheduling against standard algorithms:
- First-Come First-Served (FCFS)
- Shortest Job First (SJF Non-preemptive)
- Shortest Remaining Time First (SJF Preemptive / SRTF)
- Priority Scheduling (Non-preemptive)
- Priority Scheduling (Preemptive)
- Round Robin (RR)

---

## 2. End-to-End System Architecture

```text
                                  +-----------------------+
                                  | Process Workload      |
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------------------+
                                  | Feature Extractor     |
                                  | (ai/feature_extractor)|
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------------------+
                                  | ML Classifier Model   |
                                  | (ai/classifier.py)    |
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------------------+
                                  | Adaptive Policy Engine|
                                  | (scheduler/adaptive)  |
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------------------+
                                  | Simulation & Metrics  |
                                  | (metrics/performance) |
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------------------+
                                  | Streamlit Dashboard   |
                                  | (app.py)              |
                                  +-----------------------+
```

---

## 3. Core Components

### 1. Workload Layer (`workloads/generator.py`)
Generates synthetic and custom process workloads with key process properties: `pid`, `arrival_time`, `burst_time`, `priority`, `io_burst`.

### 2. Feature Extraction Layer (`ai/feature_extractor.py`)
Extracts numerical feature vectors from workload batches:
- `mean_burst`: Mean CPU burst duration
- `std_burst`: Standard deviation of CPU bursts
- `cv_burst`: Coefficient of Variation ($\sigma / \mu$)
- `priority_std`: Standard deviation of process priorities
- `priority_range`: Range of priorities
- `arrival_span`: Time span between first and last arrival
- `arrival_rate`: Arrival frequency
- `io_ratio`: I/O burst intensity

### 3. Machine Learning Classification Layer (`ai/classifier.py`)
- **Model**: Scikit-Learn `RandomForestClassifier` and `DecisionTreeClassifier`.
- **Training**: Trained on synthetic CPU scheduling datasets to map workload features to the optimal policy that minimizes average turnaround time.
- **Inference**: Returns predicted optimal algorithm, prediction confidence percentage, and feature importance rankings.

### 4. Scheduler Execution Layer (`scheduler/`)
Contains common-contract implementations for all baseline scheduling policies:
- `fcfs.py`: FCFS Non-preemptive
- `sjf.py`: SJF Non-preemptive
- `srtf.py`: SJF Preemptive / SRTF
- `priority.py`: Priority Non-preemptive
- `priority_preemptive.py`: Priority Preemptive
- `round_robin.py`: Round Robin with dynamic time quantum
- `adaptive.py`: AI Adaptive Policy Engine

### 5. Metrics & Comparison Engine (`metrics/performance.py`)
Computes standardized evaluation metrics:
- Average Waiting Time
- Average Turnaround Time
- Average Response Time
- CPU Utilization (%)
- Throughput (processes/sec)
- Total Context Switches

### 6. User Interface Layer (`app.py`)
Provides interactive Streamlit UI with:
- Dark theme styling with Arial graph font
- Sidebar controls for `No of process`, `Arrival Time`, `Burst Time`, `Priority`
- AI Prediction Insights tab
- Plotly Bar Charts and Execution Gantt Timeline
- CSV Export function
