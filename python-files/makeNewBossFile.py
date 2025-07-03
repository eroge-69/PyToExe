import tkinter as tk
import ctypes
import os

win = tk.Tk()
win.title("Make New Boss File")
win.geometry("320x400")


def createFile(name, ability, rage, desc):
    print("no")
    if name != '':
        try:
            open(f'Boss\kasd\description')
            ctypes.windll.user32.MessageBoxW(0, "This File Already Exists", "File Duplicat", 1)
        except:
            os.makedirs(f'Boss\{name}')
            newFile = open(f'Boss\{name}\description.txt', "x")
            newFile.write(f'{name}\n\nAbility: {ability}\nRage: {rage}\n\nOpis: \n  {desc}')

# NAME
labelBossName = tk.Label(text="Boss Name: ").grid(row=1, column=1)
nameInput = tk.Entry(width=30); nameInput.grid(row=1, column=2)


# ABILITY
labelBossAbility = tk.Label(text="Ability: ").grid(row=2, column=1)
abilityInput = tk.Entry(width=30); abilityInput.grid(row=2, column=2)

# RAGE
labelBossRage = tk.Label(text="Rage: ").grid(row=3, column=1)
rageInput = tk.Entry(width=30); rageInput.grid(row=3, column=2)


# DESCRIPTION
labelBossDesc = tk.Label(text="Opis: ").grid(row=4, column=1)
descInput = tk.Text(width=22, height=15); descInput.grid(row=4, column=2)


# SUMBIT
makeFileButton = tk.Button(text="Create File", command=lambda: createFile(name=nameInput.get(), ability=abilityInput.get(), rage=rageInput.get(), desc=descInput.get("1.0", "end-1c")))
makeFileButton.grid(row=5, column=2)



win.mainloop()

    
