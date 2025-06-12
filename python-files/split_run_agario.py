import pyautogui
import keyboard
import time

# CONFIGURAÇÕES
run_key = 'shift'       # Tecla que ativa o split run
split_key = 'space'     # Tecla do split
delay = 0.1             # Tempo entre os movimentos
offset = 200            # Distância do mouse para frente/trás a partir do centro da tela

def get_screen_center():
    screen_width, screen_height = pyautogui.size()
    return screen_width // 2, screen_height // 2

def split_run_agario():
    print("Pressione SHIFT para ativar o Split Run no Agar.io (ESC para sair)")
    center_x, center_y = get_screen_center()

    while True:
        if keyboard.is_pressed('esc'):
            print(">> BOT ENCERRADO")
            break

        if keyboard.is_pressed(run_key):
            print(">> BOT ATIVADO")
            while keyboard.is_pressed(run_key):
                if keyboard.is_pressed('esc'):
                    print(">> BOT ENCERRADO")
                    return
                pyautogui.moveTo(center_x, center_y - offset, duration=0.01)
                pyautogui.press(split_key)
                time.sleep(delay)
                pyautogui.moveTo(center_x, center_y + offset, duration=0.01)
                time.sleep(delay)

        time.sleep(0.05)

if __name__ == "__main__":
    split_run_agario()
