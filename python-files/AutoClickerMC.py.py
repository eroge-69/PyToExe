import time
import threading
import tkinter as tk
from tkinter import ttk
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, KeyCode

mouse = Controller()
clicking = False
holding = False  
click_speed = 0.1
click_type = Button.left
click_loop = False
stop_after = None
keybind = KeyCode.from_char('z')


def start_clicking():
    global clicking, holding
    clicking = True
    start_time = time.time()

    while clicking:
        if holding:
            mouse.press(click_type)  
        else:
            mouse.click(click_type)
            time.sleep(click_speed)

        if stop_after and time.time() - start_time >= stop_after:
            clicking = False
            if holding:
                mouse.release(click_type)  

def stop_clicking():
    global clicking, holding
    clicking = False
    if holding:
        mouse.release(click_type)  

def on_press(key):
    global clicking
    if key == keybind:
        if clicking:
            stop_clicking()
        else:
            threading.Thread(target=start_clicking).start()

def open_gui():
    def update_settings():
        global click_speed, click_type, click_loop, stop_after, keybind, holding
        click_speed = float(speed_entry.get())
        click_type = Button.left if click_type_var.get() == "Left Click" else Button.right
        click_loop = loop_var.get() == "Yes"
        stop_after = float(stop_entry.get()) if stop_entry.get() else None
        keybind = KeyCode.from_char(key_entry.get().lower())
        holding = click_mode_var.get() == "Hold"  

    root = tk.Tk()
    root.title("Minecraft AutoClicker")
    root.geometry("500x450") 
    root.configure(bg="#252525")

    style = ttk.Style()
    style.configure("TLabel", foreground="white", background="#252525", font=("Arial", 12, "bold"))
    style.configure("TButton", foreground="black", font=("Arial", 12, "bold"))
    style.configure("TEntry", font=("Arial", 12), padding=5, relief="solid")

    frame = ttk.Frame(root, padding="20", style="TLabel")
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Click Speed (seconds):").grid(row=0, column=0, sticky="w", pady=5)
    speed_entry = ttk.Entry(frame, width=15)
    speed_entry.grid(row=0, column=1, padx=10, pady=5)
    speed_entry.insert(0, "0.1")

    ttk.Label(frame, text="Click Type:").grid(row=1, column=0, sticky="w", pady=5)
    click_type_var = tk.StringVar(value="Left Click")
    click_type_dropdown = ttk.Combobox(frame, textvariable=click_type_var, values=["Left Click", "Right Click"])
    click_type_dropdown.grid(row=1, column=1, padx=10, pady=5)
    click_type_dropdown.current(0)

    ttk.Label(frame, text="Loop Until Stopped:").grid(row=2, column=0, sticky="w", pady=5)
    loop_var = tk.StringVar(value="No")
    loop_dropdown = ttk.Combobox(frame, textvariable=loop_var, values=["Yes", "No"])
    loop_dropdown.grid(row=2, column=1, padx=10, pady=5)
    loop_dropdown.current(1)

    ttk.Label(frame, text="Stop After (seconds, optional):").grid(row=3, column=0, sticky="w", pady=5)
    stop_entry = ttk.Entry(frame, width=15)
    stop_entry.grid(row=3, column=1, padx=10, pady=5)

    ttk.Label(frame, text="Keybind (e.g., Z):").grid(row=4, column=0, sticky="w", pady=5)
    key_entry = ttk.Entry(frame, width=15)
    key_entry.grid(row=4, column=1, padx=10, pady=5)
    key_entry.insert(0, "z")

    ttk.Label(frame, text="Click Mode:").grid(row=5, column=0, sticky="w", pady=5)
    click_mode_var = tk.StringVar(value="Rapid Click")  # Default mode
    click_mode_dropdown = ttk.Combobox(frame, textvariable=click_mode_var, values=["Rapid Click", "Hold"])
    click_mode_dropdown.grid(row=5, column=1, padx=10, pady=5)
    click_mode_dropdown.current(0)

    ttk.Button(frame, text="Save Settings", command=update_settings).grid(row=6, columnspan=2, pady=15)

    root.mainloop()

threading.Thread(target=open_gui).start()
threading.Thread(target=lambda: Listener(on_press=on_press).start()).start()