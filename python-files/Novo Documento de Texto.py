import threading
import time
import sys
from pynput import keyboard, mouse
import customtkinter as ctk
import pystray
from PIL import Image, ImageDraw

# --- Configuração inicial da interface ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# --- Controladores ---
mouse_controller = mouse.Controller()

# Variáveis globais
clicking = False
cooldown = 1000
active_key = 'f'
button_left = True
emergency_key = keyboard.Key.esc
listener = None
stop_threads = False

# Função para criar ícone da bandeja
def create_image():
    # 64x64 pixels, verde claro no centro
    image = Image.new('RGBA', (64, 64), (0,0,0,0))
    dc = ImageDraw.Draw(image)
    dc.rectangle((16, 16, 48, 48), fill=(0, 255, 0, 255))
    return image

def on_click(icon, item):
    if str(item) == 'Abrir':
        app.deiconify()
    elif str(item) == 'Sair':
        global stop_threads
        stop_threads = True
        icon.stop()
        app.quit()

def setup_tray():
    icon = pystray.Icon("AutoClicker", create_image(), "AutoClicker", menu=pystray.Menu(
        pystray.MenuItem("Abrir", on_click),
        pystray.MenuItem("Sair", on_click)
    ))
    threading.Thread(target=icon.run, daemon=True).start()
    return icon

def click_loop():
    global clicking, stop_threads
    while not stop_threads:
        if clicking:
            if button_left:
                mouse_controller.click(mouse.Button.left)
            else:
                mouse_controller.click(mouse.Button.right)
            time.sleep(cooldown/1000)
        else:
            time.sleep(0.01)

def on_press(key):
    global clicking
    try:
        if hasattr(key, 'char') and key.char == active_key:
            clicking = True
            update_status("Clicando...")
    except AttributeError:
        pass
    if key == emergency_key:
        clicking = False
        update_status("Parado (emergência)")

def on_release(key):
    global clicking
    try:
        if hasattr(key, 'char') and key.char == active_key:
            clicking = False
            update_status("Parado")
    except AttributeError:
        pass

def start_listener():
    global listener
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.daemon = True
    listener.start()

def update_status(text):
    app.status_label.configure(text=text)

def apply_settings():
    global cooldown, active_key, button_left
    try:
        cd = int(app.entry_cooldown.get())
        if cd < 10:
            cd = 10
        cooldown = cd
    except:
        update_status("Cooldown inválido")
        return

    key = app.entry_key.get().lower()
    if len(key) == 1 and key.isalnum():
        active_key = key
    else:
        update_status("Tecla inválida")
        return

    button_left = (app.radio_var.get() == "left")

    update_status(f"Pronto! Segure '{active_key.upper()}' para clicar.")

def toggle_manual():
    global clicking
    clicking = not clicking
    if clicking:
        update_status("Clicando manualmente")
        app.btn_manual.configure(text="Parar manualmente")
        app.show_indicator(True)
    else:
        update_status("Parado")
        app.btn_manual.configure(text="Iniciar manualmente")
        app.show_indicator(False)

def on_closing():
    app.withdraw()
    tray_icon.notify("AutoClicker minimizado para bandeja.")

class AutoClickerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AutoClicker Avançado")
        self.geometry("400x280")

        self.radio_var = ctk.StringVar(value="left")

        ctk.CTkLabel(self, text="Tecla de ativação (ex: F):").pack(pady=5)
        self.entry_key = ctk.CTkEntry(self)
        self.entry_key.insert(0, "f")
        self.entry_key.pack(pady=5)

        ctk.CTkLabel(self, text="Cooldown entre cliques (ms):").pack(pady=5)
        self.entry_cooldown = ctk.CTkEntry(self)
        self.entry_cooldown.insert(0, "1000")
        self.entry_cooldown.pack(pady=5)

        ctk.CTkLabel(self, text="Botão do mouse:").pack(pady=5)
        frame_radio = ctk.CTkFrame(self)
        frame_radio.pack(pady=5)
        ctk.CTkRadioButton(frame_radio, text="Esquerdo", variable=self.radio_var, value="left").pack(side="left", padx=10)
        ctk.CTkRadioButton(frame_radio, text="Direito", variable=self.radio_var, value="right").pack(side="left", padx=10)

        ctk.CTkButton(self, text="Aplicar Configurações", command=apply_settings).pack(pady=10)

        self.btn_manual = ctk.CTkButton(self, text="Iniciar manualmente", command=toggle_manual)
        self.btn_manual.pack(pady=10)

        self.status_label = ctk.CTkLabel(self, text="Pronto!")
        self.status_label.pack(pady=10)

        # Indicador quadrado azul
        self.indicador = ctk.CTkFrame(self, width=50, height=50, corner_radius=8, fg_color="blue")
        self.indicador.pack(pady=10)
        self.indicador.place_forget()  # Esconde no começo

    def show_indicator(self, show):
        if show:
            self.indicador.place(relx=0.5, rely=0.85, anchor="center")
        else:
            self.indicador.place_forget()

app = AutoClickerApp()

# Iniciar o listener de teclado e loop de clique
start_listener()
threading.Thread(target=click_loop, daemon=True).start()

# Criar ícone da bandeja
tray_icon = setup_tray()

app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()
