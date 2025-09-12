import random
import tkinter as tk
from tkinter import messagebox

# Epoche e missioni
epoche = ["Preistoria", "Medioevo", "Cyberpunk", "Apocalisse Zombie"]
missioni = {
    "Preistoria": ["Raccogliere legna", "Cacciare dinosauri", "Costruire un rifugio"],
    "Medioevo": ["Difendere il villaggio", "Costruire un castello", "Sconfiggere il drago"],
    "Cyberpunk": ["Hackerare la rete", "Recuperare gadget futuristico", "Combattere cyborg"],
    "Apocalisse Zombie": ["Proteggere sopravvissuti", "Raccogliere risorse", "Sconfiggere lo zombie boss"]
}

effetti = {}

# Giocatore
class Giocatore:
    def __init__(self, nome):
        self.nome = nome
        self.xp = 0
        self.livello = 1

    def guadagna_xp(self, punti):
        self.xp += punti
        if self.xp >= self.livello * 10:
            self.livello += 1
            self.xp = 0
            messagebox.showinfo("Level Up!", f"{self.nome} è salito al livello {self.livello}!")

giocatore = None
round_totali = 5
round_corrente = 0

# Funzioni di gioco
def gioca_round():
    global round_corrente
    if round_corrente >= round_totali:
        messagebox.showinfo("Fine Gioco", f"{giocatore.nome} ha raggiunto il livello {giocatore.livello} con {giocatore.xp} XP.")
        root.destroy()
        return

    epoca = random.choice(epoche)
    missione = random.choice(missioni[epoca])
    effetto = effetti.get(epoca, "Nessun effetto del passato in questa epoca.")
    
    risposta = messagebox.askyesno(f"Epoca: {epoca}", f"{effetto}\nMissione: {missione}\nVuoi tentare la missione?")
    
    if risposta:
        successo = random.choice([True, False])
        if successo:
            punti = random.randint(5, 10)
            giocatore.guadagna_xp(punti)
            effetti[epoca] = "Missione completata, epoca futura influenzata positivamente."
            messagebox.showinfo("Missione Completata", f"Hai guadagnato {punti} XP!")
        else:
            effetti[epoca] = "Missione fallita, epoca futura influenzata negativamente."
            messagebox.showwarning("Missione Fallita", "La missione non è andata a buon fine...")
    else:
        effetti[epoca] = "Missione ignorata, epoca futura incerta."

    round_corrente += 1
    gioca_round()

def start_game():
    global giocatore
    nome = entry_nome.get()
    if nome.strip() == "":
        messagebox.showwarning("Errore", "Inserisci un nome!")
        return
    giocatore = Giocatore(nome)
    entry_nome.destroy()
    btn_start.destroy()
    gioca_round()

# Interfaccia GUI
root = tk.Tk()
root.title("Echi del Tempo - Demo GUI")
root.geometry("400x200")

tk.Label(root, text="Inserisci il tuo nome:").pack(pady=10)
entry_nome = tk.Entry(root)
entry_nome.pack(pady=5)
btn_start = tk.Button(root, text="Inizia Gioco", command=start_game)
btn_start.pack(pady=20)

root.mainloop()
