from pynput import keyboard
import pygetwindow as gw
import time

GAME_TITLE = "Transformice"

def is_game_active():
    try:
        active_window = gw.getActiveWindow()
        return GAME_TITLE in active_window.title
    except:
        return False

def send_vanilla_command():
    # Włącz czat
    keyboard.Controller().press(keyboard.Key.enter)
    time.sleep(0.1)
    # Wpisz komendę "/vanilla"
    keyboard.Controller().type('/vanilla')
    time.sleep(0.1)
    # Wyślij komendę
    keyboard.Controller().press(keyboard.Key.enter)

def send_mort_command():
    # Włącz czat
    keyboard.Controller().press(keyboard.Key.enter)
    time.sleep(0.1)
    # Wpisz komendę "/mort"
    keyboard.Controller().type('/mort')
    time.sleep(0.1)
    # Wyślij komendę
    keyboard.Controller().press(keyboard.Key.enter)

def on_press(key):
    if key == keyboard.KeyCode.from_char('*') and is_game_active():
        send_vanilla_command()
    elif key == keyboard.Key.delete and is_game_active():
        send_mort_command()

def on_release(key):
    if key == keyboard.Key.esc:
        # Zatrzymaj nasłuchiwanie, jeśli naciśniesz Esc
        return False

# Uruchom nasłuchiwanie klawiszy
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()