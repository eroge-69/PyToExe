
import os
import pygame
import keyboard

# Instellingen
LIJN_NAAM = "LijnA"  # Pas aan naar gewenste lijnmap
MAP_PAD = os.path.join("mp3", LIJN_NAAM)

# Laad alle mp3-bestanden gesorteerd
mp3_bestanden = sorted([f for f in os.listdir(MAP_PAD) if f.endswith(".mp3")])

# Initialiseer pygame mixer
pygame.mixer.init()

index = 0
print("Metro-omroepsysteem actief. Druk op ~ voor volgende mp3. ESC om te stoppen.")

try:
    while True:
        if keyboard.is_pressed('`'):  # De ~ toets (backtick)
            if index < len(mp3_bestanden):
                bestand = os.path.join(MAP_PAD, mp3_bestanden[index])
                print(f"Afspelen: {bestand}")
                pygame.mixer.music.load(bestand)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pass  # Wacht tot het geluid klaar is
                index += 1
            else:
                print("Einde van de lijn.")
            while keyboard.is_pressed('`'):
                pass  # Voorkom dubbel indrukken
        if keyboard.is_pressed('esc'):
            print("Programma gestopt.")
            break
except KeyboardInterrupt:
    print("Afgebroken.")
