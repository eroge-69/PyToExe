import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import numpy as np
from mpmath import mp
import threading
import time
import sys

# ---------------- ALGORITMO DE KARATSUBA ----------------
def karatsuba(x, y):
    x, y = int(x), int(y)
    if x < 10 or y < 10:
        return x * y
    m = min(len(str(x)), len(str(y))) // 2
    high1, low1 = divmod(x, 10 ** m)
    high2, low2 = divmod(y, 10 ** m)
    z0 = karatsuba(low1, low2)
    z1 = karatsuba(low1 + high1, low2 + high2)
    z2 = karatsuba(high1, high2)
    return (z2 * 10 ** (2 * m)) + ((z1 - z2 - z0) * 10 ** m) + z0

# ---------------- ALGORITMO DE STRASSEN ----------------
def strassen(a, b):
    n = len(a)
    if n == 1:
        return a * b
    mid = n // 2
    a11 = a[:mid, :mid]
    a12 = a[:mid, mid:]
    a21 = a[mid:, :mid]
    a22 = a[mid:, mid:]
    b11 = b[:mid, :mid]
    b12 = b[:mid, mid:]
    b21 = b[mid:, :mid]
    b22 = b[mid:, mid:]

    m1 = strassen(a11 + a22, b11 + b22)
    m2 = strassen(a21 + a22, b11)
    m3 = strassen(a11, b12 - b22)
    m4 = strassen(a22, b21 - b11)
    m5 = strassen(a11 + a12, b22)
    m6 = strassen(a21 - a11, b11 + b12)
    m7 = strassen(a12 - a22, b21 + b22)

    c11 = m1 + m4 - m5 + m7
    c12 = m3 + m5
    c21 = m2 + m4
    c22 = m1 - m2 + m3 + m6

    c = np.vstack((np.hstack((c11, c12)), np.hstack((c21, c22))))
    return c

# ---------------- PI ----------------
def generar_pi():
    mp.dps = 10000
    return str(mp.pi)

# ---------------- INTERFAZ KARATSUBA ----------------
def open_karatsuba(parent):
    new_window = tk.Toplevel(parent)
    new_window.title("🧮 Multiplicación Karatsuba")
    new_window.geometry("600x400")

    frame = ttk.Frame(new_window, padding=20)
    frame.pack()

    ttk.Label(frame, text="Número 1:").grid(row=0, column=0, sticky="e")
    entry1 = tk.Entry(frame, width=40)
    entry1.grid(row=0, column=1)

    ttk.Label(frame, text="Número 2:").grid(row=1, column=0, sticky="e")
    entry2 = tk.Entry(frame, width=40)
    entry2.grid(row=1, column=1)

    output = scrolledtext.ScrolledText(frame, width=60, height=6)
    output.grid(row=3, column=0, columnspan=2, pady=10)

    def run_karatsuba():
        x, y = entry1.get().strip(), entry2.get().strip()
        output.delete(1.0, tk.END)
        if not x.isdigit() or not y.isdigit():
            new_window.lift()
            messagebox.showerror("Error", "Ingrese solo números enteros positivos.", parent=new_window)
            return
        try:
            result = karatsuba(x, y)
            output.insert(tk.END, f"Resultado: {result}")
        except Exception as e:
            new_window.lift()
            messagebox.showerror("Error", str(e), parent=new_window)

    def limpiar():
        entry1.delete(0, tk.END)
        entry2.delete(0, tk.END)
        output.delete(1.0, tk.END)

    ttk.Button(frame, text="✖️ Multiplicar", command=run_karatsuba).grid(row=2, column=0, pady=5)
    ttk.Button(frame, text="🧹", command=limpiar).grid(row=2, column=1, pady=5)
    ttk.Button(frame, text="⬅️", command=new_window.destroy).grid(row=4, column=0, columnspan=2, pady=10)

