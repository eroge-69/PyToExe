import instaloader
import tkinter as tk
from tkinter import messagebox

# Function to extract shortcode from Instagram URL
def extract_shortcode(url):
    parts = url.strip().split("/")
    for part in parts:
        if len(part) == 11:
            return part
    return None

# Function to download Instagram post
def download_instagram_post():
    url = url_entry.get()
    shortcode = extract_shortcode(url)
    
    if not shortcode:
        messagebox.showerror("Invalid URL", "Please enter a valid Instagram post URL.")
        return
    
    try:
        loader = instaloader.Instaloader()
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        loader.download_post(post, target="downloads")
        messagebox.showinfo("Success", "Download completed! Check the 'downloads' folder.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# GUI setup
root = tk.Tk()
root.title("Instagram Video Downloader - by Aditya Sahare")
root.geometry("400x250")
root.resizable(False, False)

# UI Elements
tk.Label(root, text="Instagram Post URL:").pack(pady=10)
url_entry = tk.Entry(root, width=50)
url_entry.pack()

tk.Button(root, text="Download", command=download_instagram_post, bg="green", fg="white").pack(pady=20)

# Footer: Developer name and Instagram ID
tk.Label(root, text="Developed by Aditya Sahare", fg="gray").pack()
tk.Label(root, text="Instagram: @adityasahare__", fg="gray").pack(pady=(0, 10))

# Start the GUI loop
root.mainloop()
