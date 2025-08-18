import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys # Import sys to access command-line arguments
import IPython.display as display

# Default assumptions
MONTHS = 12
INITIAL_CASH = 100000
INITIAL_AR = 50000
INITIAL_AP = 30000
TAX_RATE = 0.25
INTEREST_RATE = 0.06
BEGINNING_DEBT = 0
INVENTORY_DAYS = 30
INITIAL_INVENTORY = 0


# Sample data (can be overridden)
sales_forecast = [200000] * MONTHS
cogs_forecast = [120000] * MONTHS
opex_forecast = [50000] * MONTHS
capex_forecast = [10000] * MONTHS

def generate_forecasts(initial_sales, initial_cogs, num_months, sales_growth_params, cogs_growth_params):
    """
    Generates monthly sales and COGS forecasts based on growth parameters.

    Args:
        initial_sales: Starting sales value for the first month.
        initial_cogs: Starting COGS value for the first month.
        num_months: The number of months to forecast.
        sales_growth_params: Parameters for sales growth.
                             Can be a single float for compound growth,
                             or a list/array for monthly growth rates.
        cogs_growth_params: Parameters for COGS growth.
                            Can be a single float for compound growth,
                            or a list/array for monthly growth rates.

    Returns:
        Two lists: sales_forecast and cogs_forecast.
    """
    sales_forecast = [initial_sales]
    cogs_forecast = [initial_cogs]

    for i in range(1, num_months):
        # Calculate sales for the current month
        if isinstance(sales_growth_params, (int, float)):
            # Compound growth
            next_sales = sales_forecast[-1] * (1 + sales_growth_params)
        elif isinstance(sales_growth_params, (list, np.ndarray)) and len(sales_growth_params) == num_months:
            # Monthly growth rates or absolute values
            # Assuming growth_params are rates to be applied to previous month
            next_sales = sales_forecast[-1] * (1 + sales_growth_params[i])
        else:
            # Fallback to no growth if sales growth is also invalid
            next_sales = sales_forecast[-1]


        cogs_forecast.append(next_sales)

        # Calculate COGS for the current month
        if isinstance(cogs_growth_params, (int, float)):
            # Compound growth
            next_cogs = cogs_forecast[-1] * (1 + cogs_growth_params)
        elif isinstance(cogs_growth_params, (list, np.ndarray)) and len(cogs_growth_params) == num_months:
            # Monthly growth rates or absolute values
             # Assuming growth_params are rates to be applied to previous month
            next_cogs = cogs_forecast[-1] * (1 + cogs_growth_params[i])
        else:
             # Default to scaling with sales growth if COGS params are not provided or invalid
             if isinstance(sales_growth_params, (int, float)):
                 next_cogs = cogs_forecast[-1] * (1 + sales_growth_params)
             elif isinstance(sales_growth_params, (list, np.ndarray)) and len(sales_growth_params) == num_months:
                  next_cogs = cogs_forecast[-1] * (1 + sales_growth_params[i])
             else:
                  # Fallback to no growth if sales growth is also invalid
                  next_cogs = cogs_forecast[-1]


        cogs_forecast.append(next_cogs)

    return sales_forecast, cogs_forecast


