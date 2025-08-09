import tkinter as tk
from tkinter import messagebox

# 🌍 Leere Werkzeugliste beim Start
werkzeuge = []

# ➕ Werkzeug hinzufügen mit Eingabemaske
def werkzeug_hinzufuegen(parent):
    fenster = tk.Toplevel(parent)
    fenster.title("➕ Werkzeug hinzufügen")

    labels = ["🔧 Name:", "📦 Barcode:", "📍 Standort:", "⚡ Ladestand (%):", "⏰ Wartungstermin:", "📝 Infos:"]
    entries = []

    for i, text in enumerate(labels):
        tk.Label(fenster, text=text).grid(row=i, column=0, sticky="e", padx=5, pady=5)
        entry = tk.Entry(fenster, width=40)
        entry.grid(row=i, column=1, padx=5, pady=5)
        entries.append(entry)

    def speichern():
        daten = [e.get() for e in entries]
        if daten[0] and daten[1]:  # Name und Barcode erforderlich
            werkzeuge.append({
                "name": daten[0],
                "barcode": daten[1],
                "standort": daten[2],
                "ladestand": daten[3],
                "wartung": daten[4],
                "infos": daten[5]
            })
            messagebox.showinfo("Erfolg", f"Werkzeug '{daten[0]}' wurde hinzugefügt.")
            fenster.destroy()
        else:
            messagebox.showwarning("Fehler", "Name und Barcode sind erforderlich.")

    tk.Button(fenster, text="✅ OK", command=speichern).grid(row=len(labels), column=0, columnspan=2, pady=10)

