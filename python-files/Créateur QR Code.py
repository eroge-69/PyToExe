# -*- coding: utf-8 -*-
"""
Created on Thu Sep  4 13:05:53 2025

@author: pmarige
"""

import qrcode
import requests
import os
from PIL import ImageTk
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *

def run():
    global window, var_url, var_taille, var_fg_col, var_bg_col
    global Lbl_img, Button_save_s, Button_save_m, Button_save_l
    # Fenêtre
    window = Tk()
    window.title('Créateur de QR Code')
    window.geometry('800x500')
    Lbl_url = Label(window, text='Url à transformer en QR Code',
                        font=('normal', 14))
    Lbl_url.pack(side='top', fill='y')
    var_url = StringVar()
    Ent_url = Entry(window, width=100, textvariable=var_url)
    Ent_url.pack(side='top')
    Lf_fg_col = LabelFrame(window, text='Couleur QR Code')
    Lf_fg_col.pack(side='top', fill='x')
    var_fg_col = StringVar()
    fg_col_1 = Radiobutton(Lf_fg_col, text='Noir', value='#000000', 
                           variable=var_fg_col, command=affiche_qrcode)
    fg_col_2 = Radiobutton(Lf_fg_col, text='Blanc', value='#ffffff', 
                           variable=var_fg_col, command=affiche_qrcode)
    fg_col_3 = Radiobutton(Lf_fg_col, text='Bleu', value='#196cb4', 
                           variable=var_fg_col, command=affiche_qrcode)
    fg_col_4 = Radiobutton(Lf_fg_col, text='Jaune', value='#f7dc0c', 
                           variable=var_fg_col, command=affiche_qrcode)
    fg_col_1.pack(side='left', expand=True)
    fg_col_2.pack(side='left', expand=True)
    fg_col_3.pack(side='left', expand=True)
    fg_col_4.pack(side='left', expand=True)
    Lf_bg_col = LabelFrame(window, text='Couleur Fond')
    Lf_bg_col.pack(side='top', fill='x')
    var_bg_col = StringVar()
    bg_col_1 = Radiobutton(Lf_bg_col, text='Blanc', value='#ffffff', 
                           variable=var_bg_col, command=affiche_qrcode)
    bg_col_2 = Radiobutton(Lf_bg_col, text='Noir', value='#000000', 
                           variable=var_bg_col, command=affiche_qrcode)
    bg_col_3 = Radiobutton(Lf_bg_col, text='Jaune', value='#f7dc0c', 
                           variable=var_bg_col, command=affiche_qrcode)
    bg_col_4 = Radiobutton(Lf_bg_col, text='Bleu', value='#196cb4', 
                           variable=var_bg_col, command=affiche_qrcode)
    bg_col_1.pack(side='left', expand=True)
    bg_col_2.pack(side='left', expand=True)
    bg_col_3.pack(side='left', expand=True)
    bg_col_4.pack(side='left', expand=True)
    bg_col_1.invoke()
    Lbl_img = Label(window)
    Lbl_img.pack(side='top', fill='y')
    Button_save_s = Button(window, text='', state='disabled')
    Button_save_m = Button(window, text='', state='disabled')
    Button_save_l = Button(window, text='', state='disabled')
    Button_save_s.pack(side='left', expand=True)
    Button_save_m.pack(side='left', expand=True)
    Button_save_l.pack(side='left', expand=True)
    window.mainloop()

def affiche_qrcode():
    global window, var_url, var_taille, var_fg_col, var_bg_col
    global Lbl_img, Button_save_s, Button_save_m, Button_save_l
    if var_url.get():
        Lbl_img.destroy()
        Button_save_s.destroy()
        Button_save_m.destroy()
        Button_save_l.destroy()
        window.update()
        url = var_url.get()
        fg_col = var_fg_col.get()
        bg_col = var_bg_col.get()
        qr = qrcode.QRCode()
        qr.add_data(url)
        #qr.make(fit=True)
        imgQR = qr.make_image(fill_color=fg_col, back_color=bg_col)
        imgRS = imgQR.resize((300, 300))
        imgTk = ImageTk.PhotoImage(imgRS)
        Lbl_img = Label(window, image=imgTk)
        Lbl_img.image = imgTk
        Lbl_img.pack(side='top', fill='y', expand=True)
        Button_save_s = Button(window, text='Enregistrer (petit)', 
                               command=lambda img=imgQR, size='s':save(imgQR, size))
        Button_save_m = Button(window, text='Enregistrer (moyen)', 
                               command=lambda img=imgQR, size='m':save(imgQR, size))
        Button_save_l = Button(window, text='Enregistrer (grand)', 
                               command=lambda img=imgQR, size='l':save(imgQR, size))
        Button_save_s.pack(side='left', expand=True)
        Button_save_m.pack(side='left', expand=True)
        Button_save_l.pack(side='left', expand=True)

def save(imgQR, size):
    global var_url
    if size=='s':
        nouv_taille = (100, 100)
    elif size=='m':
        nouv_taille = (300, 300)
    elif size=='l':
        nouv_taille = (800, 800)
    imgRS = imgQR.resize(nouv_taille)
    url = var_url.get()
    headers = {'User-Agent': 'Mozilla/5.0'}
    session = requests.Session()
    try:
        r = session.get(url, headers=headers)
        contenu = r.text
        nom_fichier = contenu[contenu.find('<title>') + 7 : contenu.find('</title>')]
        nom_fichier += ' - ' + size
    except:
        nom_fichier = 'qrcode.png'
    cible = filedialog.asksaveasfilename(initialdir=os.path.expanduser("~/Desktop"), 
                                         defaultextension='.png', 
                                         initialfile=nom_fichier, 
                                         title='Enregistrer')
    if cible:
        imgRS.save(cible)

if __name__ == "__main__":
    run()