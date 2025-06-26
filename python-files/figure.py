import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.dates import DateFormatter, HourLocator, DayLocator
import os
from datetime import timedelta
import matplotlib
matplotlib.use('Agg')

# Загрузка данных
df = pd.read_excel('meteo.xlsx', sheet_name='Лист1')
df['Дата'] = pd.to_datetime(df['Дата'])

# Получаем первое и последнее время из данных
start_time = df['Дата'].iloc[0]
end_time = df['Дата'].iloc[-1]

# Форматируем даты для названия файла
start_date_str = start_time.strftime('%d.%m')
end_date_str = end_time.strftime('%d.%m')

# Создаем фигуру с 4 субграфиками
fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(14, 12), sharex=False)
plt.subplots_adjust(hspace=0.4, top=0.92, bottom=0.1)

# Функция для сглаживания линий (без scipy, используя полиномиальную аппроксимацию)
def smooth_line(x, y, n_points=300, window=3):
    # Скользящее среднее для небольшого сглаживания
    y_avg = pd.Series(y).rolling(window=window, center=True).mean().fillna(y).values

    # Интерполяция
    x_num = x.view('int64')
    x_new = np.linspace(x_num.min(), x_num.max(), n_points)
    y_smooth = np.interp(x_new, x_num, y_avg)

    return pd.to_datetime(x_new), y_smooth
# 1. График ветра (верхний)
x_smooth, y_smooth = smooth_line(df['Дата'], df['Ветер(м/с)'])
ax1.plot(x_smooth, y_smooth, color='black', linewidth=1.5)
ax1.set_ylabel('Ветер (м/с)', color='black')
ax1.tick_params(axis='y', labelcolor='black')
ax1.set_xlim([start_time, end_time])
wind_max = df['Ветер(м/с)'].max()
ax1.set_ylim(0, wind_max + 5)

# Ветровые зазубрины
u = df['Ветер(м/с)'] * np.sin(np.radians(df['Ветер(град)']))
v = df['Ветер(м/с)'] * np.cos(np.radians(df['Ветер(град)']))
barb_height = df['Ветер(м/с)'] + 0.5
ax1.barbs(df['Дата'], barb_height, u, v,
          length=6, linewidth=1.2, color='red', pivot='middle')


# 2. График температуры
x_smooth, y_smooth = smooth_line(df['Дата'], df['Температура(град.С)'])
ax2.plot(x_smooth, y_smooth, color='blue', linewidth=1.5)
ax2.set_ylabel('Температура (°C)', color='black')
ax2.tick_params(axis='y', labelcolor='black')
ax2.set_xlim([start_time, end_time])

# 3. График давления и осадков
x_smooth, y_smooth = smooth_line(df['Дата'], df['Давление(мм.рт.ст.)'])
ax3.plot(x_smooth, y_smooth, color='green', linewidth=1.5)
ax3.set_ylabel('Давление (мм рт.ст.)', color='black')
ax3.tick_params(axis='y', labelcolor='black')
ax3.set_xlim([start_time, end_time])

# Осадки
ax3b = ax3.twinx()
bar_width = 0.1
ax3b.bar(df['Дата'], df['Осадки(мм/3ч)'], color='blue', alpha=0.7, width=bar_width)
ax3b.set_ylabel('Осадки (мм/3ч)', color='black')
ax3b.tick_params(axis='y', labelcolor='black')
ax3b.set_xlim([start_time, end_time])

# 4. График видимости
bar_width = 0.1
ax4.bar(df['Дата'], df['Видимость(км)'], color='blue', alpha=0.7, width=bar_width)
ax4.set_ylabel('Видимость (км)', color='black')
ax4.tick_params(axis='y', labelcolor='black')
ax4.set_xlim([start_time, end_time])

# Видимость временами
ax4b = ax4.twinx()
ax4b.bar(df['Дата'], df['Видимость(км) временами'], color='red', alpha=0.5, width=bar_width)
ax4b.set_ylabel('Видимость врем. (км)', color='black')
ax4b.tick_params(axis='y', labelcolor='black')
ax4b.set_ylim(ax4.get_ylim())
ax4b.set_xlim([start_time, end_time])

# Настройка формата дат и линий границ дней
hour_formatter = DateFormatter('%H:%M')
day_formatter = DateFormatter('%d.%m')

# Создаем список всех дней в диапазоне данных
all_days = pd.date_range(start_time.floor('D'), end_time.ceil('D'), freq='D')

for ax in [ax1, ax2, ax3, ax4]:
    # Основные деления - каждые 3 часа
    ax.xaxis.set_major_locator(HourLocator(interval=3))
    ax.xaxis.set_major_formatter(hour_formatter)
    ax.grid(True, linestyle='--', alpha=0.5)

    # Добавляем вертикальные линии на границах дней (00:00)
    for day in all_days:
        ax.axvline(x=day, color='gray', linestyle=':', linewidth=1, alpha=0.7)

# Настройка подписей дат вверху (для ax1)
ax1.xaxis.set_minor_locator(DayLocator())
ax1.xaxis.set_minor_formatter(day_formatter)
ax1.tick_params(which='minor', axis='x', bottom=False, labelbottom=False,
                top=True, labeltop=True, labelsize=9, pad=10)

# Добавляем подписи дат над серыми линиями
for day in all_days:
    if start_time <= day <= end_time:
        ax1.text(day, ax1.get_ylim()[1] + 1, day.strftime('%d.%m'),
                 ha='center', va='bottom', fontsize=9, color='black')

# Настройка подписей дат внизу (для ax4)
ax4.xaxis.set_minor_locator(DayLocator())
ax4.xaxis.set_minor_formatter(day_formatter)
ax4.tick_params(which='minor', axis='x', bottom=True, labelbottom=True,
                top=False, labeltop=False, labelsize=9, pad=10)
# Поворачиваем подписи дат для лучшей читаемости
for label in ax4.get_xticklabels(minor=True):
    label.set_rotation(45)
    label.set_horizontalalignment('right')

# Общий заголовок
fig.suptitle(f'Район о. Колгуев и Поморский пролив, Баренцево море\nПрогноз с {start_date_str} по {end_date_str}',
             y=0.98, fontsize=14, color='black')

plt.tight_layout()

# Сохраняем график с датами в названии
script_dir = os.path.dirname(os.path.abspath(__file__))
save_path = os.path.join(script_dir, f'Прогноз с {start_date_str} по {end_date_str}.png')
plt.savefig(save_path, dpi=300, bbox_inches='tight')