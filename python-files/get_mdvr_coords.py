
import pyautogui
import time

labels = [
    "Поле НАЧАЛО",
    "Поле КОНЕЦ",
    "Кнопка 'Просм. по времени'",
    "Верхний левый угол видео",
    "Нижний правый угол видео"
]

coords = {}

print("Программа для захвата координат MDVR-плеера.\n")
print("Наводите мышь на указанные элементы, и нажимайте Enter.\n")

for label in labels:
    input(f"➡ Наведите мышку на: {label}, затем нажмите Enter...")
    x, y = pyautogui.position()
    coords[label] = (x, y)
    print(f"{label}: X={x}, Y={y}")

# Сохраняем координаты в файл
with open("coords.txt", "w") as f:
    for label, (x, y) in coords.items():
        f.write(f"{label}: {x},{y}\n")

print("\n✅ Координаты сохранены в 'coords.txt'. Закройте окно.")
input("Нажмите Enter для выхода...")
