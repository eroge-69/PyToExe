from tkinter import Tk, Label, Entry, Button, Text, filedialog, Scrollbar, END, messagebox, Frame, IntVar, Checkbutton
import os
import requests
import UnityPy
from datetime import datetime
import re
import threading
import binascii

# Constants
DARK_BG = "#1e1e1e"
LIGHT_TEXT = "#ffffff"
ACCENT_COLOR = "#4a6baf"
ERROR_COLOR = "#ff4444"
SUCCESS_COLOR = "#44ff44"

class AntiCheatHunter:
    def __init__(self, anti_patterns):
        self.patterns = [re.compile(re.escape(p), re.IGNORECASE) for p in anti_patterns]
        self.byte_patterns = [p.lower().encode('utf-8') for p in anti_patterns]
    
    def scan(self, obj, aggressive_mode):
        try:
            # Method 1: Check object type and path
            obj_str = f"{obj.type.name}_{obj.path_id}".lower()
            if any(p.search(obj_str) for p in self.patterns):
                return True

            # Method 2: Normal Unity object reading
            try:
                if obj.type.name == "MonoBehaviour":
                    data = obj.read()
                    type_tree = str(data.save_typetree()).lower()
                    if any(p.search(type_tree) for p in self.patterns):
                        return True
                elif obj.type.name == "MonoScript":
                    data = obj.read()
                    script_name = data.script_name.lower()
                    if any(p.search(script_name) for p in self.patterns):
                        return True
            except:
                pass

            # Method 3: Raw byte scanning
            try:
                raw_data = obj.get_raw_data()
                
                # Check UTF-8 strings
                str_data = raw_data.decode('utf-8', errors='ignore').lower()
                if any(p.search(str_data) for p in self.patterns):
                    return True
                
                # Check raw bytes
                raw_lower = raw_data.lower()
                if any(p in raw_lower for p in self.byte_patterns):
                    return True
            except:
                pass

            # Method 4: Aggressive mode checks
            if aggressive_mode:
                # Check level 0/1 objects
                level = getattr(obj, 'level', -1)
                if level in [0, 1]:
                    return True
                
                # Check hex representation
                try:
                    hex_data = binascii.hexlify(raw_data).decode('ascii')
                    for p in self.patterns:
                        hex_pattern = binascii.hexlify(p.pattern.encode('utf-8')).decode('ascii')
                        if hex_pattern in hex_data:
                            return True
                except:
                    pass

        except Exception as e:
            return False
        
        return False

