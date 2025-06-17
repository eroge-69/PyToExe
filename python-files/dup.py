# dup.py
import tkinter
import customtkinter as ctk
import threading, queue, collections
import os, re, json, asyncio, aiohttp, hashlib
from tkinter import filedialog, messagebox
from thefuzz import process as fuzz_process

# --- CONFIGURATION ---
CONFIG = {
    "APP_NAME": "Luci's Flag Gui",
    "VERSION": "1.0"
}

# --- CONSTANTS AND LOGIC (Non-GUI) ---
ROBLOX_URLS = [
    ("https://raw.githubusercontent.com/MaximumADHD/Roblox-Client-Tracker/refs/heads/roblox/FVariables.txt", True), ("https://raw.githubusercontent.com/MaximumADHD/Roblox-FFlag-Tracker/refs/heads/main/AndroidApp.json", True), ("https://raw.githubusercontent.com/MaximumADHD/Roblox-FFlag-Tracker/refs/heads/main/MacClientBootstrapper.json", True), ("https://raw.githubusercontent.com/MaximumADHD/Roblox-FFlag-Tracker/refs/heads/main/MacDesktopClient.json", True), ("https://raw.githubusercontent.com/MaximumADHD/Roblox-FFlag-Tracker/refs/heads/main/MacStudioApp.json", True), ("https://raw.githubusercontent.com/MaximumADHD/Roblox-FFlag-Tracker/refs/heads/main/MacStudioBootstrapper.json", True), ("https://raw.githubusercontent.com/MaximumADHD/Roblox-FFlag-Tracker/refs/heads/main/PCClientBootstrapper.json", True), ("https://raw.githubusercontent.com/MaximumADHD/Roblox-FFlag-Tracker/refs/heads/main/PCDesktopClient.json", True), ("https://raw.githubusercontent.com/MaximumADHD/Roblox-FFlag-Tracker/refs/heads/main/PCStudioApp.json", True), ("https://raw.githubusercontent.com/MaximumADHD/Roblox-FFlag-Tracker/refs/heads/main/PCStudioBootstrapper.json", True), ("https://raw.githubusercontent.com/MaximumADHD/Roblox-FFlag-Tracker/refs/heads/main/PlayStationClient.json", True), ("https://raw.githubusercontent.com/MaximumADHD/Roblox-FFlag-Tracker/refs/heads/main/UWPApp.json", True), ("https://raw.githubusercontent.com/MaximumADHD/Roblox-FFlag-Tracker/refs/heads/main/XboxClient.json", True), ("https://raw.githubusercontent.com/MaximumADHD/Roblox-FFlag-Tracker/refs/heads/main/iOSApp.json", True),
    ("https://clientsettings.roblox.com/v2/settings/application/PCDesktopClient", False), ("https://raw.githubusercontent.com/BirdMakingStuff/rbx-scraper/refs/heads/main/fflags/CreatorDashboard.json", False), ("https://raw.githubusercontent.com/BirdMakingStuff/rbx-scraper/refs/heads/main/fflags/GoogleAndroidApp.json", False), ("https://raw.githubusercontent.com/BirdMakingStuff/rbx-scraper/refs/heads/main/fflags/PCDesktopClientCJV.json", False), ("https://raw.githubusercontent.com/BirdMakingStuff/rbx-scraper/refs/heads/main/fflags/PCStudioAppCJV.json", False), ("https://raw.githubusercontent.com/BirdMakingStuff/rbx-scraper/refs/heads/main/fflags/RCCBootstrapper.json", False), ("https://raw.githubusercontent.com/BirdMakingStuff/rbx-scraper/refs/heads/main/fflags/iOSAppCJV.json", False), ("https://raw.githubusercontent.com/SCR00M/froststap-shi/refs/heads/main/PCDesktopClient.json", False), ("https://raw.githubusercontent.com/SCR00M/froststap-shi/refs/heads/main/FVariablesV2.json", False)
]
FFLAG_CACHE_FILE = ".fflag_cache.json"

