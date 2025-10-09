## use Fullscreen it wont work otherwise
import tkinter as tk
from tkinter import ttk
import socket
import threading
from tkinter import simpledialog, messagebox
import sqlite3
import json
import hashlib
import platform
import subprocess
import time
from queue import Queue
from tkinter import filedialog
import json

WINDOWS_NOTIFICATIONS_ENABLED = platform.system() == "Windows"

if WINDOWS_NOTIFICATIONS_ENABLED:
    from win10toast_click import ToastNotifier

root_for_dialog = tk.Tk()
root_for_dialog.withdraw()
Nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=root_for_dialog,)


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

IS_ADMIN = Nickname in ("Michael", "Connor")

db_queue = Queue()

def db_worker():
    
    conn = sqlite3.connect('chatterboxlite.db')
    while True:
        try:
            query, params = db_queue.get()
            if query is None: 
                break
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
        except Exception as e:
            print(f"Database worker error: {e}")
        finally:
            db_queue.task_done()
    conn.close()

def start():
    conn = sqlite3.connect('chatterboxlite.db')
    cursor = conn.cursor()
    cursor.execute (
        '''
     CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            Nickname TEXT NOT NULL,
            room TEXT NOT NULL,
            message TEXT NOT NULL
            )
''') 

    cursor.execute (
        '''
     CREATE TABLE IF NOT EXISTS rooms (
            name TEXT PRIMARY KEY,
            owner TEXT NOT NULL,
            password_hash TEXT
            ) 
''')
    cursor.execute (
        '''
     CREATE TABLE IF NOT EXISTS room_members (
            room_name TEXT NOT NULL,
            user_nickname TEXT NOT NULL,
            PRIMARY KEY (room_name, user_nickname)
            )
''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS banned_users (
            nickname TEXT PRIMARY KEY
        )
    ''')

    
    conn.commit()
    conn.close()
start()

current_room = "general"
chat_history = {"general": []} 

typing_status = {} 
last_typing_sent_time = 0
online_users = {} 

after_id_presence = None
after_id_online_users = None
after_id_typing_status = None


window_is_focused = True 

def on_notification_click(room_name):
    """Callback function to switch to the room when a notification is clicked."""
    if root.state() == 'iconic':
        root.deiconify()
    root.focus_force()
    select_room(room_name, force_join=True)

def show_notification(room, sender, message_text):
    if not WINDOWS_NOTIFICATIONS_ENABLED:
        return
    
    title = f"New message in #{room}"
    msg_body = f"{sender}: {message_text}"
    toaster = ToastNotifier()
    # We run this in a thread to avoid blocking the main GUI thread.
    threading.Thread(target=lambda: toaster.show_toast(title, msg_body, duration=5, threaded=False, callback_on_click=lambda: on_notification_click(room)), daemon=True).start()

