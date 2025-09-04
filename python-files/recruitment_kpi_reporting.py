import pandas as pd
import numpy as np
import xlsxwriter

# Create a Pandas Excel writer using XlsxWriter as the engine
writer = pd.ExcelWriter("Recruitment_KPI_Reporting.xlsx", engine='xlsxwriter')

# Example data for Temporary Staffing (Standard)
data_temp_standard = {
    "KPI": [
        "Time-to-Fill (days)",
        "Number of Temps",
        "Assignment Duration (days)",
        "Conversion Rate (%)",
        "Early Termination Rate (%)",
        "Cost Efficiency ($/hour)",
        "Client Satisfaction (1-5)"
    ],
    "Target": [10, 50, 90, 15, 5, 30, 4.5],
    "Actual": [12, 45, 85, 18, 7, 32, 4.2]
}

df_temp_standard = pd.DataFrame(data_temp_standard)
df_temp_standard["Deviation %"] = ((df_temp_standard["Actual"] - df_temp_standard["Target"]) / df_temp_standard["Target"]) * 100

df_temp_standard.to_excel(writer, sheet_name="Temp_Standard", index=False)

# Example data for Permanent Placement (Standard)
data_perm_standard = {
    "KPI": [
        "Time-to-Hire (days)",
        "Cost-per-Hire ($)",
        "Interview-to-Hire Ratio",
        "Retention Rate 12m (%)",
        "Candidate Quality (prob. success %)",
        "Candidate Satisfaction (1-5)",
        "Hiring Manager Satisfaction (1-5)"
    ],
    "Target": [30, 5000, 3, 85, 80, 4.5, 4.5],
    "Actual": [35, 5200, 4, 78, 75, 4.0, 4.3]
}

df_perm_standard = pd.DataFrame(data_perm_standard)
df_perm_standard["Deviation %"] = ((df_perm_standard["Actual"] - df_perm_standard["Target"]) / df_perm_standard["Target"]) * 100

df_perm_standard.to_excel(writer, sheet_name="Perm_Standard", index=False)

# Dashboard Style Data (Temporary Staffing)
data_temp_dashboard = {
    "KPI": ["Time-to-Fill", "Conversion Rate", "Client Satisfaction"],
    "Value": [12, 18, 4.2],
    "Target": [10, 15, 4.5]
}

df_temp_dashboard = pd.DataFrame(data_temp_dashboard)
df_temp_dashboard.to_excel(writer, sheet_name="Temp_Dashboard", index=False)

# Dashboard Style Data (Permanent Placement)
data_perm_dashboard = {
    "KPI": ["Time-to-Hire", "Retention Rate", "Hiring Manager Satisfaction"],
    "Value": [35, 78, 4.3],
    "Target": [30, 85, 4.5]
}

df_perm_dashboard = pd.DataFrame(data_perm_dashboard)
df_perm_dashboard.to_excel(writer, sheet_name="Perm_Dashboard", index=False)

# Save the file
writer.close()
