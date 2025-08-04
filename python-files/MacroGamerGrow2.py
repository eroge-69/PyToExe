import tkinter as tk
import threading
import time
import win32gui
import keyboard
from pynput.keyboard import Controller
import pyautogui
from datetime import datetime, timedelta
import cv2
import numpy as np

keyboard2 = Controller()
running = False
ui_navigation_enabled = None
seed_vars = {}
status_label = None  

seed_actions = {
    "Carrot Seed": 1, "Strawberry Seed": 2, "Blueberry Seed": 3, "Orange Tulip": 4,
    "Tomato Seed": 5, "Corn Seed": 6, "Daffodil Seed": 7, "Watermelon Seed": 8,
    "Pumpkin Seed": 9, "Apple Seed": 10, "Bamboo Seed": 11, "Coconut Seed": 12,
    "Cactus Seed": 13, "Dragon Fruit Seed": 14, "Mango Seed": 15, "Grape Seed": 16,
    "Mushroom Seed": 17, "Pepper Seed": 18, "Cacao Seed": 19, "Beanstalk Seed": 20,
    "Ember Lily Seed": 21, "Sugar Apple Seed": 22, "Burning Bud Seed": 23,
    "Giant Pinecone Seed": 24, "Elder Strawberry Seed": 25
}

def is_roblox_active():
    hwnd = win32gui.GetForegroundWindow()
    return "Roblox" in win32gui.GetWindowText(hwnd)

