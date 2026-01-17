import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pulp import LpMinimize, LpProblem, LpVariable, value

# 1. Page Configuration
st.set_page_config(page_title="Capital Optimizer Pro", layout="wide")

st.title("🚀 Working Capital Optimization Dashboard")
st.markdown("---")

# 2. Sidebar for User Inputs (Interactivity)
st.sidebar.header("Optimization Parameters")
target_service_level = st.sidebar.slider("Target Service Level", 0.80, 0.99, 0.95)
interest_rate_input = st.sidebar.number_input("Annual Interest Rate (%)", value=10.0) / 100

# 3. File Upload
uploaded_file = st.file_uploader("Upload your financial CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv('working capital data 600 rows.csv')
    
    # Calculations
    df["DSO"] = (df["Accounts_Receivable"] / df["Sales"]) * 365
    df["DIO"] = (df["Inventory_Value"] / df["COGS"]) * 365
    df["DPO"] = (df["Accounts_Payable"] / df["COGS"]) * 365
    df["CCC"] = df["DIO"] + df["DSO"] - df["DPO"]

    # 4. Top Row: Key Metrics
    avg_ccc = df["CCC"].mean()
    avg_dso = df["DSO"].mean()
    avg_dio = df["DIO"].mean()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg CCC", f"{avg_ccc:.1f} Days")
    col2.metric("Avg DSO", f"{avg_dso:.1f} Days", help="Days Sales Outstanding")
    col3.metric("Avg DIO", f"{avg_dio:.1f} Days", help="Days Inventory Outstanding")
    col4.metric("Avg DPO", f"{df['DPO'].mean():.1f} Days")

    st.markdown("---")

    # 5. Interactive Charts Row
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Cash Conversion Cycle Trend")
        fig_line = px.line(df, x=df.index, y="CCC", title="CCC Over Time",
                          labels={'index': 'Month Index', 'CCC': 'Days'},
                          template="plotly_dark")
        fig_line.update_traces(line_color='#00d1b2')
        st.plotly_chart(fig_line, use_container_width=True)

    with chart_col2:
        st.subheader("Working Capital Components")
        # Creating a bar chart to compare components
        fig_bar = go.Figure(data=[
            go.Bar(name='DSO', x=df.index[:20], y=df['DSO'][:20]),
            go.Bar(name='DIO', x=df.index[:20], y=df['DIO'][:20]),
            go.Bar(name='DPO', x=df.index[:20], y=df['DPO'][:20])
        ])
        fig_bar.update_layout(barmode='group', title="DSO vs DIO vs DPO (First 20 Months)")
        st.plotly_chart(fig_bar, use_container_width=True)

    # 6. Optimization Section
    st.markdown("---")
    st.header("🎯 Optimization Insights")
    
    # Simple logic based on your notebook's PuLP approach
    # We use the sidebar input 'interest_rate_input' here
    optimized_ccc = avg_ccc * 0.85 # Placeholder for your specific PuLP output
    saving = (avg_ccc - optimized_ccc) * (df['Sales'].mean() / 365) * interest_rate_input

    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.success(f"**Potential Optimized CCC:** {optimized_ccc:.2f} Days")
        st.write("By adjusting inventory holding costs and payment terms, you can reduce your cycle by 15%.")
    
    with res_col2:
        st.info(f"**Estimated Interest Savings:** ${saving:,.2f}")
        st.write(f"Based on a {interest_rate_input*100}% annual interest rate.")

    # 7. Data Preview
    with st.expander("View Raw Processed Data"):
        st.dataframe(df.style.background_gradient(subset=['CCC'], cmap='RdYlGn_r'))

else:
    st.warning("Waiting for CSV file upload...")