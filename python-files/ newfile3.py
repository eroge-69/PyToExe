import tkinter as tk
from tkinter import simpledialog, messagebox, ttk

def loading_screen(root, on_complete):
    loading = tk.Toplevel(root)
    loading.geometry("350x120")
    loading.title("Loading...")

    loading.configure(bg="#2c3e50")  # Dark blue background
    label = tk.Label(loading, text="Loading weather info, please wait...", font=("Helvetica", 14, "bold"), fg="#ecf0f1", bg="#2c3e50")
    label.pack(pady=15)

    progress = ttk.Progressbar(loading, orient="horizontal", length=300, mode="determinate")
    progress.pack(pady=10)
    progress["maximum"] = 100

    def update_progress(value=0):
        if value > 100:
            loading.destroy()
            on_complete()
        else:
            progress["value"] = value
            loading.after(15, update_progress, value + 1)

    update_progress()

def prank_weather_guesser():
    root = tk.Tk()
    root.withdraw()  # Hide main window

    city = simpledialog.askstring("City Input", "Enter your city's name:")
    if city:
        def after_loading():
            messagebox.showinfo("Weather Guess", "Why don't you move your bum to check it yourself?")
            root.quit()

        loading_screen(root, after_loading)
        root.mainloop()

prank_weather_guesser()
