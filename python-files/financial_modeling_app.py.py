import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# -------------------------------
# Cash Flow Modeling Functions
# -------------------------------

def generate_cash_flow(
    revenue: float,
    growth_rate: float,
    cogs_pct: float,
    dso: int,
    dpo: int,
    months: int = 24
):
    """Generates projected cash flows under given assumptions"""

    # Revenue projection
    revenues = [revenue * ((1 + growth_rate) ** m) for m in range(months)]
    cogs = [r * cogs_pct for r in revenues]
    gross_profit = [r - c for r, c in zip(revenues, cogs)]

    # Working capital impact
    # Assuming dso and dpo are in days, and we are working with monthly periods.
    # We shift by the number of full months represented by DSO/DPO.
    collections_delay_months = dso // 30
    payments_delay_months = dpo // 30


    collections = pd.Series(revenues).shift(collections_delay_months, fill_value=0).tolist()
    payments = pd.Series(cogs).shift(payments_delay_months, fill_value=0).tolist()


    operating_cash_flow = [c - p for c, p in zip(collections, payments)]
    cumulative_cash = np.cumsum(operating_cash_flow)

    df = pd.DataFrame({
        "Month": list(range(1, months + 1)),
        "Revenue": revenues,
        "COGS": cogs,
        "Gross Profit": gross_profit,
        "Collections": collections,
        "Payments": payments,
        "Operating Cash Flow": operating_cash_flow,
        "Cumulative Cash Balance": cumulative_cash
    })

    return df

# -------------------------------
# Streamlit App
# -------------------------------

st.set_page_config(page_title="Financial Modeling Assistant", layout="wide", initial_sidebar_state="expanded")
st.title("💰 Financial Modeling Assistant")
st.markdown("""
    Welcome to the **Financial Modeling Assistant**! This interactive tool helps you
    forecast your business's cash flow based on key assumptions.

    Adjust the parameters in the sidebar to see how changes in revenue growth, cost of
    goods sold, and working capital (DSO/DPO) impact your cash balance over time.
""")

# Initialize session state for scenarios if not already present
if 'scenarios' not in st.session_state:
    st.session_state['scenarios'] = {}
if 'current_scenario_name' not in st.session_state:
    st.session_state['current_scenario_name'] = "Default Scenario"

# Sidebar inputs
st.sidebar.header("Input Parameters")

# Use columns to group related inputs
col1, col2 = st.sidebar.columns(2)
with col1:
    # Added min_value and max_value for better control
    revenue = st.number_input("Starting Monthly Revenue ($)", min_value=1000, max_value=10000000, value=st.session_state.get('revenue_input', 100000), step=10000, key='revenue_input')
    # Added format for better display of percentage
    cogs_pct = st.slider("COGS (% of Revenue)", min_value=0.0, max_value=1.0, value=st.session_state.get('cogs_pct_input', 0.4), step=0.01, format="%.2f", key='cogs_pct_input')
    dso = st.slider("DSO (Days Sales Outstanding)", min_value=0, max_value=180, value=st.session_state.get('dso_input', 45), step=1, key='dso_input')
with col2:
    # Adjusted step and format for growth rate
    growth_rate_pct = st.slider("Monthly Growth Rate (%)", min_value=-20.0, max_value=50.0, value=st.session_state.get('growth_rate_input', 2.0), step=0.1, format="%.1f", key='growth_rate_input')
    growth_rate = growth_rate_pct / 100.0 # Convert percentage to decimal
    dpo = st.slider("DPO (Days Payables Outstanding)", min_value=0, max_value=180, value=st.session_state.get('dpo_input', 30), step=1, key='dpo_input')
    months = st.slider("Forecast Horizon (Months)", min_value=6, max_value=120, value=st.session_state.get('months_input', 24), step=1, key='months_input')

# -------------------------------
# Scenario Management Section
# -------------------------------
st.sidebar.header("Scenario Management")
# Set a default value for the scenario name input
scenario_name = st.sidebar.text_input("Scenario Name", value=st.session_state['current_scenario_name'], key='scenario_name_input')

