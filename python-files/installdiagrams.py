import psutil
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Настройки графика
fig, ax = plt.subplots()
xdata = []
ydata = []
line, = ax.plot(xdata, ydata, label='Загрузка CPU (%)')
ax.set_ylim(0, 100)
ax.set_xlim(0, 20)  # Показываем последние 20 секунд
ax.set_xlabel('Время (секунды)')
ax.set_ylabel('Загрузка CPU (%)')
ax.legend()
ax.grid()

# Начальное время
start_time = 0

# Функция обновления графика
def update(frame):
    global start_time
    cpu_usage = psutil.cpu_percent(interval=1)  # Получаем загрузку CPU
    current_time = start_time + 1  # Увеличиваем время на 1 секунду
    xdata.append(current_time)
    ydata.append(cpu_usage)
    
    # Обновляем данные на графике
    line.set_data(xdata, ydata)
    
    # Поддерживаем ось X в пределах 20 секунд
    if current_time > 20:
        ax.set_xlim(current_time - 20, current_time)
    
    # Увеличиваем начальное время
    start_time = current_time
    return line,

# Анимация
ani = animation.FuncAnimation(fig, update, blit=True,cache_frame_data=False, interval=50)
# Обновляем каждую секунду

plt.show()