def nuke_anticheats(file_path, anti_names, webhook_url, log_callback, aggressive_mode):
    log_callback("Loading Unity asset bundle...")
    env = UnityPy.load(file_path)
    anti_patterns = [name.strip() for name in anti_names.splitlines() if name.strip()]
    hunter = AntiCheatHunter(anti_patterns)
    
    total_removed = 0
    skipped = []
    found_patterns = {anti: 0 for anti in anti_patterns}
    found_patterns["[Level 0/1 Objects]"] = 0
    
    log_callback(f"Starting scan in {'AGGRESSIVE' if aggressive_mode else 'NORMAL'} mode...")
    
    # Create list of objects to process
    objects_to_process = list(env.objects)
    
    for obj in objects_to_process:
        try:
            if obj.type.name in ["MonoBehaviour", "MonoScript"]:
                removed = False
                
                # Check each pattern 1 by 1
                for anti in anti_patterns:
                    temp_hunter = AntiCheatHunter([anti])
                    if temp_hunter.scan(obj, aggressive_mode):
                        found_patterns[anti] += 1
                        removed = True
                        
                        if hasattr(env, 'remove_object'):
                            env.remove_object(obj.path_id)
                        else:
                            for asset in env.assets:
                                if obj.path_id in asset.objects:
                                    del asset.objects[obj.path_id]
                        
                        total_removed += 1
                        log_callback(f"Removed {obj.type.name} @ PathID {obj.path_id} (Matched: {anti})")
                        break
                
                # Special case for aggressive mode
                if not removed and aggressive_mode:
                    level = getattr(obj, 'level', -1)
                    if level in [0, 1]:
                        if hasattr(env, 'remove_object'):
                            env.remove_object(obj.path_id)
                        else:
                            for asset in env.assets:
                                if obj.path_id in asset.objects:
                                    del asset.objects[obj.path_id]
                        total_removed += 1
                        found_patterns["[Level 0/1 Objects]"] += 1
                        log_callback(f"Removed {obj.type.name} @ PathID {obj.path_id} (Level {level} object)")
        
        except Exception as e:
            skipped_msg = f"Skipped {obj.path_id}: {str(e)}"
            skipped.append(skipped_msg)
            log_callback(skipped_msg)

    output_path = file_path.replace(".unity3d", "_nuked.unity3d")
    with open(output_path, "wb") as f:
        f.write(env.file.save())

    # Enhanced reporting
    log_callback(f"\n=== FINAL REPORT ===")
    log_callback(f"Total objects scanned: {len(objects_to_process)}")
    log_callback(f"Total objects removed: {total_removed}")
    for pattern, count in found_patterns.items():
        if count > 0:
            log_callback(f"• {count} removed matching: {pattern}")

    # Webhook reporting
    if webhook_url:
        webhook_messages = []
        base_filename = os.path.basename(file_path)
        
        for pattern, count in found_patterns.items():
            if count > 0:
                webhook_messages.append(f"Found `{pattern}` in `{base_filename}` {count} **every single one has been removed Not sure why it says one**")
        
        summary = f"Total removed: {total_removed} objects\n" + "\n".join(webhook_messages)
        try:
            requests.post(webhook_url, json={"content": summary})
        except:
            log_callback("Failed to send webhook notification")

    log_file = f"nuker_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    with open(log_file, "w") as log:
        log.write(f"Anti-Cheat Nuker Log - {datetime.now()}\n")
        log.write(f"Input file: {file_path}\n")
        log.write(f"Mode: {'AGGRESSIVE' if aggressive_mode else 'NORMAL'}\n")
        log.write("\nDetection Report:\n")
        for pattern, count in found_patterns.items():
            if count > 0:
                log.write(f"{pattern}: {count} hits\n")
        log.write(f"\nTotal objects removed: {total_removed}\n\n")
        log.write("Skipped objects:\n")
        for s in skipped:
            log.write(s + "\n")

    return total_removed, output_path, log_file

class NukerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Unity Anti-Cheat Nuker - Made by Real_Nomii on discord")
        self.root.geometry("900x700")
        self.root.configure(bg=DARK_BG)
        self.file_path = ""
        
        # Configure styles
        self.root.option_add("*Font", "Consolas 10")
        self.root.option_add("*Background", DARK_BG)
        self.root.option_add("*Foreground", LIGHT_TEXT)
        self.root.option_add("*Button.Background", ACCENT_COLOR)
        self.root.option_add("*Button.Foreground", LIGHT_TEXT)
        self.root.option_add("*Text.Background", "#2d2d2d")
        self.root.option_add("*Entry.Background", "#2d2d2d")
        
        # Main container
        main_frame = Frame(root, bg=DARK_BG)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # File selection
        Label(main_frame, text="1. Select Unity .unity3d File", bg=DARK_BG, fg=LIGHT_TEXT).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.file_btn = Button(main_frame, text="Browse", command=self.pick_file)
        self.file_btn.grid(row=0, column=1, sticky="e", pady=(0, 5))
        
        # Anti-cheat patterns
        Label(main_frame, text="2. Anti-Cheat Patterns (one per line)", bg=DARK_BG, fg=LIGHT_TEXT).grid(row=1, column=0, sticky="w", pady=(5, 0))
        self.anti_box = Text(main_frame, height=10, width=85, bg="#2d2d2d", fg=LIGHT_TEXT, insertbackground=LIGHT_TEXT)
        self.anti_box.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        # Webhook
        Label(main_frame, text="3. Discord Webhook (optional)", bg=DARK_BG, fg=LIGHT_TEXT).grid(row=3, column=0, sticky="w", pady=(5, 0))
        self.webhook_entry = Entry(main_frame, width=85, bg="#2d2d2d", fg=LIGHT_TEXT, insertbackground=LIGHT_TEXT)
        self.webhook_entry.grid(row=4, column=0, columnspan=2, pady=(0, 10))
        
        # Aggressive mode checkbox
        self.aggressive_var = IntVar(value=1)
        self.aggressive_cb = Checkbutton(main_frame, text="Aggressive Mode (deep byte scanning)", 
                                        variable=self.aggressive_var, bg=DARK_BG, fg=LIGHT_TEXT, selectcolor="#2d2d2d")
        self.aggressive_cb.grid(row=5, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        # Nuke button
        self.nuke_btn = Button(main_frame, text="Remove anti cheats like a good boy", command=self.start_nuker_thread, bg=ACCENT_COLOR, font=("Consolas", 12, "bold"))
        self.nuke_btn.grid(row=6, column=0, columnspan=2, pady=(0, 10))
        
        # Log output
        Label(main_frame, text="Operation Log:", bg=DARK_BG, fg=LIGHT_TEXT).grid(row=7, column=0, sticky="w", pady=(5, 0))
        self.log_output = Text(main_frame, height=20, width=85, bg="#2d2d2d", fg=LIGHT_TEXT, insertbackground=LIGHT_TEXT)
        self.log_output.grid(row=8, column=0, columnspan=2)
        
        scrollbar = Scrollbar(main_frame, command=self.log_output.yview)
        scrollbar.grid(row=8, column=2, sticky="ns")
        self.log_output.config(yscrollcommand=scrollbar.set)
        
        # Add default patterns
        self.anti_box.insert(END, "MadebyRealnomiideleteme\n")

    def pick_file(self):
        path = filedialog.askopenfilename(filetypes=[("Unity Asset Bundle", "*.unity3d")])
        if path:
            self.file_path = path
            self.log(f"Selected file: {path}")

    def log(self, msg):
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        self.log_output.insert(END, f"{timestamp} {msg}\n")
        self.log_output.see(END)
        self.root.update()

    def start_nuker_thread(self):
        threading.Thread(target=self.run_nuker, daemon=True).start()

    def run_nuker(self):
        if not self.file_path:
            messagebox.showerror("Error", "No .unity3d file selected")
            return
        
        self.nuke_btn.config(state="disabled")
        self.log(" sending nudes...")
        
        try:
            anti_names = self.anti_box.get("1.0", END)
            webhook = self.webhook_entry.get().strip()
            aggressive_mode = bool(self.aggressive_var.get())
            
            total_removed, out_file, log_file = nuke_anticheats(
                self.file_path, 
                anti_names, 
                webhook, 
                self.log,
                aggressive_mode
            )
            
            self.log(f"Sending nudes complete. Removed {total_removed} anti-cheat objects.")
            self.log(f"Modified file saved to: {out_file}")
            self.log(f"Full report saved to: {log_file}")
            
            if total_removed > 0:
                self.log_output.tag_config("success", foreground=SUCCESS_COLOR)
                self.log_output.insert(END, "SUCCESS: Anti-cheat removed\n", "success")
            else:
                self.log_output.tag_config("warning", foreground="yellow")
                self.log_output.insert(END, "WARNING: No anti-cheat patterns matched\n", "warning")
                self.log("Try enabling Aggressive Mode, or tell nomi to add more scan options")
                
        except Exception as e:
            self.log_output.tag_config("error", foreground=ERROR_COLOR)
            self.log_output.insert(END, f"ERROR: {str(e)}\n", "error")
            self.log("Check the log file for details.")
        finally:
            self.nuke_btn.config(state="normal")

if __name__ == "__main__":
    root = Tk()
    gui = NukerGUI(root)
    root.mainloop()