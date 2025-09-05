import tkinter as tk
from tkinter import ttk, messagebox
import requests, random, string, json

def console_insert(msg):
    console_box.insert(tk.END, msg + "\n", "red")
    console_box.see(tk.END)

def login(titleid):
    try:
        req = requests.post(
            url=f"https://{titleid}.playfabapi.com/Client/LoginWithCustomID",
            json={
                "TitleId": titleid,
                "CustomId": ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16)),
                "CreateAccount": True
            },
            headers={"Content-Type": "application/json"}
        )
        data = req.json()
        if "error" in data:
            return None
        return {
            "PlayFabId": data["data"]["PlayFabId"],
            "SessionTicket": data["data"]["SessionTicket"],
            "EntityToken": data["data"]["EntityToken"]["EntityToken"],
            "EntityId": data["data"]["EntityToken"]["Entity"]["Id"],
            "EntityType": data["data"]["EntityToken"]["Entity"]["Type"]
        }
    except Exception as e:
        console_insert(f"[!] Login Error: {e}")
        return None

def ban_player():
    player_id = ban_player_id.get().strip()
    title_id = ban_title_id.get().strip()
    if not player_id or not title_id:
        messagebox.showerror("Error", "Player ID and Title ID required!")
        return
    login_data = login(title_id)
    if not login_data:
        console_insert("[!] Failed to login to PlayFab")
        return
    try:
        req = requests.post(
            url=f"https://{title_id}.playfabapi.com/Client/ExecuteCloudScript",
            json={
                "FunctionName": "ThroughMessage",
                "FunctionParameter": {"msg": "BANNED", "pli": player_id}
            },
            headers={"X-Authorization": login_data["SessionTicket"], "Content-Type": "application/json"}
        )
        res = req.json()
        console_insert(f"[+] Ban Result: {json.dumps(res, indent=2)}")
    except Exception as e:
        console_insert(f"[!] Error banning player: {e}")

def create_account_manual():
    url = auth_url.get().strip()
    custom_id = auth_custom_id.get().strip()
    if not url:
        messagebox.showerror("Error", "Flask Auth URL required!")
        return
    try:
        body = {"CustomId": custom_id or "RANDOM" + ''.join(random.choices(string.digits, k=8))}
        response = requests.post(f"{url}/api/PlayFabAuthentication", json=body)
        console_insert(json.dumps(response.json(), indent=2))
    except Exception as e:
        console_insert(f"[!] Error: {e}")

def playfab_login():
    title_id = login_title_id.get().strip()
    if not title_id:
        messagebox.showerror("Error", "Title ID required!")
        return
    login_data = login(title_id)
    if login_data:
        console_insert("[+] Login Success:")
        console_insert(json.dumps(login_data, indent=2))
    else:
        console_insert("[!] Login Failed")

root = tk.Tk()
root.title("TRXPZ TOOLS")
root.geometry("1000x700")
root.configure(bg="black")

style = ttk.Style()
style.theme_use("clam")
style.configure("TNotebook", background="black", borderwidth=0)
style.configure("TNotebook.Tab", background="red", foreground="white", padding=10)
style.map("TNotebook.Tab", background=[("selected", "black")], foreground=[("selected", "red")])
style.configure("TLabel", background="black", foreground="white")
style.configure("TEntry", fieldbackground="black", foreground="red")
style.configure("TButton", background="red", foreground="white")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

ban_page = tk.Frame(notebook, bg="black")
notebook.add(ban_page, text="Ban Player")

ttk.Label(ban_page, text="Title ID:").pack(pady=5)
ban_title_id = ttk.Entry(ban_page, width=40)
ban_title_id.pack()

ttk.Label(ban_page, text="Player ID:").pack(pady=5)
ban_player_id = ttk.Entry(ban_page, width=40)
ban_player_id.pack()

ttk.Button(ban_page, text="Ban Player", command=ban_player).pack(pady=20)

auth_page = tk.Frame(notebook, bg="black")
notebook.add(auth_page, text="PlayFab Auth")

ttk.Label(auth_page, text="Flask Auth URL:").pack(pady=5)
auth_url = ttk.Entry(auth_page, width=50)
auth_url.pack()

ttk.Label(auth_page, text="Custom ID:").pack(pady=5)
auth_custom_id = ttk.Entry(auth_page, width=50)
auth_custom_id.pack()

ttk.Button(auth_page, text="Run Auth", command=create_account_manual).pack(pady=20)

login_page = tk.Frame(notebook, bg="black")
notebook.add(login_page, text="Login")

ttk.Label(login_page, text="Title ID:").pack(pady=5)
login_title_id = ttk.Entry(login_page, width=40)
login_title_id.pack()

ttk.Button(login_page, text="Login to PlayFab", command=playfab_login).pack(pady=20)

console_page = tk.Frame(notebook, bg="black")
notebook.add(console_page, text="Console")

console_box = tk.Text(console_page, height=25, bg="black", fg="red", insertbackground="white")
console_box.pack(fill="both", expand=True)

root.mainloop()
