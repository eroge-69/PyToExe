import subprocess as sp
import ctypes as ct
import atexit
import keyboard
import psutil
import threading
import customtkinter as ctk
import sys
from typing import Optional
from win32gui import GetForegroundWindow, GetWindowRect, SetWindowPos
import win32con as wc
import win32process

RULE_NAME = "Roblox_Block"
DEFAULT_KEYBIND = "f6"

class SphadzLag:
    def __init__(self) -> None:
        self.settings = {
            'Keybind': DEFAULT_KEYBIND,
            'Lagswitch': 'off',
            'AutoTurnOff': False,
            'AutoTurnBackOn': False,
            'Overlay': False
        }
        self.block_flag: bool = False
        self.lagswitch_active: bool = False
        self.manual_override: bool = False
        self.timer_duration: float = 9.8
        self.reactivation_duration: float = 0.2
        self.active_timer: Optional[threading.Timer] = None
        self.timer_lock = threading.Lock()
        self.lagswitch_cycle_event = threading.Event()
        self.auto_cycle_thread: Optional[threading.Thread] = None
        self.keybind_temp_handler: Optional[int] = None
        self.keybind_handler: Optional[int] = None
        self.status_window: Optional[ctk.CTkToplevel] = None
        self.overlay_update_event = threading.Event()
        self.overlay_update_thread: Optional[threading.Thread] = None

        # Set modern dark theme with green accents
        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme('green')
        
        self.root = ctk.CTk()
        self.root.title('Sphadz Lag V2.3.2')
        self.root.geometry('420x280')
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)
        
        # Configure custom colors
        self.root.configure(fg_color=('#1a1a1a', '#1a1a1a'))
        
        # Create main frame with padding
        self.main_frame = ctk.CTkFrame(self.root, fg_color=('#2b2b2b', '#2b2b2b'), corner_radius=15)
        self.main_frame.pack(fill='both', expand=True, padx=15, pady=15)

        self.check_requirements()
        self.setup_ui()
        self.setup_keybind()

    def setup_ui(self) -> None:
        # Title section
        title_frame = ctk.CTkFrame(self.main_frame, fg_color='transparent')
        title_frame.pack(fill='x', padx=20, pady=(15, 10))
        
        self.status_label = ctk.CTkLabel(
            title_frame, text='LagSwitch OFF', text_color='#ff4444',
            font=('Segoe UI', 18, 'bold')
        )
        self.status_label.pack(side='left')
        
        author_label = ctk.CTkLabel(
            title_frame, text='Made by Sphadz', 
            text_color='#888888', font=('Segoe UI', 12)
        )
        author_label.pack(side='right')
        
        # Separator
        separator = ctk.CTkFrame(self.main_frame, height=2, fg_color='#444444')
        separator.pack(fill='x', padx=20, pady=5)
        
        # Control section
        controls_frame = ctk.CTkFrame(self.main_frame, fg_color='transparent')
        controls_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left column
        left_column = ctk.CTkFrame(controls_frame, fg_color='transparent')
        left_column.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Keybind section
        keybind_frame = ctk.CTkFrame(left_column, fg_color='#333333', corner_radius=10)
        keybind_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(
            keybind_frame, text='Keybind Settings', 
            font=('Segoe UI', 14, 'bold'), text_color='#00ff88'
        ).pack(pady=(10, 5))
        
        self.keybind_label = ctk.CTkLabel(
            keybind_frame, text=f"Current: {self.settings['Keybind'].upper()}", 
            font=('Segoe UI', 12), text_color='#ffffff'
        )
        self.keybind_label.pack(pady=5)
        
        keybind_btn = ctk.CTkButton(
            keybind_frame, text='Change Keybind', 
            command=self.change_keybind, fg_color='#00aa55', 
            hover_color='#00cc66', corner_radius=8, height=35
        )
        keybind_btn.pack(pady=(0, 10))
        
        # Auto features section
        auto_frame = ctk.CTkFrame(left_column, fg_color='#333333', corner_radius=10)
        auto_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(
            auto_frame, text='Auto Features', 
            font=('Segoe UI', 14, 'bold'), text_color='#00ff88'
        ).pack(pady=(10, 5))
        
        self.auto_turnoff_var = ctk.BooleanVar(value=self.settings['AutoTurnOff'])
        auto_turnoff_cb = ctk.CTkCheckBox(
            auto_frame, text='Anti-Timeout', variable=self.auto_turnoff_var,
            command=self.update_auto_turnoff, text_color='#ffffff',
            fg_color='#00aa55', hover_color='#00cc66', checkmark_color='#ffffff'
        )
        auto_turnoff_cb.pack(anchor='w', padx=15, pady=5)
        
        self.auto_turnbackon_var = ctk.BooleanVar(value=self.settings['AutoTurnBackOn'])
        auto_turnbackon_cb = ctk.CTkCheckBox(
            auto_frame, text='Auto Reactivate', variable=self.auto_turnbackon_var,
            command=self.update_auto_turnbackon, text_color='#ffffff',
            fg_color='#00aa55', hover_color='#00cc66', checkmark_color='#ffffff'
        )
        auto_turnbackon_cb.pack(anchor='w', padx=15, pady=(0, 10))
        
        # Right column
        right_column = ctk.CTkFrame(controls_frame, fg_color='transparent')
        right_column.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Display settings
        display_frame = ctk.CTkFrame(right_column, fg_color='#333333', corner_radius=10)
        display_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(
            display_frame, text='Display Settings', 
            font=('Segoe UI', 14, 'bold'), text_color='#00ff88'
        ).pack(pady=(10, 5))
        
        self.always_on_top_var = ctk.BooleanVar(value=True)
        always_top_cb = ctk.CTkCheckBox(
            display_frame, text='Always on Top', variable=self.always_on_top_var,
            command=self.toggle_always_on_top, text_color='#ffffff',
            fg_color='#00aa55', hover_color='#00cc66', checkmark_color='#ffffff'
        )
        always_top_cb.pack(anchor='w', padx=15, pady=5)
        
        self.overlay_var = ctk.BooleanVar(value=self.settings['Overlay'])
        overlay_cb = ctk.CTkCheckBox(
            display_frame, text='Game Overlay', variable=self.overlay_var,
            command=self.toggle_status_window, text_color='#ffffff',
            fg_color='#00aa55', hover_color='#00cc66', checkmark_color='#ffffff'
        )
        overlay_cb.pack(anchor='w', padx=15, pady=(0, 10))
        
        # Timer settings
        timer_frame = ctk.CTkFrame(right_column, fg_color='#333333', corner_radius=10)
        timer_frame.pack(fill='x')
        
        ctk.CTkLabel(
            timer_frame, text='Timer Settings', 
            font=('Segoe UI', 14, 'bold'), text_color='#00ff88'
        ).pack(pady=(10, 5))
        
        # Timer duration
        timer_duration_frame = ctk.CTkFrame(timer_frame, fg_color='transparent')
        timer_duration_frame.pack(fill='x', padx=15, pady=5)
        
        ctk.CTkLabel(
            timer_duration_frame, text='Duration:', 
            font=('Segoe UI', 11), text_color='#ffffff'
        ).pack(side='left')
        
        self.timer_label = ctk.CTkLabel(
            timer_duration_frame, text=f"{self.timer_duration:.1f}s", 
            font=('Segoe UI', 11, 'bold'), text_color='#00ff88'
        )
        self.timer_label.pack(side='right')
        
        self.timer_slider = ctk.CTkSlider(
            timer_duration_frame, from_=0, to=10, number_of_steps=100,
            command=self.update_timer_duration, fg_color='#00aa55',
            progress_color='#00ff88', button_color='#00ff88', 
            button_hover_color='#00cc66'
        )
        self.timer_slider.set(self.timer_duration)
        self.timer_slider.pack(fill='x', pady=(0, 10))
        
        # Reactivation duration
        reactivation_duration_frame = ctk.CTkFrame(timer_frame, fg_color='transparent')
        reactivation_duration_frame.pack(fill='x', padx=15, pady=5)
        
        ctk.CTkLabel(
            reactivation_duration_frame, text='Reactivation:', 
            font=('Segoe UI', 11), text_color='#ffffff'
        ).pack(side='left')
        
        self.reactivation_label = ctk.CTkLabel(
            reactivation_duration_frame, text=f"{self.reactivation_duration:.1f}s", 
            font=('Segoe UI', 11, 'bold'), text_color='#00ff88'
        )
        self.reactivation_label.pack(side='right')
        
        self.reactivation_slider = ctk.CTkSlider(
            reactivation_duration_frame, from_=0, to=1, number_of_steps=10,
            command=self.update_reactivation_duration, fg_color='#00aa55',
            progress_color='#00ff88', button_color='#00ff88', 
            button_hover_color='#00cc66'
        )
        self.reactivation_slider.set(self.reactivation_duration)
        self.reactivation_slider.pack(fill='x', pady=(0, 15))

    def toggle_status_window(self) -> None:
        if self.overlay_var.get():
            self.open_status_window()
            self.start_overlay_update()
        else:
            self.close_status_window()
            self.stop_overlay_update()

    def open_status_window(self) -> None:
        if self.status_window is None or not self.status_window.winfo_exists():
            self.status_window = ctk.CTkToplevel(self.root)
            self.status_window.overrideredirect(True)
            self.status_window.attributes('-topmost', True)
            self.status_window.attributes('-transparentcolor', self.status_window['bg'])
            self.status_window.configure(fg_color=('#1a1a1a', '#1a1a1a'))
            
            # Create a frame for the overlay content
            overlay_frame = ctk.CTkFrame(self.status_window, fg_color='#2b2b2b', corner_radius=10)
            overlay_frame.pack(expand=True, fill='both', padx=10, pady=10)
            
            self.status_window_label = ctk.CTkLabel(
                overlay_frame, text='LagSwitch OFF', text_color='#ff4444',
                font=('Segoe UI', 16, 'bold')
            )
            self.status_window_label.place(relx=0.5, rely=0.5, anchor='center')
            self.update_status_window()

    def close_status_window(self) -> None:
        if self.status_window and self.status_window.winfo_exists():
            self.status_window.destroy()
            self.status_window = None

    def start_overlay_update(self) -> None:
        if not self.overlay_update_thread or not self.overlay_update_thread.is_alive():
            self.overlay_update_event.clear()
            self.overlay_update_thread = threading.Thread(target=self.overlay_update_loop, daemon=True)
            self.overlay_update_thread.start()

    def stop_overlay_update(self) -> None:
        self.overlay_update_event.set()

    def overlay_update_loop(self) -> None:
        previous_rect = None
        previous_active = None
        while not self.overlay_update_event.is_set():
            self.overlay_update_event.wait(0.05)
            try:
                if self.overlay_var.get() and self.status_window and self.status_window.winfo_exists():
                    current_window = GetForegroundWindow()
                    rect = GetWindowRect(current_window)
                    _, pid = win32process.GetWindowThreadProcessId(current_window)
                    current_process = psutil.Process(pid)
                    is_roblox = current_process.name().lower() == 'robloxplayerbeta.exe'
                    if is_roblox and (previous_rect != rect or previous_active != is_roblox):
                        self.status_window.deiconify()
                        width, height = rect[2] - rect[0], rect[3] - rect[1]
                        self.status_window.geometry(f"{width}x{height}+{rect[0]}+{rect[1]}")
                        SetWindowPos(
                            self.status_window.winfo_id(), wc.HWND_TOPMOST,
                            rect[0], rect[1], width, height, wc.SWP_NOACTIVATE
                        )
                    elif not is_roblox and previous_active != is_roblox:
                        self.status_window.withdraw()
                    previous_rect = rect
                    previous_active = is_roblox
            except Exception:
                pass

    def update_status_window(self) -> None:
        status_text = 'LagSwitch ON' if self.block_flag else 'LagSwitch OFF'
        status_color = '#00ff88' if self.block_flag else '#ff4444'
        try:
            if self.status_window and hasattr(self, "status_window_label"):
                self.status_window_label.configure(text=status_text, text_color=status_color)
        except Exception:
            pass

    def update_status_label(self) -> None:
        status_text = 'LagSwitch ON' if self.block_flag else 'LagSwitch OFF'
        status_color = '#00ff88' if self.block_flag else '#ff4444'
        self.status_label.configure(text=status_text, text_color=status_color)
        self.update_status_window()

    def update_auto_turnoff(self) -> None:
        self.settings['AutoTurnOff'] = self.auto_turnoff_var.get()

    def update_auto_turnbackon(self) -> None:
        self.settings['AutoTurnBackOn'] = self.auto_turnbackon_var.get()

    def update_timer_duration(self, value: float) -> None:
        self.timer_duration = float(value)
        self.timer_label.configure(text=f"{self.timer_duration:.1f}s")

    def update_reactivation_duration(self, value: float) -> None:
        self.reactivation_duration = float(value)
        self.reactivation_label.configure(text=f"{self.reactivation_duration:.1f}s")

    def toggle_always_on_top(self) -> None:
        self.root.attributes('-topmost', self.always_on_top_var.get())

    def change_keybind(self) -> None:
        self.keybind_label.configure(text='Press a key...', text_color='#00ff88')
        self.keybind_temp_handler = keyboard.on_press(self.set_keybind)

    def set_keybind(self, event) -> None:
        new_key = event.name
        self.settings['Keybind'] = new_key
        self.keybind_label.configure(text=f"Current: {new_key.upper()}", text_color='#ffffff')
        if self.keybind_temp_handler is not None:
            keyboard.unhook(self.keybind_temp_handler)
            self.keybind_temp_handler = None
        if self.keybind_handler is not None:
            keyboard.unhook(self.keybind_handler)
            self.keybind_handler = None
        self.keybind_handler = keyboard.on_press_key(new_key, self.toggle_block)

    def activate_lagswitch(self) -> None:
        self.lagswitch_active = True
        self.manual_override = False
        self.turn_on_lag_switch()
        if self.settings['AutoTurnOff']:
            self.lagswitch_cycle_event.clear()
            self.auto_cycle_thread = threading.Thread(target=self.lagswitch_cycle_loop, daemon=True)
            self.auto_cycle_thread.start()

    def deactivate_lagswitch(self) -> None:
        self.lagswitch_active = False
        self.lagswitch_cycle_event.set()
        if self.active_timer:
            self.active_timer.cancel()
            self.active_timer = None
        self.turn_off_lag_switch()

    def lagswitch_cycle_loop(self) -> None:
        while self.lagswitch_active and not self.lagswitch_cycle_event.is_set():
            if self.lagswitch_cycle_event.wait(self.timer_duration):
                break
            self.turn_off_lag_switch()
            if self.lagswitch_cycle_event.wait(self.reactivation_duration):
                break
            if self.lagswitch_active:
                if self.settings['AutoTurnBackOn']:
                    self.turn_on_lag_switch()
                else:
                    self.lagswitch_active = False
                    self.update_status_label()
                    break

    def turn_on_lag_switch(self) -> None:
        self.block_flag = True
        self.update_firewall_rules('block')
        self.update_status_label()

    def turn_off_lag_switch(self) -> None:
        self.block_flag = False
        self.update_firewall_rules('delete')
        self.update_status_label()

    def toggle_block(self, event) -> None:
        if event.name != self.settings['Keybind']:
            return
        if self.lagswitch_active:
            self.deactivate_lagswitch()
        else:
            self.activate_lagswitch()

    def update_firewall_rules(self, action: str) -> None:
        try:
            roblox_process = next(
                (proc for proc in psutil.process_iter(['pid', 'name', 'exe'])
                 if proc.info['name'] == 'RobloxPlayerBeta.exe' and
                    proc.info.get('exe', '').lower().find('roblox') != -1),
                None
            )
            if not roblox_process:
                self.disable_lag_switch()
                return
            exe_path = roblox_process.exe()
            if action == 'block':
                cmd = ['netsh', 'advfirewall', 'firewall', 'add', 'rule',
                       f'name={RULE_NAME}', 'dir=out', 'action=block', f'program={exe_path}']
            else:
                cmd = ['netsh', 'advfirewall', 'firewall', 'delete', 'rule', f'name={RULE_NAME}']
            sp.run(cmd, creationflags=sp.CREATE_NO_WINDOW)
        except psutil.NoSuchProcess:
            self.disable_lag_switch()
        except Exception:
            pass

    def check_requirements(self) -> None:
        if not self.is_admin():
            self.show_message('Sphadz Lag requires administrator privileges to run.')
            sys.exit(1)
        if not any(proc.info['name'] == 'RobloxPlayerBeta.exe' for proc in psutil.process_iter(['name'])):
            self.show_message('Roblox is not running. Please start Roblox and try again.')
            sys.exit(1)

    def is_admin(self) -> bool:
        try:
            return bool(ct.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False

    def show_message(self, message: str) -> None:
        ct.windll.user32.MessageBoxW(0, message, 'Sphadz Lag V2.3.2', 0)

    def disable_lag_switch(self) -> None:
        try:
            result = sp.run(['netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name=all'],
                            capture_output=True, text=True)
            rules = [line.split(':')[1].strip() for line in result.stdout.splitlines() if 'Rule Name:' in line]
            for rule in rules:
                if RULE_NAME in rule:
                    sp.run(['netsh', 'advfirewall', 'firewall', 'delete', 'rule', f"name={rule}"])
        except Exception:
            pass
        if self.keybind_handler is not None:
            keyboard.unhook(self.keybind_handler)
        self.root.destroy()
        sys.exit(1)

    def setup_keybind(self) -> None:
        key = self.settings.get('Keybind', DEFAULT_KEYBIND)
        self.settings['Keybind'] = key
        self.keybind_label.configure(text=f"Current: {key.upper()}")
        self.keybind_handler = keyboard.on_press_key(key, self.toggle_block)

    def run(self) -> None:
        atexit.register(self.exit_handler)
        self.root.mainloop()

    def exit_handler(self) -> None:
        self.lagswitch_cycle_event.set()
        self.update_firewall_rules('delete')
        self.overlay_update_event.set()

if __name__ == '__main__':
    try:
        app = SphadzLag()
        app.run()
    except Exception:
        pass
