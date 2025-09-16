import matplotlib.pyplot as plt
import numpy as np

# Данные о количестве продаж по месяцам
months = ['Янв', 'Фев', 'Март', 'Апр', 'Май', 'Июнь', 'Июль', 'Авг']
sales_2024 = [770, 680, 559, 465, 550, 693, 889, 1037]
sales_2025 = [739, 884, 705, 434, 510, 575, 511, 432]  # в тысячах единиц

plt.figure(figsize=(12, 6))
plt.plot(months, sales_2024[:8], marker='o', label='2024 год', linewidth=2)
plt.plot(months, sales_2025[:8], marker='s', label='2025 год', linewidth=2)
plt.title('Динамика продаж по месяцам (количество единиц)')
plt.xlabel('Месяцы')
plt.ylabel('Количество продаж, шт')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()