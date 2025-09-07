import tkinter as tk
from tkinter import ttk

BG_COLOR = "#0e0e0e"
SIDEBAR_COLOR = "#1a1a1a"
PANEL_COLOR = "#121212"
TEXT_COLOR = "white"
ACCENT_COLOR = "#ff9933"
class SettingsMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("K Services Crusader")
        self.geometry("820x520")
        self.configure(bg=BG_COLOR)

        # ttk styling for dark theme
        style = ttk.Style(self)
        style.theme_use("clam")

        # Transparent checkboxes
        style.configure("TCheckbutton",
                        background=PANEL_COLOR,
                        foreground=TEXT_COLOR,
                        focuscolor=PANEL_COLOR)

        # Transparent sliders
        style.configure("TScale",
                        background=PANEL_COLOR,
                        troughcolor=BG_COLOR,
                        sliderrelief="flat")

        # Dark combobox
        style.configure("TCombobox",
                        fieldbackground=PANEL_COLOR,
                        background=PANEL_COLOR,
                        foreground=TEXT_COLOR)
        style.map("TCombobox",
                  fieldbackground=[("readonly", PANEL_COLOR)],
                  foreground=[("readonly", TEXT_COLOR)],
                  background=[("readonly", PANEL_COLOR)])

        # Sidebar
        sidebar = tk.Frame(self, bg=SIDEBAR_COLOR, width=160)
        sidebar.pack(side="left", fill="y")

        tk.Label(sidebar, text="Settings", fg=TEXT_COLOR, bg=SIDEBAR_COLOR,
                 font=("Arial", 14, "bold")).pack(pady=20, anchor="w", padx=20)

        # Sidebar buttons
        self.tabs = {}
        for tab in ["Aimbot", "Visual", "Performance"]:
            btn = tk.Button(sidebar, text=tab, font=("Arial", 12),
                            fg=TEXT_COLOR, bg=SIDEBAR_COLOR, relief="flat",
                            activebackground=PANEL_COLOR,
                            command=lambda t=tab: self.show_tab(t))
            btn.pack(fill="x", pady=5, padx=10, anchor="w")
            self.tabs[tab] = btn

        # Main panel
        self.main_panel = tk.Frame(self, bg=PANEL_COLOR)
        self.main_panel.pack(side="left", fill="both", expand=True)

        self.show_tab("Aimbot")

    def show_tab(self, tab_name):
        # Clear previous panel
        for widget in self.main_panel.winfo_children():
            widget.destroy()

        if tab_name == "Aimbot":
            self.build_aimbot_tab()

        elif tab_name == "Visual":
            self.build_visual_tab()

        elif tab_name == "Performance":
            tk.Label(self.main_panel, text="Performance Settings",
                     fg=TEXT_COLOR, bg=PANEL_COLOR, font=("Arial", 18, "bold")).pack(pady=20)

    # ---------- AIMBOT TAB ----------
    def build_aimbot_tab(self):
        tk.Label(self.main_panel, text="Aimbot Settings", fg=TEXT_COLOR,
                 bg=PANEL_COLOR, font=("Arial", 18, "bold")).pack(pady=20, anchor="w", padx=20)

        # Enable Aimbot
        self.add_toggle("Enable Aimbot")

        # Aimbot Key Dropdown
        self.add_dropdown("Aimbot Key", ["Right Mouse", "Left Mouse", "Shift", "Ctrl"])

        # Target Bone Dropdown
        self.add_dropdown("Target Bone", ["Head", "Neck", "Chest"])

        # Draw FOV toggle
        self.add_toggle("Draw FOV✅")

        # Sliders
        self.add_slider("FOV Size✅", "Controls aiming field of view", 50)
        self.add_slider("Sensitivity✅", "Adjusts aim speed", 70)
        self.add_slider("Smoothness✅", "Aiming transition smoothness", 40)

    # ---------- VISUAL TAB (ESP) ----------
    def build_visual_tab(self):
        tk.Label(self.main_panel, text="Visual Settings", fg=TEXT_COLOR,
                 bg=PANEL_COLOR, font=("Arial", 18, "bold")).pack(pady=20, anchor="w", padx=20)

        # ESP Master Toggle
        self.add_toggle("Enable ESP")

        # ESP Options
        self.add_checkbox("Show Player Boxes✅")
        self.add_checkbox("Show Health Bars✅")
        self.add_checkbox("Show Names✅")
        self.add_checkbox("Show Distance✅")
        self.add_checkbox("Show Items✅")

        # Example slider for ESP range
        self.add_slider("ESP Range", "How far ESP elements are visible", 50)

    # ---------- HELPERS ----------
    def add_toggle(self, text):
        frame = tk.Frame(self.main_panel, bg=PANEL_COLOR)
        frame.pack(fill="x", pady=10, padx=20)
        tk.Label(frame, text=text, fg=TEXT_COLOR, bg=PANEL_COLOR,
                 font=("Arial", 12)).pack(side="left", anchor="w")
        var = tk.BooleanVar()
        ttk.Checkbutton(frame, variable=var, style="TCheckbutton").pack(side="right")

    def add_checkbox(self, text):
        frame = tk.Frame(self.main_panel, bg=PANEL_COLOR)
        frame.pack(fill="x", pady=5, padx=40)
        var = tk.BooleanVar()
        chk = ttk.Checkbutton(frame, text=text, variable=var, style="TCheckbutton")
        chk.pack(anchor="w")

    def add_dropdown(self, label, options):
        frame = tk.Frame(self.main_panel, bg=PANEL_COLOR)
        frame.pack(fill="x", pady=10, padx=20)
        tk.Label(frame, text=label, fg=TEXT_COLOR, bg=PANEL_COLOR,
                 font=("Arial", 12)).pack(side="left")
        combo = ttk.Combobox(frame, values=options, state="readonly", style="TCombobox")
        combo.current(0)
        combo.pack(side="right")

    def add_slider(self, title, subtitle, default_value):
        frame = tk.Frame(self.main_panel, bg=PANEL_COLOR)
        frame.pack(fill="x", pady=15, padx=20)

        # Title
        title_frame = tk.Frame(frame, bg=PANEL_COLOR)
        title_frame.pack(fill="x")
        tk.Label(title_frame, text=title, fg=TEXT_COLOR, bg=PANEL_COLOR,
                 font=("Arial", 12)).pack(side="left", anchor="w")

        # Value label
        value_label = tk.Label(title_frame, text=f"{default_value}", fg=TEXT_COLOR,
                               bg=PANEL_COLOR, font=("Arial", 12))
        value_label.pack(side="right")

        # Slider
        var = tk.IntVar(value=default_value)
        slider = ttk.Scale(frame, from_=0, to=100, orient="horizontal", variable=var,
                           style="TScale",
                           command=lambda v: value_label.config(text=f"{int(float(v))}"))
        slider.pack(fill="x", pady=5)

        # Subtitle
        tk.Label(frame, text=subtitle, fg="gray", bg=PANEL_COLOR,
                 font=("Arial", 9)).pack(anchor="w")


if __name__ == "__main__":
    app = SettingsMenu()
    app.mainloop()
