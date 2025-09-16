import tkinter as tk
from tkinter import ttk, messagebox
import json
import threading
import time
import win32gui
import win32con
import win32api
import os

class SilkroadBot:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Silkroad Online Bot - Python")
        self.root.geometry("420x550")
        self.root.resizable(False, False)
        
        # Variables
        self.running = False
        self.current_window = None
        self.skill_timers = {}
        self.buff_timers = {}
        self.bot_thread = None
        
        # Key mappings
        self.key_map = {
            'F1': 0x70, 'F2': 0x71, 'F3': 0x72, 'F4': 0x73,
            '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
            '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39
        }
        
        self.setup_ui()
        self.refresh_windows()
        self.load_config()
        
    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg='lightgray', padx=10, pady=10)
        main_frame.pack(fill='both', expand=True)
        
        # Window selection
        window_label = tk.Label(main_frame, text="Select Window:", font=('Arial', 10, 'bold'))
        window_label.grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        window_frame = tk.Frame(main_frame)
        window_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        self.window_var = tk.StringVar()
        self.window_combo = ttk.Combobox(window_frame, textvariable=self.window_var, 
                                        state="readonly", width=40)
        self.window_combo.pack(side='left', fill='x', expand=True)
        
        refresh_btn = tk.Button(window_frame, text="Refresh", command=self.refresh_windows,
                               bg='lightblue', width=10)
        refresh_btn.pack(side='right', padx=(5, 0))
        
        # Buffs section
        buff_label = tk.Label(main_frame, text="Buffs:", font=('Arial', 10, 'bold'))
        buff_label.grid(row=2, column=0, sticky='w', pady=(10, 5))
        
        buff_frame = tk.Frame(main_frame, relief='sunken', bd=1)
        buff_frame.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(0, 5))
        
        # Buff listbox with scrollbar
        self.buff_listbox = tk.Listbox(buff_frame, height=6, font=('Arial', 9))
        buff_scrollbar = tk.Scrollbar(buff_frame, orient="vertical", command=self.buff_listbox.yview)
        self.buff_listbox.configure(yscrollcommand=buff_scrollbar.set)
        
        self.buff_listbox.pack(side='left', fill='both', expand=True)
        buff_scrollbar.pack(side='right', fill='y')
        
        # Buff buttons
        buff_btn_frame = tk.Frame(main_frame)
        buff_btn_frame.grid(row=4, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        add_buff_btn = tk.Button(buff_btn_frame, text="Add Buff", command=self.add_buff,
                                bg='lightgreen', width=12)
        add_buff_btn.pack(side='left')
        
        del_buff_btn = tk.Button(buff_btn_frame, text="Delete Buff", command=self.delete_buff,
                                bg='lightcoral', width=12)
        del_buff_btn.pack(side='right')
        
        # Attack Skills section
        skill_label = tk.Label(main_frame, text="Attack Skills:", font=('Arial', 10, 'bold'))
        skill_label.grid(row=5, column=0, sticky='w', pady=(10, 5))
        
        skill_frame = tk.Frame(main_frame, relief='sunken', bd=1)
        skill_frame.grid(row=6, column=0, columnspan=2, sticky='ew', pady=(0, 5))
        
        # Skill listbox with scrollbar
        self.skill_listbox = tk.Listbox(skill_frame, height=6, font=('Arial', 9))
        skill_scrollbar = tk.Scrollbar(skill_frame, orient="vertical", command=self.skill_listbox.yview)
        self.skill_listbox.configure(yscrollcommand=skill_scrollbar.set)
        
        self.skill_listbox.pack(side='left', fill='both', expand=True)
        skill_scrollbar.pack(side='right', fill='y')
        
        # Skill buttons
        skill_btn_frame = tk.Frame(main_frame)
        skill_btn_frame.grid(row=7, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        add_skill_btn = tk.Button(skill_btn_frame, text="Add Skill", command=self.add_skill,
                                 bg='lightgreen', width=12)
        add_skill_btn.pack(side='left')
        
        del_skill_btn = tk.Button(skill_btn_frame, text="Delete Skill", command=self.delete_skill,
                                 bg='lightcoral', width=12)
        del_skill_btn.pack(side='right')
        
        # Options
        self.use_zerk = tk.BooleanVar()
        zerk_check = tk.Checkbutton(main_frame, text="Use Zerk (Tab key)", variable=self.use_zerk,
                                   font=('Arial', 10))
        zerk_check.grid(row=8, column=0, sticky='w', pady=(10, 0))
        
        # Control buttons
        control_frame = tk.Frame(main_frame)
        control_frame.grid(row=9, column=0, columnspan=2, sticky='ew', pady=(20, 10))
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)
        
        self.start_btn = tk.Button(control_frame, text="Start Bot\n(F5)", command=self.start_bot,
                                  bg='green', fg='white', font=('Arial', 11, 'bold'),
                                  height=3, width=18)
        self.start_btn.grid(row=0, column=0, padx=(0, 5), sticky='ew')
        
        self.stop_btn = tk.Button(control_frame, text="Stop Bot\n(F5)", command=self.stop_bot,
                                 bg='red', fg='white', font=('Arial', 11, 'bold'),
                                 height=3, width=18, state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=(5, 0), sticky='ew')
        
        # Status
        self.status_label = tk.Label(main_frame, text="Status: Stopped", 
                                    font=('Arial', 12, 'bold'), fg='red')
        self.status_label.grid(row=10, column=0, columnspan=2, pady=10)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        
        # Bind events
        self.window_combo.bind('<<ComboboxSelected>>', self.on_window_change)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Bind F5 key for start/stop
        self.root.bind('<KeyPress-F5>', self.toggle_bot)
        self.root.focus_set()  # Make sure root can receive key events
        
    def refresh_windows(self):
        """Refresh the list of available windows"""
        windows = []
        
        def enum_window_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                try:
                    window_text = win32gui.GetWindowText(hwnd)
                    class_name = win32gui.GetClassName(hwnd)
                    
                    # Look for any visible window with text
                    if window_text and len(window_text.strip()) > 0:
                        windows.append(f"{window_text} (Handle: {hwnd})")
                except:
                    pass
            return True
        
        try:
            win32gui.EnumWindows(enum_window_callback, windows)
        except:
            windows = ["Error getting windows"]
        
        # Sort windows for better visibility
        windows.sort()
        
        self.window_combo['values'] = windows
        if windows and not self.window_var.get():
            # Set first window as default
            self.window_combo.current(0)
        
        print(f"Found {len(windows)} windows")  # Debug
    
    def get_window_handle(self):
        """Get handle from selected window"""
        if not self.window_var.get():
            return None
        
        try:
            # Extract handle from the combo box selection
            handle_str = self.window_var.get().split("Handle: ")[1].rstrip(")")
            return int(handle_str)
        except:
            return None
    
    def add_buff(self):
        """Open dialog to add buff"""
        dialog = BuffDialog(self.root, self.on_buff_added)
    
    def on_buff_added(self, belt, slot, delay):
        """Callback when buff is added"""
        buff_text = f"Belt: {belt} | Slot: {slot} | Delay: {delay}s"
        self.buff_listbox.insert(tk.END, buff_text)
        self.save_config()
    
    def delete_buff(self):
        """Delete selected buff"""
        selection = self.buff_listbox.curselection()
        if selection:
            self.buff_listbox.delete(selection[0])
            self.save_config()
        else:
            messagebox.showwarning("Warning", "Please select a buff to delete")
    
    def add_skill(self):
        """Open dialog to add attack skill"""
        dialog = SkillDialog(self.root, self.on_skill_added)
    
    def on_skill_added(self, belt, slot):
        """Callback when skill is added"""
        skill_text = f"Belt: {belt} | Slot: {slot}"
        self.skill_listbox.insert(tk.END, skill_text)
        self.save_config()
    
    def delete_skill(self):
        """Delete selected skill"""
        selection = self.skill_listbox.curselection()
        if selection:
            self.skill_listbox.delete(selection[0])
            self.save_config()
        else:
            messagebox.showwarning("Warning", "Please select a skill to delete")
    
    def on_window_change(self, event=None):
        """Handle window selection change"""
        self.load_config()
    
    def get_config_filename(self):
        """Get config filename based on selected window"""
        window_text = self.window_var.get()
        if not window_text:
            return None
        
        # Create a safe filename from window title
        safe_name = "".join(c for c in window_text.split(" (Handle:")[0] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')[:50]  # Limit length
        return f"{safe_name}_config.json"
    
    def save_config(self):
        """Save current configuration to file"""
        config_file = self.get_config_filename()
        if not config_file:
            return
        
        config = {
            'buffs': [self.buff_listbox.get(i) for i in range(self.buff_listbox.size())],
            'skills': [self.skill_listbox.get(i) for i in range(self.skill_listbox.size())],
            'use_zerk': self.use_zerk.get()
        }
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def load_config(self):
        """Load configuration from file"""
        config_file = self.get_config_filename()
        if not config_file or not os.path.exists(config_file):
            # Clear lists if no config exists
            self.buff_listbox.delete(0, tk.END)
            self.skill_listbox.delete(0, tk.END)
            self.use_zerk.set(False)
            return
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Load buffs
            self.buff_listbox.delete(0, tk.END)
            for buff in config.get('buffs', []):
                self.buff_listbox.insert(tk.END, buff)
            
            # Load skills
            self.skill_listbox.delete(0, tk.END)
            for skill in config.get('skills', []):
                self.skill_listbox.insert(tk.END, skill)
            
            # Load zerk setting
            self.use_zerk.set(config.get('use_zerk', False))
            
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def toggle_bot(self, event=None):
        """Toggle bot on/off with F5 key"""
        if self.running:
            self.stop_bot()
        else:
            self.start_bot()
    
    def send_key(self, hwnd, key):
        """Send key press to window"""
        try:
            if key in self.key_map:
                vk_code = self.key_map[key]
                
                # Try both PostMessage and SendMessage methods
                result1 = win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, vk_code, 0)
                time.sleep(0.02)
                result2 = win32api.PostMessage(hwnd, win32con.WM_KEYUP, vk_code, 0)
                
                # Alternative method if PostMessage doesn't work
                if result1 == 0 or result2 == 0:
                    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, vk_code, 0)
                    time.sleep(0.02)
                    win32api.SendMessage(hwnd, win32con.WM_KEYUP, vk_code, 0)
                
                print(f"Sent key: {key} (VK: {vk_code}) to window {hwnd}")
                return True
        except Exception as e:
            print(f"Error sending key {key}: {e}")
            return False
        return False
    
    def use_skill(self, hwnd, belt, slot, delay=0.5):
        """Use a skill with timing control"""
        skill_key = f"skill_{belt}_{slot}"
        current_time = time.time()
        
        if skill_key not in self.skill_timers or (current_time - self.skill_timers[skill_key]) > delay:
            print(f"Attempting to use skill: {belt}-{slot}")
            
            # Send belt key multiple times (like in original code)
            for i in range(5):
                if self.send_key(hwnd, belt):
                    print(f"Belt key {belt} sent ({i+1}/5)")
                time.sleep(0.05)
            
            # Send slot key
            if self.send_key(hwnd, slot):
                print(f"Slot key {slot} sent")
            
            self.skill_timers[skill_key] = current_time
            return True
        return False
    
    def use_buff(self, hwnd, belt, slot, delay=300):
        """Use a buff with timing control"""
        buff_key = f"buff_{belt}_{slot}"
        current_time = time.time()
        
        if buff_key not in self.buff_timers or (current_time - self.buff_timers[buff_key]) > delay:
            print(f"Attempting to use buff: {belt}-{slot}")
            
            # Send belt key multiple times
            for i in range(5):
                if self.send_key(hwnd, belt):
                    print(f"Belt key {belt} sent ({i+1}/5)")
                time.sleep(0.05)
            
            # Send slot key
            if self.send_key(hwnd, slot):
                print(f"Slot key {slot} sent")
            
            self.buff_timers[buff_key] = current_time
            return True
        return False
    
    def parse_buff_string(self, buff_str):
        """Parse buff string to extract belt, slot, delay"""
        try:
            parts = buff_str.split(" | ")
            belt = parts[0].split(": ")[1]
            slot = parts[1].split(": ")[1]
            delay = float(parts[2].split(": ")[1].rstrip("s"))
            return belt, slot, delay
        except:
            return None, None, None
    
    def parse_skill_string(self, skill_str):
        """Parse skill string to extract belt, slot"""
        try:
            parts = skill_str.split(" | ")
            belt = parts[0].split(": ")[1]
            slot = parts[1].split(": ")[1]
            return belt, slot
        except:
            return None, None
    
    def bot_loop(self):
        """Main bot loop"""
        hwnd = self.get_window_handle()
        if not hwnd:
            self.root.after(0, self.stop_bot)
            messagebox.showerror("Error", "Invalid window handle!")
            return
        
        loop_count = 0
        while self.running:
            try:
                # Check if window still exists
                if not win32gui.IsWindow(hwnd):
                    print("Window closed, stopping bot")
                    break
                
                loop_count += 1
                
                # Process buffs
                buff_count = self.buff_listbox.size()
                for i in range(buff_count):
                    if not self.running:
                        break
                    
                    buff_str = self.buff_listbox.get(i)
                    belt, slot, delay = self.parse_buff_string(buff_str)
                    
                    if belt and slot and delay:
                        if self.use_buff(hwnd, belt, slot, delay):
                            print(f"Used buff: {belt}-{slot}")
                
                # Process attack skills
                skill_count = self.skill_listbox.size()
                for i in range(skill_count):
                    if not self.running:
                        break
                    
                    skill_str = self.skill_listbox.get(i)
                    belt, slot = self.parse_skill_string(skill_str)
                    
                    if belt and slot:
                        if self.use_skill(hwnd, belt, slot):
                            print(f"Used skill: {belt}-{slot}")
                            
                            # Use zerk if enabled
                            if self.use_zerk.get():
                                self.use_zerk_skill(hwnd)
                
                # Update status every 10 loops
                if loop_count % 10 == 0:
                    self.root.after(0, lambda: self.status_label.config(
                        text=f"Status: Running (Loop: {loop_count})"))
                
                time.sleep(0.1)  # Small delay to prevent high CPU usage
                
            except Exception as e:
                print(f"Bot loop error: {e}")
                break
        
        # Reset UI when loop ends
        self.root.after(0, self.reset_ui_after_stop)
    
    def use_zerk_skill(self, hwnd):
        """Use zerk skill (Tab key)"""
        try:
            win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, 0x09, 0)  # Tab key
            time.sleep(0.01)
            win32api.PostMessage(hwnd, win32con.WM_KEYUP, 0x09, 0)
            print("Used zerk")
        except Exception as e:
            print(f"Zerk error: {e}")
    
    def start_bot(self):
        """Start the bot"""
        if not self.window_var.get():
            messagebox.showerror("Error", "Please select a window!")
            return
        
        if self.buff_listbox.size() == 0 and self.skill_listbox.size() == 0:
            messagebox.showerror("Error", "Please add at least one buff or skill!")
            return
        
        # Test window handle first
        hwnd = self.get_window_handle()
        if not hwnd or not win32gui.IsWindow(hwnd):
            messagebox.showerror("Error", "Selected window is invalid or closed!")
            return
        
        window_title = win32gui.GetWindowText(hwnd)
        print(f"Starting bot for window: {window_title} (Handle: {hwnd})")
        
        self.running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_label.config(text="Status: Starting...", fg="orange")
        
        # Save config before starting
        self.save_config()
        
        # Start bot thread
        self.bot_thread = threading.Thread(target=self.bot_loop, daemon=True)
        self.bot_thread.start()
        
        print("Bot started successfully")
    
    def stop_bot(self):
        """Stop the bot"""
        self.running = False
        self.reset_ui_after_stop()
        print("Bot stopped")
    
    def reset_ui_after_stop(self):
        """Reset UI after bot stops"""
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_label.config(text="Status: Stopped", fg="red")
    
    def on_closing(self):
        """Handle application closing"""
        self.stop_bot()
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


