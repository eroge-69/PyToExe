import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
import sys

# Volitelný dialog pro výběr CSV souboru
if len(sys.argv) < 2:
    import tkinter as tk
    from tkinter import filedialog
    tk.Tk().withdraw()
    csv_path = filedialog.askopenfilename(
        filetypes=[("CSV files", "*.csv")],
        title="Vyber CSV soubor ze Shelly"
    )
    if not csv_path:
        print("Nebyl vybrán žádný soubor.")
        sys.exit(1)
else:
    csv_path = sys.argv[1]

input_csv = Path(csv_path)
if not input_csv.exists():
    print(f"Soubor {input_csv} neexistuje.")
    sys.exit(1)

# === Předzpracování ===
df = pd.read_csv(input_csv)
df['last_changed'] = pd.to_datetime(df['last_changed'])
df['state'] = pd.to_numeric(df['state'], errors='coerce')
df = df.dropna(subset=['state']).sort_values('last_changed')

# === Výpočet energie pro daný typ entity ===
def calculate_energy_for_sensor(df: pd.DataFrame, sensor_suffix: str) -> tuple[pd.DataFrame, float]:
    sensor_df = df[df['entity_id'].str.endswith(sensor_suffix)].copy()
    sensor_df = sensor_df.sort_values('last_changed')
    sensor_df['time_diff_s'] = sensor_df['last_changed'].diff().dt.total_seconds()
    sensor_df['time_diff_s'] = sensor_df['time_diff_s'].fillna(0)
    sensor_df['energy_wh'] = (sensor_df['state'] * sensor_df['time_diff_s']) / 3600
    total_kwh = sensor_df['energy_wh'].sum() / 1000
    return sensor_df, total_kwh

# === Výpočet pro total + fáze
total_df, total_kwh = calculate_energy_for_sensor(df, "total_active_power")
phase_a_df, phase_a_kwh = calculate_energy_for_sensor(df, "phase_a_active_power")
phase_b_df, phase_b_kwh = calculate_energy_for_sensor(df, "phase_b_active_power")
phase_c_df, phase_c_kwh = calculate_energy_for_sensor(df, "phase_c_active_power")

# === Výstupní soubory
start_time = total_df['last_changed'].iloc[0]
end_time = total_df['last_changed'].iloc[-1]

timestamp_now = datetime.now().isoformat(timespec="seconds").replace(":", "-")
start_str = start_time.isoformat().replace(":", "-")
end_str = end_time.isoformat().replace(":", "-")
output_stem = f"{timestamp_now}__{start_str}_to_{end_str}"

output_dir = Path(sys.argv[0]).parent
output_txt = output_dir / f"{output_stem}.txt"
output_png = output_dir / f"{output_stem}.png"

# === Výstup do textového souboru
with open(output_txt, "w", encoding="utf-8") as f:
    f.write(f"Soubor: {input_csv.name}\n")
    f.write(f"Začátek dat: {start_time.isoformat()}\n")
    f.write(f"Konec dat:   {end_time.isoformat()}\n\n")
    f.write(f"Spotřeba total: {total_kwh:.3f} kWh\n")
    f.write(f"Spotřeba fáze A: {phase_a_kwh:.3f} kWh\n")
    f.write(f"Spotřeba fáze B: {phase_b_kwh:.3f} kWh\n")
    f.write(f"Spotřeba fáze C: {phase_c_kwh:.3f} kWh\n")

# === Graf
plt.figure(figsize=(12, 5))
plt.step(total_df['last_changed'], total_df['state'], where='post', label='Total [W]', linewidth=1.5)
if not phase_a_df.empty:
    plt.step(phase_a_df['last_changed'], phase_a_df['state'], where='post', label='Fáze A [W]', alpha=0.6)
if not phase_b_df.empty:
    plt.step(phase_b_df['last_changed'], phase_b_df['state'], where='post', label='Fáze B [W]', alpha=0.6)
if not phase_c_df.empty:
    plt.step(phase_c_df['last_changed'], phase_c_df['state'], where='post', label='Fáze C [W]', alpha=0.6)

plt.xlabel("Čas (UTC)")
plt.ylabel("Výkon [W]")
plt.title("Výkon Shelly čerpadla – total + fáze A/B/C")
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(output_png)

# === Volitelné zobrazení
try:
    plt.show()
except:
    pass

print(f"Hotovo.\nTXT: {output_txt.name}\nPNG: {output_png.name}")
