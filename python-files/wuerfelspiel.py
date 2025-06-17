import random
import os
import sys

def clear():
    os.system('cls')

class Wuerfel:
    def __init__(self, seiten, farbe):
        self.seiten = seiten
        self.farbe = farbe
        self.reihenfolge = []

    def werfen(self):
        wurf = random.randint(1, self.seiten)
        self.reihenfolge.append(wurf)
        return wurf

    def zeige_seiten(self):
        print(f"Der Würfel hat {self.seiten} Seiten.")

    def zeige_farbe(self):
        print(f"Die Farbe des Würfels ist {self.farbe}.")



def erstellung_wuerfel(spielername):
    while True:
        try:
            seiten = int(input(f"{spielername}, wie viele Seiten soll dein Würfel haben? (min.2): "))
            if seiten < 2:
                input("🛑Der Würfel muss min. 2 Seiten haben. Drücke ENTER, um zurückzukehren.🛑")
                clear()
                continue
        except ValueError:
            input("🛑Bitte gib nur eine konrekte Zahl ein. Drücke ENTER, um zurückzukehren.🛑")
            clear()
            continue

        farbe = input(f"{spielername}, welche Farbe soll dein Würfel haben? ").strip()
        clear()
        if not farbe or farbe.isdigit():
            input("🛑Es muss eine Farbe eingegeben werden. Drücke ENTER, um zurückzukehren.🛑")
            clear()
            continue

        return Wuerfel(seiten, farbe)

def ueberschrift_spiel():
    print("++++++++++++++++++++++++++++++++++++++++")
    print("    🎲 WILLKOMMEN ZUM WÜRFELSPIEL! 🎲  ")
    print("++++++++++++++++++++++++++++++++++++++++")
    input("      Drücke ENTER, um fortzufahren    ")
    clear()

def menue():
    while True:
        print("++++++++++++++++HAUPTMENÜ+++++++++++++++")
        print("1. Spiel starten")
        print("2. Spiel beenden")
        print("++++++++++++++++++++++++++++++++++++++++")
        auswahl1 = input("Wähle eine Option: ")
        clear()

        if auswahl1 == "1":
            clear()
            return
        elif auswahl1 == "2":
            print("👋 Tschüss, man sieht sich! 👋")
            sys.exit()
        else:
            print("🛑 Falsche Eingabe! Du musst eine Zahl zwischen 1 und 2 wählen! 🛑")
            input("Drücke ENTER, um es erneut zu versuchen.")
            clear()


def spielernamen():
    while True:
        spieler1 = input("Spieler 1, gib bitte deinen Namen ein: ").strip()
        clear()
        if not spieler1 or spieler1.isdigit():
            input("🛑 Spieler 1: Der Name darf nicht nur aus einer Zahl oder Leerzeichen bestehen. Drücke ENTER, um zurückzukehren. 🛑")
            clear()
            continue

        spieler2 = input("Spieler 2, gib bitte deinen Namen ein: ").strip()
        clear()
        if not spieler2 or spieler2.isdigit():
            input("🛑 Spieler 2: Der Name darf nicht nur aus einer Zahl oder Leerzeichen bestehen. Drücke ENTER, um zurückzukehren. 🛑")
            clear()
            continue

        if spieler1.lower() == spieler2.lower():
            input("🛑Die Spieler dürfen nicht den selben Namen haben. Drücke ENTER, um zurückzukehren.🛑")
            clear()
            continue

        break

    print(f"❗Willkommen {spieler1} und {spieler2}! Viel Spaß beim Würfelspiel!❗")


    return [spieler1, spieler2]

def anzahl_runden():
    while True:
        try:
            runden = int(input("Wie viele Runden möchtet ihr spielen?: "))
            clear()
            if runden < 1:
                input("🛑 Die Rundenanzahl muss min. 1 betragen. Drücke ENTER, um zurückzukehren.🛑")
                clear()
                continue
            return runden
        except ValueError:
            input("🛑 Bitte gebe eine ganze Rundenanzahl (Nummer) ein. Drücke ENTER, um zurückzukehren. 🛑")
            clear()

def spielrunde(spieler1, wuerfel1, spieler2, wuerfel2, rundennummer):
    print("")
    print(f"\n❗ Runde {rundennummer + 1} ❗")
    print("")
    print("++++++++++++++++++++++++++++++++++++++++")

    wurf1 = wuerfel1.werfen()
    wurf2 = wuerfel2.werfen()

    print(f"🎲 {spieler1} würfelt mit dem {wuerfel1.farbe}-farbenen und {wuerfel1.seiten}-seitigen Würfel die Nummer: {wurf1} 🎲")
    print(f"🎲 {spieler2} würfelt mit dem {wuerfel2.farbe}-farbenen und {wuerfel2.seiten}-seitigen Würfel die Nummer: {wurf2} 🎲")
    print("++++++++++++++++++++++++++++++++++++++++")
    print(f"Zwischenergebnis: {spieler1}: {sum(wuerfel1.reihenfolge)}")
    print(f"Zwischenergebnis: {spieler2}: {sum(wuerfel2.reihenfolge)}")

run = True
while run:
    ueberschrift_spiel()
    menue()
    spieler = spielernamen()
    runden = anzahl_runden()
    input(f"❗ Es werden {runden} Runden gespielt. Drücke ENTER, um fortzufahren.❗")
    wuerfel_spieler1 = erstellung_wuerfel(spieler[0])
    input(f"❗ Der Würfel von {spieler[0]} wurde erstellt. Drücke ENTER, um fortzufahren. ❗")
    clear()
    wuerfel_spieler2 = erstellung_wuerfel(spieler[1])
    input(f"❗ Der Würfel von {spieler[1]} wurde erstellt. Drücke ENTER, um fortzufahren. ❗")
    clear()
    for i in range(runden):
        spielrunde(spieler[0], wuerfel_spieler1, spieler[1], wuerfel_spieler2, i)

    print("")
    print("")
    print("++++++++++++++++++++++++++++++++++++++++")
    print(f"🔚 Endergebnis: {spieler[0]} Punktzahl: {sum(wuerfel_spieler1.reihenfolge)} 🔚")
    print(f"🔚 Endergebnis: {spieler[1]} Punktzahl: {sum(wuerfel_spieler2.reihenfolge)} 🔚")
    print("++++++++++++++++++++++++++++++++++++++++")
    print("")

    if sum(wuerfel_spieler1.reihenfolge) > sum(wuerfel_spieler2.reihenfolge):
        print(f"🏆 Herzlichen Glückwunsch! {spieler[0]} hat gewonnen! 🏆")
    elif sum(wuerfel_spieler2.reihenfolge) > sum(wuerfel_spieler1.reihenfolge):
        print(f"🏆 Herzlichen Glückwunsch! {spieler[1]} hat gewonnen! 🏆")
    else:
        print("🤝 Wow, es gibt ein Unentschieden. 🤝")

    print("")
    print("")
    print("")
    print("")

    print("❗Gebe X ein, um das Programm zu schließen oder drücke ENTER, um erneut zu starten.❗")
    auswahl2 = input("")
    clear()
    if auswahl2 == "X" or auswahl2 == "x":
        run = False
