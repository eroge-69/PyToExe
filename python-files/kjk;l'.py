# calc_ctk.py
import customtkinter as ctk
import math

ctk.set_appearance_mode("Dark")   # "System", "Light", "Dark"
ctk.set_default_color_theme("blue")

class Calculator(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Калькулятор")
        self.geometry("320x420")
        self.resizable(False, False)

        self.expression = ""
        self.text_var = ctk.StringVar()

        # --- Экран ---
        self.screen = ctk.CTkEntry(
            self,
            textvariable=self.text_var,
            font=("Arial", 40),
            justify="right",
            state="readonly",
            corner_radius=10,
            height=70,
        )
        self.screen.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

        # --- Кнопки ---
        buttons = [
            ("C", 1, 0), ("⌫", 1, 1), ("(", 1, 2), (")", 1, 3),
            ("7", 2, 0), ("8", 2, 1), ("9", 2, 2), ("/", 2, 3),
            ("4", 3, 0), ("5", 3, 1), ("6", 3, 2), ("*", 3, 3),
            ("1", 4, 0), ("2", 4, 1), ("3", 4, 2), ("-", 4, 3),
            ("0", 5, 0), (".", 5, 1), ("=", 5, 2), ("+", 5, 3),
        ]

        for (text, row, col) in buttons:
            w = 75 if text != "=" else 155      # кнопка «=» в два раза шире
            ctk.CTkButton(
                self,
                text=text,
                width=w,
                height=55,
                font=("Arial", 24),
                corner_radius=10,
                command=lambda t=text: self.on_click(t),
            ).grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        # горячие клавиши
        self.bind("<Key>", self.key_pressed)
        self.bind("<Return>", lambda e: self.on_click("="))
        self.bind("<BackSpace>", lambda e: self.on_click("⌫"))
        self.focus_set()

    # --- Логика ---
    def on_click(self, char):
        if char == "C":
            self.expression = ""
        elif char == "⌫":
            self.expression = self.expression[:-1]
        elif char == "=":
            try:
                # безопасный eval: разрешены только цифры и +-*/(). math.функции
                safe_dict = {"__builtins__": None}
                safe_dict.update(vars(math))   # sin, cos, sqrt и т.д.
                self.expression = str(eval(self.expression, safe_dict, {}))
            except Exception:
                self.expression = "Ошибка"
        else:
            # если на экране «Ошибка», начинаем с чистого листа
            if self.expression == "Ошибка":
                self.expression = ""
            self.expression += str(char)

        self.text_var.set(self.expression)

    def key_pressed(self, event):
        allowed = "0123456789+-*/()."
        if event.char in allowed:
            self.on_click(event.char)

if __name__ == "__main__":
    app = Calculator()
    app.mainloop()