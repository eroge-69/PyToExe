import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

fig, ax = plt.subplots(figsize=(10, 5))
ax.set_xlim(0, 10)
ax.set_ylim(0, 2)
ax.axis('off')

# Начальные позиции символов
plus_pos = [2, 1]
minus_pos = [8, 1]

plus = ax.text(plus_pos[0], plus_pos[1], '+', fontsize=30, ha='center', va='center', color='blue')
minus = ax.text(minus_pos[0], minus_pos[1], '-', fontsize=30, ha='center', va='center', color='red')

def update(frame):
    # Уменьшаем расстояние между символами
    distance = minus_pos[0] - plus_pos[0]
    step = distance * 0.02
    
    plus_pos[0] += step
    minus_pos[0] -= step
    
    # Обновляем позиции
    plus.set_position((plus_pos[0], plus_pos[1]))
    minus.set_position((minus_pos[0], minus_pos[1]))
    
    # Когда они близко, меняем цвет
    if distance < 1.5:
        plus.set_color('purple')
        minus.set_color('purple')
    
    return plus, minus

animation = FuncAnimation(fig, update, frames=100, interval=50, blit=True)
plt.show()