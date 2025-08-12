import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time
import pyautogui
import sys

# -----------------------
# Mini Interpreter (lange, expliciete structuur)
# -----------------------

class MiniInterpreterGUI:
    def __init__(self):
        # window
        self.root = tk.Tk()
        self.root.title("Mini-taal Interpreter")
        self.root.geometry("900x650")

        # toolbar (boven)
        self.toolbar = tk.Frame(self.root)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        self.load_button = tk.Button(self.toolbar, text="Load Script", command=self.load_script, width=12)
        self.load_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.save_schedule_button = tk.Button(self.toolbar, text="Save Schedule", command=self.save_schedules, width=12)
        self.save_schedule_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.load_schedule_button = tk.Button(self.toolbar, text="Load Schedule", command=self.load_schedules, width=12)
        self.load_schedule_button.pack(side=tk.LEFT, padx=5, pady=5)

        # output box (terminal-like)
        self.output_box = tk.Text(self.root, height=12, bg="black", fg="white")
        self.output_box.pack(fill=tk.X, padx=5, pady=(0,5))

        # input field
        self.input_field = tk.Entry(self.root, bg="gray15", fg="white", insertbackground="white")
        self.input_field.pack(fill=tk.X, padx=5)
        self.input_field.bind("<Return>", self.on_enter)

        # main frame: canvas left, schedule list right
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # canvas for graphics
        self.canvas_frame = tk.Frame(self.main_frame)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(self.canvas_frame, width=680, height=380, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # schedule list and controls
        self.schedule_frame = tk.Frame(self.main_frame, width=220)
        self.schedule_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(8,0))
        tk.Label(self.schedule_frame, text="Geplande taken").pack(anchor="nw")
        self.schedule_listbox = tk.Listbox(self.schedule_frame, width=34, height=18)
        self.schedule_listbox.pack(pady=5)
        self.remove_schedule_button = tk.Button(self.schedule_frame, text="Remove selected", command=self.remove_selected_schedule)
        self.remove_schedule_button.pack(fill=tk.X, padx=5, pady=2)
        self.clear_schedules_button = tk.Button(self.schedule_frame, text="Clear all", command=self.clear_schedules)
        self.clear_schedules_button.pack(fill=tk.X, padx=5, pady=2)

        # intern state
        self.current_image = None
        self.lock = threading.Lock()
        # scheduled_tasks: list of dicts {time: "HH:MM", command: "string", once: bool, triggered_today: bool}
        self.scheduled_tasks = []

        # try to load schedules on startup (optional)
        # self.load_schedules()

        # start schedule checker thread
        self.schedule_thread = threading.Thread(target=self._schedule_checker_loop, daemon=True)
        self.schedule_thread.start()

        # start input thread for terminal input fallback
        self.input_thread_obj = threading.Thread(target=self.input_thread, daemon=True)
        self.input_thread_obj.start()

        self.append_output("Mini-taal interpreter gestart. Typ commando's in het invoerveld of klik Load Script.")

    # -----------------------
    # Helpers: output, sanitize
    # -----------------------
    def append_output(self, text):
        self.output_box.insert(tk.END, text + "\n")
        self.output_box.see(tk.END)

    def sanitize_param(self, param):
        if param is None:
            return ""
        p = param.strip()
        # remove trailing pipes
        while p.endswith('|'):
            p = p[:-1].rstrip()
        # remove surrounding quotes if both present
        if (p.startswith('"') and p.endswith('"')) or (p.startswith("'") and p.endswith("'")):
            p = p[1:-1]
        return p.strip()

    # -----------------------
    # Load / Save scripts & schedules
    # -----------------------
    def load_script(self):
        file_path = filedialog.askopenfilename(title="Selecteer scriptbestand", filetypes=[("Tekstbestanden", "*.txt"), ("Alle bestanden", "*.*")])
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    self.append_output(f"> {line}")
                    res = self.interpret_line(line)
                    if res == 'quit':
                        break
        except Exception as e:
            self.append_output(f"[ERROR] Kon bestand niet laden: {e}")

    def save_schedules(self):
        # save to a file chosen by user
        if not self.scheduled_tasks:
            self.append_output("[INFO] Geen geplande taken om op te slaan.")
            return
        file_path = filedialog.asksaveasfilename(title="Save schedules", defaultextension=".txt", filetypes=[("Text files","*.txt")])
        if not file_path:
            return
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                for t in self.scheduled_tasks:
                    # store: HH:MM | command | ONCE/DAILY
                    once_flag = "ONCE" if t.get("once", False) else "DAILY"
                    f.write(f"{t['time']} | {t['command']} | {once_flag}\n")
            self.append_output(f"[INFO] Schedules saved to {file_path}")
        except Exception as e:
            self.append_output(f"[ERROR] Kon schedules niet opslaan: {e}")

    def load_schedules(self):
        file_path = filedialog.askopenfilename(title="Load schedules", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    # expect format: HH:MM | command | ONCE/DAILY
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 2:
                        time_str = parts[0]
                        cmd = parts[1]
                        once = False
                        if len(parts) >= 3 and parts[2].upper() == "ONCE":
                            once = True
                        self._add_schedule_internal(time_str, cmd, once)
            self.append_output(f"[INFO] Loaded schedules from {file_path}")
        except Exception as e:
            self.append_output(f"[ERROR] Kon schedules niet laden: {e}")

    # -----------------------
    # Schedule management
    # -----------------------
    def _add_schedule_internal(self, time_str, cmd, once=False):
        # validate time format HH:MM
        try:
            hh_mm = time_str.strip()
            time.strptime(hh_mm, "%H:%M")
        except:
            self.append_output(f"[SCHEDULE] Ongeldige tijd: {time_str} (gebruik HH:MM)")
            return False
        task = {"time": hh_mm, "command": cmd.strip(), "once": bool(once), "last_run_date": None}
        self.scheduled_tasks.append(task)
        self.update_schedule_listbox()
        self.append_output(f"[SCHEDULE] Added: {hh_mm} -> {cmd} {'(ONCE)' if once else '(DAILY)'}")
        return True

    def add_schedule(self, time_str, cmd, once=False):
        added = self._add_schedule_internal(time_str, cmd, once)
        return added

    def update_schedule_listbox(self):
        self.schedule_listbox.delete(0, tk.END)
        for idx, t in enumerate(self.scheduled_tasks):
            s = f"{t['time']} -> {t['command']} {'(ONCE)' if t.get('once') else '(DAILY)'}"
            self.schedule_listbox.insert(tk.END, s)

    def remove_selected_schedule(self):
        sel = self.schedule_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        try:
            task = self.scheduled_tasks.pop(idx)
            self.append_output(f"[SCHEDULE] Removed: {task['time']} -> {task['command']}")
            self.update_schedule_listbox()
        except Exception as e:
            self.append_output(f"[ERROR] Kon schedule niet verwijderen: {e}")

    def clear_schedules(self):
        self.scheduled_tasks.clear()
        self.update_schedule_listbox()
        self.append_output("[SCHEDULE] Alle taken verwijderd.")

    def _schedule_checker_loop(self):
        # check elke 20 seconden (of 1s) of er tasks zijn die moeten draaien
        while True:
            now = time.localtime()
            now_str = time.strftime("%H:%M", now)
            # iterate over a copy to allow removal
            for task in list(self.scheduled_tasks):
                t = task["time"]
                # check if time matches and we didn't run it today (except if once and not yet run)
                try:
                    should_run = False
                    # run once when time matches and last_run_date != today
                    today = time.strftime("%Y-%m-%d", now)
                    if t == now_str:
                        if task.get("last_run_date") != today:
                            should_run = True
                    if should_run:
                        self.append_output(f"[SCHEDULE] Executing scheduled: {t} -> {task['command']}")
                        # run the scheduled command in the GUI/main thread via after
                        self.root.after(0, lambda c=task['command']: self.interpret_line(c))
                        task["last_run_date"] = today
                        # if once: remove
                        if task.get("once"):
                            self.scheduled_tasks.remove(task)
                            self.update_schedule_listbox()
                except Exception as e:
                    self.append_output(f"[SCHEDULE ERROR] {e}")
            time.sleep(20)

    # -----------------------
    # Input threads (optional terminal fallback)
    # -----------------------
    def input_thread(self):
        # Keeps listening on stdin (useful if you run from terminal)
        while True:
            try:
                line = input("> ")
                if not line:
                    continue
                self.append_output(f"> {line}")
                res = self.interpret_line(line)
                if res == "quit":
                    break
            except EOFError:
                break
            except Exception as e:
                self.append_output(f"Fout input_thread: {e}")

    # -----------------------
    # Command interpreter (dispatch to execute_... functions)
    # -----------------------
    def on_enter(self, event=None):
        cmd = self.input_field.get()
        if not cmd:
            return
        self.append_output(f"> {cmd}")
        self.input_field.delete(0, tk.END)
        return self.interpret_line(cmd)

    def interpret_line(self, line):
        line = line.strip()
        if not line or line.startswith("#"):
            return
        if line.upper() == "QUIT":
            self.append_output("Interpreter stopt.")
            self.root.quit()
            return "quit"

        # dispatch by prefix
        # each command expects syntax like: COMMAND | params... |
        try:
            if line.startswith("SCREEN |"):
                param = line[len("SCREEN |"):].strip()
                return self.execute_screen(param)

            if line.startswith("KEYBOARD |"):
                param = line[len("KEYBOARD |"):].strip()
                return self.execute_keyboard(param)

            if line.startswith("MOUSE |"):
                param = line[len("MOUSE |"):].strip()
                return self.execute_mouse(param)

            if line.startswith("WAIT |"):
                param = line[len("WAIT |"):].strip()
                return self.execute_wait(param)

            if line.startswith("REPEAT |"):
                param = line[len("REPEAT |"):].strip()
                return self.execute_repeat(param)

            if line.startswith("FLASH |"):
                param = line[len("FLASH |"):].strip()
                return self.execute_flash(param)

            if line.startswith("DRAWRECT |"):
                param = line[len("DRAWRECT |"):].strip()
                return self.execute_drawrect(param)

            if line.startswith("CIRCLE |"):
                param = line[len("CIRCLE |"):].strip()
                return self.execute_circle(param)

            if line.startswith("CLEARCOLOR |"):
                param = line[len("CLEARCOLOR |"):].strip()
                return self.execute_clearcolor(param)

            if line.startswith("MOUSEWHEEL |"):
                param = line[len("MOUSEWHEEL |"):].strip()
                return self.execute_mousewheel(param)

            if line.startswith("SCHEDULE |"):
                param = line[len("SCHEDULE |"):].strip()
                return self.execute_schedule(param)

            # unknown
            self.append_output(f"Onbekend commando: {line}")
        except Exception as e:
            self.append_output(f"[ERROR] interpret_line: {e}")

    # -----------------------
    # execute_ functions (one-per-command)
    # -----------------------
    def execute_screen(self, param):
        p = self.sanitize_param(param)
        duration = None
        if "-->" in p:
            parts = p.split("-->")
            content = parts[0].strip()
            duration_str = parts[-1].strip()
            try:
                duration = int(duration_str)
            except:
                self.append_output("Fout: Ongeldige tijd bij SCREEN")
                return
        else:
            content = p
        content = self.sanitize_param(content)

        if content.lower() == "clear":
            self.clear_screen()
            return

        if content.lower() == "beep":
            try:
                import winsound
                winsound.Beep(1000, 500)
            except:
                print('\a')
            return

        if content.lower().startswith("color:"):
            color = content.split(":",1)[1].strip()
            self.change_bg_color(color)
            if duration:
                time.sleep(duration / 1000)
            return

        if duration is None:
            duration = 2000
        self.show_text(content, duration)

    def execute_keyboard(self, param):
        p = self.sanitize_param(param)
        if p.lower().startswith("type:"):
            txt = p[5:].lstrip()
            self.append_output(f"[KEYBOARD] typen: {txt}")
            try:
                pyautogui.write(txt)
            except Exception as e:
                self.append_output(f"[KEYBOARD ERROR] {e}")
        else:
            self.append_output(f"[KEYBOARD] onbekend commando: {p}")

    def execute_mouse(self, param):
        p = self.sanitize_param(param)
        if p.lower().startswith("click:"):
            btn = p[6:].strip()
            self.append_output(f"[MOUSE] klik: {btn}")
            try:
                pyautogui.click(button=btn)
            except Exception as e:
                self.append_output(f"[MOUSE ERROR] {e}")
            return

        if p.lower().startswith("move:"):
            coords = p[5:].split(",")
            if len(coords) == 2:
                try:
                    x = int(coords[0].strip())
                    y = int(coords[1].strip())
                    self.append_output(f"[MOUSE] move naar {x},{y}")
                    pyautogui.moveTo(x, y)
                except Exception as e:
                    self.append_output(f"[MOUSE ERROR] {e}")
            else:
                self.append_output("[MOUSE] ongeldig move commando")
            return

        self.append_output(f"[MOUSE] onbekend commando: {p}")

    def execute_wait(self, param):
        p = self.sanitize_param(param)
        try:
            ms = int(p)
            self.append_output(f"[WAIT] {ms} ms")
            time.sleep(ms / 1000)
        except:
            self.append_output("[WAIT] Ongeldige tijd opgegeven.")

    def execute_repeat(self, param):
        p = param.strip()
        if "|" not in p:
            self.append_output("[REPEAT] Gebruik: REPEAT | aantal | commando |")
            return
        parts = p.split("|",1)
        try:
            count = int(parts[0].strip())
        except:
            self.append_output("[REPEAT] Ongeldig aantal.")
            return
        command = parts[1].strip()
        for _ in range(count):
            self.interpret_line(command)

    def execute_flash(self, param):
        p = self.sanitize_param(param)
        # expected: "color, time"
        parts = [s.strip() for s in p.split(",",1)]
        if len(parts) != 2:
            self.append_output('[FLASH] Gebruik: FLASH | "kleur, tijd_ms" |')
            return
        color = parts[0]
        try:
            duration = int(parts[1])
        except:
            self.append_output("[FLASH] Ongeldige tijd opgegeven.")
            return
        self.append_output(f"[FLASH] Knipper met {color} voor {duration} ms")
        # run flash in separate thread to avoid blocking UI
        threading.Thread(target=lambda: self.flash(color, duration), daemon=True).start()

    def execute_drawrect(self, param):
        p = self.sanitize_param(param)
        parts = [s.strip() for s in p.split(",")]
        if len(parts) != 5:
            self.append_output("[DRAWRECT] Gebruik: DRAWRECT | x,y,width,height,color |")
            return
        try:
            x = int(parts[0]); y = int(parts[1]); w = int(parts[2]); h = int(parts[3]); color = parts[4]
        except:
            self.append_output("[DRAWRECT] Ongeldige parameters.")
            return
        self.append_output(f"[DRAWRECT] ({x},{y}) {w}x{h} {color}")
        self.draw_rect(x, y, w, h, color)

    def execute_circle(self, param):
        p = self.sanitize_param(param)
        parts = [s.strip() for s in p.split(",")]
        if len(parts) != 4:
            self.append_output("[CIRCLE] Gebruik: CIRCLE | x,y,radius,color |")
            return
        try:
            x = int(parts[0]); y = int(parts[1]); r = int(parts[2]); color = parts[3]
        except:
            self.append_output("[CIRCLE] Ongeldige parameters.")
            return
        self.append_output(f"[CIRCLE] ({x},{y}) r={r} {color}")
        self.draw_circle(x, y, r, color)

    def execute_clearcolor(self, param):
        color = self.sanitize_param(param)
        self.append_output(f"[CLEARCOLOR] Achtergrondkleur naar {color}")
        self.change_bg_color(color)

    def execute_mousewheel(self, param):
        p = self.sanitize_param(param)
        try:
            amt = int(p)
            self.append_output(f"[MOUSEWHEEL] Scroll {amt}")
            pyautogui.scroll(amt)
        except:
            self.append_output("[MOUSEWHEEL] Ongeldig aantal opgegeven.")

    def execute_schedule(self, param):
        # syntax: SCHEDULE | HH:MM | COMMAND... | [ONCE]
        p = self.sanitize_param(param)
        # check if ends with ONCE
        once = False
        if p.upper().endswith(" ONCE"):
            once = True
            p = p[:-5].rstrip()
        # split at first '|'
        if "|" not in p:
            self.append_output("[SCHEDULE] Gebruik: SCHEDULE | HH:MM | COMMAND | [ONCE]")
            return
        parts = p.split("|",1)
        time_str = parts[0].strip()
        cmd = parts[1].strip()
        added = self.add_schedule(time_str, cmd, once)
        if added:
            self.append_output(f"[SCHEDULE] Added: {time_str} -> {cmd} {'(ONCE)' if once else '(DAILY)'}")
        else:
            self.append_output("[SCHEDULE] Ongeldig tijd of commando.")

    # -----------------------
    # Canvas drawing small wrappers
    # -----------------------
    def show_text(self, text, duration_ms):
        with self.lock:
            self.canvas.delete("all")
            self.canvas.create_text(self.canvas.winfo_width()//2, self.canvas.winfo_height()//2, text=text, font=("Arial", 24), fill="black")
            self.root.update()
        time.sleep(duration_ms / 1000)
        with self.lock:
            self.canvas.delete("all")
            self.root.update()

    def change_bg_color(self, color):
        with self.lock:
            try:
                self.canvas.configure(bg=color)
                self.root.update()
            except tk.TclError:
                self.append_output(f"[ERROR] Ongeldige kleur: {color}")

    def flash(self, color, duration_ms):
        with self.lock:
            original = self.canvas['bg']
            end_time = time.time() + duration_ms / 1000
            while time.time() < end_time:
                try:
                    self.canvas.configure(bg=color)
                    self.root.update()
                except tk.TclError:
                    self.append_output(f"[ERROR] Ongeldige kleur: {color}")
                    break
                time.sleep(0.12)
                self.canvas.configure(bg=original)
                self.root.update()
                time.sleep(0.12)
            try:
                self.canvas.configure(bg=original)
                self.root.update()
            except:
                pass

    def draw_rect(self, x, y, w, h, color):
        with self.lock:
            try:
                self.canvas.create_rectangle(x, y, x+w, y+h, fill=color, outline="")
                self.root.update()
            except tk.TclError:
                self.append_output(f"[ERROR] Ongeldige kleur: {color}")

    def draw_circle(self, x, y, r, color):
        with self.lock:
            try:
                self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, outline="")
                self.root.update()
            except tk.TclError:
                self.append_output(f"[ERROR] Ongeldige kleur: {color}")

    # -----------------------
    # Schedule helpers public
    # -----------------------
    def add_schedule(self, time_str, cmd, once=False):
        return self._add_schedule_internal(time_str, cmd, once)

    # -----------------------
    # Utility: sanitize same as earlier
    # -----------------------
    def sanitize_param(self, param):
        return self._sanitize_param_static(param)

    @staticmethod
    def _sanitize_param_static(param):
        if param is None:
            return ""
        p = param.strip()
        while p.endswith("|"):
            p = p[:-1].rstrip()
        if (p.startswith('"') and p.endswith('"')) or (p.startswith("'") and p.endswith("'")):
            p = p[1:-1]
        return p.strip()

    # -----------------------
    # internal add schedule (used by execute_schedule and load)
    # -----------------------
    def _add_schedule_internal(self, time_str, cmd, once=False):
        try:
            # accept HH:MM format
            time.strptime(time_str, "%H:%M")
        except:
            return False
        task = {"time": time_str, "command": cmd, "once": bool(once), "last_run_date": None}
        self.scheduled_tasks.append(task)
        self.update_schedule_listbox()
        return True

    def update_schedule_listbox(self):
        self.schedule_listbox.delete(0, tk.END)
        for t in self.scheduled_tasks:
            label = f"{t['time']} -> {t['command']} {'(ONCE)' if t.get('once') else '(DAILY)'}"
            self.schedule_listbox.insert(tk.END, label)

    # -----------------------
    # Remove / Clear functions already above
    # -----------------------

    # -----------------------
    # Save / Load schedules implemented earlier (wrappers)
    # -----------------------

# -----------------------
# bootstrap + run
# -----------------------
def main():
    gui = MiniInterpreterGUI()
    gui.root.mainloop()

if __name__ == "__main__":
    main()
