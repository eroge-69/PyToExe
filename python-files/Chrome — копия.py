import tkinter as tk

def fake_virus():
    root = tk.Tk()
    root.title("ВАШ КОМПЬЮТЕР ЗАРАЖЕН")
    root.configure(bg='black')
    root.attributes('-fullscreen', True)  # полноэкранный режим
    root.protocol("WM_DELETE_WINDOW", lambda: None)  # отключаем кнопку закрытия (необязательно)

    label_main = tk.Label(root, text="ВАШ КОМПЬЮТЕР ЗАРАЖЕН", fg="red", bg="black", font=("Arial", 50, "bold"))
    label_main.pack(expand=True)

    countdown_label = tk.Label(root, text="", fg="red", bg="black", font=("Arial", 30, "bold"))
    countdown_label.pack()

    countdown_value = 10

    def countdown(i):
        if i >= 0:
            countdown_label.config(text=f"ВАШИ ФАЙЛЫ БУДУТ УДАЛЕНЫ ЧЕРЕЗ: {i}")
            root.after(1000, countdown, i - 1)
        else:
            label_main.pack_forget()
            countdown_label.pack_forget()
            # Черный экран остается

    countdown(countdown_value)
    root.mainloop()

if __name__ == "__main__":
    fake_virus()
