import time
import random
import os
import pyautogui
import string

# Função para gerar nomes aleatórios de programas
def generate_random_name(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# Função para abrir uma janela (simular)
def open_random_window():
    random_name = generate_random_name()
    # Simula a abertura de uma "janela" através do "Notepad", mas pode ser alterado para outros programas
    os.system(f'notepad.exe {random_name}.txt')

# Função para simular a tecla "Windows"
def press_windows_key():
    pyautogui.hotkey('winleft')

# Loop infinito (com intervalos de tempo para não travar o sistema rapidamente)
while True:
    open_random_window()
    time.sleep(1)  # Tempo entre a abertura das janelas
    press_windows_key()
    time.sleep(2)  # Intervalo entre o clique da tecla "Windows" e a próxima abertura
