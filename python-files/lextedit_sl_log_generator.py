import tkinter as tk
from tkinter import messagebox
import pyperclip

def generate_queries():
    input_text = mapping_text.get("1.0", tk.END).strip()
    if not input_text:
        messagebox.showerror("Input Error", "Please enter at least one ordnum with subnums.")
        return

    output_text.delete("1.0", tk.END)

    try:
        for line in input_text.splitlines():
            if ':' not in line:
                continue
            ordnum_part, subnums_part = line.split(':', 1)
            ordnum = ordnum_part.strip()
            subnums = [s.strip() for s in subnums_part.split(',') if s.strip()]
            
            for subnum in subnums:
                query = f"""sl_log event
 where evt_id = 'DSS_CUSTOM_ORDER'
   and ordnum = '{ordnum}'
   and wh_id = 'S'
   and client_id = '----'
   and subnum = '{subnum}'
   and filetyp = 'F'
   and sys_id = 'DCS' catch(@?);\n"""
                output_text.insert(tk.END, query)
    except Exception as e:
        messagebox.showerror("Parsing Error", f"An error occurred while parsing:\\n{e}")

def copy_to_clipboard():
    text = output_text.get("1.0", tk.END)
    pyperclip.copy(text)
    messagebox.showinfo("Copied", "Generated queries copied to clipboard!")

# GUI Setup
root = tk.Tk()
root.title("LextEdit sl_log Generator (Mapped)")

tk.Label(root, text="Enter mapping (ordnum: subnum1, subnum2, ...):").pack(pady=(10, 0))
mapping_text = tk.Text(root, height=8, width=80, wrap=tk.WORD)
mapping_text.pack(padx=10)

tk.Button(root, text="Generate", command=generate_queries).pack(pady=10)

output_frame = tk.Frame(root)
output_frame.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)

output_text = tk.Text(output_frame, height=20, width=80, wrap=tk.WORD)
output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(output_frame, command=output_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
output_text.config(yscrollcommand=scrollbar.set)

tk.Button(root, text="Copy to Clipboard", command=copy_to_clipboard).pack(pady=(0, 10))

root.mainloop()