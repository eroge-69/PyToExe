import math

# دریافت ابعاد از کاربر
a = float(input("طول ضلع قاعده مربع را وارد کنید: "))
b = float(input("طول ساق مثلث متساوی الساقین را وارد کنید: "))

# محاسبه ارتفاع هرم
# ارتفاع مثلث جانبی: h_triangle = sqrt(b^2 - (a/2)^2)
h_triangle = math.sqrt(b**2 - (a/2)**2)

# ارتفاع هرم: h_pyramid = sqrt(h_triangle^2 - (a/2)^2)
h_pyramid = math.sqrt(h_triangle**2 - (a/2)**2)

# محاسبه حجم هرم: V = (1/3) * مساحت قاعده * ارتفاع
volume = (1/3) * (a**2) * h_pyramid

# نمایش نتیجه
print(f"حجم هرم: {volume:.2f}")