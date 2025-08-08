#!/usr/bin/env python
# coding: utf-8

# In[1]:


import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np

class PlateReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Elaboratore dati Plate Reader")
        self.file_path = None
        self.df_raw = None
        self.triplicati = {}  # { gruppo: [lista_pozzetti] }
        self.buttons_pozzetti = {}

        self.setup_ui()

    def setup_ui(self):
        # Selezione file
        frame_file = tk.Frame(self.root)
        frame_file.pack(pady=5)
        tk.Label(frame_file, text="File dati Excel: ").pack(side=tk.LEFT)
        self.entry_file = tk.Entry(frame_file, width=50)
        self.entry_file.pack(side=tk.LEFT, padx=5)
        tk.Button(frame_file, text="Sfoglia", command=self.scegli_file).pack(side=tk.LEFT)

        # Griglia plate reader (8 righe x 12 colonne)
        frame_plate = tk.Frame(self.root)
        frame_plate.pack(pady=10)
        righe = "ABCDEFGH"
        colonne = range(1, 13)
        for r in righe:
            row_frame = tk.Frame(frame_plate)
            row_frame.pack()
            for c in colonne:
                nome_pozzetto = f"{r}{c}"
                btn = tk.Button(row_frame, text=nome_pozzetto, width=4,
                                command=lambda n=nome_pozzetto: self.seleziona_triplicato(n))
                btn.pack(side=tk.LEFT, padx=1, pady=1)
                self.buttons_pozzetti[nome_pozzetto] = btn

        # Nome gruppo
        frame_gruppo = tk.Frame(self.root)
        frame_gruppo.pack(pady=5)
        tk.Label(frame_gruppo, text="Nome gruppo triplicati: ").pack(side=tk.LEFT)
        self.entry_nome_gruppo = tk.Entry(frame_gruppo, width=30)
        self.entry_nome_gruppo.pack(side=tk.LEFT, padx=5)

        # Pulsante elaborazione
        tk.Button(self.root, text="Avvia elaborazione", command=self.avvia_elaborazione, bg="lightblue").pack(pady=10)

        # Stato
        self.label_status = tk.Label(self.root, text="", fg="green")
        self.label_status.pack()

    def scegli_file(self):
        self.file_path = filedialog.askopenfilename(
            title="Seleziona file Excel Plate Reader",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        self.entry_file.delete(0, tk.END)
        self.entry_file.insert(0, self.file_path)
        self.carica_dati()

    def carica_dati(self):
        try:
            # Carico con header a riga 24 (index 23)
            self.df_raw = pd.read_excel(self.file_path, header=23)
            self.label_status.config(text="Dati caricati correttamente.")
        except Exception as e:
            messagebox.showerror("Errore caricamento", f"Errore caricamento file:\n{e}")
            self.label_status.config(text="")

    def seleziona_triplicato(self, nome_pozzetto):
        nome_gruppo = self.entry_nome_gruppo.get().strip()
        if not nome_gruppo:
            messagebox.showwarning("Input mancante", "Inserisci prima il nome del gruppo triplicati.")
            return

        if nome_gruppo not in self.triplicati:
            self.triplicati[nome_gruppo] = []

        if nome_pozzetto in self.triplicati[nome_gruppo]:
            self.triplicati[nome_gruppo].remove(nome_pozzetto)
            self.buttons_pozzetti[nome_pozzetto].config(bg="SystemButtonFace")
        else:
            if len(self.triplicati[nome_gruppo]) >= 3:
                messagebox.showwarning("Limite triplicati", "Ogni gruppo può avere solo 3 triplicati.")
                return
            self.triplicati[nome_gruppo].append(nome_pozzetto)
            self.buttons_pozzetti[nome_pozzetto].config(bg="lightgreen")

        self.label_status.config(text=f"Gruppo {nome_gruppo}: {self.triplicati[nome_gruppo]}")

    def avvia_elaborazione(self):
        if self.df_raw is None:
            messagebox.showerror("Errore", "Carica prima un file dati.")
            return

        if not self.triplicati:
            messagebox.showerror("Errore", "Seleziona almeno un gruppo di triplicati.")
            return

        # Verifica che ogni gruppo abbia esattamente 3 pozzetti
        for g, pozzetti in self.triplicati.items():
            if len(pozzetti) != 3:
                messagebox.showerror("Errore", f"Il gruppo '{g}' deve avere esattamente 3 pozzetti, ne hai selezionati {len(pozzetti)}.")
                return

        # Rinominazione prima colonna a Wavelength se non presente
        if "Wavelength" not in self.df_raw.columns:
            self.df_raw.rename(columns={self.df_raw.columns[0]: "Wavelength"}, inplace=True)

        # Conversione Wavelength a numerico e filtraggio 300-800 nm
        self.df_raw["Wavelength"] = pd.to_numeric(self.df_raw["Wavelength"], errors='coerce')
        df_filtrato = self.df_raw[(self.df_raw["Wavelength"] >= 300) & (self.df_raw["Wavelength"] <= 800)].copy()

        # Creazione writer Excel unico per TUTTI i dati
        output_file = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                   filetypes=[("Excel files", "*.xlsx *.xls")],
                                                   title="Salva file Excel di output")
        if not output_file:
            return

        with pd.ExcelWriter(output_file) as writer:
            # Creo dataframe riepilogo media triplicati per ogni gruppo (Wavelength + 3 colonne pozzetti + 1 media)
            riepilogo_media = pd.DataFrame()
            riepilogo_media["Wavelength"] = df_filtrato["Wavelength"]

            for gruppo, pozzetti in self.triplicati.items():
                df_trip = pd.DataFrame()
                df_trip["Wavelength"] = df_filtrato["Wavelength"]

                # Controllo colonne esistenti
                colonne_presenti = [p for p in pozzetti if p in df_filtrato.columns]
                if len(colonne_presenti) != 3:
                    messagebox.showwarning("Attenzione",
                        f"Per il gruppo '{gruppo}' non sono presenti tutte le 3 colonne selezionate. Colonne trovate: {colonne_presenti}")

                # Prendo dati triplicati, convertendo a numerico
                dati_trip = df_filtrato[colonne_presenti].apply(pd.to_numeric, errors='coerce')

                # Trovo indice riga Wavelength più vicino a 800 nm per baseline
                idx_800 = (df_trip.index[(df_filtrato["Wavelength"] - 800).abs().argsort()])[0]

                # Sottraggo valore a 800 nm per baseline da ciascuna colonna
                baseline = dati_trip.iloc[idx_800]
                dati_corr = dati_trip.subtract(baseline, axis=1)

                # Media colonne raw e corrette
                media_raw = dati_trip.mean(axis=1)
                media_corr = dati_corr.mean(axis=1)

                # Preparo dataframe per foglio dati grezzi
                df_raw_singolo = pd.concat([df_trip["Wavelength"], dati_trip], axis=1)
                # Preparo dataframe per foglio dati corretti
                df_corr_singolo = pd.concat([df_trip["Wavelength"], dati_corr], axis=1)
                # Preparo dataframe per foglio medie
                df_media_singolo = pd.DataFrame({
                    "Wavelength": df_trip["Wavelength"],
                    "Mean_Raw": media_raw,
                    "Mean_Corrected": media_corr
                })

                # Scrivo 3 fogli per ogni gruppo nello stesso file Excel
                df_raw_singolo.to_excel(writer, sheet_name=f"{gruppo}_Raw", index=False)
                df_corr_singolo.to_excel(writer, sheet_name=f"{gruppo}_Corrected", index=False)
                df_media_singolo.to_excel(writer, sheet_name=f"{gruppo}_Media", index=False)

                # Aggiungo la media corretta al riepilogo (una colonna per gruppo)
                riepilogo_media[gruppo] = media_corr

            # Scrivo il riepilogo finale con medie corrette di tutti i gruppi
            riepilogo_media.to_excel(writer, sheet_name="Riepilogo_Media", index=False)

        messagebox.showinfo("Completato", f"Elaborazione completata.\nFile salvato:\n{output_file}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PlateReaderApp(root)
    root.mainloop()


# In[ ]:




