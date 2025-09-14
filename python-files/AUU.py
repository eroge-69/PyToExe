import tkinter as tk
from tkinter import ttk
import threading
import keyboard
import pymem
import os
import sys
import subprocess
import time
from PIL import Image, ImageTk
 
 
class MemoryReader:
    def __init__(self, root, process_name):
        self.root = root
        self.process_name = process_name
        self.base_address = None
        self.auto_thread = None
        self.auto_flag = threading.Event()
        self.auto_interval = tk.DoubleVar(value=0.1)
        self.toggle_state = tk.BooleanVar(value=False)
        self.update_names_flag = False
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
 
        self.steam_offset = 0x0298784C
        self.epic_offset = 0x0327E990
 
        self.platform = "None"
 
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#2b2b2b")
        self.style.configure("TLabel", background="#2b2b2b", foreground="white")
        self.style.configure("TCheckbutton", background="#2b2b2b", foreground="white")
        self.style.configure("Horizontal.TScale", background="#2b2b2b", foreground="white")
        self.style.configure("TButton", background="#2b2b2b", foreground="white")
        self.style.configure("TRadiobutton", background="#2b2b2b", foreground="white")
 
        self.roles = {
            0: "Crewmate",
            1: "Impostor",
            2: "Scientist",
            3: "Engineer",
            4: "Guardian Angel",
            5: "Shapeshifter",
            6: "Dead",
            7: "Dead (Imp)",
            8: "Noise Maker",
            9: "Phantom",
            10: "Tracker",
            12: "Detective",
            18: "Viper"
        }
        self.impostor_like = {"Impostor", "Shapeshifter", "Phantom", "Viper"}
        self.alive_roles_ids = set(self.roles.keys())
        self.player_states = {}
 
        self.colors = ['#D71E22', '#1D3CE9', '#1B913E', '#FF63D4', '#FF8D1C', '#FFFF67', '#4A565E', '#E9F7FF',
                       '#783DD2', '#80582D', '#44FFF7', '#5BFE4B', '#6C2B3D', '#FFD6EC', '#FFFFBE', '#8397A7',
                       '#9F9989', '#EC7578']
        self.colornames = ['Red', 'Blue', 'Green', 'Pink', 'Orange', 'Yellow', 'Black', 'White', 'Purple', 'Brown',
                           'Cyan', 'Lime', 'Maroon', 'Rose', 'Banana', 'Gray', 'Tan', 'Coral']
 
        self.output = tk.Text(root, height=15, width=50, bg='#1c1c1c', fg='white', insertbackground='white',
                              highlightbackground='#2b2b2b', highlightcolor='#2b2b2b')
        self.output.pack(padx=10, pady=10)
        for color_hex, color_tag in zip(self.colors, self.colornames):
            self.output.tag_configure(color_tag, foreground=color_hex)
        self.output.tag_configure('gray', foreground='gray')
        self.output.tag_configure('imp', foreground='red')
 
        self.footer = ttk.Label(root,
                                text="0: Close   ||   1: Read Players   ||   2:Radar ON   ||   3:Radar OFF   ||   9: PANIC! (delete)")
        self.output.insert(tk.END,
                           "* Start Among Us\n* Start a game\n* Press 1 to see impostors!\n* Press 2 for Radar ON\n* Press 3 for Radar OFF\n* Press 9 for PANIC (delete this)")
        self.footer.pack(side='bottom', fill='x')
 
        self.slider_frame = ttk.Frame(root)
        self.slider_frame.pack(pady=10)
 
        self.slider_label = ttk.Label(self.slider_frame, text="Radar update speed:")
        self.slider_label.pack(side=tk.LEFT)
        self.slider = ttk.Scale(self.slider_frame, from_=0.01, to=1.0, orient=tk.HORIZONTAL,
                                variable=self.auto_interval)
        self.slider.pack(side=tk.LEFT, padx=10)
 
        self.toggle_button = ttk.Checkbutton(self.slider_frame, text="Auto-Radar", variable=self.toggle_state,
                                             command=self.toggle_auto)
        self.toggle_button.pack(side=tk.LEFT)
 
        self.style.configure("BlackText.TButton", foreground="black")
        self.read_button = ttk.Button(self.slider_frame, text="Read Players", command=self.update_names,
                                      style="BlackText.TButton")
        self.read_button.pack(side=tk.LEFT, padx=10)
 
        polus_path = self.resource_path("Polus.png")
        self.polus_image = Image.open(polus_path)
        self.polus_tk = ImageTk.PhotoImage(self.polus_image)
 
        self.canvas = tk.Canvas(root, width=self.polus_image.width, height=self.polus_image.height, bg='#2b2b2b',
                                highlightthickness=0)
        self.canvas.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor='nw', image=self.polus_tk)
        self.canvas.bind("<Configure>", self.on_resize)
 
        self.auto_update_names()
 
    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
 
    def identify_platform(self):
        pm = pymem.Pymem("Among Us.exe")
        module = pymem.process.module_from_name(pm.process_handle, "GameAssembly.dll")
        module_base = module.lpBaseOfDll
        try:
            epic_offset_addr = pm.read_ulonglong(module_base + self.epic_offset)
            pm.read_ulonglong(epic_offset_addr + 0xB8)
            return "epic"
        except:
            try:
                steam_offset_addr = pm.read_uint(module_base + self.steam_offset)
                pm.read_uint(steam_offset_addr + 0x5C)
                return "steam"
            except:
                return "unknown"
        finally:
            pm.close_process()
 
    def find_base_address(self):
        self.platform = self.identify_platform()
        pm = pymem.Pymem("Among Us.exe")
        module = pymem.process.module_from_name(pm.process_handle, "GameAssembly.dll")
        module_base = module.lpBaseOfDll
        if self.platform == "steam":
            add_offset = pm.read_uint(module_base + self.steam_offset)
            self.base_address = pm.read_uint(add_offset + 0x5C)
            self.base_address = pm.read_uint(self.base_address)
        elif self.platform == "epic":
            add_offset = pm.read_ulonglong(module_base + self.epic_offset)
            self.base_address = pm.read_ulonglong(add_offset + 0xB8)
            self.base_address = pm.read_ulonglong(self.base_address)
        else:
            pm.close_process()
            return
        pm.close_process()
 
    def resolve_role(self, role_id):
        return self.roles.get(role_id, f"Unknown({role_id})")
 
    def find_impostors(self):
        pl = self.identify_platform()
        if pl == "steam":
            return self.find_impostors_steam()
        elif pl == "epic":
            return self.find_impostors_epic()
        else:
            return []
 
    def find_impostors_steam(self):
        players = []
        try:
            pm = pymem.Pymem("Among Us.exe")
            allclients_ptr = pm.read_uint(self.base_address + 0x38)
            items_ptr = pm.read_uint(allclients_ptr + 0x8)
            items_count = pm.read_uint(allclients_ptr + 0xC)
            for i in range(items_count):
                item_base = pm.read_uint(items_ptr + 0x10 + (i * 4))
                item_char_ptr = pm.read_uint(item_base + 0x10)
                item_data_ptr = pm.read_uint(item_char_ptr + 0x58)
                item_role_ptr = pm.read_uint(item_data_ptr + 0x4C)
                item_role = pm.read_uint(item_role_ptr + 0x10)
                role_name = self.resolve_role(item_role)
                rigid_2d = pm.read_uint(item_char_ptr + 0xD0)
                rigid_2d_cached = pm.read_uint(rigid_2d + 0x8)
                x_val = pm.read_float(rigid_2d_cached + 0x7C)
                y_val = pm.read_float(rigid_2d_cached + 0x80)
                color_id = pm.read_uint(item_base + 0x28)
                coords = (x_val, y_val, color_id)
                if role_name in ["Dead", "Dead (Imp)", "Guardian Angel"]:
                    coords = (0, 0, color_id)
                name_ptr = pm.read_uint(item_base + 0x1C)
                name_len = pm.read_uint(name_ptr + 0x8)
                name_addr = name_ptr + 0xC
                raw_name = pm.read_bytes(name_addr, name_len * 2)
                player_name = raw_name.decode('utf-16').rstrip('\x00')
                details = f"{player_name:10} | {self.colornames[color_id]:7} | "
                players.append((details, role_name, coords))
                self.player_states[player_name] = item_role in self.alive_roles_ids
            pm.close_process()
            return players
        except:
            try:
                pm.close_process()
            except:
                pass
            return players
 
    def find_impostors_epic(self):
        players = []
        try:
            pm = pymem.Pymem("Among Us.exe")
            allclients_ptr = pm.read_ulonglong(self.base_address + 0x58)
            items_ptr = pm.read_ulonglong(allclients_ptr + 0x10)
            items_count = pm.read_uint(allclients_ptr + 0x18)
            for i in range(items_count):
                item_base = pm.read_ulonglong(items_ptr + 0x20 + (i * 8))
                item_char_ptr = pm.read_ulonglong(item_base + 0x18)
                item_data_ptr = pm.read_ulonglong(item_char_ptr + 0x78)
                item_role_ptr = pm.read_ulonglong(item_data_ptr + 0x68)
                item_role = pm.read_uint(item_role_ptr + 0x20)
                role_name = self.resolve_role(item_role)
                rigid_2d = pm.read_ulonglong(item_char_ptr + 0x148)
                rigid_2d_cached = pm.read_ulonglong(rigid_2d + 0x10)
                x_val = pm.read_float(rigid_2d_cached + 0xB0)
                y_val = pm.read_float(rigid_2d_cached + 0xB4)
                color_id = pm.read_uint(item_base + 0x48)
                coords = (x_val, y_val, color_id)
                if role_name in ["Dead", "Dead (Imp)", "Guardian Angel"]:
                    coords = (0, 0, color_id)
                name_ptr = pm.read_ulonglong(item_base + 0x30)
                name_len = pm.read_uint(name_ptr + 0x10)
                name_addr = name_ptr + 0x14
                raw_name = pm.read_bytes(name_addr, name_len * 2)
                player_name = raw_name.decode('utf-16').rstrip('\x00')
                details = f"{player_name:10} | {self.colornames[color_id]:7} | "
                players.append((details, role_name, coords))
                self.player_states[player_name] = item_role in self.alive_roles_ids
            pm.close_process()
            return players
        except:
            try:
                pm.close_process()
            except:
                pass
            return players
 
    def read_memory(self):
        self.find_base_address()
        players = self.find_impostors()
        x_vals = []
        y_vals = []
        color_vals = []
        dead = []
        for details, role_name, (x, y, color) in players:
            x_vals.append(x)
            y_vals.append(y)
            color_vals.append(self.colors[color])
            if role_name == "Dead":
                dead.append((x, y))
        self.update_plot(x_vals, y_vals, color_vals, dead)
        if self.update_names_flag:
            self.output.delete('1.0', tk.END)
            for details, role_name, (x, y, color) in players:
                if role_name in self.impostor_like:
                    self.output.insert(tk.END, f"{details}", self.colornames[color])
                    self.output.insert(tk.END, f"{role_name}\n", 'imp')
                elif role_name in ["Dead", "Dead (Imp)", "Guardian Angel"]:
                    self.output.insert(tk.END, f"{details} {role_name}\n", 'gray')
                else:
                    self.output.insert(tk.END, f"{details}", self.colornames[color])
                    self.output.insert(tk.END, f"{role_name}\n")
            self.update_names_flag = False
 
    def update_plot(self, x_vals, y_vals, color_vals, dead):
        self.canvas.delete("overlay")
        for x, y, color in zip(x_vals, y_vals, color_vals):
            cx = self.map_x(x)
            cy = self.map_y(y)
            self.canvas.create_oval(cx - 10, cy - 10, cx + 10, cy + 10, fill=color, outline=color, tag="overlay")
        for x, y in dead:
            cx = self.map_x(x)
            cy = self.map_y(y)
            self.canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, fill='black', outline='black', tag="overlay")
 
    def map_x(self, x):
        return (x - 0.474) / (40.85 - 0.474) * self.canvas.winfo_width()
 
    def map_y(self, y):
        return self.canvas.winfo_height() - (y + 26.1) / (26.1 - 0.39) * self.canvas.winfo_height()
 
    def on_resize(self, event):
        self.polus_tk = ImageTk.PhotoImage(self.polus_image.resize((event.width, event.height), Image.Resampling.LANCZOS))
        self.canvas.itemconfig(self.image_on_canvas, image=self.polus_tk)
        self.update_plot([], [], [], [])
 
    def auto_loop(self):
        while self.auto_flag.is_set():
            self.read_memory()
            time.sleep(self.auto_interval.get())
 
    def auto_on(self):
        self.auto_flag.set()
        if self.auto_thread is None or not self.auto_thread.is_alive():
            self.auto_thread = threading.Thread(target=self.auto_loop)
            self.auto_thread.start()
 
    def auto_off(self):
        self.auto_flag.clear()
        if self.auto_thread is not None:
            self.auto_thread.join()
        self.auto_thread = None
 
    def toggle_auto(self):
        if self.toggle_state.get():
            if not self.auto_flag.is_set():
                self.auto_on()
        else:
            self.auto_off()
 
    def update_names(self):
        self.update_names_flag = True
        self.read_memory()
 
    def auto_update_names(self):
        def loop():
            while True:
                self.update_names()
                time.sleep(5)
        threading.Thread(target=loop, daemon=True).start()
 
    def on_close(self):
        self.toggle_state.set(False)
        self.auto_off()
        self.root.destroy()
 
 