def project_cash_flow(dso, dpo, sales_forecast, cogs_forecast, capex_forecast,
                      initial_cash, initial_ar, initial_ap,
                      tax_rate, interest_rate, beginning_debt,
                      inventory_days, growth_rate, new_debt_schedule=None, principal_repayment_schedule=None,
                      equity_schedule=None, initial_inventory=0, opex_params=None):
    """
    Projects cash balances under given DSO/DPO and other financial assumptions,
    including debt issuance, repayment, equity investments, inventory, and flexible OpEx.
    Returns a DataFrame with monthly projections.
    """
    MONTHS = len(sales_forecast) # Ensure MONTHS matches the forecast length

    df = pd.DataFrame({
        'Month': range(1, MONTHS + 1),
        'Sales': sales_forecast,
        'COGS': cogs_forecast,
        'CapEx': capex_forecast
    })

    # Apply growth rate to Sales and COGS for subsequent months if forecasts are shorter than MONTHS
    if len(sales_forecast) < MONTHS:
        for i in range(len(sales_forecast), MONTHS):
            df.loc[i, 'Sales'] = df.loc[i-1, 'Sales'] * (1 + growth_rate)
            df.loc[i, 'COGS'] = df.loc[i-1, 'COGS'] * (1 + growth_rate) # Assuming COGS grows with sales

    # Calculate OpEx based on opex_params
    df['OpEx'] = 0.0 # Initialize OpEx column
    if isinstance(opex_params, list) and len(opex_params) == MONTHS:
        df['OpEx'] = opex_params # Use provided list of OpEx
    elif isinstance(opex_params, dict) and 'driver' in opex_params and 'percentage' in opex_params:
        driver_col = opex_params['driver']
        percentage = opex_params['percentage']
        if driver_col in df.columns:
            df['OpEx'] = df[driver_col] * percentage
        else:
            print(f"Warning: OpEx driver column '{driver_col}' not found. Using default fixed OpEx.")
            df['OpEx'] = [50000.0] * MONTHS # Fallback to default fixed OpEx
    else:
        print("Warning: Invalid opex_params format. Using default fixed OpEx.")
        df['OpEx'] = [50000.0] * MONTHS # Fallback to default fixed OpEx


    # Calculate AR and AP based on DSO/DPO
    df['AR'] = (df['Sales'] / 365) * dso
    df['AP'] = (df['COGS'] / 365) * dpo

    # Changes in working capital
    df['Delta_AR'] = df['AR'].diff().fillna(df['AR'][0] - initial_ar)
    df['Delta_AP'] = df['AP'].diff().fillna(df['AP'][0] - initial_ap)

    # Add Inventory calculation and Delta_Inventory
    df['Inventory'] = (df['COGS'] / 365) * inventory_days
    df['Delta_Inventory'] = df['Inventory'].diff().fillna(df['Inventory'][0] - initial_inventory)

    # Initialize debt and equity columns
    df['Beginning Debt'] = 0.0
    df.loc[0, 'Beginning Debt'] = beginning_debt
    df['New Debt'] = new_debt_schedule if new_debt_schedule is not None else [0.0] * MONTHS
    df['Principal Repayment'] = principal_repayment_schedule if principal_repayment_schedule is not None else [0.0] * MONTHS
    df['Equity Investment'] = equity_schedule if equity_schedule is not None else [0.0] * MONTHS

    # Calculate financial line items
    df['EBIT'] = df['Sales'] - df['COGS'] - df['OpEx']

    # Calculate Interest Expense based on Beginning Debt
    df['Interest Expense'] = df['Beginning Debt'] * (interest_rate / 12)

    df['Taxable Income'] = df['EBIT'] - df['Interest Expense']
    df['Income Tax'] = df['Taxable Income'].apply(lambda x: max(0, x * tax_rate))

    # Calculate cash flows
    df['Cash from Sales'] = df['Sales'] - df['Delta_AR']
    df['Cash for COGS'] = df['COGS'] - df['Delta_AP'] + df['Delta_Inventory']
    df['Cash for OpEx'] = df['OpEx']
    df['Cash from Operations'] = df['Cash from Sales'] - df['Cash for COGS'] - df['Cash for OpEx']
    df['Cash for CapEx'] = df['CapEx']
    df['Cash for Interest'] = df['Interest Expense']

    # Total Cash Flow
    df['Total Cash Flow'] = df['Cash from Operations'] - df['Cash for CapEx'] - df['Cash for Interest'] - df['Income Tax'] + df['New Debt'] - df['Principal Repayment'] + df['Equity Investment']

    # Cumulative cash balance
    df['Cash_Balance'] = initial_cash
    for i in range(1, len(df)):
        df.loc[i, 'Cash_Balance'] = df.loc[i-1, 'Cash_Balance'] + df.loc[i, 'Total Cash Flow']

    # Update Beginning Debt for the next period
    df['Ending Debt'] = df['Beginning Debt'] + df['New Debt'] - df['Principal Repayment']
    if MONTHS > 1:
         df.loc[1:, 'Beginning Debt'] = df['Ending Debt'].iloc[:-1].values

    return df

def run_sensitivity_analysis(base_dso, base_dpo, variations=5, initial_sales=200000, initial_cogs=120000, num_months=12, sales_growth_params=0.01, cogs_growth_params=0.01, opex_params=None, capex=None, initial_cash=None, initial_ar=None, initial_ap=None, beginning_debt=0, new_debt_schedule=None, principal_repayment_schedule=None, equity_schedule=None, initial_inventory=0,
                             base_tax_rate=None, tax_rate_variations=None,
                             base_interest_rate=None, interest_rate_variations=None,
                             base_inventory_days=None, inventory_days_variations=None):

    num_months = num_months or MONTHS # Use provided num_months or global default
    # Use provided opex_params or default fixed OpEx
    opex_params = opex_params if opex_params is not None else [50000] * num_months
    capex = capex or ([10000] * num_months) # Use provided capex or default
    initial_cash = initial_cash or INITIAL_CASH
    initial_ar = initial_ar or INITIAL_AR
    initial_ap = initial_ap or INITIAL_AP

    dso_range = np.linspace(base_dso * 0.8, base_dso * 1.2, variations)
    dpo_range = np.linspace(base_dpo * 0.8, base_dpo * 1.2, variations)

    # Define sensitivity ranges for new variables if provided
    tax_rate_range = np.linspace(base_tax_rate * 0.8, base_tax_rate * 1.2, tax_rate_variations) if base_tax_rate is not None and tax_rate_variations is not None else [base_tax_rate if base_tax_rate is not None else 0.25]
    interest_rate_range = np.linspace(base_interest_rate * 0.8, base_interest_rate * 1.2, interest_rate_variations) if base_interest_rate is not None and interest_rate_variations is not None else [base_interest_rate if base_interest_rate is not None else 0.06]
    inventory_days_range = np.linspace(base_inventory_days * 0.8, base_inventory_days * 1.2, inventory_days_variations) if base_inventory_days is not None and inventory_days_variations is not None else [base_inventory_days if base_inventory_days is not None else 30]

    # Determine the shape of the results array based on which variables are varied
    result_shape = (len(dso_range), len(dpo_range), len(tax_rate_range), len(interest_rate_range), len(inventory_days_range))
    results = np.zeros(result_shape)

    # Use base debt and equity schedules for sensitivity unless specified
    new_debt_schedule = new_debt_schedule if new_debt_schedule is not None else [0.0] * num_months
    principal_repayment_schedule = principal_repayment_schedule if principal_repayment_schedule is not None else [0.0] * num_months
    equity_schedule = equity_schedule if equity_schedule is not None else [0.0] * num_months


    # Nested loops for each sensitivity variable
    for i, dso in enumerate(dso_range):
        for j, dpo in enumerate(dpo_range):
            for k, tax_rate in enumerate(tax_rate_range):
                for l, interest_rate in enumerate(interest_rate_range):
                    for m, inventory_days in enumerate(inventory_days_range):

                        # Generate forecasts for each sensitivity run (assuming growth is not a sensitivity variable here)
                        sales_forecast, cogs_forecast = generate_forecasts(
                            initial_sales,
                            initial_cogs,
                            num_months,
                            sales_growth_params,
                            cogs_growth_params
                        )

                        # Call project_cash_flow with all relevant parameters
                        df = project_cash_flow(dso, dpo, sales_forecast, cogs_forecast, opex_params, capex,
                                               initial_cash, initial_ar, initial_ap,
                                               tax_rate=tax_rate, # Use the varied tax rate
                                               interest_rate=interest_rate, # Use the varied interest rate
                                               beginning_debt=beginning_debt,
                                               new_debt_schedule=new_debt_schedule,
                                               principal_repayment_schedule=principal_repayment_schedule,
                                               equity_schedule=equity_schedule,
                                               inventory_days=inventory_days, # Use the varied inventory days
                                               initial_inventory=initial_inventory)
                        results[i, j, k, l, m] = df['Cash_Balance'].iloc[-1]  # Final cash balance

    # Return all ranges and the results array
    return dso_range, dpo_range, tax_rate_range, interest_rate_range, inventory_days_range, results

