#!/usr/bin/env python3
"""
Improved Head Injury Report Generator
With NASA/SAE AIS mapping, WSTC probability, HIC15/HIC36/BrIC plots, and clear layout.
"""

import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy.signal import butter, filtfilt
from scipy.spatial.transform import Rotation as R

# ----------- CONFIG -----------
import tkinter as tk
from tkinter import filedialog

# Ask user to select file
root = tk.Tk()
root.withdraw()  # Hide main window
file_path = filedialog.askopenfilename(
    title="Select head impact data file",
    filetypes=[("CSV and TXT files", "*.csv *.txt"), ("All files", "*.*")]
)

if not file_path:
    raise FileNotFoundError("No file selected. Please choose a CSV or TXT file.")

IN_PATH = file_path
#IN_PATH = "head_impact.csv"
#OUT_PDF = "injury_report_professional.pdf"
# Ask user where to save output PDF
save_path = filedialog.asksaveasfilename(
    title="Save injury report as...",
    defaultextension=".pdf",
    filetypes=[("PDF files", "*.pdf")]
)

if not save_path:
    raise FileNotFoundError("No save location chosen. Please select a file name to save the report.")

OUT_PDF = save_path
G2MSS = 9.80665

# Risk thresholds
PEAK_ACCEL_LOW, PEAK_ACCEL_MOD, PEAK_ACCEL_HIGH = 50.0, 80.0, 120.0
PEAK_ANGVEL_LOW, PEAK_ANGVEL_MOD, PEAK_ANGVEL_HIGH = 30.0, 60.0, 100.0
HIC_LOW, HIC_MOD, HIC_HIGH = 250.0, 700.0, 1500.0
BRIC_LOW, BRIC_MOD, BRIC_HIGH = 0.45, 0.7, 1.0

# AIS mapping thresholds
HIC_AIS_THRESH = [0, 250, 500, 1000, 1500, 2000]
BRIC_AIS_THRESH = [0.0, 0.25, 0.35, 0.5, 0.75, 1.0]
PA_AIS_THRESH   = [0, 50, 75, 100, 150, 200]
AV_AIS_THRESH   = [0, 30, 60, 100, 150, 250]

# BrIC denominators
W_CX, W_CY, W_CZ = 66.25, 56.45, 42.87

# ----------- FUNCTIONS -----------

def detect_time_unit_and_convert(t_raw):
    dt_raw = float(np.median(np.diff(t_raw)))
    if dt_raw > 200.0:
        return t_raw * 1e-6, "microseconds (detected)"
    else:
        return t_raw * 1e-3, "milliseconds (detected)"

def compute_hic(a_g, t_s, max_win_s):
    n = len(t_s)
    hic_best, t1_best, t2_best = 0.0, t_s[0], t_s[0]
    a_mid = 0.5*(a_g[:-1] + a_g[1:])
    dt = np.diff(t_s)
    cum_int = np.concatenate(([0.0], np.cumsum(a_mid * dt)))
    j = 0
    for i in range(n-1):
        while j < n-1 and (t_s[j] - t_s[i]) <= max_win_s:
            j += 1
        if j-1 > i:
            t1, t2 = t_s[i], t_s[j-1]
            dur = t2 - t1
            if dur <= 0: continue
            avg_a = (cum_int[j-1] - cum_int[i]) / dur
            hic_val = dur * (avg_a ** 2.5)
            if hic_val > hic_best:
                hic_best, t1_best, t2_best = hic_val, t1, t2
    return hic_best, t1_best, t2_best

def bric_from_components(wx_rad_peak, wy_rad_peak, wz_rad_peak):
    return math.sqrt((wx_rad_peak/W_CX)**2 + (wy_rad_peak/W_CY)**2 + (wz_rad_peak/W_CZ)**2)

def si_to_prob(SI, SI50=1000.0, slope=0.006):
    x = slope * (SI - SI50)
    if x >= 0:
        z = math.exp(-x); p = 1.0 / (1.0 + z)
    else:
        z = math.exp(x); p = z / (1.0 + z)
    return p

def risk_label(val, low, mod, high):
    if val < low: return "Low"
    if val < mod: return "Moderate"
    if val < high: return "High"
    return "Very High"

def map_value_to_AIS(val, breaks):
    for i in range(len(breaks)-1):
        if breaks[i] <= val < breaks[i+1]:
            return i
    return len(breaks)-2

