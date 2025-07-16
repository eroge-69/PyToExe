import tkinter as tk
import threading
import pyautogui
import time
import random

def bot_mineracao():
    # Coordenadas dos pontos de mineração (Elwynn Forest)
    rota_cobre = [
        (34, 50), (38, 62), (42, 67), (48, 76), (54, 70),
        (62, 62), (70, 60), (74, 52), (68, 44), (60, 40),
        (52, 38), (44, 40),
    ]
    
    # Configurações do minimapa (ajuste para sua tela)
    base_x, base_y = 1700, 100  # Canto superior esquerdo do minimapa
    escala = 3  # Escala do minimapa
    
    time.sleep(5)  # Tempo para abrir o jogo
    
    while True:
        # 1. Primeiro, procurar minério na tela atual
        minerio = pyautogui.locateOnScreen('minerio.png', confidence=0.7)
        if minerio:
            # Encontrou minério - clicar para minerar
            x, y = pyautogui.center(minerio)
            pyautogui.moveTo(x, y, duration=random.uniform(0.2, 0.5))
            pyautogui.click(button='right')
            time.sleep(5)  # Tempo para minerar
        else:
            # 2. Se não encontrou minério, ir para próximo ponto da rota
            for ponto in rota_cobre:
                # Converter coordenadas do mapa para pixels do minimapa
                x, y = base_x + ponto[0] * escala, base_y + ponto[1] * escala
                
                # Clicar no minimapa para ir até o ponto
                pyautogui.moveTo(x, y, duration=random.uniform(0.5, 1.0))
                pyautogui.click(button='right')
                
                # Esperar o personagem chegar
                time.sleep(random.uniform(8, 12))
                
                # Procurar minério no novo local
                minerio = pyautogui.locateOnScreen('minerio.png', confidence=0.7)
                if minerio:
                    # Encontrou minério - clicar para minerar
                    x, y = pyautogui.center(minerio)
                    pyautogui.moveTo(x, y, duration=random.uniform(0.2, 0.5))
                    pyautogui.click(button='right')
                    time.sleep(5)  # Tempo para minerar
                    break  # Sai do loop de pontos e volta ao início
            
            # Se não encontrou minério em nenhum ponto, andar um pouco
            pyautogui.keyDown('w')
            time.sleep(random.uniform(2, 3))
            pyautogui.keyUp('w')
            pyautogui.keyDown('a')
            time.sleep(random.uniform(0.5, 1.0))
            pyautogui.keyUp('a')

def iniciar_bot():
    thread = threading.Thread(target=bot_mineracao)
    thread.start()

root = tk.Tk()
root.title("Bot de Mineração WoW 3.3.5 - Coordenadas + Detecção")

label = tk.Label(root, text="Bot híbrido: Coordenadas + Detecção automática\n\n1. Procura minérios na tela atual\n2. Se não encontrar, vai para pontos da rota\n3. Ajuste base_x, base_y e escala para seu minimapa\n\nDeixe 'minerio.png' na mesma pasta!")
label.pack(pady=10)

botao = tk.Button(root, text="Iniciar Bot", command=iniciar_bot)
botao.pack(pady=10)

root.mainloop() 