# 📋 Übersicht anzeigen mit Entfernen-, Info- und Bearbeiten-Funktion
def zeige_uebersicht(parent):
    def aktualisiere_listbox():
        listbox.delete(0, tk.END)
        for w in werkzeuge:
            listbox.insert(tk.END, f"{w['name']} – {w['standort']} – {w['ladestand']}%")

    def entfernen():
        auswahl = listbox.curselection()
        if not auswahl:
            messagebox.showwarning("Hinweis", "Bitte ein Werkzeug auswählen.")
            return
        index = auswahl[0]
        name = werkzeuge[index]["name"]
        if messagebox.askyesno("Entfernen", f"Möchtest du '{name}' wirklich entfernen?"):
            del werkzeuge[index]
            messagebox.showinfo("Entfernt", f"Werkzeug '{name}' wurde entfernt.")
            fenster.destroy()

    def zeige_infos():
        auswahl = listbox.curselection()
        if not auswahl:
            messagebox.showwarning("Hinweis", "Bitte ein Werkzeug auswählen.")
            return
        w = werkzeuge[auswahl[0]]
        info_text = (
            f"🔧 Name: {w['name']}\n"
            f"📦 Barcode: {w['barcode']}\n"
            f"📍 Standort: {w['standort']}\n"
            f"⚡ Ladestand: {w['ladestand']}%\n"
            f"⏰ Wartung: {w['wartung']}\n"
            f"📝 Infos: {w['infos']}"
        )
        messagebox.showinfo("Werkzeug-Infos", info_text)

    def bearbeiten():
        auswahl = listbox.curselection()
        if not auswahl:
            messagebox.showwarning("Hinweis", "Bitte ein Werkzeug auswählen.")
            return
        index = auswahl[0]
        w = werkzeuge[index]

        edit_win = tk.Toplevel(fenster)
        edit_win.title(f"✏️ Bearbeite: {w['name']}")

        labels = ["📍 Standort:", "⚡ Ladestand (%):", "⏰ Wartungstermin:", "📝 Infos:"]
        keys = ["standort", "ladestand", "wartung", "infos"]
        entries = []

        for i, label in enumerate(labels):
            tk.Label(edit_win, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entry = tk.Entry(edit_win, width=40)
            entry.insert(0, w[keys[i]])
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries.append(entry)

        def speichern():
            for i, key in enumerate(keys):
                w[key] = entries[i].get()
            messagebox.showinfo("Gespeichert", f"Werkzeug '{w['name']}' wurde aktualisiert.")
            aktualisiere_listbox()
            edit_win.destroy()

        tk.Button(edit_win, text="✅ Speichern", command=speichern).grid(row=len(labels), column=0, columnspan=2, pady=10)

    fenster = tk.Toplevel(parent)
    fenster.title("📋 Werkzeugübersicht")

    listbox = tk.Listbox(fenster, width=50, height=10)
    listbox.pack(padx=10, pady=10)

    btn_frame = tk.Frame(fenster)
    btn_frame.pack(pady=5)

    tk.Button(btn_frame, text="❌ Entfernen", command=entfernen).pack(side="left", padx=5)
    tk.Button(btn_frame, text="ℹ️ Infos", command=zeige_infos).pack(side="left", padx=5)
    tk.Button(btn_frame, text="✏️ Bearbeiten", command=bearbeiten).pack(side="left", padx=5)

    aktualisiere_listbox()

# 🔍 Scan-Funktion – sucht Barcode in Werkzeugliste
def zeige_infos(entry, name_label, standort_label, ladestand_label, wartung_label):
    barcode = entry.get().strip()
    if not barcode:
        messagebox.showwarning("Hinweis", "Bitte Barcode eingeben.")
        return

    gefunden = None
    for w in werkzeuge:
        if w["barcode"] == barcode:
            gefunden = w
            break

    if gefunden:
        name_label.config(text=f"🔧 Name: {gefunden['name']}")
        standort_label.config(text=f"📍 Standort: {gefunden['standort']}")
        ladestand_label.config(text=f"⚡ Ladestand: {gefunden['ladestand']}%")
        wartung_label.config(text=f"⏰ Wartung: {gefunden['wartung']}")
    else:
        messagebox.showinfo("Nicht gefunden", f"Kein Werkzeug mit Barcode '{barcode}' gefunden.")
        name_label.config(text="🔧 Name:")
        standort_label.config(text="📍 Standort:")
        ladestand_label.config(text="⚡ Ladestand:")
        wartung_label.config(text="⏰ Wartung:")

# 🧭 Hauptfenster öffnen
def öffne_hauptfenster(name):
    if not name.strip():
        messagebox.showerror("Fehler", "Bitte gib deinen Namen ein.")
        return

    root.destroy()
    main_window = tk.Tk()
    main_window.title(f"Werkzeugverwaltung – Willkommen, {name}")

    tk.Label(main_window, text="📦 Barcode eingeben:").pack()
    barcode_entry = tk.Entry(main_window)
    barcode_entry.pack()

    name_label = tk.Label(main_window, text="🔧 Name:")
    standort_label = tk.Label(main_window, text="📍 Standort:")
    ladestand_label = tk.Label(main_window, text="⚡ Ladestand:")
    wartung_label = tk.Label(main_window, text="⏰ Wartung:")

    tk.Button(main_window, text="🔍 Scannen", command=lambda: zeige_infos(barcode_entry, name_label, standort_label, ladestand_label, wartung_label)).pack(pady=5)
    tk.Button(main_window, text="➕ Werkzeug hinzufügen", command=lambda: werkzeug_hinzufuegen(main_window)).pack(pady=5)
    tk.Button(main_window, text="📋 Übersicht anzeigen", command=lambda: zeige_uebersicht(main_window)).pack(pady=5)

    name_label.pack()
    standort_label.pack()
    ladestand_label.pack()
    wartung_label.pack()

    main_window.mainloop()

# 🔐 Login-Fenster
root = tk.Tk()
root.title("🔐 Anmeldung")

tk.Label(root, text="Bitte gib deinen Namen ein:").pack(pady=10)
name_entry = tk.Entry(root)
name_entry.pack(pady=5)

tk.Button(root, text="Weiter", command=lambda: öffne_hauptfenster(name_entry.get())).pack(pady=10)

root.mainloop()