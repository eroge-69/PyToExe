
import tkinter as tk
from tkinter import ttk
import pandas as pd


def piano_di_ammortamento_rata_costante(importo, tasso_interesse, durata, int_scad_mora_oneri_spese):
    rata = round((1 + 1 / ((1 + tasso_interesse) ** durata - 1)) * (tasso_interesse) * importo, 3)
    rata1 = round((1 + 1 / ((1 + tasso_interesse) ** durata - 1)) * (tasso_interesse) * importo, 3) + (int_scad_mora_oneri_spese / durata)
    E = 0
    tot_I = 0
    R = importo
    piano_di_ammortamento = []
    

    piano_di_ammortamento.append({
        'Periodo': 0,
        'Rata Totale': 0,        
        'Rata': 0,
        'Quota Capitale': 0,
        'Quota Interessi': 0,
        'Int scad mora oneri spese': 0,
        'Totale interessi': 0,
        'Debito Estinto': 0,
        'Debito Residuo': round(importo, 2)
    })
    
    for periodo in range(1, durata + 1):
        I = R * tasso_interesse
        C = rata - I
        E += C
        tot_I += I
        R = importo - E
        piano_di_ammortamento.append({
            'Periodo': periodo,
            'Rata Totale': round(rata + (int_scad_mora_oneri_spese / durata), 2),
            'Rata': round(C+I, 2),
            'Quota Capitale': round(C, 2),
            'Quota Interessi': round(I, 2),
            'Int scad mora oneri spese': round(int_scad_mora_oneri_spese / durata, 2),
            'Totale interessi': round(tot_I, 2),
            'Debito Estinto': round(E, 2),
            'Debito Residuo': round(R, 2)
        })
    
    return pd.DataFrame(piano_di_ammortamento)

def calcola_ammortamento():
    importo = float(entry_importo.get())
    tasso_interesse = float(entry_tasso_interesse.get()) / 100 / 12
    durata = int(entry_durata.get())
    int_scad_mora_oneri_spese = float(entry_int_scad_mora_oneri_spese.get())
    piano_di_ammortamento = piano_di_ammortamento_rata_costante(importo, tasso_interesse, durata, int_scad_mora_oneri_spese)
    
    for item in tree.get_children():
        tree.delete(item)
    
    for _, row in piano_di_ammortamento.iterrows():
        tree.insert("", "end", values=(row['Periodo'], row['Rata Totale'], row['Rata'], row['Quota Capitale'], row['Quota Interessi'], row['Int scad Mora Oneri Spese'], row['Totale interessi'], row['Debito Estinto'], row['Debito Residuo']))

def copia_ammortamento():
    importo = float(entry_importo.get())
    tasso_interesse = float(entry_tasso_interesse.get()) / 100 / 12
    durata = int(entry_durata.get())
    int_scad_mora_oneri_spese = float(entry_int_scad_mora_oneri_spese.get())
    
    piano_di_ammortamento = piano_di_ammortamento_rata_costante(importo, tasso_interesse, durata, int_scad_mora_oneri_spese)
    
    root.clipboard_clear()


    clipboard_data = piano_di_ammortamento.to_csv(sep='\t', index=False, decimal=',')
    root.clipboard_append(clipboard_data)
    root.update()

root = tk.Tk()
root.title("Simulatore Ammortamento")

root.geometry("1200x800")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

ttk.Label(frame, text="Importo:").grid(row=0, column=0, sticky=tk.W)
entry_importo = ttk.Entry(frame)
entry_importo.grid(row=0, column=1, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Tasso di Interesse (%):").grid(row=1, column=0, sticky=tk.W)
entry_tasso_interesse = ttk.Entry(frame)
entry_tasso_interesse.grid(row=1, column=1, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Durata (mesi):").grid(row=2, column=0, sticky=tk.W)
entry_durata = ttk.Entry(frame)
entry_durata.grid(row=2, column=1, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Int scad Mora Oneri Spese:").grid(row=3, column=0, sticky=tk.W)
entry_int_scad_mora_oneri_spese = ttk.Entry(frame)
entry_int_scad_mora_oneri_spese.grid(row=3, column=1, sticky=(tk.W, tk.E))

ttk.Button(frame, text="Calcola", command=calcola_ammortamento).grid(row=4, column=0)
ttk.Button(frame, text="Copia", command=copia_ammortamento).grid(row=4, column=2)

columns = ("Periodo", "Rata Totale", "Rata", "Quota Capitale", "Quota Interessi", "Int scad Mora Oneri Spese", "Totale interessi", "Debito Estinto", "Debito Residuo")
tree = ttk.Treeview(root, columns=columns, show="headings")
tree.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))

tree.column("Periodo", width=130)
tree.column("Rata Totale", width=130)
tree.column("Rata", width=130)
tree.column("Quota Capitale", width=130)
tree.column("Quota Interessi", width=130)
tree.column("Totale interessi", width=130)
tree.column("Int scad Mora Oneri Spese", width=130)
tree.column("Debito Estinto", width=130)
tree.column("Debito Residuo", width=130)

for col in columns:
    tree.heading(col, text=col)

scrollbar_verticale = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
scrollbar_verticale.grid(row=5, column=3, sticky=(tk.N, tk.S))
tree.configure(yscrollcommand=scrollbar_verticale.set)

tree["height"] =30


root.mainloop()
