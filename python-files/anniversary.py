import tkinter as tk
from tkinter import messagebox

# First window
def show_love_question():
    hello_window.destroy()  # Close the first window

    love_window = tk.Tk()
    love_window.title("Question for You")
    love_window.geometry("300x150")

    label = tk.Label(love_window, text="Do you love me?", font=("Arial", 14))
    label.pack(pady=20)

    def yes_clicked():
        love_window.destroy()
        messagebox.showinfo("🎉", "Happy 2 Year Anniversary ❤️")

    yes_button = tk.Button(love_window, text="Yes 💖", command=yes_clicked, width=10, font=("Arial", 12))
    yes_button.pack()

    love_window.mainloop()

hello_window = tk.Tk()
hello_window.title("Hello")
hello_window.geometry("300x150")

label = tk.Label(hello_window, text="Hello Wifey 💕", font=("Arial", 16))
label.pack(pady=40)

next_button = tk.Button(hello_window, text="Next ➡️", command=show_love_question, width=10, font=("Arial", 12))
next_button.pack()

hello_window.mainloop()
