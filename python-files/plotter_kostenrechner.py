#!/usr/bin/env python3
"""
Plotter-Kostenrechner
GUI-Tool (Tkinter) zur Berechnung der Material- und Tintenkosten für Drucke

Features:
- Wahl zwischen Rollenmaterial oder Einzelblatt
- Eingabe von Rollen-/Blattmaßen und Preisen
- Eingabe von Zielbildgröße
- Tintenparameter (Anzahl Patronen, ml pro Patrone, Preis pro Patrone, Verbrauch ml/m²)
- Zusätzliche Kosten: Keilrahmen, Firnis, Arbeitszeit
- Ergebnisanzeige und Export als CSV

Speichern als Plotter-Kostenrechner.py und ausführen mit:
    python Plotter-Kostenrechner.py

"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import math

# ---------- Hilfsfunktionen ----------

def calc_from_rolle(breite_cm, laenge_m, preis_eur):
    breite_m = breite_cm / 100.0
    flaeche_m2 = breite_m * laenge_m
    preis_pro_m2 = preis_eur / flaeche_m2 if flaeche_m2 > 0 else 0.0
    return flaeche_m2, preis_pro_m2


def calc_from_blatt(breite_cm, hoehe_cm, preis_eur):
    breite_m = breite_cm / 100.0
    hoehe_m = hoehe_cm / 100.0
    flaeche_m2 = breite_m * hoehe_m
    preis_pro_m2 = preis_eur / flaeche_m2 if flaeche_m2 > 0 else 0.0
    return flaeche_m2, preis_pro_m2


def calc_tinte(patronen, ml_pro_pat, preis_pro_pat, verbrauch_ml_m2, ziel_flaeche_m2):
    gesamt_ml = patronen * ml_pro_pat
    gesamt_eur = patronen * preis_pro_pat
    preis_pro_ml = gesamt_eur / gesamt_ml if gesamt_ml > 0 else 0.0
    verbrauch_ml = verbrauch_ml_m2 * ziel_flaeche_m2
    kosten = verbrauch_ml * preis_pro_ml
    return {
        'gesamt_ml': gesamt_ml,
        'gesamt_eur': gesamt_eur,
        'preis_pro_ml': preis_pro_ml,
        'verbrauch_ml': verbrauch_ml,
        'kosten': kosten
    }

# ---------- GUI ----------

class PlotterKostenGUI:
    def __init__(self, root):
        self.root = root
        root.title('Plotter Kostenrechner')

        frm = ttk.Frame(root, padding=12)
        frm.grid(row=0, column=0, sticky='nsew')

        # Materialquelle
        self.quelle_var = tk.StringVar(value='rolle')
        ttk.Label(frm, text='Materialquelle:').grid(row=0, column=0, sticky='w')
        ttk.Radiobutton(frm, text='Rolle', variable=self.quelle_var, value='rolle', command=self.toggle_material).grid(row=0, column=1)
        ttk.Radiobutton(frm, text='Blatt', variable=self.quelle_var, value='blatt', command=self.toggle_material).grid(row=0, column=2)

        # Rolle Eingaben
        self.rolle_breite_var = tk.DoubleVar(value=61.0)
        self.rolle_laenge_var = tk.DoubleVar(value=25.0)
        self.rolle_preis_var = tk.DoubleVar(value=150.0)

        ttk.Label(frm, text='Rollenbreite (cm):').grid(row=1, column=0, sticky='w')
        ttk.Entry(frm, textvariable=self.rolle_breite_var, width=12).grid(row=1, column=1, sticky='w')
        ttk.Label(frm, text='Rollenlänge (m):').grid(row=1, column=2, sticky='w')
        ttk.Entry(frm, textvariable=self.rolle_laenge_var, width=12).grid(row=1, column=3, sticky='w')
        ttk.Label(frm, text='Rollenpreis (EUR):').grid(row=1, column=4, sticky='w')
        ttk.Entry(frm, textvariable=self.rolle_preis_var, width=12).grid(row=1, column=5, sticky='w')

        # Blatt Eingaben
        self.blatt_breite_var = tk.DoubleVar(value=0.0)
        self.blatt_hoehe_var = tk.DoubleVar(value=0.0)
        self.blatt_preis_var = tk.DoubleVar(value=0.0)

        ttk.Label(frm, text='Blattbreite (cm):').grid(row=2, column=0, sticky='w')
        ttk.Entry(frm, textvariable=self.blatt_breite_var, width=12).grid(row=2, column=1, sticky='w')
        ttk.Label(frm, text='Blatthöhe (cm):').grid(row=2, column=2, sticky='w')
        ttk.Entry(frm, textvariable=self.blatt_hoehe_var, width=12).grid(row=2, column=3, sticky='w')
        ttk.Label(frm, text='Blattpreis (EUR):').grid(row=2, column=4, sticky='w')
        ttk.Entry(frm, textvariable=self.blatt_preis_var, width=12).grid(row=2, column=5, sticky='w')

        # Zielbild
        ttk.Separator(frm, orient='horizontal').grid(row=3, column=0, columnspan=6, sticky='ew', pady=6)
        ttk.Label(frm, text='Zielbildgröße (cm)').grid(row=4, column=0, sticky='w')
        self.ziel_b_var = tk.DoubleVar(value=40.0)
        self.ziel_h_var = tk.DoubleVar(value=60.0)
        ttk.Entry(frm, textvariable=self.ziel_b_var, width=10).grid(row=4, column=1, sticky='w')
        ttk.Label(frm, text='x').grid(row=4, column=2)
        ttk.Entry(frm, textvariable=self.ziel_h_var, width=10).grid(row=4, column=3, sticky='w')

        # Tinte
        ttk.Separator(frm, orient='horizontal').grid(row=5, column=0, columnspan=6, sticky='ew', pady=6)
        ttk.Label(frm, text='Tinten-Parameter').grid(row=6, column=0, sticky='w')
        self.patronen_var = tk.IntVar(value=8)
        self.ml_pro_pat_var = tk.DoubleVar(value=220.0)
        self.preis_pro_pat_var = tk.DoubleVar(value=110.0)
        self.verbrauch_var = tk.DoubleVar(value=10.0)

        ttk.Label(frm, text='Patronen:').grid(row=7, column=0, sticky='w')
        ttk.Entry(frm, textvariable=self.patronen_var, width=8).grid(row=7, column=1, sticky='w')
        ttk.Label(frm, text='ml/Patrone:').grid(row=7, column=2, sticky='w')
        ttk.Entry(frm, textvariable=self.ml_pro_pat_var, width=10).grid(row=7, column=3, sticky='w')
        ttk.Label(frm, text='Preis/Patrone (EUR):').grid(row=7, column=4, sticky='w')
        ttk.Entry(frm, textvariable=self.preis_pro_pat_var, width=12).grid(row=7, column=5, sticky='w')

        ttk.Label(frm, text='Verbrauch (ml/m²):').grid(row=8, column=0, sticky='w')
        ttk.Entry(frm, textvariable=self.verbrauch_var, width=10).grid(row=8, column=1, sticky='w')

        # Zusatzkosten
        ttk.Separator(frm, orient='horizontal').grid(row=9, column=0, columnspan=6, sticky='ew', pady=6)
        ttk.Label(frm, text='Zusatzkosten (EUR)').grid(row=10, column=0, sticky='w')
        self.keilrahmen_var = tk.DoubleVar(value=0.0)
        self.firnis_var = tk.DoubleVar(value=0.0)
        self.arbeit_var = tk.DoubleVar(value=0.0)
        ttk.Label(frm, text='Keilrahmen:').grid(row=11, column=0, sticky='w')
        ttk.Entry(frm, textvariable=self.keilrahmen_var, width=10).grid(row=11, column=1, sticky='w')
        ttk.Label(frm, text='Firnis:').grid(row=11, column=2, sticky='w')
        ttk.Entry(frm, textvariable=self.firnis_var, width=10).grid(row=11, column=3, sticky='w')
        ttk.Label(frm, text='Arbeitszeit:').grid(row=11, column=4, sticky='w')
        ttk.Entry(frm, textvariable=self.arbeit_var, width=10).grid(row=11, column=5, sticky='w')

        # Buttons
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=12, column=0, columnspan=6, pady=(10,0))
        ttk.Button(btn_frame, text='Berechnen', command=self.berechnen).grid(row=0, column=0, padx=6)
        ttk.Button(btn_frame, text='Export CSV', command=self.export_csv).grid(row=0, column=1, padx=6)
        ttk.Button(btn_frame, text='Beenden', command=root.quit).grid(row=0, column=2, padx=6)

        # Ergebnis
        ttk.Separator(frm, orient='horizontal').grid(row=13, column=0, columnspan=6, sticky='ew', pady=6)
        self.result_text = tk.Text(frm, height=10, width=80, wrap='word')
        self.result_text.grid(row=14, column=0, columnspan=6)
        self.result_text.insert('1.0', 'Klicke auf Berechnen, um die Kosten zu sehen.')
        self.result_text.config(state='disabled')

        self.toggle_material()

    def toggle_material(self):
        q = self.quelle_var.get()
        # If needed, adjust widget states (in this simple GUI we leave them editable)
        # Could add disabling for unused inputs in future

    def berechnen(self):
        try:
            ziel_b = float(self.ziel_b_var.get())
            ziel_h = float(self.ziel_h_var.get())
            ziel_flaeche = (ziel_b/100.0) * (ziel_h/100.0)

            if self.quelle_var.get() == 'rolle':
                fl_rolle, preis_m2 = calc_from_rolle(float(self.rolle_breite_var.get()), float(self.rolle_laenge_var.get()), float(self.rolle_preis_var.get()))
                material_preis = preis_m2 * ziel_flaeche
                quelle_text = f'Rolle: {self.rolle_breite_var.get()} cm x {self.rolle_laenge_var.get()} m'
            else:
                fl_blatt, preis_m2 = calc_from_blatt(float(self.blatt_breite_var.get()), float(self.blatt_hoehe_var.get()), float(self.blatt_preis_var.get()))
                material_preis = preis_m2 * ziel_flaeche
                quelle_text = f'Blatt: {self.blatt_breite_var.get()} cm x {self.blatt_hoehe_var.get()} cm'

            tinte = calc_tinte(int(self.patronen_var.get()), float(self.ml_pro_pat_var.get()), float(self.preis_pro_pat_var.get()), float(self.verbrauch_var.get()), ziel_flaeche)

            gesamt = material_preis + tinte['kosten'] + float(self.keilrahmen_var.get()) + float(self.firnis_var.get()) + float(self.arbeit_var.get())

            # Ausgabe
            out_lines = []
            out_lines.append('--- Plotter Kostenberechnung ---')
            out_lines.append(f'Bildgröße: {ziel_b:.0f} x {ziel_h:.0f} cm  (Fläche: {ziel_flaeche:.4f} m²)')
            out_lines.append(quelle_text)
            out_lines.append(f'Materialpreis (Leinwand/Papier): {material_preis:.2f} EUR  (Preis/m²: {preis_m2:.3f} EUR/m²)')
            out_lines.append(f'Tintenverbrauch: {tinte["verbrauch_ml"]:.2f} ml -> Kosten: {tinte["kosten"]:.2f} EUR')
            out_lines.append(f'Tintenpreis gesamt: {tinte["gesamt_eur"]:.2f} EUR für {tinte["gesamt_ml"]:.0f} ml => {tinte["preis_pro_ml"]:.3f} EUR/ml')
            out_lines.append('\nZusatzkosten:')
            out_lines.append(f'  Keilrahmen: {float(self.keilrahmen_var.get()):.2f} EUR')
            out_lines.append(f'  Firnis: {float(self.firnis_var.get()):.2f} EUR')
            out_lines.append(f'  Arbeitszeit: {float(self.arbeit_var.get()):.2f} EUR')
            out_lines.append(f'\n=> Gesamtpreis pro Bild: {gesamt:.2f} EUR')

            self.last_result = {
                'ziel_b': ziel_b,
                'ziel_h': ziel_h,
                'flaeche_m2': ziel_flaeche,
                'quelle': quelle_text,
                'material_preis': material_preis,
                'preis_m2': preis_m2,
                'tinte': tinte,
                'zusatz': {
                    'keilrahmen': float(self.keilrahmen_var.get()),
                    'firnis': float(self.firnis_var.get()),
                    'arbeit': float(self.arbeit_var.get())
                },
                'gesamt': gesamt
            }

            self.result_text.config(state='normal')
            self.result_text.delete('1.0', 'end')
            self.result_text.insert('1.0', '\n'.join(out_lines))
            self.result_text.config(state='disabled')

        except Exception as e:
            messagebox.showerror('Fehler', f'Fehler bei der Berechnung: {e}')

    def export_csv(self):
        if not hasattr(self, 'last_result'):
            messagebox.showinfo('Info', 'Bitte erst auf Berechnen klicken, bevor du exportierst.')
            return
        fpath = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV Dateien', '*.csv')], title='Speichern als CSV')
        if not fpath:
            return
        try:
            data = self.last_result
            with open(fpath, 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(['Feld', 'Wert'])
                w.writerow(['Bildgröße (cm)', f"{data['ziel_b']} x {data['ziel_h']}"])
                w.writerow(['Fläche (m2)', f"{data['flaeche_m2']:.4f}"])
                w.writerow(['Materialquelle', data['quelle']])
                w.writerow(['Materialpreis (EUR)', f"{data['material_preis']:.2f}"])
                w.writerow(['Preis/m2 (EUR)', f"{data['preis_m2']:.3f}"])
                w.writerow(['Tintenverbrauch (ml)', f"{data['tinte']['verbrauch_ml']:.2f}"])
                w.writerow(['Tinten-Kosten (EUR)', f"{data['tinte']['kosten']:.2f}"])
                w.writerow(['Zusatz Keilrahmen (EUR)', f"{data['zusatz']['keilrahmen']:.2f}"])
                w.writerow(['Zusatz Firnis (EUR)', f"{data['zusatz']['firnis']:.2f}"])
                w.writerow(['Arbeitszeit (EUR)', f"{data['zusatz']['arbeit']:.2f}"])
                w.writerow(['Gesamtpreis (EUR)', f"{data['gesamt']:.2f}"])
            messagebox.showinfo('Export', f'Erfolgreich gespeichert: {fpath}')
        except Exception as e:
            messagebox.showerror('Fehler', f'Fehler beim Export: {e}')


if __name__ == '__main__':
    root = tk.Tk()
    app = PlotterKostenGUI(root)
    root.mainloop()
