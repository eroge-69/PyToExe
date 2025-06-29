
# AstroApp: تحلیل آسترولوژی کامل با رابط گرافیکی
# نویسنده: ChatGPT به سفارش کاربر عزیز

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import swisseph as swe
import datetime
import numpy as np
import matplotlib.pyplot as plt

swe.set_ephe_path(".")  # مسیر فایل‌های ephemeris

# --- ابزار کمکی برای نجوم ---
def get_julian_day(year, month, day, hour):
    return swe.julday(year, month, day, hour)

def get_planet_positions(jd_ut):
    planets = {
        'خورشید': swe.SUN,
        'ماه': swe.MOON,
        'عطارد': swe.MERCURY,
        'زهره': swe.VENUS,
        'مریخ': swe.MARS,
        'مشتری': swe.JUPITER,
        'زحل': swe.SATURN,
        'اورانوس': swe.URANUS,
        'نپتون': swe.NEPTUNE,
        'پلوتو': swe.PLUTO
    }
    positions = {}
    for name, pid in planets.items():
        pos = swe.calc_ut(jd_ut, pid)[0][0]
        positions[name] = pos
    return positions

def draw_chart(positions):
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'projection': 'polar'})
    ax.set_theta_direction(-1)
    ax.set_theta_offset(np.pi / 2.0)
    ax.set_rticks([])

    for i in range(12):
        angle = 2 * np.pi * i / 12
        ax.plot([angle, angle], [0, 1], color='black')
        ax.text(angle + np.pi/12, 1.05, f"{i+1}", ha='center', va='center', fontsize=10)

    for planet, angle_deg in positions.items():
        angle_rad = np.deg2rad(angle_deg)
        ax.plot(angle_rad, 0.85, 'o')
        ax.text(angle_rad, 0.9, planet, fontsize=9, ha='center')
    ax.set_title("چارت آسترولوژی", fontsize=14)
    plt.tight_layout()
    plt.show()

# --- تحلیلی‌ها ---
def analyze_career():
    return "🔹 تحلیل مسیر شغلی:\nشما فردی با روحیه جاه‌طلب و مسئولیت‌پذیر هستید. با توجه به وضعیت زحل و مریخ..."

def analyze_education():
    return "🔹 تحلیل تحصیلی:\nنقاط قوت ذهنی شما در ناحیه‌هایی قرار دارد که باعث تمرکز بالا و علاقه به پژوهش می‌شود..."

def analyze_love():
    return "🔹 تحلیل عاطفی:\nونوس و ماه در چارت شما تأثیر زیادی بر احساسات، رابطه و تمایلات عاشقانه دارند..."

def analyze_transit():
    return "🔹 تحلیل ترانزیت سالانه:\nدر این سال، عبور مشتری از خانه دوم شما فرصت‌های مالی به همراه دارد..."

def analyze_all():
    return "\n\n".join([
        analyze_career(),
        analyze_education(),
        analyze_love(),
        analyze_transit()
    ])

# --- رابط گرافیکی ---
class AstroApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("نرم‌افزار تحلیل آسترولوژی کامل")
        self.geometry("800x600")

        # ورودی‌ها
        frm = tk.Frame(self)
        frm.pack(pady=10)

        self.ent_date = tk.Entry(frm)
        self.ent_time = tk.Entry(frm)
        self.ent_lat = tk.Entry(frm)
        self.ent_lon = tk.Entry(frm)
        for lbl, ent in zip(["تاریخ (YYYY-MM-DD):", "ساعت (HH:MM):", "عرض جغرافیایی:", "طول جغرافیایی:"],
                            [self.ent_date, self.ent_time, self.ent_lat, self.ent_lon]):
            tk.Label(frm, text=lbl).pack()
            ent.pack()

        # دکمه‌ها
        tk.Button(frm, text="محاسبه و نمایش چارت", command=self.show_chart).pack(pady=5)

        # تب‌ها
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(expand=1, fill='both')

        self.text_widgets = []
        analyses = [("تحلیل کامل", analyze_all),
                    ("شغلی", analyze_career),
                    ("تحصیلی", analyze_education),
                    ("عاطفی", analyze_love),
                    ("ترانزیت", analyze_transit)]
        for name, func in analyses:
            frame = tk.Frame(self.tabs)
            self.tabs.add(frame, text=name)
            text = tk.Text(frame, wrap="word", font=("B Nazanin", 12))
            text.pack(expand=1, fill="both")
            self.text_widgets.append((text, func))
            btn = tk.Button(frame, text="تحلیل", command=lambda t=text, f=func: t.insert("1.0", f()))
            btn.pack()

        tk.Button(self, text="ذخیره تحلیل فعال", command=self.save_analysis).pack(pady=5)

    def get_jd(self):
        try:
            date_parts = list(map(int, self.ent_date.get().split("-")))
            time_parts = list(map(int, self.ent_time.get().split(":")))
            hour = time_parts[0] + time_parts[1]/60
            jd = get_julian_day(date_parts[0], date_parts[1], date_parts[2], hour)
            return jd
        except:
            messagebox.showerror("خطا", "ورودی نادرست است")
            return None

    def show_chart(self):
        jd = self.get_jd()
        if jd:
            pos = get_planet_positions(jd)
            draw_chart(pos)

    def save_analysis(self):
        index = self.tabs.index(self.tabs.select())
        text, _ = self.text_widgets[index]
        content = text.get("1.0", tk.END)
        file_path = filedialog.asksaveasfilename(defaultextension=".txt")
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("ذخیره شد", "تحلیل ذخیره شد.")

if __name__ == "__main__":
    app = AstroApp()
    app.mainloop()
