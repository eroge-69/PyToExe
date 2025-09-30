import pandas as pd
import os

# === STEP 1: Load and clean the CSV ===
csv_path = "Simulação SEM HVAC - PC pala.csv"   # <-- replace with your CSV name
df = pd.read_csv(csv_path, sep=";", decimal=",")
df.columns = df.columns.str.strip()
df["Date/Time"] = df["Date/Time"].str.strip().str.replace("  ", " ", regex=False)

def fix_time(s):
    if "24:00:00" in s:
        date_str, _ = s.split(" ")
        date = pd.to_datetime(date_str, format="%m/%d")
        return date + pd.Timedelta(days=1)
    else:
        return pd.to_datetime(s, format="%m/%d %H:%M:%S")

df["Date/Time"] = df["Date/Time"].apply(fix_time)

# === STEP 2: Save to Excel with a chart ===
folder = os.path.dirname(os.path.abspath(csv_path))
excel_path = os.path.join(folder, "temps.xlsx")

with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:
    df.to_excel(writer, sheet_name="Data", index=False)

    workbook  = writer.book
    worksheet = writer.sheets["Data"]

    # Create a chart object
    chart = workbook.add_chart({"type": "line"})

    # Add series for Outdoor Temp
    chart.add_series({
        "name":       "Outdoor Temp [°C]",
        "categories": ["Data", 1, 0, len(df), 0],  # Date/Time
        "values":     ["Data", 1, 1, len(df), 1],  # Outdoor temp
    })

    # Add series for Zone Mean Temp
    chart.add_series({
        "name":       "Zone Mean Temp [°C]",
        "categories": ["Data", 1, 0, len(df), 0],  # Date/Time
        "values":     ["Data", 1, 2, len(df), 2],  # Zone temp
    })

    # Chart formatting
    chart.set_title({"name": "Outdoor vs Zone Mean Temperature"})
    chart.set_x_axis({"name": "Time"})
    chart.set_y_axis({"name": "Temperature [°C]"})
    chart.set_legend({"position": "bottom"})

    # Insert chart into worksheet
    worksheet.insert_chart("E2", chart)

print(f"Excel file with chart created: {excel_path}")
