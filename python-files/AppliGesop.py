#!/usr/bin/env python
# coding: utf-8

# In[2802]:


# ports = serial.tools.list_ports.comports()

# for port, desc, hwid in sorted(ports):
#         print("{}: {} [{}]".format(port, desc, hwid))

# import serial.tools.list_ports

# ports = serial.tools.list_ports.comports()

# listPorts = []
# for port, desc, hwid in sorted(ports):
#     # print("{}: {} [{}]".format(port, desc, hwid))
#     listPorts.append(port)
# print(listPorts)


# In[2803]:


# ser = serial.Serial("COM3", baudrate=115200)
# i = 0
# while (i < 2):
#     line = str(ser.readline())
#     line = line[2:][:-5]
#     print(line)
#     i += 1
# ser.close()


# In[2804]:


# importation des librairies
import tkinter as tk
from tkinter import ttk
import serial.tools.list_ports


# In[ ]:





# In[2805]:


fenetre = tk.Tk() # instance fenetre principale
fenetre.geometry("1280x780")
fenetre.title('Application GESOP')


# In[2806]:


notebook = ttk.Notebook(fenetre) # widget notebook
notebook.pack(expand=True, fill='both')


# In[2807]:


# Frame pour chaque onglet
frame1 = ttk.Frame(notebook)
frame2 = ttk.Frame(notebook)
frame3 = ttk.Frame(notebook)
frame4 = ttk.Frame(notebook)

# Ajout des frames en tant que pages de l'onglet
notebook.add(frame1, text="CEGI+")
notebook.add(frame2, text="CEGI2")
notebook.add(frame3, text="Configuration")
notebook.add(frame4, text="A propos")


# ## Onglet CEGI+

# ##### Informations Systèmes

# In[2808]:


# Ajout contenu dans la frame1
# label1 = ttk.Label(frame1, text="Saisie Données Usine CEGI+")
# label1.config(font=("Arial", 16))
# label1.pack()

x_entry = 250
width_entry = 25
width_lb = 750

# Informations Systèmes
labelframe1 = tk.LabelFrame(frame1,text="Informations Systèmes", font=("Arial", 12, "bold"), relief='groove')
labelframe1.place(x=20, y=30, width=width_lb, height=200)



lb_NS = ttk.Label(labelframe1, text="Numéro de série", font=("Arial", 12))
lb_NS.place(x=25, y=25)
entryNS = tk.Entry(labelframe1, bd = 2, font=("Arial", 12), width=width_entry)
entryNS.place(x=x_entry, y=25)
lb_formatNS = ttk.Label(labelframe1, text="(Format : AASSTTNNNNNRRCCLLLL)", font=("Arial", 10, "italic"))
lb_formatNS.place(x=500, y=25)

lb_date_fab = ttk.Label(labelframe1, text="Date de fabrication", font=("Arial", 12))
lb_date_fab.place(x=25, y=75)
entryFAB = tk.Entry(labelframe1, bd = 2, font=("Arial", 12), width=width_entry)
entryFAB.place(x=x_entry, y=75)
lb_formatFAB = ttk.Label(labelframe1, text="(Format : JJ/MM/AAAA)", font=("Arial", 10, "italic"))
lb_formatFAB.place(x=500, y=75)

lb_date_mes = ttk.Label(labelframe1, text="Date de mise en service", font=("Arial", 12))
lb_date_mes.place(x=25, y=125)
entryMES = tk.Entry(labelframe1, bd = 2, font=("Arial", 12), width=width_entry)
entryMES.place(x=x_entry, y=125)
lb_formatMES = ttk.Label(labelframe1, text="(Format : JJ/MM/AAAA)", font=("Arial", 10, "italic"))
lb_formatMES.place(x=500, y=125)


# ##### Compteurs internes

# In[2809]:


labelframe2 = tk.LabelFrame(frame1,text="Compteurs Internes", font=("Arial", 12, "bold"), relief='groove')
labelframe2.place(x=20, y=250, width=width_lb, height=450)

