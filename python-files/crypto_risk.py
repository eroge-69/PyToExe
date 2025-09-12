# Position Size & Profit Calculator

# دریافت ورودی‌ها
capital = float(input("کل سرمایه ($): "))
risk_percent = float(input("ریسک به درصد (%): "))
stop_loss_percent = float(input("استاپ لاس به درصد (%): "))
leverage = float(input("لوریج: "))
target_percent = float(input("تارگت به درصد (%): "))

# محاسبه سایز پوزیشن
position_size = (capital * (risk_percent / 100)) / (leverage * (stop_loss_percent / 100))

# محاسبه حجم واقعی روی بازار (با لوریج)
market_exposure = position_size * leverage

# محاسبه ضرر
loss_amount = market_exposure * (stop_loss_percent / 100)

# محاسبه سود
profit_amount = market_exposure * (target_percent / 100)

# نسبت ریسک به ریوارد
if loss_amount != 0:
    rr_ratio = profit_amount / loss_amount
else:
    rr_ratio = 0

# نمایش خروجی
print("\n--- نتایج ---")
print(f"سایز پوزیشن واقعی: {position_size:.2f} $")
print(f"حجم معامله روی بازار (با لوریج): {market_exposure:.2f} $")
print(f"حداکثر ضرر: {loss_amount:.2f} $")
print(f"سود در تارگت {target_percent}%: {profit_amount:.2f} $")
print(f"نسبت ریسک به ریوارد: 1 : {rr_ratio:.2f}")