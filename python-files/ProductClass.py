import pandas as pd
import glob
import matplotlib.pyplot as plt
import seaborn as sns

# File search
zlx_files = glob.glob("zlx*.xlsx")
desi_files = glob.glob("desi*.xlsx")
files_2025 = glob.glob("2025*.xlsx")

desi_file = desi_files[0] if desi_files else None
file_2025 = files_2025[0] if files_2025 else None

# Read and concatenate all zlx files
zlx_dataframes = []
for file in zlx_files:
    df = pd.read_excel(file, usecols=[1, 3, 5, 10, 13, 14],engine='openpyxl')
    df.columns = ['wh_code', 'floor', 'area_type', 'SKU', 'Category', 'Count']
    df = df[df['area_type'].str.strip().str.lower() == "satılabilir depo alanı"]
    df['source_file'] = file  # optional: track source file
    zlx_dataframes.append(df)

df_zlx = pd.concat(zlx_dataframes, ignore_index=True) if zlx_dataframes else None

# Read desi and default volume files
if desi_file:
    df_desi = pd.read_excel(desi_file, usecols=[0, 7])
    df_desi.columns = ['SKU', 'volume']
else:
    df_desi = None

if file_2025:
    df_2025 = pd.read_excel(file_2025, usecols=[0, 1])
    df_2025.columns = ['Category', 'default_volume']
else:
    df_2025 = None

# Merge df_zlx with df_desi using 'SKU'
if df_zlx is not None and df_desi is not None:
    df_merged = pd.merge(df_zlx, df_desi, on='SKU', how='left')
else:
    df_merged = None

# Fill missing volume using 2025 default_volume
if df_merged is not None and df_2025 is not None:
    df_merged = pd.merge(df_merged, df_2025, on='Category', how='left')
    df_merged['volume'] = df_merged['volume'].fillna(df_merged['default_volume'])
    df_merged = df_merged.drop(columns=['default_volume'])

# Compute total volume per row
if df_merged is not None:
    df_merged['total_volume'] = df_merged['Count'] * df_merged['volume']

# Capacity dictionaries
floor_capacities = {
    'MEZ2': 3478,
    'MEZ3': 4169,
    'MEZ4': 11906,
    'MEZ1': 0,  # Update if needed
    'MEZ0': 0   # Update if needed
}
warehouse_capacities = {
    'HB35': 17291,
    '8107': 15744,
}

# Grouping and occupancy calculation
occupancy_results = []

if df_merged is not None:
    df_merged['wh_code'] = df_merged['wh_code'].astype(str).str.zfill(4)  # Normalize codes like '41' -> '0041'
    wh_codes = df_merged['wh_code'].unique()

    for wh_code in wh_codes:
        df_wh = df_merged[df_merged['wh_code'] == wh_code]
        if wh_code == '0041':
            grouped = df_wh.groupby('floor')['total_volume'].sum()
            for floor, total_volume in grouped.items():
                capacity = floor_capacities.get(floor)
                if capacity:
                    occupancy = total_volume * 0.003 / capacity
                    occupancy_results.append((f"{wh_code}-{floor}", total_volume, f"{occupancy:.2%}"))
                else:
                    occupancy_results.append((f"{wh_code}-{floor}", total_volume, "Capacity not found"))
        else:
            total_volume = df_wh['total_volume'].sum()
            capacity = warehouse_capacities.get(wh_code)
            if capacity:
                occupancy = total_volume * 0.003 / capacity
                occupancy_results.append((wh_code, total_volume, f"{occupancy:.2%}"))
            else:
                occupancy_results.append((wh_code, total_volume, "Capacity not found"))

# Print outputs
print("Final Merged DataFrame with filled volumes:")
print(df_merged.head(10000) if df_merged is not None else "No merged data available.")

print("\nDefault Volume Table (2025 file):")
print(df_2025.head() if df_2025 is not None else "No 2025 file found")

print("\nOccupancy per floor or warehouse:")
for loc, volume, occ in occupancy_results:
    print(f"{loc}: M3 = {0.003 * volume:.2f}, Occupancy = {occ}")
# Prepare data (same as before)
data = []
for loc, volume, occ in occupancy_results:
    if occ == "Capacity not found":
        occupancy_val = None
    else:
        occupancy_val = float(occ.strip('%'))
    data.append({
        'location': loc,
        'm3': volume * 0.003,
        'occupancy': occupancy_val
    })

df_plot = pd.DataFrame(data).dropna(subset=['occupancy'])

plt.figure(figsize=(12, 6))
sns.set_style("whitegrid")

barplot = sns.barplot(x='location', y='occupancy', data=df_plot, palette='viridis')

# Get bar containers
bars = barplot.patches

# Add labels exactly centered on bars
for bar, (_, row) in zip(bars, df_plot.iterrows()):
    x = bar.get_x() + bar.get_width() / 2  # Center of bar
    y = bar.get_height() + 1.5              # Slightly above bar top
    label = f"%{int(row['occupancy'])} ({int(row['m3'])} M3)"
    barplot.text(x, y, label, ha='center', fontsize=10, fontweight='bold')

plt.title('Occupancy % by Location with M3 Volume on Top', fontsize=16, fontweight='bold')
plt.ylabel('Occupancy (%)')
plt.xlabel('Location')
plt.ylim(0, max(df_plot['occupancy']) * 1.25)

plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()