# ----------- LOAD DATA -----------
df = pd.read_csv(IN_PATH)
t_s, time_unit = detect_time_unit_and_convert(df["Time_ms"].values.astype(float))
t_s = t_s - t_s[0]  # zero start
fs_est = 1.0 / np.median(np.diff(t_s))

ax_g, ay_g, az_g = df["ax"].values, df["ay"].values, df["az"].values
wx_deg, wy_deg, wz_deg = df["wx"].values, df["wy"].values, df["wz"].values
wx, wy, wz = np.deg2rad(wx_deg), np.deg2rad(wy_deg), np.deg2rad(wz_deg)

a_res_g = np.sqrt(ax_g**2 + ay_g**2 + az_g**2)
w_res_deg = np.sqrt(wx_deg**2 + wy_deg**2 + wz_deg**2)

alpha_x = np.gradient(wx, t_s)
alpha_y = np.gradient(wy, t_s)
alpha_z = np.gradient(wz, t_s)
alpha_res_deg = np.rad2deg(np.sqrt(alpha_x**2 + alpha_y**2 + alpha_z**2))

# ----------- METRICS -----------
HIC15, h15_t1, h15_t2 = compute_hic(a_res_g, t_s, 0.015)
HIC36, h36_t1, h36_t2 = compute_hic(a_res_g, t_s, 0.036)
BrIC = bric_from_components(np.max(np.abs(wx)), np.max(np.abs(wy)), np.max(np.abs(wz)))
peak_a_g, peak_w_deg, peak_alpha_deg = np.max(a_res_g), np.max(w_res_deg), np.max(alpha_res_deg)
SI_val = np.sum((np.abs(a_res_g)**2.5) * np.diff(t_s, prepend=0))
wstc_prob = si_to_prob(SI_val)

hic_ais = map_value_to_AIS(HIC15, HIC_AIS_THRESH)
bric_ais = map_value_to_AIS(BrIC, BRIC_AIS_THRESH)
pa_ais = map_value_to_AIS(peak_a_g, PA_AIS_THRESH)
av_ais = map_value_to_AIS(peak_w_deg, AV_AIS_THRESH)
composite_ais = int(round(np.mean([hic_ais, bric_ais, pa_ais, av_ais])))

# ----------- PDF REPORT -----------
pdf = PdfPages(OUT_PDF)

# PAGE 1 - SUMMARY TABLE
if wstc_prob < 0.2:
    wstc_comment = "Low risk"
elif wstc_prob < 0.5:
    wstc_comment = "Moderate risk"
else:
    wstc_comment = "High risk"
fig, ax = plt.subplots(figsize=(8.5, 11))
ax.axis('off')
table_data = [
    ["Metric", "Value", "Unit", "Risk", "AIS"],
    ["Samples", len(t_s), "", "", ""],
    ["fs", f"{fs_est:.1f}", "Hz", "", ""],
    ["Peak Linear Accel", f"{peak_a_g:.2f}", "g", risk_label(peak_a_g, PEAK_ACCEL_LOW, PEAK_ACCEL_MOD, PEAK_ACCEL_HIGH), pa_ais],
    ["HIC15", f"{HIC15:.1f}", "", risk_label(HIC15, HIC_LOW, HIC_MOD, HIC_HIGH), hic_ais],
    ["HIC36", f"{HIC36:.1f}", "", risk_label(HIC36, HIC_LOW, HIC_MOD, HIC_HIGH), ""],
    ["BrIC", f"{BrIC:.3f}", "", risk_label(BrIC, BRIC_LOW, BRIC_MOD, BRIC_HIGH), bric_ais],
    ["Peak Angular Vel", f"{peak_w_deg:.1f}", "deg/s", risk_label(peak_w_deg, PEAK_ANGVEL_LOW, PEAK_ANGVEL_MOD, PEAK_ANGVEL_HIGH), av_ais],
    ["Peak Angular Accel", f"{peak_alpha_deg:.1f}", "deg/s²", "", ""],
    ["Gadd SI", f"{SI_val:.1f}", "SI units", "", ""],
    ["WSTC Prob", f"{wstc_prob*100:.1f}% ({wstc_comment})", "", "", ""],
    ["Composite AIS", composite_ais, "", "", ""]
]
table = ax.table(cellText=table_data, loc="center", cellLoc="center", colWidths=[0.28, 0.18, 0.15, 0.2, 0.1])
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1, 1.5)
pdf.savefig(fig)
plt.close()