# Save current scenario
# Added a check to ensure scenario name is not empty
if st.sidebar.button("Save Scenario"):
    if scenario_name.strip() == "":
        st.sidebar.warning("Please enter a name for the scenario.")
    else:
        st.session_state['scenarios'][scenario_name] = {
            'revenue': revenue,
            'growth_rate': growth_rate, # Save as decimal
            'cogs_pct': cogs_pct,
            'dso': dso,
            'dpo': dpo,
            'months': months
        }
        st.session_state['current_scenario_name'] = scenario_name
        st.sidebar.success(f"Scenario '{scenario_name}' saved!")

# Load scenario
saved_scenarios = list(st.session_state['scenarios'].keys())
# Added a check to disable the selectbox if no scenarios are saved
if not saved_scenarios:
    st.sidebar.info("Save a scenario to enable loading.")
    selected_scenario = "Select a scenario" # Default value when no scenarios are saved
else:
    selected_scenario = st.sidebar.selectbox("Load Scenario", ["Select a scenario"] + saved_scenarios, key='load_scenario_selectbox')

if selected_scenario != "Select a scenario":
    loaded_scenario = st.session_state['scenarios'][selected_scenario]
    st.session_state['current_scenario_name'] = selected_scenario
    # Update session state keys directly to trigger input updates
    st.session_state['revenue_input'] = loaded_scenario['revenue']
    st.session_state['growth_rate_input'] = loaded_scenario['growth_rate'] * 100 # Convert back to percentage for slider
    st.session_state['cogs_pct_input'] = loaded_scenario['cogs_pct']
    st.session_state['dso_input'] = loaded_scenario['dso']
    st.session_state['dpo_input'] = loaded_scenario['dpo']
    st.session_state['months_input'] = loaded_scenario['months']
    # Use st.rerun() instead of st.experimental_rerun()
    st.rerun()

# Generate forecast for the current scenario using the latest input values from session state
# Access input values directly from session_state after potential loading
current_revenue = st.session_state.get('revenue_input', 100000)
current_growth_rate_pct = st.session_state.get('growth_rate_input', 2.0)
current_growth_rate = current_growth_rate_pct / 100.0
current_cogs_pct = st.session_state.get('cogs_pct_input', 0.4)
current_dso = st.session_state.get('dso_input', 45)
current_dpo = st.session_state.get('dpo_input', 30)
current_months = st.session_state.get('months_input', 24)


df = generate_cash_flow(current_revenue, current_growth_rate, current_cogs_pct, current_dso, current_dpo, current_months)

# Display results for the current scenario
st.subheader(f"📊 Forecast Results: {st.session_state['current_scenario_name']}")
st.dataframe(df) # Display the full dataframe

# Chart for the current scenario
fig = px.line(
    df, x="Month", y=["Revenue", "Collections", "Payments", "Operating Cash Flow", "Cumulative Cash Balance"],
    title=f"Cash Flow Projections: {st.session_state['current_scenario_name']}", markers=True
)
st.plotly_chart(fig, use_container_width=True)

# Download option for the current scenario
st.download_button(
    f"Download {st.session_state['current_scenario_name']} Forecast as CSV",
    data=df.to_csv(index=False),
    file_name=f"{st.session_state['current_scenario_name'].replace(' ', '_').lower()}_cash_flow_forecast.csv",
    mime="text/csv"
)

# -------------------------------
# Summary Metrics Section
# -------------------------------
st.header("Summary Metrics")

# Calculate summary metrics
total_revenue = df['Revenue'].sum()
total_cogs = df['COGS'].sum()
total_gross_profit = df['Gross Profit'].sum()
ending_cash_balance = df['Cumulative Cash Balance'].iloc[-1]
min_cash_balance = df['Cumulative Cash Balance'].min()
min_cash_month = df.loc[df['Cumulative Cash Balance'].idxmin(), 'Month']

# Display summary metrics using columns for better layout
col_summary1, col_summary2, col_summary3 = st.columns(3)

with col_summary1:
    st.metric("Total Revenue", f"${total_revenue:,.2f}")
    st.metric("Total COGS", f"${total_cogs:,.2f}")

with col_summary2:
    st.metric("Total Gross Profit", f"${total_gross_profit:,.2f}")
    st.metric("Ending Cumulative Cash", f"${ending_cash_balance:,.2f}")

with col_summary3:
    st.metric("Minimum Cumulative Cash", f"${min_cash_balance:,.2f}")
    st.metric("Month of Minimum Cash", f"Month {min_cash_month}")

# -------------------------------
# Scenario Comparison Section
# -------------------------------
st.header("Scenario Comparison")

