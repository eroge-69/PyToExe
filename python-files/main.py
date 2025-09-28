from tkinter import *
from tkinter import ttk
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw

def slowmo():
    print("1")

def fast():
    print("2")

class ImageEditor(tk.Frame):
    def __init__(self, parent, path_to_image):
        super().__init__(parent)
        self.parent = parent
        self.pack(fill=tk.BOTH, expand=True)

        # Открываем оригинальное изображение
        self.original_image = Image.open(path_to_image)
        self.img_tk = ImageTk.PhotoImage(self.original_image)

        # Канва для отображения изображения
        self.canvas = tk.Canvas(self, width=self.img_tk.width(), height=self.img_tk.height())
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img_tk)

        # Фигура, которую хотим перемещать
        self.shape_id = None
        self.selected_shape = None
        self.draw_circle_at_point(100, 100)  # Исходная позиция круга

        # Свяжем события с методами для взаимодействия
        self.canvas.bind('<Button-1>', self.select_shape)
        self.canvas.bind('<B1-Motion>', self.move_shape)
        self.canvas.bind('<ButtonRelease-1>', self.release_shape)

    def draw_circle_at_point(self, x, y):
        radius = 50
        shape_coords = (x-radius, y-radius, x+radius, y+radius)
        self.shape_id = self.canvas.create_oval(*shape_coords, outline='black', fill='yellow')

    def select_shape(self, event):
        items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        if len(items) > 0 and items[0] == self.shape_id:
            self.selected_shape = self.shape_id

    def move_shape(self, event):
        if self.selected_shape:
            coords = self.canvas.coords(self.selected_shape)
            center_x = (coords[0]+coords[2])/2
            center_y = (coords[1]+coords[3])/2
            delta_x = event.x - center_x
            delta_y = event.y - center_y
            self.canvas.move(self.selected_shape, delta_x, delta_y)

    def release_shape(self, _):
        self.selected_shape = None

class DraggableSlider:
    def __init__(self, master, height=200, width=20, initial_value=0.5, command=None):
        self.master = master
        self.width = width
        self.height = height
        self.value = initial_value  # Значение в диапазоне [0.0, 1.0]
        self.command = command

        self.canvas = tk.Canvas(master, width=width, height=height, bg="lightgray", highlightthickness=0)
        self.canvas.pack()

        self.slider_height = 40  # Высота ручки ползунка
        self.slider_y = self.value * (height - self.slider_height)  # Начальное положение ручки

        self.slider = self.canvas.create_rectangle(0, self.slider_y, width, self.slider_y + self.slider_height,
                                                  fill="black", tags="slider")

        self.label = tk.Label(master, text=f"{self.value * 100:.2f}%", font=('Arial', 12))
        self.label.pack(padx=10, pady=10)

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<B1-Motion>", self.on_drag)

        self.dragging = False

    def on_press(self, event):
        # Проверяем, что нажали на ручку ползунка
        item = self.canvas.find_closest(event.x, event.y)
        if "slider" in self.canvas.gettags(item):
            self.dragging = True
            self.start_y = event.y  # Запоминаем начальную координату

    def on_release(self, event):
        self.dragging = False

    def on_drag(self, event):
        if self.dragging:
            dy = event.y - self.start_y
            self.start_y = event.y
            self.move_slider(dy)

    def move_slider(self, dy):
        # Получаем текущие координаты ручки
        x1, y1, x2, y2 = self.canvas.coords(self.slider)

        # Рассчитываем новое положение
        new_y = y1 + dy

        # Ограничиваем перемещение в пределах холста
        if new_y < 0:
            new_y = 0
        elif new_y > self.height - self.slider_height:
            new_y = self.height - self.slider_height

        # Перемещаем ручку
        self.canvas.move(self.slider, 0, new_y - y1)

        # Обновляем значение
        self.value = (self.height - new_y - self.slider_height) / (self.height - self.slider_height)
        self.value = max(0.0, min(1.0, self.value))  # Ensure value is within [0.0, 1.0]

        self.label.config(text=f"{self.value * 100:.2f}%")

        # Вызываем callback-функцию (если есть)
        if self.command:
            self.command(self.value)

    def get_value(self):
        return self.value

if __name__ == "__main__":

    root = Tk()
    root.title("Топливная система АИ-25 ТЛ")
    right_frame = Frame(root)
    right_frame.pack(side=RIGHT, padx=10)  # Place the right frame on the right side

    knopka1 = ttk.Button(right_frame, text="Медлено", command=slowmo)
    knopka1.pack(pady=5)  # Add some vertical padding

    knopka2 = ttk.Button(right_frame, text="Быстро", command=fast)
    knopka2.pack(pady=5)  # Add some vertical padding


    def slider_changed(value):
        print(f"Slider value: {value}")

    slider = DraggableSlider(right_frame, height=250, width=60, initial_value=0.7, command=slider_changed)
    slider.canvas.pack(pady=5)
    slider.label.pack(pady=5)

    # Create ImageEditor instance after right_frame is created
    editor = ImageEditor(root, 'fcbc57f9-fc1e-42bc-9985-5d11ea916ba1.png')

    # Place the ImageEditor canvas on the left
    editor.canvas.pack(side=LEFT, fill=BOTH, expand=True)

    root.mainloop()