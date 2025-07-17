import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import TextBox, Button


def lituus_parametric(theta):
    r = a / np.sqrt(theta)
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x, y


fig = plt.figure(figsize=(12, 6))
fig.canvas.manager.set_window_title("Кривая жезл")
fig.subplots_adjust(top=0.85)
ax_cart = fig.add_subplot(121)
ax_polar = fig.add_subplot(122, projection='polar')
plt.subplots_adjust(bottom=0.35)

# Добавляем надпись с формулой
fig.suptitle('Кривая жезл: ' + r"$\rho = \frac{a}{\sqrt{\phi}}$", fontsize=16)  # Здесь можно задать желаемую формулу

# Настройка осей
ax_cart.set_title('Декартова система координат')
ax_cart.set_xlabel('X')
ax_cart.set_ylabel('Y')
ax_cart.grid(True)
ax_cart.set_aspect('equal')

ax_polar.set_title('Полярная система координат')
ax_polar.grid(True)

# Элементы управления - размещаем поля ввода друг под другом
axbox_a = plt.axes([0.2, 0.25, 0.25, 0.05])  # x, y, width, height
a_text_box = TextBox(axbox_a, 'Параметр a:', initial='1.0')
axbox_len = plt.axes([0.6, 0.25, 0.25, 0.05])
len_text_box = TextBox(axbox_len, 'Длина "ручки":', initial='2.0')
axbox_rot = plt.axes([0.2, 0.15, 0.25, 0.05])
rotation_text_box = TextBox(axbox_rot, 'Количество оборотов:', initial='2.0')
axbox_nframe = plt.axes([0.6, 0.15, 0.25, 0.05])
nframe_text_box = TextBox(axbox_nframe, 'Количество кадров:', initial='128')
up_button_ax = plt.axes([0.225, 0.05, 0.2, 0.05])
pause_button_ax = plt.axes([0.625, 0.05, 0.2, 0.05])
update_button = Button(up_button_ax, 'Обновить')
pause_button = Button(pause_button_ax, 'Пауза')

# Инициализация графиков и объекта анимации
line_cart, = ax_cart.plot([], [], 'b-', lw=2)
line_polar, = ax_polar.plot([], [], 'r-', lw=2)
point_cart, = ax_cart.plot([], [], 'bs', markersize=10)
point_polar, = ax_polar.plot([], [], 'ro', markersize=10)
ani = None

# параметры для управления пропорциями графиков и формулой
length_parameter = 2
frame_parameter = 1.1
rotation_parameter = 2
number_of_frames = 128
a = 1
is_paused = 0


def get_valid_len():
    global length_parameter
    try:
        loc_len = float(len_text_box.text)
    except ValueError:
        loc_len = length_parameter
    if loc_len > 0:
        length_parameter = min(loc_len, 100)
    len_text_box.set_val(str(length_parameter))


def get_valid_rot():
    global rotation_parameter
    try:
        loc_rot = float(rotation_text_box.text)
    except ValueError:
        loc_rot = rotation_parameter
    if loc_rot > 0:
        rotation_parameter = min(loc_rot, 1000)
    rotation_text_box.set_val(str(rotation_parameter))


def get_valid_nframe():
    global number_of_frames
    try:
        loc_nframe = int(float(nframe_text_box.text))
    except ValueError:
        loc_nframe = number_of_frames
    if loc_nframe > 0:
        number_of_frames = min(loc_nframe, 10 ** 5)
    nframe_text_box.set_val(str(number_of_frames))


def get_valid_a():
    global a
    try:
        loc_a = float(a_text_box.text)
    except ValueError:
        loc_a = a
    if loc_a != 0:
        a = max(min(loc_a, 10 ** 25), -10 ** 25)
    a_text_box.set_val(str(a))


def get_valid_arggs():
    get_valid_len()
    get_valid_rot()
    get_valid_nframe()
    get_valid_a()


def update_plots():
    theta = np.linspace(0.001, rotation_parameter * np.pi * 2, int(rotation_parameter * 256))
    x, y = lituus_parametric(theta)
    # Декартов график
    line_cart.set_data(x, y)
    ax_cart.set_xlim(max(-length_parameter * abs(a), min(x) * frame_parameter),
                     min(length_parameter * abs(a), max(x) * frame_parameter))
    ax_cart.set_ylim(min(y) * frame_parameter, max(y) * frame_parameter)
    # Полярный график
    current_r = np.sqrt(x ** 2 + y ** 2)
    current_phi = np.arctan2(y, x)
    line_polar.set_data(current_phi, current_r)
    ax_polar.set_ylim(0, min(length_parameter * abs(a), max(current_r)))
    fig.canvas.draw()


def init():
    point_cart.set_data([], [])
    point_polar.set_data([], [])
    return point_cart, point_polar


def animate(i):
    t = (i / number_of_frames) * (rotation_parameter * np.pi * 2) + 0.001

    x, y = lituus_parametric(t)
    # Декартовы координаты
    point_cart.set_data([x], [y])
    # Полярные координаты
    current_r = np.sqrt(x ** 2 + y ** 2)
    current_phi = np.arctan2(y, x)
    point_polar.set_data([current_phi], [current_r])
    return point_cart, point_polar


def pause_play(val=None):
    global is_paused
    if ani is not None:
        if is_paused:
            ani.resume()
            is_paused = 0
            pause_button.label.set_text('Пауза')
        else:
            ani.pause()
            is_paused = 1
            pause_button.label.set_text('Воспр.')
        fig.canvas.draw()


def update_window(val=None):
    global ani, is_paused
    is_paused = 0
    pause_button.label.set_text('Пауза')
    get_valid_arggs()
    update_plots()
    # Останавливаем предыдущую анимацию, если она есть
    if ani is not None:
        ani.event_source.stop()
    # Создаем новую анимацию с новым количеством кадров
    ani = FuncAnimation(fig, animate, cache_frame_data=True,
                        frames=number_of_frames, init_func=init, interval=50, blit=True)
    fig.canvas.draw()  # Перерисовываем фигуру


update_button.on_clicked(update_window)
pause_button.on_clicked(pause_play)

update_window()
plt.show()
