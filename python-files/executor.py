import tkinter as tk
from tkinter import messagebox
import time

def execute_script():
    script = text_input.get("1.0", tk.END).strip()
    if not script:
        messagebox.showwarning("Błąd", "Wprowadź skrypt Lua!")
        return
    
    console_output.config(state=tk.NORMAL)
    console_output.insert(tk.END, f">>> Wykonywanie skryptu...\n{script}\n")
    console_output.insert(tk.END, "[SUKCES] Skrypt został 'wstrzyknięty' do Roblox! (Symulacja)\n\n")
    console_output.config(state=tk.DISABLED)
    text_input.delete("1.0", tk.END)

# GUI
root = tk.Tk()
root.title("Roblox Script Executor (Symulacja)")
root.geometry("600x400")

# Input
tk.Label(root, text="Wpisz skrypt Lua:").pack()
text_input = tk.Text(root, height=10, bg="#1e1e1e", fg="white", insertbackground="white")
text_input.pack(fill=tk.X, padx=10, pady=5)

# Przycisk Execute
execute_btn = tk.Button(root, text="Execute", command=execute_script, bg="#2ecc71", fg="white")
execute_btn.pack(pady=10)

# Konsola output
console_output = tk.Text(root, height=10, bg="#1e1e1e", fg="#0f0", state=tk.DISABLED)
console_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

root.mainloop()