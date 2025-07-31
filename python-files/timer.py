# -*- coding: utf-8 -*-
"""
Created on Tue Apr 29 15:09:36 2025

@author: DELAURAL
"""

import tkinter as tk
import time

class Cronometro:
    def __init__(self, root):
        self.root = root
        self.root.title("Cronometro")
        
        self.tempo_iniziale = 0
        self.tempo_corrente = 0
        self.in_esecuzione = False
        
        self.label = tk.Label(root, text="00:00:00", font=("Arial", 30))
        self.label.pack()

        self.start_button = tk.Button(root, text="Avvia", command=self.avvia)
        self.start_button.pack(side="left")

        self.pause_button = tk.Button(root, text="Pausa", command=self.pausa)
        self.pause_button.pack(side="left")

        self.stop_button = tk.Button(root, text="Stop", command=self.ferma)
        self.stop_button.pack(side="left")
        
        self.aggiorna_tempo()

    def aggiorna_tempo(self):
        if self.in_esecuzione:
            self.tempo_corrente = time.time() - self.tempo_iniziale
            ore = int(self.tempo_corrente // 3600)
            minuti = int((self.tempo_corrente % 3600) // 60)
            secondi = int(self.tempo_corrente % 60)
            self.label.config(text=f"{ore:02}:{minuti:02}:{secondi:02}")
        self.root.after(1000, self.aggiorna_tempo)

    def avvia(self):
        if not self.in_esecuzione:
            self.tempo_iniziale = time.time() - self.tempo_corrente
            self.in_esecuzione = True

    def pausa(self):
        if self.in_esecuzione:
            self.in_esecuzione = False

    def ferma(self):
        self.in_esecuzione = False
        self.tempo_corrente = 0
        self.label.config(text="00:00:00")

root = tk.Tk()
app = Cronometro(root)
root.mainloop()
