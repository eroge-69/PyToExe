import instaloader
import tkinter as tk
from tkinter import messagebox
import webbrowser
import re
import os
import sys

# ---- Validate Instagram URL ----
def is_valid_instagram_url(url):
    pattern = r"(https?://)?(www\.)?instagram\.com/p/[A-Za-z0-9_-]{11}/?"
    return re.match(pattern, url)

# ---- Extract shortcode from Instagram URL ----
def extract_shortcode(url):
    parts = url.strip().split("/")
    for part in parts:
        if len(part) == 11:
            return part
    return None

# ---- Download logic ----
def download_instagram_post():
    url = url_entry.get()
    
    if not is_valid_instagram_url(url):
        messagebox.showerror("Invalid URL", "Please enter a valid Instagram post URL.")
        return

    shortcode = extract_shortcode(url)
    if not shortcode:
        messagebox.showerror("Error", "Could not extract shortcode from the URL.")
        return

    try:
        loader = instaloader.Instaloader()
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        loader.download_post(post, target="downloads")
        messagebox.showinfo("Success", "✅ Download complete! Check the 'downloads' folder.")
    except Exception as e:
        messagebox.showerror("Download Failed", str(e))

# ---- Open Instagram profile in browser ----
def open_instagram():
    webbrowser.open_new("https://instagram.com/adityasahare__")

# ---- Setup app window ----
root = tk.Tk()
root.title("Instagram Video Downloader - by Aditya Sahare")
root.geometry("420x270")
root.resizable(False, False)

# ---- App icon setup ----
icon_path = "icon.ico"
if getattr(sys, 'frozen', False):
    icon_path = os.path.join(sys._MEIPASS, "icon.ico")
if os.path.exists(icon_path):
    root.iconbitmap(icon_path)

# ---- UI Elements ----
tk.Label(root, text="Paste Instagram Post URL:").pack(pady=10)
url_entry = tk.Entry(root, width=50)
url_entry.pack()

tk.Button(root, text="Download", command=download_instagram_post, bg="green", fg="white").pack(pady=20)

# ---- Developer info ----
tk.Label(root, text="Developed by Aditya Sahare", fg="gray").pack()
ig_link = tk.Label(root, text="Instagram: @adityasahare__", fg="blue", cursor="hand2")
ig_link.pack(pady=(0, 10))
ig_link.bind("<Button-1>", lambda e: open_instagram())

# ---- Start GUI loop ----
root.mainloop()
