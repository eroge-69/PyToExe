
import tkinter as tk
from tkinter import messagebox
import pygame

pygame.mixer.init()
click_sound = pygame.mixer.Sound("click.wav")

def save_settings():
    click_sound.play()
    settings = {
        "ESP": esp_var.get(),
        "Aim Assist": aim_assist_var.get(),
        "Tracers": tracers_var.get(),
        "Skeleton ESP": skeleton_esp_var.get(),
        "FOV": fov_slider.get()
    }
    messagebox.showinfo("Saved", "Settings have been saved!")

root = tk.Tk()
root.title("Not A Cheat Menu")
root.geometry("320x400")
root.configure(bg="#0D1117")

frame = tk.LabelFrame(root, bg="#0D1117", bd=0)
frame.pack(padx=20, pady=20, fill="both", expand=True)

label_style = {"bg": "#0D1117", "fg": "yellow", "font": ("Arial", 14)}
checkbox_style = {"bg": "#0D1117", "fg": "yellow", "activeforeground": "yellow", "selectcolor": "#161b22"}
button_style = {"bg": "#238636", "fg": "yellow", "activebackground": "#2ea043", "font": ("Arial", 12)}

tk.Label(frame, text="Miron hieno juttu chatgpt.", **label_style).pack(pady=10)

esp_var = tk.BooleanVar()
aim_assist_var = tk.BooleanVar()
tracers_var = tk.BooleanVar()
skeleton_esp_var = tk.BooleanVar()

tk.Checkbutton(frame, text="ESP", variable=esp_var, **checkbox_style).pack(anchor="w", padx=60)
tk.Checkbutton(frame, text="Aim Assist", variable=aim_assist_var, **checkbox_style).pack(anchor="w", padx=60)
tk.Checkbutton(frame, text="Tracers", variable=tracers_var, **checkbox_style).pack(anchor="w", padx=60)
tk.Checkbutton(frame, text="Skeleton ESP", variable=skeleton_esp_var, **checkbox_style).pack(anchor="w", padx=60)

tk.Label(frame, text="FOV Slider", **label_style).pack(pady=5)
fov_slider = tk.Scale(frame, from_=10, to=180, orient=tk.HORIZONTAL, bg="#0D1117", fg="yellow", troughcolor="blue")
fov_slider.set(60)
fov_slider.pack()

tk.Button(frame, text="Save Settings", command=save_settings, **button_style).pack(pady=15)

root.mainloop()
