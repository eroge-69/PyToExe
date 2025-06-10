import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import ttkbootstrap as tb
import subprocess
import threading
import queue
import os
import sys
import time
import psutil
from mcstatus import JavaServer
import pystray
from PIL import Image, ImageDraw, ImageTk
import datetime
import json
import requests
from playsound import playsound

CONFIG_PATH = "local_server_panel_config.json"
LOG_DIR = "logs"
HEAD_CACHE = "head_cache"

def ensure_dirs():
    for d in [LOG_DIR, HEAD_CACHE]:
        if not os.path.exists(d):
            os.makedirs(d)

def save_config(data):
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f)

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}

def make_tray_icon():
    size = (64, 64)
    image = Image.new("RGB", size, "black")
    draw = ImageDraw.Draw(image)
    draw.rectangle((8, 8, 56, 56), fill="#46a832")
    return image

def play_notification_sound(event="start"):
    try:
        if event == "start":
            playsound('start.wav', block=False)
        elif event == "stop":
            playsound('stop.wav', block=False)
        elif event == "restart":
            playsound('restart.wav', block=False)
    except Exception:
        pass

def fetch_player_head(username, size=32):
    """Download or load from cache a player's head image."""
    path = os.path.join(HEAD_CACHE, f"{username}.png")
    if not os.path.exists(path):
        try:
            url = f"https://mc-heads.net/avatar/{username}/{size}.png"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                with open(path, "wb") as f:
                    f.write(resp.content)
        except Exception:
            pass
    try:
        img = Image.open(path).resize((size, size), Image.NEAREST)
        return ImageTk.PhotoImage(img)
    except Exception:
        blank = Image.new("RGBA", (size, size), (100, 100, 100, 255))
        return ImageTk.PhotoImage(blank)

