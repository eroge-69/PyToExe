import tkinter as tk
import customtkinter as ctk
import random
import threading
import time
import sys
import winsound
import pyautogui
from pynput.mouse import Listener, Button
from ctypes import windll
from PIL import Image, ImageTk

# Globale Zustände
running = False
alive = True
right_mouse_pressed = False
search_color = 5197761
click_delay = 0.25

# Windows API für Pixel-Erkennung
user = windll.LoadLibrary('user32.dll')
dc = user.GetDC(0)
gdi = windll.LoadLibrary('gdi32.dll')

# Modern UI Setup
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('dark-blue')

app = ctk.CTk()
app.title(' Exe Trigger v2')
app.geometry('300x500')
app.resizable(False, False)

# Main container
main_container = ctk.CTkFrame(app, fg_color='#0a0a0a')
main_container.pack(fill='both', expand=True, padx=2, pady=2)

# Title section
title_frame = ctk.CTkFrame(main_container, fg_color='transparent')
title_frame.pack(fill='x', pady=(30, 40))

title_label = ctk.CTkLabel(title_frame, text='Exe Trigger v2',
                          font=('Consolas', 16, 'bold'),
                          text_color='white')
title_label.pack()

# Status section
status_frame = ctk.CTkFrame(main_container, fg_color='#111111', corner_radius=10)
status_frame.pack(fill='x', pady=(0, 30), padx=20)

status_container = ctk.CTkFrame(status_frame, fg_color='transparent')
status_container.pack(pady=20)

status_label = ctk.CTkLabel(status_container, text='INACTIVE',
                           text_color='#666666',
                           font=('Consolas', 24, 'bold'))
status_label.pack()

# Delay section
delay_frame = ctk.CTkFrame(main_container, fg_color='#111111', corner_radius=10)
delay_frame.pack(fill='x', pady=(0, 30), padx=20)

delay_container = ctk.CTkFrame(delay_frame, fg_color='transparent')
delay_container.pack(pady=20)

delay_value_label = ctk.CTkLabel(delay_container, text='250ms',
                                text_color='white',
                                font=('Consolas', 24, 'bold'))
delay_value_label.pack()

# Custom slider style
slider = ctk.CTkSlider(delay_frame, from_=0, to=500,
                      button_color='white',
                      progress_color='white',
                      button_hover_color='#cccccc',
                      height=4,
                      button_corner_radius=10,
                      button_length=20,
                      command=lambda v: update_slider_label(v))
slider.set(250)
slider.pack(fill='x', pady=(0, 20), padx=20)


# Control buttons
button_frame = ctk.CTkFrame(main_container, fg_color='transparent')
button_frame.pack(fill='x', pady=(0, 30), padx=20)

start_button = ctk.CTkButton(button_frame, text='START',
                            fg_color='white',
                            text_color='black',
                            hover_color='#cccccc',
                            font=('Consolas', 14, 'bold'),
                            height=45,
                            corner_radius=8,
                            command=lambda: toggle_clicker())
start_button.pack(fill='x', pady=(0, 10))

kill_button = ctk.CTkButton(button_frame, text='EXIT',
                           fg_color='#111111',
                           text_color='white',
                           hover_color='#222222',
                           font=('Consolas', 14, 'bold'),
                           height=45,
                           corner_radius=8,
                           command=lambda: kill_script())
kill_button.pack(fill='x')

# Footer
footer_label = ctk.CTkLabel(main_container, text='made by marcello and lores EXE  SERVICE',
                           text_color='#666666',
                           font=('Consolas', 10))
footer_label.pack(side='bottom', pady=20)

# Funktionen
def kill_script():
    global alive
    alive = False
    app.destroy()
    sys.exit()

def get_pixel():
    x = user.GetSystemMetrics(0) // 2
    y = user.GetSystemMetrics(1) // 2
    return gdi.GetPixel(dc, x, y)

def change_pixel_color():
    global search_color
    search_color = get_pixel()
    winsound.PlaySound('SystemAsterisk', winsound.SND_ALIAS)

def check():
    try:
        if get_pixel() == search_color:
            pyautogui.mouseDown()
            time.sleep(random.uniform(0.06, 0.2))
            pyautogui.mouseUp()
    except pyautogui.FailSafeException:
        return None

def on_click(x, y, button, pressed):
    global right_mouse_pressed
    if button == Button.right:
        right_mouse_pressed = pressed
    return None

def run_clicker():
    if alive:
        if running and right_mouse_pressed:
            check()
        time.sleep(click_delay)

def click_loop():
    while alive:
        run_clicker()

def toggle_clicker():
    global running
    running = not running
    status_label.configure(text='ACTIVE' if running else 'INACTIVE')
    status_label.configure(text_color='white' if running else '#666666')
    start_button.configure(text='STOP' if running else 'START')

def update_slider_label(value):
    global click_delay
    click_delay = float(value) / 1000.0
    delay_value_label.configure(text=f'{int(float(value))}ms')

# Listener & Thread starten
mouse_listener = Listener(on_click=on_click)
mouse_listener.start()

threading.Thread(target=click_loop, daemon=True).start()

# GUI starten
app.mainloop()