# Heure de fonctionnement
lb_heure = ttk.Label(labelframe2, text="Heure de fonctionnement", font=("Arial", 12))
lb_heure.place(x=25, y=25)
entryHeure = tk.Entry(labelframe2, bd = 2, font=("Arial", 12), width=width_entry)
entryHeure.place(x=x_entry, y=25)
lb_formatNS = ttk.Label(labelframe2, text="(Entre 0 - 300000)", font=("Arial", 10, "italic"))
lb_formatNS.place(x=500, y=25)

# Moteur
lb_moteur = ttk.Label(labelframe2, text="Moteur", font=("Arial", 12))
lb_moteur.place(x=25, y=75)
entryMoteur = tk.Entry(labelframe2, bd = 2, font=("Arial", 12), width=width_entry)
entryMoteur.place(x=x_entry, y=75)
lb_formatMoteur = ttk.Label(labelframe2, text="(Entre 0 - 10000000)", font=("Arial", 10, "italic"))
lb_formatMoteur.place(x=500, y=75)

# Ventouse
lb_ventouse = ttk.Label(labelframe2, text="Ventouse", font=("Arial", 12))
lb_ventouse.place(x=25, y=125)
entryVentouse = tk.Entry(labelframe2, bd = 2, font=("Arial", 12), width=width_entry)
entryVentouse.place(x=x_entry, y=125)
lb_formatVentouse = ttk.Label(labelframe2, text="(Entre 0 - 10000000)", font=("Arial", 10, "italic"))
lb_formatVentouse.place(x=500, y=125)

# Electrovanne
lb_EV = ttk.Label(labelframe2, text="Electrovanne", font=("Arial", 12))
lb_EV.place(x=25, y=175)
entryEV = tk.Entry(labelframe2, bd = 2, font=("Arial", 12), width=width_entry)
entryEV.place(x=x_entry, y=175)
lb_formatEV = ttk.Label(labelframe2, text="(Entre 0 - 10000000)", font=("Arial", 10, "italic"))
lb_formatEV.place(x=500, y=175)

# Bouton ouverture
lb_BPO = ttk.Label(labelframe2, text="Bouton ouverture", font=("Arial", 12))
lb_BPO.place(x=25, y=225)
entryBPO = tk.Entry(labelframe2, bd = 2, font=("Arial", 12), width=width_entry)
entryBPO.place(x=x_entry, y=225)
lb_formatBPO = ttk.Label(labelframe2, text="(Entre 0 - 10000000)", font=("Arial", 10, "italic"))
lb_formatBPO.place(x=500, y=225)

# Bouton fermeture
lb_BPF = ttk.Label(labelframe2, text="Bouton fermeture", font=("Arial", 12))
lb_BPF.place(x=25, y=275)
entryBPF = tk.Entry(labelframe2, bd = 2, font=("Arial", 12), width=width_entry)
entryBPF.place(x=x_entry, y=275)
lb_formatBPF = ttk.Label(labelframe2, text="(Entre 0 - 10000000)", font=("Arial", 10, "italic"))
lb_formatBPF.place(x=500, y=275)

# Bouton rearmement
lb_BPRearm = ttk.Label(labelframe2, text="Bouton réarmement", font=("Arial", 12))
lb_BPRearm.place(x=25, y=325)
entryBPRearm = tk.Entry(labelframe2, bd = 2, font=("Arial", 12), width=width_entry)
entryBPRearm.place(x=x_entry, y=325)
lb_formatBPRearm = ttk.Label(labelframe2, text="(Entre 0 - 10000000)", font=("Arial", 10, "italic"))
lb_formatBPRearm.place(x=500, y=325)

# Bouton reset
lb_reset = ttk.Label(labelframe2, text="Bouton reset", font=("Arial", 12))
lb_reset.place(x=25, y=375)
entryReset = tk.Entry(labelframe2, bd = 2, font=("Arial", 12), width=width_entry)
entryReset.place(x=x_entry, y=375)
lb_formatReset = ttk.Label(labelframe2, text="(Entre 0 - 10000000)", font=("Arial", 10, "italic"))
lb_formatReset.place(x=500, y=375)


# ##### Port COM

# In[2810]:


labelframeCOM = tk.LabelFrame(frame1,text="Port COM", font=("Arial", 12, "bold"), relief='groove')
labelframeCOM.place(x=width_lb+50, y=30, width=160, height=100)

