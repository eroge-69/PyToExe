import tkinter as tk
from tkinter import messagebox, scrolledtext
import socket
import threading

# =================== CONFIG ===================
HOST = '127.0.0.1'
PORT = 5000

# =================== SERVER ===================
clients = {}  # {conn: {"username": str, "status": str}}
server_started = False

def broadcast(msg, sender=None):
    for client in list(clients.keys()):
        try:
            if client != sender:
                client.send(msg.encode())
        except:
            client.close()
            if client in clients:
                del clients[client]

def broadcast_user_list():
    user_data = [f"{data['username']}|{data['status']}" for data in clients.values()]
    msg = "USERLIST:" + ";".join(user_data)
    broadcast(msg)

def handle_client(conn, addr):
    while True:
        try:
            msg = conn.recv(1024).decode()
            if not msg:
                break

            if msg.startswith("SETNAME:"):
                username = msg.split(":", 1)[1]
                clients[conn] = {"username": username, "status": "online"}
                broadcast_user_list()
            elif msg.startswith("STATUS:"):
                status = msg.split(":", 1)[1]
                if conn in clients:
                    clients[conn]["status"] = status
                    broadcast_user_list()
            else:
                broadcast(msg, sender=conn)
        except:
            break

    if conn in clients:
        del clients[conn]
        broadcast_user_list()
    conn.close()

def start_server():
    global server_started
    if server_started:
        return
    server_started = True
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print("Server started...")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

threading.Thread(target=start_server, daemon=True).start()

