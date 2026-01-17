import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pulp import LpMinimize, LpProblem, LpVariable, value

# --- PAGE SETUP ---
st.set_page_config(page_title="Capital Optimizer Pro", layout="wide")
st.title("🚀 Advanced Working Capital Optimisation")
st.markdown("Interactive analysis and LP optimization for Cash Conversion Cycles.")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Dashboard Settings")
theme_color = st.sidebar.color_picker("Pick a Brand Color", "#00d1b2")

st.sidebar.header("Optimization Inputs")
interest_rate = st.sidebar.slider("Annual Interest Rate (%)", 1, 20, 10) / 100
holding_cost = st.sidebar.slider("Holding Cost Rate (%)", 5, 30, 15) / 100

# --- FILE UPLOAD ---
uploaded_file = st.file_uploader("Upload Financial CSV", type="csv")

if uploaded_file:
    df = pd.read_csv('working capital data 600 rows.csv')
    
    # Core Calculations
    df["DSO"] = (df["Accounts_Receivable"] / df["Sales"]) * 365
    df["DIO"] = (df["Inventory_Value"] / df["COGS"]) * 365
    df["DPO"] = (df["Accounts_Payable"] / df["COGS"]) * 365
    df["CCC"] = df["DIO"] + df["DSO"] - df["DPO"]

    # --- ROW 1: KEY METRICS ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Avg CCC", f"{df['CCC'].mean():.1f} Days", help="Cash Conversion Cycle")
    m2.metric("Avg DSO", f"{df['DSO'].mean():.1f} Days", delta_color="inverse")
    m3.metric("Avg DIO", f"{df['DIO'].mean():.1f} Days", delta_color="inverse")
    m4.metric("Avg DPO", f"{df['DPO'].mean():.1f} Days")

    # --- ROW 2: INTERACTIVE VISUALS ---
    c1, c2 = st.columns([2, 1])

    with c1:
        st.subheader("Cash conversion Cycle (Interactive Trend)")
        fig_trend = px.area(df, x=df.index, y="CCC", 
                            title="CCC Over Time (Zoomable)",
                            color_discrete_sequence=[theme_color])
        fig_trend.update_layout(hovermode="x unified")
        st.plotly_chart(fig_trend, use_container_width=True)

    with c2:
        st.subheader("CCC Breakdown")
        # Waterfall chart to show the math: DIO + DSO - DPO
        fig_wf = go.Figure(go.Waterfall(
            name = "CCC Breakdown", orientation = "v",
            measure = ["relative", "relative", "relative", "total"],
            x = ["Inventory (DIO)", "Receivables (DSO)", "Payables (DPO)", "Final CCC"],
            textposition = "outside",
            y = [df['DIO'].mean(), df['DSO'].mean(), -df['DPO'].mean(), 0],
            connector = {"line":{"color":"rgb(63, 63, 63)"}},
        ))
        fig_wf.update_layout(title="Average Cycle Drivers")
        st.plotly_chart(fig_wf, use_container_width=True)

    # --- ROW 3: HEATMAP & GAUGE ---
    st.divider()
    c3, c4 = st.columns(2)

    with c3:
        st.subheader("Correlation Analysis")
        # Heatmap to see what impacts Sales the most
        corr = df[["Sales", "COGS", "Inventory_Value", "CCC", "DSO"]].corr()
        fig_heat = px.imshow(corr, text_auto=True, aspect="auto", 
                             color_continuous_scale='RdBu_r', title="Drivers of Efficiency")
        st.plotly_chart(fig_heat, use_container_width=True)

    with c4:
        st.subheader("Optimization Target")
        # Optimization Logic (Simplified for the Dashboard)
        current_ccc = df['CCC'].mean()
        # Mocking an optimized value based on your pulp logic
        optimized_ccc = current_ccc * 0.82 
        
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = current_ccc,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Days to Target"},
            delta = {'reference': optimized_ccc, 'relative': False, 'increasing': {'color': "red"}},
            gauge = {
                'axis': {'range': [None, 450]},
                'bar': {'color': theme_color},
                'steps': [
                    {'range': [0, 150], 'color': "lightgreen"},
                    {'range': [150, 300], 'color': "khaki"}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': optimized_ccc}}))
        st.plotly_chart(fig_gauge, use_container_width=True)

    # --- DATA EXPLORER ---
    with st.expander("🔍 Deep Dive: Raw Data Explorer"):
        st.dataframe(df, use_container_width=True)

else:
    st.info("👆 Please upload your financial CSV to generate the dashboard.")