from ast import Break
from cProfile import label
from re import S
from sys import maxsize
import tkinter as tk
from tracemalloc import stop
from turtle import width
from typing import Self
import keyboard
import PySimpleGUI as psg
import pyautogui as pag
from time import sleep
import mouse
from tkinter import *
from tkinter import ttk
from tkinter import Tk, Button, Toplevel
from tkinter import messagebox

true_false = True
win = None
n = 0
z = 0
g = 0

# Глобальные переменные для координат
x = [0] * 100
y = [0] * 100
q = [0] * 100

# Современная цветовая схема
BG_COLOR = '#2C3E50'
ACCENT_COLOR = '#3498DB'
BUTTON_COLOR = '#2980B9'
TEXT_COLOR = '#ECF0F1'
ENTRY_COLOR = '#34495E'
HIGHLIGHT_COLOR = '#16A085'
WARNING_COLOR = '#E74C3C'
SUCCESS_COLOR = '#27AE60'
ACTIVE_COLOR = '#E67E22'
EDIT_COLOR = '#F39C12'


def true_false_revers():
    global true_false
    true_false = False
    if win:
        win.destroy()


def close_clicked_res():
    global true_false
    true_false = False
    if win:
        win.destroy()


def restart_clicked():
    global true_false
    true_false = True
    if win:
        win.destroy()
    clicker()


def on_closing():
    if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
        global true_false
        true_false = False
        if win:
            win.destroy()


def muve():
    global x, y, n, z, g
    sleep(3)
    for i in range(n):
        w = 0
        for q_val in range(g):
            w += 1
            mouse.move(x[w], y[w], duration=0.5)
            mouse.click('left')
        sleep(z)