# =================== CLIENT (GUI) ===================
class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tycord")
        self.root.minsize(900, 550)
        self.sock = None
        self.username = None
        self.status = "online"

        # Colors
        self.style_bg = "#2f3136"
        self.style_fg = "#ffffff"
        self.style_card = "#36393f"
        self.style_entry = "#40444b"
        self.style_accent = "#5865F2"

        self.root.configure(bg=self.style_bg)
        self.login_screen()

    # ---------- UI HELPERS ----------
    def make_button(self, parent, text, command):
        btn = tk.Label(parent, text=text, font=("Arial", 12), bg=self.style_accent,
                       fg="white", padx=20, pady=10, cursor="hand2")
        btn.bind("<Button-1>", lambda e: command())
        btn.bind("<Enter>", lambda e: btn.config(bg="#6b77f8"))
        btn.bind("<Leave>", lambda e: btn.config(bg=self.style_accent))
        return btn

    def make_avatar(self, canvas, username, status="online"):
        canvas.delete("all")
        # Avatar circle
        canvas.create_oval(2, 2, 42, 42, fill="#7289da", outline="")
        # First letter
        canvas.create_text(22, 22, text=username[0].upper(), fill="white", font=("Arial", 14, "bold"))
        # Status dot
        colors = {"online": "#43b581", "idle": "#faa61a", "dnd": "#f04747", "invisible": "#747f8d"}
        dot_color = colors.get(status, "#747f8d")
        canvas.create_oval(30, 30, 42, 42, fill=dot_color, outline="")

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ---------- LOGIN SCREEN ----------
    def login_screen(self):
        self.clear()
        frame = tk.Frame(self.root, bg=self.style_bg)
        frame.pack(expand=True)

        card = tk.Frame(frame, bg=self.style_card, padx=40, pady=30)
        card.pack()

        tk.Label(card, text="Welcome to Tycord", font=("Arial", 18, "bold"),
                 bg=self.style_card, fg=self.style_fg).pack(pady=(0, 20))

        tk.Label(card, text="Username", font=("Arial", 13),
                 bg=self.style_card, fg=self.style_fg).pack(pady=5, anchor="w")
        self.username_entry = tk.Entry(card, font=("Arial", 13), bg=self.style_entry,
                                       fg=self.style_fg, insertbackground=self.style_fg,
                                       relief="flat")
        self.username_entry.pack(fill="x", pady=(0, 20), ipady=6)

        self.make_button(card, "Login", self.log_in).pack(fill="x")

    def log_in(self):
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showerror("Error", "Username cannot be empty")
            return
        self.username = username
        self.chat_screen()

    # ---------- CHAT SCREEN ----------
    def chat_screen(self):
        self.clear()
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Sidebar
        sidebar = tk.Frame(self.root, bg="#202225", width=220)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        tk.Label(sidebar, text="TYCORD", font=("Arial", 16, "bold"),
                 bg="#202225", fg="white").pack(pady=10)

        self.online_frame = tk.Frame(sidebar, bg="#2f3136")
        self.online_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Current user bottom panel
        bottom_panel = tk.Frame(sidebar, bg="#292b2f", height=60)
        bottom_panel.pack(side="bottom", fill="x")

        self.user_avatar = tk.Canvas(bottom_panel, width=44, height=44, bg="#292b2f", highlightthickness=0)
        self.user_avatar.pack(side="left", padx=5, pady=8)
        self.make_avatar(self.user_avatar, self.username, self.status)

        tk.Label(bottom_panel, text=self.username, font=("Arial", 11, "bold"),
                 bg="#292b2f", fg="white").pack(side="left", padx=5)

        # Status dropdown
        status_menu = tk.Menubutton(bottom_panel, text="▼", bg="#292b2f", fg="white",
                                   relief="flat", cursor="hand2")
        status_menu.menu = tk.Menu(status_menu, tearoff=0, bg="#2f3136", fg="white")
        status_menu["menu"] = status_menu.menu

        for s in ["online", "idle", "dnd", "invisible"]:
            status_menu.menu.add_command(
                label=s.capitalize(),
                command=lambda st=s: self.change_status(st)
            )
        status_menu.pack(side="right", padx=5)

        # Chat area
        chat_frame = tk.Frame(self.root, bg=self.style_bg)
        chat_frame.grid(row=0, column=1, sticky="nsew")

        self.text_area = scrolledtext.ScrolledText(
            chat_frame, wrap=tk.WORD, state='disabled', font=("Arial", 12),
            bg="#36393f", fg=self.style_fg, insertbackground=self.style_fg
        )
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        bottom_frame = tk.Frame(chat_frame, bg=self.style_bg)
        bottom_frame.pack(fill=tk.X, padx=10, pady=5)

        self.msg_entry = tk.Entry(
            bottom_frame, font=("Arial", 12), bg=self.style_entry, fg=self.style_fg,
            insertbackground=self.style_fg, relief="flat"
        )
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=6)
        self.msg_entry.bind("<Return>", lambda e: self.send_msg())

        self.make_button(bottom_frame, "Send", self.send_msg).pack(side=tk.RIGHT)

        # Connect to server
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((HOST, PORT))
            self.sock.send(f"SETNAME:{self.username}".encode())
        except Exception as e:
            messagebox.showerror("Error", f"Cannot connect to server: {e}")
            return

        threading.Thread(target=self.receive, daemon=True).start()

    def change_status(self, new_status):
        self.status = new_status
        self.make_avatar(self.user_avatar, self.username, self.status)
        try:
            self.sock.send(f"STATUS:{self.status}".encode())
        except:
            pass

    def send_msg(self):
        msg_content = self.msg_entry.get().strip()
        if not msg_content:
            return
        msg = f"{self.username}: {msg_content}"
        try:
            self.sock.send(msg.encode())
        except:
            messagebox.showerror("Error", "Connection lost")
            return
        self.display_message(msg, own=True)
        self.msg_entry.delete(0, tk.END)

    def receive(self):
        while True:
            try:
                msg = self.sock.recv(1024).decode()
                if not msg:
                    break
                if msg.startswith("USERLIST:"):
                    self.update_online_list(msg)
                else:
                    if msg.startswith(f"{self.username}:"):
                        continue
                    self.display_message(msg, own=False)
            except:
                break

    def display_message(self, msg, own=False):
        self.text_area.config(state='normal')
        if own:
            self.text_area.insert(tk.END, msg + '\n', 'own')
        else:
            self.text_area.insert(tk.END, msg + '\n', 'other')
        self.text_area.tag_config('own', foreground="#ffffff", justify='right')
        self.text_area.tag_config('other', foreground="#ffffff", justify='left')
        self.text_area.config(state='disabled')
        self.text_area.see(tk.END)

    def update_online_list(self, msg):
        for widget in self.online_frame.winfo_children():
            widget.destroy()

        user_data = msg.replace("USERLIST:", "").split(";")
        for u in user_data:
            if not u:
                continue
            username, status = u.split("|")
            row = tk.Frame(self.online_frame, bg="#2f3136")
            row.pack(fill="x", pady=2)

            avatar = tk.Canvas(row, width=44, height=44, bg="#2f3136", highlightthickness=0)
            avatar.pack(side="left", padx=5, pady=2)
            self.make_avatar(avatar, username, status)

            tk.Label(row, text=username, font=("Arial", 11), bg="#2f3136", fg="white").pack(side="left", padx=5)


# =================== RUN APP ===================
root = tk.Tk()
app = ChatApp(root)
root.mainloop()
