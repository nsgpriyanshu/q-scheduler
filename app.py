import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from scheduler.core import Process
from metrics.performance import run_target_simulations, build_comparison_dataframe
from ai.classifier import classify_workload

# ==========================================
# 1. STREAMLIT PAGE CONFIG & THEME SETUP
# ==========================================
st.set_page_config(
    page_title="Q-Shedular",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Dark Theme with Sidebar Slightly Darker than Main BG
MAIN_BG = "#0E1117"
SIDEBAR_BG = "#06080D"
CARD_BG = "#161B22"
BORDER_COLOR = "#30363D"
TEXT_COLOR = "#FAFAFA"
SECONDARY_TEXT = "#8B949E"

st.markdown(
    f"""
    <style>
        /* Main App Background */
        .stApp {{
            background-color: {MAIN_BG};
            color: {TEXT_COLOR};
            font-family: Arial, -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        header[data-testid="stHeader"] {{
            background-color: {MAIN_BG};
        }}
        
        /* Sidebar Slightly Darker Than Main Background */
        section[data-testid="stSidebar"] {{
            background-color: {SIDEBAR_BG};
            border-right: 1px solid {BORDER_COLOR};
        }}
        
        /* Force Text Visibility */
        .stMarkdown, .stText, label, p, h1, h2, h3, h4, h5, h6 {{
            color: {TEXT_COLOR} !important;
            font-family: Arial, sans-serif !important;
        }}
        .stCaption {{
            color: {SECONDARY_TEXT} !important;
            font-family: Arial, sans-serif !important;
        }}

        /* Fix Sidebar Collapse Button & Header Icons */
        [data-testid="stSidebarCollapseButton"] *,
        [data-testid="stHeader"] button *,
        button[aria-label*="sidebar"] *,
        button[aria-label*="Sidebar"] * {{
            font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
        }}
        
        /* Metric Card Component */
        .metric-card {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER_COLOR};
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
        }}
        .metric-title {{
            font-size: 12px;
            font-weight: 600;
            color: {SECONDARY_TEXT} !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
            font-family: Arial, sans-serif !important;
        }}
        .metric-value {{
            font-size: 22px;
            font-weight: 700;
            color: {TEXT_COLOR} !important;
            font-family: Arial, sans-serif !important;
        }}
        .metric-sub {{
            font-size: 12px;
            color: #58A6FF !important;
            margin-top: 4px;
            font-family: Arial, sans-serif !important;
        }}

        /* Clean Tabs Styling */
        button[data-baseweb="tab"] p {{
            font-size: 14px !important;
            font-weight: 600 !important;
            color: {SECONDARY_TEXT} !important;
            font-family: Arial, sans-serif !important;
        }}
        button[aria-selected="true"] p {{
            color: #FF4B4B !important;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


def get_plotly_dark_layout(title: str = "", height: int = 380):
    """Return Plotly layout configuration with Arial font and dark theme styling."""
    return dict(
        title=dict(text=title, font=dict(size=15, color=TEXT_COLOR, family="Arial")),
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        margin=dict(l=30, r=30, t=40, b=30),
        height=height,
        font=dict(color=TEXT_COLOR, family="Arial"),
        xaxis=dict(
            gridcolor="#21262D",
            linecolor=BORDER_COLOR,
            tickfont=dict(color=SECONDARY_TEXT, family="Arial"),
            title_font=dict(color=SECONDARY_TEXT, family="Arial"),
        ),
        yaxis=dict(
            gridcolor="#21262D",
            linecolor=BORDER_COLOR,
            tickfont=dict(color=SECONDARY_TEXT, family="Arial"),
            title_font=dict(color=SECONDARY_TEXT, family="Arial"),
        ),
        legend=dict(
            bgcolor="rgba(22, 27, 34, 0.8)",
            bordercolor=BORDER_COLOR,
            borderwidth=1,
            font=dict(color=TEXT_COLOR, family="Arial"),
        ),
    )


# ==========================================
# 2. SIDEBAR INPUTS (NO OF PROCESS, ARRIVAL TIME, BURST TIME, PRIORITY)
# ==========================================
with st.sidebar:
    st.markdown("## Q-Shedular")
    st.caption("AI Adaptive CPU Scheduling Engine")
    st.divider()

    st.markdown("### Process Inputs")
    num_processes = st.number_input("No of process", min_value=1, max_value=12, value=4, step=1)

    processes: list[Process] = []
    
    input_mode = st.radio("Input Method", ["Individual Process Inputs", "Quick Table Editor"], index=0)

    if input_mode == "Individual Process Inputs":
        st.markdown("#### Arrival, Burst & Priority")
        default_arrivals = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0]
        default_bursts = [7.0, 4.0, 1.0, 4.0, 6.0, 3.0, 5.0, 2.0, 8.0, 4.0, 5.0, 3.0]
        default_prios = [3, 1, 4, 2, 3, 1, 5, 2, 4, 1, 3, 2]

        for i in range(int(num_processes)):
            pid = f"P{i+1}"
            def_arr = default_arrivals[i] if i < len(default_arrivals) else float(i * 2)
            def_burst = default_bursts[i] if i < len(default_bursts) else 5.0
            def_prio = default_prios[i] if i < len(default_prios) else 0

            col_a, col_b, col_c = st.columns(3)
            with col_a:
                arr_time = st.number_input(
                    f"{pid} Arrival",
                    min_value=0.0,
                    value=float(def_arr),
                    step=1.0,
                    key=f"arr_{i}",
                )
            with col_b:
                burst_time = st.number_input(
                    f"{pid} Burst",
                    min_value=1.0,
                    value=float(def_burst),
                    step=1.0,
                    key=f"burst_{i}",
                )
            with col_c:
                prio = st.number_input(
                    f"{pid} Priority",
                    min_value=0,
                    value=int(def_prio),
                    step=1,
                    key=f"prio_{i}",
                )

            processes.append(Process(pid=pid, arrival_time=arr_time, burst_time=burst_time, priority=prio))
    else:
        st.markdown("#### Table Input")
        default_table = pd.DataFrame(
            [
                {
                    "pid": f"P{i+1}",
                    "arrival_time": float(i * 1.0),
                    "burst_time": float(6 - i if i < 4 else 4),
                    "priority": int(i % 4),
                }
                for i in range(int(num_processes))
            ]
        )
        edited_df = st.data_editor(default_table, num_rows="dynamic", key="sidebar_table_editor")
        for _, row in edited_df.iterrows():
            if str(row["pid"]).strip():
                processes.append(
                    Process(
                        pid=str(row["pid"]),
                        arrival_time=float(row["arrival_time"]),
                        burst_time=float(row["burst_time"]),
                        priority=int(row.get("priority", 0)),
                    )
                )

    st.divider()
    st.markdown("### Parameters")
    rr_quantum = st.slider("Round Robin Time Quantum", min_value=1.0, max_value=10.0, value=2.0, step=0.5)


if not processes:
    st.warning("Please define at least one process to run simulations.")
    st.stop()

# Run target simulations
simulations = run_target_simulations(processes, quantum=rr_quantum)
comparison_df = build_comparison_dataframe(simulations)
ai_classification = classify_workload(processes)


# ==========================================
# 3. MAIN APP HEADER
# ==========================================
st.title("Q-Shedular")
st.markdown(
    "AI-Powered Adaptive CPU Scheduling Platform comparing AI prediction against FCFS, SJF (Preemptive/Non-preemptive), Priority (Preemptive/Non-preemptive), and Round Robin."
)
st.write("")


# ==========================================
# 4. DASHBOARD TABS
# ==========================================
tab_ai, tab1, tab2, tab3 = st.tabs(
    [
        "AI Adaptive Insights",
        "Metrics Comparison",
        "Execution Gantt Timeline",
        "Detailed Process Data",
    ]
)

# Standard Streamlit Color Palette for Schedulers
ALGO_COLORS = [
    "#5856D6",  # Adaptive Q-Scheduler (Indigo)
    "#0068C9",  # FCFS (Blue)
    "#83C5BE",  # SJF Non-preemptive (Teal)
    "#36B37E",  # SJF Preemptive (Green)
    "#A55EEA",  # Priority Non-preemptive (Purple)
    "#FF4B4B",  # Priority Preemptive (Red)
    "#FF9F43",  # Round Robin (Orange)
]


# ------------------------------------------
# TAB AI: ADAPTIVE AI PREDICTION INSIGHTS
# ------------------------------------------
with tab_ai:
    st.subheader("AI Workload Classification & Policy Prediction")

    ac1, ac2, ac3 = st.columns(3)
    with ac1:
        st.markdown(
            f"""
            <div class='metric-card'>
                <div class='metric-title'>AI Selected Policy</div>
                <div class='metric-value' style='color:#58A6FF;'>{ai_classification['selected_policy']}</div>
                <div class='metric-sub'>Optimal Predicted Algorithm</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with ac2:
        st.markdown(
            f"""
            <div class='metric-card'>
                <div class='metric-title'>Prediction Confidence</div>
                <div class='metric-value' style='color:#36B37E;'>{ai_classification['confidence']:.1f}%</div>
                <div class='metric-sub'>Scikit-Learn Random Forest Model</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with ac3:
        st.markdown(
            f"""
            <div class='metric-card'>
                <div class='metric-title'>Dynamic RR Quantum</div>
                <div class='metric-value' style='color:#FF9F43;'>{ai_classification['dynamic_quantum']:.1f} ms</div>
                <div class='metric-sub'>Calculated from Mean Burst</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div style='background-color:#161B22; border-left:4px solid #5856D6; padding:14px; border-radius:6px; margin:10px 0;'>
            <strong>AI Prediction Rationale:</strong><br>
            {ai_classification['reasoning']}
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_fi1, col_fi2 = st.columns(2)

    with col_fi1:
        st.subheader("Workload Feature Vector")
        feat_df = pd.DataFrame([ai_classification["features"].to_dict()])
        st.dataframe(feat_df.T.rename(columns={0: "Feature Value"}), use_container_width=True)

    with col_fi2:
        st.subheader("ML Feature Importance Ranking")
        importances_dict = ai_classification["feature_importances"]
        fi_df = pd.DataFrame(
            {"Feature": list(importances_dict.keys()), "Importance": list(importances_dict.values())}
        ).sort_values(by="Importance", ascending=True)

        fig_fi = px.bar(
            fi_df,
            x="Importance",
            y="Feature",
            orientation="h",
            title="Random Forest Feature Importance",
            color_discrete_sequence=["#0068C9"],
        )
        fig_fi.update_layout(get_plotly_dark_layout("Random Forest Feature Importance", height=320))
        st.plotly_chart(fig_fi, use_container_width=True)


# ------------------------------------------
# TAB 1: METRICS COMPARISON
# ------------------------------------------
with tab1:
    st.subheader("Performance Comparison Across All Schedulers")

    col1, col2 = st.columns(2)

    with col1:
        fig_times = go.Figure()
        fig_times.add_trace(
            go.Bar(
                x=comparison_df["Algorithm"],
                y=comparison_df["Avg Waiting Time"],
                name="Avg Waiting Time",
                marker_color="#0068C9",
            )
        )
        fig_times.add_trace(
            go.Bar(
                x=comparison_df["Algorithm"],
                y=comparison_df["Avg Turnaround Time"],
                name="Avg Turnaround Time",
                marker_color="#83C5BE",
            )
        )
        fig_times.add_trace(
            go.Bar(
                x=comparison_df["Algorithm"],
                y=comparison_df["Avg Response Time"],
                name="Avg Response Time",
                marker_color="#FF4B4B",
            )
        )

        layout_times = get_plotly_dark_layout("Average Scheduling Metrics (Lower is Better)", height=400)
        layout_times["barmode"] = "group"
        fig_times.update_layout(layout_times)
        st.plotly_chart(fig_times, use_container_width=True)

    with col2:
        fig_util = go.Figure()
        fig_util.add_trace(
            go.Bar(
                x=comparison_df["Algorithm"],
                y=comparison_df["CPU Utilization (%)"],
                name="CPU Utilization (%)",
                marker_color="#36B37E",
                text=comparison_df["CPU Utilization (%)"].apply(lambda v: f"{v}%"),
                textposition="auto",
            )
        )
        fig_util.update_layout(get_plotly_dark_layout("CPU Utilization (%)", height=400))
        st.plotly_chart(fig_util, use_container_width=True)

    st.subheader("Per-Process Waiting Time Breakdown")
    proc_df_list = []
    for algo_name, sim_data in simulations.items():
        for res in sim_data["results"]:
            proc_df_list.append(
                {
                    "Algorithm": algo_name,
                    "Process": res["pid"],
                    "Waiting Time": res["waiting_time"],
                    "Turnaround Time": res["turnaround_time"],
                }
            )

    proc_df = pd.DataFrame(proc_df_list)
    fig_proc = px.bar(
        proc_df,
        x="Process",
        y="Waiting Time",
        color="Algorithm",
        barmode="group",
        title="Per-Process Waiting Time Comparison",
        color_discrete_sequence=ALGO_COLORS,
    )
    fig_proc.update_layout(get_plotly_dark_layout("Per-Process Waiting Time Comparison", height=400))
    st.plotly_chart(fig_proc, use_container_width=True)


# ------------------------------------------
# TAB 2: EXECUTION GANTT TIMELINE
# ------------------------------------------
with tab2:
    st.subheader("CPU Execution Gantt Chart")
    st.caption("Visualizing process execution intervals across all scheduling algorithms.")

    gantt_rows = []
    for algo, sim_data in simulations.items():
        for slot in sim_data["timeline"]:
            gantt_rows.append(
                {
                    "Algorithm": algo,
                    "Process": slot["pid"],
                    "Start": float(slot["start"]),
                    "End": float(slot["end"]),
                    "Duration": float(slot["end"] - slot["start"]),
                }
            )

    gantt_df = pd.DataFrame(gantt_rows)

    if not gantt_df.empty:
        fig_gantt = px.bar(
            gantt_df,
            x="Duration",
            y="Algorithm",
            base="Start",
            color="Process",
            orientation="h",
            title="CPU Execution Gantt Chart",
            color_discrete_sequence=px.colors.qualitative.Plotly,
            hover_data={"Start": ":.1f", "End": ":.1f", "Duration": ":.1f", "Algorithm": True, "Process": True},
        )
        layout_gantt = get_plotly_dark_layout("Execution Timeline (Time Units)", height=450)
        layout_gantt["xaxis"]["title"] = "Time Units"
        fig_gantt.update_layout(layout_gantt)
        st.plotly_chart(fig_gantt, use_container_width=True)
    else:
        st.info("No timeline data available.")


# ------------------------------------------
# TAB 3: DETAILED PROCESS DATA
# ------------------------------------------
with tab3:
    st.subheader("Simulation Results Data Table")
    st.dataframe(comparison_df, use_container_width=True)

    csv_data = comparison_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Export CSV Results",
        data=csv_data,
        file_name="q_shedular_simulation_results.csv",
        mime="text/csv",
    )

    st.divider()

    st.subheader("Per-Algorithm Detailed Traces")
    selected_algo = st.selectbox("Select Algorithm", options=list(simulations.keys()))
    if selected_algo:
        st.dataframe(pd.DataFrame(simulations[selected_algo]["results"]), use_container_width=True)