# ---------------- INTERFAZ STRASSEN ----------------
def open_strassen(parent):
    new_window = tk.Toplevel(parent)
    new_window.title("📊 Multiplicación Strassen")
    new_window.geometry("700x500")

    frame = ttk.Frame(new_window, padding=20)
    frame.pack()

    ttk.Label(frame, text="Tamaño de la matriz (n x n):").grid(row=0, column=0)
    size_entry = tk.Entry(frame, width=10)
    size_entry.grid(row=0, column=1)

    progress = ttk.Progressbar(frame, orient='horizontal', mode='indeterminate', length=300)
    progress.grid(row=1, column=0, columnspan=2, pady=10)

    output = scrolledtext.ScrolledText(frame, width=80, height=15)
    output.grid(row=2, column=0, columnspan=2)

    def run_strassen():
        output.delete(1.0, tk.END)
        try:
            n_str = size_entry.get().strip()
            if not n_str.isdigit():
                raise ValueError("Ingrese un número entero positivo.")
            n = int(n_str)
            if n <= 0 or (n & (n - 1)) != 0:
                raise ValueError("El tamaño debe ser potencia de 2.")
            progress.start()
            time.sleep(1)
            a = np.random.randint(0, 10, size=(n, n))
            b = np.random.randint(0, 10, size=(n, n))
            result = strassen(a, b)
            progress.stop()
            output.insert(tk.END, f"Matriz A:\n{a}\n\nMatriz B:\n{b}\n\nResultado:\n{result}")
        except Exception as e:
            progress.stop()
            new_window.lift()
            messagebox.showerror("Error", str(e), parent=new_window)

    def start_thread():
        threading.Thread(target=run_strassen).start()

    def limpiar():
        size_entry.delete(0, tk.END)
        output.delete(1.0, tk.END)

    ttk.Button(frame, text="🧮 Generar y multiplicar", command=start_thread).grid(row=3, column=0, pady=5)
    ttk.Button(frame, text="🧹", command=limpiar).grid(row=3, column=1, pady=5)
    ttk.Button(frame, text="⬅️", command=new_window.destroy).grid(row=4, column=0, columnspan=2, pady=10)

# ---------------- INTERFAZ PI ----------------
def open_pi(parent):
    new_window = tk.Toplevel(parent)
    new_window.title("🔢 Generar π (pi)")
    new_window.geometry("700x500")

    frame = ttk.Frame(new_window, padding=20)
    frame.pack()

    output = scrolledtext.ScrolledText(frame, width=85, height=20)
    output.pack(pady=10)

    def run_pi():
        output.delete(1.0, tk.END)
        output.insert(tk.END, generar_pi())

    def limpiar():
        output.delete(1.0, tk.END)

    ttk.Button(frame, text="π Generar (10.000 cifras)", command=run_pi).pack(pady=5)
    ttk.Button(frame, text="🧹", command=limpiar).pack(pady=5)
    ttk.Button(frame, text="⬅️", command=new_window.destroy).pack(pady=10)

# ---------------- MENÚ PRINCIPAL ----------------
def main():
    root = tk.Tk()
    root.title("🧠 Algoritmos Divide y Vencerás")
    root.geometry("400x350")
    root.resizable(False, False)

    ttk.Label(root, text="Bienvenido", font=("Arial", 20)).pack(pady=20)

    ttk.Button(root, text="⚙️ Karatsuba", width=25, command=lambda: open_karatsuba(root)).pack(pady=5)
    ttk.Button(root, text="📐 Strassen", width=25, command=lambda: open_strassen(root)).pack(pady=5)
    ttk.Button(root, text="π Generar", width=25, command=lambda: open_pi(root)).pack(pady=5)

    ttk.Button(root, text="❌ Salir", width=10, command=lambda: sys.exit(0), style="Exit.TButton").pack(pady=20)

    style = ttk.Style()
    style.configure("Exit.TButton", foreground="white", background="red")

    root.mainloop()

if __name__ == "__main__":
    main()
