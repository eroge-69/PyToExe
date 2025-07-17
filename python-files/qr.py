import os
import configparser
import segno
import tkinter as tk
from tkinter import messagebox
import cv2
from pyzbar.pyzbar import decode
import setuptools

root = tk.Tk()
root.withdraw()


#current_directory = os.getcwd()
path_to_check = "_working"  # Замените на нужный вам путь

if not os.path.isdir(path_to_check):
    messagebox.showwarning("ERROR", "Отсутствует папка _working !!!")
    sys.exit()
    root.destroy()
    

config = configparser.ConfigParser()
config.read('_working/MyIni.ini')
st= config.get('QR', 'Str')
qrcode = segno.make_qr(st)
qrcode.save("_working/qr.png",scale=3) 

def read_qr_code(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Ошибка: Не удалось загрузить изображение по пути {image_path}")
        return None

    decoded_objects = decode(img)
    if not decoded_objects:
        print("QR-код не найден.")
        return None

    data = [obj.data.decode('utf-8') for obj in decoded_objects]
    return data

# Пример использования
image_path = '_working/qr.png'  # Замените на путь к вашему изображению
qr_data = str(read_qr_code(image_path ))

qr_data_1=qr_data.replace("[", "").replace("]", "")
qr_data=qr_data_1.replace("'", "").replace("'", "")

with open("_working/qr.txt", "w") as file:
  file.write(qr_data)

g_new = input("Нажмите ENTER")
