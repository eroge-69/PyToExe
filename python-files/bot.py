import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import pyautogui
import psutil
from PIL import ImageGrab, Image, ImageEnhance, ImageOps
import random
import time
import threading
import json
import os
import re
import win32gui
import win32con
import pytesseract
import keyboard
import datetime
import uuid

TESSERACT_CONFIGURED = False
try:
    tesseract_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    ]
    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            TESSERACT_CONFIGURED = True
            break
    if not TESSERACT_CONFIGURED:
        pytesseract.get_tesseract_version()
        TESSERACT_CONFIGURED = True
except Exception:
    pass

class Overlay(tk.Toplevel):
    def __init__(self, root, mode='area', coords=None, display_only=False):
        super().__init__(root)
        self.attributes('-fullscreen', True, '-topmost', True, '-alpha', 0.3)
        self.configure(bg='black')
        self.mode = mode
        self.coords = coords
        self.display_only = display_only
        if not display_only:
            self.config(cursor="crosshair")
        self.canvas = tk.Canvas(self, bg='black', highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        if display_only and coords:
            self.draw_coords()
        if not display_only:
            self.start_screen_x = self.start_screen_y = None
            self.start_canvas_x = self.start_canvas_y = None
            self.current_rect_id = None
            self.result_coords = None
            self.canvas.bind("<ButtonPress-1>", self.on_press)
            self.canvas.bind("<B1-Motion>", self.on_motion)
            self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Escape>", self.on_cancel)
        if display_only:
            self.after(3000, self.on_cancel)

    def draw_coords(self):
        if self.mode == 'area' and len(self.coords) == 4:
            x1, y1, x2, y2 = self.coords
            canvas_x1 = x1 - self.winfo_rootx()
            canvas_y1 = y1 - self.winfo_rooty()
            canvas_x2 = x2 - self.winfo_rootx()
            canvas_y2 = y2 - self.winfo_rooty()
            self.canvas.create_rectangle(
                canvas_x1, canvas_y1, canvas_x2, canvas_y2, 
                outline='#00FF00', width=2
            )
        elif self.mode == 'point' and len(self.coords) == 2:
            x, y = self.coords
            canvas_x = x - self.winfo_rootx()
            canvas_y = y - self.winfo_rooty()
            size = 10
            self.canvas.create_line(
                canvas_x - size, canvas_y, canvas_x + size, canvas_y, 
                fill='#00FF00', width=2
            )
            self.canvas.create_line(
                canvas_x, canvas_y - size, canvas_x, canvas_y + size, 
                fill='#00FF00', width=2
            )

    def on_press(self, event):
        self.start_screen_x, self.start_screen_y = event.x_root, event.y_root
        self.start_canvas_x, self.start_canvas_y = event.x, event.y
        if self.mode == 'area':
            if self.current_rect_id:
                self.canvas.delete(self.current_rect_id)
            self.current_rect_id = self.canvas.create_rectangle(
                self.start_canvas_x, self.start_canvas_y, 
                self.start_canvas_x, self.start_canvas_y, 
                outline='#00A3E0', width=2
            )

    def on_motion(self, event):
        if self.mode == 'area' and self.start_canvas_x is not None:
            self.canvas.coords(
                self.current_rect_id, 
                self.start_canvas_x, self.start_canvas_y, event.x, event.y
            )

    def on_release(self, event):
        if self.start_screen_x is None:
            return
        end_screen_x, end_screen_y = event.x_root, event.y_root
        if self.mode == 'point':
            self.result_coords = (end_screen_x, end_screen_y)
        elif self.mode == 'area':
            x1, y1 = min(self.start_screen_x, end_screen_x), min(self.start_screen_y, end_screen_y)
            x2, y2 = max(self.start_screen_x, end_screen_x), max(self.start_screen_y, end_screen_y)
            x2 = max(x2, x1 + 1)
            y2 = max(y2, y1 + 1)
            self.result_coords = (x1, y1, x2, y2)
        self.destroy()

    def on_cancel(self, event=None):
        if not self.display_only:
            self.result_coords = None
        self.destroy()

    def get_coords(self, mode='area'):
        self.mode = mode
        self.grab_set()
        self.wait_window()
        return self.result_coords

class BotApp:
    LOG_LEVELS = ["INFO", "SUCCESS"]
    LOG_COLORS = {"INFO": "#E0E0E0", "SUCCESS": "#00E676"}
    MAX_LOG_LINES = 500
    DEBUG_IMAGE_DIR = "debug_images"
    IDLE_TIMEOUT_SECONDS = 3
    PROFILES_DIR = "profiles"

    def __init__(self, root):
        self.root = root
        self.root.title("Smoke v1.0")
        self.root.geometry("858x633")
        self.root.minsize(600, 400)
        if os.path.exists('logo.ico'):
            self.root.iconbitmap('logo.ico')
        self.root.attributes('-topmost', True)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self._default_button_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        self.aq3d_running = False
        self.health_box = None
        self.player_health_box = None
        self.enemy_health_box = None
        self.detect_revive_box = None
        self.menu_close_location = None
        self.movement_keys = {'w': True, 'a': True, 's': True, 'd': True}
        self.movement_loops = 5
        self.potion_hotkeys = ['', '', '']
        self.potion_cooldowns = [5, 5, 5]
        self.potion_enabled = [True, False, False]
        self.potion_health_thresholds = [50, 50, 50]
        self.loot_hotkey = 'l'
        self.jump_while_moving = tk.BooleanVar()
        self.jump_while_attacking = tk.BooleanVar()
        self.stop_bot_on_death = tk.BooleanVar()
        self.focus_aq3d_enabled = tk.BooleanVar(value=True)
        self.ignore_full_health_enemies = tk.BooleanVar(value=False)
        self.anchor_mode = tk.BooleanVar(value=False)
        self.auto_target = tk.BooleanVar(value=False)
        self.stick_to_injured = tk.BooleanVar(value=False)
        self.save_debug_images = tk.BooleanVar(value=True)
        self.no_enemy_timeout_minutes = 5
        self.max_runtime_hours = 0
        self.bot_running = False
        self.bot_start_time = 0
        self.last_enemy_detection_time = 0
        self.last_afk_time = 0
        self.last_action_time = 0
        self.last_loot_time = 0
        self.settings_modified = False
        self.log_line_count = 0
        self.input_widgets = []
        self.afk_interval_minutes = 0
        self.afk_duration_minutes = 0
        self._in_afk_mode = False
        self.last_potion_status = "None"
        self.target_enemy_names_list = []
        self.skill_names = [
            "Basic Attack", "Skill 1", "Skill 2", "Skill 3", 
            "Skill 4", "Cross Skill 1", "Cross Skill 2", "Cross Skill 3"
        ]
        self.skill_keys = ['1', '2', '3', '4', '5', 'r', 'z', 'x']
        self.skill_cooldowns = [0, 5, 10, 15, 20, 25, 30, 30]
        self.skill_enabled = [True] * len(self.skill_names)
        self.last_skill_use_time = [0] * len(self.skill_names)
        self.last_skill_attempt_time = 0
        self.skill_debounce_interval = 0.1
        self.last_health_read_time = 0
        self.health_debounce_interval = 0.2
        self.invalid_player_health_count = 0
        self.max_invalid_player_health = 3
        self.current_profile = tk.StringVar(value="default")
        self.profiles = ["default"]
        self.last_potion_use_time = [0] * len(self.potion_hotkeys)
        self.dragging_widget = None
        self.drag_start_y = 0
        self.target_rows = []
        self.current_sticky_target = None
        self.kill_count = 0
        os.makedirs(self.DEBUG_IMAGE_DIR, exist_ok=True)
        os.makedirs(self.PROFILES_DIR, exist_ok=True)
        self.setup_gui()
        self.load_profiles()
        self.load_settings()
        self.check_aq3d_status()
        self.setup_hotkeys()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_gui(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        nav_frame = ctk.CTkFrame(self.root, fg_color="#1C2526", height=50)
        nav_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 2))
        nav_frame.grid_columnconfigure(4, weight=1)
        ctk.CTkLabel(
            nav_frame, text="Profile:", font=ctk.CTkFont("Roboto", 14)
        ).grid(row=0, column=0, padx=(0, 5), pady=2)
        self.profile_dropdown = ctk.CTkComboBox(
            nav_frame, values=self.profiles, variable=self.current_profile,
            command=self.load_selected_profile, font=ctk.CTkFont("Roboto", 14),
            width=120
        )
        self.profile_dropdown.grid(row=0, column=1, padx=5, pady=2)
        self.nav_button = ctk.CTkSegmentedButton(
            nav_frame, values=["Dashboard", "Combat", "Locations", "Settings"],
            command=self.show_page, font=ctk.CTkFont("Roboto", 14), height=36,
            fg_color="#2E3A3C", selected_color="#00A3E0", 
            selected_hover_color="#0077B6"
        )
        self.nav_button.grid(row=0, column=2, padx=(0, 5), pady=2, sticky="w")
        self.start_button = ctk.CTkButton(
            nav_frame, text="▶", width=40, height=36, command=self.start_bot, 
            fg_color="#00A3E0", hover_color="#0077B6"
        )
        self.start_button.grid(row=0, column=3, padx=5, pady=2)
        self.stop_button = ctk.CTkButton(
            nav_frame, text="⏹", width=40, height=36, command=self.stop_bot, 
            state="disabled", fg_color="#FF5252", hover_color="#D32F2F"
        )
        self.stop_button.grid(row=0, column=4, padx=5, pady=2, sticky="w")
        self.save_button = ctk.CTkButton(
            nav_frame, text="Save", width=80, height=36, 
            command=self.save_all_settings
        )
        self.save_button.grid(row=0, column=5, padx=5, pady=2)
        self.save_profile_button = ctk.CTkButton(
            nav_frame, text="Save Profile", width=100, height=36, 
            command=self.save_new_profile
        )
        self.save_profile_button.grid(row=0, column=6, padx=5, pady=2)
        self.timer_label = ctk.CTkLabel(
            nav_frame, text="00:00:00", font=ctk.CTkFont("Roboto", 14)
        )
        self.timer_label.grid(row=0, column=7, padx=5, pady=2)
        self.content_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=2)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.pages = {
            name: ctk.CTkFrame(self.content_frame) 
            for name in ["Dashboard", "Combat", "Locations", "Settings"]
        }
        for frame in self.pages.values():
            frame.grid(row=0, column=0, sticky="nsew")
        self.create_dashboard_page()
        self.create_combat_page()
        self.create_locations_page()
        self.create_settings_page()
        self.show_page("Dashboard")

    def create_dashboard_page(self):
        page = self.pages["Dashboard"]
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)
        status_frame = ctk.CTkFrame(page, fg_color="#2E3A3C")
        status_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        ctk.CTkLabel(
            status_frame, text="Smoke:", font=ctk.CTkFont("Roboto", 14, "bold")
        ).grid(row=0, column=0, padx=10, pady=2)
        self.aq3d_status_label = ctk.CTkLabel(
            status_frame, text="Not Running", text_color="red", 
            font=ctk.CTkFont("Roboto", 14)
        )
        self.aq3d_status_label.grid(row=0, column=1, padx=10, pady=2)
        self.kill_count_label = ctk.CTkLabel(
            status_frame, text="Kills: 0", font=ctk.CTkFont("Roboto", 14)
        )
        self.kill_count_label.grid(row=0, column=2, padx=10, pady=2)
        log_frame = ctk.CTkFrame(page, fg_color="#2E3A3C")
        log_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=2)
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(0, weight=1)
        self.log_text = ctk.CTkTextbox(
            log_frame, wrap="word", state="disabled", fg_color="#1C2526", 
            font=ctk.CTkFont("Roboto", 12)
        )
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=2)
        for level, color in self.LOG_COLORS.items():
            self.log_text.tag_config(level, foreground=color)
        self.input_widgets.extend([
            self.start_button, self.save_button, self.save_profile_button, 
            self.profile_dropdown
        ])

    def create_combat_page(self):
        page = self.pages["Combat"]
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(0, weight=1)
        scrollable_frame = ctk.CTkScrollableFrame(
            page, fg_color="transparent", height=550
        )
        scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        scrollable_frame.grid_columnconfigure(0, weight=1)
        scrollable_frame.grid_columnconfigure(1, weight=1)
        row = 0
        ctk.CTkLabel(
            scrollable_frame, text="Skills", 
            font=ctk.CTkFont("Roboto", 16, "bold")
        ).grid(row=row, column=0, sticky="w", padx=5, pady=(10, 2), columnspan=2)
        row += 1
        skill_frame = ctk.CTkFrame(scrollable_frame, fg_color="#2E3A3C")
        skill_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2, columnspan=2)
        skill_frame.grid_columnconfigure(1, weight=1)
        skill_frame.grid_columnconfigure(2, weight=1)
        for i, header in enumerate(["Skill", "Key", "Cooldown", "On"]):
            ctk.CTkLabel(
                skill_frame, text=header, font=ctk.CTkFont("Roboto", 12, "bold")
            ).grid(row=0, column=i, padx=5, pady=2)
        self.skill_entries, self.skill_cooldown_entries, self.skill_enabled_vars = [], [], []
        for i, name in enumerate(self.skill_names):
            ctk.CTkLabel(
                skill_frame, text=name, font=ctk.CTkFont("Roboto", 12)
            ).grid(row=i+1, column=0, padx=5, pady=2, sticky="w")
            entry = ctk.CTkEntry(skill_frame, width=80, font=ctk.CTkFont("Roboto", 12))
            entry.insert(0, self.skill_keys[i])
            entry.grid(row=i+1, column=1, padx=5, pady=2, sticky="ew")
            entry.bind("<KeyRelease>", self.mark_settings_modified)
            self.skill_entries.append(entry)
            cooldown = ctk.CTkEntry(skill_frame, width=100, font=ctk.CTkFont("Roboto", 12))
            cooldown.insert(0, str(self.skill_cooldowns[i]))
            cooldown.grid(row=i+1, column=2, padx=5, pady=2, sticky="ew")
            cooldown.bind("<KeyRelease>", self.mark_settings_modified)
            self.skill_cooldown_entries.append(cooldown)
            var = tk.BooleanVar(value=self.skill_enabled[i])
            chk = ctk.CTkCheckBox(
                skill_frame, text="", variable=var, 
                command=self.mark_settings_modified
            )
            chk.grid(row=i+1, column=3, padx=5, pady=2)
            self.skill_enabled_vars.append(var)
            self.input_widgets.extend([entry, cooldown, chk])
        row += len(self.skill_names) + 1
        ctk.CTkLabel(
            scrollable_frame, text="Actions", 
            font=ctk.CTkFont("Roboto", 16, "bold")
        ).grid(row=row, column=0, sticky="w", padx=5, pady=(10, 2), columnspan=2)
        row += 1
        action_frame = ctk.CTkFrame(scrollable_frame, fg_color="#2E3A3C")
        action_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2, columnspan=2)
        action_frame.grid_columnconfigure(0, weight=1)
        actions = [
            ("Jump While Moving", self.jump_while_moving),
            ("Jump While Attacking", self.jump_while_attacking),
            ("Stop on Death", self.stop_bot_on_death),
            ("Ignore 100% HP Enemies", self.ignore_full_health_enemies),
            ("Anchor Mode", self.anchor_mode),
            ("Auto Target", self.auto_target),
            ("Stick to Injured", self.stick_to_injured)
        ]
        for i, (text, var) in enumerate(actions):
            chk = ctk.CTkCheckBox(
                action_frame, text=text, variable=var, 
                command=self.mark_settings_modified, font=ctk.CTkFont("Roboto", 12)
            )
            chk.grid(row=i, column=0, sticky="w", padx=5, pady=2)
            self.input_widgets.append(chk)
        row += len(actions)
        ctk.CTkLabel(
            action_frame, text="Potions:", font=ctk.CTkFont("Roboto", 12, "bold")
        ).grid(row=row, column=0, sticky="w", padx=5, pady=2)
        self.potion_status_label = ctk.CTkLabel(
            action_frame, text=self.last_potion_status, font=ctk.CTkFont("Roboto", 12)
        )
        self.potion_status_label.grid(row=row, column=1, sticky="w", padx=5, pady=2)
        row += 1
        for i, header in enumerate(["Potion", "Hotkey", "Cooldown", "Threshold", "Enabled"]):
            ctk.CTkLabel(
                action_frame, text=header, font=ctk.CTkFont("Roboto", 12, "bold")
            ).grid(row=row, column=i, padx=5, pady=2)
        row += 1
        self.potion_hotkey_entries = []
        self.potion_cooldown_entries = []
        self.potion_enabled_vars = []
        self.potion_threshold_entries = []
        for i in range(3):
            ctk.CTkLabel(
                action_frame, text=f"Potion {i+1}:", font=ctk.CTkFont("Roboto", 12)
            ).grid(row=row+i, column=0, sticky="w", padx=5, pady=2)
            hotkey_entry = ctk.CTkEntry(
                action_frame, width=80, font=ctk.CTkFont("Roboto", 12)
            )
            hotkey_entry.insert(0, self.potion_hotkeys[i])
            hotkey_entry.grid(row=row+i, column=1, sticky="w", padx=5, pady=2)
            hotkey_entry.bind("<KeyRelease>", self.mark_settings_modified)
            self.potion_hotkey_entries.append(hotkey_entry)
            cooldown_entry = ctk.CTkEntry(
                action_frame, width=80, font=ctk.CTkFont("Roboto", 12)
            )
            cooldown_entry.insert(0, str(self.potion_cooldowns[i]))
            cooldown_entry.grid(row=row+i, column=2, sticky="w", padx=5, pady=2)
            cooldown_entry.bind("<KeyRelease>", self.mark_settings_modified)
            self.potion_cooldown_entries.append(cooldown_entry)
            threshold_entry = ctk.CTkEntry(
                action_frame, width=80, font=ctk.CTkFont("Roboto", 12)
            )
            threshold_entry.insert(0, str(self.potion_health_thresholds[i]))
            threshold_entry.grid(row=row+i, column=3, sticky="w", padx=5, pady=2)
            threshold_entry.bind("<KeyRelease>", self.mark_settings_modified)
            self.potion_threshold_entries.append(threshold_entry)
            enabled_var = tk.BooleanVar(value=self.potion_enabled[i])
            chk = ctk.CTkCheckBox(
                action_frame, text="", variable=enabled_var, 
                command=self.mark_settings_modified, font=ctk.CTkFont("Roboto", 12)
            )
            chk.grid(row=row+i, column=4, padx=5, pady=2)
            self.potion_enabled_vars.append(enabled_var)
            self.input_widgets.extend([hotkey_entry, cooldown_entry, threshold_entry, chk])
        row += 3
        ctk.CTkLabel(
            scrollable_frame, text="Targeting", font=ctk.CTkFont("Roboto", 16, "bold")
        ).grid(row=row, column=0, sticky="w", padx=5, pady=(10, 2), columnspan=2)
        row += 1
        target_frame = ctk.CTkFrame(scrollable_frame, fg_color="#2E3A3C")
        target_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2, columnspan=2)
        target_frame.grid_columnconfigure(1, weight=1)
        self.target_enemy_entries = []
        self.target_rows = []
        for i in range(5):
            target_row_frame = ctk.CTkFrame(target_frame, fg_color="transparent")
            target_row_frame.grid(row=i, column=0, sticky="ew", columnspan=2, padx=5, pady=2)
            target_row_frame.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(
                target_row_frame, text=f"P{i+1}:", font=ctk.CTkFont("Roboto", 12)
            ).grid(row=0, column=0, padx=5, pady=2)
            entry = ctk.CTkEntry(
                target_row_frame, width=200, font=ctk.CTkFont("Roboto", 12)
            )
            entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
            entry.bind("<KeyRelease>", self.mark_settings_modified)
            entry.bind("<ButtonPress-1>", lambda e, r=i: self.start_drag(e, r))
            entry.bind("<B1-Motion>", self.on_drag)
            entry.bind("<ButtonRelease-1>", self.stop_drag)
            self.target_enemy_entries.append(entry)
            self.target_rows.append(target_row_frame)
            self.input_widgets.append(entry)
        row += 5
        auto_detect_button = ctk.CTkButton(
            scrollable_frame, text="Auto Detect Targets", command=self.auto_detect_targets, 
            font=ctk.CTkFont("Roboto", 12), fg_color="#00A3E0", hover_color="#0077B6"
        )
        auto_detect_button.grid(row=row, column=0, columnspan=2, padx=5, pady=2, sticky="ew")
        self.input_widgets.append(auto_detect_button)
        row += 1
        clear_targets_button = ctk.CTkButton(
            scrollable_frame, text="Clear Targets", command=self.clear_targets, 
            font=ctk.CTkFont("Roboto", 12), fg_color="#FF5252", hover_color="#D32F2F"
        )
        clear_targets_button.grid(row=row, column=0, columnspan=2, padx=5, pady=2, sticky="ew")
        self.input_widgets.append(clear_targets_button)

    def start_drag(self, event, row_index):
        self.dragging_widget = self.target_rows[row_index]
        self.drag_start_y = event.y_root
        self.log(f"Started dragging target row {row_index + 1}", "INFO")

    def on_drag(self, event):
        if not self.dragging_widget:
            return
        current_y = event.y_root
        delta_y = current_y - self.drag_start_y
        threshold = 20
        for i, row_frame in enumerate(self.target_rows):
            if row_frame == self.dragging_widget:
                continue
            row_y = row_frame.winfo_rooty()
            if delta_y > threshold and current_y > row_y and i > self.target_rows.index(self.dragging_widget):
                self.swap_rows(self.target_rows.index(self.dragging_widget), i)
                self.drag_start_y = current_y
                break
            elif delta_y < -threshold and current_y < row_y and i < self.target_rows.index(self.dragging_widget):
                self.swap_rows(self.target_rows.index(self.dragging_widget), i)
                self.drag_start_y = current_y
                break

    def swap_rows(self, from_index, to_index):
        if from_index == to_index:
            return
        self.target_rows[from_index], self.target_rows[to_index] = (
            self.target_rows[to_index], self.target_rows[from_index]
        )
        self.target_enemy_entries[from_index], self.target_enemy_entries[to_index] = (
            self.target_enemy_entries[to_index], self.target_enemy_entries[from_index]
        )
        for i, row_frame in enumerate(self.target_rows):
            row_frame.grid(row=i, column=0, sticky="ew", columnspan=2, padx=5, pady=2)
            ctk.CTkLabel(
                row_frame, text=f"P{i+1}:", font=ctk.CTkFont("Roboto", 12)
            ).grid(row=0, column=0, padx=5, pady=2)
            self.target_enemy_entries[i].grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        self.mark_settings_modified()
        self.log(f"Swapped target rows {from_index + 1} and {to_index + 1}", "INFO")
        self.target_enemy_names_list = [
            entry.get().strip() for entry in self.target_enemy_entries if entry.get().strip()
        ]

    def stop_drag(self, event):
        self.dragging_widget = None
        self.log("Stopped dragging target row", "INFO")

    def clear_targets(self):
        for entry in self.target_enemy_entries:
            entry.delete(0, tk.END)
        self.target_enemy_names_list = []
        self.mark_settings_modified()
        self.log("Cleared all target enemy names", "INFO")

    def create_locations_page(self):
        page = self.pages["Locations"]
        page.grid_columnconfigure(1, weight=1)
        page.grid_columnconfigure(2, weight=0)
        locations = [
            ("Enemy Name", self.set_health_location, "health_location_label", 'area', lambda: self.health_box),
            ("Player Health", self.set_player_health_location, "player_health_location_label", 'area', lambda: self.player_health_box),
            ("Enemy Health", self.set_enemy_health_location, "enemy_health_location_label", 'area', lambda: self.enemy_health_box),
            ("Menu Close", self.set_menu_close_location, "menu_close_location_label", 'point', lambda: self.menu_close_location),
            ("Revive Button", self.set_detect_revive_location, "detect_revive_location_label", 'area', lambda: self.detect_revive_box)
        ]
        for i, (text, cmd, label_attr, mode, get_coords) in enumerate(locations):
            btn = ctk.CTkButton(
                page, text=text, command=cmd, font=ctk.CTkFont("Roboto", 12), 
                fg_color="#00A3E0", hover_color="#0077B6"
            )
            btn.grid(row=i, column=0, padx=5, pady=2, sticky="ew")
            label = ctk.CTkLabel(page, text="Not Set", font=ctk.CTkFont("Roboto", 12))
            label.grid(row=i, column=1, padx=5, pady=2, sticky="w")
            setattr(self, label_attr, label)
            show_btn = ctk.CTkButton(
                page, text="Show", command=lambda m=mode, gc=get_coords: self.show_location_overlay(m, gc()), 
                font=ctk.CTkFont("Roboto", 12), fg_color="#00FF00", hover_color="#00CC00", width=60
            )
            show_btn.grid(row=i, column=2, padx=5, pady=2)
            self.input_widgets.extend([btn, show_btn])

    def create_settings_page(self):
        page = self.pages["Settings"]
        page.grid_columnconfigure(1, weight=1)
        row = 0
        self.movement_loops_entry = self.create_labeled_entry(
            page, "Move Loops:", str(self.movement_loops), row
        )
        row += 1
        self.loot_hotkey_entry = self.create_labeled_entry(
            page, "Loot Key:", self.loot_hotkey, row
        )
        row += 1
        self.no_enemy_timeout_entry = self.create_labeled_entry(
            page, "No Enemy (min):", str(self.no_enemy_timeout_minutes), row
        )
        row += 1
        self.max_runtime_entry = self.create_labeled_entry(
            page, "Max Run (hrs):", str(self.max_runtime_hours), row
        )
        row += 1
        self.afk_interval_entry = self.create_labeled_entry(
            page, "AFK After (min):", str(self.afk_interval_minutes), row
        )
        row += 1
        self.afk_duration_entry = self.create_labeled_entry(
            page, "AFK Duration:", str(self.afk_duration_minutes), row
        )
        row += 1
        ctk.CTkLabel(
            page, text="Move Keys:", font=ctk.CTkFont("Roboto", 12)
        ).grid(row=row, column=0, sticky="w", padx=5, pady=2)
        move_frame = ctk.CTkFrame(page, fg_color="transparent")
        move_frame.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
        self.movement_key_vars = {}
        for i, key in enumerate(['w', 'a', 's', 'd']):
            self.movement_key_vars[key] = tk.BooleanVar(value=self.movement_keys.get(key, True))
            chk = ctk.CTkCheckBox(
                move_frame, text=key.upper(), variable=self.movement_key_vars[key], 
                command=self.mark_settings_modified, font=ctk.CTkFont("Roboto", 12)
            )
            chk.grid(row=0, column=i, padx=5, pady=2)
            self.input_widgets.append(chk)
        row += 1
        chk = ctk.CTkCheckBox(
            page, text="Focus AQ3D", variable=self.focus_aq3d_enabled, 
            command=self.mark_settings_modified, font=ctk.CTkFont("Roboto", 12)
        )
        chk.grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        self.input_widgets.append(chk)
        row += 1
        chk = ctk.CTkCheckBox(
            page, text="Save Debug Images", variable=self.save_debug_images, 
            command=self.mark_settings_modified, font=ctk.CTkFont("Roboto", 12)
        )
        chk.grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        self.input_widgets.append(chk)

    def create_labeled_entry(self, parent, text, default, row, bind=True):
        ctk.CTkLabel(
            parent, text=text, font=ctk.CTkFont("Roboto", 12)
        ).grid(row=row, column=0, sticky="w", padx=5, pady=2)
        entry = ctk.CTkEntry(parent, width=150, font=ctk.CTkFont("Roboto", 12))
        entry.insert(0, default)
        entry.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
        if bind:
            entry.bind("<KeyRelease>", self.mark_settings_modified)
        self.input_widgets.append(entry)
        return entry

    def show_location_overlay(self, mode, coords):
        if not coords:
            messagebox.showinfo("Info", "Location not set.")
            return
        self.root.withdraw()
        try:
            overlay = Overlay(self.root, mode=mode, coords=coords, display_only=True)
            self.log(f"Displayed {mode} overlay for coordinates {coords}", "INFO")
        finally:
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()

    def show_page(self, page_name):
        for frame in self.pages.values():
            frame.grid_remove()
        self.pages[page_name].grid(sticky="nsew")
        self.nav_button.set(page_name)
        self.log(f"Switched to {page_name} page", "INFO")

    def setup_hotkeys(self):
        try:
            keyboard.unhook_all()
            keyboard.add_hotkey('f5', lambda: self.root.after(0, self.start_bot))
            keyboard.add_hotkey('f6', lambda: self.root.after(0, self.stop_bot))
            self.log("Hotkeys set: F5 (start), F6 (stop)", "INFO")
        except Exception:
            self.log("Hotkey setup completed", "INFO")

    def _set_input_state(self, state, exclude=None):
        exclude = exclude or []
        for widget in self.input_widgets:
            if widget in exclude or not widget.winfo_exists():
                continue
            widget.configure(state=state)

    def mark_settings_modified(self, event=None):
        if not self.settings_modified:
            self.settings_modified = True
            self.save_button.configure(text="Save *", fg_color="#FFAB00")
            self.log("Settings modified, save pending", "INFO")

    def log(self, message, level="INFO"):
        if level not in self.LOG_LEVELS:
            level = "INFO"
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        print(log_entry.strip())
        if self.root.winfo_exists():
            self.root.after(0, self._update_log, log_entry, level)

    def _update_log(self, log_entry, level):
        self.log_text.configure(state="normal")
        tag_start = self.log_text.index(tk.END + "-1c linestart")
        self.log_text.insert(tk.END, log_entry)
        self.log_text.tag_add(level, tag_start, tk.END + "-1c")
        self.log_line_count += 1
        if self.log_line_count > self.MAX_LOG_LINES:
            lines_to_delete = self.log_line_count - self.MAX_LOG_LINES
            self.log_text.delete("1.0", f"{lines_to_delete + 1}.0")
            self.log_line_count = self.MAX_LOG_LINES
        self.log_text.configure(state="disabled")
        self.log_text.yview(tk.END)

    def check_aq3d_status(self):
        self.aq3d_running = any(p.name() == "AQ3D.exe" for p in psutil.process_iter(['name']))
        if self.root.winfo_exists():
            self.aq3d_status_label.configure(
                text="Running" if self.aq3d_running else "Not Running", 
                text_color="green" if self.aq3d_running else "red"
            )
            self.log(f"AQ3D status: {'Running' if self.aq3d_running else 'Not Running'}", "INFO")

    def _get_overlay_coords(self, prompt, mode):
        self.root.withdraw()
        time.sleep(0.2)
        coords = None
        try:
            overlay = Overlay(self.root, mode=mode)
            coords = overlay.get_coords(mode=mode)
            self.log(f"Selected {mode} coordinates: {coords}", "INFO")
        finally:
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
        return coords

    def set_health_location(self):
        coords = self._get_overlay_coords("Set Enemy Name Area", 'area')
        if coords:
            self.health_box = coords
            self.health_location_label.configure(text=f"{coords}")
            self.mark_settings_modified()
            self.log(f"Enemy Name location set to {coords}", "INFO")

    def set_player_health_location(self):
        coords = self._get_overlay_coords("Set Player Health Area", 'area')
        if coords:
            self.player_health_box = coords
            self.player_health_location_label.configure(text=f"{coords}")
            self.mark_settings_modified()
            self.log(f"Player Health location set to {coords}", "INFO")

    def set_enemy_health_location(self):
        coords = self._get_overlay_coords("Set Enemy Health Area", 'area')
        if coords:
            self.enemy_health_box = coords
            self.enemy_health_location_label.configure(text=f"{coords}")
            self.mark_settings_modified()
            self.log(f"Enemy Health location set to {coords}", "INFO")

    def set_menu_close_location(self):
        coords = self._get_overlay_coords("Set Menu Close Point", 'point')
        if coords:
            self.menu_close_location = coords
            self.menu_close_location_label.configure(text=f"{coords}")
            self.mark_settings_modified()
            self.log(f"Menu Close location set to {coords}", "INFO")

    def set_detect_revive_location(self):
        coords = self._get_overlay_coords("Set Revive Button Area", 'area')
        if coords:
            self.detect_revive_box = coords
            self.detect_revive_location_label.configure(text=f"{coords}")
            self.mark_settings_modified()
            self.log(f"Revive Button location set to {coords}", "INFO")

    def auto_detect_targets(self):
        if not TESSERACT_CONFIGURED or not self.health_box:
            messagebox.showinfo("Info", "Tesseract OCR or Enemy Name area not set.")
            return
        self.check_aq3d_status()
        if not self.aq3d_running:
            messagebox.showinfo("Info", "AQ3D not running.")
            return
        if not self.focus_aq3d():
            messagebox.showinfo("Info", "Unable to focus AQ3D window.")
            return
        self.log("Starting auto-detection of target names", "INFO")
        detected_names = []
        max_attempts = 20
        no_enemy_attempts = 0
        max_no_enemy_attempts = 3
        for attempt in range(max_attempts):
            if len(detected_names) >= len(self.target_enemy_entries):
                break
            if no_enemy_attempts >= max_no_enemy_attempts:
                for i, entry in enumerate(self.target_enemy_entries):
                    entry.delete(0, tk.END)
                    if i < len(detected_names):
                        entry.insert(0, detected_names[i])
                self.target_enemy_names_list = detected_names[:len(self.target_enemy_entries)]
                self.mark_settings_modified()
                messagebox.showinfo("Info", "No enemies available. Auto-detection aborted.")
                self.log("Auto-detection aborted: no enemies available after 3 attempts", "INFO")
                return
            pyautogui.press('tab')
            time.sleep(0.1)
            name = self.read_enemy_name()
            if name and name not in detected_names:
                detected_names.append(name)
                self.log(f"Detected target: '{name}'", "INFO")
                no_enemy_attempts = 0
            else:
                no_enemy_attempts += 1
                self.log(f"Attempt {no_enemy_attempts}/{max_no_enemy_attempts}: no valid enemy name detected", "INFO")
            time.sleep(0.05)
        for i, entry in enumerate(self.target_enemy_entries):
            entry.delete(0, tk.END)
            if i < len(detected_names):
                entry.insert(0, detected_names[i])
        self.target_enemy_names_list = detected_names[:len(self.target_enemy_entries)]
        self.mark_settings_modified()
        self.log(f"Auto-detection complete: found {len(detected_names)} unique targets", "INFO")
        if len(detected_names) < len(self.target_enemy_entries):
            self.log(f"Found {len(detected_names)} of {len(self.target_enemy_entries)} possible targets", "INFO")

    def load_profiles(self):
        self.profiles = ["default"]
        for file in os.listdir(self.PROFILES_DIR):
            if file.endswith(".json"):
                profile_name = file.replace(".json", "")
                if profile_name not in self.profiles:
                    self.profiles.append(profile_name)
        self.profile_dropdown.configure(values=self.profiles)
        self.log(f"Loaded profiles: {self.profiles}", "INFO")

    def save_new_profile(self):
        profile_name = ctk.CTkInputDialog(
            text="Enter profile name:", title="Save Profile"
        ).get_input()
        if profile_name and profile_name.strip() and profile_name not in self.profiles:
            self.profiles.append(profile_name.strip())
            self.profile_dropdown.configure(values=self.profiles)
            self.current_profile.set(profile_name.strip())
            self.save_all_settings()
            self.log(f"Saved new profile: {profile_name}", "INFO")
        elif profile_name in self.profiles:
            messagebox.showinfo("Info", "Profile name already exists.")
        elif profile_name:
            messagebox.showinfo("Info", "Invalid profile name.")

    def save_all_settings(self):
        try:
            settings = {
                'health_box': self.health_box,
                'player_health_box': self.player_health_box,
                'enemy_health_box': self.enemy_health_box,
                'menu_close_location': self.menu_close_location,
                'detect_revive_box': self.detect_revive_box,
                'movement_keys': {k: v.get() for k, v in self.movement_key_vars.items()},
                'movement_loops': int(self.movement_loops_entry.get() or 5),
                'potion_hotkeys': [e.get().strip() for e in self.potion_hotkey_entries],
                'potion_cooldowns': [int(e.get() or 5) for e in self.potion_cooldown_entries],
                'potion_enabled': [v.get() for v in self.potion_enabled_vars],
                'potion_health_thresholds': [int(e.get() or 50) for e in self.potion_threshold_entries],
                'loot_hotkey': self.loot_hotkey_entry.get().strip() or 'l',
                'no_enemy_timeout_minutes': int(self.no_enemy_timeout_entry.get() or 5),
                'max_runtime_hours': int(self.max_runtime_entry.get() or 0),
                'target_enemy_names_list': [
                    e.get().strip() for e in self.target_enemy_entries if e.get().strip()
                ],
                'skill_keys': [e.get() for e in self.skill_entries],
                'skill_cooldowns': [int(e.get() or 0) for e in self.skill_cooldown_entries],
                'skill_enabled': [v.get() for v in self.skill_enabled_vars],
                'jump_while_moving': self.jump_while_moving.get(),
                'jump_while_attacking': self.jump_while_attacking.get(),
                'stop_bot_on_death': self.stop_bot_on_death.get(),
                'afk_interval_minutes': int(self.afk_interval_entry.get() or 0),
                'afk_duration_minutes': min(int(self.afk_duration_entry.get() or 0), 15),
                'focus_aq3d_enabled': self.focus_aq3d_enabled.get(),
                'ignore_full_health_enemies': self.ignore_full_health_enemies.get(),
                'anchor_mode': self.anchor_mode.get(),
                'auto_target': self.auto_target.get(),
                'stick_to_injured': self.stick_to_injured.get(),
                'save_debug_images': self.save_debug_images.get()
            }
            for key, value in settings.items():
                if isinstance(value, int) and value < 0:
                    raise ValueError(f"{key} cannot be negative")
                if key == 'loot_hotkey' and (not value or len(value) > 1 or not value.isalnum()):
                    raise ValueError("Loot hotkey must be a single alphanumeric character")
                if key == 'potion_hotkeys':
                    for i, hotkey in enumerate(value):
                        if hotkey and (len(hotkey) > 1 or not hotkey.isalnum()):
                            raise ValueError(f"Potion {i+1} hotkey must be a single alphanumeric character or empty")
            profile_name = self.current_profile.get()
            file_path = os.path.join(self.PROFILES_DIR, f"{profile_name}.json")
            with open(file_path, 'w') as f:
                json.dump(settings, f, indent=2)
            self.settings_modified = False
            self.save_button.configure(text="Save", fg_color=self._default_button_color)
            self.log(f"Saved settings to profile: {profile_name}", "INFO")
        except ValueError as e:
            messagebox.showinfo("Info", f"Invalid input: {e}")
            self.log(f"Attempted to save settings, invalid input: {e}", "INFO")
        except Exception as e:
            messagebox.showinfo("Info", f"Save failed: {e}")
            self.log(f"Attempted to save settings, failed: {e}", "INFO")

    def load_selected_profile(self, profile_name):
        self.current_profile.set(profile_name)
        self.load_settings()
        self.log(f"Loaded profile: {profile_name}", "INFO")

    def load_settings(self):
        profile_name = self.current_profile.get()
        file_path = os.path.join(self.PROFILES_DIR, f"{profile_name}.json")
        settings = {}
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    settings = json.load(f)
                self.log(f"Loaded settings from {file_path}", "INFO")
            except Exception as e:
                self.log(f"Attempted to load settings from {file_path}", "INFO")
        self.health_box = settings.get('health_box')
        self.player_health_box = settings.get('player_health_box')
        self.enemy_health_box = settings.get('enemy_health_box')
        self.menu_close_location = settings.get('menu_close_location')
        self.detect_revive_box = settings.get('detect_revive_box')
        self.movement_keys = settings.get('movement_keys', {'w': True, 'a': True, 's': True, 'd': True})
        self.movement_loops = settings.get('movement_loops', 5)
        self.potion_hotkeys = settings.get('potion_hotkeys', ['', '', ''])
        self.potion_cooldowns = settings.get('potion_cooldowns', [5, 5, 5])
        self.potion_enabled = settings.get('potion_enabled', [True, False, False])
        self.potion_health_thresholds = settings.get('potion_health_thresholds', [50, 50, 50])
        self.loot_hotkey = settings.get('loot_hotkey', 'l')
        self.no_enemy_timeout_minutes = settings.get('no_enemy_timeout_minutes', 5)
        self.max_runtime_hours = settings.get('max_runtime_hours', 0)
        self.target_enemy_names_list = settings.get('target_enemy_names_list', [])
        self.skill_keys = settings.get('skill_keys', ['1', '2', '3', '4', '5', 'r', 'z', 'x'])
        self.skill_cooldowns = settings.get('skill_cooldowns', [0, 5, 10, 15, 20, 25, 30, 30])
        self.skill_enabled = settings.get('skill_enabled', [True] * len(self.skill_names))
        self.jump_while_moving.set(settings.get('jump_while_moving', False))
        self.jump_while_attacking.set(settings.get('jump_while_attacking', False))
        self.stop_bot_on_death.set(settings.get('stop_bot_on_death', False))
        self.afk_interval_minutes = settings.get('afk_interval_minutes', 0)
        self.afk_duration_minutes = settings.get('afk_duration_minutes', 0)
        self.focus_aq3d_enabled.set(settings.get('focus_aq3d_enabled', True))
        self.ignore_full_health_enemies.set(settings.get('ignore_full_health_enemies', False))
        self.anchor_mode.set(settings.get('anchor_mode', False))
        self.auto_target.set(settings.get('auto_target', False))
        self.stick_to_injured.set(settings.get('stick_to_injured', False))
        self.save_debug_images.set(settings.get('save_debug_images', True))
        self.update_gui_from_settings()

    def update_gui_from_settings(self):
        try:
            for label, value in [
                (self.health_location_label, self.health_box),
                (self.player_health_location_label, self.player_health_box),
                (self.enemy_health_location_label, self.enemy_health_box),
                (self.menu_close_location_label, self.menu_close_location),
                (self.detect_revive_location_label, self.detect_revive_box)
            ]:
                label.configure(text=str(value) if value else "Not Set")
            for entry, value in [
                (self.movement_loops_entry, str(self.movement_loops)),
                (self.loot_hotkey_entry, self.loot_hotkey),
                (self.no_enemy_timeout_entry, str(self.no_enemy_timeout_minutes)),
                (self.max_runtime_entry, str(self.max_runtime_hours)),
                (self.afk_interval_entry, str(self.afk_interval_minutes)),
                (self.afk_duration_entry, str(self.afk_duration_minutes))
            ]:
                entry.delete(0, tk.END)
                entry.insert(0, value)
            for i, entry in enumerate(self.potion_hotkey_entries):
                entry.delete(0, tk.END)
                entry.insert(0, self.potion_hotkeys[i])
            for i, entry in enumerate(self.potion_cooldown_entries):
                entry.delete(0, tk.END)
                entry.insert(0, str(self.potion_cooldowns[i]))
            for i, entry in enumerate(self.potion_threshold_entries):
                entry.delete(0, tk.END)
                entry.insert(0, str(self.potion_health_thresholds[i]))
            for i, var in enumerate(self.potion_enabled_vars):
                var.set(self.potion_enabled[i])
            for i, entry in enumerate(self.target_enemy_entries):
                entry.delete(0, tk.END)
                if i < len(self.target_enemy_names_list):
                    entry.insert(0, self.target_enemy_names_list[i])
            for i in range(len(self.skill_names)):
                self.skill_entries[i].delete(0, tk.END)
                self.skill_entries[i].insert(0, self.skill_keys[i])
                self.skill_cooldown_entries[i].delete(0, tk.END)
                self.skill_cooldown_entries[i].insert(0, str(self.skill_cooldowns[i]))
                self.skill_enabled_vars[i].set(self.skill_enabled[i])
            for key, var in self.movement_key_vars.items():
                var.set(self.movement_keys.get(key, True))
            self.potion_status_label.configure(text=self.last_potion_status)
            self.settings_modified = False
            self.save_button.configure(text="Save", fg_color=self._default_button_color)
            self.log("Updated GUI with current settings", "INFO")
        except Exception as e:
            self.log(f"Attempted to update GUI with settings", "INFO")

    def start_bot(self):
        if not TESSERACT_CONFIGURED:
            messagebox.showinfo("Info", "Tesseract OCR not ready.")
            return
        self.check_aq3d_status()
        if not self.aq3d_running:
            messagebox.showinfo("Info", "AQ3D not running.")
            return
        if not self.health_box or not self.player_health_box:
            messagebox.showinfo("Info", "Enemy Name and Player Health areas required.")
            return
        if self.settings_modified and messagebox.askyesno("Unsaved", "Save settings?"):
            self.save_all_settings()
        if self.settings_modified:
            return
        self.bot_running = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self._set_input_state("disabled", exclude=[self.stop_button])
        self.bot_start_time = self.last_enemy_detection_time = self.last_afk_time = self.last_action_time = self.last_loot_time = time.time()
        self._in_afk_mode = False
        self.last_skill_use_time = [0] * len(self.skill_names)
        self.last_skill_attempt_time = 0
        self.last_potion_use_time = [0] * len(self.potion_hotkeys)
        self.last_health_read_time = 0
        self.invalid_player_health_count = 0
        self.current_sticky_target = None
        self.kill_count = 0
        self.kill_count_label.configure(text="Kills: 0")
        threading.Thread(target=self.bot_loop, daemon=True).start()
        threading.Thread(target=self.loot_loop, daemon=True).start()
        self.update_timer()
        self.log("Bot started", "INFO")

    def stop_bot(self):
        if self.bot_running:
            self.bot_running = False
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self._set_input_state("normal")
            self.timer_label.configure(text="00:00:00")
            self.log("Bot stopped", "INFO")

    def update_timer(self):
        if not self.bot_running:
            return
        elapsed = int(time.time() - self.bot_start_time)
        hrs, rem = divmod(elapsed, 3600)
        mins, secs = divmod(rem, 60)
        self.timer_label.configure(text=f"{hrs:02d}:{mins:02d}:{secs:02d}")
        if self.max_runtime_hours > 0 and elapsed >= self.max_runtime_hours * 3600:
            self.stop_bot()
        elif self.no_enemy_timeout_minutes > 0 and time.time() - self.last_enemy_detection_time > self.no_enemy_timeout_minutes * 60:
            self.stop_bot()
        else:
            self.root.after(1000, self.update_timer)
            self.log(f"Bot runtime: {hrs:02d}:{mins:02d}:{secs:02d}", "INFO")

    def loot_loop(self):
        while self.bot_running:
            current_time = time.time()
            loot_interval = random.uniform(11, 15)
            if current_time - self.last_loot_time >= loot_interval:
                if self.loot_hotkey and self.focus_aq3d():
                    pyautogui.press(self.loot_hotkey)
                    time.sleep(random.uniform(0.75, 1.50))
                    if not self.bot_running:
                        return
                    pyautogui.press(self.loot_hotkey)
                    self.last_loot_time = current_time
                    self.log(f"Loot action performed with key '{self.loot_hotkey}'", "INFO")
            time.sleep(0.1)

    def bot_loop(self):
        while self.bot_running:
            current_time = time.time()
            if current_time - self.last_action_time > self.IDLE_TIMEOUT_SECONDS:
                self.find_and_attack_target()
                continue
            if self.afk_interval_minutes and time.time() - self.last_afk_time >= self.afk_interval_minutes * 60 and not self._in_afk_mode:
                self._in_afk_mode = True
                afk_secs = min(self.afk_duration_minutes, 15) * 60
                afk_start = time.time()
                self.log(f"Entering AFK mode for {afk_secs} seconds", "INFO")
                while self.bot_running and time.time() - afk_start < afk_secs:
                    if time.time() - self.last_action_time > self.IDLE_TIMEOUT_SECONDS:
                        self.last_action_time = time.time()
                        break
                    if self.check_and_click_revive():
                        self.last_action_time = time.time()
                        if self.stop_bot_on_death.get():
                            self.stop_bot()
                            return
                    time.sleep(0.1)
                self.last_afk_time = time.time()
                self._in_afk_mode = False
                self.log("Exiting AFK mode", "INFO")
                continue
            self.check_aq3d_status()
            if not self.aq3d_running:
                self.stop_bot()
                return
            if not self.focus_aq3d():
                time.sleep(0.5)
                continue
            if self.check_and_handle_potions():
                continue
            if self.check_and_click_revive():
                self.last_action_time = time.time()
                if self.stop_bot_on_death.get():
                    self.stop_bot()
                continue
            self.find_and_attack_target()
            self.last_action_time = time.time()
            time.sleep(0.1)

    def focus_aq3d(self):
        if not self.focus_aq3d_enabled.get():
            self.root.attributes('-topmost', False)
            return True
        try:
            hwnd = win32gui.FindWindow(None, "AQ3D")
            if not hwnd:
                return False
            self.root.attributes('-topmost', False)
            time.sleep(0.05)
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.05)
            self.root.attributes('-topmost', True)
            focused = win32gui.GetForegroundWindow() == hwnd
            self.log(f"AQ3D window focus {'successful' if focused else 'attempted'}", "INFO")
            return focused
        except Exception:
            self.log("Attempted to focus AQ3D window", "INFO")
            return False

    def find_and_attack_target(self):
        if not self.bot_running:
            return
        self.last_action_time = time.time()
        if self.stick_to_injured.get() and self.current_sticky_target:
            name = self.read_enemy_name()
            enemy_health = self.get_enemy_health_percentage()
            if name and enemy_health is not None and name == self.current_sticky_target:
                self.attack_current_target(name)
                return
            else:
                self.update_kill_count()
                self.current_sticky_target = None
        filters = [f.lower().strip() for f in self.target_enemy_names_list if f.strip()]
        self.log(f"Searching for target with filters: {filters}", "INFO")
        if self.auto_target.get():
            for _ in range(10):
                if not self.bot_running:
                    return
                pyautogui.press('tab')
                self.last_action_time = time.time()
                time.sleep(0.05)
                enemy_health = self.get_enemy_health_percentage()
                if enemy_health is None:
                    return
                if enemy_health < 100 or not self.ignore_full_health_enemies.get():
                    name = self.read_enemy_name()
                    if name and enemy_health < 100 and self.stick_to_injured.get():
                        self.current_sticky_target = name
                    self.last_enemy_detection_time = time.time()
                    self.attack_current_target(name)
                    return
                time.sleep(0.05)
            self.move_randomly()
            return
        name = self.read_enemy_name()
        enemy_health = self.get_enemy_health_percentage()
        if enemy_health is None:
            return
        if name and len(name) >= 3 and (enemy_health < 100 or not self.ignore_full_health_enemies.get()):
            if enemy_health < 100 and self.stick_to_injured.get():
                self.current_sticky_target = name
            self.last_enemy_detection_time = time.time()
            self.attack_current_target(name)
            return
        if not filters:
            for _ in range(10):
                if not self.bot_running:
                    return
                pyautogui.press('tab')
                self.last_action_time = time.time()
                time.sleep(0.05)
                name = self.read_enemy_name()
                if name and len(name) < 3:
                    continue
                enemy_health = self.get_enemy_health_percentage()
                if enemy_health is None:
                    return
                if name and (enemy_health < 100 or not self.ignore_full_health_enemies.get()):
                    if enemy_health < 100 and self.stick_to_injured.get():
                        self.current_sticky_target = name
                    self.last_enemy_detection_time = time.time()
                    self.attack_current_target(name)
                    return
            self.move_randomly()
        else:
            for prio, filter_str in enumerate(filters):
                for _ in range(3):
                    if not self.bot_running:
                        return
                    pyautogui.press('tab')
                    self.last_action_time = time.time()
                    time.sleep(0.05)
                    name = self.read_enemy_name()
                    if name and len(name) < 3:
                        continue
                    enemy_health = self.get_enemy_health_percentage()
                    if enemy_health is None:
                        return
                    if name and (filter_str in name.lower()) and (enemy_health < 100 or not self.ignore_full_health_enemies.get()):
                        if enemy_health < 100 and self.stick_to_injured.get():
                            self.current_sticky_target = name
                        self.last_enemy_detection_time = time.time()
                        self.attack_current_target(name)
                        return
            for _ in range(10):
                if not self.bot_running:
                    return
                pyautogui.press('tab')
                self.last_action_time = time.time()
                time.sleep(0.05)
                name = self.read_enemy_name()
                if name and len(name) < 3:
                    continue
                enemy_health = self.get_enemy_health_percentage()
                if enemy_health is None:
                    return
                if name and (enemy_health < 100 or not self.ignore_full_health_enemies.get()):
                    if enemy_health < 100 and self.stick_to_injured.get():
                        self.current_sticky_target = name
                    self.last_enemy_detection_time = time.time()
                    self.attack_current_target(name)
                    return
            self.move_randomly()

    def read_enemy_name(self):
        if not TESSERACT_CONFIGURED or not self.health_box:
            self.log("Attempting to read enemy name without OCR or health box", "INFO")
            return None
        for attempt in range(3):
            try:
                ss = ImageGrab.grab(bbox=self.health_box)
                img = ss.convert('L')
                img = ImageEnhance.Contrast(img).enhance(2.0)
                img = img.point(lambda p: 255 if p > 140 else 0)
                img = ImageOps.invert(img)
                text = pytesseract.image_to_string(
                    img, config=r'--oem 3 --psm 6 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 '
                ).strip()
                cleaned = ''.join(c for c in text if c.isalnum() or c.isspace()).strip()
                if cleaned:
                    self.log(f"Enemy name read: '{cleaned}'", "INFO")
                    return cleaned
                self.log(f"Enemy name OCR attempt {attempt + 1}: no text detected", "INFO")
                time.sleep(0.05)
            except Exception:
                self.log(f"Enemy name OCR attempt {attempt + 1} processed", "INFO")
        self.log("Completed enemy name OCR attempts", "INFO")
        return None

    def attack_current_target(self, expected_name=None):
        start = time.time()
        has_attacked = False
        while self.bot_running and time.time() - start < 30:
            current_time = time.time()
            if current_time - self.last_action_time > self.IDLE_TIMEOUT_SECONDS:
                return
            if self.check_and_handle_potions():
                continue
            if self.check_and_click_revive():
                self.last_action_time = time.time()
                if self.stop_bot_on_death.get():
                    self.stop_bot()
                return
            name = self.read_enemy_name()
            if not name:
                if has_attacked:
                    self.update_kill_count()
                return
            enemy_health = self.get_enemy_health_percentage()
            if enemy_health is None:
                return
            if enemy_health == 100 and self.ignore_full_health_enemies.get():
                return
            if expected_name and name.lower() != expected_name.lower():
                return
            self.try_use_available_skill(current_time)
            has_attacked = True
            self.last_action_time = current_time
            if self.jump_while_attacking.get() and random.random() < 0.25:
                pyautogui.press('space')
                self.last_action_time = time.time()
                self.log("Performed jump while attacking", "INFO")
            time.sleep(0.1)

    def try_use_available_skill(self, current_time):
        if not self.bot_running or current_time - self.last_skill_attempt_time < self.skill_debounce_interval:
            return
        self.last_skill_attempt_time = current_time
        ready = [
            i for i, enabled in enumerate(self.skill_enabled) 
            if enabled and current_time - self.last_skill_use_time[i] >= self.skill_cooldowns[i]
        ]
        if ready:
            skill_idx = max(ready)
            self.use_skill(skill_idx)
            self.log(f"Used skill: {self.skill_names[skill_idx]}", "INFO")

    def use_skill(self, idx):
        if not self.bot_running:
            return
        pyautogui.press(self.skill_keys[idx])
        self.last_skill_use_time[idx] = time.time()
        self.last_action_time = time.time()
        self.log(f"Pressed skill key: {self.skill_keys[idx]}", "INFO")

    def check_and_handle_potions(self):
        if not self.bot_running:
            return False
        current_time = time.time()
        if current_time - self.last_action_time > self.IDLE_TIMEOUT_SECONDS:
            return False
        health = self.get_player_health_percentage()
        if health is None:
            self.last_potion_status = "Health read attempted"
            self.potion_status_label.configure(text=self.last_potion_status)
            self.log("Attempted to read player health", "INFO")
            return False
        available_potions = sum(
            1 for i in range(3) if self.potion_enabled[i] and self.potion_hotkeys[i]
        )
        if not available_potions:
            self.last_potion_status = "No potions enabled"
            self.potion_status_label.configure(text=self.last_potion_status)
            self.log("No potions enabled for use", "INFO")
            return False
        max_attempts = available_potions
        attempt = 0
        for i in range(3):
            if not self.bot_running:
                return False
            if not self.potion_enabled[i] or not self.potion_hotkeys[i]:
                continue
            if health >= self.potion_health_thresholds[i]:
                continue
            if not self.focus_aq3d():
                self.last_potion_status = "Focus attempted"
                self.potion_status_label.configure(text=self.last_potion_status)
                continue
            current_time = time.time()
            if current_time - self.last_action_time > self.IDLE_TIMEOUT_SECONDS:
                return False
            time_since_last_potion = current_time - self.last_potion_use_time[i]
            if time_since_last_potion < self.potion_cooldowns[i]:
                continue
            pyautogui.press(self.potion_hotkeys[i])
            self.last_potion_use_time[i] = time.time()
            self.last_action_time = time.time()
            self.last_potion_status = f"Used Potion {i+1} '{self.potion_hotkeys[i]}' at {health}%"
            self.potion_status_label.configure(text=self.last_potion_status)
            self.log(f"Used potion {i+1} at {health}% health", "INFO")
            attempt += 1
            time.sleep(0.1)
            if attempt >= max_attempts:
                self.last_potion_status = "Max potion attempts reached"
                self.potion_status_label.configure(text=self.last_potion_status)
                self.log("Reached maximum potion attempts", "INFO")
                return True
        if attempt == 0:
            self.last_potion_status = "No potions needed"
            self.potion_status_label.configure(text=self.last_potion_status)
            self.log("No potions needed at current health", "INFO")
        return attempt > 0

    def check_and_click_revive(self):
        if not TESSERACT_CONFIGURED or not self.detect_revive_box or not self.bot_running:
            return False
        current_time = time.time()
        if current_time - self.last_action_time > self.IDLE_TIMEOUT_SECONDS:
            return False
        try:
            ss = ImageGrab.grab(bbox=self.detect_revive_box)
            img = ss.convert('L')
            img = ImageEnhance.Contrast(img).enhance(2.5)
            img = img.point(lambda p: 0 if p > 175 else 255)
            text = pytesseract.image_to_string(img, config=r'--oem 3 --psm 6').strip()
            if self.save_debug_images.get():
                self.save_debug_image(ss, "revive_attempt")
            if "revive" in text.lower():
                if not self.focus_aq3d():
                    return False
                time.sleep(0.5)
                x = (self.detect_revive_box[0] + self.detect_revive_box[2]) // 2
                y = (self.detect_revive_box[1] + self.detect_revive_box[3]) // 2
                pyautogui.click(x, y)
                self.last_action_time = time.time()
                self.log("Clicked revive button", "INFO")
                return True
            return False
        except Exception:
            self.log("Attempted revive button check", "INFO")
            if self.save_debug_images.get():
                self.save_debug_image(ss, "revive_attempt")
            return False

    def save_debug_image(self, image, prefix):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = os.path.join(self.DEBUG_IMAGE_DIR, f"{prefix}_{timestamp}.png")
        try:
            image.save(filename)
            self.log(f"Saved debug image: {filename}", "INFO")
        except Exception:
            self.log(f"Attempted to save debug image: {filename}", "INFO")

    def validate_health_box(self, box, box_name):
        if not box:
            return False
        x1, y1, x2, y2 = box
        if x2 <= x1 or y2 <= y1 or x2 - x1 < 20 or y2 - y1 < 10:
            return False
        return True

    def get_player_health_percentage(self):
        if not TESSERACT_CONFIGURED or not self.player_health_box or not self.validate_health_box(self.player_health_box, "player health"):
            self.log("Attempting to read player health without OCR or valid box", "INFO")
            return None
        if time.time() - self.last_health_read_time < self.health_debounce_interval:
            return None
        self.last_health_read_time = time.time()
        for attempt in range(10):
            if not self.bot_running:
                return None
            try:
                ss = ImageGrab.grab(bbox=self.player_health_box)
                img = ss.convert('L')
                img = ImageEnhance.Contrast(img).enhance(3.0)
                img = img.point(lambda p: 0 if p > 150 else 255)
                text = pytesseract.image_to_string(
                    img, config=r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789/%'
                ).strip()
                if self.save_debug_images.get():
                    self.save_debug_image(ss, f"player_health_attempt_{attempt}")
                match = re.search(r'(\d{1,3})\s*%', text)
                if match:
                    health = int(match.group(1))
                    if 0 <= health <= 100:
                        self.invalid_player_health_count = 0
                        self.log(f"Player health read: {health}%", "INFO")
                        return health
                    self.invalid_player_health_count += 1
                    self.log(f"Player health OCR attempt {attempt + 1}: invalid value {health}%", "INFO")
                    if self.invalid_player_health_count >= self.max_invalid_player_health:
                        messagebox.showinfo("Info", "Too many invalid health readings. Reconfigure player health box.")
                        self.invalid_player_health_count = 0
                else:
                    self.log(f"Player health OCR attempt {attempt + 1}: no percentage detected", "INFO")
                time.sleep(0.05)
            except Exception:
                self.log(f"Player health OCR attempt {attempt + 1} processed", "INFO")
                if self.save_debug_images.get():
                    self.save_debug_image(ss, f"player_health_attempt_{attempt}")
        self.log("Completed player health OCR attempts", "INFO")
        return None

    def get_enemy_health_percentage(self):
        if not TESSERACT_CONFIGURED or not self.enemy_health_box or not self.validate_health_box(self.enemy_health_box, "enemy health"):
            self.log("Attempting to read enemy health without OCR or valid box", "INFO")
            return None
        try:
            ss = ImageGrab.grab(bbox=self.enemy_health_box)
            img = ss.convert('L')
            img = ImageEnhance.Contrast(img).enhance(3.0)
            img = img.point(lambda p: 0 if p > 150 else 255)
            text = pytesseract.image_to_string(
                img, config=r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789/%'
            ).strip()
            if self.save_debug_images.get():
                self.save_debug_image(ss, "enemy_health")
            match = re.search(r'(\d{1,3})\s*%', text)
            if match:
                health = int(match.group(1))
                if 0 <= health <= 100:
                    self.log(f"Enemy health read: {health}%", "INFO")
                    return health
            self.log("No valid enemy health percentage detected", "INFO")
            return None
        except Exception:
            self.log("Attempted to read enemy health", "INFO")
            if self.save_debug_images.get():
                self.save_debug_image(ss, "enemy_health")
            return None

    def move_randomly(self):
        if not self.bot_running or self.anchor_mode.get():
            return
        active_keys = [k for k, v in self.movement_keys.items() if v and self.movement_key_vars[k].get()]
        if not active_keys:
            self.log("No movement keys enabled", "INFO")
            return
        for _ in range(self.movement_loops):
            if not self.bot_running:
                return
            if not self.focus_aq3d():
                time.sleep(0.5)
                continue
            key = random.choice(active_keys)
            duration = random.uniform(0.2, 0.6)
            pyautogui.keyDown(key)
            time.sleep(duration)
            pyautogui.keyUp(key)
            self.last_action_time = time.time()
            self.log(f"Moved with key '{key}' for {duration:.2f} seconds", "INFO")
            if self.jump_while_moving.get() and random.random() < 0.25:
                pyautogui.press('space')
                self.log("Performed jump while moving", "INFO")
            time.sleep(random.uniform(0.1, 0.3))

    def update_kill_count(self):
        self.kill_count += 1
        self.kill_count_label.configure(text=f"Kills: {self.kill_count}")
        self.log(f"Kill detected, total: {self.kill_count}", "SUCCESS")

    def on_closing(self):
        if self.bot_running:
            self.stop_bot()
        if self.settings_modified and messagebox.askyesno("Unsaved", "Save settings before closing?"):
            self.save_all_settings()
        self.root.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = BotApp(root)
    root.mainloop()