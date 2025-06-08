import tkinter as tk

def generiere_und_schliessen():
    try:
        anzahl = int(entry_anzahl.get())
        prefix = entry_prefix.get().replace(" ", "")  # Leerzeichen entfernen
        if not 1 <= anzahl <= 100:
            return
        zahlen = "\n".join(f"{prefix}{i}" for i in range(1, anzahl + 1))
        root.clipboard_clear()
        root.clipboard_append(zahlen)
        root.update()  # Wichtig: Zwischenablage aktualisieren
        root.after(100, root.destroy)  # 100 ms warten, dann schließen
    except:
        root.destroy()  # Bei Fehler sofort schließen

root = tk.Tk()
root.title("Link-Generator")
root.resizable(False, False)

tk.Label(root, text="Anzahl Eisoden?").pack(pady=2)
entry_anzahl = tk.Entry(root)
entry_anzahl.pack(pady=2)
entry_anzahl.insert(0, "12")

tk.Label(root, text="Link").pack(pady=2)
entry_prefix = tk.Entry(root)
entry_prefix.pack(pady=2)

tk.Button(root, text="Links generieren", command=generiere_und_schliessen).pack(pady=10)

root.mainloop()
