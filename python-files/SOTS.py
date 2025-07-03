import tkinter as tk
from tkinter import ttk
import random

def roll_dice(n):
    return sum(random.randint(1, 6) for _ in range(n))

def calculate():
    try:
        # Get values from inputs
        dist = int(dist_entry.get())
        DES1 = int(des1_entry.get())
        AGL1 = int(agl1_entry.get())
        EVA1 = int(eva1_entry.get())
        FUE1 = int(fue1_entry.get())
        DES2 = int(des2_entry.get())
        AGL2 = int(agl2_entry.get())
        EVA2 = int(eva2_entry.get())
        FUE2 = int(fue2_entry.get())

        BackStab = backstab_var.get()
        grounded1 = grounded1_var.get()
        grounded2 = grounded2_var.get()
        defend = defend_var.get()
        roll = roll_var.get()
        parry = parry_var.get()
        ParrySafe = parrysafe_var.get()

        counter = False
        result = 0
        ground = False

        if grounded1:
            EVA1 = 0
        if grounded2 or BackStab:
            EVA2 = 0
        ParryMod = 0.5 if ParrySafe else 0

        rollAtk = roll_dice(DES1) - dist

        if defend:
            rollDef = roll_dice(DES2)
            result = rollAtk - rollDef
            if result == 0 and dist == 0:
                rollAtk = roll_dice(FUE1)
                rollDef = roll_dice(FUE2)
                result = rollAtk - rollDef
                ground = True
                counter = False
            elif result > 0:
                result -= EVA2
                counter = result < 0
            else:
                counter = False

        elif roll:
            rollDef = roll_dice(AGL2)
            result = rollAtk - rollDef
            if result == 0:
                result = -1  # defender bonus

        elif parry:
            rollDef = roll_dice(DES2)
            if rollAtk > rollDef:
                result = rollAtk - int(rollDef * ParryMod)
            elif rollAtk == rollDef:
                rollAtk = roll_dice(FUE1)
                rollDef = roll_dice(FUE2)
                result = rollAtk - rollDef
                ground = True
                counter = False
            else:
                result = rollAtk - rollDef

        if result < 0 and defend and counter:
            result += EVA1
            if result < 0:
                counter = True
            else:
                result = 0
                counter = False

        # Output results
        result_var.set(str(result))
        grounded_var.set("Yes" if ground else "No")
        counter_var.set("Yes" if counter else "No")

    except Exception as e:
        result_var.set(f"Error: {e}")
        grounded_var.set("")
        counter_var.set("")

# GUI setup
root = tk.Tk()
root.title("Sons of the Sky - Combat Resolver")

mainframe = ttk.Frame(root, padding="10")
mainframe.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

def add_entry(label, row):
    ttk.Label(mainframe, text=label).grid(column=0, row=row)
    entry = ttk.Entry(mainframe, width=5)
    entry.grid(column=1, row=row)
    return entry

# Inputs
dist_entry = add_entry("Distancia", 0)
des1_entry = add_entry("DES Atacante", 1)
agl1_entry = add_entry("AGL Atacante", 2)
eva1_entry = add_entry("EVA Atacante", 3)
fue1_entry = add_entry("FUE Atacante", 4)
des2_entry = add_entry("DES Defensor", 5)
agl2_entry = add_entry("AGL Defensor", 6)
eva2_entry = add_entry("EVA Defensor", 7)
fue2_entry = add_entry("FUE Defensor", 8)

# Checkboxes
backstab_var = tk.BooleanVar()
grounded1_var = tk.BooleanVar()
grounded2_var = tk.BooleanVar()
defend_var = tk.BooleanVar()
roll_var = tk.BooleanVar()
parry_var = tk.BooleanVar()
parrysafe_var = tk.BooleanVar()

ttk.Checkbutton(mainframe, text="BackStab", variable=backstab_var).grid(column=2, row=0)
ttk.Checkbutton(mainframe, text="Grounded Atacante", variable=grounded1_var).grid(column=2, row=1)
ttk.Checkbutton(mainframe, text="Grounded Defensor", variable=grounded2_var).grid(column=2, row=2)
ttk.Checkbutton(mainframe, text="Defender", variable=defend_var).grid(column=2, row=3)
ttk.Checkbutton(mainframe, text="Roll", variable=roll_var).grid(column=2, row=4)
ttk.Checkbutton(mainframe, text="Parry", variable=parry_var).grid(column=2, row=5)
ttk.Checkbutton(mainframe, text="Parry Seguro", variable=parrysafe_var).grid(column=2, row=6)

# Results
ttk.Label(mainframe, text="Resultado:").grid(column=0, row=10)
result_var = tk.StringVar()
ttk.Label(mainframe, textvariable=result_var).grid(column=1, row=10)

ttk.Label(mainframe, text="Derribado:").grid(column=0, row=11)
grounded_var = tk.StringVar()
ttk.Label(mainframe, textvariable=grounded_var).grid(column=1, row=11)

ttk.Label(mainframe, text="Contraataque:").grid(column=0, row=12)
counter_var = tk.StringVar()
ttk.Label(mainframe, textvariable=counter_var).grid(column=1, row=12)

ttk.Button(mainframe, text="Calcular", command=calculate).grid(column=1, row=13)

root.mainloop()
