import os
import cv2
from tkinter import Tk
from tkinter.filedialog import askdirectory

print("Выберите папку для сохранения снимков...")
root = Tk()

root.withdraw()
save_dir = askdirectory(title="Выберите папку для сохранения снимков")

if not save_dir:
    print("Папка не выбрана. Выход из программы")
    exit()

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Не удалось открыть камеру")
    exit()

snapshot_count = 0
print("Нажмите 's' для снимка, 'q' - для выхода.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Не удалось получить кадр")
        break

    cv2.imshow("Камера", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):
        filename = os.path.join(save_dir, f"snapshot_{snapshot_count:03}.png")
        cv2.imwrite(filename, frame)
        print(f"Снимок сохранен: {filename}")
        snapshot_count += 1

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

    
