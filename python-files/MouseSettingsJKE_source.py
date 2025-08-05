
import ctypes
import tkinter as tk
from tkinter import messagebox

SPI_SETMOUSESPEED = 0x0071
SPI_GETMOUSESPEED = 0x0070
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02

def set_mouse_speed(speed):
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETMOUSESPEED, 0, speed, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)

def set_mouse_acceleration(enabled):
    mouse_params = (0, 0, 1) if enabled else (0, 0, 0)
    ctypes.windll.user32.SystemParametersInfoW(0x006B, 0, mouse_params, 0)

def apply_settings():
    speed = speed_var.get()
    accel = accel_var.get()
    set_mouse_speed(speed)
    set_mouse_acceleration(accel)
    messagebox.showinfo("Mouse Settings JKE", "Settings applied.")

root = tk.Tk()
root.title("Mouse Settings JKE")
root.configure(bg="black")

title = tk.Label(root, text="Mouse settings jke", fg="red", bg="black", font=("Arial", 18))
title.pack(pady=10)

speed_label = tk.Label(root, text="Pointer speed", fg="red", bg="black", font=("Arial", 12))
speed_label.pack()

speed_var = tk.IntVar(value=6)
speed_slider = tk.Scale(root, from_=1, to=11, orient=tk.HORIZONTAL, variable=speed_var, bg="black", fg="red",
                        troughcolor="red", highlightthickness=0)
speed_slider.pack()

accel_label = tk.Label(root, text="Mouse acceleration", fg="red", bg="black", font=("Arial", 12))
accel_label.pack(pady=(10, 0))

accel_var = tk.BooleanVar(value=False)
accel_check = tk.Checkbutton(root, variable=accel_var, bg="black", activebackground="black",
                             fg="red", activeforeground="red", selectcolor="black")
accel_check.pack()

ok_button = tk.Button(root, text="OK", command=apply_settings, fg="red", bg="black", activebackground="red", font=("Arial", 12))
ok_button.pack(pady=20)

root.mainloop()
