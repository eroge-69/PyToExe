import tkinter as tk
from tkinter import messagebox
import time

class WorkBreakTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Таймер для Работы и Отдыха")

        # Default settings (can be made configurable later)
        self.work_time_minutes = 60
        self.postpone_time_minutes = 10

        self.time_left = self.work_time_minutes * 60
        self.timer_running = False
        self.is_break_time = False

        # Create widgets
        self.time_label = tk.Label(root, text=self.format_time(self.time_left), font=("Arial", 48))
        self.time_label.pack(pady=20)

        self.start_button = tk.Button(root, text="Запустить Таймер", command=self.start_timer)
        self.start_button.pack(pady=10)

        self.break_frame = tk.Frame(root)
        self.break_frame.pack(pady=10)
        self.rest_button = tk.Button(self.break_frame, text="Я размялся", command=self.reset_timer)
        self.postpone_button = tk.Button(self.break_frame, text="Отложить", command=self.postpone_break)

        self.hide_break_buttons()

    def format_time(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.is_break_time = False
            self.start_button.config(text="Остановить Таймер", command=self.stop_timer)
            self.hide_break_buttons()
            self.countdown()

    def stop_timer(self):
        self.timer_running = False
        self.start_button.config(text="Запустить Таймер", command=self.start_timer)
        self.hide_break_buttons()
        self.time_left = self.work_time_minutes * 60 # Reset time on stop

    def countdown(self):
        if self.timer_running and self.time_left > 0:
            self.time_left -= 1
            self.time_label.config(text=self.format_time(self.time_left))
            self.root.after(1000, self.countdown)
        elif self.timer_running and self.time_left == 0:
            self.is_break_time = True
            self.timer_running = False
            self.time_label.config(text="Время отдыха!")
            self.play_sound() # Placeholder for sound
            messagebox.showinfo("Перерыв", "Пора сделать перерыв!")
            self.show_break_buttons()
            self.start_button.config(text="Запустить Таймер", command=self.start_timer) # Button becomes start again


    def reset_timer(self):
        self.time_left = self.work_time_minutes * 60
        self.is_break_time = False
        self.time_label.config(text=self.format_time(self.time_left))
        self.hide_break_buttons()
        self.start_timer() # Start a new work cycle

    def postpone_break(self):
        self.time_left = self.postpone_time_minutes * 60
        self.is_break_time = False
        self.hide_break_buttons()
        self.start_timer() # Start a postponed timer

    def show_break_buttons(self):
        self.rest_button.pack(side=tk.LEFT, padx=5)
        self.postpone_button.pack(side=tk.LEFT, padx=5)
        self.start_button.pack_forget() # Hide start button when break options are shown


    def hide_break_buttons(self):
        self.rest_button.pack_forget()
        self.postpone_button.pack_forget()
        self.start_button.pack(pady=10) # Show start button

    def play_sound(self):
        # This is a placeholder. Playing sound directly in Colab might be tricky.
        # In a standalone application, you would use a library like pygame or winsound.
        print("Sound played!")


if __name__ == '__main__':
    root = tk.Tk()
    app = WorkBreakTimer(root)
    root.mainloop()