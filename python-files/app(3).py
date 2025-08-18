import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Default assumptions
MONTHS = 12
INITIAL_CASH = 100000
INITIAL_AR = 50000
INITIAL_AP = 30000

# Sample data (can be overridden)
sales_forecast = [200000] * MONTHS
cogs_forecast = [120000] * MONTHS
opex_forecast = [50000] * MONTHS
capex_forecast = [10000] * MONTHS

def project_cash_flow(dso, dpo, sales, cogs, opex, capex, initial_cash, initial_ar, initial_ap):
    df = pd.DataFrame({
        'Month': range(1, MONTHS + 1),
        'Sales': sales,
        'COGS': cogs,
        'OpEx': opex,
        'CapEx': capex
    })
    df['AR'] = (df['Sales'] / 365) * dso
    df['AP'] = (df['COGS'] / 365) * dpo
    df['Delta_AR'] = df['AR'].diff().fillna(df['AR'][0] - initial_ar)
    df['Delta_AP'] = df['AP'].diff().fillna(df['AP'][0] - initial_ap)
    df['OCF'] = df['Sales'] - df['COGS'] - df['OpEx'] - df['Delta_AR'] + df['Delta_AP'] - df['CapEx']
    df['Cash_Balance'] = initial_cash
    for i in range(1, len(df)):
        df.loc[i, 'Cash_Balance'] = df.loc[i-1, 'Cash_Balance'] + df.loc[i, 'OCF']
    return df

def run_sensitivity_analysis(base_dso, base_dpo, variations=5, sales=None, cogs=None, opex=None, capex=None, initial_cash=None, initial_ar=None, initial_ap=None):
    sales = sales or sales_forecast
    cogs = cogs or cogs_forecast
    opex = opex or opex_forecast
    capex = capex or capex_forecast
    initial_cash = initial_cash or INITIAL_CASH
    initial_ar = initial_ar or INITIAL_AR
    initial_ap = initial_ap or INITIAL_AP

    dso_range = np.linspace(base_dso * 0.8, base_dso * 1.2, variations)
    dpo_range = np.linspace(base_dpo * 0.8, base_dpo * 1.2, variations)
    results = np.zeros((variations, variations))
    for i, dso in enumerate(dso_range):
        for j, dpo in enumerate(dpo_range):
            df = project_cash_flow(dso, dpo, sales, cogs, opex, capex, initial_cash, initial_ar, initial_ap)
            results[i, j] = df['Cash_Balance'].iloc[-1]  # Final cash balance
    return dso_range, dpo_range, results

def run_scenarios():
    """
    Runs multiple scenarios and returns a dictionary of DataFrames.
    """
    scenarios = {
        'Base': {'dso': 45, 'dpo': 30, 'sales_multiplier': 1.0, 'capex_multiplier': 1.0},
        'Optimistic': {'dso': 30, 'dpo': 45, 'sales_multiplier': 1.1, 'capex_multiplier': 0.9},
        'Pessimistic': {'dso': 60, 'dpo': 20, 'sales_multiplier': 0.9, 'capex_multiplier': 1.1}
    }

    results = {}
    for name, params in scenarios.items():
        adjusted_sales = [s * params['sales_multiplier'] for s in sales_forecast]
        adjusted_cogs = [c * params['sales_multiplier'] for c in cogs_forecast] # Assuming COGS scales with sales
        adjusted_opex = opex_forecast # Assuming OpEx is fixed
        adjusted_capex = [c * params['capex_multiplier'] for c in capex_forecast]

        df = project_cash_flow(params['dso'], params['dpo'], adjusted_sales, adjusted_cogs, adjusted_opex,
                               adjusted_capex, INITIAL_CASH, INITIAL_AR, INITIAL_AP)
        results[name] = df

    return results


def generate_report(df):
    """
    Creates a summary report (table) from a projection DataFrame.
    """
    summary = df[['Month', 'Sales', 'OCF', 'Cash_Balance']].round(2)
    print("Cash Flow Projection Summary:")
    print(summary)
    print(f"\nFinal Cash Balance: ${df['Cash_Balance'].iloc[-1]:,.2f}")
    print(f"Average Monthly OCF: ${df['OCF'].mean():,.2f}")

def plot_cash_balance(scenario_results):
    """
    Plots cash balance projections for all scenarios.
    """
    plt.figure(figsize=(10, 6))
    for name, df in scenario_results.items():
        plt.plot(df['Month'], df['Cash_Balance'], label=name)
    plt.title('Cash Balance Projections by Scenario')
    plt.xlabel('Month')
    plt.ylabel('Cash Balance ($)')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_sensitivity_heatmap(dso_range, dpo_range, results):
    """
    Plots a heatmap for sensitivity analysis.
    """
    plt.figure(figsize=(8, 6))
    plt.imshow(results, cmap='viridis', extent=[dpo_range.min(), dpo_range.max(), dso_range.min(), dso_range.max()], aspect='auto')
    plt.colorbar(label='Final Cash Balance ($)')
    plt.title('Sensitivity Analysis: DSO vs DPO Impact on Final Cash')
    plt.xlabel('DPO (Days)')
    plt.ylabel('DSO (Days)')
    plt.show()


if __name__ == "__main__":
    # Base projection
    base_df = project_cash_flow(45, 30, sales_forecast, cogs_forecast, opex_forecast, capex_forecast,
                                INITIAL_CASH, INITIAL_AR, INITIAL_AP)
    generate_report(base_df)

    # Scenario analysis
    scenario_results = run_scenarios()
    plot_cash_balance(scenario_results)

    # Sensitivity analysis
    dso_range, dpo_range, sens_results = run_sensitivity_analysis(45, 30)
    plot_sensitivity_heatmap(dso_range, dpo_range, sens_results)
