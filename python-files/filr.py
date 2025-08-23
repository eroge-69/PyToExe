import pandas as pd
import xlsxwriter

# File path
output_path = "Waterjet_Cost_Calculator_Lantek_KMT_v2.xlsx"
workbook = xlsxwriter.Workbook(output_path)

# Formats
fmt_header = workbook.add_format({"bold": True, "border": 1, "align": "center"})
fmt_money = workbook.add_format({"num_format": "#,##0.00", "border": 1})
fmt_num = workbook.add_format({"num_format": "0.00", "border": 1})
fmt_text = workbook.add_format({"border": 1})
fmt_title = workbook.add_format({"bold": True, "font_size": 14})
fmt_subtitle = workbook.add_format({"italic": True, "font_color": "#555555"})
fmt_total = workbook.add_format({"bold": True, "num_format": "#,##0.00", "border": 1})

# TECH sheet
ws_tech = workbook.add_worksheet("TECH")
ws_tech.write("A1", "Cutting Parameters (for reference)", fmt_title)
ws_tech.write("A2", "Provided by user. Edit if needed.", fmt_subtitle)
ws_tech.write_row("A4", ["Technical Parameter", "Value", "Notes"], fmt_header)

tech_vals = [
    ("Pressure_bar", 3500, "Intensifier set pressure."),
    ("Orifice_mm", 0.23, "Orifice diameter (mm)."),
    ("Nozzle_mm", 0.5, "Mixing tube/nozzle diameter (mm)."),
    ("Garnet_mesh", "80", "Abrasive mesh size."),
    ("Abrasive_rate_g_per_min", 450, "Abrasive feed rate in grams per minute.")
]

for i, (p, v, n) in enumerate(tech_vals, start=5):
    ws_tech.write(f"A{i}", p, fmt_text)
    if isinstance(v, (int, float)):
        ws_tech.write_number(f"B{i}", v, fmt_num)
    else:
        ws_tech.write(f"B{i}", v, fmt_text)
    ws_tech.write(f"C{i}", n, fmt_text)

ws_tech.write("A11", "Auto-converted Abrasive rate (kg/min)", fmt_text)
ws_tech.write_formula("B11", "=B9/1000", fmt_num)
ws_tech.write("C11", "Reference: kg/min = g/min ÷ 1000", fmt_text)
ws_tech.set_column("A:A", 36)
ws_tech.set_column("B:B", 22)
ws_tech.set_column("C:C", 60)

# INPUTS sheet
ws_in = workbook.add_worksheet("INPUTS")
ws_in.write("A1", "Waterjet Job Cost – Inputs", fmt_title)
ws_in.write("A2", "Tip: Change only values in column B. All costs update automatically.", fmt_subtitle)
ws_in.write_row("A4", ["Parameter", "Value", "Notes"], fmt_header)

inputs = [
    ("Runtime_hours", 27, "Total machine runtime for this job (hours)."),
    ("Abrasive_rate_kg_per_min", None, "Set equal to TECH!B11 (auto from 450 g/min)."),
    ("Abrasive_price_per_kg", 2.50, "Your garnet price (AED per kg)."),
    ("Pump_power_kW", 45, "Average pump power draw (kW)."),
    ("Electricity_rate_per_kWh", 0.45, "Your electricity tariff (AED per kWh)."),
    ("Operator_rate_per_hour", 15, "Operator cost (AED per hour)."),
    ("Maintenance_per_hour", 10, "Maintenance allowance (seals, oil, etc.)."),
    ("Consumables_per_hour", 5, "Nozzle/orifice/misc cost per hour."),
    ("Water_cost_per_hour", 2, "Water cost per hour (water + disposal).")
]

for i, (param, val, note) in enumerate(inputs, start=5):
    ws_in.write(f"A{i}", param, fmt_text)
    if param == "Abrasive_rate_kg_per_min":
        ws_in.write_formula(f"B{i}", "=TECH!B11", fmt_num)
    else:
        ws_in.write_number(f"B{i}", val, fmt_num)
    ws_in.write(f"C{i}", note, fmt_text)

ws_in.set_column("A:A", 28)
ws_in.set_column("B:B", 18)
ws_in.set_column("C:C", 70)

