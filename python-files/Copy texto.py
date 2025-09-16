import pyautogui
import pyperclip
import time
import sys
import os

def main():
    print("✅ AutoTyper iniciado.")
    print("👉 Copie qualquer texto (CTRL+C).")
    print("🕐 Você terá 5 segundos para clicar na janela onde deseja digitar.")
    input("🔁 Pressione ENTER para começar...")

    time.sleep(5)

    texto = pyperclip.paste()
    intervalo = 0.02  # segundos entre letras

    for letra in texto:
        pyautogui.write(letra)
        time.sleep(intervalo)

    print("✅ Texto digitado com sucesso.")

if __name__ == "__main__":
    main()