def actionScan():
    ports = serial.tools.list_ports.comports()
    listeCOMs= []
    for port, desc, hwid in sorted(ports):
        listeCOMs.append(port)
    combo['values'] = listeCOMs
    if len(listeCOMs) != 0:
        combo.current(0)
    else:
        combo.set('')

def actionConnect():
    global ser
    selected = str(combo.get())
    if btConnect['text'] == 'CONNECTER':
        if selected == '':
            return
        try:
            ser = serial.Serial(selected, baudrate=115200)
            if ser is None:
                ser.close()
                messages.config(state=tk.NORMAL)
                messages.insert(tk.END, 'Connexion ' + selected + ' impossible\n')
                messages.config(state=tk.DISABLED)
            else:
                btConnect['text'] = 'DECONNECTER'
                messages.config(state=tk.NORMAL)
                messages.insert(tk.END, 'Connexion ' + selected + ' réussie\n')
                messages.config(state=tk.DISABLED)
        except IOError:
            ser.close()
            messages.config(state=tk.NORMAL)
            messages.insert(tk.END, 'Connexion ' + selected +' impossible\n')
            messages.config(state=tk.DISABLED)
    else:
        btConnect['text'] = 'CONNECTER'
        messages.config(state=tk.NORMAL)
        messages.insert(tk.END, 'Déconnexion ' + selected + '\n')
        messages.config(state=tk.DISABLED)
        ser.close()

combo = ttk.Combobox(labelframeCOM, width=15, state='readonly')
combo.pack()
# combo.bind("<<ComboboxSelected>>", actionConnect)

# Bouton scan
btScan = tk.Button(labelframeCOM, text="SCAN", width=15, command=actionScan, bd=2)
btScan.pack(pady=1)

# Bouton connecter
btConnect = tk.Button(labelframeCOM, text="CONNECTER", width=15, command=actionConnect, bd=2)
btConnect.pack()


# In[ ]:





# ##### Comtpeurs tablier

# In[2811]:


heigth_port_com = 100

labelframeCptTablier = tk.LabelFrame(frame1,text="Compteurs Tablier", font=("Arial", 12, "bold"), relief='groove')
labelframeCptTablier.place(x=width_lb+50, y=heigth_port_com+50, width=160, height=200)


# ##### Messages

# In[2812]:


# def updateinfo():
#     messages.config(state=tk.NORMAL)
#     #info.delete('1.0', tk.END) # optionnel : effacer d'abord toutes les données du widget Text
#     i = 0
#     while (i < 1):
#         line = str(ser.readline())
#         line = line[2:][:-5]
#         print(line)
#         i += 1
#     ser.close()
#     current_time = messages.strftime("%H:%M:%S") + '\n'
#     messages.insert(tk.END, current_time)
#     messages.config(state=tk.DISABLED)


# ser = serial.Serial("COM3", baudrate=115200)

labelframe3 = tk.LabelFrame(frame1,text="Messages", font=("Arial", 12, "bold"), relief='groove')
labelframe3.place(x=width_lb+50, y=550, width=400, height=400)

messages = tk.Text(labelframe3, state=tk.DISABLED)
messages.place(x=0, y=0, width=392, height=345)


# ##### Bouton Effacer

# In[2813]:


def effacerTerminal():
    messages.config(state=tk.NORMAL)
    messages.delete('1.0', tk.END)
    messages.insert(tk.END, '')
    messages.config(state=tk.DISABLED)


bt_clear = tk.Button(labelframe3, text="EFFACER", command=effacerTerminal, bd=2)
bt_clear.place(x=330, y=345)


# ##### Bouton "Envoyé"

# In[2814]:


def envoiDonneeUsine():
    progress_value = progress_var.get()
    if progress_value < 100:
        if progress_value < 10:
            messages.config(state=tk.NORMAL)
            messages.insert(tk.END, 'Envoi en cours...\n')
            messages.config(state=tk.DISABLED)
        progress_var.set(progress_value + 10)
        frame1.after(500, envoiDonneeUsine)
    else :
        progress_value = 0
        progress_var.set(progress_value)
        messages.config(state=tk.NORMAL)
        messages.insert(tk.END, 'Envoi terminé\n')
        messages.config(state=tk.DISABLED)      


# In[2815]:


