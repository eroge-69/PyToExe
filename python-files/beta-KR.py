import tkinter as tk
from tkinter import Tk, Label, Frame, Button, messagebox
import os
import psutil
import pyautogui
import pygetwindow as gw
import shutil
import subprocess
import time
import zipfile

a = os.path.expanduser("~")
b = os.path.join(a, 'Desktop', 'tdata')
c = os.path.join(a, 'Desktop', 'Выгрузка')
d = os.path.join(a, 'Desktop', 'tg')
e = [os.path.join(d, f'port{i}') for i in range(1, 11)]

def f1(p):
    if not os.path.exists(p):
        os.makedirs(p)
        print(f"Папка {p} была создана.")
    else:
        print(f"Папка {p} уже существует.")

def f2(p):
    return [os.path.join(p, _n) for _n in os.listdir(p) if os.path.isdir(os.path.join(p, _n))]

def f3():
    _1 = 10
    _2 = [f for f in os.listdir(b) if f.endswith('.zip')]
    if not _2:
        print(f'В {b} нет zip-архивов.')
        return
    _3 = min(_1, len(_2))
    for _4 in range(_3):
        _5 = os.path.join(b, _2[_4])
        _6 = os.path.join(b, f'folder{_4 + 1}')
        f1(_6)
        try:
            with zipfile.ZipFile(_5, 'r') as _7:
                _7.extractall(_6)
            print(f'Архив {_5} успешно распакован в {_6}.')
        except Exception as _8:
            print(f'Ошибка при распаковке архива {_5}: {_8}')

def f4():
    _1 = 10
    if not os.path.exists(b):
        print(f'Основная папка {b} не существует.')
        return
    _2 = f2(b)
    if not _2:
        print(f'В {b} нет подпапок.')
        return
    _3 = min(_1, len(_2))
    for _4 in range(_3):
        _5 = os.path.join(_2[_4], 'tdata')
        _6 = e[_4]
        if os.path.exists(_5):
            try:
                f1(_6)
                shutil.copytree(_5, os.path.join(_6, 'tdata'), dirs_exist_ok=True)
                print(f'Папка tdata из {_5} успешно скопирована в {_6}.')
            except Exception as _7:
                print(f'Ошибка при копировании папки tdata: {_7}')

def f5():
    for _1 in e:
        try:
            for _2 in os.listdir(_1):
                _3 = os.path.join(_1, _2)
                if os.path.isfile(_3) and _2.lower() == 'telegram.exe':
                    continue
                if os.path.isdir(_3):
                    shutil.rmtree(_3)
                    print(f"Директория {_3} успешно удалена.")
                else:
                    os.remove(_3)
                    print(f"Файл {_3} успешно удален.")
        except FileNotFoundError:
            print(f"Папка {_1} не найдена. Пропускаем.")
        except Exception as _4:
            print(f'Ошибка при очистке папки {_1}: {_4}')

def f6():
    try:
        shutil.rmtree(b)
        os.makedirs(b)
        print(f'Папка tdata по пути {b} успешно очищена.')
    except Exception as _1:
        print(f'Ошибка при очистке папки tdata: {_1}')

def f7():
    try:
        shutil.rmtree(c)
        os.makedirs(c)
        print(f'Папка выгрузки по пути {c} успешно очищена.')
    except Exception as _1:
        print(f'Ошибка при очистке папки выгрузки: {_1}')

def f8():
    for _1 in e:
        _2 = os.path.join(_1, 'tdata')
        if not os.path.exists(_2):
            if not messagebox.askyesno("tdata не загружен", f"В папке {_1} нет папки tdata. Продолжить запуск Telegram.exe?"):
                print(f'Запуск Telegram.exe в {_1} отменен.')
                continue
        try:
            _3 = subprocess.Popen([os.path.join(_1, 'Telegram.exe')], shell=True)
            _3.pid
            print(f'Telegram.exe в {_1} успешно запущен.')
        except FileNotFoundError:
            print(f'Файл Telegram.exe в {_1} не найден.')
        except Exception as _4:
            print(f'Ошибка при запуске Telegram.exe в {_1}: {_4}')

