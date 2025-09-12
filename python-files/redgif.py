import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import re
import os
import uuid
import pyperclip
import requests
import getpass


class RedGifsDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("RedGifs Downloader")
        self.root.geometry("560x300")
        self.root.configure(bg="#2e2e2e")

        # Initialize token (will be fetched dynamically)
        self.api_token = None
        self.save_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.isdir(self.save_dir) or not os.access(self.save_dir, os.W_OK):
            self.save_dir = os.path.expanduser("~")
            messagebox.showwarning("Warning", f"Default save directory is not writable. Using {self.save_dir}")

        self.font_label = ("Segoe UI", 10)
        self.text_color = "white"
        self.bg_color = "#2e2e2e"
        self.accent_color = "#444"

        # Layout frame
        frame = tk.Frame(root, bg=self.bg_color, padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        # URL input
        tk.Label(frame, text="Submit URL:", font=self.font_label, fg=self.text_color, bg=self.bg_color) \
            .grid(row=0, column=0, sticky="w")
        self.url_entry = tk.Entry(frame, width=58, bg=self.accent_color, fg=self.text_color, insertbackground="white")
        self.url_entry.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky="ew")

        # Status text box
        tk.Label(frame, text="Status:", font=self.font_label, fg=self.text_color, bg=self.bg_color) \
            .grid(row=2, column=0, sticky="w")
        self.status_text = tk.Text(frame, height=7, width=65, wrap="word", bg=self.accent_color, fg="white", border=0)
        self.status_text.grid(row=3, column=0, columnspan=2, pady=(0, 10), sticky="ew")
        self.status_text.insert("end", "Ready to download\n")
        self.status_text.config(state="disabled")

        # Button container frame
        btn_frame = tk.Frame(frame, bg=self.bg_color)
        btn_frame.grid(row=4, column=0, columnspan=2, sticky="sw", pady=(10, 0))

        self.choose_btn = tk.Button(btn_frame, text="Choose Directory", command=self.choose_directory,
                                    bg="#555", fg="white", activebackground="#666", border=0, padx=10, pady=5)
        self.choose_btn.pack(side="left", padx=(0, 10))

        self.download_btn = tk.Button(btn_frame, text="Download", command=self.start_download_thread,
                                      bg="#4a90e2", fg="white", activebackground="#357ABD", border=0, padx=10, pady=5)
        self.download_btn.pack(side="left", padx=(0, 10))

        self.save_link_btn = tk.Button(btn_frame, text="Save Link", command=self.save_link,
                                       bg="#e94a4a", fg="white", activebackground="#bd3535", border=0, padx=10, pady=5)
        self.save_link_btn.pack(side="left")

        # Save directory label
        self.dir_label = tk.Label(frame, text=self.save_dir, fg=self.text_color, bg=self.bg_color, wraplength=480)
        self.dir_label.grid(row=5, column=0, sticky="w", padx=0, pady=(10, 0))

        # Success message toggle checkbox
        self.success_message_var = tk.BooleanVar(value=True)
        self.success_message_checkbox = tk.Checkbutton(frame, text="Show success message",
                                                       variable=self.success_message_var,
                                                       fg=self.text_color, bg=self.bg_color, selectcolor="#444")
        self.success_message_checkbox.grid(row=6, column=0, columnspan=2, sticky="w", padx=0, pady=(5, 0))

        # Start clipboard checking
        self.last_clipboard_content = ""
        self.check_clipboard()

    def log_status(self, message):
        """Thread-safe status logging"""

        def update_status():
            self.status_text.config(state="normal")
            self.status_text.insert("end", f"{message}\n")
            self.status_text.see("end")
            self.status_text.config(state="disabled")

        self.root.after(0, update_status)

    def choose_directory(self):
        selected_dir = filedialog.askdirectory(initialdir=self.save_dir, title="Select Save Directory")
        if selected_dir and os.access(selected_dir, os.W_OK):
            self.save_dir = selected_dir
            self.dir_label.config(text=self.save_dir)
            self.log_status(f"Save directory set to: {self.save_dir}")
        else:
            self.log_status("Selected directory is not writable or invalid.")

    def check_clipboard(self):
        try:
            clipboard_content = pyperclip.paste().strip()
            if (clipboard_content.startswith("https://www.redgifs.com") and
                    clipboard_content != self.last_clipboard_content):
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, clipboard_content)
                self.last_clipboard_content = clipboard_content
                self.log_status("Clipboard contains a valid RedGifs URL. URL pasted into the box.")
        except Exception as e:
            self.log_status(f"Error reading clipboard: {e}")
        self.root.after(500, self.check_clipboard)

    def save_link(self):
        url = self.url_entry.get().strip()
        if not url:
            self.log_status("No URL provided. Please paste a valid RedGifs URL.")
            messagebox.showerror("Error", "No URL provided. Please paste a valid RedGifs URL.")
            return

        if not url.startswith("https://www.redgifs.com"):
            self.log_status("Invalid URL. Please use a valid RedGifs URL.")
            messagebox.showerror("Error", "Invalid URL. Please use a valid RedGifs URL.")
            return

        try:
            output_file = os.path.join(self.save_dir, "saved_links.txt")
            with open(output_file, "a", encoding="utf-8") as f:
                f.write(f"{url}\n")
            self.log_status(f"URL saved to {output_file}")
            messagebox.showinfo("Success", f"URL saved to:\n{output_file}")
        except Exception as e:
            self.log_status(f"Failed to save URL: {str(e)}")
            messagebox.showerror("Error", f"Failed to save URL: {str(e)}")

    def fetch_guest_token(self):
        """Fetch a temporary guest token from RedGifs API"""
        try:
            response = requests.get("https://api.redgifs.com/v2/auth/temporary")
            if response.status_code != 200:
                raise Exception(f"Failed to fetch guest token: {response.status_code} - {response.reason}")
            data = response.json()
            token = data.get("token")
            if not token:
                raise Exception("No token found in response")
            self.log_status("Successfully fetched guest token")
            return token
        except Exception as e:
            self.log_status(f"Error fetching guest token: {str(e)}")
            raise

    def start_download_thread(self):
        self.download_btn.config(state="disabled")
        threading.Thread(target=self.download_video, daemon=True).start()

    def download_video(self):
        try:
            url = self.url_entry.get().strip()
            self.log_status("Checking URL...")

            if not url.startswith("https://www.redgifs.com/watch/"):
                self.log_status("Invalid RedGifs URL. Use format: https://www.redgifs.com/watch/xyz")
                messagebox.showerror("Error", "Invalid RedGifs URL. Use format: https://www.redgifs.com/watch/xyz")
                return

            # Extract GIF ID
            match = re.search(r'watch/([a-zA-Z0-9_-]+)', url)
            if not match:
                self.log_status("Could not extract GIF ID from URL.")
                messagebox.showerror("Error", "Could not extract GIF ID from URL.")
                return
            gif_id = match.group(1)
            self.log_status(f"Extracted GIF ID: {gif_id}")

            output_filename = f"{gif_id}.mp4"
            output_path = os.path.join(self.save_dir, output_filename)

            # Check if file exists
            if os.path.exists(output_path):
                self.log_status(f"File '{output_filename}' already exists.")
                rename = messagebox.askyesno("File Exists",
                                             f"A file named '{output_filename}' already exists.\nDo you want to give the new one a random name?")
                if rename:
                    random_name = f"{uuid.uuid4().hex}.mp4"
                    output_path = os.path.join(self.save_dir, random_name)
                    self.log_status(f"Renaming download to: {random_name}")
                else:
                    self.log_status("Download cancelled by user.")
                    return

            # Fetch token if not already set
            if not self.api_token:
                self.api_token = self.fetch_guest_token()

            self.log_status("Connecting to RedGifs API...")
            headers = {"Authorization": f"Bearer {self.api_token}"}
            api_url = f"https://api.redgifs.com/v2/gifs/{gif_id}"
            response = requests.get(api_url, headers=headers)

            # Handle 401 Unauthorized by refreshing token
            if response.status_code == 401:
                self.log_status("Token expired or invalid. Fetching new guest token...")
                self.api_token = self.fetch_guest_token()
                headers = {"Authorization": f"Bearer {self.api_token}"}
                response = requests.get(api_url, headers=headers)

            if response.status_code != 200:
                self.log_status(f"API error: {response.status_code} - {response.reason}")
                messagebox.showerror("Error", f"API error: {response.status_code} - {response.reason}")
                return

            data = response.json()
            hd_url = data.get("gif", {}).get("urls", {}).get("hd")
            if not hd_url:
                self.log_status("HD video URL not found. Video may be restricted.")
                messagebox.showerror("Error", "HD video URL not found. Video may be restricted.")
                return

            self.log_status(f"Downloading video from {hd_url}")
            video_response = requests.get(hd_url, stream=True, headers=headers)
            if video_response.status_code != 200:
                self.log_status(f"Failed to download video: {video_response.status_code} - {video_response.reason}")
                messagebox.showerror("Error",
                                     f"Failed to download video: {video_response.status_code} - {video_response.reason}")
                return

            with open(output_path, "wb") as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            self.log_status(f"Video successfully downloaded to {output_path}")

            # Show success message only if the toggle is on
            if self.success_message_var.get():
                messagebox.showinfo("Success", f"Video downloaded to:\n{output_path}")

        except Exception as e:
            self.log_status(f"Failed to download video: {str(e)}")
            messagebox.showerror("Error", f"Failed to download video: {str(e)}")
        finally:
            self.root.after(0, lambda: self.download_btn.config(state="normal"))


def main():
    root = tk.Tk()
    root.resizable(False, False)
    app = RedGifsDownloader(root)
    root.mainloop()


if __name__ == "__main__":
    main()
