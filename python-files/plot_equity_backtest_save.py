import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Output directory
outdir = r'd:\code_repo\amibroker\Results\ReportsGraph'
os.makedirs(outdir, exist_ok=True)

# Load the CSV
file = r'd:\code_repo\amibroker\Results\Results.csv'
df = pd.read_csv(file)

# Convert date columns to datetime
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
if 'Ex. date' in df.columns:
    df['Ex. date'] = pd.to_datetime(df['Ex. date'], errors='coerce')

# 1. Equity Curve (Cumulative Profit over Time)
plt.figure(figsize=(10,5))
plt.plot(df['Date'], df['Cum. Profit'])
plt.title('Equity Curve (Cumulative Profit)')
plt.xlabel('Date (YYYY-MM-DD)')
plt.ylabel('Cumulative Profit (INR)')
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(outdir, 'equity_curve.png'))
plt.close()

# 2. Profit/Loss Distribution
plt.figure(figsize=(8,5))
sns.histplot(df['Profit'], bins=50, kde=True)
plt.title('Profit/Loss Distribution per Trade')
plt.xlabel('Profit (INR)')
plt.ylabel('Frequency (Count)')
plt.tight_layout()
plt.savefig(os.path.join(outdir, 'profit_loss_distribution.png'))
plt.close()

# 3. Win/Loss Pie Chart
win = (df['Profit'] > 0).sum()
loss = (df['Profit'] <= 0).sum()
plt.figure(figsize=(5,5))
plt.pie([win, loss], labels=['Win', 'Loss'], autopct='%1.1f%%', colors=['green', 'red'])
plt.title('Win/Loss Ratio')
plt.tight_layout()
plt.savefig(os.path.join(outdir, 'win_loss_pie.png'))
plt.close()

# 4. Drawdown Curve (from Cum. Profit)
dd = df['Cum. Profit'] - df['Cum. Profit'].cummax()
plt.figure(figsize=(10,5))
plt.plot(df['Date'], dd, color='orange')
plt.title('Drawdown Curve')
plt.xlabel('Date (YYYY-MM-DD)')
plt.ylabel('Drawdown (INR)')
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(outdir, 'drawdown_curve.png'))
plt.close()

# 5. Trade Duration Distribution
plt.figure(figsize=(8,5))
sns.histplot(df['# bars'], bins=30, kde=False)
plt.title('Trade Duration Distribution (# bars)')
plt.xlabel('Number of Bars')
plt.ylabel('Frequency (Count)')
plt.tight_layout()
plt.savefig(os.path.join(outdir, 'trade_duration_distribution.png'))
plt.close()

# 6. MAE/MFE Scatter Plot
plt.figure(figsize=(8,6))
plt.scatter(df['MAE'], df['MFE'], alpha=0.6)
plt.title('MAE vs MFE')
plt.xlabel('MAE (INR)')
plt.ylabel('MFE (INR)')
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(outdir, 'mae_mfe_scatter.png'))
plt.close()

# 7. Profit per Symbol
plt.figure(figsize=(12,6))
symbol_profit = df.groupby('Symbol')['Profit'].sum().sort_values()
symbol_profit.plot(kind='bar')
plt.title('Total Profit per Symbol')
plt.xlabel('Symbol')
plt.ylabel('Total Profit (INR)')
plt.tight_layout()
plt.savefig(os.path.join(outdir, 'profit_per_symbol.png'))
plt.close()

# 8. Profit per Month
if 'Date' in df.columns:
    df['Month'] = df['Date'].dt.to_period('M')
    month_profit = df.groupby('Month')['Profit'].sum()
    plt.figure(figsize=(12,6))
    month_profit.plot(kind='bar')
    plt.title('Profit per Month')
    plt.xlabel('Month (YYYY-MM)')
    plt.ylabel('Total Profit (INR)')
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, 'profit_per_month.png'))
    plt.close()

print('All graphs saved in', outdir)

# PyInstaller command (uncomment to use)
# os.system('python -m pip install pyinstaller')
# os.system('python -m PyInstaller --onefile --noconsole plot_equity_backtest_save.py')
