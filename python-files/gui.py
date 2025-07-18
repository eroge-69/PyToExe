import tkinter as tk
from tkinter import messagebox, simpledialog, Scrollbar, Canvas
from PIL import Image, ImageTk
import pygame, os, base64, json, string

pygame.mixer.init()
CARD_SIZE = (100, 140)
ROLE_IMG_SIZE = (600, 400)
selected_cards = []
murderer_count = 2

CARD_MAP = {
    'Murderer': 'a',
    'Neighbor': 'b',
    'Police': 'c',
    'Fortune_Teller': 'd',
    'Burglar': 'e',
    'Mischief': 'f',
    'Forgotten': 'g',
    'Night_Shift': 'h',
    'Locksmith': 'i',
    'Lock': 'j',
    'Dead': 'k'
}

wake_order = [
    "Police", "Fortune_Teller", "Mischief", "Forgotten",
    "Burglar", "Locksmith", "Night_Shift", "Neighbor", "Murderer"
]

card_abilities = {
    "Burglar": "Steals one other player's card and looks at it. May swap once.",
    "Police": "Sees who the Mischief and the Burglar are.",
    "Mischief": "Swaps two players' cards without revealing.",
    "Forgotten": "Swaps their card with a center card and does not look.",
    "Fortune_Teller": "Sees the role of one card before dawn.",
    "Night_Shift": "Looks at their card at the end of the night.",
    "Locksmith": "Locks one card (not self) to prevent changes or death.",
    "Murderer": "Picks who to eliminate using the 'Dead' card. If two, must agree.",
    "Lock": "Card used by the Locksmith to block another role.",
    "Dead": "Marker for who is eliminated — no action or vote.",
    "Neighbor": "Each Neighbor sees the other if paired correctly."
}

excluded_cards = ["Dead", "Lock"]

def enforce_dependencies():
    if "Murderer" in selected_cards and "Dead" not in selected_cards:
        selected_cards.append("Dead")
    if "Locksmith" in selected_cards and "Lock" not in selected_cards:
        selected_cards.append("Lock")

def show_recommended_players():
    total_cards = len([c for c in selected_cards if c not in excluded_cards]) + 3
    recommended_label.config(text=f"Recommended players: {total_cards - 3}")

def update_card_gallery():
    for widget in gallery_frame_inner.winfo_children():
        widget.destroy()
    for filename in sorted(os.listdir("cards")):
        if filename.endswith(".png"):
            card = filename[:-4]
            if card in excluded_cards:
                continue
            img = Image.open(f"cards/{filename}").resize(CARD_SIZE)
            img_tk = ImageTk.PhotoImage(img)
            frame = tk.Frame(gallery_frame_inner, bg='black')
            frame.pack(side="left", padx=5)
            btn = tk.Button(frame, image=img_tk, bg='black', command=lambda c=card: toggle_card(c))
            btn.image = img_tk
            btn.pack()
            label = tk.Label(frame, text=card.replace("_", " "), fg='white', bg='black',
                             cursor="hand2", font=('Courier', 10, 'underline'))
            label.pack()
            label.bind("<Button-1>", lambda e, c=card: show_card_info_popup(c))

def toggle_card(card):
    global murderer_count
    if card == "Murderer":
        count = simpledialog.askinteger("Murderer", "How many Murderers in this game? (1 or 2)", minvalue=1, maxvalue=2)
        if count:
            murderer_count = count
            selected_cards[:] = [c for c in selected_cards if c != "Murderer"]
            selected_cards.extend(["Murderer"] * murderer_count)
    elif card == "Neighbor":
        if selected_cards.count("Neighbor") < 2:
            selected_cards.extend(["Neighbor"] * (2 - selected_cards.count("Neighbor")))
    elif card in selected_cards:
        selected_cards.remove(card)
    else:
        selected_cards.append(card)
    enforce_dependencies()
    update_deck_display()
    show_recommended_players()

