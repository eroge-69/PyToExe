import os
import sys

os.system('start cmd /C "netsh wlan show profiles & pause"')

red = input("Escriba el nombre de la red que desees : ")
documento = "HAPPY.txt"

comando = f'start cmd /C "netsh wlan show profile name=\\"{red}\\" key=clear > {documento} "'
os.system(comando)

sys.exit()

