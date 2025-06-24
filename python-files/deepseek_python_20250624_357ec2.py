import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Data Setup
years = np.array([2019, 2020, 2021, 2022, 2023, 2024, 2025])

# 1. Wireless Subscribers (in millions)
wireless_data = {
    'Jio': [370, 410, 430, 450, 480, 510, 540],
    'Airtel': [320, 340, 360, 380, 400, 420, 440],
    'Vi': [410, 380, 340, 300, 270, 240, 210],
    'BSNL/MTNL': [120, 115, 110, 105, 100, 95, 90],
    'Others': [50, 45, 40, 35, 30, 25, 20]
}

# 2. Wireline Subscribers (in millions)
wireline_data = {
    'JioFiber': [1.5, 3.5, 6.0, 9.0, 12.0, 15.0, 18.0],
    'Airtel Xstream': [1.2, 2.5, 4.0, 6.0, 8.0, 10.0, 12.0],
    'BSNL': [8.0, 7.5, 7.0, 6.5, 6.0, 5.5, 5.0],
    'ACT/Tata Play': [3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0],
    'Others': [9.0, 7.0, 5.0, 4.5, 3.0, 2.5, 2.0]
}

# 3. Cable TV (MSO) Subscribers (in millions)
mso_data = {
    'Hathway': [12, 11, 10, 9, 8, 7, 6],
    'DEN': [10, 9, 8, 7, 6, 5, 4],
    'Siti Cable': [8, 7, 6, 5, 4, 3, 2],
    'GTPL': [7, 7, 6, 6, 5, 5, 4],
    'Others': [33, 30, 28, 26, 24, 22, 20]
}

# 4. Satellite (DTH) Subscribers (in millions)
dth_data = {
    'Tata Play': [22, 21, 20, 19, 18, 17, 16],
    'Dish TV': [18, 17, 15, 14, 13, 12, 11],
    'Airtel DTH': [16, 15, 14, 13, 12, 11, 10],
    'Sun Direct': [10, 9, 8, 7, 6, 5, 4],
    'DD Free Dish': [40, 42, 44, 46, 48, 50, 52]
}

# 5. OTT & YouTube Subscribers (in millions)
ott_data = {
    'Disney+ Hotstar': [25, 35, 45, 55, 70, 85, 100],
    'Amazon Prime': [12, 18, 22, 26, 30, 34, 38],
    'Netflix': [3, 5, 8, 12, 15, 18, 22],
    'SonyLIV': [8, 12, 16, 20, 25, 30, 35],
    'ZEE5': [10, 15, 20, 25, 30, 35, 40],
    'YouTube MAU': [225, 280, 340, 400, 460, 520, 580]
}

# Create plots
plt.style.use('ggplot')
fig, axs = plt.subplots(3, 2, figsize=(20, 18))
fig.suptitle('India Telecom & Media Subscribers (2019-2025)', fontsize=20, fontweight='bold')

# Chart 1: Wireless Subscribers (Stacked Area)
df_wireless = pd.DataFrame(wireless_data, index=years)
axs[0, 0].stackplot(years, df_wireless.T, labels=df_wireless.columns, alpha=0.8)
axs[0, 0].set_title('Wireless (Mobile) Subscribers', fontweight='bold')
axs[0, 0].set_ylabel('Subscribers (Millions)')
axs[0, 0].legend(loc='upper left')
axs[0, 0].grid(True, linestyle='--', alpha=0.7)

# Chart 2: Wireline Subscribers (Line Plot)
df_wireline = pd.DataFrame(wireline_data, index=years)
for column in df_wireline.columns:
    axs[0, 1].plot(years, df_wireline[column], marker='o', linewidth=2.5, label=column)
axs[0, 1].set_title('Wireline (Broadband) Subscribers', fontweight='bold')
axs[0, 1].set_ylabel('Subscribers (Millions)')
axs[0, 1].legend()
axs[0, 1].grid(True, linestyle='--', alpha=0.7)

# Chart 3: MSO (Cable TV) Subscribers (Bar Plot)
df_mso = pd.DataFrame(mso_data, index=years)
df_mso.plot(kind='bar', stacked=True, ax=axs[1, 0], width=0.8)
axs[1, 0].set_title('Cable TV (MSO) Subscribers', fontweight='bold')
axs[1, 0].set_ylabel('Subscribers (Millions)')
axs[1, 0].set_xticklabels(years, rotation=0)
axs[1, 0].legend(loc='upper right')
axs[1, 0].grid(axis='y', linestyle='--', alpha=0.7)

# Chart 4: DTH Subscribers (Line Plot)
df_dth = pd.DataFrame(dth_data, index=years)
for column in df_dth.columns:
    axs[1, 1].plot(years, df_dth[column], marker='s', linewidth=2.5, label=column)
axs[1, 1].set_title('Satellite (DTH) Subscribers', fontweight='bold')
axs[1, 1].set_ylabel('Subscribers (Millions)')
axs[1, 1].legend()
axs[1, 1].grid(True, linestyle='--', alpha=0.7)

# Chart 5: OTT Subscribers (Area Plot)
df_ott = pd.DataFrame({k: v for k, v in ott_data.items() if k != 'YouTube MAU'}, index=years)
axs[2, 0].stackplot(years, df_ott.T, labels=df_ott.columns, alpha=0.7)
axs[2, 0].set_title('OTT Platform Subscribers (Paid)', fontweight='bold')
axs[2, 0].set_ylabel('Subscribers (Millions)')
axs[2, 0].legend(loc='upper left')
axs[2, 0].grid(True, linestyle='--', alpha=0.7)

# Chart 6: YouTube MAU (Line Plot)
axs[2, 1].plot(years, ott_data['YouTube MAU'], 'r-', marker='o', linewidth=3, label='YouTube MAU')
axs[2, 1].set_title('YouTube Monthly Active Users (MAU)', fontweight='bold')
axs[2, 1].set_ylabel('Users (Millions)')
axs[2, 1].legend()
axs[2, 1].grid(True, linestyle='--', alpha=0.7)

# Adjust layout
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('india_telecom_media_growth.png', dpi=300, bbox_inches='tight')
plt.show()