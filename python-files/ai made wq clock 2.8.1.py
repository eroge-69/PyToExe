# wq_clock_litters.py
import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox, ttk
from datetime import datetime, timedelta
import time
import threading
import keyboard
import os
import shutil

# === SETTINGS ===
REAL_DAY_LENGTH_MINUTES = 65
GAME_HOURS_IN_DAY = 24
SKIP_HOURS = 8
UPDATE_INTERVAL_MS = 100
SEASONS = ["Spring", "Summer", "Autumn", "Winter"]
real_seconds_per_game_hour = (REAL_DAY_LENGTH_MINUTES * 60) / GAME_HOURS_IN_DAY
SEASON_MODES = {"no mate": 4, "mate and pups": 3}

# === WOLFQUEST COAT NAMES ===
WQ_COATS = [
    "Original Coat 1", "Original Coat 2", "Original Coat 3", "Original Coat 4", "Original Coat 5",
    "Lamar Coat 1", "Lamar Coat 2", "Lamar Coat 3", "Lamar Coat 4", "Lamar Coat 5",
    "BDP Coat 1", "BDP Coat 2", "BDP Coat 3", "BDP Coat 4", "BDP Coat 5",
    "Ambassador Coat 1", "Ambassador Coat 2", "Ambassador Coat 3", "Ambassador Coat 4", "Ambassador Coat 5",
    "Minnesota Brown 1", "Minnesota Brown 2", "Minnesota Brown 3", "Minnesota Brown 4", "Minnesota Brown 5",
    "Campfire Coat 1", "Campfire Coat 2", "Campfire Coat 3", "Campfire Coat 4", "Campfire Coat 5",
    "LifeisRough1 Coat 1", "LifeisRough1 Coat 2", "LifeisRough1 Coat 3", "LifeisRough1 Coat 4", "LifeisRough1 Coat 5",
    "LifeisRough2 Coat 1", "LifeisRough2 Coat 2", "LifeisRough2 Coat 3", "LifeisRough2 Coat 4", "LifeisRough2 Coat 5",
    "Classic Coat 1", "Classic Coat 2", "Classic Coat 3", "Classic Coat 4", "Classic Coat 5",
    "Eyebrows", "White Cheeks", "White Star", "Blackfire", "Chocosnout",
    "Bronze Forehead", "Buffy", "Shadow", "Frosty", "Stormy",
    "Founders Coat 1", "Founders Coat 2", "Founders Coat 3", "Founders Coat 4", "Founders Coat 5",
    "Hall of Fame Coat 1", "Hall of Fame Coat 2", "Hall of Fame Coat 3", "Hall of Fame Coat 4", "Hall of Fame Coat 5",
    "Cool Coat 1", "Cool Coat 2", "Cool Coat 3", "Cool Coat 4", "Cool Coat 5",
    "Beauteous Black 1", "Beauteous Black 2", "Beauteous Black 3", "Beauteous Black 4", "Beauteous Black 5",
    "Gorgeous Gray 1", "Gorgeous Gray 2", "Gorgeous Gray 3", "Gorgeous Gray 4", "Gorgeous Gray 5",
]

# Trait mapping -> file key names
TRAITS = [
    (("Cautious", "Bold"), "cautious_bold"),
    (("Loner", "Social"), "loner_social"),
    (("Lazy", "Energetic"), "lazy_energetic"),
]