class BuffDialog:
    def __init__(self, parent, callback):
        self.callback = callback
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Buff")
        self.dialog.geometry("250x180")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.transient(parent)
        
        # Main frame
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Belt selection
        tk.Label(main_frame, text="Belt:", font=('Arial', 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.belt_var = tk.StringVar(value="F1")
        belt_combo = ttk.Combobox(main_frame, textvariable=self.belt_var, values=["F1", "F2", "F3", "F4"], 
                                 state="readonly", width=15)
        belt_combo.grid(row=0, column=1, padx=(10, 0), pady=5)
        
        # Slot selection
        tk.Label(main_frame, text="Slot:", font=('Arial', 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.slot_var = tk.StringVar(value="1")
        slot_combo = ttk.Combobox(main_frame, textvariable=self.slot_var, 
                                 values=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
                                 state="readonly", width=15)
        slot_combo.grid(row=1, column=1, padx=(10, 0), pady=5)
        
        # Delay input
        tk.Label(main_frame, text="Delay (s):", font=('Arial', 10)).grid(row=2, column=0, sticky="w", pady=5)
        self.delay_var = tk.StringVar(value="300")
        delay_entry = tk.Entry(main_frame, textvariable=self.delay_var, width=18)
        delay_entry.grid(row=2, column=1, padx=(10, 0), pady=5)
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=15)
        
        ok_btn = tk.Button(button_frame, text="OK", command=self.ok_clicked, 
                          bg='lightgreen', width=10)
        ok_btn.pack(side="left", padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=self.dialog.destroy,
                              bg='lightcoral', width=10)
        cancel_btn.pack(side="left")
    
    def ok_clicked(self):
        try:
            belt = self.belt_var.get()
            slot = self.slot_var.get()
            delay = float(self.delay_var.get())
            
            if delay < 0:
                raise ValueError("Delay must be positive")
            
            self.callback(belt, slot, delay)
            self.dialog.destroy()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid delay value: {e}")


class SkillDialog:
    def __init__(self, parent, callback):
        self.callback = callback
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Attack Skill")
        self.dialog.geometry("250x150")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.transient(parent)
        
        # Main frame
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Belt selection
        tk.Label(main_frame, text="Belt:", font=('Arial', 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.belt_var = tk.StringVar(value="F1")
        belt_combo = ttk.Combobox(main_frame, textvariable=self.belt_var, values=["F1", "F2", "F3", "F4"], 
                                 state="readonly", width=15)
        belt_combo.grid(row=0, column=1, padx=(10, 0), pady=5)
        
        # Slot selection
        tk.Label(main_frame, text="Slot:", font=('Arial', 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.slot_var = tk.StringVar(value="1")
        slot_combo = ttk.Combobox(main_frame, textvariable=self.slot_var, 
                                 values=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
                                 state="readonly", width=15)
        slot_combo.grid(row=1, column=1, padx=(10, 0), pady=5)
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=15)
        
        ok_btn = tk.Button(button_frame, text="OK", command=self.ok_clicked,
                          bg='lightgreen', width=10)
        ok_btn.pack(side="left", padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=self.dialog.destroy,
                              bg='lightcoral', width=10)
        cancel_btn.pack(side="left")
    
    def ok_clicked(self):
        belt = self.belt_var.get()
        slot = self.slot_var.get()
        
        self.callback(belt, slot)
        self.dialog.destroy()


if __name__ == "__main__":
    try:
        app = SilkroadBot()
        app.run()
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")