def get_known_rooms():
    with sqlite3.connect('chatterboxlite.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT room FROM messages ORDER BY room ASC;")
        rooms = [row[0] for row in cursor.fetchall()]
        if "general" not in rooms:
            rooms.insert(0, "general")
    return rooms

def listen_for_messages():

    sock.bind(('0.0.0.0', 6767))
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            payload = json.loads(data.decode('utf-8'))
            msg_type = payload.get("type", "message")

            if msg_type == "message":
           
                full_message = payload['message']
                sender_nickname, message_text = full_message.split(':', 1)
                if IS_ADMIN and is_user_banned(sender_nickname):
                    print(f"Admin client ignoring message from banned user: {sender_nickname}")
                    continue 
                room, full_message = payload['room'], payload['message']
                if not full_message.startswith(f"{Nickname}:"):
                    if room not in chat_history:
                        chat_history[room] = []
                        root.after(0, add_room_to_sidebar, room)
                    
                    chat_history[room].append(full_message)
                    if room == current_room:
                        root.after(0, update_chat_display)
                    elif not window_is_focused:
                        show_notification(room, sender_nickname, message_text.strip())
            
            elif msg_type == "typing":
                room, nickname = payload['room'], payload['nickname']
                if nickname != Nickname:
                    typing_status[(room, nickname)] = time.time()
                    if room == current_room:
                        root.after(0, update_typing_status_display)

            elif msg_type == "presence":
                room, nickname = payload['room'], payload['nickname']
                if room not in online_users:
                    online_users[room] = {}
                online_users[room][nickname] = time.time()
                # UI will be updated by the periodic `update_online_users_display`

            elif msg_type == "invite":
                invited_user = payload.get("invited_user")
                if invited_user == Nickname:
                    room_name = payload.get("room")
                    owner = payload.get("owner")
                  
                    db_queue.put(("INSERT OR IGNORE INTO room_members VALUES (?, ?)", (room_name, Nickname)))
               
                    if room_name not in chat_history:
                        chat_history[room_name] = []

                    root.after(0, add_room_to_sidebar, room_name)
                    messagebox.showinfo("Invitation", f"You have been invited to the room '#{room_name}' by {owner}.")

            elif msg_type == "delete_room":
                room_to_delete = payload.get("room")
               
                owner = payload.get("owner")
                if not owner or owner == Nickname: 
                    continue

                if room_to_delete in chat_history:
                    del chat_history[room_to_delete]
                
                root.after(0, remove_room_from_sidebar, room_to_delete)
                if current_room == room_to_delete:
                    root.after(0, select_room, "general")
            
        except (socket.error, UnicodeDecodeError, json.JSONDecodeError):
            break

def send_and_save_message(event=None):
    message = Chat.get()
    if message:

     
        query = "INSERT INTO messages (Nickname, room, message) VALUES (?, ?, ?)"
        db_queue.put((query, (Nickname, current_room, message)))
        full_message = f"{Nickname}: {message}"
        payload = {
            "type": "message",
            "room": current_room,
            "message": full_message
        }
        sock.sendto(json.dumps(payload).encode('utf-8'), ('<broadcast>', 6767))
        
      
        chat_history[current_room].append(full_message)
        update_chat_display()
        Chat.delete(0, tk.END)

def on_key_release(event=None):
    """Sends a typing notification, but not more than once per second."""
    global last_typing_sent_time
    current_time = time.time()
    if current_time - last_typing_sent_time > 1:
        payload = {
            "type": "typing",
            "room": current_room,
            "nickname": Nickname
        }
        sock.sendto(json.dumps(payload).encode('utf-8'), ('<broadcast>', 6767))
        last_typing_sent_time = current_time

def send_presence_heartbeat():
    """Broadcasts presence to the network every 10 seconds."""
    global after_id_presence
    payload = {
        "type": "presence",
        "room": current_room,
        "nickname": Nickname
    }
    sock.sendto(json.dumps(payload).encode('utf-8'), ('<broadcast>', 6767))
    after_id_presence = root.after(10000, send_presence_heartbeat)


db_thread = threading.Thread(target=db_worker, daemon=True)
db_thread.start()

listener_thread = threading.Thread(target=listen_for_messages, daemon=True)
listener_thread.start()

def update_chat_display():
    global chat_box
    chat_box.config(state=tk.NORMAL)
    chat_box.delete("1.0", tk.END)
    for msg in chat_history.get(current_room, []):
        chat_box.insert(tk.END, f"{msg}\n")
    
    if IS_ADMIN:
        chat_box.tag_config("user_message", foreground="cyan")
        chat_box.tag_bind("user_message", "<Button-3>", show_user_context_menu)
    chat_box.config(state=tk.DISABLED)
    chat_box.see(tk.END)
    root.title(f"ChatterBox Local - {Nickname} in #{current_room}")

def load_history():
  
    with sqlite3.connect('chatterboxlite.db') as conn:
    
        cursor = conn.cursor()
        cursor.execute("SELECT Nickname, room, message FROM messages ORDER BY timestamp ASC;")
        history = cursor.fetchall()
        for nick, room, msg in history:
            if room not in chat_history:
             
                is_member = cursor.execute("SELECT 1 FROM room_members WHERE room_name = ? AND user_nickname = ?", (room, Nickname)).fetchone()
                is_private = cursor.execute("SELECT 1 FROM rooms WHERE name = ? AND password_hash IS NOT NULL", (room,)).fetchone()
                if not is_private or is_member or IS_ADMIN:
                    chat_history[room] = []
            if room in chat_history:
                chat_history[room].append(f"{nick}: {msg}")

       
        if IS_ADMIN:
            cursor.execute("SELECT name FROM rooms")
            all_private_rooms_from_db = [row[0] for row in cursor.fetchall()]
            for room_name in all_private_rooms_from_db:
                if room_name not in chat_history:
                    chat_history[room_name] = [] 

       
        cursor.execute("SELECT DISTINCT room_name FROM room_members WHERE user_nickname = ?", (Nickname,))
        member_rooms = [row[0] for row in cursor.fetchall()]
        for room in member_rooms:
            if room not in chat_history:
                chat_history[room] = []

     
        cursor.execute("SELECT DISTINCT room FROM messages WHERE room NOT IN (SELECT name FROM rooms)")
        public_rooms = [row[0] for row in cursor.fetchall()]
        for room in public_rooms:
            if room not in chat_history:
                chat_history[room] = []
    
    
    for room_name in sorted(chat_history.keys()):
        add_room_to_sidebar(room_name)
    
    if "general" in chat_history:
        select_room("general")
    else: 
        chat_history["general"] = []
        add_room_to_sidebar("general")
        select_room("general")

    if IS_ADMIN: load_banned_users() 
    update_chat_display()


root = tk.Tk()
root.title(f"ChatterBox Local - {Nickname}")
root.configure(bg="#2E2E2E")
root.geometry("1000x700")
root.minsize(600, 400)

main_pane = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, bg="#2E2E2E", sashwidth=4)

