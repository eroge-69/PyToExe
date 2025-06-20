import pyautogui
import time

# Coordenadas do botão "Atualizar"
x = 514
y = 1056

while True:
    print("Clicando no botão 'Atualizar' do Power BI...")
    pyautogui.click(x, y)
    print("Aguardando 1 hora para a próxima atualização...")
    time.sleep(60)  # 3600 segundos = 1 hora
