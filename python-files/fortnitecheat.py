import tkinter as tk

class CheatTab(tk.Frame):
    def __init__(self, master, title, options):
        super().__init__(master, bg="#23272A")
        tk.Label(self, text=title, bg="#23272A", fg="#7289DA", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=20, pady=(10, 20))
        for opt in options:
            var = tk.BooleanVar()
            cb = tk.Checkbutton(self, text=opt, variable=var, bg="#23272A", fg="#99AAB5",
                               font=("Segoe UI", 12), activebackground="#23272A", activeforeground="#7289DA",
                               selectcolor="#23272A", highlightthickness=0, bd=0)
            cb.pack(anchor="w", padx=40, pady=6)

class FakeCheatGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VYXON")
        self.geometry("600x400")
        self.configure(bg="#181A20")
        self.tabs = {
            "Visual": ("🟦 Visual", ["Wallhack", "Player ESP", "Loot ESP", "Night Mode", "No Fog"]),
            "Aimbot": ("🎯 Aimbot", ["Enable Aimbot", "Silent Aim", "Smooth Aim", "Trigger Bot", "Aim at Head", "Aim at Chest"]),
            "Misc": ("🛠️ Misc", ["No Recoil", "Speed Hack", "Infinite Jump", "Rainbow Skin", "Fake Victory"]),
            "Stopper": ("🛡️ Stopper", ["Anticheat Stopper", "Spoof HWID", "Fake Ban Protection", "Hide from Task Manager"])
        }
        self.selected_tab = None
        self.create_header()
        self.create_sidebar()
        self.create_content()
        self.show_tab("Visual")

    def create_header(self):
        header = tk.Frame(self, bg="#23272A", height=50)
        header.pack(fill="x", side="top")
        tk.Label(header, text="VYXON", bg="#23272A", fg="#7289DA",
                 font=("Segoe UI", 18, "bold")).pack(side="left", padx=20)
        tk.Label(header, text="", bg="#23272A", fg="#99AAB5",
                 font=("Segoe UI", 10)).pack(side="right", padx=20)

    def create_sidebar(self):
        self.sidebar = tk.Frame(self, bg="#181A20", width=120)
        self.sidebar.pack(fill="y", side="left", anchor="nw")
        for tab in self.tabs:
            btn = tk.Button(self.sidebar, text=self.tabs[tab][0], bg="#181A20", fg="#99AAB5",
                            font=("Segoe UI", 13, "bold"), bd=0, relief="flat", activebackground="#7289DA",
                            activeforeground="#23272A", command=lambda t=tab: self.show_tab(t))
            btn.pack(fill="x", pady=8, padx=0)

    def create_content(self):
        self.content = tk.Frame(self, bg="#23272A")
        self.content.pack(expand=True, fill="both", side="left")

    def show_tab(self, tab_name):
        for widget in self.content.winfo_children():
            widget.destroy()
        title, options = self.tabs[tab_name]
        tab_frame = CheatTab(self.content, title, options)
        tab_frame.pack(expand=True, fill="both")

if __name__ == "__main__":
    FakeCheatGUI().mainloop()