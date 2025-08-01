import tkinter as tk
import random

cartes_valeurs = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
    "7": 7, "8": 8, "9": 9, "10": 10,
    "J": 10, "Q": 10, "K": 10, "A": 11
}

class BlackjackGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("♠ Blackjack Casino ♣")
        self.root.configure(bg="#003300")
        self.solde = 400
        self.mise = 10
        self.init_widgets()
        self.rejouer_btn.config(state=tk.DISABLED)

    def init_widgets(self):
        self.titre = tk.Label(self.root, text="♠ Blackjack Casino ♣", font=("Arial Black", 26), bg="#003300", fg="gold")
        self.titre.pack(pady=10)

        self.solde_label = tk.Label(self.root, text=f"💰 Solde : {self.solde} jetons", font=("Arial", 18, "bold"), bg="#003300", fg="white")
        self.solde_label.pack()

        self.mise_frame = tk.Frame(self.root, bg="#003300")
        self.mise_frame.pack(pady=5)
        self.mise_label = tk.Label(self.mise_frame, text="Mise :", font=("Arial", 14), bg="#003300", fg="white")
        self.mise_label.pack(side=tk.LEFT)
        self.mise_entry = tk.Entry(self.mise_frame, width=6, font=("Arial", 14))
        self.mise_entry.insert(0, str(self.mise))
        self.mise_entry.pack(side=tk.LEFT, padx=5)
        self.mise_entry.bind("<KeyRelease>", self.verifier_mise)

        self.mise_erreur_label = tk.Label(self.root, text="", font=("Arial", 12, "bold"), bg="#003300", fg="red")
        self.mise_erreur_label.pack()

        self.main_frame = tk.Frame(self.root, bg="#003300")
        self.main_frame.pack(pady=20)

        self.label_dealer = tk.Label(self.main_frame, text="Main du dealer", font=('Arial', 20, "bold"), bg="#003300", fg="white")
        self.label_dealer.pack()
        self.main_dealer_label = tk.Label(self.main_frame, text="", font=('Courier New', 20), bg="#660000", fg="white", width=45, height=2)
        self.main_dealer_label.pack(pady=10)

        tk.Label(self.main_frame, text="", bg="#003300").pack(pady=10)

        self.label_joueur = tk.Label(self.main_frame, text="Votre main", font=('Arial', 20, "bold"), bg="#003300", fg="white")
        self.label_joueur.pack()
        self.main_joueur_label = tk.Label(self.main_frame, text="", font=('Courier New', 20), bg="#004d00", fg="white", width=45, height=2)
        self.main_joueur_label.pack(pady=(0, 5))
        self.total_joueur_label = tk.Label(self.main_frame, text="", font=('Arial Black', 24), bg="#003300", fg="cyan")
        self.total_joueur_label.pack()

        self.boutons_frame = tk.Frame(self.root, bg="#003300")
        self.boutons_frame.pack(pady=15)

        self.tirer_btn = tk.Button(self.boutons_frame, text="🃏 Tirer", command=self.tirer,
                                   font=("Arial", 16, "bold"), bg="#1a75ff", fg="white", width=12, state=tk.DISABLED)
        self.tirer_btn.grid(row=0, column=0, padx=10)

        self.rester_btn = tk.Button(self.boutons_frame, text="✋ Rester", command=self.rester,
                                    font=("Arial", 16, "bold"), bg="#ff4d4d", fg="white", width=12, state=tk.DISABLED)
        self.rester_btn.grid(row=0, column=1, padx=10)

        self.rejouer_btn = tk.Button(self.root, text="🎮 Jouer", command=self.nouvelle_partie,
                                     font=("Arial", 14), bg="gold", fg="black", width=14, state=tk.DISABLED)
        self.rejouer_btn.pack(pady=10)

        self.message_label = tk.Label(self.root, text="", font=("Arial", 18, "bold"), bg="#003300", fg="yellow")
        self.message_label.pack(pady=10)

        self.verifier_mise()

    def verifier_mise(self, event=None):
        try:
            mise = int(self.mise_entry.get())
            if mise <= 0:
                self.mise_erreur_label.config(text="Mise invalide")
                self.rejouer_btn.config(state=tk.DISABLED)
            elif mise > self.solde:
                self.mise_erreur_label.config(text="Vous n'avez pas assez de jetons")
                self.rejouer_btn.config(state=tk.DISABLED)
            else:
                self.mise_erreur_label.config(text="")
                self.rejouer_btn.config(state=tk.NORMAL)
        except ValueError:
            self.mise_erreur_label.config(text="Mise invalide")
            self.rejouer_btn.config(state=tk.DISABLED)

    def creer_paquet(self):
        cartes = list(cartes_valeurs.keys()) * 4
        random.shuffle(cartes)
        return cartes

    def piocher_carte(self):
        return self.paquet.pop()

    def calculer_main(self, main):
        total = sum(cartes_valeurs[carte] for carte in main)
        as_count = main.count("A")
        while total > 21 and as_count:
            total -= 10
            as_count -= 1
        return total

    def afficher_avec_animation(self, label, texte_final, delay=25):
        label.config(text="")
        def step(index=0):
            if index <= len(texte_final):
                label.config(text=texte_final[:index])
                self.root.after(delay, step, index + 1)
        step()

    def mise_a_jour_affichage(self, afficher_dealer=False):
        joueur_total = self.calculer_main(self.main_joueur)
        texte_joueur = f"{self.main_joueur}"
        self.afficher_avec_animation(self.main_joueur_label, texte_joueur)
        self.total_joueur_label.config(text=f"TOTAL : {joueur_total}")

        if afficher_dealer:
            dealer_total = self.calculer_main(self.main_dealer)
            texte_dealer = f"{self.main_dealer}  (Total: {dealer_total})"
        else:
            texte_dealer = f"[{self.main_dealer[0]}, '?']"
        self.afficher_avec_animation(self.main_dealer_label, texte_dealer)

        self.solde_label.config(text=f"💰 Solde : {self.solde} jetons")

    def tirer(self):
        self.main_joueur.append(self.piocher_carte())
        self.mise_a_jour_affichage()
        if self.calculer_main(self.main_joueur) > 21:
            self.fin_partie("❌ Vous avez dépassé 21. Le dealer gagne.", perdu=True)

    def rester(self):
        while self.calculer_main(self.main_dealer) < 17:
            self.main_dealer.append(self.piocher_carte())
        self.mise_a_jour_affichage(afficher_dealer=True)
        self.verifier_gagnant()

    def verifier_gagnant(self):
        joueur = self.calculer_main(self.main_joueur)
        dealer = self.calculer_main(self.main_dealer)

        if dealer > 21 or joueur > dealer:
            self.fin_partie("✅ Vous gagnez !", gagne=True)
        elif joueur < dealer:
            self.fin_partie("❌ Le dealer gagne.", perdu=True)
        else:
            self.fin_partie("🤝 Égalité.")

    def fin_partie(self, message, gagne=False, perdu=False):
        if gagne:
            self.solde += self.mise * 2
        elif perdu:
            pass

        if self.solde <= 0:
            self.solde += 100
            self.message_label.config(text="💸 Vous êtes ruiné ! +100 jetons offerts")

        self.tirer_btn.config(state=tk.DISABLED)
        self.rester_btn.config(state=tk.DISABLED)
        self.rejouer_btn.config(state=tk.DISABLED)
        self.mise_a_jour_affichage(afficher_dealer=True)

        self.message_label.config(text=message)
        self.root.after(5000, lambda: self.message_label.config(text=""))
        self.verifier_mise()

    def nouvelle_partie(self):
        try:
            mise = int(self.mise_entry.get())
            if mise <= 0 or mise > self.solde:
                self.mise_erreur_label.config(text="Mise invalide.")
                return
            else:
                self.mise_erreur_label.config(text="")
            self.mise = mise
        except ValueError:
            self.mise_erreur_label.config(text="Mise invalide.")
            return

        self.solde -= self.mise
        self.paquet = self.creer_paquet()
        self.main_joueur = [self.piocher_carte(), self.piocher_carte()]
        self.main_dealer = [self.piocher_carte(), self.piocher_carte()]
        self.tirer_btn.config(state=tk.NORMAL)
        self.rester_btn.config(state=tk.NORMAL)
        self.rejouer_btn.config(state=tk.DISABLED)
        self.mise_a_jour_affichage()
        self.message_label.config(text="")

if __name__ == "__main__":
    root = tk.Tk()
    app = BlackjackGUI(root)
    root.mainloop()
