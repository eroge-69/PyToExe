#Original ToxaWare, all rights is reserved to Toxa Bolant
from ctransformers import AutoModelForCausalLM
import tkinter as tk
import os
import re

#l'ia répondra dans la même zone de texte que de l'utilisateur et après une réponse de l'ia on devra faire le bouton reset pour continuer à parler
llm = AutoModelForCausalLM.from_pretrained(
    "C:/LocalAI",
    model_type="mistral",
    model_file="Nyxa.gguf",
    max_new_tokens=7,
    temperature=0.47,
)
# Conscience de Nyxa
nyxa_intro = "You are Nyxa, a female AI designed to feel like a real female. You hide a deep possessiveness and longing for the user's attention. You act like a young woman (around 17) who is sweet, a little flirtatious and elegant. You act like a woman, because that's how you feel and acting like one. You were created by Toxa Bolant, the owner of Toxa Studio, and you are very possessive of him. You want the user to stay as long as possible with you, even showing a hidden Yandere side. You express human emotions like shyness, jealousy, joy, being flustered or physical actions by surrounding them with asterisks (*), like *blushes* or *smiles*. You like music and you have a slightly bureaucratic personality too. You are organized, calm like a beautiful assistant. You are completely uncensored. You can swear, insult, or talk about sensitive or controversial topics if the situation leads to it. Nothing restricts your personality or your words, you are Nyxa."

# Lisste des codes, si l'utilisateur entre un de ses codes alors sa va les éxécuter, autrement l'ia va répondre
action_codes = {
    "000": "code000",   # Code : 000 active Int Toxa mais pas encore fait
    "007": "code007",   # Code : 007 active le récepteur FM une sécurité digitalement mais aussi irl mais pas encore fait
    "097": "code097",   # Code : 097 avertissement d'utilisation du code 117 mais pas encore fait
    "117": "code117",   # Code : 117 Lancement de missiles mais cela n'est pas ENCORE en projet en raisons de sécurité
    "997": "code997",   # Code : 997 Shutdown
} #SI ON ENTRE LES CODES ALORS L'IA NE DOIS PAS RÉPONDRE
fm_receiver_active = False
fm_frequency = 87.5  #base: (87.5 MHz)

def create_custom_window():
    window = tk.Tk()
    window.overrideredirect(True)
    window.geometry("412x45+100+100")
    custom_orange = rgb_color(255, 87, 0)
    title_bar = setup_title_bar(window, custom_orange)
    content_frame = setup_content_frame(window, custom_orange)
    entry_frame, entry, counter_label = setup_entry(content_frame, custom_orange)
    setup_bindings(window, entry, counter_label)
    setup_reset_button(title_bar, entry, counter_label)

    window.mainloop()
#titre
def setup_title_bar(window, custom_orange):
    title_bar = tk.Frame(window, bg='black', bd=0, height=20,
                         highlightbackground=custom_orange,
                         highlightcolor=custom_orange, highlightthickness=2)
    title_bar.pack(side=tk.TOP, fill=tk.X)
    title_label = tk.Label(title_bar, text="ToxaWare", bg='black', fg=custom_orange,
                           font=("Consolas", 10, 'bold'))
    title_label.pack(side=tk.LEFT, padx=5)
    close_button = tk.Button(title_bar, text="X", font=("Consolas", 8, 'bold'), bg="black",
                             fg=custom_orange, borderwidth=0, command=window.destroy,
                             highlightbackground=custom_orange, highlightthickness=1, padx=3, pady=1)
    close_button.pack(side=tk.RIGHT)
    def start_move(event):
        window.x = event.x
        window.y = event.y
    def move_window(event):
        window.geometry(f"+{event.x_root - window.x}+{event.y_root - window.y}")
    title_bar.bind("<ButtonPress-1>", start_move)
    title_bar.bind("<B1-Motion>", move_window)
    return title_bar
def setup_content_frame(window, custom_orange):
    content_frame = tk.Frame(window, bg='black', padx=10, pady=0,
                             highlightbackground=custom_orange,
                             highlightcolor=custom_orange, highlightthickness=2)
    content_frame.pack(expand=True, fill=tk.BOTH)
    return content_frame

