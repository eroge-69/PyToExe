import os
import sys
import json
import glob
import subprocess
from urllib.parse import urlparse
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog, ttk

CONFIG_FILE = os.path.expanduser("~/.profile_link_router_config.json")

def get_browser_user_data_path(browser):
    if browser == "Edge":
        return os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data")
    elif browser == "Chrome":
        return os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
    else:
        return None

def get_browser_executable(browser):
    if browser == "Edge":
        paths = [
            os.path.expandvars(r"%PROGRAMFILES(X86)%\Microsoft\Edge\Application\msedge.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\Microsoft\Edge\Application\msedge.exe"),
        ]
    elif browser == "Chrome":
        paths = [
            os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
        ]
    else:
        return None
    for path in paths:
        if os.path.exists(path):
            return path
    return None

def get_profiles(browser):
    user_data_path = get_browser_user_data_path(browser)
    if not user_data_path or not os.path.exists(user_data_path):
        return []
    profiles = [os.path.join(user_data_path, "Default")]
    profiles += glob.glob(os.path.join(user_data_path, "Profile *"))
    return profiles

def extract_domains_from_profile(profile_path):
    preferences_path = os.path.join(profile_path, "Preferences")
    if not os.path.exists(preferences_path):
        return []
    try:
        with open(preferences_path, "r", encoding="utf-8") as f:
            prefs = json.load(f)
        domains = []
        for acct in prefs.get("account_info", []):
            email = acct.get("email", "")
            if "@" in email:
                domains.append(email.split("@")[1].lower())
        return domains
    except Exception as e:
        print(f"Error reading {preferences_path}: {e}")
        return []

def build_domain_profile_mapping(browser):
    mapping = {}
    for profile_path in get_profiles(browser):
        domains = extract_domains_from_profile(profile_path)
        for domain in domains:
            mapping[domain] = profile_path
    return mapping

def launch_browser_with_profile(browser, profile_path, url):
    profile_dir = os.path.basename(profile_path)
    exe = get_browser_executable(browser)
    if not exe:
        messagebox.showerror("Error", f"{browser} executable not found!")
        return
    cmd = [
        exe,
        f'--profile-directory={profile_dir}',
        url
    ]
    subprocess.Popen(cmd)

def open_url_in_correct_profile(url, browser, mapping):
    domain = urlparse(url).hostname
    matched_profile = None
    for mapped_domain, profile_path in mapping.items():
        if domain and domain.lower().endswith(mapped_domain):
            matched_profile = profile_path
            break
    if matched_profile:
        launch_browser_with_profile(browser, matched_profile, url)
    else:
        # Fallback: open with default profile
        default_profile = os.path.join(get_browser_user_data_path(browser), "Default")
        launch_browser_with_profile(browser, default_profile, url)

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# --- GUI Section ---
class ProfileRouterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Profile Link Router - Default Browser")
        self.geometry("650x500")
        self.resizable(False, False)
        self.config = load_config()
        self.browser_var = tk.StringVar(value=self.config.get("browser", "Edge"))
        self.mapping = self.config.get("mapping", {})

        frame = tk.Frame(self)
        frame.pack(pady=10)

        tk.Label(frame, text="Select Preferred Browser:").grid(row=0, column=0, sticky="w")
        self.browser_combo = ttk.Combobox(frame, textvariable=self.browser_var, values=["Edge", "Chrome"], state="readonly", width=10)
        self.browser_combo.grid(row=0, column=1, padx=10)

        self.btn_build = tk.Button(frame, text="Build/Update Profile Mapping", command=self.build_mapping)
        self.btn_build.grid(row=0, column=2, padx=10)

        self.btn_save = tk.Button(frame, text="Save Settings", command=self.save_settings)
        self.btn_save.grid(row=0, column=3, padx=10)

        self.txt_mapping = scrolledtext.ScrolledText(self, width=80, height=15)
        self.txt_mapping.pack(pady=10)

        self.lbl_url = tk.Label(self, text="Test: Enter a URL to open in the correct profile:")
        self.lbl_url.pack()
        self.entry_url = tk.Entry(self, width=70)
        self.entry_url.pack(pady=5)

        self.btn_open = tk.Button(self, text="Open in Correct Profile", command=self.open_url)
        self.btn_open.pack(pady=10)

        self.load_mapping_display()

    def build_mapping(self):
        browser = self.browser_var.get()
        self.mapping = build_domain_profile_mapping(browser)
        self.load_mapping_display()
        messagebox.showinfo("Mapping Updated", f"Domain to profile mapping for {browser} updated.")

    def load_mapping_display(self):
        self.txt_mapping.delete(1.0, tk.END)
        if not self.mapping:
            self.txt_mapping.insert(tk.END, "No profiles or domains found.\n")
        else:
            for domain, profile in self.mapping.items():
                self.txt_mapping.insert(tk.END, f"{domain} -> {profile}\n")

    def save_settings(self):
        self.config["browser"] = self.browser_var.get()
        self.config["mapping"] = self.mapping
        save_config(self.config)
        messagebox.showinfo("Settings Saved", "Browser and mapping settings saved.")

    def open_url(self):
        url = self.entry_url.get().strip()
        if not url:
            messagebox.showwarning("Input Needed", "Please enter a URL.")
            return
        if not url.startswith("http"):
            url = "https://" + url
        browser = self.browser_var.get()
        open_url_in_correct_profile(url, browser, self.mapping)

# --- Main Entrypoint ---
def main():
    # If launched with a URL, handle as default browser
    if len(sys.argv) > 1:
        url = sys.argv[1]
        config = load_config()
        browser = config.get("browser", "Edge")
        mapping = config.get("mapping", {})
        open_url_in_correct_profile(url, browser, mapping)
    else:
        # Launch GUI
        app = ProfileRouterApp()
        app.mainloop()

if __name__ == "__main__":
    main()
