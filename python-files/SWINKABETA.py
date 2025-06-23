import tkinter as tk
from tkinter import font, messagebox

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, radius=20, **kwargs):
        super().__init__(parent, **kwargs)
        self.command = command
        self.radius = radius
        self.text = text

        self.bind("<Button-1>", self.on_click)
        self.bind("<Configure>", self.on_configure)  # Обработчик изменения размеров

        self.draw_button()  # Нарисовать кнопку при инициализации

    def draw_button(self):
        self.delete("all")  # Удалить предыдущие компоненты
        width = self.winfo_width()
        height = self.winfo_height()

        # Draw rectangle for the center part
        self.create_rectangle(self.radius, 0, width - self.radius, height, outline="", fill="#4CAF50")  # Основной прямоугольник

        # Draw the arcs for the corners
        self.create_arc(0, 0, self.radius * 2, self.radius * 2, start=90, extent=90, outline="", fill="#4CAF50")  # Верхний левый угол
        self.create_arc(0, height - self.radius * 2, self.radius * 2, height, start=180, extent=90, outline="", fill="#4CAF50")  # Нижний левый угол
        self.create_arc(width - self.radius * 2, 0, width, self.radius * 2, start=0, extent=90, outline="", fill="#4CAF50")  # Верхний правый угол
        self.create_arc(width - self.radius * 2, height - self.radius * 2, width, height, start=270, extent=90, outline="", fill="#4CAF50")  # Нижний правый угол

        # Fill the center sides with the same color
        self.create_rectangle(0, self.radius, self.radius, height - self.radius, outline="", fill="#4CAF50")  # Левая серединная часть
        self.create_rectangle(width - self.radius, self.radius, width, height - self.radius, outline="", fill="#4CAF50")  # Правая серединная часть
    
        # Draw the text in the center
        self.text_id = self.create_text(width / 2, height / 2, text=self.text, fill="white", font=("Helvetica", 20, "bold"))

    def on_click(self, event):
        if self.command:
            self.command()

    def on_configure(self, event):
        self.draw_button()  # Перерисовать кнопку при изменении размера

class SvinkaClient(tk.Tk):
    def __init__(self):
        super().__init__()

        self.geometry("400x300")
        self.resizable(False, False)
        self.title("SvinkaClient")
        
        custom_font = font.Font(family="Helvetica", size=24, weight="bold")

        self.label = tk.Label(self, text="SvinkaClient", font=custom_font)
        self.label.pack(pady=20)
        
        # Учитываем радиус для кнопок
        self.start_button = RoundedButton(self, text="СТАРТ", command=self.show_instructions, radius=20, width=200, height=50)
        self.start_button.pack(pady=(0, 10))

        self.developer_button = RoundedButton(self, text="DEVELOPER", command=self.show_developer_info, radius=20, width=200, height=50)
        self.developer_button.pack(pady=10)

    def show_instructions(self):
        instructions = (
            "Нажмите:\n"
            "1 - чтобы бот нажимал W/A/S/D\n"
            "2 - чтобы бот открывал телефон\n"
            "3 - чтобы бот ел вашу еду (еду надо поставить на букву Z)"
        )
        messagebox.showinfo("Инструкции", instructions)
    
    def show_developer_info(self):
        developer_info = (
            "Developer: Coban\n"
            "Project name: SvinkaClient\n"
            "Version: 1.0 (beta)"
        )
        messagebox.showinfo("INFO", developer_info)

if __name__ == "__main__":
    app = SvinkaClient()
    app.mainloop()


