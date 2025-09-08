import tkinter as tk
from tkinter import ttk, messagebox

APP_TITLE = "Forex Lot Size Calculator — 0.5% Risk | RR 1:2"
CONTRACT_SIZE = 100_000  # standard lot units
DEFAULT_RISK_PCT = 0.5   # fixed as requested
RR_NUM = 1
RR_DEN = 2               # 1:2

def detect_pip_size(pair: str) -> float:
    pair = pair.strip().upper().replace(" ", "")
    # Basic rule: JPY pairs use 0.01, most others 0.0001
    return 0.01 if "JPY" in pair[-3:] else 0.0001

def compute():
    try:
        balance = float(balance_var.get())
        pair = pair_var.get().strip().upper()
        entry = float(entry_var.get())
        stop = float(stop_var.get())
        quote_to_acct = conv_var.get().strip()
        direction = dir_var.get()

        if not pair or len(pair) < 6:
            messagebox.showerror("Input error", "Please enter a valid pair (e.g., EURUSD, GBPJPY).")
            return

        pip_size = detect_pip_size(pair)

        # If user didn’t provide conversion, assume 1 if account currency == quote currency.
        # We can’t auto-detect account currency here; default to 1 unless user supplies a rate.
        if quote_to_acct == "":
            quote_to_acct_rate = 1.0
        else:
            quote_to_acct_rate = float(quote_to_acct)

        risk_pct = DEFAULT_RISK_PCT
        risk_amount = balance * (risk_pct / 100.0)

        stop_distance_price = abs(entry - stop)
        if stop_distance_price <= 0:
            messagebox.showerror("Input error", "Entry and Stop must be different.")
            return

        stop_distance_pips = stop_distance_price / pip_size

        # Pip value per 1.00 lot in QUOTE currency:
        # = CONTRACT_SIZE * pip_size  (e.g., 100000 * 0.0001 = 10 quote units; for JPY: 100000*0.01=1000 JPY)
        pip_value_quote_per_lot = CONTRACT_SIZE * pip_size

        # Convert pip value into ACCOUNT currency using provided conversion (QUOTE -> ACCOUNT)
        pip_value_acct_per_lot = pip_value_quote_per_lot * quote_to_acct_rate

        if pip_value_acct_per_lot <= 0:
            messagebox.showerror("Input error", "Conversion rate must be positive.")
            return

        # Lot size = Risk $ / (Stop pips * $ per pip per 1 lot)
        # $ per pip per 1 lot = pip_value_acct_per_lot
        lots = risk_amount / (stop_distance_pips * pip_value_acct_per_lot)

        if lots <= 0:
            messagebox.showerror("Calculation error", "Calculated lot size is non-positive. Check inputs.")
            return

        # Convert to units (base currency units)
        units = lots * CONTRACT_SIZE

        # Take-profit (RR 1:2)
        tp_distance_price = (RR_DEN / RR_NUM) * stop_distance_price  # 2x stop distance in price terms
        if direction == "Long":
            tp_price = entry + tp_distance_price
        else:
            tp_price = entry - tp_distance_price

        # Potential reward in $ at 1:2
        reward_pips = (RR_DEN / RR_NUM) * stop_distance_pips
        potential_reward_amount = reward_pips * pip_value_acct_per_lot * lots

        # Display nicely
        out_lines = []
        out_lines.append(f"Pair: {pair} | Pip size: {pip_size}")
        out_lines.append(f"Risk: {risk_pct:.2f}%  →  ${risk_amount:,.2f}")
        out_lines.append(f"Stop distance: {stop_distance_pips:.1f} pips ({stop_distance_price:.5f} price)")
        out_lines.append(f"Lot size: {lots:.3f} lots  ({units:,.0f} units)")
        out_lines.append(f"$ per pip (per 1 lot): {pip_value_acct_per_lot:,.4f}")
        out_lines.append(f"Direction: {direction}")
        out_lines.append(f"Entry: {entry}")
        out_lines.append(f"Stop:  {stop}")
        out_lines.append(f"TP (1:2): {tp_price}")
        out_lines.append(f"Potential reward (1:2): ${potential_reward_amount:,.2f}  (~{reward_pips:.1f} pips)")

        output_var.set("\n".join(out_lines))

    except ValueError:
        messagebox.showerror("Input error", "Please ensure all numeric fields are valid numbers.")

def fill_conversion_hint(*args):
    # Simple helper to hint conversion logic
    pair = pair_var.get().strip().upper()
    if len(pair) >= 6:
        quote = pair[-3:]
        # If user’s account currency is same as quote currency, conversion is 1.0
        # We assume account currency USD. If quote == USD, prefill 1.0 as a hint.
        if quote == "USD":
            conv_var.set("1.0")

