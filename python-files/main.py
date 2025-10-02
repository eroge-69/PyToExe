####################################################
#########  STAMPI REALIZZABILE DA PROGRA  ##########
### version 1.0     01/10/2025 			         ###
### author Marco Prosperi 			             ###
### copyright SACMI Imola S.C., Imola		     ###
####################################################

import pandas as pd
import numpy as np
import os
from openpyxl import load_workbook
#import xlwings as xw
from helpFunctions import *

### Carico il file Excel del CONFIGURATORE ed estraggo i codici delle varie parti dello stampo 
parent_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))
file_path = os.path.join(parent_dir, "CONFIGURATORE STAMPO-POST COOLING.xlsm")

# Estrapolo codici core plate
sheet_name = "CORE"        # Nome del foglio da cui estrarre i dati
df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
# core = df.iloc[1:, [0,2,3,4,5,12]].to_numpy()   # 0 = A, 1 = B, 2 = C...)
df = df.iloc[1:, [0,2,3,4,5,11]]  # CODICE-CAVITA'-PASSO-PRESSA-VERSIONE-PROD.ATTUALE
# filtro le righe mantenendo solo quelle che contengono "Produz. attuale" nell'ultima colonna
df = df[df.iloc[:, 5].astype(str).str.contains("Produz. attuale", na=False)]
core = df.to_numpy()

# Estrapolo codici stripper plate
sheet_name = "STRIPPER"        # Nome del foglio da cui estrarre i dati
df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
stripper = df.iloc[1:, [0,3,4,5,6]].to_numpy()   # 0 = A, 1 = B, 2 = C...)

# Estrapolo codici hot runner
sheet_name = "HR"        # Nome del foglio da cui estrarre i dati
df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
hr = df.iloc[1:, [0,1,2,3,4]].to_numpy()   # 0 = A, 1 = B, 2 = C...)

# Estrapolo codici take out plate
sheet_name = "TOP"        # Nome del foglio da cui estrarre i dati
df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
top = df.iloc[1:, [0,1,2,3,4,5]].to_numpy()   # 0 = A, 1 = B, 2 = C...)

# Estrapolo codici cool plus plate
sheet_name = "COOL"        # Nome del foglio da cui estrarre i dati
df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
cp = df.iloc[1:, [0,1,2,3,4,5]].to_numpy()   # 0 = A, 1 = B, 2 = C...)

# Estrapolo codici gripper plate
sheet_name = "GP"        # Nome del foglio da cui estrarre i dati
df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
gp = df.iloc[1:, [0,2,3,4,5]].to_numpy()   # 0 = A, 1 = B, 2 = C...)

### Carico il file Excel della PROGRA da cui ricavo i vari codici di piastre presenti a magazzino
file_path = "./analisiprogra.xlsx"     
sheet_name = "analisiprogra"                

# Leggo il foglio, escludendo la prima sei righe (header=None per non interpretare intestazioni)
df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
progra = df.iloc[6:, [7,8,21]]   # 0 = A, 1 = B, 2 = C...)

# Rimuovo le righe vuote (se tutte e tre le colonne sono NaN)
progra = progra.dropna(how='all')

# Rimuovo le righe dove la **seconda colonna selezionata** NON è vuota, escludo quindi quelle che hanno già un ODV abbinato
progra = progra[progra.iloc[:, 1].isna()]

# Rimuovo le righe dove la **terza colonna selezionata** NON contiene un certo valore da escludere
valore_da_escludere = "Materiale"
progra = progra[progra.iloc[:, 2] != valore_da_escludere]


# Rimuovo la seconda colonna perchè ho già rimosso le righe abbinate agli ODV
progra = progra.drop(progra.columns[1], axis=1)
progra = progra.to_numpy()

#print(codici)
#print(progra)

### Apro file Excel della PROGRA
file_path = "./PROGRA.xlsx"

# Leggo solo le prime 5 colonne, saltando la prima riga (skiprows=1), elimino le righe vuote, converto in un array e ricavo le sue dimensioni
df = pd.read_excel(file_path, usecols=[0, 1, 2, 3, 4], header=None, skiprows=1)
df = df.dropna(how='all')
matrix = df.to_numpy()
a,b = matrix.shape

# Apri il file Excel con openpyxl per poterci poi scrivere e cancello la lista dei codici estitenti
wb = load_workbook(file_path)
ws = wb['Foglio1']
# 
for r in range(2, 2+a):      # righe da 2 a 2+a
    for c in range(6, 18):   # colonne da 6 (F) a 18 (Q)
        ws.cell(row=r, column=c).value=None

for i in range(a):
    mach = matrix[i,0]
    vers = matrix[i,1]
    cav = matrix[i,2]
    pitch = matrix[i,3]
    stage = matrix[i,4]
    #print(mach,vers,cav, pitch)
      
    # cerco le take out plate compatibili con la macchina che si sta analizzando
    progra_stripper = clean_progra_stripper(progra)
    search(stripper, mach, vers, cav, pitch, 0, progra_stripper, ws, i, "str")
    search(stripper, mach, vers, cav, pitch, 0, progra, ws, i, "core", core)
    search(hr, mach, vers, cav, pitch, 0, progra, ws, i, "hr")
    search(top, mach, vers, cav, pitch, stage, progra, ws, i, "top")
    search(cp, mach, vers, cav, pitch, stage, progra, ws, i, "cp")
    search(gp, mach, vers, cav, pitch, 0, progra, ws, i, "gp")

# autofit altezza righe
# wb = xw.Book("PROGRA.xlsx")
# sheet = wb.sheets["Foglio1"]
# #sheet.autofit("c")  # auto-adatta le colonne
# sheet.autofit("r")  # auto-adatta le righe
# wb.save()
# wb.close()