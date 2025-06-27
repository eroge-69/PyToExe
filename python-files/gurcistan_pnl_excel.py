import pandas as pd

# Girdi değerleri
daily_sales_per_machine = 25
machines = 20
sale_price = 1.25
cost_price = 0.28
machine_price = 1980
entry_fee = 10000
initial_stock = 100000
operational_cost_yearly = 15000
marketing_cost_yearly = 5000
amortization_years = 5

days_year = 365
months_year = 12

# Hesaplamalar
total_daily_sales = daily_sales_per_machine * machines
total_annual_sales_units = total_daily_sales * days_year
total_annual_revenue = total_annual_sales_units * sale_price
total_annual_cost = total_annual_sales_units * cost_price

total_machine_cost = machines * machine_price
annual_amortization = total_machine_cost / amortization_years

total_annual_expense = total_annual_cost + annual_amortization + operational_cost_yearly + marketing_cost_yearly
total_annual_profit = total_annual_revenue - total_annual_expense

# Aylık hesaplama
monthly_units_sold = total_daily_sales * 30
monthly_revenue = monthly_units_sold * sale_price
monthly_cost = monthly_units_sold * cost_price
monthly_amortization = annual_amortization / months_year
monthly_operational = operational_cost_yearly / months_year
monthly_marketing = marketing_cost_yearly / months_year
monthly_total_expense = monthly_cost + monthly_amortization + monthly_operational + monthly_marketing
monthly_profit = monthly_revenue - monthly_total_expense

# Geri dönüş süresi
initial_investment = total_machine_cost + (initial_stock * cost_price) + entry_fee
roi_months = initial_investment / monthly_profit

# Excel tablosu verisi
summary = pd.DataFrame({
    'Kalem': [
        'Yıllık Satış (adet)', 'Yıllık Ciro (€)', 'Yıllık Maliyet (€)', 'Yıllık Amortisman (€)',
        'Yıllık Operasyonel Gider (€)', 'Yıllık Pazarlama Gideri (€)', 'Toplam Gider (€)',
        'Yıllık Net Kâr (€)', 'Aylık Net Kâr (€)', 'Yatırım Tutarı (€)', 'ROI (Ay)'
    ],
    'Değer': [
        total_annual_sales_units, total_annual_revenue, total_annual_cost, annual_amortization,
        operational_cost_yearly, marketing_cost_yearly, total_annual_expense,
        total_annual_profit, monthly_profit, initial_investment, roi_months
    ]
})

# Excel çıktısı
tablename = "Rulomatik_Gürcistan_PNL.xlsx"
summary.to_excel(tablename, index=False)

print(f"PNL tablosu '{tablename}' olarak oluşturuldu.")