def on_focus_in(event):
    global window_is_focused
    window_is_focused = True

def on_focus_out(event):
    global window_is_focused
    window_is_focused = False

root.bind("<FocusIn>", on_focus_in)
root.bind("<FocusOut>", on_focus_out)
main_pane.pack(fill=tk.BOTH, expand=True)

sidebar_frame = tk.Frame(main_pane, bg="#252526", width=200)
sidebar_frame.pack_propagate(False)

sidebar_header = tk.Frame(sidebar_frame, bg="#252526")
sidebar_header.pack(fill=tk.X, pady=5, padx=5)

rooms_label = tk.Label(sidebar_header, text="CHATROOMS", font=("Segoe UI", 10, "bold"), bg="#252526", fg="#CCCCCC")
rooms_label.pack(side=tk.LEFT)

add_room_button = tk.Button(sidebar_header, text="+", command=lambda: create_new_room(), bg="#3C3C3C", fg="white", font=("Segoe UI", 12, "bold"), width=2, borderwidth=0, activebackground="#007ACC")
add_room_button.pack(side=tk.RIGHT)


invite_button = tk.Button(sidebar_header, text="Invite", command=lambda: invite_user_to_room(current_room), bg="#3C3C3C", fg="white", font=("Segoe UI", 10, "bold"), borderwidth=0, activebackground="#007ACC", state=tk.DISABLED)
invite_button.pack(side=tk.RIGHT, padx=(5, 0))


