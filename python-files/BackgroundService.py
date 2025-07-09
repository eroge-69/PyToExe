import time
import threading
import tkinter as tk
from pynput.mouse import Controller, Button
from pynput.mouse import Listener
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw

# Variáveis globais
clicking = False
click_interval = 0.1  # Padrão para 10 CPS
mouse_controller = Controller()

# Função para iniciar ou parar o auto clicker
def toggle_clicker():
    global clicking
    clicking = not clicking
    if clicking:
        status_label.config(text="Status: Ativo", fg="green")
        start_clicking_thread()
    else:
        status_label.config(text="Status: Inativo", fg="red")

# Função para iniciar o clique automático em um thread separado
def start_clicking_thread():
    click_thread = threading.Thread(target=auto_click)
    click_thread.daemon = True  # Thread que se fecha quando o programa termina
    click_thread.start()

# Função de auto clicker
def auto_click():
    while clicking:
        mouse_controller.click(Button.left)
        time.sleep(click_interval)

# Função para atualizar a taxa de cliques (CPS)
def update_cps():
    global click_interval
    try:
        cps = float(cps_entry.get())
        if cps > 0:
            click_interval = 1 / cps  # Converter CPS para intervalo de tempo
    except ValueError:
        pass  # Caso o valor não seja um número válido

# Função para capturar cliques do mouse (ligar/desligar o auto clicker)
def on_click(x, y, button, pressed):
    global clicking
    if button == Button.x2 and pressed:  # Quando pressionar o botão lateral X2 do mouse
        toggle_clicker()

# Iniciar o listener do mouse em um thread separado
def start_listener():
    with Listener(on_click=on_click) as listener:
        listener.join()

# Função para desenhar o ícone da bandeja (com transparência)
def create_icon():
    # Criar uma imagem completamente transparente (sem ícone visível)
    image = Image.new("RGBA", (64, 64), (255, 255, 255, 0))  # Imagem completamente transparente
    return image

# Função para sair do programa
def exit_action(icon, item):
    icon.stop()

# Função para mostrar/ocultar a janela principal
def toggle_window():
    if root.winfo_ismapped():
        root.withdraw()  # Ocultar a janela
    else:
        root.deiconify()  # Mostrar a janela

# Função para criar o menu da bandeja
def create_tray_icon():
    icon_image = create_icon()  # Cria o ícone invisível
    menu = Menu(MenuItem('Abrir', toggle_window), MenuItem('Sair', exit_action))
    icon = Icon("AutoClicker", icon_image, menu=menu)
    icon.run()

# Iniciar o listener em um thread
listener_thread = threading.Thread(target=start_listener)
listener_thread.daemon = True
listener_thread.start()

# Criar a interface gráfica invisível
root = tk.Tk()
root.title("Explorador de Arquivos")  # Nome "Explorador de Arquivos" (ou qualquer nome do Windows)
root.geometry("300x200")
root.withdraw()  # Esconde a janela

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

# Status
status_label = tk.Label(frame, text="Status: Inativo", fg="red")
status_label.grid(row=0, column=0, columnspan=2, pady=5)

# Taxa de CPS
cps_label = tk.Label(frame, text="Taxa de CPS (cliques por segundo):")
cps_label.grid(row=1, column=0, pady=5)

cps_entry = tk.Entry(frame)
cps_entry.insert(0, "10")  # Valor padrão de 10 CPS
cps_entry.grid(row=1, column=1, pady=5)

update_button = tk.Button(frame, text="Atualizar CPS", command=update_cps)
update_button.grid(row=2, column=0, columnspan=2, pady=5)

# Botão para iniciar/parar o auto clicker
toggle_button = tk.Button(frame, text="Iniciar / Parar Auto Click", command=toggle_clicker)
toggle_button.grid(row=3, column=0, columnspan=2, pady=10)

# Criar o ícone na bandeja
thread_tray = threading.Thread(target=create_tray_icon)
thread_tray.daemon = True
thread_tray.start()

# Iniciar a interface gráfica
root.mainloop()


