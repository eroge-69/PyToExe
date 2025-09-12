import tkinter as tk
from tkinter import messagebox

# Українська літера → пояснення французькою
pronunciation = {
    "а": "Comme le 'a' français (papa).",
    "б": "Comme 'b' français (bon).",
    "в": "Comme 'v' français (vin).",
    "г": "Un son guttural, proche du 'r' ou de 'h' dans la gorge.",
    "ґ": "Comme 'g' français dur (gare).",
    "д": "Comme 'd' français (donner).",
    "е": "Comme 'è' français (mère).",
    "є": "Se prononce 'yè'. Ou sinon й + e.",
    "ж": "Comme 'j' français (jour).",
    "з": "Comme 'z' français (zéro).",
    "и": "Voyelle entre 'i' et 'u', n’existe pas en français mais on peut dire é/// tres aigu.",
    "і": "Comme 'i' français (si)",
    "ї": "Se prononce 'yi' (comme 'y' + 'i')ou sinon й + i.",
    "й": "Comme 'y' en français (payer). Doux.",
    "к": "Comme 'k' français (kangourou).",
    "л": "Comme 'l' dur français (lumière) pas comme dans 'la'.",
    "м": "Comme 'm' français (maman).",
    "н": "Comme 'n' français (non).",
    "о": "Comme 'o' français (porte).",
    "п": "Comme 'p' français (papa).",
    "р": "R roulé, comme en espagnol, pas comme le 'r' français.",
    "с": "Comme 's' français (soleil).",
    "т": "Comme 't' français (terre).",
    "у": "Comme 'ou' français (tout).",
    "ф": "Comme 'f' français (fête).",
    "х": "comme h mais qui se prononce",
    "ц": "Comme 'ts', proche du 'z' allemand (Zvolf).",
    "ч": "Comme 'ch' anglais (chocolate).",
    "ш": "Comme 'ch' français (chat).",
    "щ": "Se prononce 'shch' anglais (comme 'шч' ou 'шь').",
    "ь": "Signe doux : rend doux la consonne précédente.",
    "ю": "Comme 'you' anglais, 'y' + 'ou' ou sinon й + у.",
    "я": "Comme 'ya' (y + a) ou sinon й + а."
}

# Функція при натисканні
def show_pronunciation(letter):
    info = pronunciation.get(letter, "Pas d'information.")
    messagebox.showinfo("infos", f"{letter} → {info}")

# Вікно
root = tk.Tk()
root.title("Clavier ukrainien")

# Робимо кілька рядків (як клавіатура ЙЦУКЕН)
rows = [
    "абвгґдеєжзи",
    "іїйклмнопрс",
    "туфхцчшщьюя"
]

for row in rows:
    frame = tk.Frame(root)
    frame.pack()
    for letter in row:
        if letter in pronunciation:
            btn = tk.Button(frame, text=letter, width=4, height=2,
                            command=lambda l=letter: show_pronunciation(l))
            btn.pack(side="left", padx=2, pady=2)

root.mainloop()
