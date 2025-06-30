import tkinter as tk

# المتغيرات العامة
smoothing = 0.08
aim_enabled = False
prediction_enabled = False
aim_position = "الرأس"

# تحديث الحالة على الواجهة
def update_status():
    aim_label.config(text="✅ مفعل" if aim_enabled else "❌ متوقف", fg="green" if aim_enabled else "red")
    prediction_label.config(text="✅ مفعل" if prediction_enabled else "❌ متوقف", fg="green" if prediction_enabled else "red")
    position_label.config(text=f"📌 التصويب: {aim_position}")
    smoothing_label.config(text=f"{smoothing:.2f}")

# دوال التبديل
def toggle_aim():
    global aim_enabled
    aim_enabled = not aim_enabled
    update_status()

def toggle_prediction():
    global prediction_enabled
    prediction_enabled = not prediction_enabled
    update_status()

def set_headshot():
    global aim_position
    aim_position = "الرأس"
    update_status()

def set_chest():
    global aim_position
    aim_position = "البطن"
    update_status()

def increase_smoothing():
    global smoothing
    smoothing = min(smoothing + 0.1, 2.0)
    update_status()

def decrease_smoothing():
    global smoothing
    smoothing = max(smoothing - 0.1, 0.1)
    update_status()

# إعداد الواجهة
window = tk.Tk()
window.title("🎯 Aim Assist - MW3")
window.geometry("400x400")
window.config(bg="#1e1e1e")

tk.Label(window, text="🎮 لوحة تحكم Aim Assist", font=("Segoe UI", 14, "bold"), fg="white", bg="#1e1e1e").pack(pady=10)

# التصويب العادي
frame = tk.Frame(window, bg="#1e1e1e")
frame.pack(pady=5)
tk.Button(frame, text="تفعيل / تعطيل التصويب", command=toggle_aim).pack(side="left", padx=5)
aim_label = tk.Label(frame, text="❌ متوقف", fg="red", bg="#1e1e1e")
aim_label.pack(side="left")

# التصويب الذكي
frame2 = tk.Frame(window, bg="#1e1e1e")
frame2.pack(pady=5)
tk.Button(frame2, text="تفعيل / تعطيل التنبؤ", command=toggle_prediction).pack(side="left", padx=5)
prediction_label = tk.Label(frame2, text="❌ متوقف", fg="red", bg="#1e1e1e")
prediction_label.pack(side="left")

# مكان التصويب
tk.Label(window, text="اختر مكان التصويب:", bg="#1e1e1e", fg="white").pack(pady=5)
frame3 = tk.Frame(window, bg="#1e1e1e")
frame3.pack(pady=5)
tk.Button(frame3, text="🎯 على الرأس", command=set_headshot).pack(side="left", padx=10)
tk.Button(frame3, text="🎯 على البطن", command=set_chest).pack(side="left", padx=10)
position_label = tk.Label(window, text="📌 التصويب: الرأس", bg="#1e1e1e", fg="white")
position_label.pack(pady=5)

# نعومة التصويب
tk.Label(window, text="⚙️ نعومة الحركة:", bg="#1e1e1e", fg="white").pack(pady=5)
frame4 = tk.Frame(window, bg="#1e1e1e")
frame4.pack(pady=5)
tk.Button(frame4, text="➖", command=decrease_smoothing).pack(side="left", padx=10)
tk.Button(frame4, text="➕", command=increase_smoothing).pack(side="left", padx=10)
smoothing_label = tk.Label(window, text=f"{smoothing:.2f}", bg="#1e1e1e", fg="white")
smoothing_label.pack(pady=5)

# زر الخروج
tk.Button(window, text="❌ خروج", command=window.destroy).pack(pady=20)

update_status()
window.mainloop()