bt_send = tk.Button(frame1, text="ENVOYER", command=envoiDonneeUsine, bd=2)
bt_send.place(x=width_lb+50, y=450)


# ##### Barre de progression

# In[2816]:


progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(frame1, length=325, variable=progress_var, mode='determinate')
progress_bar.place(x=width_lb+125, y=452)


# ## Onglet CEGI2

# In[2817]:


label2 = ttk.Label(frame2, text="Contenu de la page 2")
label2.pack()


# ## Onglet Configuration

# In[2818]:


label3 = ttk.Label(frame3, text="Contenu de la page 3")
label3.pack()


# In[2819]:


notebook.pack() # ajout du notebook dans la fenetre principale

# Création du widget Scrollbar
scrollbar = tk.Scrollbar(frame1)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

fenetre.mainloop()


# ## Test

# In[ ]:





# In[ ]:





# In[2820]:


# import tkinter as tk
# from tkinter import ttk

# # Création de la fenêtre principale
# root = tk.Tk()
# root.title("Exemple de LabelFrame dans un Frame")
# root.geometry("300x200")

# # Création d'un Frame principal
# frame_principal = ttk.Frame(root, padding=10)
# frame_principal.pack(fill="both", expand=True)

# # Création d'un LabelFrame à l'intérieur du Frame principal
# labelframe = ttk.LabelFrame(frame_principal, text="Informations", padding=10)
# labelframe.pack(fill="both", expand=True)

# # Ajout de widgets dans le LabelFrame
# label_nom = ttk.Label(labelframe, text="Nom :")
# label_nom.grid(row=0, column=0, sticky="w")

# entry_nom = ttk.Entry(labelframe)
# entry_nom.grid(row=0, column=1, sticky="ew")

# # Pour que l'entrée s'étende avec la colonne
# labelframe.columnconfigure(1, weight=1)

# # Lancement de la boucle principale
# root.mainloop()


# In[ ]:





# In[2821]:


# import tkinter as tk
 
# programming = ['Java', 'Python', 'C++', 
#                'C#', 'JavaScript', 'NodeJS', 
#                'Kotlin', 'VB.Net', 'MySql', 'SQLite']
 
# # Création de la fenêtre principale
# window = tk.Tk()
# window.title("Exemple de Scrollbar")
# window.geometry("275x100")
# # Création du widget Listbox
# listbox = tk.Listbox(window)
 
# # Création du widget Scrollbar
# scrollbar = tk.Scrollbar(window)
 
# # Configuration de la relation entre le Listbox et le Scrollbar
# listbox.config(yscrollcommand=scrollbar.set)
# scrollbar.config(command=listbox.yview)
 
# # Ajout des éléments à la liste
# for item in programming:
#     listbox.insert(tk.END, item)
 
# # Placement des widgets dans la fenêtre
# listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
# scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
 
# # Lancement de la boucle principale
# window.mainloop()


# In[2822]:


# import time
# import tkinter as tk
# from datetime import datetime


# def updateinfo():
#     info.config(state=tk.NORMAL)
#     #info.delete('1.0', tk.END) # optionnel : effacer d'abord toutes les données du widget Text
#     now = datetime.now()
#     # current_time = now.strftime("%H:%M:%S") + '\n'
#     info.insert(tk.END, 'toto\n')
#     info.config(state=tk.DISABLED)

# info = tk.Text(state=tk.DISABLED)
# info.pack()
# btn = tk.Button(text="Cliquez-moi !", command=updateinfo)
# btn.pack()

# tk.mainloop()


# In[2823]:


# from tkinter import *
# from tkinter import ttk
# root = Tk()
# root.title("Barre de progression avec longueur ajustée")
# # Barre de progression avec une longueur de 400 pixels
# progress_bar = ttk.Progressbar(root,length=400)
# progress_bar.pack(pady=20)
# i = 0
# def update():
#     global i
#     i += 10
#     progress_bar.config(value=i)
# # Création du bouton et association de la fonction
# button = Button(root,text="Avancer",command=update)
# button.pack()
# root.mainloop()


# In[2824]:


# import tkinter as tk
# from tkinter import ttk
 