def update_deck_display():
    for widget in deck_frame.winfo_children():
        widget.destroy()
    for card in selected_cards:
        if card in excluded_cards:
            continue
        frame = tk.Frame(deck_frame, bg='black')
        frame.pack(side="left", padx=5)
        path = f"cards/{card}.png"
        if os.path.exists(path):
            img = Image.open(path).resize(CARD_SIZE)
            img_tk = ImageTk.PhotoImage(img)
            btn = tk.Button(frame, image=img_tk, bg='black', command=lambda c=card: toggle_card(c))
            btn.image = img_tk
            btn.pack()
        label = tk.Label(frame, text=card, fg='white', bg='black',
                         cursor="hand2", font=('Courier', 10, 'underline'))
        label.pack()
        label.bind("<Button-1>", lambda e, c=card: show_card_info_popup(c))

def show_card_info_popup(card):
    info = card_abilities.get(card, "No ability listed.")
    win = tk.Toplevel(root)
    win.configure(bg='black')
    win.title(card)
    tk.Label(win, text=card, font=('Courier', 16, 'bold'), fg='red', bg='black').pack(pady=10)
    tk.Label(win, text=info, wraplength=360, fg='white', bg='black', font=('Courier', 12)).pack(pady=10)

def validate_deck():
    if len(selected_cards) < 6:
        messagebox.showwarning("Too Few Cards", "Deck must have at least 6 cards.")
        return False
    if "Murderer" not in selected_cards:
        messagebox.showwarning("No Murderer", "Deck must include the Murderer.")
        return False
    if selected_cards.count("Neighbor") == 1:
        messagebox.showwarning("Neighbors Error", "Neighbors must appear in pairs.")
        return False
    return True

def play_audio(role):
    lookup = {"Neighbor": "Neighbors", "Intro": "Intro", "Outro": "Outro"}
    filename = lookup.get(role, role) + ".mp3"
    path = f"audio/{filename}"
    if os.path.exists(path):
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()

def show_role(role):
    label = f"{role} ({murderer_count})" if role == "Murderer" and murderer_count == 2 else role
    role_label.config(text=label, fg='white', font=("Courier", 24), image='')

def start_night_phase():
    if not validate_deck():
        return
    play_audio("Intro")
    win = tk.Toplevel(root)
    win.geometry("800x500")
    win.configure(bg='black')
    win.title("Night Phase")
    global role_label
    role_label = tk.Label(win, bg='black')
    role_label.pack()

    def next_role(i=0):
        if i >= len(wake_order):
            play_audio("Outro")
            role_label.config(text="🌅 Dawn breaks. Let the deadly decisions begin.",
                              fg='white', font=("Courier", 20), image='')
            return

        role = wake_order[i]
        show_role(role)
        if role in ["Neighbor", "Murderer"] and wake_order[:i].count(role) > 0:
            pass
        else:
            play_audio(role)
        next_btn.config(command=lambda: next_role(i + 1))

    next_btn = tk.Button(win, text="Next Role", bg='gray20', fg='white', font=("Courier", 12))
    next_btn.pack(pady=10)
    next_role()

def encode_preset():
    letter_counts = {}
    for card in selected_cards:
        if card in CARD_MAP:
            key = CARD_MAP[card]
            letter_counts[key] = letter_counts.get(key, 0) + 1

    code = ''
    for letter, count in letter_counts.items():
        if count == 1:
            code += letter
        elif count == 2:
            code += letter.upper()
    messagebox.showinfo("Short Code", code)

def decode_preset():
    reverse_map = {v: k for k, v in CARD_MAP.items()}
    reverse_map.update({v.upper(): k for k, v in CARD_MAP.items()})

    global selected_cards, murderer_count
    code = simpledialog.askstring("Preset Code", "Enter code:")
    if not code:
        return

    selected_cards.clear()
    murderer_count = 1

    for char in code:
        card = reverse_map.get(char)
        if card:
            selected_cards.append(card)
            if card == "Murderer" and char.isupper():
                selected_cards.append(card)
                murderer_count = 2
    enforce_dependencies()
    update_deck_display()
    show_recommended_players()

def load_preset_by_players(n):
    presets = {
        6: ["Murderer", "Neighbor", "Neighbor", "Police", "Fortune_Teller", "Burglar"],
        7: ["Murderer", "Neighbor", "Neighbor", "Police", "Fortune_Teller", "Burglar", "Forgotten"],
        8: ["Murderer", "Neighbor", "Neighbor", "Police", "Fortune_Teller", "Mischief", "Forgotten", "Burglar"],
        9: ["Murderer", "Neighbor", "Neighbor", "Police", "Fortune_Teller", "Mischief", "Forgotten", "Burglar", "Night_Shift"]
    }
    deck = presets.get(n, [])
    selected_cards.clear()
    selected_cards.extend(deck)
    enforce_dependencies()
    update_deck_display()
    show_recommended_players()

