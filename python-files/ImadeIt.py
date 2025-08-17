import tkinter as tk
from tkinter import ttk, messagebox

# -------------------------
# Error "table" (in-code)
# -------------------------
ERROR_TABLE = {
    "empty":      ("Missing Input", "Please type a number first. type a fuckin number this time mouth breather."),
    "invalid_int":("Invalid Input", "Please enter a valid integer. Do it or im gonna reach through the screen and harm you"),
    "negative":   ("Out of Range", "Please enter a number ≥ 0. Your lack of fuckin iq is concerning"),
    "too_large":  ("Number Too Large", "Please enter a number ≤ 1_000_000. please.... just fuckin do it."),
}

def show_error(key: str, fallback=("Error", "Something went wrong. How could you have fucked this up")):
    """
    Show an error popup.
    - If key matches ERROR_TABLE -> use predefined title & message.
    - If key contains "Title|Message" -> split and use directly.
    - Otherwise, treat key as a message body with fallback title.
    """
    if key in ERROR_TABLE:
        title, msg = ERROR_TABLE[key]
        return messagebox.showerror(title, msg)

    if "|" in key:
        title, msg = key.split("|", 1)
        return messagebox.showerror(title.strip(), msg.strip())

    title, msg = fallback
    return messagebox.showerror(title, key)

# -------------------------
# Core logic
# -------------------------
def sieve_of_eratosthenes(n: int):
    if n < 2:
        return []
    prime = [True] * (n + 1)
    prime[0] = prime[1] = False
    for p in range(2, int(n**0.5) + 1):
        if prime[p]:
            prime[p*p:n+1:p] = [False] * len(range(p*p, n+1, p))
    return [i for i, is_prime in enumerate(prime) if is_prime]

# -------------------------
# GUI actions
# -------------------------
MAX_N = 1_000_000  # change if you want a different upper bound

def calculate_primes():
    s = entry.get().strip()
    if not s:
        # Using a table key
        return show_error("empty")

    try:
        n = int(s)
    except ValueError:
        # Using a custom inline Title|Message
        return show_error("Invalid Input|That wasn’t a number dipshit, try again and do it fuckin right")

    if n < 0:
        return show_error("Out of Range|Negative numbers are not valid here. Tell me how fuckin retarded are you? nothing below us")
    if n > MAX_N:
        return show_error(f"Too Large|Please enter a number, this is for fuckin prime numbers within the max value you set, NUMBERS YOU SET IN THE RANGE TO FIND YOU JARHEAD ≤ {MAX_N:,}.")

    primes = sieve_of_eratosthenes(n)
    result_text.config(state="normal")
    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, f"Primes up to {n} ({len(primes)} total):\n\n")
    # Keep output readable for large n
    if len(primes) > 200:
        result_text.insert(tk.END, ", ".join(map(str, primes[:200])) + ", ...")
        result_text.insert(tk.END, f"\n\n(Showing first 200 of {len(primes)} primes.)")
    else:
        result_text.insert(tk.END, ", ".join(map(str, primes)))
    result_text.config(state="disabled")

def clear_output():
    result_text.config(state="normal")
    result_text.delete("1.0", tk.END)
    result_text.config(state="disabled")
    entry.delete(0, tk.END)
    entry.focus_set()

# -------------------------
# Build GUI
# -------------------------
root = tk.Tk()
root.title("Sieve of Eratosthenes")

main = ttk.Frame(root, padding=12)
main.pack(fill="both", expand=True)

# Input row
row_top = ttk.Frame(main)
row_top.pack(fill="x", pady=(0, 8))

ttk.Label(row_top, text="Enter an integer (0 – {:,}):".format(MAX_N)).pack(side="left")
entry = ttk.Entry(row_top, width=18)
entry.pack(side="left", padx=(8, 8))
entry.focus_set()

btn_run = ttk.Button(row_top, text="Find Primes", command=calculate_primes)
btn_run.pack(side="left")

btn_clear = ttk.Button(row_top, text="Clear", command=clear_output)
btn_clear.pack(side="left", padx=(8, 0))

# Output text with vertical scrollbar
out_frame = ttk.Frame(main)
out_frame.pack(fill="both", expand=True)

result_text = tk.Text(out_frame, wrap="word", height=16, state="disabled")
scrollbar = ttk.Scrollbar(out_frame, orient="vertical", command=result_text.yview)
result_text.configure(yscrollcommand=scrollbar.set)

result_text.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Run
root.mainloop()
# fuctions ripped from stack overflow and tweaked to my liking with some things parts of labled as such 
# gui added because i like it