def parse_roblox_data(content, flags_data, is_priority):
    try:
        data = json.loads(content)
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)): parse_roblox_data(json.dumps(value), flags_data, is_priority)
                else:
                    if key not in flags_data: flags_data[key] = {"values": [], "priority_source": False}
                    if is_priority: flags_data[key]["priority_source"] = True; flags_data[key]["values"].insert(0, str(value))
                    else: flags_data[key]["values"].append(str(value))
    except (json.JSONDecodeError, AttributeError):
        for line in content.splitlines():
            if ":" in line:
                parts = line.strip().split(":", 1)
                key, value = parts[0].strip(), parts[1].strip()
                if key and not key.startswith("//"): # Simple check to avoid parsing comment lines
                    if key not in flags_data: flags_data[key] = {"values": [], "priority_source": False}
                    if is_priority: flags_data[key]["priority_source"] = True; flags_data[key]["values"].insert(0, str(value))
                    else: flags_data[key]["values"].append(str(value))

class BaseWorker(threading.Thread):
    def __init__(self, app_instance, start_button):
        super().__init__(); self.app = app_instance; self.start_button = start_button
    def run(self):
        try: self._run_logic()
        except Exception as e: self.app.update_status(f"CRITICAL ERROR: {type(e).__name__} - {e}", "red")
        finally: self.app.after(0, self.app._task_finished_callback, self.start_button)
    def _run_logic(self): raise NotImplementedError

class RobloxScraperWorker(BaseWorker):
    def __init__(self, app, settings, start_button): super().__init__(app, start_button); self.settings = settings
    def _run_logic(self):
        old_cache_state = dict(self.app.scraped_fflags_cache)
        self.app.update_status("Fetching sources concurrently...", "blue")
        results = asyncio.run(self.app.fetch_all(ROBLOX_URLS))
        if self.app.cancel_flag.is_set(): self.app.update_status("Scraping cancelled.", "orange"); return

        flags_data = {}; self.app.scraped_fflags_cache.clear()
        for content, is_priority, url, error in results:
            if error: self.app.log_message(f"WARN: Could not fetch {url}.\n", self.app.roblox_log)
            else: parse_roblox_data(content, flags_data, is_priority)

        filtered_flags = {f: d for f, d in flags_data.items() if not any(kw.lower() in f.lower() for kw in self.settings["filter_keywords"])}
        self.app.log_message(f"INFO: Found {len(flags_data)} total flags, {len(filtered_flags)} remain after filtering.\n", self.app.roblox_log)
        
        for flag, data in filtered_flags.items():
            if len(data["values"]) > 1:
                if self.settings["conflict_strategy"] == "Keep Priority Source" and data["priority_source"]:
                    final_value = data["values"][0] # The first item is from a priority source
                else:
                    final_value = collections.Counter(data["values"]).most_common(1)[0][0]
            else:
                final_value = data["values"][0] if data["values"] else ""
            self.app.scraped_fflags_cache[flag] = {"value": final_value}
        
        self.app.save_fflag_cache(); self.app.log_message("INFO: Local FFlag cache updated.\n", self.app.roblox_log)
        new_cache_state = self.app.scraped_fflags_cache
        
        if old_cache_state == new_cache_state:
            self.app.log_message("INFO: No changes detected in the flag database.\n", self.app.roblox_log)
        else:
            added = len(set(new_cache_state.keys()) - set(old_cache_state.keys()))
            removed = len(set(old_cache_state.keys()) - set(new_cache_state.keys()))
            self.app.log_message(f"INFO: Database changed. Added: +{added}, Removed: -{removed}\n", self.app.roblox_log)
        
        output_dict = {flag: data["value"] for flag, data in sorted(self.app.scraped_fflags_cache.items())}
        output_str = json.dumps(output_dict, indent=4)
        
        if self.settings["output_target"] == "Clipboard":
            self.app.after(0, lambda: (self.app.clipboard_clear(), self.app.clipboard_append(output_str)))
            self.app.log_message(f"SUCCESS: {len(output_dict)} flags copied to clipboard.\n", self.app.roblox_log)
        else:
            with open("mergedflags.txt", "w", encoding='utf-8') as f: f.write(output_str)
            self.app.log_message(f"SUCCESS: 'mergedflags.txt' written.\n", self.app.roblox_log)
        self.app.update_status("✨ Scraper Finished Successfully! ✨", "green")

