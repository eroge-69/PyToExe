from appwrite.client import Client
from appwrite.services.account import Account
from appwrite.services.databases import Databases
from appwrite.id import ID
import tkinter as tk
from tkinter import ttk, messagebox
import random, string
from datetime import datetime, timedelta
import threading, time
from pynput import mouse as pynput_mouse
import pyautogui  # for macro movement

# --- Initialize Appwrite ---
client = Client()
client.set_endpoint("https://nyc.cloud.appwrite.io/v1")
client.set_project("689806140037dd617064")
client.set_key("standard_...")  # Your API key here

account = Account(client)
db = Databases(client)

DATABASE_ID = "<YOUR_DATABASE_ID>"
COLLECTION_ID = "keysCollectionId"

# --- GUI Helper ---
def show_frame(frame):
    frame.tkraise()

# --- Owner Logic ---
def owner_login():
    email = owner_user_entry.get().strip()
    pw = owner_pass_entry.get().strip()
    try:
        account.create_email_password_session(email=email, password=pw)
        update_keys_list()
        show_frame(owner_panel_frame)
    except Exception as e:
        messagebox.showerror("Login Failed", str(e))

def generate_key():
    key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    exp_choice = expiration_var.get()
    now = datetime.now()
    expires = {
        "1 Day": (now + timedelta(days=1)).isoformat(),
        "1 Week": (now + timedelta(weeks=1)).isoformat(),
        "1 Month": (now + timedelta(days=30)).isoformat(),
        "Lifetime": "Lifetime"
    }.get(exp_choice, "Lifetime")
    db.create_document(
        database_id=DATABASE_ID,
        collection_id=COLLECTION_ID,
        document_id=ID.unique(),
        data={"key": key, "userId": None, "expires": expires}
    )
    messagebox.showinfo("Key Generated", f"{key}\nExpires: {expires}")
    update_keys_list()

def update_keys_list():
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    res = db.list_documents(database_id=DATABASE_ID, collection_id=COLLECTION_ID)
    for i, doc in enumerate(res.documents):
        k = doc["key"]
        uid = doc.get("userId") or "Unused"
        e = doc["expires"]
        tk.Label(scrollable_frame, text=f"{k} — User: {uid} — Expires: {e}", anchor="w")\
          .grid(row=i, column=0, sticky="w", padx=5, pady=2)

# --- User Logic ---
def register_user():
    email = reg_user_entry.get().strip()
    pw = reg_pass_entry.get().strip()
    key = reg_key_entry.get().strip().upper()
    if not (email and pw and key):
        messagebox.showerror("Error", "All fields required")
        return
    res = db.list_documents(
        database_id=DATABASE_ID, collection_id=COLLECTION_ID,
        filters=[f"key={key}"]
    )
    if not res.documents:
        messagebox.showerror("Error", "Invalid key")
        return
    doc = res.documents[0]
    if doc.get("userId"):
        messagebox.showerror("Error", "Key already used")
        return
    user = account.create(email=email, password=pw, user_id=ID.unique(), name=email)
    uid = user["$id"]
    db.update_document(
        database_id=DATABASE_ID, collection_id=COLLECTION_ID,
        document_id=doc["$id"], data={"userId": uid}
    )
    messagebox.showinfo("Success", "Registered! Please login.")
    show_frame(login_frame)

def user_login():
    email = login_user_entry.get().strip()
    pw = login_pass_entry.get().strip()
    try:
        account.create_email_password_session(email=email, password=pw)
        user = account.get()
        uid = user["$id"]
        res = db.list_documents(
            database_id=DATABASE_ID, collection_id=COLLECTION_ID,
            filters=[f"userId={uid}"]
        )
        if not res.documents:
            messagebox.showerror("Error", "No key assigned")
            return
        welcome_label.config(text=f"Welcome, {email}!")
        show_frame(macro_frame)
    except Exception as e:
        messagebox.showerror("Login Failed", str(e))

# --- Macro Logic ---
macro_enabled = False
button_held = False

def macro_loop():
    interval = 1 / 400  # 400Hz
    global button_held
    while macro_enabled:
        start = time.perf_counter()
        if button_held:
            try:
                h = float(horizontal_pull_var.get())
                v = float(vertical_pull_var.get())
                h = max(min(h, 50), -50)
                v = max(min(v, 50), -50)
                if h or v:
                    pyautogui.moveRel(h, v, duration=0)
            except:
                pass
        elapsed = time.perf_counter() - start
        time.sleep(max(interval - elapsed, 0.001))

def on_click(x, y, button, pressed):
    global button_held
    if not macro_enabled: return
    btn_map = {
        "left": pynput_mouse.Button.left,
        "right": pynput_mouse.Button.right,
        "middle": pynput_mouse.Button.middle
    }
    if button == btn_map.get(mouse_button_var.get()):
        button_held = pressed

def toggle_macro():
    global macro_enabled
    macro_enabled = not macro_enabled
    toggle_macro_btn.config(text="Disable Macro" if macro_enabled else "Enable Macro")
    if macro_enabled:
        threading.Thread(target=macro_loop, daemon=True).start()

