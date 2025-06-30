
import tkinter as tk
from tkinter import messagebox
import numpy as np

# Główne okno aplikacji
app = tk.Tk()
app.title("Wektory - Liniowa niezależność i kombinacja liniowa")
app.geometry("600x500")

# --- Sekcja 1: Sprawdzenie liniowej niezależności ---

tk.Label(app, text="Sprawdź liniową niezależność 3 wektorów (oddzielone spacjami)").pack(pady=10)
tk.Label(app, text="Wektor a:").pack()
entry_v1 = tk.Entry(app, width=40)
entry_v1.pack()

tk.Label(app, text="Wektor b:").pack()
entry_v2 = tk.Entry(app, width=40)
entry_v2.pack()

tk.Label(app, text="Wektor c:").pack()
entry_v3 = tk.Entry(app, width=40)
entry_v3.pack()

def check_independence():
    try:
        v1 = list(map(int, entry_v1.get().split()))
        v2 = list(map(int, entry_v2.get().split()))
        v3 = list(map(int, entry_v3.get().split()))
        matrix = np.column_stack((v1, v2, v3))
        rank = np.linalg.matrix_rank(matrix)
        if rank == 3:
            messagebox.showinfo("Wynik", "✅ Wektory są liniowo niezależne.")
        else:
            messagebox.showinfo("Wynik", "❌ Wektory są liniowo zależne.")
    except:
        messagebox.showerror("Błąd", "Wprowadź poprawne dane (np. 1 2 3).")

tk.Button(app, text="Sprawdź niezależność", command=check_independence).pack(pady=10)

# --- Sekcja 2: Oblicz kombinację liniową ---

tk.Label(app, text="\nOblicz współczynniki kombinacji liniowej: w = a*v1 + b*v2 + c*v3").pack(pady=10)

tk.Label(app, text="Wektor v1:").pack()
entry_c1 = tk.Entry(app, width=40)
entry_c1.pack()

tk.Label(app, text="Wektor v2:").pack()
entry_c2 = tk.Entry(app, width=40)
entry_c2.pack()

tk.Label(app, text="Wektor v3:").pack()
entry_c3 = tk.Entry(app, width=40)
entry_c3.pack()

tk.Label(app, text="Wektor w:").pack()
entry_w = tk.Entry(app, width=40)
entry_w.pack()

def find_coefficients():
    try:
        v1 = list(map(int, entry_c1.get().split()))
        v2 = list(map(int, entry_c2.get().split()))
        v3 = list(map(int, entry_c3.get().split()))
        w = list(map(int, entry_w.get().split()))
        A = np.column_stack((v1, v2, v3))
        coeffs = np.linalg.lstsq(A, w, rcond=None)[0]
        result = f"{coeffs[0]:.2f} * v1 + {coeffs[1]:.2f} * v2 + {coeffs[2]:.2f} * v3"
        messagebox.showinfo("Wynik", f"Rozwiązanie:\n{result}")
    except:
        messagebox.showerror("Błąd", "Wprowadź poprawne dane (np. 1 2 3).")

tk.Button(app, text="Oblicz współczynniki", command=find_coefficients).pack(pady=10)

# Zakończenie
app.mainloop()
