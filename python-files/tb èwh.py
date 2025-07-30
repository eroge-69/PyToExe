import pyautogui
pyautogui.FAILSAFE = False
import threading
import tkinter as tk
import time
import math
from pynput import mouse

running = False
seuil_pixels = 5
zone_size = 19

# Couleur cible rouge foncé : RGB(121, 9, 9)
target_color = (121, 9, 9)
distance_max = 60  # tolérance (plus grand = plus permissif)

# Variable pour savoir si le bouton trigger est pressé
trigger_pressed = False

def couleur_proche(r, g, b, cible=target_color, dist_max=distance_max):
    dist = math.sqrt((r - cible[0])**2 + (g - cible[1])**2 + (b - cible[2])**2)
    return dist <= dist_max

def detection_zone():
    global running, trigger_pressed
    screen_w, screen_h = pyautogui.size()
    centre_x, centre_y = screen_w // 2, screen_h // 2

    while running:
        if trigger_pressed:
            try:
                left = centre_x - zone_size // 2
                top = centre_y - zone_size // 2
                screenshot = pyautogui.screenshot(region=(left, top, zone_size, zone_size))

                count_pixels = 0
                for x in range(zone_size):
                    for y in range(zone_size):
                        r, g, b = screenshot.getpixel((x, y))
                        if couleur_proche(r, g, b):
                            count_pixels += 1
                        if count_pixels >= seuil_pixels:
                            pyautogui.click(centre_x, centre_y)
                            print(f"Clic déclenché - pixels proches rouges détectés : {count_pixels}")
                            break
                    if count_pixels >= seuil_pixels:
                        break

                if count_pixels < seuil_pixels:
                    print(f"Pixels rouges détectés : {count_pixels}")

            except Exception as e:
                print(f"Erreur dans la détection : {e}")
                running = False

        time.sleep(0.001)

def on_click(x, y, button, pressed):
    global trigger_pressed
    if button == mouse.Button.x2:  # bouton forward (côté droit)
        trigger_pressed = pressed

def start():
    global running
    if not running:
        running = True
        threading.Thread(target=detection_zone, daemon=True).start()
        print("Triggerbot rouge lancé (maintenir le bouton latéral droit pour détecter).")

def stop():
    global running, trigger_pressed
    running = False
    trigger_pressed = False
    print("Triggerbot arrêté.")

fenetre = tk.Tk()
fenetre.title("Triggerbot Rouge")

tk.Label(fenetre, text="Maintiens le bouton latéral droit (Forward) pour activer la détection", font=("Arial", 12)).pack(pady=5)
tk.Button(fenetre, text="ON", bg="green", fg="white", font=("Arial", 14), command=start).pack(pady=10)
tk.Button(fenetre, text="OFF", bg="red", fg="white", font=("Arial", 14), command=stop).pack(pady=10)

# Lance le listener souris pour détecter le bouton latéral
listener = mouse.Listener(on_click=on_click)
listener.start()

fenetre.mainloop()
