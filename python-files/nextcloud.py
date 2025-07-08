import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import requests
from requests.auth import HTTPBasicAuth
import os
import xml.etree.ElementTree as ET

class NextcloudClient:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Nextcloud Client")
        self.login_screen()

    def login_screen(self):
        tk.Label(self.root, text="Nextcloud WebDAV URL:").pack()
        self.url_entry = tk.Entry(self.root, width=50); self.url_entry.pack()
        self.url_entry.insert(0, "https://cloud.domain.de/remote.php/webdav/")

        tk.Label(self.root, text="Benutzername:").pack()
        self.username_entry = tk.Entry(self.root); self.username_entry.pack()

        tk.Label(self.root, text="Passwort/App-Passwort:").pack()
        self.password_entry = tk.Entry(self.root, show="*"); self.password_entry.pack()

        tk.Button(self.root, text="🔐 Verbinden", command=self.login).pack(pady=5)
        self.root.mainloop()

    def login(self):
        self.url = self.url_entry.get().strip()
        self.username = self.username_entry.get().strip()
        self.password = self.password_entry.get().strip()
        auth = HTTPBasicAuth(self.username, self.password)
        try:
            r = requests.request("PROPFIND", self.url, auth=auth, headers={"Depth": "1"})
            if r.status_code != 207:
                raise Exception("Ungültige Login-Daten oder URL.")
            self.root.destroy()
            self.main_screen(auth)
        except Exception as e:
            messagebox.showerror("Login fehlgeschlagen", str(e))

    def main_screen(self, auth):
        self.auth = auth
        self.root = tk.Tk()
        self.root.title("Nextcloud Dateimanager")
        tk.Button(self.root, text="📁 Datei hochladen", command=self.upload_file).pack(pady=5)
        tk.Button(self.root, text="📥 Datei herunterladen", command=self.download_file).pack(pady=5)
        tk.Button(self.root, text="🔃 Liste aktualisieren", command=self.list_files).pack(pady=5)
        self.output = tk.Text(self.root, height=20, width=70)
        self.output.pack(pady=5)
        self.list_files()
        self.root.mainloop()

    def list_files(self):
        self.output.delete(1.0, tk.END)
        try:
            r = requests.request("PROPFIND", self.url, auth=self.auth, headers={"Depth": "1"})
            r.raise_for_status()
            tree = ET.fromstring(r.content)
            ns = {'d': 'DAV:'}
            for resp in tree.findall('d:response', ns):
                href = resp.find('d:href', ns)
                if href is not None:
                    path = href.text.replace(self.url, "")
                    if path:
                        self.output.insert(tk.END, path + "\n")
        except Exception as e:
            self.output.insert(tk.END, f"Fehler: {e}")

    def upload_file(self):
        filepath = filedialog.askopenfilename()
        if not filepath: return
        name = os.path.basename(filepath)
        url = self.url + name
        with open(filepath, 'rb') as f:
            r = requests.put(url, data=f, auth=self.auth)
        if r.status_code in (201,204):
            messagebox.showinfo("Erfolg", f"{name} hochgeladen.")
            self.list_files()
        else:
            messagebox.showerror("Fehler", f"Upload fehlgeschlagen: {r.status_code}")

    def download_file(self):
        name = simpledialog.askstring("Dateiname", "Datei herunterladen:")
        if not name: return
        url = self.url + name
        save = filedialog.asksaveasfilename(initialfile=name)
        if not save: return
        try:
            r = requests.get(url, auth=self.auth); r.raise_for_status()
            with open(save,'wb') as f: f.write(r.content)
            messagebox.showinfo("Erfolg", f"{name} gespeichert.")
        except Exception as e:
            messagebox.showerror("Fehler", str(e))

if __name__ == "__main__":
    NextcloudClient()