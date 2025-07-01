import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

# ---------- Colors & fonts ----------
COLORS = {
    "bg": "#121212",
    "panel_bg": "#1e1e1e",
    "accent": "#bb86fc",
    "text_primary": "#e0e0e0",
    "text_secondary": "#a0a0a0",
    "button_bg": "#3700b3",
    "button_hover": "#6200ee",
    "toggle_on": "#03dac6",
    "toggle_off": "#555555",
    "border": "#333333",
}

FONTS = {
    "title": ("Segoe UI Semibold", 22),
    "subtitle": ("Segoe UI", 14),
    "text": ("Segoe UI", 11),
    "toggle": ("Segoe UI", 10, "bold"),
}

MOD_CATEGORIES = {
    "Il2Cpp": [
        "Bypass SigCheck", "Bypass Ban", "Patch Game"
    ],
    "PlayFab": [
        "Bypass Login", "Bypass CloudScript", "Disable Cloud Saves", "Fake Stats Return",
        "Auto Respawn", "Infinite Stamina"
    ],
    "Photon": [
        "No Lag", "Teleport Patch", "Ghost Mode", "Fake Ping", "Room Bypass",
        "Anti Kick", "Auto Reconnect"
    ]
}

class ToggleSwitch(tk.Canvas):
    def __init__(self, master, width=48, height=24, bg_off=COLORS["toggle_off"], bg_on=COLORS["toggle_on"], command=None, *args, **kwargs):
        super().__init__(master, width=width, height=height, bg=master["bg"], highlightthickness=0, *args, **kwargs)
        self.width = width
        self.height = height
        self.bg_off = bg_off
        self.bg_on = bg_on
        self.command = command
        self.is_on = False

        self.bind("<Button-1>", self.toggle)

        self.bg_rect = self.create_rounded_rect(0, 0, width, height, radius=height//2, fill=self.bg_off)
        self.knob = self.create_oval(2, 2, height-2, height-2, fill="#121212", outline="#999")

    def create_rounded_rect(self, x1, y1, x2, y2, radius=12, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def toggle(self, event=None):
        self.is_on = not self.is_on
        self.update_toggle()
        if self.command:
            self.command(self.is_on)

    def update_toggle(self):
        if self.is_on:
            self.itemconfig(self.bg_rect, fill=self.bg_on)
            self.coords(self.knob, self.width - self.height + 2, 2, self.width - 2, self.height - 2)
        else:
            self.itemconfig(self.bg_rect, fill=self.bg_off)
            self.coords(self.knob, 2, 2, self.height - 2, self.height - 2)

# ---------- Accordion Section ----------
class AccordionSection(tk.Frame):
    def __init__(self, master, title, mods, set_mod_state, mod_states, *args, **kwargs):
        super().__init__(master, bg=COLORS["panel_bg"], *args, **kwargs)
        self.title = title
        self.mods = mods
        self.set_mod_state = set_mod_state
        self.mod_states = mod_states
        self.is_expanded = False

        self.header = tk.Frame(self, bg=COLORS["panel_bg"])
        self.header.pack(fill="x")
        self.header.bind("<Button-1>", self.toggle)

        self.title_label = tk.Label(self.header, text=title, font=FONTS["subtitle"], fg=COLORS["accent"], bg=COLORS["panel_bg"])
        self.title_label.pack(side="left", padx=10, pady=8)
        self.title_label.bind("<Button-1>", self.toggle)

        self.arrow_label = tk.Label(self.header, text="▶", font=FONTS["subtitle"], fg=COLORS["accent"], bg=COLORS["panel_bg"])
        self.arrow_label.pack(side="right", padx=10)
        self.arrow_label.bind("<Button-1>", self.toggle)

        self.body = tk.Frame(self, bg=COLORS["panel_bg"])
        self.body.pack(fill="x", expand=False)
        self.body.forget()

        self.toggles = {}
        self.build_body()

    def build_body(self):
        for mod in self.mods:
            row = tk.Frame(self.body, bg=COLORS["panel_bg"])
            row.pack(fill="x", padx=20, pady=6)

            label = tk.Label(row, text=mod, font=FONTS["text"], fg=COLORS["text_primary"], bg=COLORS["panel_bg"])
            label.pack(side="left")

            toggle = ToggleSwitch(row, command=lambda s, m=mod: self.set_mod_state(m, s))
            toggle.pack(side="right")
            if mod in self.mod_states and self.mod_states[mod]:
                toggle.is_on = True
                toggle.update_toggle()
            self.toggles[mod] = toggle

    def toggle(self, event=None):
        if self.is_expanded:
            self.body.forget()
            self.arrow_label.config(text="▶")
            self.is_expanded = False
        else:
            self.body.pack(fill="x")
            self.arrow_label.config(text="▼")
            self.is_expanded = True

# ---------- Main App ----------
class UnityModderX(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("UnityModderX Revamped")
        self.geometry("960x640")
        self.configure(bg=COLORS["bg"])
        self.resizable(False, False)

        self.libil2cpp_path = None
        self.mod_states = {}

        self.create_header()
        self.create_main_panel()
        self.create_statusbar()
        self.create_inject_button()

    def create_header(self):
        header = tk.Frame(self, bg=COLORS["panel_bg"], height=60)
        header.pack(side="top", fill="x")

        title = tk.Label(header, text="UnityModderX", font=FONTS["title"], fg=COLORS["accent"], bg=COLORS["panel_bg"])
        title.pack(side="left", padx=20, pady=10)

        self.file_label = tk.Label(header, text="No file chosen", font=FONTS["text"], fg=COLORS["text_secondary"], bg=COLORS["panel_bg"])
        self.file_label.pack(side="left", padx=10)

        choose_btn = tk.Button(header, text="Choose libil2cpp.so", bg=COLORS["button_bg"], fg=COLORS["text_primary"],
                               activebackground=COLORS["button_hover"], font=FONTS["text"], relief="flat", padx=10, pady=5,
                               command=self.choose_file)
        choose_btn.pack(side="right", padx=20, pady=10)

    def create_main_panel(self):
        main_panel = tk.Frame(self, bg=COLORS["bg"])
        main_panel.pack(fill="both", expand=True, padx=15, pady=(5, 50))

        self.accordion_panel = tk.Frame(main_panel, bg=COLORS["panel_bg"], width=280)
        self.accordion_panel.pack(side="left", fill="y", pady=5, padx=(0, 15))

        self.accordion_sections = {}
        for category, mods in MOD_CATEGORIES.items():
            section = AccordionSection(self.accordion_panel, category, mods, self.set_mod_state, self.mod_states)
            section.pack(fill="x", pady=8)
            self.accordion_sections[category] = section

        self.info_panel = tk.Frame(main_panel, bg=COLORS["panel_bg"])
        self.info_panel.pack(side="left", fill="both", expand=True, pady=5)

        self.info_title = tk.Label(self.info_panel, text="Select mods from the categories on the left.", font=FONTS["subtitle"], fg=COLORS["text_primary"], bg=COLORS["panel_bg"])
        self.info_title.pack(pady=20, padx=20)

        self.info_text = tk.Text(self.info_panel, bg=COLORS["panel_bg"], fg=COLORS["text_secondary"], font=FONTS["text"], bd=0, wrap="word", height=15)
        self.info_text.insert("1.0", "Instructions:\n\n1. Choose the libil2cpp.so file.\n2. Expand categories on the left.\n3. Toggle desired mods.\n4. Click 'Inject Mods' to patch.\n\nEnjoy modding safely!")
        self.info_text.config(state="disabled")
        self.info_text.pack(fill="both", expand=True, padx=20, pady=(0,20))

    def create_statusbar(self):
        statusbar = tk.Frame(self, bg=COLORS["panel_bg"], height=28)
        statusbar.pack(side="bottom", fill="x")

        self.status_label = tk.Label(statusbar, text="Ready", font=FONTS["text"], fg=COLORS["text_secondary"], bg=COLORS["panel_bg"])
        self.status_label.pack(side="left", padx=15)

    def create_inject_button(self):
        inject_btn = tk.Button(self, text="💉 Inject Mods", bg=COLORS["button_bg"], fg=COLORS["text_primary"],
                               activebackground=COLORS["button_hover"], font=FONTS["subtitle"], relief="flat",
                               command=self.inject_mods)
        inject_btn.place(relx=0.88, rely=0.91, anchor="center")

    def choose_file(self):
        path = filedialog.askopenfilename(title="Select libil2cpp.so file",
                                          filetypes=[("Shared Object", "*.so"), ("All Files", "*.*")])
        if path:
            self.libil2cpp_path = path
            filename = os.path.basename(path)
            self.file_label.config(text=filename)
            self.status_label.config(text="File selected: " + filename)
        else:
            self.status_label.config(text="File selection cancelled")

    def set_mod_state(self, mod_name, state):
        self.mod_states[mod_name] = state
        self.status_label.config(text=f"Set '{mod_name}' to {'ON' if state else 'OFF'}")
        self.handle_mod_hook(mod_name, state)

    def handle_mod_hook(self, mod_name, state):
        if state:
            print(f"[HOOK ACTIVATED] {mod_name}")
        else:
            print(f"[HOOK DEACTIVATED] {mod_name}")

    def inject_mods(self):
        if not self.libil2cpp_path:
            messagebox.showwarning("No file selected", "Please choose the libil2cpp.so file first.")
            return

        selected_mods = [mod for mod, on in self.mod_states.items() if on]
        if not selected_mods:
            messagebox.showinfo("No mods selected", "Please select at least one mod to inject.")
            return
        
        # Hooking Code soon idk just wait

        self.status_label.config(text="Injecting mods...")
        print(f"Injecting mods into {self.libil2cpp_path}: {selected_mods}")
        messagebox.showinfo("Injection Complete", f"Injected mods:\n- " + "\n- ".join(selected_mods))
        self.status_label.config(text="Injection completed successfully!")

if __name__ == "__main__":
    app = UnityModderX()
    app.mainloop()
