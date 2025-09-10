import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# CONFIG
CODM_SERVERS = {
    "Singapore": "203.205.127.254",
    "Hong Kong": "203.205.127.255",
    "Tokyo": "203.205.127.253"
}
PING_THRESHOLD = 55
GAME_PROCESS = "AppMarket.exe"
BACKGROUND_APPS = ["chrome.exe", "discord.exe", "spotify.exe"]
GAME_PATH = "C:\\Program Files\\txgameassistant\\AppMarket\\AppMarket.exe"

class CODMOptimizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CODM Ultimate Optimizer GUI")
        self.root.geometry("700x500")
        self.root.resizable(False, False)
        self.running = False
        self.ping_data = []

        # UI Elements
        ttk.Label(root, text="CODM Ultimate Optimizer", font=("Arial", 16)).pack(pady=10)

        # Server selector
        ttk.Label(root, text="Select CODM Server:").pack()
        self.server_var = tk.StringVar(value="Singapore")
        self.server_menu = ttk.Combobox(root, textvariable=self.server_var, values=list(CODM_SERVERS.keys()), state="readonly")
        self.server_menu.pack()

        # Start/Stop buttons
        ttk.Button(root, text="Start Optimizer", command=self.start_optimizer).pack(pady=5)
        ttk.Button(root, text="Stop Optimizer", command=self.stop_optimizer).pack(pady=5)

        # Ping display
        self.ping_var = tk.StringVar(value="Ping: N/A")
        ttk.Label(root, textvariable=self.ping_var, font=("Arial", 14)).pack(pady=5)

        self.status_var = tk.StringVar(value="Status: Idle")
        ttk.Label(root, textvariable=self.status_var, font=("Arial", 12)).pack(pady=5)

        # Real-time ping graph
        self.fig, self.ax = plt.subplots(figsize=(6,2))
        self.ax.set_title("Ping Over Time (ms)")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Ping")
        self.line, = self.ax.plot([], [], color='blue')
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(pady=10)

    def start_optimizer(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.optimize_loop, daemon=True).start()
            messagebox.showinfo("Optimizer", "CODM Optimizer Started!")

    def stop_optimizer(self):
        self.running = False
        messagebox.showinfo("Optimizer", "CODM Optimizer Stopped!")

    def optimize_loop(self):
        server_ip = CODM_SERVERS[self.server_var.get()]
        self.status_var.set("Status: Launching Gameloop and applying optimizations...")
        self.initial_setup()
        subprocess.Popen([GAME_PATH])
        time.sleep(10)
        self.set_gameloop_priority()

        self.status_var.set("Status: Monitoring ping...")

        while self.running:
            ping = self.get_ping(server_ip)
            self.ping_var.set(f"Ping: {ping} ms")
            self.ping_data.append(ping)
            if len(self.ping_data) > 50:
                self.ping_data.pop(0)
            self.update_graph()

            if ping > PING_THRESHOLD:
                self.status_var.set(f"Status: Ping high ({ping} ms)! Optimizing...")
                self.non_disruptive_optimize()
            else:
                self.status_var.set(f"Status: Ping stable ({ping} ms)")
            time.sleep(10)

    def initial_setup(self):
        # Flush DNS & Winsock
        subprocess.run("ipconfig /flushdns", shell=True)
        subprocess.run("netsh winsock reset catalog", shell=True)
        subprocess.run("netsh int ip reset", shell=True)
        # Set Cloudflare DNS
        for iface in ["Wi-Fi", "Ethernet"]:
            subprocess.run(f'netsh interface ip set dns name="{iface}" static 1.1.1.1', shell=True)
            subprocess.run(f'netsh interface ip add dns name="{iface}" 1.0.0.1 index=2', shell=True)
        # TCP optimizations
        cmds = [
            "netsh int tcp set global autotuninglevel=disabled",
            "netsh int tcp set global chimney=enabled",
            "netsh int tcp set global rss=enabled",
            "netsh int tcp set global netdma=enabled",
            "netsh int tcp set global dca=enabled"
        ]
        for cmd in cmds:
            subprocess.run(cmd, shell=True)
        # Free RAM
        for arg in ["workingsets", "modifiedpagelist", "standbylist"]:
            subprocess.run(f"EmptyStandbyList.exe {arg}", shell=True)

    def set_gameloop_priority(self):
        subprocess.run(f'wmic process where name="{GAME_PROCESS}" CALL setpriority "128"', shell=True)

    def get_ping(self, host):
        try:
            output = subprocess.check_output(f"ping -n 1 {host}", shell=True).decode()
            for line in output.splitlines():
                if "Average" in line:
                    ping_ms = line.split("Average = ")[1].replace("ms","").strip()
                    return int(ping_ms)
        except:
            return 999
        return 999

    def non_disruptive_optimize(self):
        subprocess.run("arp -d *", shell=True)
        subprocess.run("ipconfig /flushdns", shell=True)
        # Free RAM
        for arg in ["workingsets", "modifiedpagelist", "standbylist"]:
            subprocess.run(f"EmptyStandbyList.exe {arg}", shell=True)
        # Limit background apps
        for app in BACKGROUND_APPS:
            subprocess.run(f'wmic process where name="{app}" CALL setpriority "64"', shell=True)

    def update_graph(self):
        self.line.set_data(range(len(self.ping_data)), self.ping_data)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = CODMOptimizerGUI(root)
    root.mainloop()
