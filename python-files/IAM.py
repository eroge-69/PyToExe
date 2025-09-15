from tkinter import *
from tkinter import ttk, messagebox

root = Tk()
frm = ttk.Frame(root, padding=10)
frm.grid()
root.title("IAM Calculator")
month = 30

def trad():   
    try:
        tw = wordtrad.get()
        result = int(tw) / int(month)
        result = result / 24
        messagebox.showinfo("Result", f"{result:.2f}")
    except Exception as e:
        messagebox.showerror("Erreur", f"{e}")

def small():
    global month
    month = 30
    messagebox.showinfo("Mois choisi", "Mois de 30 jours sélectionné")

def big():
    global month
    month = 31
    messagebox.showinfo("Mois choisi", "Mois de 31 jours sélectionné")
def fev():
    global month
    month = 28
    messagebox.showinfo("Mois choisi", "Mois de 28 jours sélectionné")

ttk.Label(frm, text="IAM Calculator by Enket").grid(column=0, row=0)

ttk.Button(frm, text="Quitter", command=root.destroy).grid(column=1, row=1)

wordtrad = StringVar()
e1 = ttk.Entry(frm, textvariable=wordtrad)
e1.grid(row=1)

ttk.Button(frm, text="Calculer", command=trad).grid(row=3)
ttk.Label(frm, text="Choix du mois").grid(row=4)
ttk.Button(frm, text="31 jours", command=big).grid(row=5)
ttk.Button(frm, text="30 jours", command=small).grid(row=6)
ttk.Button(frm, text="28 jours", command=fev).grid(row=7)

root.mainloop()
