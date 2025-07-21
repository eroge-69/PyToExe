import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
import winsound  # ✅ Added for sound playback
import json
import os
import sys

# XP needed per level (Level: XP to reach this level from previous)
LEVELS = {
    1: 0,
    2: 300,
    3: 600,
    4: 1800,
    5: 3800,
    6: 7500,
    7: 9000,
    8: 11000,
    9: 14000,
    10: 16000,
    11: 21000,
    12: 15000,
    13: 20000,
    14: 20000,
    15: 25000,
    16: 30000,
    17: 30000,
    18: 40000,
    19: 40000,
    20: 50000
}


def resource_path(relative_path):
    """ Get absolute path to resource for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)


def get_total_xp_for_level(level):
    xp = 0
    for i in range(1, level):
        xp += LEVELS[i + 1]
    return xp


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb_color):
    return '#{:02x}{:02x}{:02x}'.format(*rgb_color)


def interpolate_color(c1, c2, factor: float):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * factor) for i in range(3))


class SmoothRainbowProgressBar(tk.Canvas):
    def __init__(self, parent, length=400, height=25, **kwargs):
        super().__init__(parent, width=length, height=height, **kwargs)
        self.length = length
        self.height = height

        self.colors = [
            "#FF0000", "#FF7F00", "#FFFF00", "#7FFF00", "#00FF00",
            "#00FF7F", "#00FFFF", "#007FFF", "#0000FF", "#7F00FF",
            "#FF00FF"
        ]
        self.rgb_colors = [hex_to_rgb(c) for c in self.colors]

        self.background_color = "#ddd"
        self.bg_rect = self.create_rectangle(0, 0, self.length, self.height, fill=self.background_color, width=0)

        self.filled_rects = []

    def set_progress(self, percent):
        for rect in self.filled_rects:
            self.delete(rect)
        self.filled_rects.clear()

        fill_width = int((percent / 100) * self.length)
        if fill_width == 0:
            return

        total_segments = len(self.rgb_colors) - 1
        for x in range(fill_width):
            rel_pos = x / max(fill_width - 1, 1)
            segment_pos = rel_pos * total_segments
            segment_index = int(segment_pos)
            segment_factor = segment_pos - segment_index

            c1 = self.rgb_colors[segment_index]
            c2 = self.rgb_colors[min(segment_index + 1, total_segments)]

            color = interpolate_color(c1, c2, segment_factor)
            hex_color = rgb_to_hex(color)

            rect = self.create_rectangle(x, 0, x + 1, self.height, fill=hex_color, width=0)
            self.filled_rects.append(rect)


class XPTracker:
    def __init__(self, root):
        self.root = root
        self.set_window_icon(self.root)  # Set icon on main window
        self.root.title("D&D XP Tracker")

        self.party_name = ""
        self.player_names = []
        self.total_xp = 0
        self.current_level = 1
        self.target_xp = 0
        self.dm_window = None
        self.level_up_label = None

        self.setup_window()

    def set_window_icon(self, window):
        try:
            window.iconbitmap("icon.ico")
        except Exception as e:
            print(f"Failed to set icon on window: {e}")

    def setup_window(self):
        setup = tk.Toplevel(self.root)
        self.set_window_icon(setup)  # Set icon on setup window
        setup.title("Setup")

        container = tk.Frame(setup)
        container.pack(anchor='n', pady=10, padx=50)  # Center horizontally, align to top

        # Party Name label and entry
        tk.Label(container, text="Party Name:", width=15, anchor='w').grid(row=0, column=0, sticky='w', pady=5)
        self.party_entry = tk.Entry(container, width=25)
        self.party_entry.grid(row=0, column=1, sticky='w', pady=5)
        self.party_entry.insert(0, "The Fluffy Menaces")

        # Number of Players label and combobox
        tk.Label(container, text="Number of Players:", width=15, anchor='w').grid(row=1, column=0, sticky='w', pady=5)
        self.num_players_var = tk.IntVar(value=3)
        num_players_cb = ttk.Combobox(container, textvariable=self.num_players_var, values=list(range(1, 13)), state="readonly", width=23)
        num_players_cb.grid(row=1, column=1, sticky='w', pady=5)

        # Players frame
        self.players_frame = tk.Frame(container)
        self.players_frame.grid(row=2, column=0, columnspan=2, pady=10)

        self.player_name_entries = []
        default_names = ["Plum", "Chubs", "Strawberry"]

        def create_player_entries():
            for widget in self.players_frame.winfo_children():
                widget.destroy()
            self.player_name_entries.clear()

            num = self.num_players_var.get()
            for i in range(num):
                lbl = tk.Label(self.players_frame, text=f"Player {i+1}:", width=15, anchor='w')
                lbl.grid(row=i, column=0, sticky='w', pady=2)
                entry = tk.Entry(self.players_frame, width=25)
                entry.grid(row=i, column=1, sticky='w', pady=2)
                if i < len(default_names):
                    entry.insert(0, default_names[i])
                self.player_name_entries.append(entry)

        create_player_entries()

        def on_num_players_change(event):
            create_player_entries()

        num_players_cb.bind("<<ComboboxSelected>>", on_num_players_change)

        # Level input
        tk.Label(container, text="Current Level (1-20):", width=15, anchor='w').grid(row=3, column=0, sticky='w', pady=5)
        self.level_var = tk.IntVar(value=1)
        self.level_entry = tk.Spinbox(container, from_=1, to=20, width=5, textvariable=self.level_var)
        self.level_entry.grid(row=3, column=1, sticky='w', pady=5)

        # Total XP input
        tk.Label(container, text="Total XP:", width=15, anchor='w').grid(row=4, column=0, sticky='w', pady=5)
        self.xp_var = tk.IntVar(value=0)
        self.xp_entry = tk.Entry(container, width=10, textvariable=self.xp_var)
        self.xp_entry.grid(row=4, column=1, sticky='w', pady=5)

        # Buttons frame
        buttons_frame = tk.Frame(container)
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=10)

        tk.Button(buttons_frame, text="Load Game", command=lambda: self.load_data(setup)).pack(side='left', padx=5)  # Load button in setup
        tk.Button(buttons_frame, text="Start Tracking", command=lambda: self.start_tracker(setup)).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="Exit", command=setup.destroy).pack(side='left', padx=5)

        # Optional: Dynamically resize window based on content
        setup.update_idletasks()
        setup.minsize(setup.winfo_width(), setup.winfo_height())

    def start_tracker(self, setup_window):
        self.party_name = self.party_entry.get()
        names = [entry.get().strip() for entry in self.player_name_entries if entry.get().strip()]
        if len(names) != len(set(names)):
            messagebox.showerror("Error", "Duplicate player names are not allowed.")
            return
        self.player_names = names

        # Use loaded XP and level if available
        if hasattr(self, "loaded_total_xp") and hasattr(self, "loaded_current_level"):
            self.total_xp = self.loaded_total_xp
            self.current_level = self.loaded_current_level
            del self.loaded_total_xp
            del self.loaded_current_level
        else:
            # Otherwise, use values from the input boxes
            level = self.level_var.get()
            xp = self.xp_var.get()
            if level < 1 or level > 20:
                messagebox.showerror("Error", "Level must be between 1 and 20.")
                return
            if xp < 0:
                messagebox.showerror("Error", "XP must be zero or positive.")
                return
            self.current_level = level
            self.total_xp = xp

        setup_window.destroy()
        self.build_main_window()
        self.build_dm_window()

    def build_main_window(self):
        self.root.configure(bg="#f4ecd8")
        self.root.geometry("800x325")  # ✅ Resizes the XP Tracker window
        self.root.deiconify()

        frame = tk.Frame(self.root, bg="#e5d7b3", bd=4, relief="ridge")
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        level_font = ("BlackChancery", 28, "bold")
        xp_font = ("BlackChancery", 16)
        party_font = ("BlackChancery", 34, "bold")
        player_font = ("BlackChancery", 14)

        tk.Label(frame, text=f"{self.party_name}", font=party_font, bg="#e5d7b3", fg="#5a3e1b").pack(pady=10)
        tk.Label(frame, text="Players: " + ", ".join(self.player_names), font=player_font, bg="#e5d7b3", fg="#5a3e1b").pack()

        self.level_label = tk.Label(frame, text=f"Level: {self.current_level}", font=level_font, bg="#e5d7b3", fg="#704214")
        self.level_label.pack(pady=(10, 0))

        self.progress = SmoothRainbowProgressBar(frame, length=400, height=25, bg="#e5d7b3", highlightthickness=0)
        self.progress.pack(pady=5)

        self.xp_label = tk.Label(frame, text="", font=xp_font, bg="#e5d7b3", fg="#5a3e1b")
        self.xp_label.pack(pady=(0, 0))

        self.level_up_label = tk.Label(frame, text="", fg="#4b5320", font=("Book Antiqua", 14, "bold"), bg="#e5d7b3")
        self.level_up_label.pack(pady=(0, 0))

        self.update_progress()

    def build_dm_window(self):
        self.dm_window = tk.Toplevel(self.root)
        self.set_window_icon(self.dm_window)  # Set icon on DM window
        self.dm_window.title("DM Control Panel")

        tk.Label(self.dm_window, text="DM Control Panel", font=("Helvetica", 12, "bold")).pack(pady=10,padx=30)
        tk.Button(self.dm_window, text="Add XP", command=self.prompt_add_xp).pack(pady=5)
        tk.Button(self.dm_window, text="Set Total XP", command=self.prompt_set_xp).pack(pady=5)
        tk.Button(self.dm_window, text="Set Level", command=self.prompt_set_level).pack(pady=5)

        tk.Button(self.dm_window, text="Save Game", command=self.save_data).pack(pady=5)  # Save button on DM panel
        tk.Button(self.dm_window, text="Setup", command=self.reset_to_setup).pack(pady=5)
        tk.Button(self.dm_window, text="Exit", fg="red", command=self.root.destroy).pack(pady=(5,20))

    def reset_to_setup(self):
        if self.dm_window:
            self.dm_window.destroy()
            self.dm_window = None

        for widget in self.root.winfo_children():
            widget.destroy()

        self.party_name = ""
        self.player_names = []
        self.total_xp = 0
        self.current_level = 1
        self.target_xp = 0
        self.level_up_label = None

        self.setup_window()

    def prompt_add_xp(self):
        xp = simpledialog.askinteger("Add XP", "How much XP to add?", parent=self.dm_window)
        if xp is not None:
            self.animate_xp_gain(xp)

    def prompt_set_xp(self):
        xp = simpledialog.askinteger("Set XP", "Enter total XP:", parent=self.dm_window)
        if xp is not None and xp >= 0:
            self.total_xp = xp
            self.recalculate_level()
            self.update_progress()

    def prompt_set_level(self):
        level = simpledialog.askinteger("Set Level", "Enter level (1–20):", parent=self.dm_window)
        if level is not None and 1 <= level <= 20:
            self.current_level = level
            self.total_xp = get_total_xp_for_level(level)
            self.update_progress()

    def animate_xp_gain(self, xp_to_add):
        self.target_xp = self.total_xp + xp_to_add
        winsound.PlaySound("xp.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)  # ✅ XP sound
        self.animate_step()

    def animate_step(self):
        if self.total_xp >= self.target_xp:
            return

        current_level_xp = get_total_xp_for_level(self.current_level)
        next_level_xp = get_total_xp_for_level(self.current_level + 1) if self.current_level < 20 else float('inf')
        xp_to_next_level = next_level_xp - self.total_xp

        xp_left = self.target_xp - self.total_xp

        # Level speed scale starting lower at 0.1 for level 1, increasing by 0.12 per level
        level_speed = 0.3 + (self.current_level - 1) * 0.2
        level_speed = min(level_speed, 4.0)  # Cap max speed

        # Base step sizes and delays depending on xp_left
        if xp_left > 100:
            base_step = 50
            base_delay = 15
        elif xp_left > 20:
            base_step = 20
            base_delay = 40
        else:
            base_step = 5
            base_delay = 90

        # Easier easing: use squared easing factor to smooth slow down
        easing_factor = xp_left / max(self.target_xp * 0.15, 1)
        easing_factor = min(max(easing_factor, 0.05), 1)  # Clamp between 0.05 and 1
        easing_factor = easing_factor ** 2  # Squared for smoother ease-out

        delay = int(base_delay / level_speed * (1 / easing_factor))
        delay = max(10, min(delay, 150))  # Delay between 10ms and 150ms

        step = min(int(base_step * level_speed), xp_left, xp_to_next_level)

        self.total_xp += step
        self.update_progress()

        if self.total_xp >= next_level_xp and self.current_level < 20:
            self.root.update()
            self.root.after(500, self.level_up)
        else:
            self.root.after(delay, self.animate_step)

    def level_up(self):
        self.current_level += 1
        winsound.PlaySound("levelup.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
        self.show_level_up_message(f"Leveled up to Level {self.current_level}!")
        self.update_progress()
        self.root.update_idletasks()  # Force update so label refreshes immediately
        self.root.after(3000, self.hide_level_up_message)

    def show_level_up_message(self, text):
        self.level_up_label.config(text=text)

    def hide_level_up_message(self):
        self.level_up_label.config(text="")
        self.animate_step()

    def update_progress(self):
        if self.current_level >= 20:
            self.progress.set_progress(100)
            self.level_label.config(text="Level: 20 (Max)")
            self.xp_label.config(text="")
            return

        current_level_xp = get_total_xp_for_level(self.current_level)
        next_level_xp = get_total_xp_for_level(self.current_level + 1)

        range_xp = next_level_xp - current_level_xp
        xp_into_level = self.total_xp - current_level_xp
        percent = (xp_into_level / range_xp) * 100 if range_xp != 0 else 100

        self.progress.set_progress(percent)
        self.level_label.config(text=f"Level: {self.current_level}")
        self.xp_label.config(text=f"{xp_into_level} / {range_xp} XP")

    def recalculate_level(self):
        for lvl in range(1, 21):
            if self.total_xp < get_total_xp_for_level(lvl + 1):
                self.current_level = lvl
                return
        self.current_level = 20

    def save_data(self):
        save_dir = "saves"
        os.makedirs(save_dir, exist_ok=True)

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialdir=save_dir,
            title="Save Game",
            filetypes=[("JSON Files", "*.json")],
        )
        if not file_path:
            return  # Cancelled

        data = {
            "party_name": self.party_name,
            "player_names": self.player_names,
            "total_xp": self.total_xp,
            "current_level": self.current_level
        }

        try:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo("Save", "Game saved successfully.")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save game:\n{e}")

    def load_data(self, setup_window=None):
        save_dir = "saves"
        os.makedirs(save_dir, exist_ok=True)

        file_path = filedialog.askopenfilename(
            initialdir=save_dir,
            title="Load Game",
            filetypes=[("JSON Files", "*.json")],
        )
        if not file_path:
            return

        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            self.party_name = data.get("party_name", "The Fluffy Menaces")
            self.player_names = data.get("player_names", ["Plum", "Chubs", "Strawberry"])
            self.loaded_total_xp = data.get("total_xp", 0)
            self.loaded_current_level = data.get("current_level", 1)

            if setup_window:
                # Update fields in setup window
                self.party_entry.delete(0, tk.END)
                self.party_entry.insert(0, self.party_name)

                # Update number of players and recreate entries
                self.num_players_var.set(len(self.player_names))
                for widget in self.players_frame.winfo_children():
                    widget.destroy()
                self.player_name_entries.clear()
                for i, name in enumerate(self.player_names):
                    lbl = tk.Label(self.players_frame, text=f"Player {i+1}:", width=15, anchor='w')
                    lbl.grid(row=i, column=0, sticky='w', pady=2)
                    entry = tk.Entry(self.players_frame, width=25)
                    entry.grid(row=i, column=1, sticky='w', pady=2)
                    entry.insert(0, name)
                    self.player_name_entries.append(entry)

                self.level_var.set(self.loaded_current_level)
                self.xp_var.set(self.loaded_total_xp)

                messagebox.showinfo("Load", "Game loaded successfully.")
            else:
                messagebox.showinfo("Load", "Please load a game from the setup window.")

        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load game:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    root.iconbitmap(resource_path('icon.ico'))  # Main window icon
    root.withdraw()  # Hide main window until setup is done
    app = XPTracker(root)
    root.mainloop()