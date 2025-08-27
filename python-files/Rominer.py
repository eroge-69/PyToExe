import customtkinter as ctk
import random
import string
import time
from threading import Thread
import pyperclip  # pip install pyperclip

# Store codes
recent_codes = []

# Generate fake code
def generate_fake_code():
    return "-".join(
        "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
        for _ in range(4)
    )

# ---------------- Main App ----------------
class RobuxApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Robux Generator - PRANK")
        self.geometry("720x460")
        self.resizable(False, False)

        # Appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        # Info bar (top)
        self.infobar = ctk.CTkFrame(self, height=40, corner_radius=0)
        self.infobar.pack(side="top", fill="x")

        self.infobar_label = ctk.CTkLabel(
            self.infobar, text="⚡ If code isnt working please try again",
            font=("Segoe UI", 14, "bold"), anchor="w"
        )
        self.infobar_label.pack(side="left", padx=15)

        self.infobar_status = ctk.CTkLabel(
            self.infobar, text="Ready", font=("Segoe UI", 12), text_color="gray"
        )
        self.infobar_status.pack(side="right", padx=15)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=160, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        self.logo = ctk.CTkLabel(self.sidebar, text="⚡ Robux Gen", font=("Segoe UI", 22, "bold"))
        self.logo.pack(pady=30)

        self.btn_main = ctk.CTkButton(self.sidebar, text="Generator", command=self.show_main)
        self.btn_recent = ctk.CTkButton(self.sidebar, text="Recent Codes", command=self.show_recent)
        self.btn_settings = ctk.CTkButton(self.sidebar, text="Settings", command=self.show_settings)

        self.btn_main.pack(pady=5, fill="x")
        self.btn_recent.pack(pady=5, fill="x")
        self.btn_settings.pack(pady=5, fill="x")

        # Main container
        self.container = ctk.CTkFrame(self, corner_radius=10)
        self.container.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        # Pages
        self.pages = {}
        for P in (MainPage, RecentPage, SettingsPage):
            page = P(self.container, self)
            self.pages[P.__name__] = page
            page.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show_main()

    def show_main(self):
        self.pages["MainPage"].tkraise()
        self.update_status("Ready")

    def show_recent(self):
        self.pages["RecentPage"].update_codes()
        self.pages["RecentPage"].tkraise()
        self.update_status("Viewing recent codes")

    def show_settings(self):
        self.pages["SettingsPage"].tkraise()
        self.update_status("Adjust settings")

    def update_status(self, message, color="gray"):
        self.infobar_status.configure(text=message, text_color=color)

# ---------------- Main Page ----------------
class MainPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.title = ctk.CTkLabel(self, text="Robux Generator", font=("Segoe UI", 28, "bold"))
        self.title.pack(pady=25)

        self.status = ctk.CTkLabel(self, text="Click Generate to start", font=("Segoe UI", 14))
        self.status.pack(pady=15)

        self.progress = ctk.CTkProgressBar(self, width=400, height=15)
        self.progress.pack(pady=15)
        self.progress.set(0)

        self.code_display = ctk.CTkLabel(self, text="", font=("Consolas", 22, "bold"))
        self.code_display.pack(pady=20)

        self.copy_btn = ctk.CTkButton(self, text="Copy Code", width=120, state="disabled", command=self.copy_code)
        self.copy_btn.pack(pady=5)

        self.generate_btn = ctk.CTkButton(self, text="Generate Code", command=self.start_generation, width=240, height=40)
        self.generate_btn.pack(pady=15)

        self.footer = ctk.CTkLabel(self, text="(This is a prank, not real!)", font=("Segoe UI", 10), text_color="red")
        self.footer.pack(side="bottom", pady=10)

    def start_generation(self):
        self.generate_btn.configure(state="disabled")
        self.copy_btn.configure(state="disabled")
        self.status.configure(text="Generating...", text_color="orange")
        self.code_display.configure(text="")
        self.progress.set(0)
        self.controller.update_status("Generating code...", "orange")
        Thread(target=self.fake_progress).start()

    def fake_progress(self):
        for i in range(1, 101):
            time.sleep(0.02)
            self.progress.set(i/100)
        fake_code = generate_fake_code()
        recent_codes.append(fake_code)
        self.status.configure(text="✅ Code Generated!", text_color="green")
        self.code_display.configure(text=fake_code)
        self.copy_btn.configure(state="normal")
        self.generate_btn.configure(state="normal")
        self.controller.update_status("Code generated successfully!", "green")

    def copy_code(self):
        code = self.code_display.cget("text")
        if code:
            import pyperclip
            pyperclip.copy(code)
            self.controller.update_status("Code copied to clipboard!", "cyan")

# ---------------- Recent Codes Page ----------------
class RecentPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.title = ctk.CTkLabel(self, text="Recent Codes", font=("Segoe UI", 24, "bold"))
        self.title.pack(pady=20)

        self.codes_list = ctk.CTkTextbox(self, width=500, height=280, font=("Consolas", 14))
        self.codes_list.pack(pady=10)

    def update_codes(self):
        self.codes_list.delete("1.0", "end")
        for code in recent_codes[-10:][::-1]:
            self.codes_list.insert("end", code + "\n")

# ---------------- Settings Page ----------------
class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.title = ctk.CTkLabel(self, text="Settings", font=("Segoe UI", 24, "bold"))
        self.title.pack(pady=20)

        self.theme_toggle = ctk.CTkSwitch(self, text="Dark Mode", command=self.toggle_theme)
        self.theme_toggle.select()
        self.theme_toggle.pack(pady=10)

    def toggle_theme(self):
        if self.theme_toggle.get() == 1:
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")

# ---------------- Run ----------------
if __name__ == "__main__":
    app = RobuxApp()
    app.mainloop()