def run_scenarios():
    """
    Runs multiple scenarios and returns a dictionary of DataFrames.
    Includes debt, equity, inventory, and flexible OpEx considerations.
    """
    num_months = 12 # Assuming a fixed forecast horizon for scenarios

    # Example debt, equity, and inventory schedules for scenarios (can be customized)
    base_new_debt = [0.0] * num_months
    base_principal_repayment = [0.0] * num_months
    base_equity_schedule = [0.0] * num_months # Base case no equity
    base_inventory_days = 30 # Base inventory days
    base_initial_inventory = 0 # Base initial inventory
    base_opex_params = [50000.0] * num_months # Base case fixed OpEx
    base_beginning_debt = 100000.0 # Base case initial debt
    base_tax_rate = 0.25
    base_interest_rate = 0.06


    optimistic_new_debt = [50000.0 if m == 1 else 0.0 for m in range(1, num_months + 1)] # Example: Take out 50k in month 1
    optimistic_principal_repayment = [10000.0 if m % 6 == 0 else 0.0 for m in range(1, num_months + 1)] # Example: Repay 10k every 6 months
    optimistic_equity_schedule = [20000.0 if m == 3 or m == 9 else 0.0 for m in range(1, num_months + 1)] # Example: Equity investment in months 3 and 9
    optimistic_inventory_days = 25 # Lower inventory days in optimistic scenario
    optimistic_initial_inventory = 0 # Optimistic initial inventory
    optimistic_opex_params = {'driver': 'Sales', 'percentage': 0.20} # Optimistic case OpEx as % of Sales
    optimistic_beginning_debt = 100000.0 # Optimistic case initial debt
    optimistic_tax_rate = 0.20 # Lower tax rate in optimistic scenario
    optimistic_interest_rate = 0.05 # Lower interest rate in optimistic scenario


    pessimistic_new_debt = [0.0] * num_months
    pessimistic_principal_repayment = [20000.0 if m % 3 == 0 else 0.0 for m in range(1, num_months + 1)] # Example: Higher, more frequent repayment
    pessimistic_equity_schedule = [0.0] * num_months # Pessimistic case no equity
    pessimistic_inventory_days = 40 # Higher inventory days in pessimistic scenario
    pessimistic_initial_inventory = 0 # Pessimistic initial inventory
    pessimistic_opex_params = {'driver': 'Sales', 'percentage': 0.30} # Pessimistic case OpEx as higher % of Sales
    pessimistic_beginning_debt = 150000.0 # Pessimistic case initial debt
    pessimistic_tax_rate = 0.30 # Higher tax rate in pessimistic scenario
    pessimistic_interest_rate = 0.07 # Higher interest rate in pessimistic scenario


    scenarios = {
        'Base': {'dso': 45, 'dpo': 30, 'inventory_days': base_inventory_days, 'sales_growth': 0.01, 'cogs_growth': 0.01, 'capex_multiplier': 1.0,
                 'beginning_debt': base_beginning_debt, 'new_debt_schedule': base_new_debt, 'principal_repayment_schedule': base_principal_repayment,
                 'equity_schedule': base_equity_schedule, 'initial_inventory': base_initial_inventory, 'opex_params': base_opex_params,
                 'tax_rate': base_tax_rate, 'interest_rate': base_interest_rate}, # Added tax and interest rate
        'Optimistic': {'dso': 30, 'dpo': 45, 'inventory_days': optimistic_inventory_days, 'sales_growth': 0.02, 'cogs_growth': 0.015, 'capex_multiplier': 0.9,
                       'beginning_debt': optimistic_beginning_debt, 'new_debt_schedule': optimistic_new_debt, 'principal_repayment_schedule': optimistic_principal_repayment,
                       'equity_schedule': optimistic_equity_schedule, 'initial_inventory': optimistic_initial_inventory, 'opex_params': optimistic_opex_params,
                       'tax_rate': optimistic_tax_rate, 'interest_rate': optimistic_interest_rate}, # Added tax and interest rate
        'Pessimistic': {'dso': 60, 'dpo': 20, 'inventory_days': pessimistic_inventory_days, 'sales_growth': 0.005, 'cogs_growth': 0.008, 'capex_multiplier': 1.1,
                        'beginning_debt': pessimistic_beginning_debt, 'new_debt_schedule': pessimistic_new_debt, 'principal_repayment_schedule': pessimistic_principal_repayment,
                        'equity_schedule': pessimistic_equity_schedule, 'initial_inventory': pessimistic_initial_inventory, 'opex_params': pessimistic_opex_params,
                        'tax_rate': pessimistic_tax_rate, 'interest_rate': pessimistic_interest_rate} # Added tax and interest rate
    }

    results = {}
    initial_sales = 200000 # Assuming a fixed starting point for scenarios
    initial_cogs = 120000 # Assuming a fixed starting point for scenarios
    capex_forecast_base = [10000] * num_months # Base CapEx for scenarios


    for name, params in scenarios.items():
        # Generate forecasts for each scenario
        sales_forecast, cogs_forecast = generate_forecasts(
            initial_sales,
            initial_cogs,
            num_months,
            params['sales_growth'],
            params['cogs_growth']
        )

        adjusted_capex = [c * params['capex_multiplier'] for c in capex_forecast_base]

        df = project_cash_flow(params['dso'], params['dpo'], sales_forecast, cogs_forecast,
                               adjusted_capex, INITIAL_CASH, INITIAL_AR, INITIAL_AP,
                               beginning_debt=params['beginning_debt'],
                               new_debt_schedule=params['new_debt_schedule'],
                               principal_repayment_schedule=params['principal_repayment_schedule'],
                               equity_schedule=params['equity_schedule'],
                               inventory_days=params['inventory_days'],
                               initial_inventory=params['initial_inventory'],
                               opex_params=params['opex_params'],
                               tax_rate=params['tax_rate'], # Passed tax rate
                               interest_rate=params['interest_rate']) # Passed interest rate
        results[name] = df

    return results