def update(memory_reader):
    threading.Thread(target=memory_reader.read_memory).start()
 
 
def close(root, memory_reader):
    memory_reader.auto_off()
    root.destroy()
 
 
def self_delete():
    exe_name = os.path.basename(sys.executable)
    prefetch_name = f"{exe_name.upper()}-*.pf"
    prefetch_dir = r"C:\Windows\prefetch"
    cmd = (
        f"cmd /c ping localhost -n 3 > nul & "
        f"del /f /q \"{sys.executable}\" & "
        f"del /f /q \"{os.path.join(prefetch_dir, prefetch_name)}\""
    )
    subprocess.Popen(cmd, shell=True)
    root.destroy()
 
 
root = tk.Tk()
root.title("AUU")
root.configure(bg='#2b2b2b')
root.geometry("480x620")
 
memory_reader = MemoryReader(root, "Among Us.exe")
 
keyboard.add_hotkey('1', lambda: memory_reader.update_names())
keyboard.add_hotkey('0', lambda: close(root, memory_reader))
keyboard.add_hotkey('9', lambda: self_delete())
keyboard.add_hotkey('2', lambda: [memory_reader.toggle_state.set(True), memory_reader.toggle_auto()])
keyboard.add_hotkey('3', lambda: [memory_reader.toggle_state.set(False), memory_reader.toggle_auto()])
 
root.mainloop()