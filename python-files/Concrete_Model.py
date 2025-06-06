#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  3 10:11:14 2025

@author: eduardoallen
"""
import numpy as np
import matplotlib.pyplot as plt
import os
import tkinter as tk
from tkinter import messagebox
import pandas as pd
from tkinter import simpledialog, messagebox

class MultiInputDialog(simpledialog.Dialog):
    def __init__(self, parent, title, labels):
        self.labels = labels
        self.entries = []
        super().__init__(parent, title)

    def body(self, master):
        for i, label_text in enumerate(self.labels):
            tk.Label(master, text=label_text).grid(row=i, column=0, padx=10, pady=5)
            entry = tk.Entry(master)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries.append(entry)
        return self.entries[0] if self.entries else None

    def apply(self):
        values = []
        try:
            for entry in self.entries:
                val = float(entry.get())
                values.append(val)
            self.result = tuple(values)
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter valid numbers. Run it Again")
            self.result = None

def get_multiple_inputs(labels):
    root = tk.Tk()
    root.withdraw()
    dialog = MultiInputDialog(root, "Concrete Deterioration Model HDM-5", labels)
    return dialog.result if dialog.result else None

# Usage example with 5 inputs
labels = ['NE4 (Million ESAL)','Cd (Drainage Coefficient)','Hp (mm)','L (m)','BASE (1 if stabilised, 0 otherwise)','FI (Celcius-days)','MMP (mm/month)','DAYS32 (days)','WIDENED (0 if not widened/no tied. 1 otherwise)', 'AGE3 (Age from construction)', 'LTE (0 if dowels in good condition, 1 otherwise)','SEAL (Sealant in joint, 1 if present)','REINF (1 if reinforzed, 1.2 otherwise)','MI (Thornthwaite moisture index)']
values = get_multiple_inputs(labels)


# IT COULD BE JPCP, JRCP OR CRCP

def ask_for_string():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    user_input = simpledialog.askstring("Concrete Model HDM-5", "Enter the Pavement Type (JPCP, JRCP, CRCP):")

    if user_input is not None:
        print(f"You entered: {user_input}")
        return user_input
    else:
        print("User cancelled.")
        return None

# Example usage
if __name__ == "__main__":
    result = ask_for_string()

TYPE = result
dowels = False

# (1) FOR FAULTING

# Variable Definition

# With Dowels:
# NE4 = 1
# C_d = 1
# H_p = 250
# L = 6
# BASE = 0
# FI = 100
# MMP = 100
# DAYS32 = 100
# WIDENED = 0

NE4 = values[0]
C_d = values[1]
H_p = values[2]
L = values[3]
BASE = values[4]
FI = values[5]
MMP = values[6]
DAYS32 = values[7]
WIDENED = values[8]
Initial_Fault = 0
years_of_analysis = 20

# Without Dowels 

AGE3 = values[9]

# Calculation
FAULT = np.zeros(years_of_analysis + 1)
FAULT[0] = Initial_Fault

if dowels:
    for i in range(years_of_analysis):
        FAULT[i+1] = (25.4*(NE4*(i+1))**0.25 * max(0, 0.0628*(1 - C_d)+1.74*10**(-2)+ 4.431*10**(-5)*(L**2) + 5.13*10**(-10)*(FI**2)*(MMP**0.5)- 0.009503*BASE- 0.01917*(WIDENED) + 0.0009217*AGE3))    
else: 
    for i in range(years_of_analysis):
        FAULT[i+1] = (25.4*(NE4*(i+1))**0.25 * max(0, 0.2347-0.1516*C_d-2.88*10**(-7)*((H_p**2)/(L**0.25))-0.0115*BASE + 6.45 *(10**(-8))* (FI**1.5) * (MMP**0.25)-0.002478 * (DAYS32**0.5)- 0.0415 * WIDENED))



def get_base_path():
    try:
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        return os.getcwd()

# Plot
plt.figure
plt.plot(np.arange(0, years_of_analysis+1),FAULT)
plt.xlabel('Pavement Age (years)')
plt.ylabel('Faulting (mm)')
plt.savefig(os.path.join(get_base_path(), 'Concrete Faulting.pdf'), bbox_inches= 'tight', pad_inches = 0)
plt.show()
plt.close()

# (2) For Transverse Joint Spalling

# Variable Definition

LTE = values[10]
SEAL= values[11]

Initial_SPALL = 0

SPALL = np.zeros(years_of_analysis + 1)
SPALL[0] = Initial_SPALL

if TYPE == 'JPCP':
    for i in range(years_of_analysis):
        SPALL[i+1] = 3.281*(10**(-6))*((AGE3+1+i)**2)*L*(549.9 - 895.7*SEAL + 1.11*(10**(-3))*(DAYS32**3) + 375 *LTE + FI *(36 - 49.5 * SEAL))

elif TYPE == 'JRCP':
    for i in range(years_of_analysis):
        SPALL[i+1] = 3.281*(10**(-5)) * ((AGE3+i+1)**3) * L * (1.94*LTE+8.819*BASE * (1-SEAL) + 0.0128*FI)
else:
    print('NO SPALLING MODEL FOR CRCP')

# Plot 
plt.figure
plt.plot(np.arange(0, years_of_analysis+1),SPALL)
plt.xlabel('Pavement Age (years)')
plt.ylabel('Percentage of spalled joints (%)')
plt.savefig(os.path.join(get_base_path(), 'Concrete Spalling Model.pdf'), bbox_inches= 'tight', pad_inches = 0)
plt.show()
plt.close()

# (3) TRANSVERSE CRACKING

REINF = values[12]
MI = values[13]
Initial_NCRACKS = 0

NCRACKS = np.zeros(years_of_analysis + 1)
NCRACKS[0] = Initial_NCRACKS
for i in range(years_of_analysis):
    NCRACKS[i+1] = 0.62 * REINF * (AGE3+i+1)**2.5 * (1.24 *(10**(- 5))* FI + (NE4*(i+1)) *(0.116 - 0.073 * BASE)* (1-np.exp(-0.032*MI)*0.2023) )

# Plot 
plt.figure
plt.plot(np.arange(0, years_of_analysis+1),NCRACKS)
plt.xlabel('Pavement Age (years)')
plt.ylabel('Number of medium/severe cracks per kilometre')
plt.savefig(os.path.join(get_base_path(), 'Cracking Model.pdf'), bbox_inches= 'tight', pad_inches = 0)
plt.show()
plt.close()

# (4) ROUGHNESS

Initial_IRI = 3.5

IRI = np.zeros(years_of_analysis + 1)
IRI[0] = Initial_IRI

if TYPE == 'JPCP':
    for i in range(years_of_analysis):
        IRI[i+1] = IRI[0] + 0.00265 * FAULT[i+1] + 0.0291 *SPALL[i+1] + 0.15 * (10**(-6)) * (NCRACKS[i+1]**3)
elif TYPE == 'JRCP':
    for i in range(years_of_analysis):
        IRI[i+1] = -3.67 * np.log(0.2*(4.165 - 0.0169*(FAULT[i+1]**0.5) - 0.1447*(SPALL[i+1]**0.25) - 8.367 * (10**(-5))*(NCRACKS[i+1]**2) ))
elif TYPE == 'CRCP':
    for i in range(years_of_analysis):
        IRI[i+1] = -3.67 * np.log(0.2*(4.5430 * AGE3**(0.1849) * NE4**(0.2634) * H_p **(-1.3121)))

# Plot 
plt.figure
plt.plot(np.arange(0, years_of_analysis+1),IRI)
plt.xlabel('Pavement Age (years)')
plt.ylabel('Roughness m/km')
plt.savefig(os.path.join(get_base_path(), 'Roughnness Model.pdf'), bbox_inches= 'tight', pad_inches = 0)
plt.show()
plt.close()



years = np.arange(0, years_of_analysis + 1)

# === STEP 3: Your actual data arrays (same length as years) ===
# These must be defined in your script before this block runs
# FAULT = np.array([...])
# SPALL = np.array([...])
# NCRACKS = np.array([...])
# IRI = np.array([...])

# === STEP 4: Create DataFrame and save ===
df = pd.DataFrame({
    'Year': years,
    'Faulting (mm)': FAULT,
    'Spalling (%)': SPALL,
    'Cracking (%)': NCRACKS,
    'IRI (m/km)': IRI
})

output_path = os.path.join(get_base_path(), 'Concrete_Model_Results.xlsx')
df.to_excel(output_path, index=False)