import time
import keyboard
import datetime
from PIL import ImageGrab
import colorama
from colorama import Fore, Back, Style, init
import pyfiglet
from pyfiglet import Figlet
import os
titulo = pyfiglet.figlet_format("Ez S.hot", font = "alligator")
#// introdução
print(Fore.RED + titulo + Fore.RESET)
print("")
time.sleep(1)
#// Variaveis

now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
foto = ImageGrab.grab()
numero = 1
#// Tecla

print("Selecione uma tecla")
tecla = input("teclas especiais tem que ser escrevidas por exemplo 'esc': ")
print("Carregando")
time.sleep(0.5)
os.system("cls")
print("Carregando.")
time.sleep(0.5)
os.system("cls")
print("Carregando..")
time.sleep(0.5)
os.system("cls")
print("Carregando...")
time.sleep(0.5)
os.system("cls")
print("Carregando")
os.system("cls")
time.sleep(1)
print("Aplicativo Pronto")
while True:
    if keyboard.is_pressed(tecla):
        foto.save(f"{now} {numero}.png")
        print(F"foto tirada {now} {numero}")
        numero = numero + 1
        time.sleep(0.5)
        