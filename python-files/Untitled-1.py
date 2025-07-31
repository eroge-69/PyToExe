import pandas as pd

# Helper function to map input quarter to column labels
def map_quarter_labels(input_quarter):
    q_part, year_str = input_quarter.split()
    qnum = int(q_part[1:])
    year = int(year_str)

    financial_current = f"{qnum}Q{str(year)[-2:]}"
    financial_prev = f"{qnum - 1 if qnum > 1 else 4}Q{str(year)[-2:] if qnum > 1 else str(year - 1)[-2:]}"
    financial_last = f"{qnum}Q{str(year - 1)[-2:]}cb"

    kpi_current = f"{qnum}Q{str(year)[-2:]}"
    kpi_prev = f"{qnum - 1 if qnum > 1 else 4}Q{str(year)[-2:] if qnum > 1 else str(year - 1)[-2:]}"
    kpi_last = f"{qnum}Q{str(year - 1)[-2:]}"

    return (financial_current, financial_prev, financial_last), (kpi_current, kpi_prev, kpi_last)

# Load Excel file
file_path = r"C:\Users\bianca.prelipcean\OneDrive - Vodafone Group\Desktop\Orange reporting Q3FY25\Q1 FY 2026 Databook KPIs - Excel.xlsx"
financial_df = pd.read_excel(file_path, sheet_name='Europe (excl Spain) - Financial', header=6, engine='openpyxl')
kpi_df = pd.read_excel(file_path, sheet_name='Europe (excl Spain) - KPIs', header=6, engine='openpyxl')

# Map quarters
input_quarter = "Q2 2025"
(fin_curr, fin_prev, fin_last), (kpi_curr, kpi_prev, kpi_last) = map_quarter_labels(input_quarter)

# Extract revenue
romania_revenue = financial_df[financial_df.iloc[:, 1] == 'Romania']
revenue_values = {
    fin_curr: romania_revenue[fin_curr].iloc[0] if fin_curr in financial_df.columns else None,
    fin_prev: romania_revenue[fin_prev].iloc[0] if fin_prev in financial_df.columns else None,
    fin_last: romania_revenue[fin_last].iloc[0] if fin_last in financial_df.columns else None
}

# Extract mobile and fixed broadband accesses
mobile_candidates = kpi_df[kpi_df.iloc[:, 2] == 'Romania']
fixed_candidates = kpi_df[kpi_df.iloc[:, 3] == 'Romania']

mobile_values = {}
fixed_values = {}

if not mobile_candidates.empty:
    row_mobile = mobile_candidates.iloc[0]
    for label in [kpi_curr, kpi_prev, kpi_last]:
        mobile_values[label] = row_mobile[label] if label in kpi_df.columns else None

if not fixed_candidates.empty:
    row_fixed = fixed_candidates.iloc[0]
    for label in [kpi_curr, kpi_prev, kpi_last]:
        fixed_values[label] = row_fixed[label] if label in kpi_df.columns else None

formatted_revenue = {k: float(v) for k, v in revenue_values.items()}
formatted_mobile = {k: float(v) for k, v in mobile_values.items()}
formatted_fixed = {k: float(v) for k, v in fixed_values.items()}
# Display results

print("Revenue:", formatted_revenue)
print("Mobile accesses:", formatted_mobile)
print("Fixed broadband accesses:", formatted_fixed)

# Create a summary DataFrame
result_df = pd.DataFrame({
    "Metric": ["Revenue", "Mobile accesses", "Fixed broadband accesses"],
    fin_curr: [formatted_revenue.get(fin_curr), formatted_mobile.get(kpi_curr), formatted_fixed.get(kpi_curr)],
    fin_prev: [formatted_revenue.get(fin_prev), formatted_mobile.get(kpi_prev), formatted_fixed.get(kpi_prev)],
    fin_last: [formatted_revenue.get(fin_last), formatted_mobile.get(kpi_last), formatted_fixed.get(kpi_last)]
})

result_df['QoQ'] = result_df[fin_curr] - result_df[fin_prev]
result_df['%QoQ'] = ((result_df[fin_curr] - result_df[fin_prev]) / result_df[fin_prev]) * 100
result_df['YoY'] = result_df[fin_curr] - result_df[fin_last]
result_df['%YoY'] = ((result_df[fin_curr] - result_df[fin_last]) / result_df[fin_last]) * 100

# Display the table
print("\nSummary Table:")
print(result_df)