if IS_ADMIN:
    admin_frame = tk.LabelFrame(sidebar_frame, text="ADMIN CONTROLS", font=("Segoe UI", 10, "bold"), bg="#252526", fg="#CCCCCC", bd=1, relief=tk.SOLID)
    admin_frame.pack(fill=tk.X, padx=5, pady=5)

    tk.Label(admin_frame, text="Banned Users:", bg="#252526", fg="white", font=("Segoe UI", 9)).pack(anchor=tk.W, padx=5, pady=(5,0))
    banned_users_listbox = tk.Listbox(admin_frame, bg="#1E1E1E", fg="white", font=("Segoe UI", 9), borderwidth=0, highlightthickness=0, selectbackground="#CC0000", activestyle="none", height=3)
    banned_users_listbox.pack(fill=tk.X, padx=5)

    ban_entry = tk.Entry(admin_frame, bg="#3C3C3C", fg="white", font=("Segoe UI", 9), insertbackground="white", borderwidth=0)
    ban_entry.pack(fill=tk.X, padx=5, pady=(5,0))

    ban_button_frame = tk.Frame(admin_frame, bg="#252526")
    ban_button_frame.pack(fill=tk.X, pady=(0,5))
    tk.Button(ban_button_frame, text="Ban User", command=lambda: ban_user(ban_entry.get()), bg="#CC0000", fg="white", font=("Segoe UI", 9, "bold"), borderwidth=0, activebackground="#990000").pack(side=tk.LEFT, expand=True, padx=(5,2))
    tk.Button(ban_button_frame, text="Unban User", command=lambda: unban_user_from_listbox(), bg="#007ACC", fg="white", font=("Segoe UI", 9, "bold"), borderwidth=0, activebackground="#005f9e").pack(side=tk.RIGHT, expand=True, padx=(2,5))

room_listbox = tk.Listbox(sidebar_frame, bg="#252526", fg="white", font=("Segoe UI", 11), borderwidth=0, highlightthickness=0, selectbackground="#007ACC", activestyle="none")
room_listbox.pack(fill=tk.BOTH, expand=True, padx=5)

main_pane.add(sidebar_frame, minsize=150)
main_pane.paneconfig(sidebar_frame, width=200)

chat_and_users_pane = tk.PanedWindow(main_pane, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, bg="#2E2E2E", sashwidth=4)
main_pane.add(chat_and_users_pane)

def update_online_users_display():
    """Updates the online user list and removes timed-out users."""
    global after_id_online_users
    now = time.time()
    
    # Clear the listbox before repopulating
    online_users_listbox.delete(0, tk.END)

    current_room_users = online_users.get(current_room, {})
    
    # Filter out timed-out users (inactive for > 25 seconds)
    active_users = {nick: ts for nick, ts in current_room_users.items() if now - ts < 25}
    if current_room in online_users:
        online_users[current_room] = active_users

    # Populate the listbox with active users
    for nickname in sorted(active_users.keys()):
        online_users_listbox.insert(tk.END, nickname)

    # Reschedule the check
    after_id_online_users = root.after(5000, update_online_users_display) # Check less frequently


chat_area_frame = tk.Frame(main_pane, bg="#2E2E2E")

def update_typing_status_display():
    """Updates the 'is typing' label based on current typing statuses."""
    global after_id_typing_status
    now = time.time()
    
    # Remove users who have timed out
    timed_out_users = [key for key, timestamp in typing_status.items() if now - timestamp > 3]
    for key in timed_out_users:
        del typing_status[key]

    # Get users typing in the current room
    typing_users = [nickname for (room, nickname) in typing_status.keys() if room == current_room]

    if not typing_users:
        typing_status_label.config(text="")
    elif len(typing_users) == 1:
        typing_status_label.config(text=f"{typing_users[0]} is typing...")
    elif len(typing_users) == 2:
        typing_status_label.config(text=f"{' and '.join(typing_users)} are typing...")
    else:
        typing_status_label.config(text="Several people are typing...")

    # Reschedule the check
    after_id_typing_status = root.after(1000, update_typing_status_display)



chat_box = tk.Text(chat_area_frame, state=tk.DISABLED, wrap=tk.WORD, bg="#1E1E1E", fg="white", font=("Segoe UI", 11), insertbackground="white", borderwidth=0, padx=5, pady=5)
chat_box.pack(fill=tk.BOTH, expand=True)

input_frame = tk.Frame(chat_area_frame, bg="#2E2E2E")
input_frame.pack(fill=tk.X, padx=10, pady=(5, 10))

Chat = tk.Entry(input_frame, bg="#3C3C3C", fg="white", font=("Segoe UI", 11), insertbackground="white", borderwidth=0)
Chat.bind("<KeyRelease>", on_key_release)
Chat.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 5))

typing_status_label = tk.Label(input_frame, text="", font=("Segoe UI", 9, "italic"), bg="#2E2E2E", fg="#999999")
typing_status_label.pack(side=tk.BOTTOM, anchor='w')

