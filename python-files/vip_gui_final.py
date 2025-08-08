
import tkinter as tk
from tkinter import messagebox

def decoder(income):
    patt = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    patt2 = ['K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T']
    patt3 = ['F', 'G', 'H', 'I', 'J', 'P', 'Q', 'K', 'L', 'M']
    patt4 = ['P', 'O', 'N', 'M', 'L', 'K', 'D', 'C', 'E', 'F']
    patt5 = ['F', 'G', 'H', 'I', 'J', 'P', 'Q', 'K', 'L', 'M']

    digits = [int(ch) for ch in income]
    output = [
        patt[digits[0]],
        patt2[digits[1]],
        patt3[digits[2]],
        patt4[digits[3]],
        patt5[digits[4]],
    ]
    return ''.join(output)

def generate_confirm_code(decode):
    if not decode.startswith("VIP") or len(decode) < 8:
        raise ValueError("รหัส DeCode ไม่ถูกต้อง (ควรขึ้นต้นด้วย 'VIP' และตามด้วย 5 หลัก)")

    numeric_part = decode[3:8]
    decoded_part = decoder(numeric_part)
    return f"VIP{decoded_part}TDR"

def on_generate():
    code = entry.get().strip()
    try:
        confirm = generate_confirm_code(code)
        messagebox.showinfo("ผลลัพธ์", f"Confirm Code:\n{confirm}")
    except Exception as e:
        messagebox.showerror("ข้อผิดพลาด", str(e))

root = tk.Tk()
root.title("Credit Code VIP Generator")
root.geometry("330x160")

label = tk.Label(root, text="ป้อนรหัส DeCode เช่น VIP89696:", font=("Tahoma", 10))
label.pack(pady=(10, 0))

entry = tk.Entry(root, font=("Tahoma", 12), justify='center')
entry.pack(pady=5)

btn = tk.Button(root, text="Generate", bg="green", fg="white", font=("Tahoma", 10), command=on_generate)
btn.pack(pady=5)

root.mainloop()
