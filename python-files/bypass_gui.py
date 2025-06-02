import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
from bypass import start_game, bypass_emulator
from config import game_path

class BypassGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Emulator Bypass Tool")
        self.geometry("300x150")
        self.resizable(False, False)

        self.label = tk.Label(self, text="Click Start to bypass and launch the game")
        self.label.pack(pady=10)

        self.start_button = tk.Button(self, text="Start", command=self.run_bypass)
        self.start_button.pack(pady=10)

    def run_bypass(self):
        self.start_button.config(state="disabled")
        self.label.config(text="Launching game and bypassing...")
        threading.Thread(target=self.bypass_process).start()

    def bypass_process(self):
        try:
            # Launch game
            start_game()
            # Perform bypass
            bypass_emulator()
            self.label.config(text="Bypass successful! Game launched.")
            messagebox.showinfo("Success", "Bypass completed and game has been launched.")
        except Exception as e:
            self.label.config(text="An error occurred.")
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.start_button.config(state="normal")

if __name__ == "__main__":
    app = BypassGUI()
    app.mainloop()
