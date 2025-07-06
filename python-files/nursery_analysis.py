
import pandas as pd

# Load Excel file
file_path = "Nurcery_Updated (1).xlsx"
xls = pd.ExcelFile(file_path)

# Analyze Daily Production
def analyze_daily_production():
    df = xls.parse("Daily Production ")
    print("🔹 Daily Production Summary")
    print("Average trays per day:", df["No of Tray Produced"].apply(pd.to_numeric, errors="coerce").mean())
    print("Total Sampling Produced:", df["Total Sampling Produced (Qty)"].sum())
    print("Total Labor Cost:", df["Total Labor Cost"].sum())
    print("-" * 40)

# Analyze Raw Material Cost
def analyze_raw_material():
    df = xls.parse("RAW Material Cost")
    print("🔹 Raw Material Cost Summary")
    print("Total Qty received (Ton):", df["Qty received in Ton"].sum())
    print("Total RM Cost:", df["Total RM Cost"].sum())
    print("Total Labor Cost:", df["Total Labor Cost"].sum())
    print("Total Transport Cost:", df["Trasport (Tractor Rent)"].sum())
    print("-" * 40)

# Analyze Sales
def analyze_sales():
    df = xls.parse("Sales_Seedling")
    print("🔹 Sales Summary")
    print("Total Seedlings Sold:", df["Total Seedling Sold"].sum())
    print("Total Revenue:", df["Total Cost"].sum())
    print("Total Received Payment:", df["Received Payment"].sum(skipna=True))
    print("-" * 40)

# Analyze Employee Pay Rates
def analyze_employee_pay():
    df = xls.parse("Employee IDs with Pay Rate", skiprows=2)
    df.columns = ["ID", "Name", "Pay Rate"]
    print("🔹 Employee Pay Summary")
    print(df.describe())
    print("-" * 40)

# Capital Investment
def analyze_capital_investment():
    df = xls.parse("Capital Investment")
    print("🔹 Capital Investment")
    print("Total Items Cost:", df["Total Cost"].sum())
    print("Top 5 Items:")
    print(df[["Item ", "Total Cost"]].sort_values(by="Total Cost", ascending=False).head(5))
    print("-" * 40)

# Main function
def main():
    print("\n📊 NURSERY DATA ANALYSIS 📊")
    analyze_daily_production()
    analyze_raw_material()
    analyze_sales()
    analyze_employee_pay()
    analyze_capital_investment()

if __name__ == "__main__":
    main()
