
import tkinter as tk
from tkinter import ttk, messagebox

# Simple cooling tower selector (open / closed circuit)
# NOTE: This is a preliminary engineering tool for quick sizing. Use manufacturer data for final selection.

CP_WATER = 4.186  # kJ/kg-K
DENSITY_WATER = 1000  # kg/m3

def calc():
    try:
        mode = mode_var.get()  # "open" or "closed"
        q_kw = float(q_entry.get())
        tin = float(tin_entry.get())
        tout = float(tout_entry.get())
        wbt = float(wbt_entry.get())

        if tout >= tin:
            messagebox.showerror("خطا", "دمای خروجی باید از ورودی کمتر باشد.")
            return
        if wbt >= tout:
            messagebox.showwarning("توجه", "دمای مرطوب نباید از دمای خروجی بالاتر باشد (approach منفی).")

        rng = tin - tout
        approach = tout - wbt

        # Mass flow (kg/s) using Q = m*Cp*ΔT  (kW = kJ/s)
        m_dot = q_kw / (CP_WATER * rng)  # kg/s
        v_dot_m3h = (m_dot / DENSITY_WATER) * 3600  # m3/h

        # Very rough capacity derate/adder for closed-circuit fluid coolers vs open towers
        cap_factor = 1.0 if mode == "open" else 1.15  # closed typically needs ~10–20% more capacity
        q_required_kw = q_kw * cap_factor

        # Extremely rough fan power estimate (placeholder): 1% of heat rejected
        p_fan_kw = 0.01 * q_required_kw

        # Text recommendation (placeholder). A real tool must use Merkel method & vendor curves.
        rec = []
        rec.append(f"ظرفیت دفع حرارت مورد نیاز (با ضریب مد {('مدار باز' if mode=='open' else 'مدار بسته')}): ~ {q_required_kw:,.1f} kW")
        rec.append(f"دبی آب چرخشی تقریبی: ~ {v_dot_m3h:,.0f} m³/h")
        rec.append(f"رنج (Range): {rng:.1f} °C   |   اپروچ (Approach): {approach:.1f} °C")
        rec.append(f"برآورد توان فن (تقریبی و محافظه‌کارانه): ~ {p_fan_kw:.1f} kW")
        rec.append("** توجه: نتایج مقدماتی است. برای انتخاب نهایی از دیتاشیت/نمودار سازنده و روش مرکل استفاده کنید. **")

        result_box.configure(state="normal")
        result_box.delete("1.0", tk.END)
        result_box.insert(tk.END, "\n".join(rec))
        result_box.configure(state="disabled")

    except ValueError:
        messagebox.showerror("خطا", "لطفاً همه ورودی‌ها را به صورت عددی صحیح وارد کنید.")

root = tk.Tk()
root.title("Cooling Tower Selector - Open/Closed Circuit (Beta)")
root.geometry("720x540")

main = ttk.Frame(root, padding=12)
main.pack(fill=tk.BOTH, expand=True)

# Mode
mode_var = tk.StringVar(value="open")
mode_frame = ttk.LabelFrame(main, text="نوع دستگاه")
mode_frame.pack(fill=tk.X, pady=8)
ttk.Radiobutton(mode_frame, text="مدار باز (Cooling Tower)", variable=mode_var, value="open").pack(side=tk.RIGHT, padx=6)
ttk.Radiobutton(mode_frame, text="مدار بسته (Fluid Cooler)", variable=mode_var, value="closed").pack(side=tk.RIGHT, padx=6)

# Inputs
inp = ttk.LabelFrame(main, text="ورودی‌ها (واحدها: °C و kW)")
inp.pack(fill=tk.X, pady=8)

row = ttk.Frame(inp); row.pack(fill=tk.X, pady=4)
ttk.Label(row, text="بار حرارتی برای دفع Q (kW):").pack(side=tk.RIGHT, padx=6)
q_entry = ttk.Entry(row, width=18, justify="center"); q_entry.pack(side=tk.RIGHT)
q_entry.insert(0, "1000")

row = ttk.Frame(inp); row.pack(fill=tk.X, pady=4)
ttk.Label(row, text="دمای آب ورودی به برج Tin (°C):").pack(side=tk.RIGHT, padx=6)
tin_entry = ttk.Entry(row, width=18, justify="center"); tin_entry.pack(side=tk.RIGHT)
tin_entry.insert(0, "35")

row = ttk.Frame(inp); row.pack(fill=tk.X, pady=4)
ttk.Label(row, text="دمای آب خروجی از برج Tout (°C):").pack(side=tk.RIGHT, padx=6)
tout_entry = ttk.Entry(row, width=18, justify="center"); tout_entry.pack(side=tk.RIGHT)
tout_entry.insert(0, "30")

row = ttk.Frame(inp); row.pack(fill=tk.X, pady=4)
ttk.Label(row, text="دمای مرطوب محیط WBT (°C):").pack(side=tk.RIGHT, padx=6)
wbt_entry = ttk.Entry(row, width=18, justify="center"); wbt_entry.pack(side=tk.RIGHT)
wbt_entry.insert(0, "25")

# Button
btn = ttk.Button(main, text="محاسبه", command=calc)
btn.pack(pady=10)

# Output
out = ttk.LabelFrame(main, text="نتیجه")
out.pack(fill=tk.BOTH, expand=True, pady=8)
result_box = tk.Text(out, height=12, state="disabled", wrap="word")
result_box.pack(fill=tk.BOTH, expand=True)

# Footer
footer = ttk.Label(main, foreground="#555", text="نسخه آزمایشی. برای انتخاب نهایی از داده‌های سازنده و روش مرکل استفاده شود.")
footer.pack(pady=6)

root.mainloop()
