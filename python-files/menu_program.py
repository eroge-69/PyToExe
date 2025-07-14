import tkinter as tk
from tkinter import messagebox

def settings():
    messagebox.showinfo("Настройки", "Здесь будут настройки игры (в разработке).")

def play():
    messagebox.showinfo("Игра", "Игра запущена! (Функционал в разработке).")

def main():
    root = tk.Tk()
    root.title("Меню")
    root.geometry("300x200")
    
    label = tk.Label(root, text="Добро пожаловать!", font=("Arial", 14))
    label.pack(pady=20)
    
    play_button = tk.Button(root, text="Play", font=("Arial", 12), command=play)
    play_button.pack(pady=10)
    
    settings_button = tk.Button(root, text="Настройки", font=("Arial", 12), command=settings)
    settings_button.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    main()