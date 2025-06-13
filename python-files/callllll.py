import tkinter as tk
from tkinter import ttk

# 💰 Pip values per lot
PAIR_PIP_VALUES = {
    'NQ': 20,
    'SP': 50,
    'EURUSD': 10,
    'GBPUSD': 10,
    'XAUUSD': 100,
    'US30': 10
}

# 📊 Main app class
class TariqForexCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("💹 Tariq Forex Calculator")
        self.root.geometry("500x550")
        self.root.configure(bg="#f2f2f2")

        # 🏷️ UI Labels and Inputs
        self.create_label_entry("💲 Account Size", "account_size")
        self.create_label_dropdown("📉 Risk %", "risk_percent", ["0.50", "1", "2"])
        self.create_label_value("💥 Risk $", "risk_dollars", readonly=True)
        self.create_label_dropdown("🔁 Pair", "pair", list(PAIR_PIP_VALUES.keys()))
        self.create_label_entry("🎯 Target ($)", "target")
        self.create_label_entry("🛑 Stop Size (pips)", "stop_size")
        self.create_label_entry("📦 Lot Size", "lot_size")  # ✅ Unlocked
        self.create_label_value("🎯 Pips Needed to Win", "pips_needed", readonly=True)

        # Buttons
        tk.Button(root, text="🧮 Calculate", command=self.calculate, bg="#4CAF50", fg="white", width=20).pack(pady=8)
        tk.Button(root, text="🧹 Clear", command=self.clear_all, bg="#2196F3", fg="white", width=20).pack(pady=4)
        tk.Button(root, text="🧽 Clear Stop Size", command=self.clear_stop_size, bg="#FFC107", fg="black", width=20).pack(pady=4)

    def create_label_entry(self, text, var_name):
        label = tk.Label(self.root, text=text, bg="#f2f2f2", anchor="w", font=("Arial", 10, "bold"))
        label.pack(fill="x", padx=20)
        entry = tk.Entry(self.root)
        entry.pack(fill="x", padx=20, pady=3)
        setattr(self, var_name, entry)

    def create_label_dropdown(self, text, var_name, options):
        label = tk.Label(self.root, text=text, bg="#f2f2f2", anchor="w", font=("Arial", 10, "bold"))
        label.pack(fill="x", padx=20)
        frame = tk.Frame(self.root)
        frame.pack(fill="x", padx=20, pady=3)
        combo = ttk.Combobox(frame, values=options)
        combo.pack(side="left", fill="x", expand=True)
        entry = tk.Entry(frame, width=5)
        entry.pack(side="right")
        setattr(self, f"{var_name}_combo", combo)
        setattr(self, var_name, entry)

    def create_label_value(self, text, var_name, readonly=False):
        label = tk.Label(self.root, text=text, bg="#f2f2f2", anchor="w", font=("Arial", 10, "bold"))
        label.pack(fill="x", padx=20)
        entry = tk.Entry(self.root, state="readonly" if readonly else "normal")
        entry.pack(fill="x", padx=20, pady=3)
        setattr(self, var_name, entry)

    def calculate(self):
        try:
            account_size = float(self.account_size.get())
            stop_size = float(self.stop_size.get())
            pair = self.pair_combo.get()
            pip_value = PAIR_PIP_VALUES.get(pair, 10)

            # Risk percent logic
            risk_percent = self.risk_percent_combo.get() or self.risk_percent.get()
            risk_percent = float(risk_percent)

            risk_dollars = (risk_percent / 100) * account_size
            self.risk_dollars.config(state="normal")
            self.risk_dollars.delete(0, tk.END)
            self.risk_dollars.insert(0, f"{risk_dollars:.2f}")
            self.risk_dollars.config(state="readonly")

            # Lot size
            lot_size = float(self.lot_size.get())

            # Pips needed to win
            target = float(self.target.get())
            pips_needed = target / (lot_size * pip_value)
            self.pips_needed.config(state="normal")
            self.pips_needed.delete(0, tk.END)
            self.pips_needed.insert(0, f"{pips_needed:.2f}")
            self.pips_needed.config(state="readonly")

        except Exception as e:
            print("Error:", e)

    def clear_all(self):
        for var in ["account_size", "risk_percent", "risk_dollars", "target", "stop_size", "lot_size", "pips_needed"]:
            entry = getattr(self, var)
            entry.config(state="normal")
            entry.delete(0, tk.END)
            if "readonly" in entry.cget("state"):
                entry.config(state="readonly")

    def clear_stop_size(self):
        self.stop_size.delete(0, tk.END)
        self.lot_size.delete(0, tk.END)


# 🚀 Launch the app
if __name__ == "__main__":
    root = tk.Tk()
    app = TariqForexCalculator(root)
    root.mainloop()