def clear_all():
    balance_var.set("")
    pair_var.set("")
    entry_var.set("")
    stop_var.set("")
    conv_var.set("")
    dir_var.set("Long")
    output_var.set("")

# --- UI ---
root = tk.Tk()
root.title(APP_TITLE)
root.resizable(False, False)

pad = 8

frm = ttk.Frame(root, padding=pad)
frm.grid(row=0, column=0)

# Inputs
balance_var = tk.StringVar()
pair_var = tk.StringVar()
entry_var = tk.StringVar()
stop_var = tk.StringVar()
conv_var = tk.StringVar()
dir_var = tk.StringVar(value="Long")
output_var = tk.StringVar()

ttk.Label(frm, text="Account Balance (in your account currency)").grid(row=0, column=0, sticky="w", padx=pad, pady=(pad, 2))
ttk.Entry(frm, textvariable=balance_var, width=28).grid(row=0, column=1, padx=pad, pady=(pad, 2))

ttk.Label(frm, text="Pair (e.g., EURUSD, USDJPY, EURGBP)").grid(row=1, column=0, sticky="w", padx=pad, pady=2)
pair_entry = ttk.Entry(frm, textvariable=pair_var, width=28)
pair_entry.grid(row=1, column=1, padx=pad, pady=2)
pair_var.trace_add("write", fill_conversion_hint)

ttk.Label(frm, text="Trade Direction").grid(row=2, column=0, sticky="w", padx=pad, pady=2)
ttk.Combobox(frm, textvariable=dir_var, values=["Long", "Short"], width=25, state="readonly").grid(row=2, column=1, padx=pad, pady=2)

ttk.Label(frm, text="Entry Price").grid(row=3, column=0, sticky="w", padx=pad, pady=2)
ttk.Entry(frm, textvariable=entry_var, width=28).grid(row=3, column=1, padx=pad, pady=2)

ttk.Label(frm, text="Stop-Loss Price").grid(row=4, column=0, sticky="w", padx=pad, pady=2)
ttk.Entry(frm, textvariable=stop_var, width=28).grid(row=4, column=1, padx=pad, pady=2)

ttk.Label(frm, text="Quote → Account conversion rate (optional)").grid(row=5, column=0, sticky="w", padx=pad, pady=2)
ttk.Entry(frm, textvariable=conv_var, width=28).grid(row=5, column=1, padx=pad, pady=2)

ttk.Label(frm, text="Risk % (fixed)").grid(row=6, column=0, sticky="w", padx=pad, pady=2)
ttk.Label(frm, text=f"{DEFAULT_RISK_PCT}%").grid(row=6, column=1, sticky="w", padx=pad, pady=2)

ttk.Label(frm, text="Risk/Reward").grid(row=7, column=0, sticky="w", padx=pad, pady=2)
ttk.Label(frm, text=f"{RR_NUM}:{RR_DEN}").grid(row=7, column=1, sticky="w", padx=pad, pady=2)

btns = ttk.Frame(frm)
btns.grid(row=8, column=0, columnspan=2, pady=(pad, 0))
ttk.Button(btns, text="Calculate", command=compute).grid(row=0, column=0, padx=pad, pady=pad)
ttk.Button(btns, text="Clear", command=clear_all).grid(row=0, column=1, padx=pad, pady=pad)

# Output
ttk.Label(frm, text="Result").grid(row=9, column=0, sticky="nw", padx=pad, pady=(pad, 2))
out_box = tk.Text(frm, height=12, width=58, wrap="word")
out_box.grid(row=9, column=1, padx=pad, pady=(pad, 2))

def bind_output(*args):
    out_box.config(state="normal")
    out_box.delete("1.0", "end")
    out_box.insert("1.0", output_var.get())
    out_box.config(state="disabled")

output_var.trace_add("write", bind_output)

# Footer hint
hint = (
    "Notes:\n"
    "• Pip size auto-detected (JPY pairs use 0.01, others 0.0001).\n"
    "• If your account currency ≠ pair’s quote currency, enter Quote→Account rate.\n"
    "  Examples (USD account): EURUSD → 1.0; USDJPY → use current USDJPY price; EURGBP → use GBPUSD.\n"
    "• Standard lot = 100,000 units.\n"
)
ttk.Label(frm, text=hint, foreground="#555").grid(row=10, column=0, columnspan=2, sticky="w", padx=pad, pady=(4, pad))

root.mainloop()
