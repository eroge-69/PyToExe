
import tkinter as tk
from tkinter import filedialog, messagebox

def wypelnij_szablon():
    sciezka = filedialog.askopenfilename(title="Wybierz plik szablonu", filetypes=[("Pliki tekstowe", "*.txt")])
    if not sciezka:
        return

    try:
        with open(sciezka, "r", encoding="utf-8") as f:
            tekst = f.read()
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie można otworzyć pliku: {e}")
        return

    dane = {
        "{{var1}}": var1_var.get(),
        "{{var2}}": var2_var.get(),
        "{{var3}}": var3_var.get(),
        "{{var4}}": var4_var.get()
    }

    for szukany, nowy in dane.items():
        tekst = tekst.replace(szukany, nowy)

    nowa_sciezka = sciezka.replace(".txt", "_wypelniony.txt")
    try:
        with open(nowa_sciezka, "w", encoding="utf-8") as f:
            f.write(tekst)
        messagebox.showinfo("Sukces", f"Plik zapisany jako:\n{nowa_sciecka}")
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie można zapisać pliku: {e}")

root = tk.Tk()
root.title("Wypełniacz szablonu TXT (var1-var4)")

tk.Label(root, text="var1:").grid(row=0, column=0, sticky="e")
tk.Label(root, text="var2:").grid(row=1, column=0, sticky="e")
tk.Label(root, text="var3:").grid(row=2, column=0, sticky="e")
tk.Label(root, text="var4:").grid(row=3, column=0, sticky="e")

var1_var = tk.StringVar()
var2_var = tk.StringVar()
var3_var = tk.StringVar()
var4_var = tk.StringVar()

tk.Entry(root, textvariable=var1_var).grid(row=0, column=1)
tk.Entry(root, textvariable=var2_var).grid(row=1, column=1)
tk.Entry(root, textvariable=var3_var).grid(row=2, column=1)
tk.Entry(root, textvariable=var4_var).grid(row=3, column=1)

tk.Button(root, text="Wybierz szablon i generuj", command=wypelnij_szablon).grid(row=4, column=0, columnspan=2, pady=10)

root.mainloop()
