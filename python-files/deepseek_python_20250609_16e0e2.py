import time
import random
from pynput.keyboard import Controller, Key
from pynput.mouse import Button, Controller as MouseController
from pynput import keyboard, mouse
import sys

# Inizializza controller
kb = Controller()
mouse_ctrl = MouseController()

# Mappatura tasti mouse personalizzati (aggiunta)
MOUSE_BUTTONS = {
    'mouse4': Button.button8,
    'mouse5': Button.button9,
    'mouse6': Button.button10,
    'mouse7': Button.button11
}

# Variabili per i tasti
bow_key = None
sword_key = None
start_key = None

def parse_key(key_str):
    """Converte una stringa in tasto keyboard/mouse"""
    key_str = key_str.lower().strip()
    if key_str.startswith('mouse'):
        return MOUSE_BUTTONS.get(key_str, None)
    elif len(key_str) == 1:  # Tasto singolo
        return key_str
    elif key_str == 'ctrl':
        return Key.ctrl
    elif key_str == 'shift':
        return Key.shift
    elif key_str == 'alt':
        return Key.alt
    else:
        return None

def setup_keys():
    global bow_key, sword_key, start_key
    print("=== Configurazione Macro Minecraft ===")
    print("Tasti disponibili: tasti normali (es. 'q'), mouse4, mouse5, mouse6, mouse7")
    
    while True:
        bow_key = parse_key(input("Tasto Bow (es. 'q' o 'mouse4'): "))
        if bow_key: break
        print("Tasto non valido! Riprova")
    
    while True:
        sword_key = parse_key(input("Tasto Spada (es. 'e' o 'mouse5'): "))
        if sword_key: break
        print("Tasto non valido! Riprova")
    
    while True:
        start_key = parse_key(input("Tasto Avvio (es. 'f' o 'mouse6'): "))
        if start_key: break
        print("Tasto non valido! Riprova")
    
    print("\nConfigurazione completata:")
    print(f"Bow: {str(bow_key)}")
    print(f"Spada: {str(sword_key)}")
    print(f"Avvio: {str(start_key)}")
    print(f"\nTieni premuto il tasto di avvio per usare la macro!")

def press_key(key):
    """Premi un tasto (keyboard o mouse)"""
    if isinstance(key, Button):
        mouse_ctrl.press(key)
    else:
        kb.press(key)

def release_key(key):
    """Rilascia un tasto (keyboard o mouse)"""
    if isinstance(key, Button):
        mouse_ctrl.release(key)
    else:
        kb.release(key)

def is_key_pressed(key):
    """Controlla se un tasto è premuto"""
    if isinstance(key, Button):
        # Non c'è un modo diretto per verificare lo stato del mouse in pynput
        # Usiamo keyboard.is_pressed come workaround per i tasti mouse
        return False  # Modifica questa parte se trovi un modo migliore
    else:
        return keyboard.is_pressed(key)

def run_macro():
    print("Macro attiva! Premi ESC per uscire")
    with keyboard.Listener(on_press=None, on_release=None) as k_listener, \
         mouse.Listener(on_click=None) as m_listener:
        
        while True:
            if is_key_pressed(start_key):
                # Bow (0-10ms)
                press_key(bow_key)
                time.sleep(random.uniform(0, 0.01))
                release_key(bow_key)
                
                # Tasto destro (170-220ms)
                mouse_ctrl.press(Button.right)
                time.sleep(random.uniform(0.17, 0.22))
                mouse_ctrl.release(Button.right)
                
                # Spada (0-10ms)
                press_key(sword_key)
                time.sleep(random.uniform(0, 0.01))
                release_key(sword_key)
                
                # Pausa (300-400ms)
                time.sleep(random.uniform(0.3, 0.4))
            
            # Uscita con ESC
            if keyboard.is_pressed(Key.esc):
                print("\nMacro disattivata")
                sys.exit(0)
            time.sleep(0.01)

if __name__ == "__main__":
    setup_keys()
    try:
        run_macro()
    except KeyboardInterrupt:
        print("\nMacro chiusa")
    except Exception as e:
        print(f"Errore: {e}")