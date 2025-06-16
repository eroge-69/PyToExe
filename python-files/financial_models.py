#!/usr/bin/env python3
"""
Comprehensive Financial Models and Projections for KKIP Strategic Blueprint
Creates detailed financial analysis for all three approaches including:
- 20-year financial projections
- Sensitivity analysis
- Scenario planning
- Risk-adjusted returns
- Cash flow models
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set up plotting parameters
plt.style.use('default')
sns.set_palette("husl")

class KKIPFinancialModel:
    def __init__(self):
        self.years = list(range(2025, 2046))  # 20-year projection
        self.usd_to_myr = 4.2  # Exchange rate assumption
        
    def approach_one_model(self):
        """Detailed financial model for Approach One"""
        # Investment schedule (in billions USD)
        investment = {
            2025: 1.5, 2026: 3.2, 2027: 4.8, 2028: 5.1, 
            2029: 3.8, 2030: 2.1, 2031: 0.7
        }
        
        # Revenue ramp-up
        revenue_multipliers = [0, 0, 0.1, 0.3, 0.6, 1.0, 1.0, 1.0, 1.0, 1.0,
                              1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.35, 1.4, 1.45, 1.5, 1.55]
        
        # Operating parameters
        peak_revenue = 21.8  # Billion USD
        operating_margin_target = 0.28
        tax_rate = 0.24
        
        results = []
        cumulative_investment = 0
        
        for i, year in enumerate(self.years):
            # Investment
            annual_investment = investment.get(year, 0)
            cumulative_investment += annual_investment
            
            # Revenue
            revenue = peak_revenue * revenue_multipliers[i]
            
            # Operating costs
            if revenue > 0:
                operating_costs = revenue * (1 - operating_margin_target)
                ebitda = revenue - operating_costs
                depreciation = cumulative_investment * 0.08  # 8% annual depreciation
                ebit = ebitda - depreciation
                tax = max(0, ebit * tax_rate)
                net_income = ebit - tax
            else:
                operating_costs = annual_investment * 0.1  # Development costs
                ebitda = -operating_costs
                depreciation = cumulative_investment * 0.08
                ebit = ebitda - depreciation
                tax = 0
                net_income = ebit
            
            # Cash flow
            operating_cash_flow = net_income + depreciation
            free_cash_flow = operating_cash_flow - annual_investment
            
            # Employment (thousands)
            if revenue > 0:
                employment = min(75, revenue / peak_revenue * 75)
            else:
                employment = annual_investment * 5  # 5k jobs per billion invested
            
            results.append({
                'Year': year,
                'Investment': annual_investment,
                'Cumulative_Investment': cumulative_investment,
                'Revenue': revenue,
                'Operating_Costs': operating_costs,
                'EBITDA': ebitda,
                'EBIT': ebit,
                'Net_Income': net_income,
                'Operating_Cash_Flow': operating_cash_flow,
                'Free_Cash_Flow': free_cash_flow,
                'Employment': employment,
                'Revenue_MYR': revenue * self.usd_to_myr,
                'GDP_Contribution': revenue * 1.2  # Multiplier effect
            })
        
        return pd.DataFrame(results)
    
    def approach_two_model(self):
        """Detailed financial model for Approach Two"""
        # Similar structure to Approach One but with different parameters
        investment = {
            2025: 1.8, 2026: 3.5, 2027: 4.9, 2028: 5.2, 
            2029: 3.6, 2030: 1.9, 2031: 0.3
        }
        
        revenue_multipliers = [0, 0, 0.08, 0.25, 0.55, 0.95, 1.0, 1.0, 1.0, 1.0,
                              1.04, 1.08, 1.12, 1.16, 1.2, 1.24, 1.28, 1.32, 1.36, 1.4, 1.44]
        
        peak_revenue = 21.8
        operating_margin_target = 0.30  # Slightly higher due to premium positioning
        tax_rate = 0.24
        
        results = []
        cumulative_investment = 0
        
        for i, year in enumerate(self.years):
            annual_investment = investment.get(year, 0)
            cumulative_investment += annual_investment
            
            revenue = peak_revenue * revenue_multipliers[i]
            
            if revenue > 0:
                operating_costs = revenue * (1 - operating_margin_target)
                ebitda = revenue - operating_costs
                depreciation = cumulative_investment * 0.08
                ebit = ebitda - depreciation
                tax = max(0, ebit * tax_rate)
                net_income = ebit - tax
            else:
                operating_costs = annual_investment * 0.12  # Higher development costs
                ebitda = -operating_costs
                depreciation = cumulative_investment * 0.08
                ebit = ebitda - depreciation
                tax = 0
                net_income = ebit
            
            operating_cash_flow = net_income + depreciation
            free_cash_flow = operating_cash_flow - annual_investment
            
            if revenue > 0:
                employment = min(58, revenue / peak_revenue * 58)
            else:
                employment = annual_investment * 4.5
            
            results.append({
                'Year': year,
                'Investment': annual_investment,
                'Cumulative_Investment': cumulative_investment,
                'Revenue': revenue,
                'Operating_Costs': operating_costs,
                'EBITDA': ebitda,
                'EBIT': ebit,
                'Net_Income': net_income,
                'Operating_Cash_Flow': operating_cash_flow,
                'Free_Cash_Flow': free_cash_flow,
                'Employment': employment,
                'Revenue_MYR': revenue * self.usd_to_myr,
                'GDP_Contribution': revenue * 1.21
            })
        
        return pd.DataFrame(results)
    
    def approach_three_model(self):
        """Detailed financial model for Approach Three"""
        # Phased investment over 10 years
        investment = {
            2025: 0.8, 2026: 1.2, 2027: 0.8, 2028: 1.1, 2029: 1.5, 
            2030: 1.2, 2031: 0.9, 2032: 0.6, 2033: 0.4, 2034: 0.3
        }
        
        # More gradual ramp-up
        revenue_multipliers = [0, 0, 0.15, 0.35, 0.55, 0.75, 0.9, 1.0, 1.0, 1.0,
                              1.03, 1.06, 1.09, 1.12, 1.15, 1.18, 1.21, 1.24, 1.27, 1.3, 1.33]
        
        peak_revenue = 12.4
        operating_margin_target = 0.32  # Higher margins due to specialization
        tax_rate = 0.24
        
        results = []
        cumulative_investment = 0
        
        for i, year in enumerate(self.years):
            annual_investment = investment.get(year, 0)
            cumulative_investment += annual_investment
            
            revenue = peak_revenue * revenue_multipliers[i]
            
            if revenue > 0:
                operating_costs = revenue * (1 - operating_margin_target)
                ebitda = revenue - operating_costs
                depreciation = cumulative_investment * 0.08
                ebit = ebitda - depreciation
                tax = max(0, ebit * tax_rate)
                net_income = ebit - tax
            else:
                operating_costs = annual_investment * 0.08  # Lower development costs
                ebitda = -operating_costs
                depreciation = cumulative_investment * 0.08
                ebit = ebitda - depreciation
                tax = 0
                net_income = ebit
            
            operating_cash_flow = net_income + depreciation
            free_cash_flow = operating_cash_flow - annual_investment
            
            if revenue > 0:
                employment = min(38, revenue / peak_revenue * 38)
            else:
                employment = annual_investment * 6  # More labor-intensive initially
            
            results.append({
                'Year': year,
                'Investment': annual_investment,
                'Cumulative_Investment': cumulative_investment,
                'Revenue': revenue,
                'Operating_Costs': operating_costs,
                'EBITDA': ebitda,
                'EBIT': ebit,
                'Net_Income': net_income,
                'Operating_Cash_Flow': operating_cash_flow,
                'Free_Cash_Flow': free_cash_flow,
                'Employment': employment,
                'Revenue_MYR': revenue * self.usd_to_myr,
                'GDP_Contribution': revenue * 1.18
            })
        
        return pd.DataFrame(results)
    
    def calculate_roi_metrics(self, df):
        """Calculate ROI and other financial metrics"""
        total_investment = df['Cumulative_Investment'].max()
        total_cash_flows = df['Free_Cash_Flow'].sum()
        
        # NPV calculation (10% discount rate)
        discount_rate = 0.10
        npv = 0
        for i, cash_flow in enumerate(df['Free_Cash_Flow']):
            npv += cash_flow / ((1 + discount_rate) ** i)
        
        # IRR approximation
        irr = (total_cash_flows / total_investment) ** (1/20) - 1
        
        # Payback period
        cumulative_cf = 0
        payback_period = 20
        for i, cf in enumerate(df['Free_Cash_Flow']):
            cumulative_cf += cf
            if cumulative_cf >= total_investment:
                payback_period = i + 1
                break
        
        return {
            'Total_Investment': total_investment,
            'Total_Cash_Flows': total_cash_flows,
            'NPV': npv,
            'IRR': irr,
            'ROI_20_Year': (total_cash_flows / total_investment) * 100,
            'Payback_Period': payback_period
        }
    
    def sensitivity_analysis(self, base_model, approach_name):
        """Perform sensitivity analysis on key variables"""
        scenarios = {
            'Optimistic': {'revenue_mult': 1.2, 'cost_mult': 0.9, 'investment_mult': 0.95},
            'Base': {'revenue_mult': 1.0, 'cost_mult': 1.0, 'investment_mult': 1.0},
            'Conservative': {'revenue_mult': 0.8, 'cost_mult': 1.1, 'investment_mult': 1.1},
            'Pessimistic': {'revenue_mult': 0.6, 'cost_mult': 1.2, 'investment_mult': 1.2}
        }
        
        results = {}
        for scenario, multipliers in scenarios.items():
            df_scenario = base_model.copy()
            df_scenario['Revenue'] *= multipliers['revenue_mult']
            df_scenario['Operating_Costs'] *= multipliers['cost_mult']
            df_scenario['Investment'] *= multipliers['investment_mult']
            df_scenario['Cumulative_Investment'] = df_scenario['Investment'].cumsum()
            
            # Recalculate financial metrics
            for i in range(len(df_scenario)):
                if df_scenario.iloc[i]['Revenue'] > 0:
                    ebitda = df_scenario.iloc[i]['Revenue'] - df_scenario.iloc[i]['Operating_Costs']
                    depreciation = df_scenario.iloc[i]['Cumulative_Investment'] * 0.08
                    ebit = ebitda - depreciation
                    tax = max(0, ebit * 0.24)
                    net_income = ebit - tax
                    operating_cash_flow = net_income + depreciation
                    free_cash_flow = operating_cash_flow - df_scenario.iloc[i]['Investment']
                    
                    df_scenario.at[i, 'EBITDA'] = ebitda
                    df_scenario.at[i, 'EBIT'] = ebit
                    df_scenario.at[i, 'Net_Income'] = net_income
                    df_scenario.at[i, 'Operating_Cash_Flow'] = operating_cash_flow
                    df_scenario.at[i, 'Free_Cash_Flow'] = free_cash_flow
            
            metrics = self.calculate_roi_metrics(df_scenario)
            results[scenario] = metrics
        
        return results
    
    def create_visualizations(self, df1, df2, df3):
        """Create comprehensive financial visualizations"""
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('KKIP Financial Projections Comparison', fontsize=16, fontweight='bold')
        
        # Revenue comparison
        axes[0,0].plot(df1['Year'], df1['Revenue'], label='Approach One', linewidth=2)
        axes[0,0].plot(df2['Year'], df2['Revenue'], label='Approach Two', linewidth=2)
        axes[0,0].plot(df3['Year'], df3['Revenue'], label='Approach Three', linewidth=2)
        axes[0,0].set_title('Annual Revenue Projection')
        axes[0,0].set_xlabel('Year')
        axes[0,0].set_ylabel('Revenue (Billion USD)')
        axes[0,0].legend()
        axes[0,0].grid(True, alpha=0.3)
        
        # Cumulative investment
        axes[0,1].plot(df1['Year'], df1['Cumulative_Investment'], label='Approach One', linewidth=2)
        axes[0,1].plot(df2['Year'], df2['Cumulative_Investment'], label='Approach Two', linewidth=2)
        axes[0,1].plot(df3['Year'], df3['Cumulative_Investment'], label='Approach Three', linewidth=2)
        axes[0,1].set_title('Cumulative Investment')
        axes[0,1].set_xlabel('Year')
        axes[0,1].set_ylabel('Investment (Billion USD)')
        axes[0,1].legend()
        axes[0,1].grid(True, alpha=0.3)
        
        # Employment projection
        axes[0,2].plot(df1['Year'], df1['Employment'], label='Approach One', linewidth=2)
        axes[0,2].plot(df2['Year'], df2['Employment'], label='Approach Two', linewidth=2)
        axes[0,2].plot(df3['Year'], df3['Employment'], label='Approach Three', linewidth=2)
        axes[0,2].set_title('Employment Projection')
        axes[0,2].set_xlabel('Year')
        axes[0,2].set_ylabel('Employment (Thousands)')
        axes[0,2].legend()
        axes[0,2].grid(True, alpha=0.3)
        
        # Free cash flow
        axes[1,0].plot(df1['Year'], df1['Free_Cash_Flow'], label='Approach One', linewidth=2)
        axes[1,0].plot(df2['Year'], df2['Free_Cash_Flow'], label='Approach Two', linewidth=2)
        axes[1,0].plot(df3['Year'], df3['Free_Cash_Flow'], label='Approach Three', linewidth=2)
        axes[1,0].set_title('Free Cash Flow')
        axes[1,0].set_xlabel('Year')
        axes[1,0].set_ylabel('Cash Flow (Billion USD)')
        axes[1,0].legend()
        axes[1,0].grid(True, alpha=0.3)
        axes[1,0].axhline(y=0, color='black', linestyle='--', alpha=0.5)
        
        # GDP contribution
        axes[1,1].plot(df1['Year'], df1['GDP_Contribution'], label='Approach One', linewidth=2)
        axes[1,1].plot(df2['Year'], df2['GDP_Contribution'], label='Approach Two', linewidth=2)
        axes[1,1].plot(df3['Year'], df3['GDP_Contribution'], label='Approach Three', linewidth=2)
        axes[1,1].set_title('GDP Contribution')
        axes[1,1].set_xlabel('Year')
        axes[1,1].set_ylabel('GDP Impact (Billion USD)')
        axes[1,1].legend()
        axes[1,1].grid(True, alpha=0.3)
        
        # Cumulative free cash flow
        axes[1,2].plot(df1['Year'], df1['Free_Cash_Flow'].cumsum(), label='Approach One', linewidth=2)
        axes[1,2].plot(df2['Year'], df2['Free_Cash_Flow'].cumsum(), label='Approach Two', linewidth=2)
        axes[1,2].plot(df3['Year'], df3['Free_Cash_Flow'].cumsum(), label='Approach Three', linewidth=2)
        axes[1,2].set_title('Cumulative Free Cash Flow')
        axes[1,2].set_xlabel('Year')
        axes[1,2].set_ylabel('Cumulative Cash Flow (Billion USD)')
        axes[1,2].legend()
        axes[1,2].grid(True, alpha=0.3)
        axes[1,2].axhline(y=0, color='black', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        plt.savefig('/home/ubuntu/financial_projections_detailed.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Create sensitivity analysis chart
        return fig

def main():
    model = KKIPFinancialModel()
    
    # Generate models for all approaches
    print("Generating financial models...")
    df1 = model.approach_one_model()
    df2 = model.approach_two_model()
    df3 = model.approach_three_model()
    
    # Calculate metrics
    metrics1 = model.calculate_roi_metrics(df1)
    metrics2 = model.calculate_roi_metrics(df2)
    metrics3 = model.calculate_roi_metrics(df3)
    
    # Perform sensitivity analysis
    print("Performing sensitivity analysis...")
    sens1 = model.sensitivity_analysis(df1, "Approach One")
    sens2 = model.sensitivity_analysis(df2, "Approach Two")
    sens3 = model.sensitivity_analysis(df3, "Approach Three")
    
    # Create visualizations
    print("Creating visualizations...")
    model.create_visualizations(df1, df2, df3)
    
    # Save detailed data to Excel
    with pd.ExcelWriter('/home/ubuntu/KKIP_Financial_Models.xlsx', engine='openpyxl') as writer:
        df1.to_excel(writer, sheet_name='Approach_One', index=False)
        df2.to_excel(writer, sheet_name='Approach_Two', index=False)
        df3.to_excel(writer, sheet_name='Approach_Three', index=False)
        
        # Summary metrics
        summary_data = {
            'Metric': ['Total Investment (B USD)', 'Peak Revenue (B USD)', 'Total Cash Flows (B USD)', 
                      'NPV (B USD)', 'IRR (%)', '20-Year ROI (%)', 'Payback Period (Years)',
                      'Peak Employment (000s)', 'Peak GDP Impact (B USD)'],
            'Approach One': [metrics1['Total_Investment'], df1['Revenue'].max(), metrics1['Total_Cash_Flows'],
                           metrics1['NPV'], metrics1['IRR']*100, metrics1['ROI_20_Year'], metrics1['Payback_Period'],
                           df1['Employment'].max(), df1['GDP_Contribution'].max()],
            'Approach Two': [metrics2['Total_Investment'], df2['Revenue'].max(), metrics2['Total_Cash_Flows'],
                           metrics2['NPV'], metrics2['IRR']*100, metrics2['ROI_20_Year'], metrics2['Payback_Period'],
                           df2['Employment'].max(), df2['GDP_Contribution'].max()],
            'Approach Three': [metrics3['Total_Investment'], df3['Revenue'].max(), metrics3['Total_Cash_Flows'],
                             metrics3['NPV'], metrics3['IRR']*100, metrics3['ROI_20_Year'], metrics3['Payback_Period'],
                             df3['Employment'].max(), df3['GDP_Contribution'].max()]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary_Metrics', index=False)
        
        # Sensitivity analysis
        sens_df1 = pd.DataFrame(sens1).T
        sens_df2 = pd.DataFrame(sens2).T
        sens_df3 = pd.DataFrame(sens3).T
        
        sens_df1.to_excel(writer, sheet_name='Sensitivity_Approach_One')
        sens_df2.to_excel(writer, sheet_name='Sensitivity_Approach_Two')
        sens_df3.to_excel(writer, sheet_name='Sensitivity_Approach_Three')
    
    print("Financial analysis complete!")
    print(f"Approach One 20-Year ROI: {metrics1['ROI_20_Year']:.1f}%")
    print(f"Approach Two 20-Year ROI: {metrics2['ROI_20_Year']:.1f}%")
    print(f"Approach Three 20-Year ROI: {metrics3['ROI_20_Year']:.1f}%")
    
    return df1, df2, df3, metrics1, metrics2, metrics3

if __name__ == "__main__":
    main()

