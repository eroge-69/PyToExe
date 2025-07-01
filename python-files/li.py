import tkinter as tk
from tkinter import simpledialog, messagebox
import pyperclip
import pyrebase

# --------- Firebase Config ---------
firebaseConfig = {
    "apiKey": "AIzaSyC2AMMfm647GBJ-V8i8iL5arKYHLznwHIE",
    "authDomain": "drivelinkmanager-b7168.firebaseapp.com",
    "databaseURL": "https://drivelinkmanager-b7168-default-rtdb.firebaseio.com",
    "storageBucket": "drivelinkmanager-b7168.firebasestorage.app"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()

MASTER_PASSWORD = "9821590207"

# --------- Colors and Fonts ---------
BG_COLOR = "#1e1e2f"       # Dark blueish background
FG_COLOR = "#ffffff"       # White foreground text
ENTRY_BG = "#2c2c4c"       # Entry background
BTN_BG = "#4a90e2"         # Blue buttons
BTN_FG = "#ffffff"
BTN_HOVER_BG = "#357ABD"   # Button hover color
LABEL_FONT = ("Segoe UI", 10, "bold")
ENTRY_FONT = ("Segoe UI", 10)
BTN_FONT = ("Segoe UI", 10, "bold")

firebase_user = None  # global user variable

# --------- Master Password Dialog ---------
def ask_master_password():
    pwd = simpledialog.askstring("Master Password", "Enter Master Password:", show='*')
    if pwd != MASTER_PASSWORD:
        messagebox.showerror("Error", "Wrong Master Password! Exiting...")
        root.destroy()
        return False
    return True

# --------- Firebase Login Dialog ---------
def ask_firebase_login():
    login_win = tk.Toplevel(root)
    login_win.title("Firebase Login")
    login_win.geometry("320x170")
    login_win.config(bg=BG_COLOR)
    login_win.grab_set()

    tk.Label(login_win, text="Email:", fg=FG_COLOR, bg=BG_COLOR, font=LABEL_FONT).pack(pady=(15,0))
    email_entry = tk.Entry(login_win, width=35, bg=ENTRY_BG, fg=FG_COLOR, insertbackground=FG_COLOR, font=ENTRY_FONT)
    email_entry.pack(pady=5)

    tk.Label(login_win, text="Password:", fg=FG_COLOR, bg=BG_COLOR, font=LABEL_FONT).pack()
    pass_entry = tk.Entry(login_win, show="*", width=35, bg=ENTRY_BG, fg=FG_COLOR, insertbackground=FG_COLOR, font=ENTRY_FONT)
    pass_entry.pack(pady=5)

    def login_action():
        email = email_entry.get()
        password = pass_entry.get()
        global firebase_user
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            firebase_user = user
            messagebox.showinfo("Success", "Logged in successfully!")
            login_win.destroy()
        except Exception as e:
            print("Login error:", e)  # For debugging in console
            messagebox.showerror("Login Failed", "Invalid email or password! Or check your internet.")

    btn_login = tk.Button(login_win, text="Login", bg=BTN_BG, fg=BTN_FG, font=BTN_FONT, command=login_action)
    btn_login.pack(pady=15, ipadx=10, ipady=5)

    root.wait_window(login_win)

# --------- Save Link ---------
def save_link():
    if not firebase_user:
        messagebox.showerror("Error", "Not logged in!")
        return
    title = entry_title.get().strip().lower()
    link = entry_link.get().strip()
    password = entry_password.get().strip()
    if not title or not link or not password:
        messagebox.showwarning("Warning", "Fill all fields!")
        return
    try:
        db.child("links").child(title).set({"link": link, "password": password}, firebase_user['idToken'])
        messagebox.showinfo("Saved", f"Saved '{title}' successfully!")
    except Exception as e:
        print("Save error:", e)
        messagebox.showerror("Error", "Failed to save data. Check your internet connection.")

# --------- Search Link ---------
def search_link():
    if not firebase_user:
        messagebox.showerror("Error", "Not logged in!")
        return
    title = entry_title.get().strip().lower()
    if not title:
        messagebox.showwarning("Warning", "Enter title to search!")
        return
    try:
        result = db.child("links").child(title).get(firebase_user['idToken'])
        if result.val():
            data = result.val()
            entry_link.delete(0, tk.END)
            entry_link.insert(0, data.get('link', ''))
            entry_password.delete(0, tk.END)
            entry_password.insert(0, data.get('password', ''))
        else:
            messagebox.showinfo("Not Found", "No data found for this title.")
    except Exception as e:
        print("Search error:", e)
        messagebox.showerror("Error", "Failed to fetch data. Check your internet connection.")

# --------- Show All Data Window ---------
def show_all_data():
    if not firebase_user:
        messagebox.showerror("Error", "Not logged in!")
        return
    try:
        all_data = db.child("links").get(firebase_user['idToken'])
        if not all_data.each():
            messagebox.showinfo("No Data", "No saved links found.")
            return

        display_win = tk.Toplevel(root)
        display_win.title("All Saved Links")
        display_win.geometry("750x480")
        display_win.config(bg=BG_COLOR)

        tk.Label(display_win, text="Search:", fg=FG_COLOR, bg=BG_COLOR, font=LABEL_FONT).pack(anchor='w', padx=10, pady=5)
        search_var = tk.StringVar()
        search_entry = tk.Entry(display_win, textvariable=search_var, width=55, bg=ENTRY_BG, fg=FG_COLOR, insertbackground=FG_COLOR, font=ENTRY_FONT)
        search_entry.pack(padx=10, pady=5)

        frame = tk.Frame(display_win, bg=BG_COLOR)
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        canvas = tk.Canvas(frame, bg=BG_COLOR, highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BG_COLOR)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def copy_to_clipboard(link, password):
            combined = f"Link: {link}\nPassword: {password}"
            pyperclip.copy(combined)
            messagebox.showinfo("Copied", "Link and Password copied to clipboard!")

        items_widgets = []

        def update_list(*args):
            search_term = search_var.get().lower()
            for item in items_widgets:
                title = item['title']
                if search_term in title.lower():
                    item['frame'].pack(fill='x', pady=3)
                else:
                    item['frame'].pack_forget()

        search_var.trace_add('write', update_list)

        for item in all_data.each():
            title = item.key()
            data = item.val()
            link = data.get('link', '')
            password = data.get('password', '')

            item_frame = tk.Frame(scrollable_frame, relief='ridge', borderwidth=1, padx=8, pady=8, bg="#2c2c4c")
            item_frame.pack(fill='x', pady=3)

            lbl_title = tk.Label(item_frame, text=f"Title: {title}", font=("Segoe UI", 10, "bold"), bg="#2c2c4c", fg="#cde0ff")
            lbl_title.grid(row=0, column=0, sticky='w')

            btn_copy = tk.Button(item_frame, text="Copy Link & Password", bg="#357ABD", fg="white", font=BTN_FONT,
                                 command=lambda l=link, p=password: copy_to_clipboard(l, p), cursor="hand2")
            btn_copy.grid(row=0, column=1, padx=5)

            lbl_link = tk.Label(item_frame, text=f"Link: {link}", bg="#2c2c4c", fg="#e0e0e0", font=ENTRY_FONT)
            lbl_link.grid(row=1, column=0, columnspan=2, sticky='w')

            lbl_password = tk.Label(item_frame, text=f"Password: {password}", bg="#2c2c4c", fg="#e0e0e0", font=ENTRY_FONT)
            lbl_password.grid(row=2, column=0, columnspan=2, sticky='w')

            items_widgets.append({'frame': item_frame, 'title': title})

        display_win.mainloop()

    except Exception as e:
        print("Show all data error:", e)
        messagebox.showerror("Error", "Failed to fetch data. Check your internet connection.")

# --------- GUI Setup ---------
root = tk.Tk()
root.title("Drive Link Manager (Firebase)")
root.geometry("570x300")
root.config(bg=BG_COLOR)

def on_enter(e):
    e.widget['background'] = BTN_HOVER_BG

def on_leave(e):
    e.widget['background'] = BTN_BG

tk.Label(root, text="Title:", bg=BG_COLOR, fg=FG_COLOR, font=LABEL_FONT).grid(row=0, column=0, padx=10, pady=15, sticky='e')
entry_title = tk.Entry(root, width=50, bg=ENTRY_BG, fg=FG_COLOR, insertbackground=FG_COLOR, font=ENTRY_FONT)
entry_title.grid(row=0, column=1)

tk.Label(root, text="Google Drive Link:", bg=BG_COLOR, fg=FG_COLOR, font=LABEL_FONT).grid(row=1, column=0, padx=10, pady=10, sticky='e')
entry_link = tk.Entry(root, width=50, bg=ENTRY_BG, fg=FG_COLOR, insertbackground=FG_COLOR, font=ENTRY_FONT)
entry_link.grid(row=1, column=1)

tk.Label(root, text="Password:", bg=BG_COLOR, fg=FG_COLOR, font=LABEL_FONT).grid(row=2, column=0, padx=10, pady=10, sticky='e')
entry_password = tk.Entry(root, width=50, bg=ENTRY_BG, fg=FG_COLOR, insertbackground=FG_COLOR, font=ENTRY_FONT)
entry_password.grid(row=2, column=1)

btn_save = tk.Button(root, text="Save Link", bg=BTN_BG, fg=BTN_FG, font=BTN_FONT, command=save_link, cursor="hand2")
btn_save.grid(row=3, column=0, pady=20, padx=10, sticky='e')
btn_save.bind("<Enter>", on_enter)
btn_save.bind("<Leave>", on_leave)

btn_search = tk.Button(root, text="Search Link", bg=BTN_BG, fg=BTN_FG, font=BTN_FONT, command=search_link, cursor="hand2")
btn_search.grid(row=3, column=1, pady=20, padx=10, sticky='w')
btn_search.bind("<Enter>", on_enter)
btn_search.bind("<Leave>", on_leave)

btn_show_all = tk.Button(root, text="Show All Data", bg=BTN_BG, fg=BTN_FG, font=BTN_FONT, command=show_all_data, cursor="hand2")
btn_show_all.grid(row=4, column=0, columnspan=2, pady=10)
btn_show_all.bind("<Enter>", on_enter)
btn_show_all.bind("<Leave>", on_leave)

# Start with master password
if not ask_master_password():
    exit()

# Then firebase login
ask_firebase_login()

root.mainloop()
