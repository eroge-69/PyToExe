# RoyalAdminTool.py - Parts 1–6 Combined

import customtkinter as ctk
import tkinter as tk
import os
import json
from tkinter import messagebox

# Initialize GUI appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

USER_DB = "users.json"

def ensure_user_db():
    if not os.path.exists(USER_DB):
        with open(USER_DB, 'w') as f:
            json.dump({"FR08EN": "Freddie91"}, f)

def validate_login(username, password):
    with open(USER_DB, 'r') as f:
        users = json.load(f)
    return users.get(username) == password

def add_user(username, password):
    with open(USER_DB, 'r') as f:
        users = json.load(f)
    users[username] = password
    with open(USER_DB, 'w') as f:
        json.dump(users, f)

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x300")
        self.title("Admin Login")
        self.resizable(False, False)

        ctk.CTkLabel(self, text="Username:").pack(pady=(40, 5))
        self.username_entry = ctk.CTkEntry(self)
        self.username_entry.pack()

        ctk.CTkLabel(self, text="Password:").pack(pady=5)
        self.password_entry = ctk.CTkEntry(self, show="*")
        self.password_entry.pack()

        ctk.CTkButton(self, text="Login", command=self.login).pack(pady=(20, 10))

    def login(self):
        user = self.username_entry.get()
        pwd = self.password_entry.get()
        if validate_login(user, pwd):
            self.destroy()
            App(user)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

class App(ctk.CTk):
    def __init__(self, username):
        super().__init__()
        self.title("RoyalAdminTool")
        self.geometry("1200x800")
        self.username = username
        self.configure(fg_color="#1e1e1e")

        self.sidebar = ctk.CTkFrame(self, width=60, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        self.content = ctk.CTkFrame(self)
        self.content.pack(side="right", fill="both", expand=True)

        self.sidebar_buttons = {}
        self.frames = {}

        self.create_sidebar()
        self.create_footer()
        self.switch_tab("Home")

    def create_sidebar(self):
        tabs = [
            ("Home", "🏠"),
            ("Custom Edits", "🧱"),
            ("Text Generator", "🔤"),
            ("Dino Spawner", "🦖"),
            ("Admin Commands", "🛠"),
            ("Settings", "⚙️"),
        ]

        for name, icon in tabs:
            frame = ctk.CTkFrame(self.content)
            self.frames[name] = frame

            btn = ctk.CTkButton(
                self.sidebar, text="", width=60, height=60, corner_radius=0,
                image=None, fg_color="transparent",
                command=lambda n=name: self.switch_tab(n), text_color="white",
                hover_color="#6f42c1"
            )
            btn.grid(row=len(self.sidebar_buttons), column=0, pady=2, padx=2, sticky="n")
            btn._text_label.configure(text=icon)
            self.sidebar_buttons[name] = btn

    def switch_tab(self, name):
        for frame in self.frames.values():
            frame.pack_forget()
        self.frames[name].pack(fill="both", expand=True)

    def create_footer(self):
        label = ctk.CTkLabel(
            self,
            text="Made By A2T1C",
            text_color="gray",
            font=("Courier New", 14, "bold")
        )
        label.place(relx=1.0, rely=1.0, x=-20, y=-20, anchor="se")

# Launch login window
ensure_user_db()
app = LoginWindow()
app.mainloop()

# Part 4: Dino Spawner Tab
class DinoSpawnerTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Select Dino:").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.dino_dropdown = ctk.CTkComboBox(self, values=["Rex", "Giga", "Shadowmane", "Desmodus"])
        self.dino_dropdown.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(self, text="Level:").grid(row=1, column=0, sticky="w", padx=10)
        self.level_entry = ctk.CTkEntry(self)
        self.level_entry.insert(0, "600")
        self.level_entry.grid(row=1, column=1, padx=10, pady=5)

        self.output_box = ctk.CTkTextbox(self, height=100)
        self.output_box.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        ctk.CTkButton(self, text="Generate Command", command=self.generate_command).grid(row=2, column=0, columnspan=2, pady=10)

    def generate_command(self):
        dino = self.dino_dropdown.get()
        level = self.level_entry.get()
        command = f"cheat gmsummon \"{dino}_Character_BP_C\" {level}"
        self.output_box.delete("0.0", "end")
        self.output_box.insert("end", command)

# Part 5: Admin Commands Tab
class AdminCommandsTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        commands = [
            ("Destroy Wild Dinos", "cheat DestroyWildDinos"),
            ("God Mode", "cheat god"),
            ("Fly", "cheat fly"),
            ("Teleport To Player", "cheat TeleportToPlayer <PlayerID>"),
            ("Give Item", "cheat giveitemnum 1 1 0"),
        ]

        for i, (label, cmd) in enumerate(commands):
            ctk.CTkButton(self, text=label, command=lambda c=cmd: self.copy_command(c)).pack(padx=10, pady=5, fill="x")

        self.output_box = ctk.CTkTextbox(self, height=80)
        self.output_box.pack(padx=10, pady=10, fill="x")

    def copy_command(self, cmd):
        self.output_box.delete("0.0", "end")
        self.output_box.insert("end", cmd)
        self.clipboard_clear()
        self.clipboard_append(cmd)

# Part 6: Custom Edits (Grid Editor + Text Spawner)
class CustomEditsTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_size = 15
        self.cells = []
        self.base_x, self.base_y, self.base_z = 0, 0, 0

        grid_frame = ctk.CTkFrame(self)
        grid_frame.pack(pady=10)

        for row in range(self.grid_size):
            row_cells = []
            for col in range(self.grid_size):
                var = tk.IntVar()
                cb = ctk.CTkCheckBox(grid_frame, variable=var, text="")
                cb.grid(row=row, column=col, padx=1, pady=1)
                row_cells.append(var)
            self.cells.append(row_cells)

        self.text_entry = ctk.CTkEntry(self)
        self.text_entry.pack(pady=10)

        ctk.CTkButton(self, text="Generate Text Spawn Commands", command=self.generate_text_commands).pack()
        self.output_box = ctk.CTkTextbox(self, height=200)
        self.output_box.pack(padx=10, pady=10, fill="both", expand=True)

    def generate_text_commands(self):
        text = self.text_entry.get().upper()
        commands = []
        offset = 200
        for i, letter in enumerate(text):
            cmd = f"c spawnactor \"Blueprint'/Game/Genesis2/Structures/LoadoutMannequin/Structure_LoadoutDummy_Hotbar.Structure_LoadoutDummy_Hotbar'\" {i * offset} 0 0"
            commands.append(cmd)
        self.output_box.delete("0.0", "end")
        self.output_box.insert("end", "
".join(commands))
