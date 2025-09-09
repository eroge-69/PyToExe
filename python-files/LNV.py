print('Программа расчета очередности навески лопастей несущего винта \nвертолета Ми-8 и его модификаций')
lop1 = float(input('Вес 1 лопасти: '))
lop2 = float(input('Вес 2 лопасти: '))
lop3 = float(input('Вес 3 лопасти: '))
lop4 = float(input('Вес 4 лопасти: '))
lop5 = float(input('Вес 5 лопасти: '))

# Расчет отклонения от «идеальной лопасти»
g1 = 0.81*(lop2+lop3)-0.31*(lop4+lop5)
otkl1 = lop1-g1
g2 = 0.81*(lop1+lop4)-0.31*(lop3+lop5)
otkl2 = lop2-g2
g3 = 0.81*(lop1+lop5)-0.31*(lop2+lop4)
otkl3 = lop3-g3
g4 = 0.81*(lop2+lop5)-0.31*(lop1+lop3)
otkl4 = lop4-g4
g5 = 0.81*(lop3+lop4)-0.31*(lop1+lop2)
otkl5= lop5-g5

print('-'* 30)
lop = [
    {'weight': lop1, 'otklonenie': otkl1, 'number': 1},
    {'weight': lop2, 'otklonenie': otkl2, 'number': 2},
    {'weight': lop3, 'otklonenie': otkl3, 'number': 3},
    {'weight': lop4, 'otklonenie': otkl4, 'number': 4},
    {'weight': lop5, 'otklonenie': otkl5, 'number': 5}
]    

# Сортировка
sortirovka = sorted(lop, key=lambda x: x['otklonenie'])

# Распределение по рукавам
raspr = {
    'Рукав 1': sortirovka[0],
    'Рукав 2': sortirovka[2],
    'Рукав 3': sortirovka[4],
    'Рукав 4': sortirovka[3],
    'Рукав 5': sortirovka[1]
}

print('Оптимальная схема монтажа лопастей: ')
for hub, alop in raspr.items():
    dev = alop['otklonenie']
    sign = '+' if dev >= 0 else ''
    print(f"{hub}: Лопасть №{alop['number']} Вес = {alop['weight']} кг, Отклонение = {sign}{round(dev, 4)} кг")

# Графическая часть
import matplotlib.pyplot as plt
import numpy as np

# Создаем фигуру и полярную подложку
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
ax.set_theta_zero_location('N')
ax.set_theta_direction('clockwise')

# Углы для рукавов (в радианах)
angles = np.radians([0, 72, 144, 216, 288])
hub_names = ['Рукав 1', 'Рукав 2', 'Рукав 3', 'Рукав 4', 'Рукав 5']

# Цвета для лопастей
colors = ['red', 'green', 'blue', 'orange', 'purple']

# Отображаем схему расположения
for i, (hub, alop) in enumerate(raspr.items()):
    angle = angles[i]
    dev = alop['otklonenie']
    weight = alop['weight']
    number = alop['number']
    
    # Отображаем рукав
    ax.plot(angle, 1, 'o', markersize=20, color=colors[i])
    ax.text(angle, 1.1, f"{hub}\nЛопасть №{number}\nВес: {weight} кг\nОткл: {dev:.2f} кг", 
            ha='center', va='center', fontsize=8, bbox=dict(facecolor='white', alpha=0.7))

# Настраиваем внешний вид
ax.set_ylim(0, 1.5)
ax.set_yticklabels([])
ax.grid(True)
ax.set_title('Схема расположения лопастей по рукавам\n', fontsize=14)

plt.show()