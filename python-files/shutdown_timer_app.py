
import tkinter as tk
import subprocess

def main():
    root = tk.Tk()
    root.title("Shutdown Timer")
    root.geometry("300x200")
    root.resizable(False, False)

    label = tk.Label(root, text="Enter minutes before shutdown:")
    label.pack(pady=10)
    
    minutes_var = tk.StringVar()
    entry = tk.Entry(root, textvariable=minutes_var)
    entry.pack()

    status_label = tk.Label(root, text="", fg="green")
    status_label.pack(pady=5)

    def start_timer():
        try:
            minutes = int(minutes_var.get())
            seconds = minutes * 60
            subprocess.call(["shutdown", "-s", "-t", str(seconds)])
            status_label.config(text=f"Shutdown in {minutes} minute(s).", fg="green")
        except ValueError:
            status_label.config(text="Invalid input. Enter a number.", fg="red")

    def cancel_shutdown():
        subprocess.call(["shutdown", "-a"])
        status_label.config(text="Shutdown cancelled.", fg="blue")

    start_button = tk.Button(root, text="Start Timer", command=start_timer)
    start_button.pack(pady=5)

    cancel_button = tk.Button(root, text="Cancel Shutdown", command=cancel_shutdown)
    cancel_button.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
