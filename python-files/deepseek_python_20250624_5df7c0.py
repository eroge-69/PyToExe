import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter

# Data Setup
years = np.array([2019, 2020, 2021, 2022, 2023, 2024, 2025])

# Format y-axis labels in millions
def millions_formatter(x, pos):
    return f'{x:,.0f}M'

millions_format = FuncFormatter(millions_formatter)

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

# Create professional-looking charts
plt.style.use('seaborn-v0_8-darkgrid')
fig = plt.figure(figsize=(20, 25), facecolor='#f8f9fa')
fig.suptitle('India Telecom & Media Subscriber Growth (2019-2025)\nPlayer-wise Analysis', 
             fontsize=24, fontweight='bold', y=0.97)

# Define color palettes
telecom_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
broadcast_colors = ['#FF9AA2', '#FFB7B2', '#FFDAC1', '#E2F0CB', '#B5EAD7']
ott_colors = ['#A05195', '#F95D6A', '#FF7C43', '#FFA600', '#00C0AF', '#003F5C']

# Chart 1: Wireless Subscribers (Stacked Area)
ax1 = plt.subplot(3, 2, 1)
df_wireless = pd.DataFrame(wireless_data, index=years)
df_wireless.plot(kind='area', ax=ax1, stacked=True, color=telecom_colors, alpha=0.9, linewidth=0)
ax1.set_title('Wireless (Mobile) Subscribers', fontsize=16, fontweight='bold', pad=15)
ax1.set_ylabel('Subscribers (Millions)', fontsize=12)
ax1.legend(loc='upper left', frameon=True)
ax1.yaxis.set_major_formatter(millions_format)
ax1.grid(True, linestyle='--', alpha=0.7)
ax1.set_ylim(0, 1300)

# Chart 2: Wireline Subscribers (Line)
ax2 = plt.subplot(3, 2, 2)
df_wireline = pd.DataFrame(wireline_data, index=years)
for i, column in enumerate(df_wireline.columns):
    ax2.plot(years, df_wireline[column], marker='o', linewidth=3, 
             label=column, color=telecom_colors[i], markersize=8)
ax2.set_title('Wireline (Broadband) Subscribers', fontsize=16, fontweight='bold', pad=15)
ax2.set_ylabel('Subscribers (Millions)', fontsize=12)
ax2.legend(frameon=True)
ax2.yaxis.set_major_formatter(millions_format)
ax2.grid(True, linestyle='--', alpha=0.7)
ax2.set_ylim(0, 50)

# Chart 3: MSO Subscribers (Stacked Bar)
ax3 = plt.subplot(3, 2, 3)
df_mso = pd.DataFrame(mso_data, index=years)
df_mso.plot(kind='bar', stacked=True, ax=ax3, color=broadcast_colors, width=0.8, alpha=0.9)
ax3.set_title('Cable TV (MSO) Subscribers', fontsize=16, fontweight='bold', pad=15)
ax3.set_ylabel('Subscribers (Millions)', fontsize=12)
ax3.set_xticklabels(years, rotation=0)
ax3.legend(loc='upper right', frameon=True)
ax3.yaxis.set_major_formatter(millions_format)
ax3.grid(axis='y', linestyle='--', alpha=0.7)

# Chart 4: DTH Subscribers (Line)
ax4 = plt.subplot(3, 2, 4)
df_dth = pd.DataFrame(dth_data, index=years)
for i, column in enumerate(df_dth.columns):
    ax4.plot(years, df_dth[column], marker='s', linewidth=3, 
             label=column, color=broadcast_colors[i], markersize=8)
ax4.set_title('Satellite (DTH) Subscribers', fontsize=16, fontweight='bold', pad=15)
ax4.set_ylabel('Subscribers (Millions)', fontsize=12)
ax4.legend(frameon=True)
ax4.yaxis.set_major_formatter(millions_format)
ax4.grid(True, linestyle='--', alpha=0.7)
ax4.set_ylim(0, 120)

# Chart 5: OTT Subscribers (Area)
ax5 = plt.subplot(3, 2, 5)
df_ott = pd.DataFrame({k: v for k, v in ott_data.items() if k != 'YouTube MAU'}, index=years)
df_ott.plot(kind='area', ax=ax5, stacked=True, color=ott_colors[:-1], alpha=0.8, linewidth=0)
ax5.set_title('OTT Platform Subscribers (Paid)', fontsize=16, fontweight='bold', pad=15)
ax5.set_ylabel('Subscribers (Millions)', fontsize=12)
ax5.set_xlabel('Year', fontsize=12)
ax5.legend(loc='upper left', frameon=True)
ax5.yaxis.set_major_formatter(millions_format)
ax5.grid(True, linestyle='--', alpha=0.7)
ax5.set_ylim(0, 250)

# Chart 6: YouTube MAU (Line)
ax6 = plt.subplot(3, 2, 6)
ax6.plot(years, ott_data['YouTube MAU'], marker='D', linewidth=4, 
         color=ott_colors[-1], markersize=8, label='YouTube MAU')
ax6.set_title('YouTube Monthly Active Users (MAU)', fontsize=16, fontweight='bold', pad=15)
ax6.set_ylabel('Users (Millions)', fontsize=12)
ax6.set_xlabel('Year', fontsize=12)
ax6.legend(frameon=True)
ax6.yaxis.set_major_formatter(millions_format)
ax6.grid(True, linestyle='--', alpha=0.7)
ax6.set_ylim(200, 600)

# Add data source and footer
plt.figtext(0.5, 0.01, 'Source: Hypothetical data based on TRAI reports, company disclosures, and industry trends', 
            ha='center', fontsize=10, style='italic')

# Adjust layout and save
plt.tight_layout(rect=[0, 0.03, 1, 0.97])
plt.savefig('india_telecom_media_growth.png', dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.show()