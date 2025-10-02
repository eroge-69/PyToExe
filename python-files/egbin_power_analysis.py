#!/usr/bin/env python3
"""
Egbin Power PLC Work Order Analysis Tool
========================================
Comprehensive KPI analysis for maintenance work orders to support continuous improvement.

Usage:
    python egbin_power_analysis.py path/to/excel_file.xlsx

Author: AI Assistant
Date: 2024
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
import sys
import os
from pathlib import Path
import argparse

# Configure plotting
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")
warnings.filterwarnings('ignore')

class EgbinPowerAnalysis:
    """Main analysis class for Egbin Power PLC work order data."""
    
    def __init__(self, excel_file_path):
        """Initialize the analysis with Excel file path."""
        self.excel_file_path = excel_file_path
        self.df = None
        self.kpi_results = {}
        self.output_dir = Path("egbin_analysis_output")
        self.output_dir.mkdir(exist_ok=True)
        
    def load_and_clean_data(self):
        """Load and clean the Excel data."""
        try:
            print("📂 Loading Excel file...")
            self.df = pd.read_excel(self.excel_file_path)
            print(f"✅ Loaded {len(self.df)} work orders")
            
            # Basic data cleaning
            print("🧹 Cleaning data...")
            
            # Handle missing values and data types
            self.df = self.df.fillna({
                'Status': 'Unknown',
                'Priority': 'Medium',
                'Department': 'Unknown',
                'Equipment_Type': 'Unknown',
                'Cost': 0
            })
            
            # Ensure proper data types
            if 'Cost' in self.df.columns:
                self.df['Cost'] = pd.to_numeric(self.df['Cost'], errors='coerce').fillna(0)
            
            # Create derived columns for analysis
            self._create_derived_columns()
            
            print("✅ Data cleaning completed")
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            return False
    
    def _create_derived_columns(self):
        """Create derived columns for analysis."""
        # Status categories
        completed_statuses = ['Completed', 'Closed', 'Done', 'Finished']
        self.df['Is_Completed'] = self.df['Status'].isin(completed_statuses)
        
        # Date handling (if date columns exist)
        date_columns = [col for col in self.df.columns if 'date' in col.lower() or 'time' in col.lower()]
        for col in date_columns:
            try:
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
            except:
                pass
        
        # Priority mapping
        priority_map = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1, 'Unknown': 2}
        self.df['Priority_Score'] = self.df['Priority'].map(priority_map).fillna(2)
        
        # Equipment categorization
        self.df['Equipment_Category'] = self.df.get('Equipment_Type', 'Unknown')
    
    def calculate_overall_kpis(self):
        """Calculate overall performance KPIs."""
        print("📊 Calculating overall KPIs...")
        
        total_orders = len(self.df)
        completed_orders = self.df['Is_Completed'].sum()
        completion_rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0
        
        total_cost = self.df['Cost'].sum() if 'Cost' in self.df.columns else 0
        avg_cost = self.df['Cost'].mean() if 'Cost' in self.df.columns else 0
        
        self.kpi_results['overall'] = {
            'total_work_orders': total_orders,
            'completed_orders': completed_orders,
            'completion_rate': completion_rate,
            'total_cost': total_cost,
            'average_cost_per_order': avg_cost,
            'pending_orders': total_orders - completed_orders
        }
        
        print(f"   📈 Total Work Orders: {total_orders:,}")
        print(f"   ✅ Completion Rate: {completion_rate:.1f}%")
        print(f"   💰 Total Cost: ₦{total_cost/1e9:.2f}B")
    
    def analyze_department_performance(self):
        """Analyze performance by department."""
        print("🏢 Analyzing department performance...")
        
        if 'Department' not in self.df.columns:
            print("   ⚠️  Department column not found, skipping analysis")
            return
        
        dept_analysis = self.df.groupby('Department').agg({
            'Is_Completed': ['count', 'sum', 'mean'],
            'Cost': ['sum', 'mean']
        }).round(2)
        
        dept_analysis.columns = ['Total_Orders', 'Completed_Orders', 'Completion_Rate', 
                                'Total_Cost', 'Avg_Cost']
        dept_analysis['Completion_Rate'] *= 100
        dept_analysis = dept_analysis.sort_values('Completion_Rate', ascending=False)
        
        self.kpi_results['departments'] = dept_analysis
        
        # Save to CSV
        dept_analysis.to_csv(self.output_dir / 'department_performance.csv')
        print(f"   💾 Saved department analysis to {self.output_dir}/department_performance.csv")
    
    def analyze_equipment_performance(self):
        """Analyze performance by equipment type."""
        print("⚙️  Analyzing equipment performance...")
        
        if 'Equipment_Type' not in self.df.columns:
            print("   ⚠️  Equipment_Type column not found, skipping analysis")
            return
        
        equip_analysis = self.df.groupby('Equipment_Type').agg({
            'Is_Completed': ['count', 'sum', 'mean'],
            'Cost': ['sum', 'mean'],
            'Priority_Score': 'mean'
        }).round(2)
        
        equip_analysis.columns = ['Total_Orders', 'Completed_Orders', 'Completion_Rate', 
                                 'Total_Cost', 'Avg_Cost', 'Avg_Priority']
        equip_analysis['Completion_Rate'] *= 100
        equip_analysis = equip_analysis.sort_values('Completion_Rate', ascending=False)
        
        self.kpi_results['equipment'] = equip_analysis
        
        # Save to CSV
        equip_analysis.to_csv(self.output_dir / 'equipment_performance.csv')
        print(f"   💾 Saved equipment analysis to {self.output_dir}/equipment_performance.csv")
    
    def analyze_priority_distribution(self):
        """Analyze work orders by priority."""
        print("🚨 Analyzing priority distribution...")
        
        priority_analysis = self.df.groupby('Priority').agg({
            'Is_Completed': ['count', 'sum', 'mean'],
            'Cost': ['sum', 'mean']
        }).round(2)
        
        priority_analysis.columns = ['Total_Orders', 'Completed_Orders', 'Completion_Rate', 
                                    'Total_Cost', 'Avg_Cost']
        priority_analysis['Completion_Rate'] *= 100
        priority_analysis['Percentage_of_Total'] = (priority_analysis['Total_Orders'] / 
                                                   len(self.df) * 100).round(1)
        
        self.kpi_results['priority'] = priority_analysis
        
        # Save to CSV
        priority_analysis.to_csv(self.output_dir / 'priority_analysis.csv')
        print(f"   💾 Saved priority analysis to {self.output_dir}/priority_analysis.csv")
    
    def generate_visualizations(self):
        """Generate comprehensive visualizations."""
        print("📊 Generating visualizations...")
        
        # Set up the plotting parameters
        plt.rcParams['figure.figsize'] = (15, 10)
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        fig.suptitle('Egbin Power PLC - Work Order Analysis Dashboard', fontsize=16, fontweight='bold')
        
        # 1. Overall completion rate
        if 'overall' in self.kpi_results:
            completion_rate = self.kpi_results['overall']['completion_rate']
            pending_rate = 100 - completion_rate
            
            axes[0, 0].pie([completion_rate, pending_rate], 
                          labels=['Completed', 'Pending'], 
                          autopct='%1.1f%%',
                          colors=['#2ecc71', '#e74c3c'])
            axes[0, 0].set_title('Overall Work Order Status')
        
        # 2. Department performance
        if 'departments' in self.kpi_results and not self.kpi_results['departments'].empty:
            dept_data = self.kpi_results['departments'].head(8)
            axes[0, 1].barh(dept_data.index, dept_data['Completion_Rate'])
            axes[0, 1].set_title('Department Completion Rates (%)')
            axes[0, 1].set_xlabel('Completion Rate (%)')
        
        # 3. Equipment performance
        if 'equipment' in self.kpi_results and not self.kpi_results['equipment'].empty:
            equip_data = self.kpi_results['equipment'].head(8)
            axes[0, 2].barh(equip_data.index, equip_data['Completion_Rate'])
            axes[0, 2].set_title('Equipment Completion Rates (%)')
            axes[0, 2].set_xlabel('Completion Rate (%)')
        
        # 4. Priority distribution
        if 'priority' in self.kpi_results:
            priority_data = self.kpi_results['priority']
            axes[1, 0].bar(priority_data.index, priority_data['Total_Orders'])
            axes[1, 0].set_title('Work Orders by Priority')
            axes[1, 0].set_ylabel('Number of Orders')
            axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 5. Cost analysis
        if 'departments' in self.kpi_results and not self.kpi_results['departments'].empty:
            dept_cost = self.kpi_results['departments'].head(6)
            axes[1, 1].bar(dept_cost.index, dept_cost['Total_Cost'] / 1e6)
            axes[1, 1].set_title('Department Total Costs (₦ Millions)')
            axes[1, 1].set_ylabel('Cost (₦ Millions)')
            axes[1, 1].tick_params(axis='x', rotation=45)
        
        # 6. Completion rate trend (if applicable)
        axes[1, 2].text(0.5, 0.5, 'Completion Rate Analysis\n\nOverall: {:.1f}%\nTarget: 85%\nGap: {:.1f}%'.format(
            self.kpi_results['overall']['completion_rate'],
            85 - self.kpi_results['overall']['completion_rate']
        ), ha='center', va='center', fontsize=12, 
        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
        axes[1, 2].set_title('Performance Summary')
        axes[1, 2].axis('off')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'egbin_dashboard.png', dpi=300, bbox_inches='tight')
        print(f"   💾 Saved dashboard to {self.output_dir}/egbin_dashboard.png")
        plt.show()
    
    def generate_recommendations(self):
        """Generate strategic recommendations based on analysis."""
        print("💡 Generating recommendations...")
        
        recommendations = []
        
        # Overall performance recommendations
        overall = self.kpi_results.get('overall', {})
        completion_rate = overall.get('completion_rate', 0)
        
        if completion_rate < 75:
            recommendations.append({
                'Category': 'Critical',
                'Area': 'Overall Performance',
                'Issue': f'Completion rate at {completion_rate:.1f}% is below target',
                'Recommendation': 'Implement immediate process review and resource reallocation',
                'Expected_Impact': 'Increase completion rate by 10-15%',
                'Timeline': '0-3 months'
            })
        
        # Department-specific recommendations
        if 'departments' in self.kpi_results:
            dept_data = self.kpi_results['departments']
            worst_dept = dept_data['Completion_Rate'].idxmin()
            worst_rate = dept_data['Completion_Rate'].min()
            
            if worst_rate < 65:
                recommendations.append({
                    'Category': 'High Priority',
                    'Area': f'{worst_dept} Department',
                    'Issue': f'Lowest completion rate at {worst_rate:.1f}%',
                    'Recommendation': 'Conduct detailed process audit and provide additional training',
                    'Expected_Impact': 'Improve department efficiency by 20%',
                    'Timeline': '3-6 months'
                })
        
        # Equipment-specific recommendations
        if 'equipment' in self.kpi_results:
            equip_data = self.kpi_results['equipment']
            worst_equip = equip_data['Completion_Rate'].idxmin()
            worst_equip_rate = equip_data['Completion_Rate'].min()
            
            if worst_equip_rate < 70:
                recommendations.append({
                    'Category': 'Medium Priority',
                    'Area': f'{worst_equip} Equipment',
                    'Issue': f'Low completion rate at {worst_equip_rate:.1f}%',
                    'Recommendation': 'Implement predictive maintenance and spare parts optimization',
                    'Expected_Impact': 'Reduce equipment downtime by 25%',
                    'Timeline': '6-12 months'
                })
        
        # Cost optimization recommendations
        avg_cost = overall.get('average_cost_per_order', 0)
        if avg_cost > 1.5e6:  # If average cost > 1.5M
            recommendations.append({
                'Category': 'Cost Optimization',
                'Area': 'Financial Performance',
                'Issue': f'High average cost per order: ₦{avg_cost/1e6:.1f}M',
                'Recommendation': 'Implement cost control measures and vendor negotiations',
                'Expected_Impact': 'Reduce average cost by 15-20%',
                'Timeline': '3-9 months'
            })
        
        # Priority management recommendations
        if 'priority' in self.kpi_results:
            critical_completion = self.kpi_results['priority'].loc['Critical', 'Completion_Rate'] if 'Critical' in self.kpi_results['priority'].index else 100
            if critical_completion < 90:
                recommendations.append({
                    'Category': 'Critical',
                    'Area': 'Priority Management',
                    'Issue': f'Critical work orders completion at {critical_completion:.1f}%',
                    'Recommendation': 'Establish fast-track process for critical work orders',
                    'Expected_Impact': 'Achieve 95%+ critical work order completion',
                    'Timeline': '0-1 month'
                })
        
        # Convert to DataFrame and save
        recommendations_df = pd.DataFrame(recommendations)
        if not recommendations_df.empty:
            recommendations_df.to_csv(self.output_dir / 'strategic_recommendations.csv', index=False)
            self.kpi_results['recommendations'] = recommendations_df
            print(f"   💾 Saved {len(recommendations)} recommendations to {self.output_dir}/strategic_recommendations.csv")
        
        return recommendations
    
    def generate_summary_report(self):
        """Generate a comprehensive summary report."""
        print("📋 Generating summary report...")
        
        # Compile KPI summary
        kpi_summary = {
            'Total Work Orders': self.kpi_results['overall']['total_work_orders'],
            'Completion Rate (%)': round(self.kpi_results['overall']['completion_rate'], 1),
            'Total Cost (₦ Billions)': round(self.kpi_results['overall']['total_cost'] / 1e9, 2),
            'Average Cost per Order (₦ Millions)': round(self.kpi_results['overall']['average_cost_per_order'] / 1e6, 2),
            'Pending Orders': self.kpi_results['overall']['pending_orders']
        }
        
        # Best and worst performing areas
        if 'departments' in self.kpi_results and not self.kpi_results['departments'].empty:
            best_dept = self.kpi_results['departments']['Completion_Rate'].idxmax()
            worst_dept = self.kpi_results['departments']['Completion_Rate'].idxmin()
            kpi_summary['Best Performing Department'] = f"{best_dept} ({self.kpi_results['departments']['Completion_Rate'].max():.1f}%)"
            kpi_summary['Worst Performing Department'] = f"{worst_dept} ({self.kpi_results['departments']['Completion_Rate'].min():.1f}%)"
        
        if 'equipment' in self.kpi_results and not self.kpi_results['equipment'].empty:
            best_equip = self.kpi_results['equipment']['Completion_Rate'].idxmax()
            worst_equip = self.kpi_results['equipment']['Completion_Rate'].idxmin()
            kpi_summary['Best Performing Equipment'] = f"{best_equip} ({self.kpi_results['equipment']['Completion_Rate'].max():.1f}%)"
            kpi_summary['Worst Performing Equipment'] = f"{worst_equip} ({self.kpi_results['equipment']['Completion_Rate'].min():.1f}%)"
        
        # Save KPI summary
        kpi_df = pd.DataFrame(list(kpi_summary.items()), columns=['KPI', 'Value'])
        kpi_df.to_csv(self.output_dir / 'kpi_summary.csv', index=False)
        
        print(f"   💾 Saved KPI summary to {self.output_dir}/kpi_summary.csv")
        return kpi_summary
    
    def run_complete_analysis(self):
        """Run the complete analysis pipeline."""
        print("🚀 Starting Egbin Power PLC Work Order Analysis")
        print("=" * 60)
        
        # Load and clean data
        if not self.load_and_clean_data():
            return False
        
        # Run all analyses
        self.calculate_overall_kpis()
        self.analyze_department_performance()
        self.analyze_equipment_performance()
        self.analyze_priority_distribution()
        
        # Generate outputs
        self.generate_visualizations()
        recommendations = self.generate_recommendations()
        summary = self.generate_summary_report()
        
        # Print final summary
        print("\n" + "=" * 60)
        print("📊 ANALYSIS COMPLETE - KEY FINDINGS")
        print("=" * 60)
        
        for key, value in summary.items():
            print(f"   {key}: {value}")
        
        print(f"\n💡 Generated {len(recommendations)} strategic recommendations")
        print(f"📁 All outputs saved to: {self.output_dir.absolute()}")
        
        print("\n🎯 NEXT STEPS:")
        print("   1. Review detailed CSV files for specific insights")
        print("   2. Implement high-priority recommendations")
        print("   3. Monitor KPIs monthly for continuous improvement")
        print("   4. Use dashboard visualizations for stakeholder presentations")
        
        return True

def main():
    """Main function to run the analysis."""
    parser = argparse.ArgumentParser(description='Egbin Power PLC Work Order Analysis Tool')
    parser.add_argument('excel_file', help='Path to the Excel file containing work order data')
    parser.add_argument('--output-dir', default='egbin_analysis_output', 
                       help='Output directory for analysis results')
    
    args = parser.parse_args()
    
    # Check if file exists
    if not os.path.exists(args.excel_file):
        print(f"❌ Error: File '{args.excel_file}' not found")
        return 1
    
    # Run analysis
    analyzer = EgbinPowerAnalysis(args.excel_file)
    analyzer.output_dir = Path(args.output_dir)
    analyzer.output_dir.mkdir(exist_ok=True)
    
    success = analyzer.run_complete_analysis()
    
    if success:
        print("\n✅ Analysis completed successfully!")
        return 0
    else:
        print("\n❌ Analysis failed!")
        return 1

if __name__ == "__main__":
    # If running directly with a file path as argument
    if len(sys.argv) > 1:
        exit(main())
    else:
        # Interactive mode for Jupyter or direct Python execution
        print("Egbin Power PLC Work Order Analysis Tool")
        print("=" * 50)
        print("Usage: python egbin_power_analysis.py <excel_file_path>")
        print("Or modify the script to include your file path directly")
        
        # Example usage (modify this path)
        # excel_file_path = "path/to/your/excel_file.xlsx"
        # analyzer = EgbinPowerAnalysis(excel_file_path)
        # analyzer.run_complete_analysis()