# --- Build GUI ---
root = tk.Tk()
root.title("R6 Secure Access")
root.geometry("650x600")
root.resizable(False, False)

container = tk.Frame(root)
container.pack(fill="both", expand=True)
container.grid_rowconfigure(0, weight=1)
container.grid_columnconfigure(0, weight=1)

login_frame = tk.Frame(container)
register_frame = tk.Frame(container)
owner_login_frame = tk.Frame(container)
owner_panel_frame = tk.Frame(container)
macro_frame = tk.Frame(container)

for f in (login_frame, register_frame, owner_login_frame, owner_panel_frame, macro_frame):
    f.grid(row=0, column=0, sticky="nsew")

# -- Login Frame --
tk.Label(login_frame, text="User Login", font=("Arial", 26)).pack(pady=20)
login_user_entry = tk.Entry(login_frame, font=("Arial", 16)); login_user_entry.pack(pady=8, ipadx=120, ipady=7)
login_pass_entry = tk.Entry(login_frame, font=("Arial", 16), show="*"); login_pass_entry.pack(pady=8, ipadx=120, ipady=7)
tk.Button(login_frame, text="Login", font=("Arial", 16), command=user_login).pack(pady=12)
tk.Button(login_frame, text="Register", font=("Arial", 12), command=lambda: show_frame(register_frame)).pack()

# -- Register Frame --
tk.Label(register_frame, text="Register", font=("Arial", 26)).pack(pady=20)
reg_user_entry = tk.Entry(register_frame, font=("Arial", 16)); reg_user_entry.pack(pady=8, ipadx=120, ipady=7)
reg_pass_entry = tk.Entry(register_frame, font=("Arial", 16), show="*"); reg_pass_entry.pack(pady=8, ipadx=120, ipady=7)
reg_key_entry = tk.Entry(register_frame, font=("Arial", 16)); reg_key_entry.pack(pady=8, ipadx=120, ipady=7)
tk.Button(register_frame, text="Register", font=("Arial", 16), command=register_user).pack(pady=12)
tk.Button(register_frame, text="Back", font=("Arial", 12), command=lambda: show_frame(login_frame)).pack()

# -- Owner Login --
tk.Label(owner_login_frame, text="Owner Login", font=("Arial", 26)).pack(pady=20)
owner_user_entry = tk.Entry(owner_login_frame, font=("Arial", 16)); owner_user_entry.pack(pady=8, ipadx=120, ipady=7)
owner_pass_entry = tk.Entry(owner_login_frame, font=("Arial", 16), show="*"); owner_pass_entry.pack(pady=8, ipadx=120, ipady=7)
tk.Button(owner_login_frame, text="Login", font=("Arial", 16), command=owner_login).pack(pady=12)
tk.Button(owner_login_frame, text="User Login", font=("Arial", 12), command=lambda: show_frame(login_frame)).pack()

# -- Owner Panel --
tk.Label(owner_panel_frame, text="Owner Panel", font=("Arial", 26)).pack(pady=20)
expiration_var = tk.StringVar(value="Lifetime")
tk.OptionMenu(owner_panel_frame, expiration_var, "1 Day", "1 Week", "1 Month", "Lifetime").pack()
tk.Button(owner_panel_frame, text="Generate Key", font=("Arial", 16), command=generate_key).pack(pady=12)
canvas = tk.Canvas(owner_panel_frame); canvas.pack(side="left", fill="both", expand=True)
scrollbar = ttk.Scrollbar(owner_panel_frame, orient="vertical", command=canvas.yview); scrollbar.pack(side="right", fill="y")
scrollable_frame = tk.Frame(canvas)
canvas.create_window((0,0), window=scrollable_frame, anchor="nw"); canvas.configure(yscrollcommand=scrollbar.set)
scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
tk.Button(owner_panel_frame, text="Logout", font=("Arial", 12), command=lambda: show_frame(login_frame)).pack(pady=10)

# -- Macro Frame --
welcome_label = tk.Label(macro_frame, text="", font=("Arial", 20)); welcome_label.pack(pady=20)
tk.Label(macro_frame, text="Horizontal Pull (-50 to 50):").pack()
horizontal_pull_var = tk.StringVar(value="0"); tk.Entry(macro_frame, textvariable=horizontal_pull_var, width=10).pack()
tk.Label(macro_frame, text="Vertical Pull (-50 to 50):").pack()
vertical_pull_var = tk.StringVar(value="0"); tk.Entry(macro_frame, textvariable=vertical_pull_var, width=10).pack()
tk.Label(macro_frame, text="Mouse Button:").pack()
mouse_button_var = tk.StringVar(value="left")
for mb in ["left", "right", "middle"]:
    ttk.Radiobutton(macro_frame, text=mb.capitalize(), variable=mouse_button_var, value=mb).pack()
toggle_macro_btn = tk.Button(macro_frame, text="Enable Macro", font=("Arial", 16), command=toggle_macro); toggle_macro_btn.pack(pady=20)
tk.Button(macro_frame, text="Logout", font=("Arial", 12), command=lambda: show_frame(login_frame)).pack(pady=10)

# Initialize
show_frame(login_frame)
pynput_mouse.Listener(on_click=on_click).start()
root.mainloop()
