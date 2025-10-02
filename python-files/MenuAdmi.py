# -*- coding utf-8 -*-

import tkinter as tk
import datetime
import subprocess

from tkinter import *
from tkinter import messagebox 
from pathlib import Path

import sys

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(Path(sys.argv[0]).stem)
        self.configure(bg="lightblue")
        self.state("zoomed")
        self.resizable(False, False)

        self.frmtela()
        self.lblcabe()
        self.menuadm()

    def frmtela(self):
        
        self.frm_1 = tk.Frame(self, bd = 5, bg = "lightgray", relief="ridge")
        self.frm_1.place(relx=0.005, rely=0.02, relwidth=0.28, relheight=0.10)

        self.frm_2 = tk.Frame(self, bd = 5, bg = "lightgray", relief="ridge")
        self.frm_2.place(relx=0.29, rely=0.02, relwidth=0.425, relheight=0.10)

        self.frm_3 = tk.Frame(self, bd = 5, bg = "lightgray", relief="ridge")
        self.frm_3.place(relx=0.72, rely=0.02, relwidth=0.275, relheight=0.10)

        self.frm_4 = tk.Frame(self, bd=3, bg = "lightgray", relief="ridge")
        self.frm_4.place(relx=0.005, rely=0.13, relwidth=0.990, relheight=0.85)

        self.frm_5 = tk.Frame(self.frm_4, bd=3, bg = "lightblue", relief="ridge")
        self.frm_5.place(relx=0.288, rely=0.02, relwidth=0.428, relheight=0.96)
        
    def lblcabe(self):

        self.lbc_S = Label(self.frm_1, text="Sistema Gestão de Bolsas", 
            font=("Times New Roman", 20, "bold","italic"), bg=("lightgray"), fg=("green"))
        self.lbc_S.pack(pady=20)

        self.lbc_P = Label(self.frm_2, text="Administrador do Sistema", 
           font=("Times New Roman", 20, "bold","italic"), bg=("lightgray"), fg=("green"))
        self.lbc_P.pack(pady=20)

        try:
            self.usuar = sys.argv[1]
        except IndexError:
            messagebox.showerror("Erro !!!", "Usuário Invalido")
            exit()

        self.lbc_D = Label(self.frm_3,
            font=("Times New Roman", 18, "bold","italic"), bg=("lightgray"), fg=("green"))
        self.lbc_D.pack(pady=20)

        def atualizar_data_hora():
            data_hora_atual = datetime.datetime.now().strftime("Data:%d/%m/%Y Hora:%H:%M:%S")
            self.lbc_D.config(text=data_hora_atual)
            self.lbc_D.after(1000, atualizar_data_hora)
      
        atualizar_data_hora()

    def menuadm(self):

        apporigem  = "MenuAdmi.py"

        def on_enter(event):
            # Mudar a cor de fundo do widget para amarelo ao passar o mouse
            event.widget.config(bg="lightgreen")

        def on_leave(event):
            # Mudar a cor de fundo do widget de volta para branco ao sair
            event.widget.config(bg="white")

        def btCadMatra():
            app.destroy()
            subprocess.run([sys.executable, "CadMatra.py", self.usuar, apporigem])

        def btCadMatda(): 
            app.destroy()
            subprocess.run([sys.executable, "CadMatda.py", self.usuar, apporigem])

        def btCadLocal(): 
            app.destroy()
            subprocess.run([sys.executable, "CadLocal.py", self.usuar, apporigem])

        def btCadUsuar(): 
            app.destroy()
            subprocess.run([sys.executable, "CadUsuar.py", self.usuar, apporigem])
        
        def btResSenha(): 
            app.destroy()
            subprocess.run([sys.executable, "ResSenha.py", self.usuar, apporigem])

        def btMenuModu(): 
            app.destroy() 		
            subprocess.run([sys.executable, "MenuModu.py", self.usuar, apporigem])
            
        def btInicSyst(): 
            app.destroy()
            subprocess.run([sys.executable, "InicSyst.py", self.usuar])            

        btCadMatra = Button(self.frm_5, text="Cadastro de Mantenedora", 
        width=25, height = 1, bd=5,
        font=("Times New Roman", 20, "bold","italic"),
        command=(btCadMatra))
        btCadMatra.pack(pady=10)
        btCadMatra.config(bg="white")
        btCadMatra.bind("<Enter>", on_enter)
        btCadMatra.bind("<Leave>", on_leave)

        btCadMatda = Button(self.frm_5,text="Cadastro de Mantida", 
        width=25, height = 1, bd=5,
        font=("Times New Roman", 20, "bold","italic"),
        command=(btCadMatda))
        btCadMatda.pack(pady=10)
        btCadMatda.config(bg="white")
        btCadMatda.bind("<Enter>", on_enter)
        btCadMatda.bind("<Leave>", on_leave)

        btCadLocal = Button(self.frm_5,text="Cadastro de Local de Oferta",
        width=25, height = 1, bd=5,
        font=("Times New Roman", 20, "bold","italic"),
        command=btCadLocal)
        btCadLocal.pack(pady=10)
        btCadLocal.config(bg="white")
        btCadLocal.bind("<Enter>", on_enter)
        btCadLocal.bind("<Leave>", on_leave)

        btCadUsuar = Button(self.frm_5,text="Cadastro de Usuário", 
        width=25, height = 1, bd=5,
        font=("Times New Roman", 20, "bold","italic"),
        command=btCadUsuar)
        btCadUsuar.pack(pady=10)
        btCadUsuar.config(bg="white")
        btCadUsuar.bind("<Enter>", on_enter)
        btCadUsuar.bind("<Leave>", on_leave)

        btResSenha = Button(self.frm_5,text="Reseta a Senha do Usuário", 
        width=25, height = 1, bd=5,
        font=("Times New Roman", 20, "bold","italic"),
        command=btResSenha)
        btResSenha.pack(pady=10)
        btResSenha.config(bg="white")
        btResSenha.bind("<Enter>", on_enter)
        btResSenha.bind("<Leave>", on_leave)

        btMenuModu = Button(self.frm_5,text='Módulos do Sistema', 
        width=25, height = 1, bd=5,
        font=("Times New Roman", 20, "bold","italic"),
        command=btMenuModu)
        btMenuModu.pack(pady=10)
        btMenuModu.config(bg="white")
        btMenuModu.bind("<Enter>", on_enter)
        btMenuModu.bind("<Leave>", on_leave)

        btInicSyst = Button(self.frm_5,text="Login do Sistema", 
        width=25, height = 1, bd=5,
        font=("Times New Roman", 20, "bold","italic"),
        command=(btInicSyst))
        btInicSyst.pack(pady=10)
        btInicSyst.config(bg="white")
        btInicSyst.bind("<Enter>", on_enter)
        btInicSyst.bind("<Leave>", on_leave)

if __name__ == "__main__":
    app = App()
    app.mainloop()
