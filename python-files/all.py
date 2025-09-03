import tkinter as tk
import keyboard
import time

# Морзянка для букв и пробела
morse_code = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..',
    '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
    '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----',
    ' ': '/'
}

class MorseApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Morse Code Translator")

        self.input_text = ""
        self.current_morse = ""

        self.text_display = tk.Label(master, text="", font=("Helvetica", 24))
        self.text_display.pack(pady=20)

        self.morse_display = tk.Label(master, text="", font=("Helvetica", 24))
        self.morse_display.pack(pady=20)

        self.master.bind('<space>', self.space_pressed)
        self.master.bind('<Return>', self.enter_pressed)
        self.master.bind('<Escape>', self.exit_app)

        self.master.after(100, self.check_keyboard)

    def space_pressed(self, event):
        start_time = time.time()
        while keyboard.is_pressed('space'):
            time.sleep(0.01)  # ждем, пока пробел будет нажат
        duration = time.time() - start_time

        if duration < 0.5:
            self.current_morse += '.'  # короткое нажатие - точка
        else:
            self.current_morse += '-'  # длительное нажатие - тире

        self.morse_display.config(text=self.current_morse)

    def enter_pressed(self, event):
        if self.current_morse:  # Проверяем, что текущий ввод не пуст
            self.input_text += self.current_morse + " "  # добавляем символ в текст
            self.text_display.config(text=self.input_text.strip())  # обновляем текст
            self.current_morse = ""  # сбрасываем текущее нажатие
            self.morse_display.config(text="")  # очищаем морзянку

    def exit_app(self, event):
        self.master.quit()

    def check_keyboard(self):
        self.master.after(100, self.check_keyboard)  # проверка нажатий клавиш

if __name__ == "__main__":
    root = tk.Tk()
    app = MorseApp(root)
    root.mainloop()