def generate_report(df, filename='cash_flow_summary_report.csv'):
    """
    Creates a summary report (table) from a projection DataFrame and provides key summaries.
    Saves the summary table to a CSV file.
    """
    # Select key columns for the main summary table
    summary_cols = ['Month', 'Sales', 'COGS', 'OpEx', 'EBIT',
                    'Beginning Debt', 'New Debt', 'Principal Repayment', 'Ending Debt', 'Interest Expense',
                    'Equity Investment', 'Taxable Income', 'Income Tax', 'Total Cash Flow', 'Cash_Balance']

    # Ensure all summary_cols exist in the DataFrame before selecting
    existing_summary_cols = [col for col in summary_cols if col in df.columns]
    summary = df[existing_summary_cols].round(2)

    print("Cash Flow Projection Summary:")
    display.display(summary)

    # Save summary to CSV
    try:
        summary.to_csv(filename, index=False)
        print(f"\nCash flow summary report saved to {filename}")
    except Exception as e:
        print(f"Error saving summary report to CSV: {e}")


    print("\n--- Key Metrics Summary ---")
    print(f"Final Cash Balance: ${df['Cash_Balance'].iloc[-1]:,.2f}")
    print(f"Average Monthly Total Cash Flow: ${df['Total Cash Flow'].mean():,.2f}")
    if 'Income Tax' in df.columns:
        print(f"Average Monthly Income Tax: ${df['Income Tax'].mean():,.2f}")
    if 'Ending Debt' in df.columns:
        print(f"Final Ending Debt: ${df['Ending Debt'].iloc[-1]:,.2f}")

    # Add new summary statistics
    if 'Delta_Inventory' in df.columns:
        print(f"Average Monthly Change in Inventory: ${df['Delta_Inventory'].mean():,.2f}")
    if 'OpEx' in df.columns:
        print(f"Average Monthly OpEx: ${df['OpEx'].mean():,.2f}")
    if 'New Debt' in df.columns:
         print(f"Total New Debt Issued: ${df['New Debt'].sum():,.2f}")
    if 'Principal Repayment' in df.columns:
         print(f"Total Principal Repaid: ${df['Principal Repayment'].sum():,.2f}")
    if 'Interest Expense' in df.columns:
         print(f"Total Interest Expense: ${df['Interest Expense'].sum():,.2f}")
    if 'Equity Investment' in df.columns:
         print(f"Total Equity Invested: ${df['Equity Investment'].sum():,.2f}")

    print("--------------------------")


def plot_cash_balance(scenario_results, filename='cash_balance_projections.png'):
    """
    Plots cash balance projections for all scenarios and saves to a file.
    """
    plt.figure(figsize=(10, 6))
    for name, df in scenario_results.items():
        plt.plot(df['Month'], df['Cash_Balance'], label=name)
    plt.title('Cash Balance Projections by Scenario')
    plt.xlabel('Month')
    plt.ylabel('Cash Balance ($)')
    plt.legend()
    plt.grid(True)
    plt.savefig(filename) # Save to file
    # plt.show() # Removed individual plot show