def f9():
    _1, _2 = 5, 2
    _3, _4 = pyautogui.size()
    _5 = int(_4 * 0.037)
    _4 -= _5
    _6 = _3 // _1
    _7 = _4 // _2
    _8 = gw.getWindowsWithTitle('Telegram')
    for _9, _10 in enumerate(_8):
        try:
            if _10.isMaximized:
                _10.restore()
            _10.resizeTo(_6, _7)
            _11 = (_9 % _1) * _6
            _12 = (_9 // _1) * _7
            _10.moveTo(_11, _12)
            print(f"Окно {_9+1} перемещено в x={_11}, y={_12}.")
        except IndexError:
            print(f'Окно Telegram с индексом {_9} не найдено.')
        except Exception as _13:
            print(f'Ошибка при расположении окон Telegram: {_13}')

def f10():
    _1 = 10
    _2 = f2(b)
    if not _2:
        print(f'В {b} нет подпапок.')
        return
    _3 = min(_1, len(_2))
    for _4 in range(_3):
        _5 = _2[_4]
        _6 = e[_4]
        try:
            f1(_6)
            shutil.copytree(_5, os.path.join(_6, 'tdata'), dirs_exist_ok=True)
            print(f'Подпапка {_5} успешно скопирована в {_6}.')
        except Exception as _7:
            print(f'Ошибка при обработке папки {_5}: {_7}')

def f11():
    f1(c)
    _1 = {"D877F783D5D3EF8C", "key_datas", "D877F783D5D3EF8Cs", "maps"}
    for _2 in e:
        _3 = os.path.join(_2, 'tdata')
        if not os.path.exists(_3):
            print(f"В {_2} нет папки tdata. Пропускаем.")
            continue
        print(f"Сжатие данных в {_3}...")
        for _4, _5, _6 in os.walk(_3, topdown=False):
            for _7 in _6:
                if _7 not in _1:
                    _8 = os.path.join(_4, _7)
                    os.remove(_8)
                    print(f"Файл {_8} удален.")
            for _9 in _5:
                if _9 not in _1:
                    _10 = os.path.join(_4, _9)
                    shutil.rmtree(_10)
                    print(f"Папка {_10} удалена.")
        print(f"Сжатие данных в {_3} завершено.")
        try:
            _11 = 1
            while os.path.exists(os.path.join(c, str(_11), 'tdata')):
                _11 += 1
            _12 = os.path.join(c, str(_11))
            os.makedirs(_12, exist_ok=True)
            shutil.copytree(_3, os.path.join(_12, 'tdata'), dirs_exist_ok=True)
            print(f"Папка tdata из {_2} успешно скопирована в {_12}.")
        except Exception as _13:
            print(f"Ошибка при копировании папки tdata из {_2}: {_13}")

def f12():
    if messagebox.askyesno("Подтверждение", "Вы хотите очистить папку tdata?"):
        f6()

def f13():
    if messagebox.askyesno("Подтверждение", "Вы хотите очистить папку выгрузки?"):
        f7()

def f14():
    for _1 in psutil.process_iter(['pid', 'name']):
        if _1.info['name'] == 'Telegram.exe':
            _1.terminate()

def f15():
    if not messagebox.askyesno("Подтверждение", "Вы хотите выйти из аккаунтов?"):
        print("Пользователь отменил операцию.")
        return
    for _1 in e:
        try:
            for _2 in os.listdir(_1):
                _3 = os.path.join(_1, _2)
                if os.path.isfile(_3) and _2.lower() == 'telegram.exe':
                    continue
                if os.path.isdir(_3):
                    shutil.rmtree(_3)
                    print(f"Директория {_3} успешно удалена.")
                else:
                    os.remove(_3)
                    print(f"Файл {_3} успешно удален.")
        except FileNotFoundError:
            print(f"Папка {_1} не найдена. Пропускаем.")
        except Exception as _4:
            print(f"Ошибка при очистке папки {_1}: {_4}")
    print("Выход из аккаунтов завершен.")


def f_fix_structure():
    root_dir = b  # т.е. Desktop/tdata

    for folder_name in os.listdir(root_dir):
        folder_path = os.path.join(root_dir, folder_name)

        if not os.path.isdir(folder_path):
            continue

        found_tdata = False

        for inner_name in os.listdir(folder_path):
            inner_path = os.path.join(folder_path, inner_name)
            if os.path.isdir(inner_path):
                tdata_path = os.path.join(inner_path, "tdata")
                if os.path.isdir(tdata_path):
                    dst_path = os.path.join(folder_path, "tdata")
                    if not os.path.exists(dst_path):
                        shutil.move(tdata_path, dst_path)
                        print(f"[+] Перемещена tdata для: {folder_name}")
                    else:
                        print(f"[!] tdata уже существует в {folder_name}, пропущено.")

                    for item in os.listdir(inner_path):
                        if item == "tdata":
                            continue
                        src_item = os.path.join(inner_path, item)
                        dst_item = os.path.join(folder_path, item)
                        if not os.path.exists(dst_item):
                            shutil.move(src_item, dst_item)

                    shutil.rmtree(inner_path)
                    found_tdata = True
                    break

        if not found_tdata:
            print(f"[-] В папке {folder_name} не найдено tdata.")

    print("\n✅ Обработка завершена.")


def f16():
    _1 = [
    [
        {"Распаковать tdata": f3},
        {"Исправить структуру tdata": f_fix_structure},
        {"Переместить и переименовать tdata": f10},
        {"Переместить tdata": f4}
    ],
        [
            {"Запустить Telegram": f8},
            {"Переместить Telegram": f9},
        ],
        [
            {"Закрыть Telegram": f14},
            {"Сохранить tdata": f11},
        ],
        [
            {"Выйти из аккаунтов": f15},
            {"Очистить папку tdata": f12},
            {"Очистить папку выгрузки": f13}
        ]
    ]
    r = Tk()
    r.protocol("WM_DELETE_WINDOW", r.destroy)
    r.title('Управление')
    r.geometry('790x340')
    r.resizable(False, False)
    r['bg'] = "black"
    Label(r, text='Выберите задачу', foreground="white", background="black", font=16).pack(pady=12)
    _2 = Frame(r, bg="black")
    _2.place(relx=0.05, relheight=0.90, relwidth=0.90)
    for _3, _4 in enumerate(_1):
        for _5, _6 in enumerate(_4):
            _7, _8 = _6.popitem()
            Button(_2, text=_7, command=_8, width=20).grid(row=_3, column=_5, padx=5, pady=5)
    return r

if __name__ == '__main__':
    _r = f16()
    _r.mainloop()