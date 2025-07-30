
import random

def würfelwurf():
    w1 = random.randint(1,50)
    w2 = random.randint(1,50)
    return w1 + w2

def portionen_bestimmen(summe):
    if 2 <= summe <= 26:
        return 1
    elif 27 <= summe <= 56:
        return 2
    elif 57 <= summe <= 76:
        return 3
    elif 77 <= summe <= 91:
        return 4
    elif 92 <= summe <= 100:
        return 5
    else:
        return 1  # Fallback

def zufällige_einnahmeart():
    arten = [
        "Direkt aus einem Becher",
        "Mit einer Spritze",
        "In warmen Nudeln",
        "Auf einer Pizza",
        "Auf einem Brot",
        "In Pudding untergehoben",
        "In einem Milchbrötchen versteckt",
        "In Toast eingeknetet",
        "In Nudelsalat untergemischt",
        "Mit Keksen kombiniert"
    ]
    return random.choice(arten)

def main():
    print("CUMPLAY - Schreib /start um eine Runde zu beginnen, /exit zum Beenden.")
    while True:
        user = input("> ").strip().lower()
        if user == "/start":
            wurf = würfelwurf()
            portionszahl = portionen_bestimmen(wurf)
            art = zufällige_einnahmeart()
            print(f"Würfelwurf: {wurf} → Portionen: {portionszahl}")
            print(f"Einnahmeart: {art}")
            print()
        elif user == "/exit":
            print("Bis zum nächsten Mal!")
            break
        else:
            print("Unbekannter Befehl. Bitte /start oder /exit eingeben.")

if __name__ == "__main__":
    main()
