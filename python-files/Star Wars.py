import time
import sys
import os

def slow_print(text, delay=0.05):
    """Druckt Text Buchstabe wie in einem Terminal mit einer Verzögerung."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')    

# Star Wars Intro
clear()
slow_print("************************************************", 0.002)
slow_print("*                                              *", 0.002)
slow_print("*              Star Wars Terminal!             *", 0.002)
slow_print("*                                              *", 0.002)
slow_print("************************************************", 0.002)
time.sleep(1)
clear()

slow_print("In einer weit, weit entfernten Galaxis....", 0.08)
time.sleep(1)
slow_print("Episode <3 - A New Love", 0.08)
time.sleep(1)
clear()

slow_print("Dies ist deine Mission, junger Padawan.", 0.06)
slow_print("Finde die geheime Botschaft deiner Jedi-Meisterin.", 0.06)
time.sleep(2)
slow_print("Möge die Macht mit dir sein!", 0.06)
clear()

password = input("Gib das geheime Passwort ein, um fortzufahren. (Tipp: Dein Lieblingscharakter): ")

while password.lower() != "Darth Maul".lower():
    slow_print("Falsches Passwort. Versuche es erneut.", 0.06)
    password = input("Passwort: ")

slow_print("Passwort akzeptiert. Willkommen, junger Padawan!", 0.06)
time.sleep(1)

slow_print("Übertrage geheime Nachricht...", 0.06)
time.sleep(2)
slow_print("Geheime Nachricht empfangen:", 0.06)
time.sleep(1)
clear()

slow_print("Möge die Macht mit dir sein.", 0.06)
slow_print("Und möge unsere Liebe stärker sein als das Imperium <3")
slow_print("Mission abgeschlossen.")
time.sleep(3)
clear()

slow_print("Nie wieder mache ich das...", 0.08)
time.sleep(3)

slow_print("Naja vielleicht doch irgendwann mal wieder...", 0.08)
slow_print("Ich liebe dich Peer <3", 0.1)
time.sleep(2)
clear()

# Herz in ASCII-Art
heart = [
    "  *****     *****  ",
    " *******   ******* ",
    "********* *********",
    " ***************** ",
    "  **************** ",
    "   *************  ",
    "    ***********   ",
    "     *********    ",
    "      *******     ",
    "       *****      ",
    "        ***       ",
    "         *        "
]

print("\n")
for line in heart:
    print(line.center(50))
    time.sleep(0.2)