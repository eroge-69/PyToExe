import tkinter as tk
from tkinter import ttk, messagebox
import secrets, string

ALFABETO = string.ascii_letters + string.digits

def generar():
    try:
        n = int(spin_cant.get())
        l = int(spin_len.get())
        if n <= 0 or l <= 0:
            raise ValueError
    except Exception:
        messagebox.showerror("Error", "Valores inválidos")
        return
    salida.configure(state="normal")
    salida.delete("1.0", "end")
    vistos = set()
    while len(vistos) < n:
        s = "".join(secrets.choice(ALFABETO) for _ in range(l))
        if s not in vistos:
            vistos.add(s)
            salida.insert("end", s + "\n")
    salida.configure(state="disabled")

def copiar():
    data = salida.get("1.0", "end").strip()
    if data:
        root.clipboard_clear()
        root.clipboard_append(data)
        messagebox.showinfo("Copiado", "IDs copiados")

root = tk.Tk()
root.title("Generador de IDs")
root.geometry("600x420")
root.minsize(520, 360)

# Estilos ttk sin archivos externos
style = ttk.Style()
style.theme_use(style.theme_use())  # usa el tema por defecto de la plataforma
style.configure("TLabel", font=("Segoe UI", 10))
style.configure("TButton", font=("Segoe UI", 10))
style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"))
style.configure("Accent.TButton", foreground="white")
style.map("Accent.TButton", background=[("active", "#2563eb"), ("!active", "#1d4ed8")])
style.configure("Accent.TButton", background="#1d4ed8")  # azul simple
style.configure("Card.TFrame", padding=16)

card = ttk.Frame(root, style="Card.TFrame")
card.pack(fill="both", expand=True, padx=12, pady=12)

ttk.Label(card, text="Generador de IDs", style="Header.TLabel").grid(row=0, column=0, columnspan=6, sticky="w", pady=(0, 8))

ttk.Label(card, text="Cantidad").grid(row=1, column=0, sticky="w")
spin_cant = ttk.Spinbox(card, from_=1, to=100000, width=10)
spin_cant.set(10)
spin_cant.grid(row=1, column=1, padx=(6, 18))

ttk.Label(card, text="Longitud").grid(row=1, column=2, sticky="w")
spin_len = ttk.Spinbox(card, from_=1, to=512, width=10)
spin_len.set(16)
spin_len.grid(row=1, column=3, padx=(6, 18))

ttk.Button(card, text="Generar", style="Accent.TButton", command=generar).grid(row=1, column=4, padx=6)
ttk.Button(card, text="Copiar", command=copiar).grid(row=1, column=5, padx=6)

salida = tk.Text(card, height=14, wrap="none", font=("Consolas", 10))
salida.grid(row=2, column=0, columnspan=6, pady=10, sticky="nsew")
salida.configure(state="disabled")

scroll_y = ttk.Scrollbar(card, orient="vertical", command=salida.yview)
scroll_y.grid(row=2, column=6, sticky="ns")
salida.configure(yscrollcommand=scroll_y.set)

card.columnconfigure(0, weight=1)
card.rowconfigure(2, weight=1)

root.mainloop()