# CALC sheet
ws = workbook.add_worksheet("CALC")
ws.write("A1", "Waterjet Job Cost – Calculations", fmt_title)
ws.write_row("A3", ["Item", "Value"], fmt_header)

base_calcs = [
    ("Runtime (hours)", "=INPUTS!B5"),
    ("Abrasive rate (kg/min)", "=INPUTS!B6"),
    ("Abrasive price (AED/kg)", "=INPUTS!B7"),
    ("Pump power (kW)", "=INPUTS!B8"),
    ("Electricity rate (AED/kWh)", "=INPUTS!B9"),
    ("Operator rate (AED/hr)", "=INPUTS!B10"),
    ("Maintenance (AED/hr)", "=INPUTS!B11"),
    ("Consumables (AED/hr)", "=INPUTS!B12"),
    ("Water cost (AED/hr)", "=INPUTS!B13"),
]

row = 4
for label, formula in base_calcs:
    ws.write(f"A{row}", label, fmt_text)
    ws.write_formula(f"B{row}", formula, fmt_num)
    row += 1

# Derived calcs
ws.write_row(row, 0, ["Calculated Item", "Value"], fmt_header)
row += 1

derived = [
    ("Abrasive used (kg)", "=B4*B5*60"),
    ("Abrasive cost (AED)", "=B12*B6"),
    ("Electricity used (kWh)", "=B4*B7"),
    ("Electricity cost (AED)", "=B14*B8"),
    ("Operator cost (AED)", "=B4*B9"),
    ("Maintenance cost (AED)", "=B4*B10"),
    ("Consumables cost (AED)", "=B4*B11"),
    ("Water cost (AED)", "=B4*B13"),
    ("TOTAL COST (AED)", "=SUM(B15,B16,B17,B18,B19,B20,B21)")
]

for label, formula in derived:
    ws.write(f"A{row}", label, fmt_text)
    fmt = fmt_money if "cost" in label.lower() or "TOTAL" in label else fmt_num
    ws.write_formula(f"B{row}", formula, fmt)
    row += 1

# KPIs
ws.write_row(row, 0, ["KPI", "Value"], fmt_header)
row += 1
ws.write("A{}".format(row), "Cost per hour (AED/hr)", fmt_text)
ws.write_formula("B{}".format(row), "=B22/B4", fmt_money)
row += 1
ws.write("A{}".format(row), "Cost per kg abrasive (AED/kg)", fmt_text)
ws.write_formula("B{}".format(row), "=IF(B12>0,B22/B12,0)", fmt_money)

ws.set_column("A:A", 32)
ws.set_column("B:B", 20)

# QUOTE sheet
ws_q = workbook.add_worksheet("QUOTE")
ws_q.write("A1", "Waterjet Cutting Quotation – Summary", fmt_title)
ws_q.write("A2", "Auto-filled from INPUTS and CALC. Edit only the highlighted input cells.", fmt_subtitle)

ws_q.write("A4", "Material", fmt_text); ws_q.write("B4", "MS (Mild Steel)", fmt_text)
ws_q.write("A5", "Thickness (mm)", fmt_text); ws_q.write_number("B5", 40, fmt_num)
ws_q.write("A6", "Cutting Parameters", fmt_text)
ws_q.write("B6", "3500 bar, Orifice 0.23 mm, Nozzle 0.5 mm, 80 mesh, 450 g/min", fmt_text)

ws_q.write_row("A8", ["Line Item", "Value / Cost (AED)"], fmt_header)
quote_items = [
    ("Runtime (hours)", "=CALC!B4"),
    ("Abrasive used (kg)", "=CALC!B15"),
    ("Abrasive cost", "=CALC!B16"),
    ("Electricity cost", "=CALC!B18"),
    ("Operator cost", "=CALC!B19"),
    ("Maintenance cost", "=CALC!B20"),
    ("Consumables cost", "=CALC!B21"),
    ("Water cost", "=CALC!B22"),
    ("TOTAL COST (AED)", "=CALC!B23")
]

row = 9
for label, formula in quote_items:
    ws_q.write(f"A{row}", label, fmt_text)
    ws_q.write_formula(f"B{row ​:contentReference[oaicite:0]{index=0}​
