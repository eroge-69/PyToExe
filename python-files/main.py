'''

                            Online Python Compiler.
                Code, Compile, Run and Debug python program online.
Write your code in this editor and press "Run" button to execute it.

'''

from pynput import keyboard

# Arquivo onde vamos salvar as teclas digitadas
arquivo_log = "captura_teclado.txt"

def on_press(key):
    try:
        # Se for uma tecla "normal", escreve a letra
        tecla = key.char
    except AttributeError:
        # Se for tecla especial, escreve o nome dela entre colchetes
        tecla = f'[{key.name}]'

    print(f"Tecla pressionada: {tecla}")
    
    # Salva a tecla no arquivo
    with open(arquivo_log, "a", encoding="utf-8") as f:
        f.write(tecla)

def on_release(key):
    # Para sair, pressione ESC
    if key == keyboard.Key.esc:
        print("Encerrando captura...")
        return False

# Inicia a escuta do teclado
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