class GameClock:
    def __init__(self, master):
        self.master = master
        self.master.title("ai made custom wolf quest widget")

        # State
        self.pups = {}  # pup_id -> pup_data dict
        self.pup_events = []  # flat chronological list (for compatibility)
        self.litters = []  # list of litters: {"id": n, "year":..., "day":..., "time": "...", "pups":[pup_id,...]}
        self.save_folder = None
        self.saved = False
        self.temp_folder = "temp_pup_data"
        os.makedirs(self.temp_folder, exist_ok=True)
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

        # --- Make main content scrollable ---
        outer = tk.Frame(master)
        outer.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(outer, highlightthickness=0)
        self.v_scroll = tk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.v_scroll.set)

        self.v_scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.content = tk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content, anchor="nw")

        self.content.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        # UI elements
        self.time_label = tk.Label(self.content, font=("Arial", 20))
        self.time_label.pack(pady=20)

        self.day_label = tk.Label(self.content, font=("Arial", 20))
        self.day_label.pack(pady=10)

        self.year_frame = tk.Frame(self.content)
        self.year_frame.pack(pady=5)
        self.year_label = tk.Label(self.year_frame, font=("Arial", 20), text="Year: 0")
        self.year_label.pack(side="left", padx=5)
        self.year_button = tk.Button(self.year_frame, text="+", font=("Arial", 16), command=self.increment_year)
        self.year_button.pack(side="left")

        self.log_pups_button = tk.Button(self.content, text="Log Pups", font=("Arial", 14), command=self.log_pups)
        self.log_pups_button.pack(pady=5)

        self.save_button = tk.Button(self.content, text="Save Loadout", font=("Arial", 14), command=self.save_loadout)
        self.save_button.pack(pady=5)
        self.load_button = tk.Button(self.content, text="Load Save", font=("Arial", 14), command=self.load_save)
        self.load_button.pack(pady=5)

        # Pup selection row (OptionMenu + Edit + Delete)
        selector_row = tk.Frame(self.content)
        selector_row.pack(pady=5, fill="x")
        self.selected_pup_var = tk.StringVar(value="Select Pup")
        self.pup_selector = tk.OptionMenu(selector_row, self.selected_pup_var, "Select Pup")
        self.pup_selector.pack(side="left", padx=(0, 10))
        self.edit_pup_button = tk.Button(selector_row, text="Edit Pup", font=("Arial", 12), command=self.open_edit_pup_dialog)
        self.edit_pup_button.pack(side="left")
        self.delete_pup_button = tk.Button(selector_row, text="Delete Pup", font=("Arial", 12), command=self.delete_selected_pup)
        self.delete_pup_button.pack(side="left", padx=(6, 0))

        self.pup_info_label = tk.Label(self.content, font=("Arial", 12), justify="left", anchor="w")
        self.pup_info_label.pack(fill="x", pady=10)

        # Sliders (created but not packed until a pup is selected)
        self.slider_frame = tk.Frame(self.content)
        self.slider_vars = {}
        self.slider_labels = {}
        for trait_tuple, _file_key in TRAITS:
            trait = trait_tuple
            tk.Label(self.slider_frame, text=f"{trait[0]}–{trait[1]}").pack()
            var = tk.IntVar(value=0)
            slider = tk.Scale(self.slider_frame, from_=-100, to=100, orient="horizontal", variable=var, showvalue=False,
                              command=lambda v, t=trait: self.update_trait_label(t))
            slider.pack(fill="x", padx=10)
            desc_label = tk.Label(self.slider_frame, text="")
            desc_label.pack()
            self.slider_vars[trait] = var
            self.slider_labels[trait] = desc_label

        self.save_changes_button = tk.Button(self.content, text="Save Changes to Pup (sliders)", command=self.save_changes_to_pup)

        self.pup_log_label = tk.Label(self.content, font=("Arial", 12), text="Pup Log:\n", justify="left", anchor="w")
        self.pup_log_label.pack(fill="x", pady=10)

        self.set_time_entry = tk.Entry(self.content, font=("Arial", 14))
        self.set_time_entry.pack(pady=5)
        self.set_time_entry.insert(0, "HH:MM")
        self.set_time_button = tk.Button(self.content, text="Set Time", command=self.set_time)
        self.set_time_button.pack(pady=5)

        self.season_var = tk.StringVar(value=SEASONS[0])
        self.season_menu = tk.OptionMenu(self.content, self.season_var, *SEASONS, command=self.set_season)
        self.season_menu.pack(pady=5)
        self.mode_var = tk.StringVar(value="no mate")
        self.mode_menu = tk.OptionMenu(self.content, self.mode_var, *SEASON_MODES.keys())
        self.mode_menu.pack(pady=5)

        self.version_button = tk.Button(self.content, text="Version Log", command=self.show_version_log)
        self.version_button.pack(pady=5)

        # Clock state
        self.game_time = datetime(2000, 1, 1, 0, 0)
        self.last_update = time.time()
        self.paused = True
        self.day_count = 0
        self.season_index = 0
        self.last_day_number = self.game_time.day
        self.year_count = 0
        self.key_states = {}
        self.unpause_key = None

        # initialize selector, start keyboard thread and clock
        self.update_pup_selector(reset=True)
        threading.Thread(target=self.check_key_press, daemon=True).start()
        self.update_clock()

    # --------------- Scroll helpers ----------------
    def _on_frame_configure(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

    def _on_mousewheel(self, event):
        delta = 0
        if hasattr(event, "delta") and event.delta:
            delta = -1 * (event.delta // 120)
        elif getattr(event, "num", None) == 5:
            delta = 1
        elif getattr(event, "num", None) == 4:
            delta = -1
        if delta:
            self.canvas.yview_scroll(delta, "units")

    # === Slider description updater ===
    def update_trait_label(self, trait):
        val = self.slider_vars[trait].get()
        neg_trait, pos_trait = trait
        desc = ""
        if val < 0:
            abs_val = abs(val)
            if 1 <= abs_val <= 25:
                desc = f"a little bit {neg_trait.lower()}"
            elif 26 <= abs_val <= 50:
                desc = f"decently {neg_trait.lower()}"
            elif 51 <= abs_val <= 75:
                desc = f"very {neg_trait.lower()}"
            elif 76 <= abs_val <= 90:
                desc = f"highly {neg_trait.lower()}"
            elif 91 <= abs_val <= 100:
                desc = neg_trait.lower()
        elif val > 0:
            if 1 <= val <= 25:
                desc = f"a little {pos_trait.lower()}"
            elif 26 <= val <= 50:
                desc = f"kinda {pos_trait.lower()}"
            elif 51 <= val <= 75:
                desc = f"very {pos_trait.lower()}"
            elif 76 <= val <= 90:
                desc = f"highly {pos_trait.lower()}"
            elif 91 <= val <= 100:
                desc = pos_trait.lower()
        else:
            desc = f"not {neg_trait.lower()} or {pos_trait.lower()}"
        self.slider_labels[trait].config(text=desc)

    # === Pup handling ===
    def update_pup_selector(self, reset=False):
        menu = self.pup_selector["menu"]
        menu.delete(0, "end")
        menu.add_command(label="Select Pup", command=lambda: self.selected_pup_var.set("Select Pup"))
        for pup_id, pup_data in list(self.pups.items()):
            menu.add_command(label=pup_data.get("name", pup_id), command=lambda pid=pup_id: self.show_pup_info(pid))
        if reset:
            self.selected_pup_var.set("Select Pup")
            self.pup_info_label.config(text="")
            self.hide_sliders_and_save_button()

    def show_pup_info(self, pup_id):
        pup = self.pups[pup_id]
        self.selected_pup_var.set(pup.get("name", "Unknown"))
        coat_desc = pup.get("coat", "Unknown")
        genes_desc = pup.get("coat_genes", "Unknown")
        self.pup_info_label.config(text=(
            f"Name: {pup.get('name', 'Unknown')}\n"
            f"Age: {pup.get('age', 0)}\n"
            f"Gender: {pup.get('gender', 'Unknown')}\n"
            f"Pup Weight: {pup.get('weight', 0)}\n"
            f"Year Born: {pup.get('year_born', self.year_count)}\n"
            f"Day Born: {pup.get('day_born', self.day_count)}\n"
            f"Coat genes: {genes_desc}\n"
            f"Coat: {coat_desc}"
        ))
        self.show_sliders_and_save_button()
        for trait_tuple, file_key in TRAITS:
            val = pup.get(file_key, 0)
            try:
                val = int(val)
            except Exception:
                val = 0
            self.slider_vars[trait_tuple].set(val)
            self.update_trait_label(trait_tuple)

    def show_sliders_and_save_button(self):
        if not self.slider_frame.winfo_ismapped():
            self.slider_frame.pack(pady=5, fill="x")
        if not self.save_changes_button.winfo_ismapped():
            self.save_changes_button.pack(pady=5)

    def hide_sliders_and_save_button(self):
        if self.slider_frame.winfo_ismapped():
            self.slider_frame.pack_forget()
        if self.save_changes_button.winfo_ismapped():
            self.save_changes_button.pack_forget()

    def log_pups(self):
        # Ask how many pups — this whole call becomes one litter
        num_pups = simpledialog.askinteger("Pup Log", "How many pups were born?", minvalue=1, maxvalue=12)
        if num_pups is None:
            return
        pup_popup = tk.Toplevel(self.master)
        pup_popup.title("Log Pups")
        pup_entries = []

        for i in range(num_pups):
            frame = tk.LabelFrame(pup_popup, text=f"Pup {i+1}", padx=10, pady=5)
            frame.pack(padx=10, pady=5, fill="x")
            # Name
            name_entry = tk.Entry(frame)
            tk.Label(frame, text="Name:").grid(row=0, column=0, sticky="w")
            name_entry.grid(row=0, column=1)
            # Gender
            gender_var = tk.StringVar(value="Male")
            tk.Label(frame, text="Gender:").grid(row=1, column=0, sticky="w")
            gender_frame = tk.Frame(frame)
            tk.Radiobutton(gender_frame, text="Male", variable=gender_var, value="Male").pack(side="left")
            tk.Radiobutton(gender_frame, text="Female", variable=gender_var, value="Female").pack(side="left")
            gender_frame.grid(row=1, column=1, sticky="w")
            # Weight
            tk.Label(frame, text="Weight:").grid(row=2, column=0, sticky="w")
            weight_entry = tk.Entry(frame)
            weight_entry.grid(row=2, column=1)
            # Coat genes
            tk.Label(frame, text="Coat genes:").grid(row=3, column=0, sticky="w")
            genes_var = tk.StringVar(value="KK")
            genes_frame = tk.Frame(frame)
            for g in ["KK", "Kk", "kk"]:
                tk.Radiobutton(genes_frame, text=g, variable=genes_var, value=g).pack(side="left")
            genes_frame.grid(row=3, column=1, sticky="w")
            # Coat dropdown
            tk.Label(frame, text="Coat:").grid(row=4, column=0, sticky="w")
            coat_var = tk.StringVar(value=WQ_COATS[0])
            coat_menu = ttk.Combobox(frame, textvariable=coat_var, values=WQ_COATS, state="readonly")
            coat_menu.grid(row=4, column=1)
            pup_entries.append((name_entry, gender_var, weight_entry, genes_var, coat_var))

        def save_pups_inner():
            litter_id = len(self.litters) + 1
            litter_pup_ids = []
            for name_entry, gender_var, weight_entry, genes_var, coat_var in pup_entries:
                name = name_entry.get().strip()
                if not name:
                    continue
                gender = gender_var.get()
                try:
                    weight = float(weight_entry.get().strip())
                except:
                    weight = 0.0
                genes = genes_var.get()
                coat = coat_var.get()
                pup_id = f"pup_{len(self.pups) + 1}"
                pup_data = {
                    "name": name,
                    "gender": gender,
                    "weight": weight,
                    "year_born": self.year_count,
                    "day_born": self.day_count,
                    "age": 0,
                    "coat_genes": genes,
                    "coat": coat,
                }
                # add default trait values
                for _, file_key in TRAITS:
                    pup_data[file_key] = 0
                # store pup
                self.pups[pup_id] = pup_data
                self.pup_events.append(pup_data)
                litter_pup_ids.append(pup_id)
                # write pup file to temp folder
                try:
                    with open(os.path.join(self.temp_folder, f"{pup_id}.txt"), "w") as f:
                        for k, v in pup_data.items():
                            f.write(f"{k}: {v}\n")
                except Exception:
                    pass

            # If at least one pup was added, create litter metadata and file
            if litter_pup_ids:
                litter = {
                    "id": litter_id,
                    "year": self.year_count,
                    "day": self.day_count,
                    "time": self.game_time.strftime("%H:%M:%S"),
                    "pups": litter_pup_ids
                }
                self.litters.append(litter)
                # Write litter file
                self._write_litter_file(litter)

            self.update_pup_selector()
            self.update_pup_log()
            pup_popup.destroy()

        tk.Button(pup_popup, text="Save", command=save_pups_inner).pack(pady=10)

    # Litter file helpers
    def _write_litter_file(self, litter, folder=None):
        folder = folder or self.temp_folder
        fname = os.path.join(folder, f"litter_{litter['id']}.txt")
        try:
            with open(fname, "w") as f:
                f.write(f"litter_id: {litter['id']}\n")
                f.write(f"year: {litter['year']}\n")
                f.write(f"day: {litter['day']}\n")
                f.write(f"time: {litter['time']}\n")
                for pid in litter["pups"]:
                    f.write(f"pup: {pid}\n")
        except Exception:
            pass

    def _remove_litter_file(self, litter_id, folder=None):
        folder = folder or self.temp_folder
        fname = os.path.join(folder, f"litter_{litter_id}.txt")
        try:
            if os.path.exists(fname):
                os.remove(fname)
        except Exception:
            pass

    def update_pup_log(self):
        if self.litters:
            parts = []
            for lit in self.litters:
                header = f"Litter {lit['id']} — Year {lit.get('year', '?')}, Day {lit.get('day','?')}, Time {lit.get('time','?')}"
                parts.append(header)
                for pid in lit.get("pups", []):
                    pup = self.pups.get(pid)
                    if pup:
                        parts.append(f"  {pup.get('name','?')} ({pup.get('gender','?')}, {pup.get('weight',0)}lb)")
                    else:
                        parts.append(f"  {pid} (missing data)")
                parts.append("")  # blank line between litters
            log_text = "Pup Log by Litter:\n" + "\n".join(parts)
        else:
            # fallback: flat list as before
            log_text = "Pup Log:\n" + "\n".join(
                f"{p['name']} ({p.get('gender','?')}, {p.get('weight',0)}lb)" for p in self.pup_events
            )
        self.pup_log_label.config(text=log_text)

    # === Save / Load ===
    def save_loadout(self):
        """
        Save behavior:
        - If a save folder is currently loaded (self.save_folder), ask whether to save into it.
        - Otherwise ask for a folder.
        """
        target_folder = None

        if self.save_folder and os.path.isdir(self.save_folder):
            try:
                use_current = messagebox.askyesno(
                    "Save to Current?",
                    f"A save folder is currently loaded:\n\n{self.save_folder}\n\n"
                    "Do you want to save into this currently-loaded folder?"
                )
            except Exception:
                use_current = False
            if use_current:
                target_folder = self.save_folder

        if not target_folder:
            folder_name = filedialog.asksaveasfilename(defaultextension="", filetypes=[("Folder", "*")])
            if not folder_name:
                return
            target_folder = folder_name

        try:
            os.makedirs(target_folder, exist_ok=True)
        except Exception:
            messagebox.showerror("Error", "Could not create or access the target folder.")
            return

        # copy temp files into target folder
        for file in os.listdir(self.temp_folder):
            try:
                shutil.copy(os.path.join(self.temp_folder, file), os.path.join(target_folder, file))
            except Exception:
                pass

        # Save clock state
        try:
            with open(os.path.join(target_folder, "clock_state.txt"), "w") as f:
                f.write(f"year_count: {self.year_count}\n")
                f.write(f"day_count: {self.day_count}\n")
                f.write(f"game_time: {self.game_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"season_index: {self.season_index}\n")
                f.write(f"paused: {int(self.paused)}\n")
        except Exception:
            messagebox.showwarning("Warning", "Saved pups but failed to write clock_state.txt (permission or disk issue).")

        # Ensure litter files are in target folder
        for lit in self.litters:
            try:
                self._write_litter_file(lit, folder=target_folder)
            except Exception:
                pass

        self.save_folder = target_folder
        self.saved = True
        messagebox.showinfo("Saved", f"Loadout saved successfully to:\n{self.save_folder}")

    def load_save(self):
        folder_name = filedialog.askdirectory(title="Select Save Folder")
        if not folder_name:
            return
        self.save_folder = folder_name
        self.pups.clear()
        self.pup_events.clear()
        self.litters.clear()
        missing_data = False

        # load pup files
        for file in os.listdir(folder_name):
            if file.startswith("pup_") and file.endswith(".txt"):
                try:
                    with open(os.path.join(folder_name, file), "r") as f:
                        data = {}
                        for line in f:
                            if ": " not in line:
                                continue
                            key, val = line.strip().split(": ", 1)
                            if key in ["age", "year_born", "day_born"]:
                                try:
                                    val = int(val)
                                except:
                                    val = 0
                            elif key == "weight":
                                try:
                                    val = float(val)
                                except:
                                    val = 0.0
                            else:
                                for _, file_key in TRAITS:
                                    if key == file_key:
                                        try:
                                            val = int(val)
                                        except:
                                            val = 0
                            data[key] = val
                        if "coat" not in data or "coat_genes" not in data:
                            missing_data = True
                        for _, file_key in TRAITS:
                            if file_key not in data:
                                missing_data = True
                                data[file_key] = 0
                        pup_id = file.replace(".txt", "")
                        self.pups[pup_id] = data
                        self.pup_events.append(data)
                except Exception:
                    continue

        # load litter files
        litter_files = [f for f in os.listdir(folder_name) if f.startswith("litter_") and f.endswith(".txt")]
        if litter_files:
            litter_files.sort()
            for lf in litter_files:
                try:
                    with open(os.path.join(folder_name, lf), "r") as f:
                        lit = {"id": None, "year": None, "day": None, "time": None, "pups": []}
                        for line in f:
                            if ": " not in line:
                                continue
                            key, val = line.strip().split(": ", 1)
                            if key == "litter_id":
                                try:
                                    lit["id"] = int(val)
                                except:
                                    lit["id"] = None
                            elif key == "year":
                                try:
                                    lit["year"] = int(val)
                                except:
                                    lit["year"] = None
                            elif key == "day":
                                try:
                                    lit["day"] = int(val)
                                except:
                                    lit["day"] = None
                            elif key == "time":
                                lit["time"] = val
                            elif key == "pup":
                                lit["pups"].append(val)
                        if lit["id"] is None:
                            lit["id"] = len(self.litters) + 1
                        self.litters.append(lit)
                except Exception:
                    continue
        else:
            # infer single litter of all pups if none present
            if self.pups:
                inferred = {
                    "id": 1,
                    "year": self.year_count,
                    "day": self.day_count,
                    "time": self.game_time.strftime("%H:%M:%S"),
                    "pups": list(self.pups.keys())
                }
                self.litters.append(inferred)
                try:
                    self._write_litter_file(inferred, folder=self.temp_folder)
                except Exception:
                    pass

        # Restore clock state if present
        clock_file = os.path.join(folder_name, "clock_state.txt")
        if os.path.exists(clock_file):
            try:
                with open(clock_file, "r") as f:
                    for line in f:
                        if ": " not in line:
                            continue
                        key, val = line.strip().split(": ", 1)
                        if key == "year_count":
                            try:
                                self.year_count = int(val)
                            except:
                                pass
                            self.year_label.config(text=f"Year: {self.year_count}")
                        elif key == "day_count":
                            try:
                                self.day_count = int(val)
                            except:
                                pass
                        elif key == "game_time":
                            parsed = None
                            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%H:%M"):
                                try:
                                    parsed = datetime.strptime(val, fmt)
                                    break
                                except Exception:
                                    parsed = None
                            if parsed is not None:
                                if parsed.year == 1900:
                                    self.game_time = self.game_time.replace(hour=parsed.hour, minute=parsed.minute, second=0)
                                else:
                                    self.game_time = parsed
                                self.last_day_number = self.game_time.day
                        elif key == "season_index":
                            try:
                                self.season_index = int(val) % len(SEASONS)
                            except:
                                self.season_index = 0
                            try:
                                self.season_var.set(SEASONS[self.season_index])
                            except Exception:
                                pass
                        elif key == "paused":
                            try:
                                self.paused = bool(int(val))
                            except:
                                pass
            except Exception:
                pass

        # Refresh UI
        self.update_pup_selector(reset=True)
        self.update_pup_log()
        try:
            self.time_label.config(text=self.game_time.strftime("%H:%M") + (" [PAUSED]" if self.paused else ""))
        except Exception:
            pass
        try:
            self.day_label.config(text=f"Day {self.day_count} - {SEASONS[self.season_index]}")
        except Exception:
            pass
        self.last_update = time.time()
        messagebox.showinfo("Loaded", "Save loaded successfully!")
        if missing_data:
            if messagebox.askyesno("Missing Data", "Some pup data is missing. Add now?"):
                self.log_pups()

    # === Save changes to currently selected pup (sliders) ===
    def save_changes_to_pup(self):
        selected_name = self.selected_pup_var.get()
        if not selected_name or selected_name == "Select Pup":
            messagebox.showwarning("No Pup Selected", "Please select a pup to save changes.")
            return
        pup_id = None
        for pid, pdata in self.pups.items():
            if pdata.get("name") == selected_name:
                pup_id = pid
                break
        if pup_id is None:
            messagebox.showerror("Not Found", "Selected pup not found in internal data.")
            return
        for trait_tuple, file_key in TRAITS:
            val = self.slider_vars[trait_tuple].get()
            self.pups[pup_id][file_key] = int(val)
        try:
            with open(os.path.join(self.temp_folder, f"{pup_id}.txt"), "w") as f:
                for k, v in self.pups[pup_id].items():
                    f.write(f"{k}: {v}\n")
        except Exception:
            pass
        if self.save_folder:
            try:
                shutil.copy(os.path.join(self.temp_folder, f"{pup_id}.txt"), os.path.join(self.save_folder, f"{pup_id}.txt"))
            except Exception:
                pass
        messagebox.showinfo("Saved", f"Changes saved for {selected_name}.")
        self.show_pup_info(pup_id)
        # rewrite litter files that include this pup
        for lit in self.litters:
            if pup_id in lit.get("pups", []):
                try:
                    self._write_litter_file(lit)
                except Exception:
                    pass
                if self.save_folder:
                    try:
                        self._write_litter_file(lit, folder=self.save_folder)
                    except Exception:
                        pass

    # === Edit pup attributes popup ===
    def open_edit_pup_dialog(self):
        selected_name = self.selected_pup_var.get()
        if not selected_name or selected_name == "Select Pup":
            messagebox.showwarning("No Pup Selected", "Please select a pup to edit.")
            return
        pup_id = None
        for pid, pdata in self.pups.items():
            if pdata.get("name") == selected_name:
                pup_id = pid
                break
        if pup_id is None:
            messagebox.showerror("Not Found", "Selected pup not found in internal data.")
            return

        pup = self.pups[pup_id]
        edit_popup = tk.Toplevel(self.master)
        edit_popup.title(f"Edit Pup: {pup.get('name','')}")
        edit_popup.transient(self.master)
        edit_popup.grab_set()

        tk.Label(edit_popup, text="Name:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        name_entry = tk.Entry(edit_popup)
        name_entry.grid(row=0, column=1, padx=6, pady=6)
        name_entry.insert(0, pup.get("name", ""))

        tk.Label(edit_popup, text="Gender:").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        gender_var = tk.StringVar(value=pup.get("gender", "Male"))
        gender_frame = tk.Frame(edit_popup)
        tk.Radiobutton(gender_frame, text="Male", variable=gender_var, value="Male").pack(side="left")
        tk.Radiobutton(gender_frame, text="Female", variable=gender_var, value="Female").pack(side="left")
        gender_frame.grid(row=1, column=1, sticky="w", padx=6, pady=6)

        tk.Label(edit_popup, text="Weight:").grid(row=2, column=0, sticky="w", padx=6, pady=6)
        weight_entry = tk.Entry(edit_popup)
        weight_entry.grid(row=2, column=1, padx=6, pady=6)
        weight_entry.insert(0, str(pup.get("weight", 0)))

        tk.Label(edit_popup, text="Coat genes:").grid(row=3, column=0, sticky="w", padx=6, pady=6)
        genes_var = tk.StringVar(value=pup.get("coat_genes", "KK"))
        genes_frame = tk.Frame(edit_popup)
        for g in ["KK", "Kk", "kk"]:
            tk.Radiobutton(genes_frame, text=g, variable=genes_var, value=g).pack(side="left")
        genes_frame.grid(row=3, column=1, sticky="w", padx=6, pady=6)

        tk.Label(edit_popup, text="Coat:").grid(row=4, column=0, sticky="w", padx=6, pady=6)
        coat_var = tk.StringVar(value=pup.get("coat", WQ_COATS[0]))
        coat_menu = ttk.Combobox(edit_popup, textvariable=coat_var, values=WQ_COATS, state="readonly")
        coat_menu.grid(row=4, column=1, padx=6, pady=6)

        tk.Label(edit_popup, text="Year Born:").grid(row=5, column=0, sticky="w", padx=6, pady=6)
        year_entry = tk.Entry(edit_popup)
        year_entry.grid(row=5, column=1, padx=6, pady=6)
        year_entry.insert(0, str(pup.get("year_born", self.year_count)))

        tk.Label(edit_popup, text="Day Born:").grid(row=6, column=0, sticky="w", padx=6, pady=6)
        day_entry = tk.Entry(edit_popup)
        day_entry.grid(row=6, column=1, padx=6, pady=6)
        day_entry.insert(0, str(pup.get("day_born", self.day_count)))

        def save_edits():
            new_name = name_entry.get().strip()
            if not new_name:
                messagebox.showwarning("Invalid", "Name cannot be blank.")
                return
            new_gender = gender_var.get()
            try:
                new_weight = float(weight_entry.get().strip())
            except:
                messagebox.showwarning("Invalid", "Weight must be a number.")
                return
            new_genes = genes_var.get()
            new_coat = coat_var.get()
            try:
                new_year = int(year_entry.get().strip())
            except:
                new_year = pup.get("year_born", self.year_count)
            try:
                new_day = int(day_entry.get().strip())
            except:
                new_day = pup.get("day_born", self.day_count)

            pup["name"] = new_name
            pup["gender"] = new_gender
            pup["weight"] = new_weight
            pup["coat_genes"] = new_genes
            pup["coat"] = new_coat
            pup["year_born"] = new_year
            pup["day_born"] = new_day

            try:
                with open(os.path.join(self.temp_folder, f"{pup_id}.txt"), "w") as f:
                    for k, v in pup.items():
                        f.write(f"{k}: {v}\n")
            except Exception:
                pass
            if self.save_folder:
                try:
                    shutil.copy(os.path.join(self.temp_folder, f"{pup_id}.txt"),
                                os.path.join(self.save_folder, f"{pup_id}.txt"))
                except Exception:
                    pass

            self.update_pup_selector(reset=False)
            self.update_pup_log()
            self.show_pup_info(pup_id)
            edit_popup.destroy()
            messagebox.showinfo("Saved", f"Pup '{new_name}' updated.")

        tk.Button(edit_popup, text="Save", command=save_edits).grid(row=7, column=0, columnspan=2, pady=10)

    def delete_selected_pup(self):
        selected_name = self.selected_pup_var.get()
        if not selected_name or selected_name == "Select Pup":
            messagebox.showwarning("No Pup Selected", "Please select a pup to delete.")
            return
        pup_id = None
        for pid, pdata in list(self.pups.items()):
            if pdata.get("name") == selected_name:
                pup_id = pid
                break
        if pup_id is None:
            messagebox.showerror("Not Found", "Selected pup not found in internal data.")
            return
        if not messagebox.askyesno("Confirm Delete", f"Delete pup '{selected_name}'?"):
            return
        # Remove files and data
        self.pups.pop(pup_id, None)
        self.pup_events = [p for p in self.pup_events if p.get("name") != selected_name]
        try:
            os.remove(os.path.join(self.temp_folder, f"{pup_id}.txt"))
        except Exception:
            pass
        if self.save_folder:
            try:
                os.remove(os.path.join(self.save_folder, f"{pup_id}.txt"))
            except Exception:
                pass
        # Remove from litters; delete litter if empty
        updated_litters = []
        for lit in self.litters:
            if pup_id in lit.get("pups", []):
                lit["pups"].remove(pup_id)
                if lit.get("pups"):
                    updated_litters.append(lit)
                    try:
                        self._write_litter_file(lit)
                    except Exception:
                        pass
                else:
                    try:
                        self._remove_litter_file(lit["id"])
                    except Exception:
                        pass
            else:
                updated_litters.append(lit)
        self.litters = updated_litters
        # update save_folder copies of litter files
        if self.save_folder:
            for lit in self.litters:
                try:
                    self._write_litter_file(lit, folder=self.save_folder)
                except Exception:
                    pass
        self.update_pup_selector(reset=True)
        self.update_pup_log()
        messagebox.showinfo("Deleted", f"Pup '{selected_name}' deleted.")

    # === Clock / Game Functions ===
    def increment_year(self):
        self.year_count += 1
        self.year_label.config(text=f"Year: {self.year_count}")

    def set_time(self):
        try:
            time_str = self.set_time_entry.get().strip()
            if time_str.isdigit() and len(time_str) == 4:
                time_str = time_str[:2] + ":" + time_str[2:]
            user_time = datetime.strptime(time_str, "%H:%M")
            self.game_time = self.game_time.replace(hour=user_time.hour, minute=user_time.minute, second=0)
            self.time_label.config(text=self.game_time.strftime("%H:%M") + (" [PAUSED]" if self.paused else ""))
        except ValueError:
            self.set_time_entry.delete(0, tk.END)
            self.set_time_entry.insert(0, "Invalid")

    def set_season(self, selected):
        if selected in SEASONS:
            self.season_index = SEASONS.index(selected)

    def skip_time(self):
        self.game_time += timedelta(hours=SKIP_HOURS)

    def toggle_pause(self):
        self.paused = not self.paused

    def check_key_press(self):
        pause_keys = ["esc", "tab", "m", "k", "f11", "j"]
        while True:
            if self._key_just_pressed("z"):
                self.skip_time()
            for key in pause_keys:
                if self._key_just_pressed(key):
                    if keyboard.is_pressed("alt"):
                        continue
                    if self.paused:
                        if self.unpause_key == key:
                            self.toggle_pause()
                            self.unpause_key = None
                        else:
                            self.unpause_key = key
                    else:
                        self.toggle_pause()
                        self.unpause_key = key
            time.sleep(0.05)

    def _key_just_pressed(self, key):
        pressed = keyboard.is_pressed(key)
        was_pressed = self.key_states.get(key, False)
        self.key_states[key] = pressed
        return pressed and not was_pressed

    def update_day_and_season(self):
        if self.game_time.day != self.last_day_number:
            self.day_count += 1
            self.last_day_number = self.game_time.day
            days_per_season = SEASON_MODES.get(self.mode_var.get(), 4)
            if (self.day_count) % days_per_season == 0:
                self.season_index = (self.season_index + 1) % len(SEASONS)
                self.season_var.set(SEASONS[self.season_index])

    def update_clock(self):
        now = time.time()
        elapsed_real_seconds = now - self.last_update
        self.last_update = now
        if not self.paused:
            game_seconds_advance = elapsed_real_seconds * (3600 / real_seconds_per_game_hour)
            self.game_time += timedelta(seconds=game_seconds_advance)
            self.update_day_and_season()
        try:
            self.time_label.config(text=self.game_time.strftime("%H:%M") + (" [PAUSED]" if self.paused else ""))
            self.day_label.config(text=f"Day {self.day_count} - {SEASONS[self.season_index]}")
        except Exception:
            pass
        self.master.after(UPDATE_INTERVAL_MS, self.update_clock)

    def show_version_log(self):
        version_info = (
            "Version 1: simple clock only\n"
            "Version 1.2: keyboard and pausing stuff added\n"
            "Version 2.0: pups, years, logging, saves etc. added\n"
            "Version 2.1: fixed bug with keyboard pause/unpause\n"
            "Version 2.2: scrollable UI + edit pup dialog added\n"
            "Version 2.5: bug fixes, wolf quest coats and genetics, editable attributes\n"
            "Version 2.8: pup litters added (each Log Pups call becomes a litter)"
        )
        messagebox.showinfo("Version Log", version_info)

    def on_close(self):
        if not self.saved:
            shutil.rmtree(self.temp_folder, ignore_errors=True)
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("360x700")
    clock = GameClock(root)
    root.mainloop()