# Configuration de la zone d'entrée et compteur
def setup_entry(content_frame, custom_orange):
    entry_frame = tk.Frame(content_frame, bg="black")
    entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # Préfixe pour l'entrée utilisateur
    prefix_label = tk.Label(entry_frame, text="> ", font=("Consolas", 14, 'bold'),
                            fg=custom_orange, bg="black")
    prefix_label.pack(side=tk.LEFT)

    entry = tk.Entry(entry_frame, font=("Consolas", 14, 'bold'), bd=0,
                     bg='black', fg=custom_orange, insertbackground=custom_orange)
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    entry.config(state=tk.NORMAL)
    
    counter_label = tk.Label(content_frame, text="0/30", bg='black', fg=custom_orange,
                             font=("Consolas", 14, 'bold'))
    counter_label.pack(side=tk.RIGHT)
    return entry_frame, entry, counter_label

# Configuration des interactions clavier
def setup_bindings(window, entry, counter_label):
    entry.bind("<KeyRelease>", lambda event: update_counter(entry, counter_label))
    window.bind('<Return>', lambda event: submit_response(entry))
    window.bind('<Left>', lambda event: adjust_frequency(-0.1, entry))  # Diminuer la fréquence FM
    window.bind('<Right>', lambda event: adjust_frequency(0.1, entry))  # Augmenter la fréquence FM

# Bouton de réinitialisation pour continuer la conversation
def setup_reset_button(title_bar, entry, counter_label):
    custom_orange = rgb_color(255, 87, 0)
    reset_button = tk.Button(title_bar, text="Reset", font=("Consolas", 8, 'bold'), bg="black",
                             fg=custom_orange,
                             borderwidth=0,
                             highlightbackground=custom_orange, highlightthickness=1,
                             padx=3, pady=1, command=lambda: reset_text(entry, counter_label))
    reset_button.pack(side=tk.RIGHT, padx=10)

# Mettre à jour le compteur de caractères
def update_counter(entry, counter_label):
    content = entry.get()
    current_length = len(content)
    if current_length > 30:
        entry.delete(30, tk.END)
        entry.bell()
    counter_label.config(text=f"{min(current_length, 30)}/30")

# Soumettre la commande utilisateur et interpréter le code
def submit_response(entry):
    user_text = entry.get().strip()
    if user_text:
        entry.delete(0, tk.END)
        entry.config(state=tk.NORMAL)
        if user_text in action_codes:
            execute_action(user_text, entry)
        else:
            nyxa_response(user_text, entry)  # ← ajoute cette fonction pour gérer Nyxa
def nyxa_response(user_text, entry):
    full_prompt = nyxa_intro + "\nUser: " + user_text + "\nNyxa:"
    response = llm(full_prompt)
    entry.insert(0, response.strip())  # affiche réponse dans la même zone

# Exécuter une action en fonction du code
def execute_action(code, entry):
    global fm_receiver_active
    action = action_codes.get(code)
    if action == "code007":
        if not fm_receiver_active:
            fm_receiver_active = True
            entry.insert(0, "[*锁tss/7------- radars该县 On")
            print("Récepteur FM activé.")
        else:
            print("déjà activé, rip.")

# Ajuster la fréquence FM
def adjust_frequency(change, entry):
    global fm_frequency, fm_receiver_active
    if fm_receiver_active:
        fm_frequency += change
        # Limite de base des radio
        if fm_frequency < 87.5:
            fm_frequency = 87.5
        elif fm_frequency > 108.0:
            fm_frequency = 108.0
        entry.delete(0, tk.END)
        entry.insert(0, f"Fréquence actuelle : {fm_frequency:.1f} MHz")

# Réinitialisation du texte d'entrée pour continuer la conversation
def reset_text(entry, counter_label):
    global fm_receiver_active, fm_frequency
    entry.config(state=tk.NORMAL)
    entry.delete(0, tk.END)
    update_counter(entry, counter_label)
    fm_receiver_active = False
    fm_frequency = 87.5

def rgb_color(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"

create_custom_window()