def launch_tutorial():
    steps = [
        "💡 Each player receives one face-down card. DO NOT deal 'Dead' or 'Lock'.",
        "🃏 Place three random extra cards in the center. Put 'Dead' and 'Lock' nearby.",
        "🙈 Players secretly look at their own card. No peeking!",
        "🌙 Roles wake in sequence during the night and perform actions.",
        "🔍 Press 'Start Night Phase' to begin. You'll manually step through roles.",
        "🧠 Tap each card name to see its ability. No need to memorize everything.",
        "🔪 Murderers must agree to eliminate one player. Use the 'Dead' card.",
        "🧙 Fortune Teller sees one card. Burglar may steal and swap once.",
        "🔐 Locksmith locks another role. That role becomes untouchable.",
        "😵 Mischief swaps two player cards. Forgotten swaps with a center card.",
        "👥 Neighbors act as a pair. They see each other. Only one audio plays.",
        "🌅 At dawn, players discuss and vote. Dead players don't vote.",
        "🎉 Customize the deck or load a preset. Have fun!"
    ]

    win = tk.Toplevel(root)
    win.title("Game Tutorial")
    win.configure(bg='black')
    win.geometry("700x500")

    tutorial_text = tk.Label(win, text=steps[0], wraplength=640,
                             fg='white', bg='black', font=('Courier', 14), justify='left')
    tutorial_text.pack(pady=40)

    def next_step(i=1):
        if i < len(steps):
            tutorial_text.config(text=steps[i])
            next_btn.config(command=lambda: next_step(i + 1))
        else:
            win.destroy()

    next_btn = tk.Button(win, text="Next", font=('Courier', 12),
                         bg='gray20', fg='white', command=lambda: next_step(1))
    next_btn.pack()

# === GUI ===
root = tk.Tk()
root.title("Deadly Decisions – Online")
root.geometry("1150x800")
root.configure(bg='black')

ctrl_frame = tk.Frame(root, bg='black')
ctrl_frame.pack(pady=10)

tk.Button(ctrl_frame, text="Custom Mode", command=update_card_gallery,
          bg='gray20', fg='white', font=('Courier', 12)).pack(side="left", padx=5)

tk.Button(ctrl_frame, text="Use Preset Code", command=decode_preset,
          bg='gray25', fg='white', font=('Courier', 12)).pack(side="left", padx=5)

tk.Button(ctrl_frame, text="Generate Code", command=encode_preset,
          bg='gray25', fg='white', font=('Courier', 12)).pack(side="left", padx=5)

tk.Button(ctrl_frame, text="Start Night Phase", command=start_night_phase,
          bg='darkgreen', fg='white', font=('Courier', 12)).pack(side="left", padx=5)

for count in range(6, 10):
    tk.Button(ctrl_frame, text=f"{count} Players",
              command=lambda c=count: load_preset_by_players(c),
              bg='gray25', fg='white', font=('Courier', 10)).pack(side="left", padx=2)

recommended_label = tk.Label(ctrl_frame, text="", fg='lightblue',
                             bg='black', font=('Courier', 10, 'italic'))
recommended_label.pack(side="left", padx=15)

gallery_canvas = Canvas(root, bg="black", height=180)
gallery_canvas.pack(fill="x")
gallery_scroll = Scrollbar(root, orient="horizontal", command=gallery_canvas.xview)
gallery_scroll.pack(fill="x")
gallery_canvas.configure(xscrollcommand=gallery_scroll.set)

gallery_frame_inner = tk.Frame(gallery_canvas, bg="black")
gallery_canvas.create_window((0, 0), window=gallery_frame_inner, anchor="nw")
gallery_frame_inner.bind("<Configure>", lambda e: gallery_canvas.configure(
    scrollregion=gallery_canvas.bbox("all")))

deck_frame = tk.Frame(root, bg='black')
deck_frame.pack(pady=10)

update_card_gallery()
show_recommended_players()
launch_tutorial()
root.mainloop()