import customtkinter as ctk
import threading
import time
import pygetwindow as gw
import win32gui
from pynput.mouse import Button, Controller as MouseController, Listener as MouseListener
from pynput import keyboard

# Inicialização
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")
app = ctk.CTk()
app.title("Speed AutoClicker")
app.geometry("450x700")

# Variáveis
mouse = MouseController()
clicking = False
activation_key = None
activation_mode = "Hold"
click_button = Button.left
allowed_apps = ["ALL"]
key_pressed = False

# Funções auxiliares
def parse_float(text):
    try:
        return float(text.replace(",", "."))
    except:
        return 50.0

def get_active_window_title():
    hwnd = win32gui.GetForegroundWindow()
    return win32gui.GetWindowText(hwnd)

def is_allowed_window():
    if "ALL" in allowed_apps:
        return True
    current = get_active_window_title()
    return any(app in current for app in allowed_apps)

def click_loop():
    global clicking
    while clicking:
        if activation_mode_var.get() == "Hold" and not key_pressed:
            time.sleep(0.05)
            continue
        if is_allowed_window():
            rate = parse_float(cps_entry.get())
            duty = parse_float(duty_entry.get()) / 100.0
            if unlimited_var.get():
                interval = 0.001
            elif random_var.get():
                import random
                rate = random.uniform(1, rate)
                interval = 1 / rate
            else:
                interval = 1 / max(rate, 1)
            press_time = interval * duty
            release_time = interval * (1 - duty)
            mouse.press(click_button)
            time.sleep(press_time)
            mouse.release(click_button)
            time.sleep(release_time)
        else:
            time.sleep(0.1)

def start_clicker():
    global clicking, click_button
    if clicking:
        return
    btn = button_var.get()
    click_button = Button.left if btn == "Left" else Button.right if btn == "Right" else Button.middle
    clicking = True
    status_label.configure(text="Status: Ativo")
    threading.Thread(target=click_loop, daemon=True).start()

def stop_clicker():
    global clicking
    clicking = False
    status_label.configure(text="Status: Inativo")

# Ativação por tecla ou botão do rato
def on_press(key):
    global key_pressed, clicking
    if str(key) == str(activation_key):
        if activation_mode_var.get() == "Hold":
            key_pressed = True
            if not clicking:
                start_clicker()
        elif activation_mode_var.get() == "Toggle":
            if clicking:
                stop_clicker()
            else:
                start_clicker()

def on_release(key):
    global key_pressed
    if str(key) == str(activation_key) and activation_mode_var.get() == "Hold":
        key_pressed = False
        stop_clicker()

keyboard.Listener(on_press=on_press, on_release=on_release).start()
MouseListener(on_click=lambda x, y, button, pressed: on_press(button) if pressed else on_release(button)).start()

def detect_key():
    def on_key_press(key):
        global activation_key
        activation_key = key
        key_label.configure(text=f"Activation: {str(key)}")
        return False

    def on_mouse_click(x, y, button, pressed):
        if pressed:
            global activation_key
            activation_key = button
            key_label.configure(text=f"Activation: {str(button)}")
            return False

    key_label.configure(text="Press a key or mouse button...")
    keyboard.Listener(on_press=on_key_press).start()
    MouseListener(on_click=on_mouse_click).start()

def open_app_selector():
    selector = ctk.CTkToplevel(app)
    selector.title("Choose Applications")
    selector.geometry("400x500")
    selector.transient(app)
    selector.grab_set()
    selector.focus_force()

    all_var = ctk.BooleanVar(value="ALL" in allowed_apps)
    all_checkbox = ctk.CTkCheckBox(selector, text="Allow all apps", variable=all_var)
    all_checkbox.pack(pady=10)

    frame = ctk.CTkScrollableFrame(selector)
    frame.pack(expand=True, fill="both", padx=10, pady=10)

    app_vars = {}
    for win in gw.getWindowsWithTitle(""):
        title = win.title.strip()
        if title:
            var = ctk.BooleanVar()
            chk = ctk.CTkCheckBox(frame, text=title, variable=var)
            chk.pack(anchor="w", padx=5, pady=2)
            app_vars[title] = var

    def confirm():
        allowed_apps.clear()
        if all_var.get():
            allowed_apps.append("ALL")
        else:
            for app, var in app_vars.items():
                if var.get():
                    allowed_apps.append(app)
        selector.destroy()

    ctk.CTkButton(selector, text="Confirm", command=confirm).pack(pady=10)

# Interface gráfica
ctk.CTkLabel(app, text="Speed AutoClicker", font=("Arial", 20)).pack(pady=10)

ctk.CTkLabel(app, text="Activation key/button:", font=("Arial", 14)).pack(pady=5)
ctk.CTkButton(app, text="Select...", command=detect_key).pack(pady=5)
key_label = ctk.CTkLabel(app, text="Activation: None")
key_label.pack(pady=5)

ctk.CTkLabel(app, text="Activation mode:", font=("Arial", 14)).pack(pady=5)
activation_mode_var = ctk.StringVar(value="Hold")
ctk.CTkComboBox(app, variable=activation_mode_var, values=["Hold", "Toggle"]).pack(pady=5)

ctk.CTkLabel(app, text="Mouse button:", font=("Arial", 14)).pack(pady=5)
button_var = ctk.StringVar(value="Left")
ctk.CTkComboBox(app, variable=button_var, values=["Left", "Right", "Middle"]).pack(pady=5)

ctk.CTkLabel(app, text="Click rate:", font=("Arial", 14)).pack(pady=5)
cps_entry = ctk.CTkEntry(app)
cps_entry.insert(0, "120,00")
cps_entry.pack(pady=5)

unlimited_var = ctk.BooleanVar()
ctk.CTkCheckBox(app, text="Unlimited", variable=unlimited_var).pack(pady=2)

random_var = ctk.BooleanVar()
ctk.CTkCheckBox(app, text="Random", variable=random_var).pack(pady=2)

ctk.CTkLabel(app, text="Click duty cycle (%):", font=("Arial", 14)).pack(pady=5)
duty_entry = ctk.CTkEntry(app)
duty_entry.insert(0, "50,00")
duty_entry.pack(pady=5)

ctk.CTkButton(app, text="Choose apps", command=open_app_selector).pack(pady=10)

status_label = ctk.CTkLabel(app, text="Status: Inativo", font=("Arial", 12))
status_label.pack(pady=5)

ctk.CTkButton(app, text="▶️ OK", command=start_clicker).pack(pady=5)
ctk.CTkButton(app, text="⏹️ RESET", command=stop_clicker).pack(pady=5)
ctk.CTkButton(app, text="❌ EXIT", command=app.destroy).pack(pady=5)

ctk.CTkLabel(app, text="Made with ❤️ by Conta", font=("Arial", 12)).pack(pady=20)

app.mainloop()
