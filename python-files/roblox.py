import pyautogui
import keyboard
import time
import threading
import tkinter as tk

monitoring = False
window = None
status_label = None

def update_label(state):
    status_label.config(text=f"Monitoring: {'ON' if state else 'OFF'}", fg='green' if state else 'red')

def get_offset_colors():
    x, y = pyautogui.position()
    left_pixel = pyautogui.pixel(x - 2, y)
    right_pixel = pyautogui.pixel(x + 2, y)
    return left_pixel, right_pixel

def monitor_pixels():
    global monitoring
    update_label(True)
    initial_left, initial_right = get_offset_colors()
    time.sleep(0.1)

    while monitoring:
        if keyboard.is_pressed("esc"):
            monitoring = False
            update_label(False)
            print("Monitoring manually stopped.")
            break

        left, right = get_offset_colors()
        if left != initial_left or right != initial_right:
            print("Pixel change detected! Clicking mouse.")
            pyautogui.click()
            monitoring = False
            update_label(False)
            break

        time.sleep(0.01)

def start_monitoring():
    global monitoring
    if not monitoring:
        monitoring = True
        threading.Thread(target=monitor_pixels, daemon=True).start()

def keyboard_listener():
    while True:
        if keyboard.is_pressed("f6"):
            start_monitoring()
            time.sleep(0.3)  # zapobiega wielokrotnemu uruchomieniu
        time.sleep(0.1)

def create_gui():
    global window, status_label
    window = tk.Tk()
    window.title("Pixel Monitor")
    window.geometry("200x80")
    window.resizable(False, False)

    status_label = tk.Label(window, text="Monitoring: OFF", font=("Arial", 14), fg="red")
    status_label.pack(pady=20)

    threading.Thread(target=keyboard_listener, daemon=True).start()
    window.mainloop()

if __name__ == "__main__":
    create_gui()