# def update_progress():
#     progress_value = progress_var.get()
#     if progress_value < 20:
#         progress_var.set(progress_value + 10)
#         root.after(500, update_progress)
 
# root = tk.Tk()
# root.title("Progress Bar Example")
# root.geometry('300x100')
# progress_var = tk.IntVar()
# progress_bar = ttk.Progressbar(root, variable=progress_var, mode='determinate')
# progress_bar.pack(pady=10)
 
# start_button = tk.Button(root, text="Start", command=update_progress)
# start_button.pack(pady=5)
 
# root.mainloop()


# In[2825]:


# import tkinter as tk
# from tkinter import ttk
 
# root = tk.Tk() 
# root.geometry('300x200')
 
# labelChoix = tk.Label(root, text = "Veuillez faire un choix !")
# labelChoix.pack()
 
# # 2) - créer la liste Python contenant les éléments de la liste Combobox
# listeProduits=["Laptop", "Imprimante","Tablette","SmartPhone"]
 
# # 3) - Création de la Combobox via la méthode ttk.Combobox()
# listeCombo = ttk.Combobox(root, values=listeProduits)
 
# # 4) - Choisir l'élément qui s'affiche par défaut
# listeCombo.current(0)
 
# listeCombo.pack()
# root.mainloop()


# In[2826]:


# import tkinter as tk
# from tkinter import ttk
 
# root = tk.Tk() 
# root.geometry('300x200')
 
# def action(event):
    
#     # Obtenir l'élément sélectionné
#     select = listeCombo.get()
#     print("Vous avez sélectionné : '", select,"'")
 
# labelChoix = tk.Label(root, text = "Veuillez faire un choix !")
# labelChoix.pack()
 
# # 2) - créer la liste Python contenant les éléments de la liste Combobox
# listeProduits=["Laptop", "Imprimante","Tablette","SmartPhone"]
 
# # 3) - Création de la Combobox via la méthode ttk.Combobox()
# listeCombo = ttk.Combobox(root, values=listeProduits, state= 'readonly')
 
# # 4) - Choisir l'élément qui s'affiche par défaut
# listeCombo.current(0)
 
# listeCombo.pack()
# listeCombo.bind("<<ComboboxSelected>>", action)
 
# root.mainloop()


# In[2827]:


# import tkinter as tk
# from tkinter import ttk

# def remplir_combobox():
#     # Liste des éléments à ajouter
#     elements = ["Option 1", "Option 2", "Option 3", "Option 4"]
#     # Remplir le combobox avec ces éléments
#     combo['values'] = elements
#     combo.current(0)  # Sélectionne le premier élément par défaut

# # Création de la fenêtre principale
# root = tk.Tk()
# root.title("Exemple de Combobox dynamique")

# # Création du Combobox (initialement vide)
# combo = ttk.Combobox(root)
# combo.pack(pady=10)

# # Création du bouton qui remplit le Combobox
# btn = tk.Button(root, text="Remplir le Combobox", command=remplir_combobox)
# btn.pack(pady=10)

# # Boucle principale
# root.mainloop()


# In[2828]:


# # Python program to get index of selected
# # option in Tkinter Combobox

# # Import the libraries tkinter
# from tkinter import *
# from tkinter import ttk

# # Create a GUI app
# app = Tk()

# # Set the geometry of the app
# app.geometry("600x400")

# # Function to clear the Combobox
# def clear():
#     combo.set('')

# # Function to print the index of selected option
# # in Combobox
# def get_index(*arg):
#     Label(app, text="The value at index " + str(combo.current()) +
#           " is" + " " + str(var.get()), font=('Helvetica 12')).pack()


# # Define Tuple of months
# months = ('January', 'February', 'March', 'April', 'May', 'June',
#           'July', 'August', 'September', 'October', 'November',
#           'December')

# # Create a Combobox widget
# var = StringVar()
# combo = ttk.Combobox(app, textvariable=var)
# combo['values'] = months
# combo['state'] = 'readonly'
# combo.pack(padx=5, pady=5)

# # Set the tracing for the given variable
# var.trace('w', get_index)

# # Create a button to clear the selected combobox 
# # text value
# button = Button(app, text="Clear", command=clear)
# button.pack()

# # Make infinite loop for displaying app on 
# # the screen
# app.mainloop()

