import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pulp import LpMinimize, LpProblem, LpVariable, value

# --- PAGE SETUP ---
st.set_page_config(page_title="Working Capital Optimizer", layout="wide")
st.title("📊 Working Capital Optimization Tool")
st.markdown("Optimization based on Computational Business Modelling Report logic.")

# --- FILE UPLOAD ---
uploaded_file = st.file_uploader("Upload your financial CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv('working capital data 600 rows.csv')
    
    # 1. Baseline Calculations (Current State)
    df["DSO"] = (df["Accounts_Receivable"] / df["Sales"]) * 365
    df["DIO"] = (df["Inventory_Value"] / df["COGS"]) * 365
    df["DPO"] = (df["Accounts_Payable"] / df["COGS"]) * 365
    df["CCC"] = df["DIO"] + df["DSO"] - df["DPO"]

    avg_dso = df["DSO"].mean()
    avg_dio = df["DIO"].mean()
    avg_dpo = df["DPO"].mean()
    before_ccc = df["CCC"].mean()

    # 2. Optimization Model (PuLP Logic from Report)
    # Objective: Minimize CCC subject to business constraints
    model = LpProblem("Working_Capital_Optimization", LpMinimize)
    
    # Decision Variables with bounds from your project report
    DSO_opt = LpVariable("DSO_opt", lowBound=20, upBound=100) 
    DIO_opt = LpVariable("DIO_opt", lowBound=30, upBound=100)
    DPO_opt = LpVariable("DPO_opt", lowBound=15, upBound=150)

    # Constraints from Report [cite: 569, 571]
    model += DSO_opt >= 30  # Minimum customer credit
    model += DIO_opt >= 45  # Minimum inventory for service level
    model += DPO_opt <= 60  # Supplier relationship constraint (max delay)
    
    # Objective Function: Minimize DSO + DIO - DPO
    model += DSO_opt + DIO_opt - DPO_opt
    model.solve()

    optimal_dso = value(DSO_opt)
    optimal_dio = value(DIO_opt)
    optimal_dpo = value(DPO_opt)
    optimal_ccc = optimal_dso + optimal_dio - optimal_dpo
    efficiency_gain = before_ccc - optimal_ccc

    # --- DASHBOARD LAYOUT ---
    
    # Row 1: Key Metrics (Before vs After)
    st.header("🎯 Optimization Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Baseline CCC", f"{before_ccc:.1f} Days")
    col2.metric("Improved CCC", f"{optimal_ccc:.1f} Days", delta=f"-{efficiency_gain:.1f} Days", delta_color="normal")
    
    # Financial Impact Calculation 
    avg_daily_sales = df["Sales"].mean() / 365
    cash_released = efficiency_gain * avg_daily_sales
    col3.metric("Estimated Cash Released", f"${cash_released:,.0f}", help="Based on average daily sales")

    st.divider()

    # Row 2: Comparison Chart 
    st.subheader("Baseline vs. Optimized Metrics")
    comp_data = pd.DataFrame({
        "Metric": ["DSO", "DIO", "DPO", "CCC"],
        "Before": [avg_dso, avg_dio, avg_dpo, before_ccc],
        "After": [optimal_dso, optimal_dio, optimal_dpo, optimal_ccc]
    })
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(name='Before Optimization', x=comp_data['Metric'], y=comp_data['Before'], marker_color='#EF553B'))
    fig_comp.add_trace(go.Bar(name='After Optimization', x=comp_data['Metric'], y=comp_data['After'], marker_color='#00CC96'))
    fig_comp.update_layout(barmode='group', title="Days Improvement per Component")
    st.plotly_chart(fig_comp, use_container_width=True)

    # Row 3: Monte Carlo Simulation (Graphics for Uncertainty) [cite: 585]
    st.divider()
    st.subheader("🎲 Risk Analysis: Monte Carlo Simulation")
    st.write("Simulating CCC variability under 1,000 random demand shocks.")
    
    simulated_ccc = []
    for i in range(1000):
        # Random demand shock logic from report [cite: 585, 586]
        shock = np.random.normal(1, 0.05)
        sim_ccc = (optimal_dio * shock) + (optimal_dso * shock) - optimal_dpo
        simulated_ccc.append(sim_ccc)
    
    fig_sim = px.histogram(simulated_ccc, nbins=30, title="Probability Distribution of Improved CCC",
                          labels={'value': 'Days'}, color_discrete_sequence=['#636EFA'])
    st.plotly_chart(fig_sim, use_container_width=True)

    # Data Explorer
    with st.expander("🔍 View Processed Financial Data"):
        st.dataframe(df)
else:
    st.info("Please upload your project's CSV data file to generate the improved insights.")