class ValidatorWorker(BaseWorker):
    def _extract_best_flag_candidate(self, line):
        # This new, robust function finds the most likely flag name on a line.
        # It no longer relies on a strict prefix.
        
        # Remove common wrapping characters to isolate words
        clean_line = re.sub(r'["\',:]', ' ', line)
        candidates = clean_line.split()
        
        if not candidates:
            return None

        # A good flag name is usually long and contains mixed case or numbers
        def score(word):
            length = len(word)
            has_upper = any(c.isupper() for c in word)
            has_lower = any(c.islower() for c in word)
            has_digit = any(c.isdigit() for c in word)
            
            # The best flags are long and have mixed case/digits
            if length > 5 and has_upper and has_lower:
                return length * 1.5 + (2 if has_digit else 0)
            return length

        return max(candidates, key=score)

    def __init__(self, app, settings, start_button): super().__init__(app, start_button); self.settings = settings
    def _run_logic(self):
        self.app.update_status("Validating...", "blue"); self.app.after(0, self.app.clear_validator_outputs)
        lines = self.settings["input_text"].strip().split("\n")
        all_cached_flags = list(self.app.scraped_fflags_cache.keys())
        
        validation_results, unique_processed = [], set()
        for i, line in enumerate(lines):
            if self.app.cancel_flag.is_set(): break
            self.app.update_status(f"Processing line {i+1}/{len(lines)}...", "blue")
            
            flag_name_input = self._extract_best_flag_candidate(line)
            
            if not flag_name_input:
                if line.strip(): validation_results.append({"status": "invalid", "input_line": line})
                continue
            
            if flag_name_input in unique_processed: continue
            unique_processed.add(flag_name_input)
            
            input_val_match = re.search(r':\s*["\']?([^"\']+)["\']?', line)
            input_value = input_val_match.group(1).strip() if input_val_match else None

            # First, try an exact match (case-insensitive)
            exact_match = next((cf for cf in all_cached_flags if cf.lower() == flag_name_input.lower()), None)
            
            if exact_match:
                result = {"status": "valid", "input_line": line, "found_flag": exact_match, "input_value": input_value}
                validation_results.append(result)
            else: # If no exact match, try fuzzy
                best_match, score = fuzz_process.extractOne(flag_name_input, all_cached_flags)
                if score >= 85: # Fuzzy match threshold
                    result = {"status": "fuzzy", "input_line": line, "found_flag": best_match, "original_input": flag_name_input, "input_value": input_value}
                    validation_results.append(result)
                else:
                    validation_results.append({"status": "invalid", "input_line": line})
            if lines: self.app.update_progressbar((i+1)/len(lines))

        if self.app.cancel_flag.is_set(): self.app.update_status("Validation cancelled.", "orange"); return
        self.app.last_validation_results = validation_results
        self.app.after(0, self.app.rerender_validator_results)
        self.app.update_status("Validation complete.", "green")

