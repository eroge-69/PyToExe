import os
from cryptography.fernet import Fernet
import hashlib
import base64
import tkinter as t
import time
import winsound as w
import tkinter.messagebox

#-----------VARS-----------
BG="black"
FOLDERNAME = "-private-"


class Main(t.Tk):
    def __init__(self):
        super().__init__()
        self.config(bg=BG)
        self.resizable(False, False)
        self.title("F1LE_D3KR1P7ER")
        self.iconbitmap("decrypter/icon.ico")
        self.geometry("600x750")
        self.splashscreen()
        self.guide1 = t.Label(bg=BG, fg="green", text="1NS3R1SC1 L4 CH14V3 D1 D3CR1774Z1ON3:", font=("Impact", 21))
        self.guide1.pack(pady=10)
        self.entry1 = t.Entry(bg=BG, fg="green", font=("Impact", 31))
        self.entry1.pack()
        self.button1 = t.Button(bg=BG, fg="green", font=("Impact", 31), text="OK", command=self.button1f)
        self.button1.pack(pady=21)
        
    def button1f(self):
        self.password = self.entry1.get()
        w.Beep(1000, 50)

        self.guide1.destroy()
        self.entry1.destroy()
        self.button1.destroy()

        self.initialize()

    def initialize(self):
        self.crittografa = t.Button(bg=BG, fg="green", font=("Impact", 50), width=15, text="CR1770GR4F4", command=lambda: self.crittografa_cartella(FOLDERNAME, self.password))
        self.crittografa.pack(pady=88)

        self.decrittografa = t.Button(bg=BG, fg="green", font=("Impact", 50), width=15, text="D3CR1770GR4F4", command=lambda: self.decrittografa_cartella(FOLDERNAME, self.password))
        self.decrittografa.pack(pady=50)

    def splashscreen(self):
        splashphoto = t.PhotoImage(file="decrypter/splashscreen.png")
        splash = t.Label(bg=BG, image=splashphoto)
        splash.pack()
        self.update()
        old_time = time.time()
        w.PlaySound("decrypter/splash_sound.wav", w.SND_ASYNC)

        while time.time()-old_time < 3:
            self.update()

        self.update()
        splash.destroy()
        self.update()

    def genera_chiave(self, password):
        """Genera una chiave Fernet da una password"""
        # Usa SHA-256 per derivare una chiave fissa da una password
        sha = hashlib.sha256(password.encode()).digest()
        return Fernet(base64.urlsafe_b64encode(sha))

    def crittografa_file(self, percorso, fernet):

        with open(percorso, 'rb') as file:
            dati = file.read()

        dati_criptati = fernet.encrypt(dati)
        with open(percorso, 'wb') as file:
            file.write(dati_criptati)

        head, tail = os.path.split(percorso)
        os.rename(percorso, head+"/"+fernet.encrypt(tail.encode("utf-8")).decode('utf-8'))

    def decrittografa_file(self, percorso, fernet):
        with open(percorso, 'rb') as file:
            dati_criptati = file.read()

        dati = fernet.decrypt(dati_criptati)
        with open(percorso, 'wb') as file:
            file.write(dati)

        head, tail = os.path.split(percorso)
        os.rename(percorso, head+"/"+fernet.decrypt(tail.encode("utf-8")).decode('utf-8'))

    def crittografa_cartella(self, percorso_cartella, password):
        fernet = self.genera_chiave(password)
        for root, _, files in os.walk(percorso_cartella):
            for nome_file in files:
                percorso_file = os.path.join(root, nome_file)
                print(f"Crittografo: {percorso_file}")
                self.crittografa_file(percorso_file, fernet)

    def decrittografa_cartella(self, percorso_cartella, password):
        fernet = self.genera_chiave(password)
        for root, _, files in os.walk(percorso_cartella):
            for nome_file in files:
                percorso_file = os.path.join(root, nome_file)
                print(f"Decrittografo: {percorso_file}")
                try:
                    self.decrittografa_file(percorso_file, fernet)
                except Exception as e:
                    print(f"Errore con {percorso_file}: {e}")


root = Main()
root.mainloop()