if len(saved_scenarios) > 1:
    scenarios_to_compare = st.multiselect("Select scenarios to compare", saved_scenarios)

    if scenarios_to_compare:
        comparison_dfs = []
        for scenario_name_compare in scenarios_to_compare:
            scenario_params = st.session_state['scenarios'][scenario_name_compare]
            compare_df = generate_cash_flow(
                scenario_params['revenue'],
                scenario_params['growth_rate'],
                scenario_params['cogs_pct'],
                scenario_params['dso'],
                scenario_params['dpo'],
                scenario_params['months']
            )
            compare_df['Scenario'] = scenario_name_compare
            comparison_dfs.append(compare_df)

        if comparison_dfs:
            combined_df = pd.concat(comparison_dfs)

            # Chart for comparison (Cumulative Cash Balance)
            fig_comparison = px.line(
                combined_df, x="Month", y="Cumulative Cash Balance", color="Scenario",
                title="Cumulative Cash Balance Comparison", markers=True
            )
            st.plotly_chart(fig_comparison, use_container_width=True)

else:
    st.info("Save at least two scenarios to enable comparison.")


# -------------------------------
# Sensitivity Analysis Section
# -------------------------------
st.sidebar.header("Sensitivity Analysis")

col3, col4 = st.sidebar.columns(2)
with col3:
    min_dso = st.number_input("Min DSO", min_value=0, max_value=180, value=st.session_state.get('min_dso_input', 30), step=1, key='min_dso_input')
    min_dpo = st.number_input("Min DPO", min_value=0, max_value=180, value=st.session_state.get('min_dpo_input', 30), step=1, key='min_dpo_input')
with col4:
    max_dso = st.number_input("Max DSO", min_value=0, max_value=180, value=st.session_state.get('max_dso_input', 60), step=1, key='max_dso_input')
    max_dpo = st.number_input("Max DPO", min_value=0, max_value=180, value=st.session_state.get('max_dpo_input', 60), step=1, key='max_dpo_input')

# Added step size input for sensitivity analysis
sensitivity_step = st.sidebar.number_input("Sensitivity Step (Days)", min_value=1, max_value=30, value=st.session_state.get('sensitivity_step_input', 15), step=1, key='sensitivity_step_input')


run_sensitivity = st.sidebar.button("Run Sensitivity Analysis", key='run_sensitivity_button')

if run_sensitivity:
    # Added validation for sensitivity ranges
    if min_dso > max_dso or min_dpo > max_dpo:
        st.sidebar.warning("Minimum values for DSO/DPO should not be greater than maximum values.")
    else:
        st.subheader("🔬 Sensitivity Analysis Results")

        sensitivity_results = {}
        # Use the sensitivity_step input
        for current_dso_sens in range(min_dso, max_dso + 1, sensitivity_step):
            for current_dpo_sens in range(min_dpo, max_dpo + 1, sensitivity_step):
                # Use current input parameters for revenue, growth_rate, cogs_pct, and months
                scenario_df = generate_cash_flow(current_revenue, current_growth_rate, current_cogs_pct, current_dso_sens, current_dpo_sens, current_months)
                sensitivity_results[(current_dso_sens, current_dpo_sens)] = scenario_df["Cumulative Cash Balance"].iloc[-1]

        # Display sensitivity results in a table
        sensitivity_df = pd.DataFrame({
            "DSO": [dso_val for (dso_val, dpo_val) in sensitivity_results.keys()],
            "DPO": [dpo_val for (dso_val, dpo_val) in sensitivity_results.keys()],
            "Ending Cumulative Cash": list(sensitivity_results.values())
        })
        st.dataframe(sensitivity_df)

# -------------------------------
# Data Integration Section
# -------------------------------
st.sidebar.header("Data Integration")
uploaded_file = st.sidebar.file_uploader("Upload Historical Data (CSV)", type=["csv"])

if uploaded_file is not None:
    try:
        historical_df = pd.read_csv(uploaded_file)
        st.sidebar.success("File uploaded successfully!")

        # Display the head of the uploaded data
        st.subheader("Uploaded Historical Data")
        st.dataframe(historical_df.head())

        # Placeholder for future data validation and cleaning
        st.info("Note: Data validation and cleaning steps will be added here in the future.")

    except Exception as e:
        st.sidebar.error(f"Error reading file: {e}")