def image_matches_reference(threshold=0.9):
    try:
        ref_image_path = "images/reference.png"
        ref_image = cv2.imread(ref_image_path, cv2.IMREAD_GRAYSCALE)
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

        result = cv2.matchTemplate(screenshot, ref_image, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        print(f"🔍 Nivel de coincidencia: {max_val:.3f}")
        return max_val >= threshold
    except Exception as e:
        print(f"⚠ Error en detección de imagen con OpenCV: {e}")
        return False

def repeat_until_image_matches():
    keyboard.press_and_release('s')
    time.sleep(0.100)
    keyboard.press_and_release('a')
    time.sleep(0.100)
    keyboard.press_and_release('enter')
    time.sleep(1.0)

    attempts = 0
    while running and not image_matches_reference():
        if attempts > 999999999:
            print("⚠ Límite sin coincidencia.")
            break
        keyboard.press_and_release('enter')
        time.sleep(0.100)
        attempts += 1

def countdown_gui_and_console(total_seconds):
    if not running:
        return
    end_time = time.time() + total_seconds
    timer_root = tk.Tk()
    timer_root.title("⏳ Espera")
    timer_root.geometry("250x100")
    timer_root.attributes("-topmost", True)
    label = tk.Label(timer_root, text="", font=("Arial", 20))
    label.pack(pady=20)

    def update():
        if not running:
            timer_root.destroy()
            return
        remaining = max(0, int(end_time - time.time()))
        mins, secs = divmod(remaining, 60)
        label.config(text=f"{mins:02d}m {secs:02d}s restantes")
        if remaining > 0:
            timer_root.after(1000, update)
        else:
            timer_root.destroy()

    update()
    timer_root.mainloop()
    print("⏰ Tiempo cumplido.")

def wait_until_next_multiple_of_5():
    if not running:
        return
    now = datetime.now()
    current_minute = now.minute
    minutes_to_add = (5 - current_minute % 5) % 5
    if minutes_to_add == 0:
        minutes_to_add = 5

    next_trigger_time = now.replace(second=0, microsecond=0) + timedelta(minutes=minutes_to_add)
    total_seconds = int((next_trigger_time - now).total_seconds())
    print(f"⏳ Esperando hasta {next_trigger_time.strftime('%H:%M')} ({total_seconds}s)...")
    countdown_gui_and_console(total_seconds)

def process_selected_seeds():
    if not running:
        return
    selected = [(seed, seed_actions[seed]) for seed, var in seed_vars.items() if var.get()]
    if not selected:
        print("⚠ No seleccionaste semillas.")
        return

    selected_sorted = sorted(selected, key=lambda x: x[1], reverse=True)

    print("⏬ Bajando a posición 25...")
    for _ in range(25):
        if not running:
            return
        keyboard.press_and_release('s')
        time.sleep(0.100)
    current_pos = 25

    for seed, target_pos in selected_sorted:
        if not running:
            return
        if target_pos < current_pos:
            for _ in range(current_pos - target_pos):
                if not running:
                    return
                keyboard.press_and_release('w')
                time.sleep(0.1)
        elif target_pos > current_pos:
            for _ in range(target_pos - current_pos):
                if not running:
                    return
                keyboard.press_and_release('s')
                time.sleep(0.1)

        print(f"🔍 Verificando {seed}")
        keyboard.press_and_release('enter')
        time.sleep(1.0)
        if not running:
            return

        if not image_matches_reference():
            print("❌ Imagen distinta. Corrigiendo...")
            repeat_until_image_matches()
            if not running:
                return
            print("✅ Imagen corregida.")
            keyboard.press_and_release('w')
            time.sleep(0.3)
            keyboard.press_and_release('enter')
            time.sleep(0.5)
        else:
            print("✅ Imagen correcta. Solo enter.")
            keyboard.press_and_release('enter')
            time.sleep(0.5)

        current_pos = target_pos

    was_ui_enabled = ui_navigation_enabled.get()
    wait_until_next_multiple_of_5()
    if not running:
        return

    for _ in range(current_pos - 1):
        if not running:
            return
        keyboard.press_and_release('w')
        time.sleep(0.1)

    if was_ui_enabled:
        print("➡ En posición 1: 'w' + 'enter'")
        keyboard.press_and_release('w')
        time.sleep(0.3)
        keyboard.press_and_release('enter')
        time.sleep(0.5)
        print("🛑 Desactivando UI Navigation")
        keyboard2.press('ç'); keyboard2.release('ç')
        time.sleep(0.5)
    else:
        print("▶ Clásico: d x3 + enter")
        for _ in range(3):
            if not running:
                return
            keyboard.press_and_release('d')
            time.sleep(0.2)
        keyboard.press_and_release('enter')
        time.sleep(0.5)

    if not running:
        return

    if was_ui_enabled:
        print("✅ Reactivando UI Navigation")
        keyboard2.press('ç'); keyboard2.release('ç')
        time.sleep(0.5)
        print("▶ Acción: w + enter")
        keyboard.press_and_release('w')
        time.sleep(0.3)
        keyboard.press_and_release('enter')
        time.sleep(0.3)
        keyboard.press_and_release('e')
        time.sleep(2)
    else:
        print("▶ Clásico: d x3 + enter")
        for _ in range(3):
            if not running:
                return
            keyboard.press_and_release('d')
            time.sleep(0.2)
        keyboard.press_and_release('enter')
        time.sleep(0.3)
        keyboard.press_and_release('e')
        time.sleep(2)

    if running:
        process_selected_seeds()

def action():
    global running
    if not is_roblox_active():
        print("⚠ Roblox no activo.")
        running = False
        update_status_label()
        return

    if ui_navigation_enabled.get():
        print("▶ UI Navigation ON")
        keyboard2.press('ç'); keyboard2.release('ç')
        time.sleep(2)
        keyboard.press_and_release('w')
        time.sleep(0.100)
        keyboard.press_and_release('enter')
        time.sleep(0.100)
        keyboard2.press('e'); keyboard2.release('e')
    else:
        print("▶ Modo clásico")
        keyboard2.press('ç'); keyboard2.release('ç')
        for _ in range(3):
            if not running:
                return
            keyboard.press_and_release('d')
            time.sleep(0.100)
        keyboard.press_and_release('enter')
        time.sleep(0.100)
        keyboard2.press('e'); keyboard2.release('e')

    time.sleep(2)
    if running:
        process_selected_seeds()
    running = False
    update_status_label()

def toggle_script():
    global running
    running = not running
    if running:
        print("✅ Script iniciado")
        threading.Thread(target=action, daemon=True).start()
    else:
        print("🛑 Script detenido")
    update_status_label()

def update_status_label():
    if status_label:
        status_label.config(text="🟢 Corriendo" if running else "🔴 Detenido")

def hotkey_listener():
    keyboard.add_hotkey('F5', toggle_script)
    keyboard.wait()

def start_gui():
    global ui_navigation_enabled, status_label
    root = tk.Tk()
    root.title("Control de Seeds")
    root.geometry("350x800")
    ui_navigation_enabled = tk.BooleanVar()
    tk.Checkbutton(root, text="UI Navigation(Item Bar)", variable=ui_navigation_enabled).pack(pady=5)
    tk.Label(root, text="Selecciona semillas:").pack()
    for seed in seed_actions:
        var = tk.BooleanVar()
        seed_vars[seed] = var
        tk.Checkbutton(root, text=seed, variable=var).pack(anchor='w')

    status_label = tk.Label(root, text="🔴 Detenido", font=("Arial", 14))
    status_label.pack(pady=10)

    tk.Label(root, text="Presiona F5 para ejecutar/detener").pack(pady=10)

    threading.Thread(target=hotkey_listener, daemon=True).start()
    root.mainloop()

if __name__ == "__main__":
    start_gui()