# PAGE 2 - AIS INTERPRETATION
fig, ax = plt.subplots(figsize=(8.5, 11))
ax.axis('off')
lines = [
    "AIS (Abbreviated Injury Scale) - Head (NASA/SAE approximation):",
    "AIS 0: No injury",
    "AIS 1: Minor",
    "AIS 2: Moderate",
    "AIS 3: Serious",
    "AIS 4: Severe",
    "AIS 5: Critical",
    "",
    "Risk Interpretation (per-parameter):",
    f"- Peak Linear Accel: {risk_label(peak_a_g, PEAK_ACCEL_LOW, PEAK_ACCEL_MOD, PEAK_ACCEL_HIGH)}",
    f"- HIC15: {risk_label(HIC15, HIC_LOW, HIC_MOD, HIC_HIGH)}",
    f"- HIC36: {risk_label(HIC36, HIC_LOW, HIC_MOD, HIC_HIGH)}",
    f"- BrIC: {risk_label(BrIC, BRIC_LOW, BRIC_MOD, BRIC_HIGH)}",
    f"- Peak Angular Velocity: {risk_label(peak_w_deg, PEAK_ANGVEL_LOW, PEAK_ANGVEL_MOD, PEAK_ANGVEL_HIGH)}",
    f"- WSTC Probability: {wstc_comment}"
]

y = 0.95
for line in lines:
    ax.text(0.05, y, line, fontsize=10, va="top")
    y -= 0.04
pdf.savefig(fig)
plt.close()

# PAGE 3 - LINEAR ACCEL
fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(t_s*1000, ax_g, label='ax')
ax.plot(t_s*1000, ay_g, label='ay')
ax.plot(t_s*1000, az_g, label='az')
ax.plot(t_s*1000, a_res_g, label='Resultant', color='k')
ax.set_xlabel("Time (ms)"); ax.set_ylabel("g")
ax.set_title("Linear Acceleration")
ax.legend(); ax.grid(True)
pdf.savefig(fig); plt.close()

# PAGE 4 - ANGULAR VELOCITY
fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(t_s*1000, wx_deg, label='wx')
ax.plot(t_s*1000, wy_deg, label='wy')
ax.plot(t_s*1000, wz_deg, label='wz')
ax.plot(t_s*1000, w_res_deg, label='Resultant', color='k')
ax.set_xlabel("Time (ms)"); ax.set_ylabel("deg/s")
ax.set_title("Angular Velocity")
ax.legend(); ax.grid(True)
pdf.savefig(fig); plt.close()

# PAGE 5 - ANGULAR ACCEL
fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(t_s*1000, alpha_res_deg, color='purple')
ax.set_xlabel("Time (ms)"); ax.set_ylabel("deg/s²")
ax.set_title("Angular Acceleration")
ax.grid(True)
pdf.savefig(fig); plt.close()

# PAGE 6 - HIC WINDOWS
fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(t_s*1000, a_res_g)
ax.axvspan(h15_t1*1000, h15_t2*1000, color='orange', alpha=0.3, label="HIC15")
ax.axvspan(h36_t1*1000, h36_t2*1000, color='purple', alpha=0.2, label="HIC36")
ax.set_xlabel("Time (ms)"); ax.set_ylabel("g")
ax.set_title("HIC Windows")
ax.legend(); ax.grid(True)
pdf.savefig(fig); plt.close()

# PAGE 7 - BrIC PLOT
fig, ax = plt.subplots(figsize=(11, 4))
bric_curve = np.sqrt((np.abs(wx)/W_CX)**2 + (np.abs(wy)/W_CY)**2 + (np.abs(wz)/W_CZ)**2)
ax.plot(t_s*1000, bric_curve)
ax.set_xlabel("Time (ms)"); ax.set_ylabel("BrIC")
ax.set_title("BrIC Over Time")
ax.grid(True)
pdf.savefig(fig); plt.close()

# PAGE 8 - SI PROBABILITY
fig, ax = plt.subplots(figsize=(11, 4))
si_range = np.linspace(0, max(SI_val*1.2, 2000), 300)
si_prob = [si_to_prob(s)*100 for s in si_range]
ax.plot(si_range, si_prob)
ax.axvline(SI_val, color='r', linestyle='--', label=f"Observed SI={SI_val:.1f}")
ax.set_xlabel("Gadd SI"); ax.set_ylabel("Probability (%)")
ax.set_title("WSTC Probability Curve")
ax.legend(); ax.grid(True)
pdf.savefig(fig); plt.close()

pdf.close()
print(f"Report saved: {OUT_PDF}")