def send_image():
    # This is a placeholder for sending image data.
    # In a real implementation, you would read the file, maybe encode it (e.g., base64),
    # and send it in the JSON payload. The receiving clients would need to handle this new message type.
    filepath = filedialog.askopenfilename(title="Select an image", filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif")])
    if not filepath:
        return
    messagebox.showinfo("Image Messaging", f"Image messaging is not fully implemented yet.\nSelected file: {filepath}", parent=root)

image_button = tk.Button(input_frame, text="🖼️", command=send_image, bg="#3C3C3C", fg="white", font=("Segoe UI", 10), borderwidth=0, activebackground="#005f9e")
image_button.pack(side=tk.RIGHT, ipady=4, ipadx=5)

send_button = tk.Button(input_frame, text="Send", command=send_and_save_message, bg="#007ACC", fg="white", font=("Segoe UI", 10, "bold"), borderwidth=0, activebackground="#005f9e", activeforeground="white")
send_button.pack(side=tk.RIGHT, ipady=4, ipadx=10)
chat_and_users_pane.add(chat_area_frame)

# --- Online Users Panel ---
user_list_frame = tk.Frame(chat_and_users_pane, bg="#252526", width=180)
user_list_frame.pack_propagate(False)

online_label = tk.Label(user_list_frame, text="ONLINE USERS", font=("Segoe UI", 10, "bold"), bg="#252526", fg="#CCCCCC")
online_label.pack(pady=5, padx=10, anchor='w')

online_users_listbox = tk.Listbox(user_list_frame, bg="#252526", fg="white", font=("Segoe UI", 10), borderwidth=0, highlightthickness=0, selectbackground="#252526", activestyle="none")
online_users_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

chat_and_users_pane.add(user_list_frame)
chat_and_users_pane.paneconfig(user_list_frame, minsize=120, width=180)



def select_room(room_name, force_join=False):
    global current_room

    if not force_join:
        with sqlite3.connect('chatterboxlite.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash FROM rooms WHERE name = ?", (room_name,))
            private_room_info = cursor.fetchone()
            
            is_private = private_room_info and private_room_info[0]
            if is_private and not IS_ADMIN:
                cursor.execute("SELECT 1 FROM room_members WHERE room_name = ? AND user_nickname = ?", (room_name, Nickname))
                is_member = cursor.fetchone()
                if not is_member:
                    password = simpledialog.askstring("Password Required", f"Room '#{room_name}' is private. Enter password:", show='*')
                    if not password:
                        return 
                    
                    password_hash = hashlib.sha256(password.encode()).hexdigest()
                    if password_hash == private_room_info[0]:
                        db_queue.put(("INSERT OR IGNORE INTO room_members VALUES (?, ?)", (room_name, Nickname)))
                        messagebox.showinfo("Success", f"Correct password. You can now access #{room_name}.")
                    else:
                        messagebox.showerror("Access Denied", "Incorrect password.")
                       
                        if current_room in room_listbox.get(0, tk.END):
                            idx = room_listbox.get(0, tk.END).index(current_room)
                            room_listbox.selection_set(idx)
                        return


    if current_room == room_name and not force_join:
        return 

    current_room = room_name    
    if room_name in room_listbox.get(0, tk.END):
        idx = room_listbox.get(0, tk.END).index(room_name)
        room_listbox.selection_clear(0, tk.END)
        room_listbox.selection_set(idx)
        room_listbox.activate(idx)

 
    chat_box.config(state=tk.NORMAL)
    chat_box.delete("1.0", tk.END)
    for msg in chat_history.get(current_room, []):
        chat_box.insert(tk.END, f"{msg}\n")
        if IS_ADMIN:
         
            start_index = f"{chat_box.index(tk.END)} - 1 lines linestart"
            end_index = f"{chat_box.index(tk.END)} - 1 lines lineend"
            chat_box.tag_add("user_message", start_index, end_index)
    chat_box.config(state=tk.DISABLED)
    chat_box.see(tk.END)
    root.title(f"ChatterBox Local - {Nickname} in #{current_room}")

    is_owner = False
    with sqlite3.connect('chatterboxlite.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT owner FROM rooms WHERE name = ?", (room_name,))
        result = cursor.fetchone()
        if result and result[0] == Nickname:
            is_owner = True
    
    invite_button.config(state=tk.NORMAL if IS_ADMIN or is_owner else tk.DISABLED)


def on_room_select(event):
    selection = event.widget.curselection()
    if selection:
        index = selection[0]
        room_name = event.widget.get(index)
        select_room(room_name)

def add_room_to_sidebar(room_name):
    if room_name not in room_listbox.get(0, tk.END):
        room_listbox.insert(tk.END, room_name)

def create_new_room():
    new_room = simpledialog.askstring("New Room", "Enter a name for the new chatroom:", parent=root)
    if new_room and new_room.strip():
        new_room = new_room.strip().lower().replace(" ", "-")
        is_private = messagebox.askyesno("Private Room", "Make this room private? (Only invited users can join)")

        password_hash = None
        if is_private:
            password = simpledialog.askstring("Set Password", "Enter a password for the room:", show='*')
            if password:
                password_hash = hashlib.sha256(password.encode()).hexdigest()
            else: 
                messagebox.showwarning("Cancelled", "Private room creation cancelled as no password was provided.")
                return

        if new_room not in chat_history:
            chat_history[new_room] = []
            add_room_to_sidebar(new_room)

            db_queue.put(("INSERT OR IGNORE INTO rooms (name, owner, password_hash) VALUES (?, ?, ?)", (new_room, Nickname, password_hash)))
            db_queue.put(("INSERT OR IGNORE INTO room_members VALUES (?, ?)", (new_room, Nickname)))

        select_room(new_room)

def invite_user_to_room(room_name):
    invitee = simpledialog.askstring("Invite User", f"Enter the nickname of the user to invite to #{room_name}:", parent=root)
    if invitee:
        payload = {
            "type": "invite",
            "room": room_name,
            "owner": Nickname,
            "invited_user": invitee
        }
        sock.sendto(json.dumps(payload).encode('utf-8'), ('<broadcast>', 6767))
        db_queue.put(("INSERT OR IGNORE INTO room_members VALUES (?, ?)", (room_name, invitee)))
        messagebox.showinfo("Invitation Sent", f"An invitation has been sent to {invitee}.")

def delete_room(room_name):
   
    if messagebox.askyesno("Delete Room", f"Are you sure you want to permanently delete the room '#{room_name}'? This cannot be undone."):
        payload = {
            "type": "delete_room",
            "room": room_name,
            "owner": Nickname
        }
        sock.sendto(json.dumps(payload).encode('utf-8'), ('<broadcast>', 6767))
        if room_name in chat_history:
            del chat_history[room_name]
        remove_room_from_sidebar(room_name)
        if current_room == room_name:
            select_room("general")
        
      
        db_queue.put(("DELETE FROM rooms WHERE name = ?", (room_name,)))
        db_queue.put(("DELETE FROM room_members WHERE room_name = ?", (room_name,)))
        db_queue.put(("DELETE FROM messages WHERE room = ?", (room_name,)))

def remove_room_from_sidebar(room_name):
  
    if room_name in room_listbox.get(0, tk.END):
        idx = room_listbox.get(0, tk.END).index(room_name)
        room_listbox.delete(idx)


def load_banned_users():
    
    if not IS_ADMIN: return
    banned_users_listbox.delete(0, tk.END)
    with sqlite3.connect('chatterboxlite.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nickname FROM banned_users")
        for row in cursor.fetchall():
            banned_users_listbox.insert(tk.END, row[0])

def ban_user(nickname_to_ban):
    if not IS_ADMIN or not nickname_to_ban: return
    nickname_to_ban = nickname_to_ban.strip()
    if nickname_to_ban == Nickname:
        messagebox.showerror("Error", "You cannot ban yourself!")
        return
    db_queue.put(("INSERT OR IGNORE INTO banned_users VALUES (?)", (nickname_to_ban,)))
    load_banned_users()
    ban_entry.delete(0, tk.END)
    messagebox.showinfo("User Banned", f"User '{nickname_to_ban}' has been banned locally.")

def unban_user_from_listbox():
    if not IS_ADMIN: return
    selection = banned_users_listbox.curselection()
    if selection:
        nickname_to_unban = banned_users_listbox.get(selection[0])
        db_queue.put(("DELETE FROM banned_users WHERE nickname = ?", (nickname_to_unban,)))
        load_banned_users()
        messagebox.showinfo("User Unbanned", f"User '{nickname_to_unban}' has been unbanned locally.")

def is_user_banned(nickname):
  
    if not IS_ADMIN: return False
    with sqlite3.connect('chatterboxlite.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM banned_users WHERE nickname = ?", (nickname,))
        return cursor.fetchone() is not None

def show_user_context_menu(event):
    if not IS_ADMIN:
        return

   
    index = chat_box.index(f"@{event.x},{event.y}")
    
 
    line_start = f"{index} linestart"
    line_end = f"{index} lineend"
    line_text = chat_box.get(line_start, line_end)
    
    try:
        user_nickname = line_text.split(':', 1)[0].strip()
        
        user_context_menu = tk.Menu(root, tearoff=0)
        user_context_menu.add_command(label=f"View chat history for {user_nickname}", command=lambda u=user_nickname: view_user_history(u))
        user_context_menu.tk_popup(event.x_root, event.y_root)
    except IndexError:
      
        pass

def view_user_history(user_nickname):
    history_window = tk.Toplevel(root)
    history_window.title(f"Chat History for {user_nickname}")
    history_window.geometry("600x400")
    history_text = tk.Text(history_window, wrap=tk.WORD, state=tk.DISABLED, bg="#1E1E1E", fg="white")
    history_text.pack(fill=tk.BOTH, expand=True)

    with sqlite3.connect('chatterboxlite.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT room, message, timestamp FROM messages WHERE Nickname = ? ORDER BY timestamp ASC", (user_nickname,))
        history_text.config(state=tk.NORMAL)
        for room, message, timestamp in cursor.fetchall():
            history_text.insert(tk.END, f"[{timestamp}] in #{room}: {message}\n")
        history_text.config(state=tk.DISABLED)

room_context_menu = tk.Menu(root, tearoff=0)

def show_room_context_menu(event):
    selection = room_listbox.curselection()
    if not selection: return
    room_name = room_listbox.get(selection[0])

    with sqlite3.connect('chatterboxlite.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT owner FROM rooms WHERE name = ?", (room_name,))
        result = cursor.fetchone()

    room_context_menu.delete(0, tk.END)
    if (result and result[0] == Nickname) or IS_ADMIN:
        room_context_menu.add_command(label=f"Invite user to #{room_name}", command=lambda: invite_user_to_room(room_name))
        room_context_menu.add_command(label="Delete room", command=lambda: delete_room(room_name))
        room_context_menu.tk_popup(event.x_root, event.y_root)

room_listbox.bind('<<ListboxSelect>>', on_room_select)
room_listbox.bind("<Button-3>", show_room_context_menu)

root.bind('<Return>', send_and_save_message)

def on_closing():
    if messagebox.askokcancel("Quit", "do you want to end your chat session?"):
        # Stop the listener thread from processing more messages
        # which might schedule new 'after' jobs on a closing root.
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass # Socket might already be closed
        sock.close()

        # Cancel all scheduled 'after' jobs
        if after_id_presence:
            root.after_cancel(after_id_presence)
        if after_id_online_users:
            root.after_cancel(after_id_online_users)
        if after_id_typing_status:
            root.after_cancel(after_id_typing_status)

        db_queue.put((None, None))
        db_queue.join() 
        db_queue.join()
        root.destroy()
root.protocol("WM_DELETE_WINDOW", on_closing)

load_history()
update_typing_status_display() # Start the periodic check for typing status
update_online_users_display() # Start the periodic check for online users
send_presence_heartbeat() # Start broadcasting our presence

root.mainloop()
