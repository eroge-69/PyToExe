## use Fullscreen it wont work otherwise
import pickle
import tkinter as tk
import socket
import threading
import math 
from tkinter import simpledialog, messagebox
import sqlite3



chat_list = []
Hostname = ""
root_for_dialog = tk.Tk()
root_for_dialog.withdraw()
Nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=root_for_dialog,)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)


sock.bind(('0.0.0.0', 6767))
def start():
    conn = sqlite3.connect('chatterboxlite.db')
    cursor = conn.cursor()
    cursor.execute (
        '''
     CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            Nickname TEXT NOT NULL,
            message TEXT NOT NULL
            )
''') 
    
    conn.commit()
    conn.close()
start()









def save_message(): 
    message = Chat.get 



def listen_for_messages():
    while True:
        try:
            data, addr = sock.recvfrom(80)
            message = data.decode('utf-8')
            if message not in [msg for _, msg in chat_list]:
                chat_list.append(("Other", message))
                update_chat_display()
        except Exception:
            break

def send_message(message):
    
    sock.sendto(message.encode('utf-8'), ('<broadcast>', 6767))


def New_Chat():
    item = Chat.get()
    message = Chat.get()
    if item:
        chat_list.append((Nickname, item))
        send_message(item)
        Chat.delete(0, tk.END)
        update_chat_display()

def db_message(): 
    message = Chat.get()
    conn = sqlite3.connect('chatterboxlite.db')
    cursor = conn.cursor()
    cursor.execute(
         "INSERT INTO messages (Nickname, message) VALUES (?, ?)",
        (Nickname, message)

)
    conn.commit()
    conn.close()

listener_thread = threading.Thread(target=listen_for_messages, daemon=True)
listener_thread.start()



def update_chat_display():
    global chat_box
    with sqlite3.connect('chatterboxlite.db') as conn:
        cursor = conn.cursor() 
        cursor.execute("SELECT Nickname, message, timestamp FROM messages ORDER BY timestamp ASC;")
    message = cursor.fetchall()
   
    chat_box.config(state=tk.NORMAL)
    chat_box.delete("1.0", tk.END)
   
    for sender, message in chat_list:
        chat_box.insert(tk.END, f"{sender}: {message}\n")
   
    chat_box.config(state=tk.DISABLED)
    chat_box.see(tk.END)

def New_Chat():
    item = Chat.get()
    if item:
        chat_list.append((Nickname, item))
        send_message(item)
        update_chat_display()


    
root = tk.Tk()
root.configure(bg="lightgrey")
root.title("ChatterBox Local Edition")
Chat = tk.Entry(root, width=40, background="black",
                foreground="white",
                justify="center")
Chat.pack(pady=10)

chat_box = tk.Text(root, state=tk.DISABLED, wrap=tk.WORD)
chat_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

lable = tk.Label(root, text="ChatterBox Local Edition",
                 background="black",
                 foreground="white",
                 justify="center")
lable.pack(pady=20)
Chat.pack(pady=10)



root.bind('<Return>', lambda event: (save_message(), New_Chat(), db_message()))
def on_closing():
    if messagebox.askokcancel("Quit", "do you want to end your chat session?"):
        sock.close()
        root.destroy()
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
