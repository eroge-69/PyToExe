import tkinter as tk
from tkinter import messagebox
import pyperclip
import random
import string

# --- Identifiants de connexion ---
LOGIN_ID = "KarimLH"
LOGIN_PASSWORD = "NhGiqTJr$eYQGj4KrbCSBkJgeScj4$igsa9mNFr4"

# --- Données des comptes ---
CREDENTIALS = {
    "ARLO CAMERA": {
        "ID": "autovisionlkd@gmail.com",
        "Password": "Karim1987@"
    },
    "SOGEXIA": {
        "ID": "lahcene.abdelkarim",
        "Password": "KarimLAHcene1987@"
    },
    "GMAIL": {
        "ID": "autovisionlkd@gmail.com",
        "Password": "bateau87@"
    },
    "VERISUR": {
        "ID": "Lahcene94600",
        "Password": "KarimLAHcene1987."
    }
}

# --- Couleurs Matrix 🇫🇷 ---
COLOR_BG = "#000000"
COLOR_TITLE = "#1E90FF"  # Bleu
COLOR_ID = "#FFFFFF"     # Blanc
COLOR_PASS = "#FF4040"   # Rouge
COLOR_BTN = "#1E90FF"

FONT_TITLE = ("Courier", 20, "bold")
FONT_LABEL = ("Courier", 12)
FONT_CREDITS = ("Courier", 10, "italic")

# --- Animation Matrix en fond ---
class MatrixBackground:
    def __init__(self, canvas, width, height, font_size=14):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.font_size = font_size
        self.columns = int(width / font_size)
        self.drops = [0 for _ in range(self.columns)]

        self.texts = list(string.ascii_letters + string.digits + "アカサタナハマヤラワ012345")

    def draw(self):
        self.canvas.delete("matrix")
        for i in range(self.columns):
            char = random.choice(self.texts)
            x = i * self.font_size
            y = self.drops[i] * self.font_size

            self.canvas.create_text(x, y, text=char, fill="#00FF00", tags="matrix", font=("Courier", self.font_size))

            if y > self.height and random.random() > 0.975:
                self.drops[i] = 0
            self.drops[i] += 1

        self.canvas.after(50, self.draw)

# --- Fonction pour copier un mot de passe ---
def copy_to_clipboard(text):
    pyperclip.copy(text)
    messagebox.showinfo("Copié", "Mot de passe copié dans le presse-papiers !")

# --- Affiche les comptes si connexion réussie ---
def show_credentials():
    login_frame.destroy()

    content_frame = tk.Frame(root, bg=COLOR_BG)
    content_frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(content_frame, text="🔐 PANEL DE COMPTES", font=FONT_TITLE, bg=COLOR_BG, fg=COLOR_TITLE).pack(pady=10)

    for site, creds in CREDENTIALS.items():
        frame = tk.Frame(content_frame, bg=COLOR_BG)
        frame.pack(anchor="w", pady=5, fill="x")

        tk.Label(frame, text=f"▶ {site}", font=FONT_LABEL, bg=COLOR_BG, fg=COLOR_TITLE).pack(anchor="w")
        tk.Label(frame, text=f"   📧 ID : {creds['ID']}", font=FONT_LABEL, bg=COLOR_BG, fg=COLOR_ID).pack(anchor="w")

        pass_frame = tk.Frame(frame, bg=COLOR_BG)
        pass_frame.pack(anchor="w")

        tk.Label(pass_frame, text=f"   🔑 Mot de passe : {creds['Password']}", font=FONT_LABEL, bg=COLOR_BG, fg=COLOR_PASS).pack(side="left")
        tk.Button(pass_frame, text="Copier", command=lambda pw=creds['Password']: copy_to_clipboard(pw),
                  font=("Courier", 10), bg=COLOR_BTN, fg=COLOR_BG, relief="flat").pack(side="left", padx=10)

        tk.Label(frame, text="-"*70, font=FONT_LABEL, bg=COLOR_BG, fg=COLOR_ID).pack(anchor="w", pady=5)

    tk.Label(content_frame, text="🇫🇷 Logiciel créé par Dalil Lahcene 🇫🇷", font=FONT_CREDITS, bg=COLOR_BG, fg=COLOR_TITLE).pack(pady=20)

# --- Vérifie l'identifiant ---
def check_credentials():
    if id_entry.get() == LOGIN_ID and password_entry.get() == LOGIN_PASSWORD:
        show_credentials()
    else:
        messagebox.showerror("Erreur", "Identifiant ou mot de passe incorrect")

# --- Fenêtre principale ---
root = tk.Tk()
root.title("🔐 Connexion sécurisée - Matrix FR 🇫🇷")
app_width = 800
app_height = 600
root.geometry(f"{app_width}x{app_height}")
root.configure(bg=COLOR_BG)
root.resizable(False, False)

# --- Canvas pour animation Matrix ---
canvas = tk.Canvas(root, width=app_width, height=app_height, bg=COLOR_BG, highlightthickness=0)
canvas.place(x=0, y=0)
matrix = MatrixBackground(canvas, app_width, app_height)
matrix.draw()

# --- Frame de connexion ---
login_frame = tk.Frame(root, bg=COLOR_BG)
login_frame.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(login_frame, text="ID de connexion :", font=FONT_LABEL, bg=COLOR_BG, fg=COLOR_ID).pack(pady=5)
id_entry = tk.Entry(login_frame, font=FONT_LABEL, width=30, bg="#1C1C1C", fg=COLOR_ID, insertbackground=COLOR_ID)
id_entry.pack()

tk.Label(login_frame, text="Mot de passe :", font=FONT_LABEL, bg=COLOR_BG, fg=COLOR_ID).pack(pady=5)
password_entry = tk.Entry(login_frame, show="*", font=FONT_LABEL, width=30, bg="#1C1C1C", fg=COLOR_ID, insertbackground=COLOR_ID)
password_entry.pack()

tk.Button(login_frame, text="Se connecter", command=check_credentials, font=FONT_LABEL,
          bg=COLOR_BTN, fg=COLOR_BG, activebackground=COLOR_PASS, activeforeground=COLOR_ID).pack(pady=15)

root.mainloop()
