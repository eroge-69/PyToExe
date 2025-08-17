import tkinter as tk
from tkinter import messagebox
from itertools import cycle
import random
import winsound  # для звуку (тільки Windows)

class Launcher:
    def __init__(self, root):
        self.root = root
        self.root.title("A Server connect - golden edition")
        self.root.geometry("700x450")
        self.root.configure(bg="#1E1E1E")  # повернув темний стиль golden edition
        self.mi_enabled = False

        # Стиль golden edition
        self.style_bg = "#1E1E1E"
        self.style_button = "#333333"
        self.style_button_hover = "#FFD700"
        self.style_text = "#FFD700"

        # Заголовок
        self.label = tk.Label(root, text="A Server connect - golden edition", font=("Helvetica", 22, "bold"), fg=self.style_text, bg=self.style_bg)
        self.label.pack(pady=30)

        # Кнопка запуску
        self.play_btn = tk.Button(root, text="▶ Запуск", font=("Arial", 16, "bold"), bg=self.style_button, fg=self.style_text, activebackground=self.style_button_hover, relief="flat", padx=20, pady=10, command=self.start_game)
        self.play_btn.pack(pady=20)
        self.add_hover_effect(self.play_btn, self.style_button, self.style_button_hover)

        # Кнопка налаштувань
        self.settings_btn = tk.Button(root, text="⚙ Налаштування", font=("Arial", 14), bg=self.style_button, fg=self.style_text, activebackground=self.style_button_hover, relief="flat", padx=15, pady=8, command=self.open_settings)
        self.settings_btn.pack(pady=10)
        self.add_hover_effect(self.settings_btn, self.style_button, self.style_button_hover)

        # Анімація появи
        self.fade_in_widget(self.play_btn)
        self.fade_in_widget(self.settings_btn, delay=100)

        # Бінд на тильду для виклику консолі адміністратора
        self.root.bind("<asciitilde>", self.open_admin_console)
        # Бінд на клавішу 1, якщо буде активована команда BIND/console
        self.console_bind_enabled = False
        self.root.bind("1", self.open_admin_console_if_bound)

    def fade_in_widget(self, widget, delay=30):
        widget.attributes = {"alpha": 0}
        def fade():
            alpha = widget.attributes["alpha"]
            if alpha < 1:
                alpha += 0.1
                widget.attributes["alpha"] = alpha
                widget.configure(highlightbackground=f"#{int(255*alpha):02x}{int(215*alpha):02x}00")
                self.root.after(delay, fade)
        fade()

    def add_hover_effect(self, widget, base_color, hover_color):
        def on_enter(e):
            widget["bg"] = hover_color
        def on_leave(e):
            widget["bg"] = base_color
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def start_game(self):
        if not self.mi_enabled:
            messagebox.showerror("Помилка", "Код помилки: -38432\nУвімкніть MI у налаштуваннях!")
        else:
            self.open_server_program()

    def open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Налаштування")
        win.geometry("400x220")
        win.configure(bg=self.style_bg)

        tk.Label(win, text="MM | DV", font=("Arial", 16, "bold"), bg=self.style_bg, fg=self.style_text).pack(pady=15)
        tk.Label(win, text="MI:", bg=self.style_bg, fg=self.style_text).pack()

        self.mi_var = tk.StringVar(value="off")
        toggle = tk.Checkbutton(win, text="on / off", variable=self.mi_var, onvalue="on", offvalue="off", command=self.toggle_mi, bg=self.style_bg, fg=self.style_text, selectcolor=self.style_button_hover, activebackground=self.style_button_hover)
        toggle.pack(pady=15)

    def toggle_mi(self):
        self.mi_enabled = (self.mi_var.get() == "on")

    def open_server_program(self):
        server = tk.Toplevel(self.root)
        server.title("A Server connect - golden edition")
        server.geometry("600x400")
        server.configure(bg=self.style_bg)

        tk.Label(server, text="Підключення до сервера", font=("Arial", 18, "bold"), fg=self.style_text, bg=self.style_bg).pack(pady=15)

        tk.Label(server, text="IP:", bg=self.style_bg, fg=self.style_text).pack()
        ip_entry = tk.Entry(server, bg=self.style_button, fg=self.style_text, insertbackground="white")
        ip_entry.pack(pady=5)

        tk.Label(server, text="Порт:", bg=self.style_bg, fg=self.style_text).pack()
        port_entry = tk.Entry(server, bg=self.style_button, fg=self.style_text, insertbackground="white")
        port_entry.insert(0, "1187")
        port_entry.pack(pady=5)

        log_box = tk.Text(server, bg="#000000", fg="#00FF00", insertbackground="white", height=10, width=70)
        log_box.pack(pady=10)

        def connect():
            ip = ip_entry.get()
            port = port_entry.get()
            messagebox.showinfo("Статус", f"Підключення до {ip}:{port} успішне!")
            self.generate_logs(log_box, ip, port)

        connect_btn = tk.Button(server, text="🔗 Підключитися", font=("Arial", 14, "bold"), bg=self.style_button, fg=self.style_text, activebackground=self.style_button_hover, relief="flat", padx=15, pady=8, command=connect)
        connect_btn.pack(pady=10)
        self.add_hover_effect(connect_btn, self.style_button, self.style_button_hover)
        self.fade_in_widget(connect_btn)

    def generate_logs(self, log_box, ip, port):
        log_box.insert(tk.END, f"[INFO] Connected to {ip}:{port}\n")
        log_box.insert(tk.END, "[INFO] Data transfer started...\n")
        log_box.see(tk.END)

        def add_log():
            fake_ip = f"192.168.{random.randint(0,255)}.{random.randint(0,255)}"
            log_box.insert(tk.END, f"[LOG] Incoming connection from {fake_ip}\n")
            log_box.insert(tk.END, "[INFO] Data transfer started...\n")
            log_box.see(tk.END)
            try:
                winsound.Beep(800, 200)  # короткий звук
            except:
                pass
            self.root.after(10000, add_log)

        self.root.after(10000, add_log)

    def open_admin_console_if_bound(self, event=None):
        if self.console_bind_enabled:
            self.open_admin_console()

    def open_admin_console(self, event=None):
        console = tk.Toplevel(self.root)
        console.title("Administration Console")
        console.geometry("600x400")
        console.configure(bg="black")

        self.log_area = tk.Text(console, bg="black", fg="lime", insertbackground="white")
        self.log_area.pack(fill=tk.BOTH, expand=True)

        commands = [
            "cl_shadowboost 1", "cl_weaponblur 0", "cl_autopickup 1", "cl_voicefilter 'team'", "cl_pinglimit 80",
            "cl_crosshairpulse 1", "cl_reloadspeed 1.2", "cl_zoomtoggle 0", "cl_hudscale 0.85", "cl_minimaprotate 1",
            "sv_autosave 1", "sv_respawnrate 5", "sv_botdifficulty 3", "sv_mapcycle 'arena_dust'", "sv_maxplayers 16",
            "sv_teamlock 0", "sv_gravity 800", "sv_fogdensity 0.4", "sv_weather 'rain'", "sv_afktimeout 120",
            "mp_roundlimit 10", "mp_teamnames 'Alpha' 'Bravo'", "mp_spawnprotection 3", "mp_itemrespawn 30", "mp_scorelimit 100",
            "mp_autoswitch 1", "mp_voicechat 1", "mp_killfeed 1", "mp_matchid 'XJ-2048'", "mp_hudstyle 'classic'",
            "r_bloomintensity 0.7", "r_lodbias -1", "r_shadows 1", "r_particles 1", "r_waterquality 'high'",
            "r_texturefilter 'trilinear'", "r_postfx 1", "r_lightmapscale 0.5", "r_skybox 'stormy'", "r_fpscap 144",
            "ui_language 'uk-UA'", "ui_theme 'dark'", "ui_hints 0", "ui_chatopacity 0.8", "ui_cursorstyle 'dot'",
            "ui_reloadui", "ui_volume 0.6", "ui_keybinds 'default'", "ui_notifications 1", "ui_streammode 0",
            "BIND/console to '1'"
        ]

        self.log_area.insert(tk.END, "Administration Console Initialized...\n")
        self.log_area.insert(tk.END, "Available commands:\n")
        for cmd in commands:
            self.log_area.insert(tk.END, f" - {cmd}\n")
        self.log_area.see(tk.END)

        # Обробка команд
        def execute_command(event=None):
            cmd = entry.get()
            if cmd == "BIND/console to '1'":
                self.console_bind_enabled = True
                self.log_area.insert(tk.END, "[SYSTEM] Console binded to key '1'\n")
            else:
                self.log_area.insert(tk.END, f"Executed: {cmd}\n")
            self.log_area.see(tk.END)
            entry.delete(0, tk.END)

        entry = tk.Entry(console, bg="gray20", fg="white", insertbackground="white")
        entry.pack(fill=tk.X)
        entry.bind("<Return>", execute_command)


if __name__ == "__main__":
    root = tk.Tk()
    app = Launcher(root)
    root.mainloop()
