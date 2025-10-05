import random
import pyperclip
import os

# Beispielhafte große Liste männlicher Vornamen
vornamen = [
    "Paul","Peter","Michael","David","John","Robert","James","Mark","Thomas","Daniel",
    "Alexander","Benjamin","Christopher","Christian","Stefan","Patrick","Simon","Felix",
    "Lucas","Niklas","Jan","Lukas","Philipp","Tobias","Matthias","Jonathan","Julian",
    "Dennis","Florian","Andreas","Sebastian","Kevin","Moritz","Maximilian","Leon","Nico",
    "Raphael","Fabian","Dominik","Martin","Erik","Sven","Jens","Kai","Marc","Oliver"
]

# Beispielhafte große Liste Nachnamen
nachnamen = [
    "Hoffman","Müller","Schmidt","Schneider","Fischer","Weber","Meyer","Wagner","Becker","Koch",
    "Bauer","Richter","Klein","Wolf","Neumann","Schwarz","Zimmermann","Braun","Krüger","Hofmann",
    "Hartmann","Lange","Schmitt","Werner","Schmitz","Krause","Meier","Lehmann","Schmid","Schulz",
    "Mayer","Maier","Köhler","Herrmann","König","Walter","Frank","Fuchs","Berg","Lorenz"
]

# Liste der PD-Ränge
pd_ranks = [
    "Stv Chief",
    "Chief",
    "Leutnant",
    "Sergeant 2",
    "Sergeant",
    "Rookie",
    "Azubi",
    "Officer",
    "Detective"
]

def clear_screen():
    os.system("cls")  # Für Windows
    # os.system("clear")  # Für Linux/Mac, falls nötig

def generate_option1():
    type_choice = random.choice(["DOJ", "MEDIC"])
    vorname = random.choice(vornamen)
    nachname = random.choice(nachnamen)
    name = f"{type_choice} | Prof .Dr {vorname} {nachname}"
    pyperclip.copy(name)
    print(f"{name} wurde in die Zwischenablage kopiert!")

def generate_option2():
    vorname = random.choice(vornamen)
    nachname = random.choice(nachnamen)
    rank = random.choice(pd_ranks)
    name = f"PD {rank} | {vorname} {nachname}"
    pyperclip.copy(name)
    print(f"{name} wurde in die Zwischenablage kopiert!")

def main():
    while True:
        clear_screen()
        print("Wähle eine Option:")
        print("1 - DOJ/MEDIC Namen")
        print("2 - PD | Vor- und Nachname mit Rang")
        print("0 - Beenden")
        choice = input("Option: ")

        clear_screen()
        if choice == "1":
            generate_option1()
        elif choice == "2":
            generate_option2()
        elif choice == "0":
            print("Programm beendet.")
            break
        else:
            print("Ungültige Auswahl! Bitte 1, 2 oder 0 eingeben.")
        input("\nDrücke Enter, um fortzufahren...")  # Pause, damit man den kopierten Namen sehen kann

if __name__ == "__main__":
    main()
