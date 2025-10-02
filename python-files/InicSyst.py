# -*- coding utf-8 -*-

import tkinter as tk
import mysql.connector
import subprocess
import sys
import bcrypt

from tkinter import *
from tkinter import messagebox
from pathlib import Path
#from DataBase import conectar_banco, tabela_existe
from DataBase import tabela_existe

#import CriaTabe

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title(Path(sys.argv[0]).stem)
        self.configure(bg='lightblue')
        self.state("zoomed")
        self.resizable(False, False)

        self.frmtela()
        self.lblcabe()
        self.lbl_cmp()
        self.btnacao()

    def frmtela(self):
        
        self.frm_1 = tk.Frame(self, bd=3, bg = "lightgray", relief="ridge")
        self.frm_1.place(relx=0.005, rely=0.02, relwidth=0.99, relheight=0.10)

        self.frm_2 = tk.Frame(self,bd=3, bg = "lightgray", relief="ridge")
        self.frm_2.place(relx=0.005, rely=0.13, relwidth=0.990, relheight=0.85)

        self.frm_3 = tk.Frame(self.frm_2, bd=3, bg = "lightblue", relief="ridge")
        self.frm_3.place(relx=0.288, rely=0.02, relwidth=0.428, relheight=0.96)
    
    def lblcabe(self):
        self.lbl_1 = Label(self.frm_1, text='Início do Sistema', 
        font=('Times New Roman', 25, 'bold','italic'), bg=('lightgray'), fg=("green"))
        self.lbl_1.pack(pady=20)

    def lbl_cmp(self):
        #-----------------------------------------------------#
        # Validação para não permitir digitar acima do tamanho#
        #-----------------------------------------------------#
        def valida_tamanho(text, tam):
            max_length = int(tam)
            if len(text) > max_length:
                return False
            return True
        #-----------------------------------------------------------#
        self.label_login = Label(self.frm_3, text="Login do Sistema", 
            relief="ridge", width=15, height = 1, bd=5, 
            font=("Times New Roman", 25, "bold", "italic"), 
            bg=("lightblue"), fg=("blue"))
        self.label_login.pack(pady=60)
        #-----------------------------------------------------------#
        self.label_usuar = Label(self.frm_3, text="Usuário", 
            font=("Times New Roman", 22, "bold","italic"), 
            bg=("lightblue"), fg=("blue"))
        self.label_usuar.pack(pady=5)
        #-----------------------------------------------------------#
        self.campo_usuar = Entry(self.frm_3, width=25,
            font=("Times New Roman", 16, "bold"),justify="center")
        self.campo_usuar.config(validate="key", 
            validatecommand=(self.campo_usuar.master.register(valida_tamanho), "%P", 15))
        self.campo_usuar.pack()
        self.campo_usuar.focus()
        #-----------------------------------------------------------#
        self.label_senha = Label(self.frm_3, text="Senha",
             font=("Times New Roman", 22, "bold","italic"), 
             bg=("lightblue"),fg=("blue"))
        self.label_senha.pack()
        #-----------------------------------------------------------#
        self.campo_senha = Entry(self.frm_3, width=25, show="*", 
            font=("Times New Roman", 16, "bold"),justify="center")
        self.campo_senha.config(validate="key", 
            validatecommand=(self.campo_senha.master.register(valida_tamanho), "%P", 15))
        self.campo_senha.pack()

    def btnacao(self):
        #------------------------------------------------------#
        #  Alteração da cor do botão quando o cursor passar    #
        #------------------------------------------------------#
        def on_enter(event):
            # Mudar a cor de fundo 
            event.widget.config(bg="lightgreen")
        def on_leave(event):
            # Volta a cor de fundo 
            event.widget.config(bg="white")

        self.btEnter = Button(self.frm_3,text="Entrar no Sistema", 
            width=19, bd=4,
            font=("Times New Roman", 18, "bold","italic"),
            command=self.validar_login)
        self.btEnter.pack(pady=20)
        self.btEnter.bind("<Enter>", on_enter)
        self.btEnter.bind("<Leave>", on_leave)

        self.btGerar = Button(self.frm_3,text="Gerar Senha", 
            width=19, bd=4,
            font=("Times New Roman", 18, "bold","italic"),
            command=self.gera_senha)
        self.btGerar.pack(pady=5)
        self.btGerar.bind("<Enter>", on_enter)
        self.btGerar.bind("<Leave>", on_leave)

        self.btSair = Button(self.frm_3,text="Sair do Login", 
            width=19, bd=4,
            font=("Times New Roman", 18, "bold","italic"),
            command=self.Sair_sistema)
        self.btSair.pack(pady=20)
        self.btSair.bind("<Enter>", on_enter)
        self.btSair.bind("<Leave>", on_leave)

    def conectar_banco(self):

        CONFIG = {
            'host': 'localhost',
            'user': 'root',
            'password': 'luciana',
            'database': 'sgbdb'
            }

        try:
            mydb = mysql.connector.connect(**CONFIG)
            return mydb
        except mysql.connector.Error as err:
            mydb.close()
            mycursor.close()
            messagebox.showerror("Erro", f"Erro de Conexão como Banco de Dados: {err}")
            mydb = None
            exit()

    def validar_login(self):
        if not self.campo_usuar.get():
            messagebox.showinfo("Inclui", "Informe o Usuário")
            self.campo_usuar.focus_set()
            return()

        if not self.campo_senha.get():
            messagebox.showinfo("Inclui", "Informe a Senha")
            self.campo_senha.focus_set()
            return()

        self.usuar = self.campo_usuar.get().upper()
        self.senha = self.campo_senha.get().upper()

        if not tabela_existe('CadUsuar'):
            messagebox.showerror("Erro !!!", "Tabela Cadastro de Usuário não existe")
            exit()
        else:

            global mydb
            
            mydb = self.conectar_banco()

            if mydb.is_connected():
                messagebox.showinfo("Ok !!!", "Conexão com MySQL estabelecida com sucesso")

            mycursor = mydb.cursor()


            try:
                mycursor.execute("""SELECT CodUsuar, SenUsuar 
                                    FROM   CadUsuar     
                                    WHERE  CodUsuar = %s""", (self.usuar,))

                resultado = mycursor.fetchone()

                codusuar, senusuar = resultado

                mydb.close()
                mycursor.close()

                if senusuar == None:
                    messagebox.showinfo("Atenção !!!", "Senha não está criada, clica em 'Gerar Senha'")
                    self.campo_senha.focus()            
                else:
                    if bcrypt.checkpw(self.senha.encode(), senusuar):
                        if self.usuar == "MASTER": 
                            app.destroy()
                            subprocess.run([sys.executable, "MenuAdmi.py", self.usuar])
                        else:
                            app.destroy()
                            subprocess.run([sys.executable, "MenuModu.py", self.usuar])
                    else:
                        messagebox.showinfo("Atenção !!!", "Senha invalida")
                        self.campo_senha.focus()			

            except:
                mydb.close()
                mycursor.close()
                messagebox.showerror("Atenção !!!", "Usuário Invalido")
                self.campo_usuar.focus()            
                return()

    def gera_senha(self):

        self.usuar = self.campo_usuar.get().upper()

        if self.usuar == "":
            messagebox.showinfo("Atenção !!!", "Informe o Usuário")
            self.campo_usuar.focus()    
            return()    
        else:
            mydb = conectar_banco()
            mycursor = mydb.cursor()

            try:
                mycursor.execute("""SELECT CodUsuar, SenUsuar
                                    FROM   CadUsuar     
                                    WHERE  CodUsuar = %s""", (self.usuar,))

                resultado = mycursor.fetchone()

                codusuar, senusuar = resultado

                mydb.close()
                mycursor.close()

                if resultado:
                    if senusuar:
                        messagebox.showinfo("Atenção !!!", "Usuário já tem senha gerada. Se esqueceu a senha, fale com o Administrador do sistema para resetar a senha")
                        self.campo_usuar.focus()            
                        return()
                    else:
                        app.destroy()
                        subprocess.run([sys.executable, "GerSenha.py", self.usuar]) 
                else:
                    messagebox.showinfo("Atenção !!!", "Usuário invalido")
                    self.campo_usuar.focus()            
                    return()
            except:

                mydb.close()
                mycursor.close()

                messagebox.showerror("Consulta !!!", "Erro ao buscar dados no Cadastro de Usuário")
                exit()

    def Sair_sistema(self):
        app.destroy()
        exit()
    
if __name__ == "__main__":
    app = App()
    app.mainloop()