def plot_sensitivity_heatmap(dso_range, dpo_range, results, filename='sensitivity_heatmap.png'):
    """
    Plots a heatmap for sensitivity analysis and saves to a file.
    """
    plt.figure(figsize=(8, 6))
    plt.imshow(results, cmap='viridis', extent=[dpo_range.min(), dpo_range.max(), dso_range.min(), dso_range.max()], aspect='auto')
    plt.colorbar(label='Final Cash Balance ($)')
    plt.title('Sensitivity Analysis: DSO vs DPO Impact on Final Cash')
    plt.xlabel('DPO (Days)')
    plt.ylabel('DSO (Days)')
    plt.savefig(filename) # Save to file
    # plt.show() # Removed individual plot show

# New plot for Inventory Levels
def plot_inventory_levels(scenario_results, filename='inventory_levels_by_scenario.png'):
    """
    Plots inventory levels for all scenarios and saves to a file.
    """
    plt.figure(figsize=(10, 6))
    for name, df in scenario_results.items():
        plt.plot(df['Month'], df['Inventory'], label=name)
    plt.title('Inventory Levels by Scenario')
    plt.xlabel('Month')
    plt.ylabel('Inventory Value ($)')
    plt.legend()
    plt.grid(True)
    plt.savefig(filename) # Save to file
    # plt.show() # Removed individual plot show

# New plot for Operating Expenses by Scenario
def plot_opex_by_scenario(scenario_results, filename='opex_by_scenario.png'):
    """
    Plots operating expenses for all scenarios and saves to a file.
    """
    plt.figure(figsize=(10, 6))
    for name, df in scenario_results.items():
        plt.plot(df['Month'], df['OpEx'], label=name)
    plt.title('Operating Expenses by Scenario')
    plt.xlabel('Month')
    plt.ylabel('Operating Expenses ($)')
    plt.legend()
    plt.grid(True)
    plt.savefig(filename) # Save to file
    # plt.show() # Removed individual plot show

# New plot for 3D sensitivity (DSO, DPO, and one other variable)
def plot_sensitivity_3d(dso_range, dpo_range, other_range, results_slice, other_var_name, base_filename='sensitivity_3d'):
    """
    Plots a series of heatmaps for sensitivity analysis across three variables and saves to files.
    """
    num_slices = results_slice.shape[2] # Assuming the third dimension is the 'other' variable

    for i in range(num_slices):
        plt.figure(figsize=(8, 6))
        plt.imshow(results_slice[:, :, i], cmap='viridis', extent=[dpo_range.min(), dpo_range.max(), dso_range.min(), dso_range.max()], aspect='auto')
        plt.colorbar(label='Final Cash Balance ($)')
        # Format the title based on the variable type
        if other_var_name in ['Tax Rate', 'Interest Rate']:
             title_suffix = f"{other_var_name} = {other_range[i]:.2%}" # Format as percentage
        elif other_var_name in ['Inventory Days']:
             title_suffix = f"{other_var_name} = {other_range[i]:.0f} days" # Format as integer days
        else:
            title_suffix = f"{other_var_name} = {other_range[i]:,.2f}" # Default formatting

        plt.title(f'Sensitivity Analysis: DSO vs DPO at {title_suffix}')
        plt.xlabel('DPO (Days)')
        plt.ylabel('DSO (Days)')

        # Create filename based on the slice
        filename = f"{base_filename}_{other_var_name.replace(' ', '_')}_{i}.png"
        plt.savefig(filename) # Save to file
        # plt.show() # Removed individual plot show


def plot_financial_metrics(scenario_results, filename='financial_metrics_dashboard.png'):
    """
    Plots a dashboard of financial metrics for all scenarios and saves to a file.
    """
    # Determine the number of metrics to plot
    metrics_to_plot = ['Cash_Balance', 'Total Cash Flow', 'Ending Debt', 'Income Tax', 'Inventory', 'OpEx']
    num_metrics = len(metrics_to_plot)

    # Calculate the number of rows and columns for subplots
    n_cols = 2 # Number of columns
    n_rows = (num_metrics + n_cols - 1) // n_cols # Calculate rows needed

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(12, n_rows * 4)) # Adjust figure size based on number of rows
    axes = axes.flatten() # Flatten the axes array for easy iteration

    for i, metric in enumerate(metrics_to_plot):
        if metric in scenario_results[list(scenario_results.keys())[0]].columns: # Check if metric exists in DataFrame
            for name, df in scenario_results.items():
                axes[i].plot(df['Month'], df[metric], label=name)
            axes[i].set_title(f'{metric} by Scenario')
            axes[i].set_xlabel('Month')
            axes[i].set_ylabel(metric)
            axes[i].legend()
            axes[i].grid(True)
        else:
            # Hide unused subplots if number of metrics is less than total subplots
            if i < len(axes): # Prevent error if axes is smaller than num_metrics
                 fig.delaxes(axes[i])


    plt.tight_layout() # Adjust layout to prevent overlapping
    plt.savefig(filename) # Save to file
    plt.show() # Show the combined plot