def clicker():
    global true_false, win, x, y, q

    true_false = True

    win = tk.Tk()
    win.title("Auto Click Manager")
    win.geometry('500x600')
    win.configure(bg=BG_COLOR)
    win.resizable(width=False, height=False)
    win.protocol("WM_DELETE_WINDOW", on_closing)

    # Главный фрейм
    main_frame = tk.Frame(win, bg=BG_COLOR, padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Заголовок
    header_label = tk.Label(main_frame, text="Auto Click",
                            bg=BG_COLOR, fg=TEXT_COLOR,
                            font=('Arial', 18, 'bold'))
    header_label.grid(row=0, column=0, columnspan=8, pady=(0, 20))

    # Переменная для отслеживания активной точки
    active_point = None

    # Метки для отображения координат
    coord_labels = []
    for i in range(1, 6):
        coord_labels.append([None, None])

    # Функции для установки точек
    def set_point_1():
        nonlocal active_point
        active_point = 1
        status_label.config(text="Наведите курсор и нажмите клавишу '1' для установки точки 1", fg=ACTIVE_COLOR)
        point_buttons[0].config(bg=ACTIVE_COLOR)
        # Временно активируем горячую клавишу
        keyboard.add_hotkey('1', checkpos1, suppress=True)

    def set_point_2():
        nonlocal active_point
        active_point = 2
        status_label.config(text="Наведите курсор и нажмите клавишу '2' для установки точки 2", fg=ACTIVE_COLOR)
        point_buttons[1].config(bg=ACTIVE_COLOR)
        keyboard.add_hotkey('2', checkpos2, suppress=True)

    def set_point_3():
        nonlocal active_point
        active_point = 3
        status_label.config(text="Наведите курсор и нажмите клавишу '3' для установки точки 3", fg=ACTIVE_COLOR)
        point_buttons[2].config(bg=ACTIVE_COLOR)
        keyboard.add_hotkey('3', checkpos3, suppress=True)

    def set_point_4():
        nonlocal active_point
        active_point = 4
        status_label.config(text="Наведите курсор и нажмите клавишу '4' для установки точки 4", fg=ACTIVE_COLOR)
        point_buttons[3].config(bg=ACTIVE_COLOR)
        keyboard.add_hotkey('4', checkpos4, suppress=True)

    def set_point_5():
        nonlocal active_point
        active_point = 5
        status_label.config(text="Наведите курсор и нажмите клавишу '5' для установки точки 5", fg=ACTIVE_COLOR)
        point_buttons[4].config(bg=ACTIVE_COLOR)
        keyboard.add_hotkey('5', checkpos5, suppress=True)

    def checkpos1():
        nonlocal active_point
        if active_point == 1:
            x[1], y[1] = pag.position()
            if coord_labels[0][0] and coord_labels[0][1]:
                coord_labels[0][0].config(text=f"X: {x[1]}", bg=SUCCESS_COLOR)
                coord_labels[0][1].config(text=f"Y: {y[1]}", bg=SUCCESS_COLOR)
            q[1] = 1  # Устанавливаем флаг, что точка задана
            status_label.config(text=f"Точка 1 установлена: {x[1]}, {y[1]}", fg=SUCCESS_COLOR)
            point_buttons[0].config(bg=EDIT_COLOR, text="1 ✏️")
            active_point = None
            # Удаляем временную горячую клавишу
            keyboard.remove_hotkey('1')

    def checkpos2():
        nonlocal active_point
        if active_point == 2:
            x[2], y[2] = pag.position()
            if coord_labels[1][0] and coord_labels[1][1]:
                coord_labels[1][0].config(text=f"X: {x[2]}", bg=SUCCESS_COLOR)
                coord_labels[1][1].config(text=f"Y: {y[2]}", bg=SUCCESS_COLOR)
            q[2] = 1
            status_label.config(text=f"Точка 2 установлена: {x[2]}, {y[2]}", fg=SUCCESS_COLOR)
            point_buttons[1].config(bg=EDIT_COLOR, text="2 ✏️")
            active_point = None
            keyboard.remove_hotkey('2')

    def checkpos3():
        nonlocal active_point
        if active_point == 3:
            x[3], y[3] = pag.position()
            if coord_labels[2][0] and coord_labels[2][1]:
                coord_labels[2][0].config(text=f"X: {x[3]}", bg=SUCCESS_COLOR)
                coord_labels[2][1].config(text=f"Y: {y[3]}", bg=SUCCESS_COLOR)
            q[3] = 1
            status_label.config(text=f"Точка 3 установлена: {x[3]}, {y[3]}", fg=SUCCESS_COLOR)
            point_buttons[2].config(bg=EDIT_COLOR, text="3 ✏️")
            active_point = None
            keyboard.remove_hotkey('3')

    def checkpos4():
        nonlocal active_point
        if active_point == 4:
            x[4], y[4] = pag.position()
            if coord_labels[3][0] and coord_labels[3][1]:
                coord_labels[3][0].config(text=f"X: {x[4]}", bg=SUCCESS_COLOR)
                coord_labels[3][1].config(text=f"Y: {y[4]}", bg=SUCCESS_COLOR)
            q[4] = 1
            status_label.config(text=f"Точка 4 установлена: {x[4]}, {y[4]}", fg=SUCCESS_COLOR)
            point_buttons[3].config(bg=EDIT_COLOR, text="4 ✏️")
            active_point = None
            keyboard.remove_hotkey('4')

    def checkpos5():
        nonlocal active_point
        if active_point == 5:
            x[5], y[5] = pag.position()
            if coord_labels[4][0] and coord_labels[4][1]:
                coord_labels[4][0].config(text=f"X: {x[5]}", bg=SUCCESS_COLOR)
                coord_labels[4][1].config(text=f"Y: {y[5]}", bg=SUCCESS_COLOR)
            q[5] = 1
            status_label.config(text=f"Точка 5 установлена: {x[5]}, {y[5]}", fg=SUCCESS_COLOR)
            point_buttons[4].config(bg=EDIT_COLOR, text="5 ✏️")
            active_point = None
            keyboard.remove_hotkey('5')

    # Функции для сброса точек
    def reset_point(point_num):
        nonlocal active_point
        q[point_num] = 0
        if coord_labels[point_num - 1][0] and coord_labels[point_num - 1][1]:
            coord_labels[point_num - 1][0].config(text="Не установлено", bg=ENTRY_COLOR)
            coord_labels[point_num - 1][1].config(text="Не установлено", bg=ENTRY_COLOR)
        point_buttons[point_num - 1].config(bg=ACCENT_COLOR, text=str(point_num))
        status_label.config(text=f"Точка {point_num} сброшена. Можно установить заново", fg=WARNING_COLOR)

    # Фрейм для настроек
    settings_frame = tk.LabelFrame(main_frame, text="Настройки",
                                   bg=BG_COLOR, fg=TEXT_COLOR,
                                   font=('Arial', 12, 'bold'),
                                   padx=15, pady=15)
    settings_frame.grid(row=1, column=0, columnspan=8, sticky='ew', pady=(0, 15))

    # Количество повторений
    tk.Label(settings_frame, text="Количество повторений:",
             bg=BG_COLOR, fg=TEXT_COLOR, font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=5)
    e1 = tk.Entry(settings_frame, width=12, bg=ENTRY_COLOR, fg=TEXT_COLOR,
                  font=('Arial', 10), relief=tk.FLAT)
    e1.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(settings_frame, text="OK", command=lambda: f_n(e1),
              bg=BUTTON_COLOR, fg=TEXT_COLOR, font=('Arial', 9, 'bold'),
              width=6, relief=tk.FLAT).grid(row=0, column=2, padx=5, pady=5)

    # Пауза между циклами
    tk.Label(settings_frame, text="Пауза (секунды):",
             bg=BG_COLOR, fg=TEXT_COLOR, font=('Arial', 10)).grid(row=1, column=0, sticky='w', pady=5)
    e2 = tk.Entry(settings_frame, width=12, bg=ENTRY_COLOR, fg=TEXT_COLOR,
                  font=('Arial', 10), relief=tk.FLAT)
    e2.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(settings_frame, text="OK", command=lambda: f_z(e2),
              bg=BUTTON_COLOR, fg=TEXT_COLOR, font=('Arial', 9, 'bold'),
              width=6, relief=tk.FLAT).grid(row=1, column=2, padx=5, pady=5)

    # Количество точек
    tk.Label(settings_frame, text="Количество точек (1-5):",
             bg=BG_COLOR, fg=TEXT_COLOR, font=('Arial', 10)).grid(row=2, column=0, sticky='w', pady=5)
    e3 = tk.Entry(settings_frame, width=12, bg=ENTRY_COLOR, fg=TEXT_COLOR,
                  font=('Arial', 10), relief=tk.FLAT)
    e3.grid(row=2, column=1, padx=10, pady=5)
    tk.Button(settings_frame, text="OK", command=lambda: f_g(e3),
              bg=BUTTON_COLOR, fg=TEXT_COLOR, font=('Arial', 9, 'bold'),
              width=6, relief=tk.FLAT).grid(row=2, column=2, padx=5, pady=5)

    # Фрейм для точек
    points_frame = tk.LabelFrame(main_frame, text="Точки кликов",
                                 bg=BG_COLOR, fg=TEXT_COLOR,
                                 font=('Arial', 12, 'bold'),
                                 padx=15, pady=15)
    points_frame.grid(row=2, column=0, columnspan=8, sticky='ew', pady=(0, 15))

    # Заголовки для точек
    headers = ["Точка", "Координата X", "Координата Y", "Действие", "Сброс"]
    for col, header in enumerate(headers):
        tk.Label(points_frame, text=header, bg=BG_COLOR, fg=TEXT_COLOR,
                 font=('Arial', 10, 'bold')).grid(row=0, column=col, padx=5, pady=8)

    # Создаем точки
    for i in range(1, 6):
        # Номер точки
        tk.Label(points_frame, text=str(i), bg=BG_COLOR, fg=TEXT_COLOR,
                 font=('Arial', 10, 'bold')).grid(row=i, column=0, padx=10, pady=5)

        # Координата X
        x_label = tk.Label(points_frame, text="Не установлено",
                           bg=ENTRY_COLOR, fg=TEXT_COLOR, width=15,
                           font=('Arial', 9))
        x_label.grid(row=i, column=1, padx=5, pady=5)

        # Координата Y
        y_label = tk.Label(points_frame, text="Не установлено",
                           bg=ENTRY_COLOR, fg=TEXT_COLOR, width=15,
                           font=('Arial', 9))
        y_label.grid(row=i, column=2, padx=5, pady=5)

        coord_labels[i - 1] = [x_label, y_label]

    # Кнопки для установки точек
    button_frame = tk.Frame(points_frame, bg=BG_COLOR)
    button_frame.grid(row=1, column=3, rowspan=5, padx=5)

    point_buttons = []
    for i in range(5):
        btn = tk.Button(button_frame, text=str(i + 1),
                        bg=ACCENT_COLOR, fg=TEXT_COLOR,
                        font=('Arial', 10, 'bold'), width=4,
                        relief=tk.FLAT)
        btn.grid(row=i, column=0, pady=3)
        point_buttons.append(btn)

    # Кнопки для сброса точек
    reset_frame = tk.Frame(points_frame, bg=BG_COLOR)
    reset_frame.grid(row=1, column=4, rowspan=5, padx=5)

    reset_buttons = []
    for i in range(5):
        btn = tk.Button(reset_frame, text="🗑️",
                        bg=WARNING_COLOR, fg=TEXT_COLOR,
                        font=('Arial', 10), width=3,
                        relief=tk.FLAT, command=lambda idx=i + 1: reset_point(idx))
        btn.grid(row=i, column=0, pady=3)
        reset_buttons.append(btn)

    # Назначаем команды кнопкам установки
    point_buttons[0].config(command=set_point_1)
    point_buttons[1].config(command=set_point_2)
    point_buttons[2].config(command=set_point_3)
    point_buttons[3].config(command=set_point_4)
    point_buttons[4].config(command=set_point_5)

    # Функции обработки ввода
    def f_n(entry):
        global n
        if entry.get() == '':
            error_label = tk.Label(main_frame, text='Значение не указано',
                                   bg=WARNING_COLOR, fg=TEXT_COLOR,
                                   font=('Arial', 9))
            error_label.grid(row=5, column=0, columnspan=8, pady=5)
            win.after(2000, error_label.destroy)
            status_label.config(text="Ошибка: количество повторений не указано", fg=WARNING_COLOR)
        elif entry.get().isdigit():
            n = int(entry.get())
            status_label.config(text=f"Количество повторений установлено: {n}", fg=SUCCESS_COLOR)
        win.focus_force()

    def f_z(entry):
        global z
        pause = entry.get()
        if pause and pause.isdigit():
            z = int(pause)
            status_label.config(text=f"Пауза установлена: {z} секунд", fg=SUCCESS_COLOR)
        else:
            error_label = tk.Label(main_frame, text='Значение не указано',
                                   bg=WARNING_COLOR, fg=TEXT_COLOR,
                                   font=('Arial', 9))
            error_label.grid(row=5, column=0, columnspan=8, pady=5)
            win.after(2000, error_label.destroy)
            status_label.config(text="Ошибка: пауза не указана", fg=WARNING_COLOR)
        win.focus_force()

    def f_g(entry):
        global g
        keys = entry.get()
        if keys and keys.isdigit():
            g = int(keys)
            status_label.config(text=f"Количество точек установлено: {g}", fg=SUCCESS_COLOR)
        else:
            error_label = tk.Label(main_frame, text='Значение не указано',
                                   bg=WARNING_COLOR, fg=TEXT_COLOR,
                                   font=('Arial', 9))
            error_label.grid(row=5, column=0, columnspan=8, pady=5)
            win.after(2000, error_label.destroy)
            status_label.config(text="Ошибка: количество точек не указано", fg=WARNING_COLOR)
        win.focus_force()

    # Фрейм управления
    control_frame = tk.Frame(main_frame, bg=BG_COLOR)
    control_frame.grid(row=3, column=0, columnspan=8, pady=20)

    # Кнопки управления
    start_btn = tk.Button(control_frame, text='Старт',
                          bg=SUCCESS_COLOR, fg=TEXT_COLOR,
                          font=('Arial', 11, 'bold'),
                          command=muve, width=10, relief=tk.FLAT)
    start_btn.grid(row=0, column=0, padx=10)

    restart_btn = tk.Button(control_frame, text="Перезапуск",
                            bg=ACCENT_COLOR, fg=TEXT_COLOR,
                            font=('Arial', 11, 'bold'),
                            command=restart_clicked, width=10, relief=tk.FLAT)
    restart_btn.grid(row=0, column=1, padx=10)

    close_btn = tk.Button(control_frame, text="Выход",
                          bg=WARNING_COLOR, fg=TEXT_COLOR,
                          font=('Arial', 11, 'bold'),
                          command=close_clicked_res, width=10, relief=tk.FLAT)
    close_btn.grid(row=0, column=2, padx=10)

    # Статус бар
    status_label = tk.Label(main_frame, text="Готов к работе. Нажмите кнопку точки для активации",
                            relief=tk.SUNKEN, bg=ENTRY_COLOR,
                            fg=TEXT_COLOR, font=('Arial', 10),
                            anchor='w', padx=10)
    status_label.grid(row=4, column=0, columnspan=8, sticky='ew', pady=(10, 0))

    # Инструкция
    instruction_frame = tk.Frame(main_frame, bg=BG_COLOR)
    instruction_frame.grid(row=5, column=0, columnspan=8, pady=(10, 0))


    # Горячая клавиша для выхода
    keyboard.add_hotkey('esc', true_false_revers)

    # Центрируем окно
    win.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()
    x_pos = (win.winfo_screenwidth() // 2) - (width // 2)
    y_pos = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry(f'{width}x{height}+{x_pos}+{y_pos}')

    win.mainloop()


clicker()