class LocalServerPanel(tb.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("Local Server Panel")
        self.geometry("1200x700")
        self.server_process = None
        self.output_queue = queue.Queue()
        self.log_file = None
        self.session_log_path = None
        self.ps_proc = None
        self.crashed = False
        self.tray_icon = None
        self.tray_thread = None
        self.tray_active = False
        self.restart_pending = False

        config = load_config()
        self.selected_jar = config.get("selected_jar")
        self.ram = config.get("ram")
        self.server_port = config.get("server_port", 25565)

        self.auto_scroll = tk.BooleanVar(value=True)
        ensure_dirs()
        self._create_sidebar()
        self._create_status_panel()
        self._create_console()
        self._create_right_panel()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.after(100, self.update_console)
        self.after(2000, self.update_status_info)
        self.after(3000, self.update_player_list_panel)
        self._update_start_btn_state()
        self.jar_lbl.config(text=os.path.basename(self.selected_jar) if self.selected_jar else "No server.jar selected")
        self.ram_lbl.config(text=f"RAM: {self.ram} MB" if self.ram else "RAM: Not set")

    def _create_sidebar(self):
        self.sidebar = tb.Frame(self, bootstyle="dark")
        self.sidebar.pack(side="left", fill="y", padx=(0,10), pady=10)

        self.config_btn = tb.Button(
            self.sidebar, text="⚙ Configuration", width=18, bootstyle="secondary", command=self.open_config)
        self.config_btn.pack(pady=(20,15))

        self.start_btn = tb.Button(
            self.sidebar, text="Start", width=15, bootstyle="success", command=self.start_server, state="disabled")
        self.start_btn.pack(pady=(5,10))

        self.restart_btn = tb.Button(
            self.sidebar, text="Restart", width=15, bootstyle="info", command=self.restart_server, state="disabled")
        self.restart_btn.pack(pady=(5,10))

        self.stop_btn = tb.Button(
            self.sidebar, text="Stop", width=15, bootstyle="danger", command=self.stop_server, state="disabled")
        self.stop_btn.pack()

        self.jar_lbl = tb.Label(self.sidebar, text="No server.jar selected", wraplength=150)
        self.jar_lbl.pack(pady=(60,0))

        self.ram_lbl = tb.Label(self.sidebar, text="RAM: Not set", wraplength=150)
        self.ram_lbl.pack(pady=(5,0))

        self.tray_btn = tb.Button(
            self.sidebar, text="Minimize to Tray", width=18, bootstyle="secondary", command=self.minimize_to_tray)
        self.tray_btn.pack(pady=(30,0))

    def _create_status_panel(self):
        self.status_panel = tb.Frame(self, bootstyle="dark")
        self.status_panel.pack(side="top", fill="x", padx=(0,0), pady=(5,0))

        self.statusdot = tb.Label(self.status_panel, text="●", font=("Segoe UI", 16, "bold"), foreground="#444")
        self.statusdot.grid(row=0, column=0, padx=(18,5), pady=8)
        self.status_title = tb.Label(self.status_panel, text="Server Status:", font=("Segoe UI", 12, "bold"))
        self.status_title.grid(row=0, column=1, sticky="w", pady=8)

        self.status_info = tb.Label(self.status_panel, text="Stopped", font=("Segoe UI", 11))
        self.status_info.grid(row=0, column=2, sticky="w", padx=(12,0), pady=8)

        self.ram_status = tb.Label(self.status_panel, text="RAM: -", font=("Segoe UI", 11))
        self.ram_status.grid(row=0, column=3, sticky="w", padx=(20,0), pady=8)
        self.cpu_status = tb.Label(self.status_panel, text="CPU: -", font=("Segoe UI", 11))
        self.cpu_status.grid(row=0, column=4, sticky="w", padx=(15,0), pady=8)
        self.player_status = tb.Label(self.status_panel, text="Players: -", font=("Segoe UI", 11))
        self.player_status.grid(row=0, column=5, sticky="w", padx=(15,0), pady=8)

    def _create_console(self):
        self.main_pane = tk.PanedWindow(self, orient="vertical", sashwidth=4, bg="#333")
        self.main_pane.pack(side="left", fill="both", expand=True, padx=0, pady=10)

        self.console_frame = tb.Frame(self.main_pane)
        self.console = tk.Text(
            self.console_frame, wrap="word", state="disabled", height=25, bg="#222",
            fg="#ccc", insertbackground="#fff")
        self.console.pack(fill="both", expand=True, padx=5, pady=(0,5))
        console_scroll = tk.Scrollbar(self.console_frame, command=self.console.yview)
        self.console['yscrollcommand'] = console_scroll.set
        console_scroll.pack(side="right", fill="y")
        self.main_pane.add(self.console_frame, stretch="always")

        controls_frame = tb.Frame(self.console_frame)
        controls_frame.pack(fill="x", pady=(0,5))

        self.clear_btn = tb.Button(
            controls_frame, text="Clear Console", bootstyle="warning", command=self.clear_console)
        self.clear_btn.pack(side="left", padx=(0,10))
        self.autoscroll_chk = tb.Checkbutton(
            controls_frame, text="Auto-scroll", variable=self.auto_scroll, bootstyle="info")
        self.autoscroll_chk.pack(side="left")

        self.entry_frame = tb.Frame(self.main_pane)
        self.command_entry = tb.Entry(self.entry_frame)
        self.command_entry.pack(side="left", fill="x", expand=True, padx=(0,5))
        self.command_entry.bind("<Return>", self.send_command)
        send_btn = tb.Button(self.entry_frame, text="Send", command=self.send_command)
        send_btn.pack(side="right")
        self.main_pane.add(self.entry_frame, minsize=40)

    def _create_right_panel(self):
        self.right_panel = tb.Frame(self)
        self.right_panel.pack(side="right", fill="y", padx=(0,8), pady=10)
        # Player list title
        tb.Label(self.right_panel, text="Players", font=("Segoe UI", 14, "bold")).pack(pady=(8,4))
        self.player_canvas = tk.Canvas(self.right_panel, width=250, height=600, bg="#232323", bd=0, highlightthickness=0)
        self.player_canvas.pack(side="top", fill="y", expand=True)
        self._player_head_cache = {}

    def update_player_list_panel(self):
        self.player_canvas.delete("all")
        try:
            server = JavaServer.lookup(f"localhost:{self.server_port}")
            status = server.status()
            players = status.players.sample if hasattr(status.players, "sample") and status.players.sample else []
            if not players and status.players.online > 0:
                self.player_canvas.create_text(120, 40, text="Player list unavailable.", fill="#ccc", font=("Segoe UI", 10))
                return
            y = 15
            self._player_head_cache.clear()
            for p in players:
                head_img = fetch_player_head(p.name, size=32)
                self._player_head_cache[p.name] = head_img
                self.player_canvas.create_image(20, y, image=head_img, anchor="nw")
                self.player_canvas.create_text(68, y+16, text=p.name, anchor="w", fill="#fff", font=("Segoe UI", 12, "bold"))
                y += 42
            if not players:
                self.player_canvas.create_text(120, 40, text="No players online.", fill="#aaa", font=("Segoe UI", 10))
        except Exception as ex:
            self.player_canvas.create_text(120, 40, text="Server offline or unreachable.", fill="#f33", font=("Segoe UI", 10))
        self.after(5000, self.update_player_list_panel)

    def set_status_dot(self, status="stopped"):
        if status == "running":
            def pulse():
                color1, color2 = "#31d17a", "#42ea97"
                now = int(time.time() * 2) % 2
                c = color1 if now == 0 else color2
                self.statusdot.config(foreground=c)
                if self.server_process:
                    self.statusdot.after(400, pulse)
                else:
                    self.statusdot.config(foreground="#444")
            pulse()
        elif status == "crashed":
            self.statusdot.config(foreground="#d13c3c")
        else:
            self.statusdot.config(foreground="#444")

    def _update_start_btn_state(self):
        if self.selected_jar and self.ram:
            self.start_btn.config(state="normal")
            self.restart_btn.config(state="disabled" if not self.server_process else "normal")
        else:
            self.start_btn.config(state="disabled")
            self.restart_btn.config(state="disabled")

    def open_config(self):
        top = tb.Toplevel(self)
        top.title("Configuration")
        top.geometry("400x240")
        top.grab_set()
        top.resizable(False, False)

        tb.Label(top, text="Select server.jar:").pack(anchor="w", padx=20, pady=(20,5))
        jar_frame = tb.Frame(top)
        jar_frame.pack(fill="x", padx=20)
        jar_path_var = tk.StringVar(value=self.selected_jar or "")
        jar_entry = tb.Entry(jar_frame, textvariable=jar_path_var, state="readonly")
        jar_entry.pack(side="left", fill="x", expand=True)
        tb.Button(jar_frame, text="Browse", bootstyle="info", command=lambda: self._browse_jar(jar_path_var)).pack(side="right", padx=(5,0))

        tb.Label(top, text="Assigned RAM (MB):").pack(anchor="w", padx=20, pady=(15,5))
        ram_var = tk.StringVar(value=self.ram if self.ram else "")
        ram_entry = tb.Entry(top, textvariable=ram_var)
        ram_entry.pack(fill="x", padx=20)

        tb.Label(top, text="Server Port (for player list):").pack(anchor="w", padx=20, pady=(15,5))
        port_var = tk.StringVar(value=str(self.server_port))
        port_entry = tb.Entry(top, textvariable=port_var)
        port_entry.pack(fill="x", padx=20)

        btn_frame = tb.Frame(top)
        btn_frame.pack(pady=18)

        def save():
            jar = jar_path_var.get()
            ram = ram_var.get().strip()
            port = port_var.get().strip()
            if not jar or not os.path.isfile(jar):
                messagebox.showerror("Error", "Please select a valid server.jar file.")
                return
            if not ram.isdigit() or int(ram) < 512:
                messagebox.showerror("Error", "RAM must be a number (at least 512 MB).")
                return
            if not port.isdigit() or not (1 <= int(port) <= 65535):
                messagebox.showerror("Error", "Port must be a number between 1 and 65535.")
                return
            self.selected_jar = jar
            self.ram = ram
            self.server_port = int(port)
            self.jar_lbl.config(text=os.path.basename(jar))
            self.ram_lbl.config(text=f"RAM: {ram} MB")
            self._update_start_btn_state()
            save_config({
                "selected_jar": self.selected_jar,
                "ram": self.ram,
                "server_port": self.server_port
            })
            top.destroy()

        tb.Button(btn_frame, text="Save", bootstyle="success", command=save, width=10).pack(side="left", padx=(0,10))
        tb.Button(btn_frame, text="Cancel", bootstyle="secondary", command=top.destroy, width=10).pack(side="right")

    def _browse_jar(self, jar_path_var):
        path = filedialog.askopenfilename(
            title="Select server.jar",
            filetypes=[("Java Archives", "*.jar")])
        if path:
            jar_path_var.set(path)

    def start_server(self):
        if self.server_process or not self.selected_jar or not self.ram:
            return
        try:
            ensure_dirs()
            start_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            log_name = f"{start_time}.log"
            self.session_log_path = os.path.join(LOG_DIR, log_name)
            self.log_file = open(self.session_log_path, "w", encoding="utf-8")
            cmd = [
                "java",
                f"-Xmx{self.ram}M",
                f"-Xms{self.ram}M",
                "-jar",
                self.selected_jar,
                "nogui"
            ]
            self.append_console(f"Starting server: {' '.join(cmd)}\n")
            self.server_process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            self.ps_proc = psutil.Process(self.server_process.pid)
            self.crashed = False
            self.set_status_dot("running")
            self.status_info.config(text="Running")
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.restart_btn.config(state="normal")
            play_notification_sound("start")
            threading.Thread(target=self.read_output, daemon=True).start()
        except Exception as e:
            self.append_console(f"Failed to start server: {e}\n")
            self.server_process = None
            self.ps_proc = None
            self.set_status_dot("crashed")
            self.status_info.config(text="Crashed")
            self.crashed = True

    def stop_server(self):
        if self.server_process:
            try:
                self.send_to_server("stop\n")
                self.append_console("Stopping server...\n")
                play_notification_sound("stop")
            except Exception:
                pass
        else:
            self.stop_btn.config(state="disabled")

    def restart_server(self):
        if self.server_process:
            self.restart_pending = True
            self.stop_server()
            play_notification_sound("restart")
            self.append_console("Restarting server...\n")
        else:
            self.start_server()

    def send_command(self, event=None):
        cmd = self.command_entry.get()
        if cmd.strip() and self.server_process:
            self.send_to_server(cmd + "\n")
            self.command_entry.delete(0, tk.END)

    def send_to_server(self, text):
        try:
            self.server_process.stdin.write(text)
            self.server_process.stdin.flush()
        except Exception as e:
            self.append_console(f"Failed to send command: {e}\n")

    def read_output(self):
        try:
            for line in self.server_process.stdout:
                self.output_queue.put(line)
                if self.log_file:
                    self.log_file.write(line)
        except Exception:
            pass
        self.output_queue.put("***SERVER_STOPPED***")

    def update_console(self):
        try:
            while True:
                line = self.output_queue.get_nowait()
                if line == "***SERVER_STOPPED***":
                    if self.log_file:
                        self.log_file.close()
                        self.log_file = None
                    self.ps_proc = None
                    self.server_process = None
                    self.stop_btn.config(state="disabled")
                    self.start_btn.config(state="normal" if self.selected_jar and self.ram else "disabled")
                    self.restart_btn.config(state="disabled")
                    self.set_status_dot("stopped" if not self.crashed else "crashed")
                    self.status_info.config(text="Stopped" if not self.crashed else "Crashed")
                    if self.crashed:
                        self.show_crash_alert()
                    elif self.restart_pending:
                        self.restart_pending = False
                        self.start_server()
                else:
                    self.append_console(line)
        except queue.Empty:
            pass
        self.after(100, self.update_console)

    def append_console(self, text):
        self.console.config(state="normal")
        self.console.insert(tk.END, text)
        if self.auto_scroll.get():
            self.console.see(tk.END)
        self.console.config(state="disabled")

    def clear_console(self):
        self.console.config(state="normal")
        self.console.delete("1.0", tk.END)
        self.console.config(state="disabled")

    def minimize_to_tray(self):
        self.withdraw()
        self.tray_active = True

        def on_restore(icon, item=None):
            self.after(0, self.restore_from_tray)

        def on_exit(icon, item=None):
            self.after(0, self.destroy)

        menu = pystray.Menu(
            pystray.MenuItem("Restore", on_restore),
            pystray.MenuItem("Exit", on_exit)
        )
        icon = pystray.Icon("local_server_panel", make_tray_icon(), "Local Server Panel", menu)
        self.tray_icon = icon

        def run_icon():
            icon.run()
        self.tray_thread = threading.Thread(target=run_icon, daemon=True)
        self.tray_thread.start()

    def restore_from_tray(self):
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        self.deiconify()
        self.tray_active = False

    def show_crash_alert(self):
        resp = messagebox.askyesno(
            "Server Stopped",
            "The server process stopped unexpectedly.\n\nDo you want to open the latest log file?",
        )
        if resp and self.session_log_path:
            try:
                os.startfile(self.session_log_path)
            except Exception:
                messagebox.showinfo("Info", f"Log file is located at:\n{self.session_log_path}")

    def update_status_info(self):
        # RAM/CPU (all children + main process)
        ram_mb = 0.0
        cpu = 0.0
        procs = []
        if self.ps_proc and self.ps_proc.is_running():
            try:
                procs = [self.ps_proc] + self.ps_proc.children(recursive=True)
                for proc in procs:
                    if proc.is_running():
                        ram_mb += proc.memory_info().rss / 1024 / 1024
                        cpu += proc.cpu_percent(interval=0.0)
            except Exception:
                pass
        cpu_count = psutil.cpu_count() or 1
        ram_str = f"RAM: {ram_mb:.1f} MB" if ram_mb > 0 else "RAM: -"
        cpu_str = f"CPU: {cpu / cpu_count:.1f}%" if cpu > 0 else "CPU: -"
        self.ram_status.config(text=ram_str)
        self.cpu_status.config(text=cpu_str)
        # Player count (using mcstatus)
        player_str = "Players: -"
        try:
            if self.server_port and self.server_process:
                server = JavaServer.lookup(f"localhost:{self.server_port}")
                status = server.status()
                player_str = f"Players: {status.players.online}"
        except Exception:
            pass
        self.player_status.config(text=player_str)
        self.after(2000, self.update_status_info)

    def on_close(self):
        if self.server_process:
            if messagebox.askyesno("Exit", "Server is running. Stop and exit?"):
                self.stop_server()
                self.destroy()
        else:
            self.destroy()

if __name__ == "__main__":
    app = LocalServerPanel()
    app.mainloop()
