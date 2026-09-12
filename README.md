# Problem Statement

Traditional CPU scheduling algorithms such as FCFS, SJF, Priority, and Round Robin use fixed rules to allocate CPU time. However, no single scheduling policy performs optimally across different workload types, such as CPU-intensive, I/O-intensive, interactive, bursty, and mixed workloads. Using an unsuitable policy can increase waiting time, response time, context-switch overhead, and reduce overall system efficiency.

This project proposes an **Adaptive AI-Based CPU Scheduler** that analyzes process and workload characteristics—such as CPU burst time, arrival patterns, priority, I/O behavior, and historical execution patterns—to dynamically select or adjust the most suitable scheduling strategy.

The proposed scheduler will be compared against traditional algorithms using controlled and reproducible workloads. Performance will be evaluated using **average waiting time, turnaround time, response time, throughput, CPU utilization, context switches, fairness, and starvation**.

The goal is to determine, through measurable experiments and statistical analysis, whether workload-aware adaptive scheduling can provide better overall performance than conventional fixed scheduling policies while keeping the overhead of the adaptive mechanism low.