class RemoverWorker(BaseWorker):
    def __init__(self, app, settings, start_button): super().__init__(app, start_button); self.settings = settings
    def _run_logic(self):
        self.app.update_status("Cleaning duplicates...", "blue"); self.app.after(0, lambda: (self.app.remover_output.configure(state="normal"), self.app.remover_output.delete("1.0", "end")))
        lines = self.settings["input_text"].strip().splitlines()
        
        kept_lines, fuzzy_duplicates_found, seen_hashes = [], [], set()
        for i, line in enumerate(lines):
            if not line.strip(): continue
            is_duplicate = False; normalized_line = re.sub(r'[^a-zA-Z0-9]', '', line).lower()
            if not normalized_line: continue
            
            line_hash = hashlib.sha256(normalized_line.encode()).hexdigest()
            if line_hash in seen_hashes and not self.settings["use_fuzzy"]: is_duplicate = True
            else:
                if self.settings["use_fuzzy"]:
                    for kept_line in kept_lines:
                        normalized_kept = re.sub(r'[^a-zA-Z0-9]', '', kept_line.strip().lower())
                        if fuzz_process.fuzz.ratio(normalized_line, normalized_kept) >= self.settings["sensitivity"]:
                            fuzzy_duplicates_found.append((kept_line, line)); is_duplicate = True; break
            if not is_duplicate: kept_lines.append(line); seen_hashes.add(line_hash)
            self.app.update_progressbar((i + 1) / len(lines) if lines else 1)
        
        final_lines = kept_lines
        if self.settings["use_fuzzy"] and fuzzy_duplicates_found:
            msg = "Fuzzy matching found these potential duplicates:\n\n" + "\n".join([f'"{d[0]}"  ≈  "{d[1]}"' for d in fuzzy_duplicates_found[:5]])
            if len(fuzzy_duplicates_found) > 5: msg += f"\n...and {len(fuzzy_duplicates_found)-5} more."
            msg += "\n\nDo you want to remove them?"
            if self.app.ask_yes_no("Fuzzy Duplicate Warning", msg): self.app.update_status(f"User approved removal.", "orange")
            else: self.app.update_status("User rejected fuzzy removals.", "orange"); final_lines = lines
        
        self.app.after(0, lambda: self.app.remover_output.insert("1.0", "\n".join(final_lines)))
        self.app.update_progressbar(1.0); self.app.update_status("Cleaning complete.", "green")
        self.app.after(0, lambda: self.app.remover_output.configure(state="disabled"))


