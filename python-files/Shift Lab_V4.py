import tkinter as tk
from tkinter import messagebox, colorchooser
import serial
import os
import threading

# ---------- Serial Setup ----------
SERIAL_PORT = 'COM3'  # Change to your Arduino port
BAUD_RATE = 9600

try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE)
except:
    arduino = None
    print(f"Could not connect to {SERIAL_PORT}")

# ---------- User Credentials ----------
users = {
    "user": {"password": "1234", "role": "basic"},
    "KR": {"password": "6801", "role": "admin"}
}

current_role = None
checkbox_vars = []
main_window = None

# ---------- Relay Control ----------
def send_relay_states():
    states = ''.join(['1' if var.get() else '0' for var in checkbox_vars])
    print(f"Sending: {states}")
    if arduino:
        arduino.write(states.encode())

def set_all_relays(state):
    for var in checkbox_vars:
        var.set(state)
    send_relay_states()

# ---------- Exit ----------
def exit_app():
    if main_window:
        main_window.destroy()
    exit()

# ---------- User Switch ----------
def user_switch():
    if main_window:
        main_window.destroy()
    login_screen()

# ---------- Pick Background Color ----------
def pick_background_color():
    color = colorchooser.askcolor()[1]
    if color:
        main_window.config(bg=color)

# ---------- Build Main GUI ----------
def open_main_gui():
    global checkbox_vars, main_window
    main_window = tk.Tk()
    main_window.title("Shift Lab_V4")

    # ----- Menu Bar -----
    menubar = tk.Menu(main_window)

    menu_menu = tk.Menu(menubar, tearoff=0)
    menu_menu.add_command(label="User Switch", command=user_switch)
    menubar.add_cascade(label="Menu", menu=menu_menu)

    menubar.add_command(label="Exit", command=exit_app)

    main_window.config(menu=menubar)

    # ----- Relay Checkboxes -----
    checkbox_vars = [tk.IntVar() for _ in range(64)]

    for i in range(64):
        cb = tk.Checkbutton(main_window, text=f"{i+1}", variable=checkbox_vars[i], command=send_relay_states)
        cb.grid(row=(i // 8) + 1, column=i % 8, padx=5, pady=5)

    # ----- Admin Buttons: ALL ON/OFF -----
    if current_role == "admin":
        control_frame = tk.Frame(main_window)
        control_frame.grid(row=9, column=0, columnspan=8, pady=10)

        tk.Button(control_frame, text="Turn ALL ON", width=15, command=lambda: set_all_relays(1)).pack(side=tk.LEFT, padx=10)
        tk.Button(control_frame, text="Turn ALL OFF", width=15, command=lambda: set_all_relays(0)).pack(side=tk.LEFT, padx=10)

    main_window.mainloop()

# ---------- Login ----------
def check_login():
    global current_role
    entered_user = username_entry.get()
    entered_pass = password_entry.get()

    if entered_user in users and users[entered_user]["password"] == entered_pass:
        current_role = users[entered_user]["role"]
        login_window.destroy()
        open_main_gui()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

def login_screen():
    global login_window, username_entry, password_entry

    login_window = tk.Tk()
    login_window.title("Login")
    login_window.geometry("300x150")

    tk.Label(login_window, text="Username:").pack(pady=(10, 0))
    username_entry = tk.Entry(login_window)
    username_entry.pack()

    tk.Label(login_window, text="Password:").pack()
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack()

    tk.Button(login_window, text="Login", command=check_login).pack(pady=10)

    login_window.mainloop()

# ---------- Start the App ----------
login_screen()
