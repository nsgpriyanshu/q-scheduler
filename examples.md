# Presentation Demo Workload Examples (Q-Shedular)

Use these copy-pasteable process workload parameters during live presentations and demonstrations.

---

## 1. FCFS (First-Come, First-Served)

> [!NOTE]
> FCFS schedules processes strictly by arrival time order. Priority is not applicable.

### Sample Input 1: Basic Sequential Arrival

| Process | Arrival Time (ms) | Burst Time (ms) |
| :--- | :--- | :--- |
| **P1** | 0.0 | 8.0 |
| **P2** | 1.0 | 4.0 |
| **P3** | 2.0 | 9.0 |
| **P4** | 3.0 | 3.0 |

### Quick Copy Format:
```text
P1: Arrival = 0.0, Burst = 8.0
P2: Arrival = 1.0, Burst = 4.0
P3: Arrival = 2.0, Burst = 9.0
P4: Arrival = 3.0, Burst = 3.0
```

---

## 2. SJF (Shortest Job First - Non-preemptive)

> [!NOTE]
> SJF Non-preemptive selects the arrived process with the smallest CPU burst time. Priority is not applicable.

### Sample Input: Short vs Long Burst Tasks

| Process | Arrival Time (ms) | Burst Time (ms) |
| :--- | :--- | :--- |
| **P1** | 0.0 | 7.0 |
| **P2** | 2.0 | 4.0 |
| **P3** | 4.0 | 1.0 |
| **P4** | 5.0 | 4.0 |

### Expected Behavior:
- `P1` starts at $t=0.0$.
- At $t=7.0$, processes `P2`, `P3`, `P4` have arrived. `P3` (Burst = 1.0) is selected next.

---

## 3. SJF (Preemptive) / SRTF (Shortest Remaining Time First)

> [!NOTE]
> SRTF preempts the running process if a newly arrived process has a shorter remaining burst time. Priority is not applicable.

### Sample Input: Preemption Demonstration

| Process | Arrival Time (ms) | Burst Time (ms) |
| :--- | :--- | :--- |
| **P1** | 0.0 | 8.0 |
| **P2** | 1.0 | 2.0 |
| **P3** | 2.0 | 1.0 |
| **P4** | 3.0 | 4.0 |

### Expected Behavior:
- `P1` starts at $t=0.0$.
- At $t=1.0$, `P2` arrives with burst $2.0 < 7.0$ (remaining $P1$). `P2` preempts `P1`.
- At $t=2.0$, `P3` arrives with burst $1.0 < 1.0$ (remaining $P2$). `P3` preempts `P2`.

---

## 4. Priority (Non-preemptive)

> [!NOTE]
> Lower numerical priority value represents higher importance (e.g. Priority 1 is highest).

### Sample Input: Priority Selection

| Process | Arrival Time (ms) | Burst Time (ms) | Priority (1 = Highest) |
| :--- | :--- | :--- | :--- |
| **P1** | 0.0 | 10.0 | 3 |
| **P2** | 1.0 | 6.0 | 1 |
| **P3** | 2.0 | 14.0 | 4 |
| **P4** | 3.0 | 4.0 | 2 |

---

## 5. Priority (Preemptive)

> [!NOTE]
> Critical high-priority arrivals immediately preempt lower-priority processes running on the CPU.

### Sample Input: Priority Preemption

| Process | Arrival Time (ms) | Burst Time (ms) | Priority (1 = Highest) |
| :--- | :--- | :--- | :--- |
| **P1** | 0.0 | 10.0 | 4 |
| **P2** | 1.0 | 4.0 | 1 |
| **P3** | 2.0 | 8.0 | 1 |
| **P4** | 3.0 | 3.0 | 2 |

### Expected Behavior:
- `P1` (Priority 4) starts at $t=0.0$.
- At $t=1.0$, `P2` (Priority 1) arrives and immediately preempts `P1`.

---

## 6. Round Robin (RR)

> [!NOTE]
> Executes processes in time slices equal to Time Quantum ($Q$). Priority is not applicable.

### Sample Input (Time Quantum = 2.0 ms)

| Process | Arrival Time (ms) | Burst Time (ms) |
| :--- | :--- | :--- |
| **P1** | 0.0 | 5.0 |
| **P2** | 1.0 | 3.0 |
| **P3** | 2.0 | 8.0 |

### Execution Trace:
- $t=0.0 \to 2.0$: `P1` executes (3.0 ms remaining)
- $t=2.0 \to 4.0$: `P2` executes (1.0 ms remaining)
- $t=4.0 \to 6.0$: `P3` executes (6.0 ms remaining)
- $t=6.0 \to 7.0$: `P1` executes (1.0 ms remaining) ...

---

## 7. Adaptive Q-Scheduler (AI Triggering Profiles)

### Profile A: AI Triggers SJF (Preemptive)
- **Workload**: `P1 (0.0, 1.0)`, `P2 (1.0, 22.0)`, `P3 (2.0, 2.0)`
- **AI Rationale**: High burst variation ($\text{CV} = 1.42$). AI selects SRTF to eliminate convoy delays.

### Profile B: AI Triggers Priority (Preemptive)
- **Workload**: `P1 (0.0, 10.0, Prio=4)`, `P2 (1.0, 4.0, Prio=1)`, `P3 (2.0, 8.0, Prio=1)`
- **AI Rationale**: High priority variance ($\text{Std} = 1.73$). AI selects Priority Preemptive for urgent tasks.

### Profile C: AI Triggers Round Robin
- **Workload**: `P1 (0.0, 3.0)`, `P2 (1.0, 2.0)`, `P3 (2.0, 4.0)`
- **AI Rationale**: Short interactive tasks. AI selects Round Robin and computes dynamic quantum ($1.2\,\text{ms}$).
