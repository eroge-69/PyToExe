# NOTE: This script requires tkinter which is not available in some environments (e.g., headless/sandboxed).
# Make sure tkinter is installed or run it on a system with GUI support (Windows/macOS/Linux with desktop).

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, PhotoImage
    from PIL import Image, ImageDraw
    import socket
    import threading
    import os
    import tkinter.simpledialog as sd
    from pystray import Icon, MenuItem as item
    from messaging import broadcast_presence, listen_for_peers, get_active_peers
    from chat_server import start_receivers
    from plyer import notification
except ModuleNotFoundError as e:
    print("ERROR:", e)
    print("This program requires a graphical environment with tkinter installed.")
    print("Please run this script on a local desktop environment (Windows/Mac/Linux with GUI support).")
    raise SystemExit(1)

PORT_MESSAGE = 5050
PORT_FILE = 5051

def show_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=5
    )

class RMATeamApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RMA TEAM")
        self.root.geometry("300x600")
        self.root.configure(bg="white")
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

        self.canvas = tk.Canvas(self.root, width=300, height=600, highlightthickness=0)
        self.bg_image = tk.PhotoImage(file="RMA.png")
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)

        self.username = self.get_username()
        self.icon = self.create_tray_icon()
        threading.Thread(target=self.icon.run, daemon=True).start()

        self.build_top_bar()
        self.build_main_buttons()
        self.build_chat_sidebar()
        self.build_direct_message_ui()

        broadcast_presence(self.username)
        listen_for_peers(self.update_peer_dropdown)
        start_receivers(show_notification)  # <-- pass notification callback here

    def get_username(self):
        try:
            with open("user_info.txt", "r") as f:
                return f.read().strip()
        except:
            name = ""
            while not name:
                name = sd.askstring("Your Name", "Enter your display name:")
            with open("user_info.txt", "w") as f:
                f.write(name)
            return name

    def build_top_bar(self):
        top_frame = tk.Frame(self.root, bg="white")
        top_frame.pack(fill="x", padx=5, pady=5)

        self.username_var = tk.StringVar(value=self.username)
        user_dropdown = ttk.Combobox(top_frame, textvariable=self.username_var, width=10, state="readonly")
        user_dropdown['values'] = [self.username]
        user_dropdown.grid(row=0, column=0, padx=(0, 5))

        self.note_var = tk.StringVar()
        note_entry = ttk.Entry(top_frame, textvariable=self.note_var, width=20)
        note_entry.insert(0, "Type a note")
        note_entry.grid(row=0, column=1)

        self.status_var = tk.StringVar()
        self.status_dropdown = ttk.Combobox(top_frame, textvariable=self.status_var, state="readonly", width=10)
        self.status_dropdown['values'] = ['Available', 'Busy', 'Offline']
        self.status_dropdown.current(0)
        self.status_dropdown.grid(row=0, column=2, padx=(5, 0))
        self.status_dropdown.bind("<<ComboboxSelected>>", self.update_status_color)

        self.status_color_label = tk.Label(top_frame, text="●", font=("Arial", 14), fg="green", bg="white")
        self.status_color_label.grid(row=0, column=3, padx=(5, 0))

        try:
            self.photo = PhotoImage(file="profile.png")
        except:
            self.photo = PhotoImage(width=32, height=32)
        photo_label = tk.Label(top_frame, image=self.photo, bg="white")
        photo_label.grid(row=0, column=4, padx=(5, 0))

        self.update_status_color()

    def update_status_color(self, event=None):
        status = self.status_var.get()
        color = {'Available': 'green', 'Busy': 'orange', 'Offline': 'gray'}.get(status, 'black')
        self.status_color_label.config(fg=color)

    def build_main_buttons(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Blue.TButton", foreground="#0066cc", background="white", borderwidth=2,
                        focusthickness=3, focuscolor="none", relief="solid", padding=6)
        style.map("Blue.TButton", foreground=[('active', '#004c99')], background=[('active', '#f0f8ff')])

        button_frame = tk.Frame(self.root, bg="white")
        button_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(button_frame, text="Chat", width=6, style="Blue.TButton", command=self.open_direct_chat).grid(row=0, column=0, padx=2)
        ttk.Button(button_frame, text="Broadcast", width=10, style="Blue.TButton", command=self.open_general_chat).grid(row=0, column=1, padx=2)
        ttk.Button(button_frame, text="File", width=6, style="Blue.TButton", command=self.send_file).grid(row=0, column=2, padx=2)
        ttk.Button(button_frame, text="Settings", width=8, style="Blue.TButton").grid(row=0, column=3, padx=2)

    def build_chat_sidebar(self):
        sidebar = tk.Frame(self.root, bg="white")
        sidebar.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        tk.Label(sidebar, text="Groups", anchor="w", bg="white", fg="#444", font=("Arial", 10, "bold")).pack(fill="x")
        tk.Button(sidebar, text="🧑‍🤝‍🧑  General", anchor="w", relief="flat", bg="#f0f0f0", fg="black", padx=10,
                  command=self.open_general_chat).pack(fill="x", pady=2)

    def open_general_chat(self):
        messagebox.showinfo("General Chat", "Broadcast chat coming soon!")

    def build_direct_message_ui(self):
        frame = tk.Frame(self.root, bg="white")
        frame.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(frame, text="Direct Message:", anchor="w", bg="white", fg="#333", font=("Arial", 10)).pack(fill="x", pady=(0, 3))
        self.dm_var = tk.StringVar()
        self.dm_dropdown = ttk.Combobox(frame, textvariable=self.dm_var, state="readonly")
        self.dm_dropdown.pack(fill="x")
        ttk.Button(frame, text="Start Chat", command=self.open_direct_chat).pack(pady=5)

    def update_peer_dropdown(self):
        peers = get_active_peers()
        values = [f"{name} ({ip})" for ip, name in peers.items()]
        self.dm_dropdown['values'] = values
        if values:
            self.dm_dropdown.current(0)

    def open_direct_chat(self):
        selected = self.dm_var.get()
        if not selected:
            return
        try:
            ip = selected.split("(")[-1].replace(")", "").strip()
        except:
            return

        win = tk.Toplevel(self.root)
        win.title(f"Chat with {selected}")
        win.geometry("400x400")
        win.configure(bg="white")

        display = tk.Text(win, bg="#f9f9f9", state='disabled')
        display.pack(padx=10, pady=5, fill="both", expand=True)

        entry_frame = tk.Frame(win)
        entry_frame.pack(fill="x", padx=10, pady=5)

        msg_var = tk.StringVar()
        tk.Entry(entry_frame, textvariable=msg_var).pack(side="left", fill="x", expand=True)
        ttk.Button(entry_frame, text="Send", command=lambda: self.send_message(ip, msg_var, display)).pack(side="left", padx=5)

    def send_message(self, ip, msg_var, display):
        msg = msg_var.get().strip()
        if not msg:
            return
        try:
            s = socket.socket()
            s.connect((ip, PORT_MESSAGE))
            s.send(msg.encode())
            s.close()
            self.append_chat(display, f"You: {msg}")
            msg_var.set("")
        except:
            self.append_chat(display, "Failed to send message.")

    def append_chat(self, display, msg):
        display.config(state='normal')
        display.insert("end", msg + "\n")
        display.config(state='disabled')
        display.see("end")

    def send_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Documents", "*.pdf *.docx *.xlsx")])
        selected = self.dm_var.get()
        if not selected or not file_path:
            return
        ip = selected.split("(")[-1].replace(")", "").strip()
        filename = os.path.basename(file_path)
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            s = socket.socket()
            s.connect((ip, PORT_FILE))
            s.send(filename.encode() + b'||' + data)
            s.close()
            messagebox.showinfo("File", f"{filename} sent to {selected}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def create_image(self):
        image = Image.new('RGB', (64, 64), color=(0, 128, 255))
        draw = ImageDraw.Draw(image)
        draw.rectangle((16, 16, 48, 48), fill=(255, 255, 255))
        return image

    def show_window(self, icon=None, item=None):
        self.root.after(0, self.root.deiconify)

    def quit_app(self, icon=None, item=None):
        self.icon.stop()
        self.root.destroy()

    def hide_window(self):
        self.root.withdraw()

    def create_tray_icon(self):
        menu = (item('Show', self.show_window), item('Exit', self.quit_app))
        return Icon("RMA TEAM", self.create_image(), "RMA TEAM", menu)

if __name__ == "__main__":
    os.makedirs("received_files", exist_ok=True)
    root = tk.Tk()
    app = RMATeamApp(root)
    root.mainloop()