def plot_weighted_average_cash_flow(weighted_avg_df, filename='weighted_average_cash_flow.png'):
    """
    Plots the weighted average cash balance and total cash flow and saves to a file.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(weighted_avg_df['Month'], weighted_avg_df['Weighted_Average_Cash_Balance'], label='Weighted Average Cash Balance')
    plt.plot(weighted_avg_df['Month'], weighted_avg_df['Weighted_Average_Total_Cash_Flow'], label='Weighted Average Total Cash Flow')
    plt.title('Weighted Average Cash Flow Projection')
    plt.xlabel('Month')
    plt.ylabel('Amount ($)')
    plt.legend()
    plt.grid(True)
    plt.savefig(filename) # Save to file
    plt.show()

# Function to read parameters from CSV
def read_parameters_from_csv(filepath):
    """Reads financial parameters from a CSV file."""
    params = {}
    try:
        df = pd.read_csv(filepath)
        # Assuming the CSV has a 'Parameter' and 'Value' column for single values
        if 'Parameter' in df.columns and 'Value' in df.columns:
            for index, row in df.iterrows():
                params[row['Parameter']] = row['Value']

        # Assuming monthly forecasts/schedules are in separate columns named after the metric
        for col in ['Sales', 'COGS', 'OpEx', 'CapEx', 'New Debt', 'Principal Repayment', 'Equity Investment']:
            if col in df.columns:
                 params[col + '_Forecast'] = df[col].tolist()

        # Handle OpEx_Params if specified (e.g., as 'OpEx_Params_Driver' and 'OpEx_Params_Percentage')
        if 'OpEx_Params_Driver' in df.columns and 'OpEx_Params_Percentage' in df.columns:
             params['OpEx_Params'] = {'driver': df['OpEx_Params_Driver'].iloc[0], 'percentage': df['OpEx_Params_Percentage'].iloc[0]}


    except FileNotFoundError:
        print(f"Parameter file not found at {filepath}. Using default parameters.")
        return None # Indicate that file was not found or read
    except Exception as e:
        print(f"Error reading parameter file: {e}. Using default parameters.")
        return None # Indicate error

    return params


def main():
    # Default parameters
    num_months = MONTHS
    initial_cash = INITIAL_CASH
    initial_ar = INITIAL_AR
    initial_ap = INITIAL_AP
    base_tax_rate = TAX_RATE
    base_interest_rate = INTEREST_RATE
    base_beginning_debt = BEGINNING_DEBT
    base_inventory_days = INVENTORY_DAYS
    base_initial_inventory = INITIAL_INVENTORY

    # Default forecasts and schedules (fixed or growth-based)
    sales_growth_rate = 0.01
    cogs_growth_rate = 0.01
    sales_forecast, cogs_forecast = generate_forecasts(200000, 120000, num_months, sales_growth_rate, cogs_growth_rate)
    opex_forecast_default = [50000] * num_months
    capex_forecast_default = [10000] * num_months
    base_new_debt = [0.0] * num_months
    base_principal_repayment = [0.0] * num_months
    base_equity_schedule = [0.0] * num_months
    base_opex_params_main = opex_forecast_default # Default OpEx params

    # Attempt to read parameters from CSV if specified
    input_params = None
    if len(sys.argv) > 1:
        csv_filepath = sys.argv[1]
        input_params = read_parameters_from_csv(csv_filepath)
        if input_params:
             print(f"Using parameters from {csv_filepath}")
             # Update parameters with values from CSV, falling back to defaults if not in CSV
             num_months = int(input_params.get('Months', num_months))
             initial_cash = input_params.get('Initial Cash', initial_cash)
             initial_ar = input_params.get('Initial AR', initial_ar)
             initial_ap = input_params.get('Initial AP', initial_ap)
             base_tax_rate = input_params.get('Tax Rate', base_tax_rate)
             base_interest_rate = input_params.get('Interest Rate', base_interest_rate)
             base_beginning_debt = input_params.get('Beginning Debt', base_beginning_debt)
             base_inventory_days = input_params.get('Inventory Days', base_inventory_days)
             base_initial_inventory = input_params.get('Initial Inventory', base_initial_inventory)

             # Update forecasts/schedules from CSV if available, otherwise use defaults/generated
             sales_forecast = input_params.get('Sales_Forecast', generate_forecasts(input_params.get('Initial Sales', 200000), input_params.get('Initial COGS', 120000), num_months, input_params.get('Sales Growth Rate', 0.01), input_params.get('COGS Growth Rate', 0.01))[0])
             cogs_forecast = input_params.get('COGS_Forecast', generate_forecasts(input_params.get('Initial Sales', 200000), input_params.get('Initial COGS', 120000), num_months, input_params.get('Sales Growth Rate', 0.01), input_params.get('COGS Growth Rate', 0.01))[1])
             opex_forecast = input_params.get('OpEx_Forecast', [input_params.get('Default OpEx', 50000)] * num_months if 'OpEx_Params' not in input_params else None) # Use Default OpEx if not provided as list or params
             capex_forecast = input_params.get('CapEx_Forecast', [input_params.get('Default CapEx', 10000)] * num_months)
             base_new_debt = input_params.get('New Debt_Forecast', base_new_debt)
             base_principal_repayment = input_params.get('Principal Repayment_Forecast', base_principal_repayment)
             base_equity_schedule = input_params.get('Equity Investment_Forecast', base_equity_schedule)
             base_opex_params_main = input_params.get('OpEx_Params', opex_forecast if opex_forecast is not None else base_opex_params_main) # Use OpEx_Params if provided, else list forecast, else default fixed

             # Ensure forecast lists match num_months, pad with growth if necessary (simple approach)
             while len(sales_forecast) < num_months:
                 last_sales = sales_forecast[-1]
                 growth_rate = input_params.get('Sales Growth Rate', 0.01) if isinstance(input_params.get('Sales Growth Rate', 0.01), (int,float)) else 0.01 # Use compound rate
                 sales_forecast.append(last_sales * (1 + growth_rate))
             while len(cogs_forecast) < num_months:
                  last_cogs = cogs_forecast[-1]
                  growth_rate = input_params.get('COGS Growth Rate', 0.01) if isinstance(input_params.get('COGS Growth Rate', 0.01), (int,float)) else 0.01 # Use compound rate
                  cogs_forecast.append(last_cogs * (1 + growth_rate))
             # Pad other schedules with zeros if shorter than num_months
             for schedule_name in ['base_new_debt', 'base_principal_repayment', 'base_equity_schedule', 'capex_forecast']:
                  current_schedule = locals()[schedule_name]
                  while len(current_schedule) < num_months:
                       current_schedule.append(0.0)
                  locals()[schedule_name] = current_schedule # Update local variable

             # Special handling for OpEx params if it's a list and needs padding
             if isinstance(base_opex_params_main, list):
                 while len(base_opex_params_main) < num_months:
                     base_opex_params_main.append(base_opex_params_main[-1] if base_opex_params_main else 50000.0) # Pad with last value or default


        else:
             print("Using default parameters and forecasts.")

    else:
        print("No parameter CSV file specified. Using default parameters and forecasts.")


    # Base projection
    base_df = project_cash_flow(45, 30, sales_forecast, cogs_forecast, capex_forecast,
                                initial_cash, initial_ar, initial_ap,
                                tax_rate=base_tax_rate,
                                interest_rate=base_interest_rate,
                                beginning_debt=base_beginning_debt,
                                inventory_days=base_inventory_days,
                                growth_rate=0.02, # Using a fixed growth rate for project_cash_flow (forecasts are already generated)
                                new_debt_schedule=base_new_debt,
                                principal_repayment_schedule=base_principal_repayment,
                                equity_schedule=base_equity_schedule,
                                initial_inventory=base_initial_inventory,
                                opex_params=base_opex_params_main)

    generate_report(base_df, filename='base_case_summary_report.csv') # Save base case report


    # Scenario analysis
    # Need to potentially define scenarios based on loaded parameters or keep them fixed for now
    # Keeping scenarios fixed as per previous implementation for now.
    scenario_results = run_scenarios() # This will use its own internally defined scenarios


    # Define scenario probabilities
    scenario_probabilities = {
        'Base': 0.5,
        'Optimistic': 0.3,
        'Pessimistic': 0.2
    }

    # Calculate weighted average cash flow
    weighted_avg_data = {}
    # Check if scenario results are available and have consistent length
    if scenario_results and all(len(df) == MONTHS for df in scenario_results.values()):
        for name, df in scenario_results.items():
            probability = scenario_probabilities.get(name, 0) # Get probability, default to 0 if not found
            weighted_avg_data[name + '_Weighted_Cash_Balance'] = df['Cash_Balance'] * probability
            weighted_avg_data[name + '_Weighted_Total_Cash_Flow'] = df['Total Cash Flow'] * probability


        # Create a DataFrame for weighted averages
        weighted_avg_df = pd.DataFrame(weighted_avg_data)
        weighted_avg_df['Month'] = scenario_results[list(scenario_results.keys())[0]]['Month'] # Use Month column from one of the scenarios

        # Calculate the sum of weighted cash balances and total cash flows across all scenarios
        weighted_avg_df['Weighted_Average_Cash_Balance'] = weighted_avg_df.filter(like='_Weighted_Cash_Balance').sum(axis=1)
        weighted_avg_df['Weighted_Average_Total_Cash_Flow'] = weighted_avg_df.filter(like='_Weighted_Total_Cash_Flow').sum(axis=1)

        # Print or visualize the weighted average
        print("\n--- Weighted Average Cash Flow ---")
        display.display(weighted_avg_df[['Month', 'Weighted_Average_Cash_Balance', 'Weighted_Average_Total_Cash_Flow']].round(2))
        print(f"\nFinal Weighted Average Cash Balance: ${weighted_avg_df['Weighted_Average_Cash_Balance'].iloc[-1]:,.2f}")
        print(f"Average Monthly Weighted Average Total Cash Flow: ${weighted_avg_df['Weighted_Average_Total_Cash_Flow'].mean():,.2f}")

        plot_weighted_average_cash_flow(weighted_avg_df, filename='weighted_average_cash_flow.png') # Plot weighted average cash flow and save
    else:
        print("Scenario results are not available or have inconsistent lengths. Cannot calculate weighted average.")


    plot_financial_metrics(scenario_results, filename='financial_metrics_dashboard.png') # Plot the combined dashboard and save


    # Sensitivity analysis: Vary Tax Rate
    # Use base parameters for sensitivity analysis unless overridden by input_params
    sens_base_tax_rate = input_params.get('Tax Rate', base_tax_rate) if input_params else base_tax_rate
    sens_base_interest_rate = input_params.get('Interest Rate', base_interest_rate) if input_params else base_interest_rate
    sens_base_inventory_days = input_params.get('Inventory Days', base_inventory_days) if input_params else base_inventory_days
    sens_beginning_debt = input_params.get('Beginning Debt', base_beginning_debt) if input_params else base_beginning_debt
    sens_new_debt = input_params.get('New Debt_Forecast', base_new_debt) if input_params else base_new_debt
    sens_principal_repayment = input_params.get('Principal Repayment_Forecast', base_principal_repayment) if input_params else base_principal_repayment
    sens_equity_schedule = input_params.get('Equity Investment_Forecast', base_equity_schedule) if input_params else base_equity_schedule
    sens_initial_inventory = input_params.get('Initial Inventory', base_initial_inventory) if input_params else base_initial_inventory
    sens_opex_params = input_params.get('OpEx_Params', base_opex_params_main) if input_params else base_opex_params_main


    dso_range_tax, dpo_range_tax, tax_rate_range_sens, interest_rate_range_sens_dummy, inventory_days_range_sens_dummy, sens_results_tax = run_sensitivity_analysis(
        base_dso=45, base_dpo=30, variations=5, # Vary DSO and DPO
        base_tax_rate=sens_base_tax_rate, tax_rate_variations=3, # Vary Tax Rate over 3 levels
        initial_sales=sales_forecast[0] if sales_forecast else 200000, # Use first month's sales or default
        initial_cogs=cogs_forecast[0] if cogs_forecast else 120000, # Use first month's COGS or default
        num_months=MONTHS,
        sales_growth_params=input_params.get('Sales Growth Rate', 0.01) if input_params else 0.01, # Use growth rate from params or default
        cogs_growth_params=input_params.get('COGS Growth Rate', 0.01) if input_params else 0.01, # Use growth rate from params or default
        opex_params=sens_opex_params,
        capex=capex_forecast,
        beginning_debt=sens_beginning_debt,
        new_debt_schedule=sens_new_debt,
        principal_repayment_schedule=sens_principal_repayment,
        equity_schedule=sens_equity_schedule,
        base_inventory_days=sens_base_inventory_days, # Use base inventory days
        initial_inventory=sens_initial_inventory,
        base_interest_rate=sens_base_interest_rate # Use base interest rate
    )

    # Plot 3D sensitivity (DSO, DPO, and Tax Rate) and save
    plot_sensitivity_3d(dso_range_tax, dpo_range_tax, tax_rate_range_sens, sens_results_tax[:, :, :, 0, 0], 'Tax Rate', base_filename='sensitivity_tax')

    # Sensitivity analysis: Vary Interest Rate
    dso_range_interest, dpo_range_interest, tax_rate_range_sens_dummy, interest_rate_range_sens, inventory_days_range_sens_dummy, sens_results_interest = run_sensitivity_analysis(
        base_dso=45, base_dpo=30, variations=5, # Vary DSO and DPO
        base_interest_rate=sens_base_interest_rate, interest_rate_variations=3, # Vary Interest Rate over 3 levels
        initial_sales=sales_forecast[0] if sales_forecast else 200000, # Use first month's sales or default
        initial_cogs=cogs_forecast[0] if cogs_forecast else 120000, # Use first month's COGS or default
        num_months=MONTHS,
        sales_growth_params=input_params.get('Sales Growth Rate', 0.01) if input_params else 0.01, # Use growth rate from params or default
        cogs_growth_params=input_params.get('COGS Growth Rate', 0.01) if input_params else 0.01, # Use growth rate from params or default
        opex_params=sens_opex_params,
        capex=capex_forecast,
        beginning_debt=sens_beginning_debt,
        new_debt_schedule=sens_new_debt,
        principal_repayment_schedule=sens_principal_repayment,
        equity_schedule=sens_equity_schedule,
        base_inventory_days=sens_base_inventory_days, # Use base inventory days
        initial_inventory=sens_initial_inventory,
        base_tax_rate=sens_base_tax_rate # Use base tax rate
    )

    # Plot 3D sensitivity (DSO, DPO, and Interest Rate) and save
    plot_sensitivity_3d(dso_range_interest, dpo_range_interest, interest_rate_range_sens, sens_results_interest[:, :, 0, :, 0], 'Interest Rate', base_filename='sensitivity_interest_rate')

    # Sensitivity analysis: Vary Inventory Days
    dso_range_inv, dpo_range_inv, tax_rate_range_sens_dummy, interest_rate_range_sens_dummy, inventory_days_range_sens, sens_results_inv = run_sensitivity_analysis(
        base_dso=45, base_dpo=30, variations=5, # Vary DSO and DPO
        base_inventory_days=sens_base_inventory_days, inventory_days_variations=3, # Vary Inventory Days over 3 levels
        initial_sales=sales_forecast[0] if sales_forecast else 200000, # Use first month's sales or default
        initial_cogs=cogs_forecast[0] if cogs_forecast else 120000, # Use first month's COGS or default
        num_months=MONTHS,
        sales_growth_params=input_params.get('Sales Growth Rate', 0.01) if input_params else 0.01, # Use growth rate from params or default
        cogs_growth_params=input_params.get('COGS Growth Rate', 0.01) if input_params else 0.01, # Use growth rate from params or default
        opex_params=sens_opex_params,
        capex=capex_forecast,
        beginning_debt=sens_beginning_debt,
        new_debt_schedule=sens_new_debt,
        principal_repayment_schedule=sens_principal_repayment,
        equity_schedule=sens_equity_schedule,
        initial_inventory=sens_initial_inventory,
        base_tax_rate=sens_base_tax_rate, # Use base tax rate
        base_interest_rate=sens_base_interest_rate # Use base interest rate
    )

    # Plot 3D sensitivity (DSO, DPO, and Inventory Days) and save
    plot_sensitivity_3d(dso_range_inv, dpo_range_inv, inventory_days_range_sens, sens_results_inv[:, :, 0, 0, :], 'Inventory Days', base_filename='sensitivity_inventory_days')


if __name__ == "__main__":
    main()
