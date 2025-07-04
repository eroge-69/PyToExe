import customtkinter as ctk
import subprocess
import webbrowser
import os

# Paths to your .lnk or executable files
APP_PATHS = {
    "Discord": r"C:\Users\karfi\OneDrive\Počítač\spyfi mod\files\dsc.lnk",
    "Discord PTB": r"C:\Users\karfi\OneDrive\Počítač\spyfi mod\files\dscptb.lnk",
    "FL Studio": r"C:\Users\karfi\OneDrive\Počítač\spyfi mod\files\flstudio.lnk",
    "VPS": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    "vibranceGUI": r"C:\Users\karfi\OneDrive\Počítač\vibranceGUI.exe"
}

# VPS URL
VPS_URL = "https://panel.pebblehost.com/server/007668a4/files"

# GUI setup
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SpyfiApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Spyfi Mod - by Spify")
        self.geometry("400x540")
        self.resizable(False, False)

        self.login_screen()

    def login_screen(self):
        self.clear_widgets()

        ctk.CTkLabel(self, text="Please log in", font=("Arial", 22, "bold")).pack(pady=20)

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username")
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=10)

        ctk.CTkButton(self, text="Login", command=self.check_login).pack(pady=10)
        self.message_label = ctk.CTkLabel(self, text="")
        self.message_label.pack(pady=5)

    def check_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "Spify" and password == "2367":
            self.menu_screen()
        else:
            self.message_label.configure(text="Invalid credentials", text_color="red")

    def menu_screen(self):
        self.clear_widgets()

        ctk.CTkLabel(self, text="☰ Spyfi Launcher", font=("Arial", 24, "bold")).pack(pady=10)
        ctk.CTkLabel(self, text="Choose an option:", font=("Arial", 16)).pack(pady=5)

        # Buttons (like profiles in Steam login)
        self.create_menu_button("1) Discord", lambda: self.launch_app("Discord"))
        self.create_menu_button("2) Discord PTB", lambda: self.launch_app("Discord PTB"))
        self.create_menu_button("3) FL Studio", lambda: self.launch_app("FL Studio"))
        self.create_menu_button("4) VPS", self.open_vps)
        self.create_menu_button("5) vibranceGUI", lambda: self.launch_app("vibranceGUI"))
        self.create_menu_button("6) Credits", self.show_credits)

    def create_menu_button(self, text, command):
        ctk.CTkButton(self, text=text, font=("Arial", 14), width=250, height=40, command=command).pack(pady=6)

    def launch_app(self, app_name):
        path = APP_PATHS.get(app_name)
        if path:
            try:
                os.startfile(path)
            except Exception as e:
                print(f"Error opening {app_name}: {e}")

    def open_vps(self):
        try:
            subprocess.Popen([APP_PATHS["VPS"], VPS_URL])
        except Exception as e:
            print(f"Could not open VPS: {e}")

    def show_credits(self):
        self.clear_widgets()
        ctk.CTkLabel(self, text="Spyfi Mod by Spify", font=("Arial", 20)).pack(pady=20)
        ctk.CTkButton(self, text="Back to Menu", command=self.menu_screen).pack(pady=10)

    def clear_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

# Run the app
if __name__ == "__main__":
    app = SpyfiApp()
    app.mainloop()