class App(ctk.CTk):
    def __init__(self):
        super().__init__(); self.title(f"{CONFIG['APP_NAME']} v{CONFIG['VERSION']}"); self.geometry("850x700")
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(1, weight=1)
        ctk.set_appearance_mode("dark"); ctk.set_default_color_theme("blue")
        self.current_task = None; self.cancel_flag = threading.Event(); self.last_validation_results = []
        self.scraped_fflags_cache = {}; self.load_fflag_cache()

        self.header_frame = ctk.CTkFrame(self, corner_radius=0); self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10); self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_label = ctk.CTkLabel(self.header_frame, text=f"{CONFIG['APP_NAME']} v{CONFIG['VERSION']}", font=ctk.CTkFont(size=20, weight="bold")); self.header_label.grid(row=0, column=0, pady=10)
        self.theme_button = ctk.CTkButton(self.header_frame, text="☼", width=30, command=self.toggle_theme); self.theme_button.grid(row=0, column=1, padx=10)
        
        self.tab_view = ctk.CTkTabview(self, anchor="w"); self.tab_view.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.tab_view.add("FFlag Scraper"); self.tab_view.add("FFlag Validator"); self.tab_view.add("Duplicate Remover")
        self.setup_scraper_tab(); self.setup_validator_tab(); self.setup_remover_tab()

        self.status_frame = ctk.CTkFrame(self, height=40, corner_radius=0); self.status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5,10)); self.status_frame.grid_columnconfigure(0, weight=1)
        self.status_label = ctk.CTkLabel(self.status_frame, text="Status: Ready", anchor="w"); self.status_label.grid(row=0, column=0, padx=10, sticky="w")
        self.progressbar = ctk.CTkProgressBar(self.status_frame); self.progressbar.set(0); self.progressbar.grid(row=0, column=1, padx=10, sticky="ew")
        self.cancel_button = ctk.CTkButton(self.status_frame, text="Cancel", width=80, command=self.cancel_task, state="disabled"); self.cancel_button.grid(row=0, column=2, padx=10)

    def setup_scraper_tab(self):
        tab = self.tab_view.tab("FFlag Scraper"); tab.grid_columnconfigure(0, weight=1); tab.grid_rowconfigure(1, weight=1)
        settings_frame = ctk.CTkFrame(tab); settings_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew"); settings_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(settings_frame, text="This tool updates the local FFlag database used by the Validator.", wraplength=500, justify="left").grid(row=0, column=0, columnspan=2, padx=10, pady=(5,10))
        ctk.CTkLabel(settings_frame, text="Filter Keywords:").grid(row=1, column=0, padx=10, pady=5, sticky="n"); self.roblox_keywords_textbox = ctk.CTkTextbox(settings_frame, height=80); self.roblox_keywords_textbox.grid(row=1, column=1, padx=10, pady=5, sticky="ew"); self.roblox_keywords_textbox.insert("0.0", "UWP\nandroid\nxbox\nstudio\nPlaceFilter\ntoken\nfaststring\ndynamicstring\nIXP")
        ctk.CTkLabel(settings_frame, text="Conflict Strategy:").grid(row=2, column=0, padx=10, pady=5); self.conflict_strategy_var = ctk.StringVar(value="Keep Priority Source"); ctk.CTkOptionMenu(settings_frame, variable=self.conflict_strategy_var, values=["Keep Priority Source", "Keep Most Common Value"]).grid(row=2, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(settings_frame, text="Output To:").grid(row=3, column=0, padx=10, pady=5); self.output_target_var = ctk.StringVar(value="File (mergedflags.txt)"); ctk.CTkOptionMenu(settings_frame, variable=self.output_target_var, values=["File (mergedflags.txt)", "Clipboard"]).grid(row=3, column=1, padx=10, pady=5, sticky="w")
        self.roblox_start_button = ctk.CTkButton(tab, text="Update FFlag Database", command=self.start_roblox_scraping); self.roblox_start_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.roblox_log = ctk.CTkTextbox(tab, state="disabled", font=("Consolas", 12)); self.roblox_log.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    def setup_validator_tab(self):
        tab = self.tab_view.tab("FFlag Validator"); tab.grid_columnconfigure((0, 2), weight=1); tab.grid_rowconfigure(1, weight=1)
        top_frame = ctk.CTkFrame(tab, fg_color="transparent"); top_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=(10,0), sticky="ew")
        ctk.CTkLabel(top_frame, text="Input Flags", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        self.validator_details_var = tkinter.BooleanVar(value=False); self.validator_details_var.trace_add("write", self.rerender_validator_results); ctk.CTkCheckBox(top_frame, text="Show Details", variable=self.validator_details_var).pack(side="right")
        self.validator_input = ctk.CTkTextbox(tab, font=("Consolas", 12)); self.validator_input.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="nsew"); self.validator_input.insert("0.0", 'Paste flags here or use "Load from File..."')
        ctk.CTkLabel(tab, text="✔️ Valid / Corrected", text_color="#A5D6A7").grid(row=2, column=0, pady=(5,0)); ctk.CTkLabel(tab, text="❌ Invalid / Not Found", text_color="#EF9A9A").grid(row=2, column=2, pady=(5,0))
        self.validator_valid_output = ctk.CTkTextbox(tab, state="disabled", font=("Consolas", 12)); self.validator_valid_output.grid(row=3, column=0, padx=(10,5), pady=5, sticky="nsew")
        self.validator_invalid_output = ctk.CTkTextbox(tab, state="disabled", font=("Consolas", 12)); self.validator_invalid_output.grid(row=3, column=2, padx=(5,10), pady=5, sticky="nsew")
        tab.grid_rowconfigure(3, weight=1)
        action_frame = ctk.CTkFrame(tab); action_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="ew"); action_frame.grid_columnconfigure((0,1), weight=1)
        ctk.CTkButton(action_frame, text="Load from File...", command=self.load_flags_to_validator).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.validate_button = ctk.CTkButton(action_frame, text="Validate Flags Using Local Cache", command=self.start_validator); self.validate_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
    def setup_remover_tab(self):
        tab = self.tab_view.tab("Duplicate Remover"); tab.grid_columnconfigure((0, 2), weight=1); tab.grid_rowconfigure(0, weight=1)
        ctk.CTkLabel(tab, text="Input", font=ctk.CTkFont(size=14)).grid(row=1, column=0, pady=(5,0)); ctk.CTkLabel(tab, text="Output (Cleaned)", font=ctk.CTkFont(size=14)).grid(row=1, column=2, pady=(5,0))
        self.remover_input = ctk.CTkTextbox(tab, font=("Consolas", 12)); self.remover_input.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.remover_output = ctk.CTkTextbox(tab, state="disabled", font=("Consolas", 12)); self.remover_output.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(tab, text="▶", font=ctk.CTkFont(size=30)).grid(row=0, column=1, padx=5)
        settings_frame = ctk.CTkFrame(tab); settings_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew"); settings_frame.grid_columnconfigure(0, weight=1)
        fuzzy_frame = ctk.CTkFrame(settings_frame); fuzzy_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        self.remover_fuzzy = ctk.CTkCheckBox(fuzzy_frame, text="Enable Fuzzy Matching"); self.remover_fuzzy.grid(row=0, column=0, padx=(0,10))
        self.fuzzy_sensitivity_var = tkinter.IntVar(value=90); ctk.CTkLabel(fuzzy_frame, text="Sensitivity:").grid(row=0, column=1); ctk.CTkSlider(fuzzy_frame, from_=50, to=100, variable=self.fuzzy_sensitivity_var, number_of_steps=50).grid(row=0, column=2, sticky="ew", padx=5); ctk.CTkLabel(fuzzy_frame, textvariable=self.fuzzy_sensitivity_var).grid(row=0, column=3)
        self.remover_start_button = ctk.CTkButton(tab, text="Clean and Remove Duplicates", command=self.start_remover); self.remover_start_button.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

    def save_fflag_cache(self):
        try:
            with open(FFLAG_CACHE_FILE, "w", encoding='utf-8') as f: json.dump(self.scraped_fflags_cache, f, indent=4)
        except Exception as e: self.update_status(f"Error saving cache: {e}", "red")
    def load_fflag_cache(self):
        if os.path.exists(FFLAG_CACHE_FILE):
            try:
                with open(FFLAG_CACHE_FILE, "r", encoding='utf-8') as f: self.scraped_fflags_cache = json.load(f)
                self.after(100, lambda: self.update_status(f"Loaded {len(self.scraped_fflags_cache)} flags from cache.", "green"))
            except (json.JSONDecodeError, IOError): self.scraped_fflags_cache = {}; self.after(100, lambda: self.update_status("Cache corrupted. Run scraper.", "orange"))
        else: self.after(100, lambda: self.update_status("No cache found. Run scraper first.", "orange"))
    def toggle_theme(self): mode = ctk.get_appearance_mode(); new_mode = "Light" if mode == "Dark" else "Dark"; ctk.set_appearance_mode(new_mode); self.theme_button.configure(text="🌙" if new_mode == "Light" else "☼")
    def load_flags_to_validator(self):
        filepath = filedialog.askopenfilename(filetypes=(("Text/JSON", "*.txt;*.json"), ("All files", "*.*")))
        if filepath:
            with open(filepath, 'r', encoding='utf-8') as f: content = f.read()
            self.validator_input.delete("0.0", "end"); self.validator_input.insert("0.0", content)
    def ask_yes_no(self, title, message): response_queue = queue.Queue(); self.after(0, lambda: response_queue.put(messagebox.askyesno(title, message))); return response_queue.get()
    
    def start_task(self, worker_class, settings, start_button):
        if self.current_task and self.current_task.is_alive(): self.update_status("Task already running.", "orange"); return
        start_button.configure(state="disabled", text="Running...")
        self.cancel_button.configure(state="normal"); self.cancel_flag.clear(); self.progressbar.set(0)
        self.current_task = worker_class(self, settings, start_button); self.current_task.start()
    def cancel_task(self):
        if self.current_task and self.current_task.is_alive(): self.cancel_flag.set(); self.update_status("Cancellation signal sent...", "orange")
    def _task_finished_callback(self, start_button):
        button_map = { self.roblox_start_button: "Update FFlag Database", self.validate_button: "Validate Flags Using Local Cache", self.remover_start_button: "Clean and Remove Duplicates" }
        start_button.configure(text=button_map.get(start_button, "Start"), state="normal")
        self.cancel_button.configure(state="disabled"); self.progressbar.set(0); self.current_task = None
    
    def start_roblox_scraping(self):
        settings = {"filter_keywords": [k.strip() for k in self.roblox_keywords_textbox.get("1.0", "end-1c").splitlines() if k.strip()], "conflict_strategy": self.conflict_strategy_var.get(), "output_target": self.output_target_var.get()}
        self.start_task(RobloxScraperWorker, settings, self.roblox_start_button)
    def start_remover(self):
        settings = {"input_text": self.remover_input.get("1.0", "end-1c"), "use_fuzzy": self.remover_fuzzy.get(), "sensitivity": self.fuzzy_sensitivity_var.get()}
        self.start_task(RemoverWorker, settings, self.remover_start_button)
    def start_validator(self):
        if not self.scraped_fflags_cache: self.update_status("Cache empty. Run Scraper first.", "orange"); return
        settings = {"input_text": self.validator_input.get("1.0", "end-1c")}
        self.start_task(ValidatorWorker, settings, self.validate_button)
    
    async def fetch_all(self, urls):
        async with aiohttp.ClientSession() as session:
            tasks = [asyncio.ensure_future(self.fetch_one(session, url, is_priority)) for url, is_priority in urls]
            results, total_tasks = [], len(tasks)
            for i, task in enumerate(asyncio.as_completed(tasks)):
                if self.cancel_flag.is_set(): [t.cancel() for t in tasks if not t.done()]; break
                try: results.append(await task)
                except asyncio.CancelledError: pass
                if total_tasks > 0: self.update_progressbar((i + 1) / total_tasks * 0.5)
            return results
    async def fetch_one(self, session, url, is_priority):
        try:
            async with session.get(url, timeout=10) as response:
                response.raise_for_status(); content = await response.text(encoding='utf-8-sig'); return (content, is_priority, url, None)
        except Exception as e: return (None, is_priority, url, e)

    def rerender_validator_results(self, *args):
        if not hasattr(self, "last_validation_results") or not self.last_validation_results: return
        self.clear_validator_outputs()
        show_details = self.validator_details_var.get(); valid_text, invalid_text = [], []
        
        for res in self.last_validation_results:
            if res["status"] == "invalid": invalid_text.append(res["input_line"])
            else:
                cached_data = self.scraped_fflags_cache[res["found_flag"]]
                output_line = f'    "{res["found_flag"]}": "{cached_data["value"]}"'
                
                if show_details:
                    annotations = []
                    if res["status"] == "fuzzy": annotations.append(f'Matched "{res["original_input"]}"')
                    if res["input_value"] is not None and str(res["input_value"]) != str(cached_data["value"]):
                        annotations.append(f'Default is "{cached_data["value"]}"')
                    if annotations: output_line += f' // {"; ".join(annotations)}'
                valid_text.append(output_line)

        self.validator_valid_output.insert("1.0", "\n".join(sorted(valid_text)))
        self.validator_invalid_output.insert("1.0", "\n".join(sorted(invalid_text)))
        self.disable_validator_outputs()

    def update_status(self, text, color): self.status_label.after(0, lambda: self.status_label.configure(text=f"Status: {text}", text_color={"red":"#E57373", "green":"#81C784", "orange":"#FFB74D", "blue":"#64B5F6"}.get(color, "white")))
    def update_progressbar(self, value): self.progressbar.after(0, lambda: self.progressbar.set(value))
    def log_message(self, text, log_widget): self.after(0, lambda: (log_widget.configure(state="normal"), log_widget.insert("end", text), log_widget.configure(state="disabled"), log_widget.see("end")))
    def clear_validator_outputs(self):
        for w in [self.validator_valid_output, self.validator_invalid_output]: w.configure(state="normal"); w.delete("1.0", "end")
    def disable_validator_outputs(self):
        for w in [self.validator_valid_output, self.validator_invalid_output]: w.configure(state="disabled")

if __name__ == "__main__":
    app = App()
    app.mainloop()