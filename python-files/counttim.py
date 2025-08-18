import tkinter as tk
from tkinter import messagebox
import pyttsx3
import threading
import time

class CountdownTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Countdown Timer App")
        
        self.timers = []  # Store active timers

        # Setup Text-to-Speech Engine
        self.engine = pyttsx3.init()

        # Labels and Input Fields for Hours, Minutes, Seconds
        self.hour_label = tk.Label(root, text="Hours:")
        self.hour_label.grid(row=0, column=0)
        self.hour_entry = tk.Entry(root)
        self.hour_entry.grid(row=0, column=1)

        self.minute_label = tk.Label(root, text="Minutes:")
        self.minute_label.grid(row=1, column=0)
        self.minute_entry = tk.Entry(root)
        self.minute_entry.grid(row=1, column=1)

        self.second_label = tk.Label(root, text="Seconds:")
        self.second_label.grid(row=2, column=0)
        self.second_entry = tk.Entry(root)
        self.second_entry.grid(row=2, column=1)

        # Word to Speak on Completion
        self.word_label = tk.Label(root, text="Word to Speak:")
        self.word_label.grid(row=3, column=0)
        self.word_entry = tk.Entry(root)
        self.word_entry.grid(row=3, column=1)

        # Button to Add Timer
        self.add_button = tk.Button(root, text="Add Timer", command=self.add_timer)
        self.add_button.grid(row=4, column=0, columnspan=2)

        # Status Label
        self.status_label = tk.Label(root, text="Timers will appear here.", anchor="w")
        self.status_label.grid(row=5, column=0, columnspan=2, sticky="w")

    def add_timer(self):
        try:
            # Read inputs for hours, minutes, and seconds
            hours = int(self.hour_entry.get() or 0)
            minutes = int(self.minute_entry.get() or 0)
            seconds = int(self.second_entry.get() or 0)
            word = self.word_entry.get().strip()

            if word == "":
                messagebox.showerror("Input Error", "Please provide a word to speak after timer finishes.")
                return

            total_seconds = (hours * 3600) + (minutes * 60) + seconds
            if total_seconds <= 0:
                messagebox.showerror("Input Error", "Please set a valid time for the timer.")
                return

            # Create a timer and append to timers list
            timer = (total_seconds, word)
            self.timers.append(timer)

            # Display active timers
            self.update_timer_list()

            # Start the countdown in a background thread
            threading.Thread(target=self.start_timer, args=(total_seconds, word)).start()

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for hours, minutes, and seconds.")

    def start_timer(self, countdown_time, word_to_speak):
        while countdown_time > 0:
            time.sleep(1)
            countdown_time -= 1
            # Here you can update the UI if you want to show the countdown live (use `root.after()` to schedule updates)

        # Timer has finished, speak the word
        self.speak_word(word_to_speak)

    def speak_word(self, word):
        self.engine.say(word)
        self.engine.runAndWait()
        print(f"Speaking: {word}")

    def update_timer_list(self):
        timers_text = "Active Timers:\n"
        for idx, (time_left, word) in enumerate(self.timers):
            timers_text += f"{idx + 1}. {self.format_time(time_left)} - Word: {word}\n"
        self.status_label.config(text=timers_text)

    def format_time(self, total_seconds):
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"

if __name__ == "__main__":
    root = tk.Tk()
    app = CountdownTimerApp(root)
    root.mainloop()
