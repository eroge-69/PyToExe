import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import requests
import json
import os

# Authentication credentials
USERNAME = "C2cI7EqOjTV7YmhE"
PASSWORD = "m!fxEe+8gS&Tdg9S"

SAVE_FILE = "saved_requests.json"

# Load saved requests from file
def load_saved_requests():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return {}

saved_requests = load_saved_requests()

def send_request(method, ip=None, endpoint=None, json_body=None):
    ip = ip or ip_entry.get().strip()
    endpoint = endpoint or endpoint_entry.get().strip()
    json_body = json_body or json_text.get("1.0", tk.END).strip()

    if not ip or not endpoint:
        messagebox.showerror("Error", "IP address and endpoint path are required.")
        return

    url = f"https://{ip}/{endpoint.lstrip('/')}"
    headers = {"Content-Type": "application/json"}

    try:
        data = json.loads(json_body) if json_body else None
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Invalid JSON format.")
        return

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=data,
            auth=(USERNAME, PASSWORD),
            verify=False  # Accept any certificate
        )
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, f"Method: {method}\n")
        result_text.insert(tk.END, f"Status Code: {response.status_code}\n")
        result_text.insert(tk.END, response.text)
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Request Error", str(e))

def save_request():
    name = simpledialog.askstring("Save Request", "Enter a name for this request:")
    if not name:
        return
    saved_requests[name] = {
        "ip": ip_entry.get().strip(),
        "endpoint": endpoint_entry.get().strip(),
        "json_body": json_text.get("1.0", tk.END).strip(),
        "method": method_selector.get()
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(saved_requests, f)
    update_dropdown()
    messagebox.showinfo("Saved", f"Request '{name}' saved.")

def load_request():
    name = request_selector.get()
    if name not in saved_requests:
        messagebox.showerror("Error", "Selected request not found.")
        return
    data = saved_requests[name]
    ip_entry.delete(0, tk.END)
    ip_entry.insert(0, data.get("ip", ""))
    endpoint_entry.delete(0, tk.END)
    endpoint_entry.insert(0, data.get("endpoint", ""))
    json_text.delete("1.0", tk.END)
    json_text.insert(tk.END, data.get("json_body", ""))
    method = data.get("method", "GET")
    method_selector.set(method)
    send_request(method, data["ip"], data["endpoint"], data["json_body"])

def delete_request():
    name = request_selector.get()
    if name in saved_requests:
        del saved_requests[name]
        with open(SAVE_FILE, "w") as f:
            json.dump(saved_requests, f)
        update_dropdown()
        messagebox.showinfo("Deleted", f"Request '{name}' deleted.")

def update_dropdown():
    request_selector['values'] = list(saved_requests.keys())
    if saved_requests:
        request_selector.set(list(saved_requests.keys())[0])
    else:
        request_selector.set("")

# GUI setup
root = tk.Tk()
root.title("HTTPS API Request Tool")

# Grid configuration for resizing
for i in range(4):
    root.columnconfigure(i, weight=1)
root.rowconfigure(6, weight=1)

tk.Label(root, text="IP Address:").grid(row=0, column=0, sticky="w")
ip_entry = tk.Entry(root)
ip_entry.grid(row=0, column=1, columnspan=3, sticky="ew")

tk.Label(root, text="Endpoint Path:").grid(row=1, column=0, sticky="w")
endpoint_entry = tk.Entry(root)
endpoint_entry.grid(row=1, column=1, columnspan=3, sticky="ew")

tk.Label(root, text="JSON Body:").grid(row=2, column=0, sticky="nw")
json_text = tk.Text(root, height=10)
json_text.grid(row=2, column=1, columnspan=3, sticky="nsew")
root.rowconfigure(2, weight=1)

tk.Label(root, text="Method:").grid(row=3, column=0, sticky="w")
method_selector = ttk.Combobox(root, values=["GET", "POST", "PUT", "DELETE"], state="readonly")
method_selector.set("GET")
method_selector.grid(row=3, column=1, sticky="ew")

tk.Button(root, text="Send", command=lambda: send_request(method_selector.get())).grid(row=3, column=2)
tk.Button(root, text="Save Request", command=save_request).grid(row=3, column=3)

tk.Label(root, text="Saved Requests:").grid(row=4, column=0, sticky="w")
request_selector = ttk.Combobox(root, state="readonly")
request_selector.grid(row=4, column=1, columnspan=2, sticky="ew")
tk.Button(root, text="Load Request", command=load_request).grid(row=4, column=3)
tk.Button(root, text="Delete Request", command=delete_request).grid(row=5, column=3)

tk.Label(root, text="Response:").grid(row=6, column=0, sticky="nw")
result_text = tk.Text(root)
result_text.grid(row=6, column=1, columnspan=3, sticky="nsew")

update_dropdown()
root.mainloop()