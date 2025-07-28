import random
import struct
import flet as ft
import win32con
import win32process
from pyautogui import screenshot
import win32gui
import requests
import ctypes
import telebot
from threading import Thread
import psutil
from pymemoryapi import Process
from os import abort
import math
from time import sleep, time
from subprocess import check_output, STDOUT

PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400
float_value = ctypes.c_float()
float_value_balance = ctypes.c_float()
bytes_read = ctypes.c_size_t()

Zakazatx, Zakazaty = 1714, 157
Confirmx, Confirmy = 950, 725
UPx1, UPy1 = 712, 371
OKx1, OKy1 = 950, 725
Otmenax, Otmenay = 1712, 273
NAZADx2, NAZADy2 = 950, 725
Prodatx, Prodaty = 400, 840
Skinx, Skiny = 302, 224
Vibratx, Vibraty = 1609, 964
Polex, Poley = 1302, 448
Krestikx, Krestiky = 1421, 308
Kupitx, Kupity = 1713, 470
check_set = False
stop = False
Bluestacks = False
aga = 0
auto = 0
myLove = 0
stupa = 0
check_able = 0

with open("cfg/dict/tg_bot.txt") as ftg:
    txt_ID = ftg.readlines()
tg_ID = txt_ID[0]
ftg.close()

bot1 = telebot.TeleBot('7350227076:AAEeet5oYhbzm8FQ7ko0MNSucWHYQzHOqNk')
Okup = 0
coords = [(Confirmx, Confirmy), (Otmenax, Otmenay), (Otmenax, Otmenay), (OKx1, OKy1), (Zakazatx, Zakazaty)]
_error_wth_add = 2
_count_wrong_adr = 0

def Auto_PID(proc_name1, proc_name2):
    global _proc_num1, _proc_num2, LD9, PID
    for proc in procs_sorted:
        if proc.info['name'] == proc_name1:
            _proc_num1 += 1
            if _proc_num1 == int(window_number):
                LD9 = proc.pid
        if proc.info['name'] == proc_name2:
            _proc_num2 += 1
            if _proc_num2 == int(window_number):
                PID = proc.pid
        if _proc_num1 == _proc_num2 == window_number:
            break

def MAKELPARAM(low, high):
    return (high << 16) | (low & 0xFFFF)

def write_key(msg):
    for c in msg:
        if c == ("\n"):
            win32gui.PostMessage(hWnd1, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
            win32gui.PostMessage(hWnd1, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
        else:
            win32gui.PostMessage(hWnd1, win32con.WM_CHAR, ord(c), 0)

def click(x, y):
    rect = win32gui.GetClientRect(hWnd1)
    a = 1920 / x
    b = 1080 / y
    x_win = int(rect[2] / a)
    y_win = int(rect[3] / b)
    lParam = MAKELPARAM(x_win, y_win)
    ctypes.windll.user32.PostMessageW(hWnd1, 513, 0, lParam)
    ctypes.windll.user32.PostMessageW(hWnd1, 514, 0, lParam)

def for_unreq():
    global adres14, adres38, adres39, adres33, adres34, adres37, adres32, adres3a, adres35, _error_wth_add, _count_wrong_adr
    for addr in adres14:
        if hex(addr).endswith("002"):
            _count_wrong_adr += 1
            if _count_wrong_adr >= _error_wth_add:
                adres38 = int(addr)
                adres38 = adres38 + 0x36
                adres39 = adres38 + 1
                adres33 = adres38 - 5
                adres34 = adres38 - 4
                adres37 = adres38 - 1
                adres32 = adres38 - 6
                adres3a = adres38 + 2
                adres35 = adres38 - 3
                _error_wth_add += 1
                _count_wrong_adr = 1
                print(hex(addr), 'fds')
                break
            print(_count_wrong_adr, _error_wth_add)
            if _error_wth_add >= 10:
                _error_wth_add = 1

def enum_window_callback(hwnd, pid):
    tid, current_pid = win32process.GetWindowThreadProcessId(hwnd)
    if pid == current_pid and win32gui.IsWindowVisible(hwnd):
        windows.append(hwnd)

def read_float(address) -> float:
    ctypes.windll.kernel32.ReadProcessMemory(h_process, address, ctypes.byref(float_value), ctypes.sizeof(float_value), ctypes.byref(bytes_read))
    return float_value.value

def read_float_balance(address) -> float:
    ctypes.windll.kernel32.ReadProcessMemory(h_process, address, ctypes.byref(float_value_balance), ctypes.sizeof(float_value_balance), ctypes.byref(bytes_read))
    return float_value_balance.value

def freeze_float(add, add1, value):
    for _ in range(10000):
        process.write_float(add, value)
        process.write_float(add1, value)
        sleep(0.0001)

def sleep_stop() -> float:
    global Lol2
    return float(Lol2.value)

########################################################

def full_request_fun(price, w_adres, w_adres1, w_adres2, w_adres3):
    m_adres = w_adres
    m_adres1 = w_adres1
    m_adres2 = w_adres2
    m_adres3 = w_adres3
    if botg == 1:
        bot1.send_message(tg_ID, "· Request: " + str(round(price, 2)) + "\n· First Lot: " + str(round(read_float(m_adres3), 2)) + "\n· Balance: " + str(round(read_float_balance(balance), 2)))
        bot1.poll_handler(tg_ID)
    while not stop:
        sleep(0.1)
        price = read_float(m_adres2)
        while not stop:
            sleep(0.000001)
            price2 = read_float(m_adres2)
            savemode = read_float(m_adres3)
            if -1 < price < price2 < savemode - 0.01 < 999999.00:
                sleep(myLove / 1000)
                if read_float(m_adres2) < read_float(m_adres3) - 0.01:
                    bal1 = read_float_balance(balance)
                    Thread(target=freeze_float, args=(m_adres, m_adres1, savemode - 0.01)).start()
                    sleeps = [sleep_stop(), 0.1, 0.25, 0.4, 1]
                    for (coord, Sleep) in zip(coords, sleeps):
                        click(*coord)
                        sleep(Sleep)
                    if botg == 1:
                        Thread(target=tgtg, args=(bal1, savemode, price2), daemon=True).start()
                break
            if 999999.00 > price > price2 > 1 or 999999 > price2 > savemode - 0.01 > 1:
                price = read_float(m_adres2)


def polu_api_fun(price, w_adres, w_adres1, w_adres2, w_adres3):
    m_adres = w_adres
    m_adres1 = w_adres1
    m_adres2 = w_adres2
    m_adres3 = w_adres3
    if botg == 1:
        bot1.send_message(tg_ID, "· Request: " + str(round(price, 2)) + "\n· First Lot: " + str(round(read_float(m_adres3), 2)) + "\n· Balance: " + str(round(read_float_balance(balance), 2)))
        bot1.poll_handler(tg_ID)
    while not stop:
        sleep(0.1)
        price = read_float(m_adres2)
        while not stop:
            sleep(0.000001)
            price2 = read_float(m_adres2)
            savemode = read_float(m_adres3)
            stupa = aga
            if -1 < price < price2 < savemode - stupa - anti < 999999.00:
                sleep(myLove / 1000)
                if read_float(m_adres2) < read_float(m_adres3) - stupa - anti:
                    bal1 = read_float_balance(balance)
                    Thread(target=freeze_float, args=(m_adres, m_adres1, price2 + stupa)).start()
                    sleeps = [sleep_stop(), 0.1, 0.25, 0.4, 1]
                    for (coord, Sleep) in zip(coords, sleeps):
                        click(*coord)
                        sleep(Sleep)
                    if botg == 1:
                        Thread(target=tgtg, args=(bal1, savemode, price2), daemon=True).start()
                    price = read_float(m_adres2)
            if 999999.00 > price > price2 > 1 or 999999 > price2 > savemode - stupa - anti > 1:
                price = read_float(m_adres2)


def switcher_fun(price, w_adres, w_adres1, w_adres2, w_adres3):
    m_adres = w_adres
    m_adres1 = w_adres1
    m_adres2 = w_adres2
    m_adres3 = w_adres3
    if botg == 1:
        bot1.send_message(tg_ID, "· Request: " + str(round(price, 2)) + "\n· First Lot: " + str(round(read_float(m_adres3), 2)) + "\n· Balance: " + str(round(read_float_balance(balance), 2)))
        bot1.poll_handler(tg_ID)
    while not stop:
        sleep(0.1)
        price = read_float(m_adres2)
        while not stop:
            sleep(0.000001)
            price2 = read_float(m_adres2)
            savemode = read_float(m_adres3)
            stupa = aga
            if -1 < price < price2 < savemode - stupa - anti < 999999.00:
                for _ in range(400000):
                    price03 = read_float(m_adres2)
                    if -1 < price2 < price03 < read_float(m_adres3) - stupa - anti < 999999.00:
                        sleep(myLove / 1000)
                        if read_float(m_adres2) < read_float(m_adres3) - stupa - anti:
                            bal1 = read_float_balance(balance)
                            if zp == 0:
                                Thread(target=freeze_float, args=(m_adres, m_adres1, price03 + stupa)).start()
                                sleeps = [sleep_stop(), 0.1, 0.25, 0.4, 1]
                                for (coord, Sleep) in zip(coords, sleeps):
                                    click(*coord)
                                    sleep(Sleep)
                            else:
                                Thread(target=freeze_float, args=(m_adres, m_adres1, read_float(m_adres3) - 0.01)).start()
                                sleeps = [sleep_stop(), 0.1, 0.25, 0.4, 1]
                                for (coord, Sleep) in zip(coords, sleeps):
                                    click(*coord)
                                    sleep(Sleep)
                            if botg == 1:
                                Thread(target=tgtg, args=(bal1, savemode, price2), daemon=True).start()
                            price = read_float(m_adres2)
                            break
            if 999999.00 > price > price2 > 1 or 999999 > price2 > savemode - stupa - anti > 1:
                price = read_float(m_adres2)


def apimode_switcher_fun(price, w_adres, w_adres1, w_adres2, w_adres3):
    coords2 = [(Otmenax, Otmenay), (Otmenax, Otmenay), (OKx1, OKy1), (Zakazatx, Zakazaty)]
    sleeps2 = [0.1, 0.25, 0.4, 1]
    m_adres = w_adres
    m_adres1 = w_adres1
    m_adres2 = w_adres2
    m_adres3 = w_adres3
    if botg == 1:
        bot1.send_message(tg_ID, "· Request: " + str(round(price, 2)) + "\n· First Lot: " + str(round(read_float(m_adres3), 2)) + "\n· Balance: " + str(round(read_float_balance(balance), 2)))
        bot1.poll_handler(tg_ID)
    while not stop:
        sleep(0.1)
        price = read_float(m_adres2)
        while not stop:
            sleep(0.000001)
            price2 = read_float(m_adres2)
            savemode = read_float(m_adres3)
            stupa = aga
            if -1 < price < price2 < savemode - stupa - anti < 999999.00:
                for _ in range(400000):
                    price03 = read_float(m_adres2)
                    b = 0
                    if price2 < price03 < read_float(m_adres3) - anti - stupa:
                        bal1 = read_float_balance(balance)
                        Thread(target=freeze_float, args=(m_adres, m_adres1, price2 + stupa)).start()
                        click(Confirmx, Confirmy)
                        sleep(0.25)
                        start_time = time()
                        while True:
                            price5 = round(read_float(m_adres2), 2)
                            if zp == 0:
                                if -1 < round(price2 + stupa, 2) < price5 < read_float(
                                        m_adres3) - anti - stupa < 999999.00:
                                    For_Low(Lot)
                                    Thread(target=freeze_float, args=(m_adres, m_adres1, price5 + stupa)).start()
                                    click(Confirmx, Confirmy)
                                    sleep(0.25)
                                    start_time = time()
                                    while True:
                                        price6 = round(read_float(m_adres2), 2)
                                        if -1 < round(price5 + stupa, 2) < price6 < read_float(
                                                m_adres3) - anti - stupa < 999999.00:
                                            For_Low(Lot)
                                            Thread(target=freeze_float,
                                                   args=(m_adres, m_adres1, price6 + stupa)).start()
                                            click(Confirmx, Confirmy)
                                            sleep(0.25)
                                            start_time = time()
                                            while True:
                                                price7 = round(read_float(m_adres2), 2)
                                                if -1 < round(price6 + stupa, 2) < price7 < read_float(m_adres3) - (
                                                        anti + stupa) < 999999.00:
                                                    b = 3
                                                    For_Low(Lot)
                                                    Thread(target=freeze_float,
                                                           args=(m_adres, m_adres1, price7 + stupa)).start()
                                                    sleeps = [sleep_stop(), 0.1, 0.25, 0.4, 1]
                                                    for (coord, Sleep) in zip(coords, sleeps):
                                                        click(*coord)
                                                        sleep(Sleep)
                                                    break
                                                if time() - start_time >= sleep_stop():
                                                    break
                                        if time() - start_time >= sleep_stop():
                                            break
                            else:
                                save_mode = read_float(m_adres3)
                                if -1 < round(price2 + stupa, 2) < price5 < save_mode - anti - stupa < 999999.00:
                                    b = 1
                                    For_Low(Lot)
                                    Thread(target=freeze_float, args=(m_adres, m_adres1, save_mode - 0.01)).start()
                                    sleeps = [sleep_stop(), 0.1, 0.25, 0.4, 1]
                                    for (coord, Sleep) in zip(coords, sleeps):
                                        click(*coord)
                                        sleep(Sleep)
                                    break
                            if time() - start_time >= sleep_stop():
                                break
                        if b == 0:
                            for (coord, Sleep) in zip(coords2, sleeps2):
                                click(*coord)
                                sleep(Sleep)
                        if botg == 1:
                            Thread(target=tgtg, args=(bal1, savemode, price2), daemon=True).start()
                        b = 0
                        price = read_float(m_adres2)
                        break
            if 999999.00 > price > price2 > 1 or 999999 > price2 > savemode - stupa - anti > 1:
                price = read_float(m_adres2)


def api_mode_fun(price, w_adres, w_adres1, w_adres2, w_adres3):
    coords = [(Confirmx, Confirmy), (Otmenax, Otmenay), (Otmenax, Otmenay), (OKx1, OKy1), (Zakazatx, Zakazaty)]
    coords2 = [(Otmenax, Otmenay), (Otmenax, Otmenay), (OKx1, OKy1), (Zakazatx, Zakazaty)]
    sleeps2 = [0.1, 0.25, 0.4, 1]
    m_adres = w_adres
    m_adres1 = w_adres1
    m_adres2 = w_adres2
    m_adres3 = w_adres3
    if botg == 1:
        bot1.send_message(tg_ID, "· Request: " + str(round(price, 2)) + "\n· First Lot: " + str(round(read_float(m_adres3), 2)) + "\n· Balance: " + str(round(read_float_balance(balance), 2)))
        bot1.poll_handler(tg_ID)
    while not stop:
        sleep(0.1)
        price = read_float(m_adres2)
        while not stop:
            sleep(0.000001)
            price2 = read_float(m_adres2)
            savemode = read_float(m_adres3)
            stupa = aga
            if -1 < price < price2 < savemode - anti - stupa < 999999.00:
                b = 0
                sleep(myLove / 1000)
                if read_float(m_adres2) < read_float(m_adres3) - anti - stupa:
                    bal1 = read_float_balance(balance)
                    Thread(target=freeze_float, args=(m_adres, m_adres1, price2 + stupa)).start()
                    click(Confirmx, Confirmy)
                    sleep(0.25)
                    start_time = time()
                    while True:
                        price5 = round(read_float(m_adres2), 2)
                        if zp == 0:
                            if -1 < round(price2 + stupa, 2) < price5 < read_float(m_adres3) - anti - stupa < 999999.00:
                                For_Low(Lot)
                                Thread(target=freeze_float, args=(m_adres, m_adres1, price5 + stupa)).start()
                                click(Confirmx, Confirmy)
                                sleep(0.25)
                                start_time = time()
                                while True:
                                    price6 = round(read_float(m_adres2), 2)
                                    if -1 < round(price5 + stupa, 2) < price6 < read_float(
                                            m_adres3) - anti - stupa < 999999.00:
                                        For_Low(Lot)
                                        Thread(target=freeze_float, args=(m_adres, m_adres1, price6 + stupa)).start()
                                        click(Confirmx, Confirmy)
                                        sleep(0.25)
                                        start_time = time()
                                        while True:
                                            price7 = round(read_float(m_adres2), 2)
                                            if -1 < round(price6 + stupa, 2) < price7 < read_float(m_adres3) - (anti + stupa) < 999999.00:
                                                b = 3
                                                For_Low(Lot)
                                                Thread(target=freeze_float, args=(m_adres, m_adres1, price7 + stupa)).start()
                                                sleeps = [sleep_stop(), 0.1, 0.25, 0.4, 1]
                                                for (coord, Sleep) in zip(coords, sleeps):
                                                    click(*coord)
                                                    sleep(Sleep)
                                                break
                                            if time() - start_time >= sleep_stop():
                                                break
                                    if time() - start_time >= sleep_stop():
                                        break
                        else:
                            save_mode = read_float(m_adres3)
                            if -1 < round(price2 + stupa, 2) < price5 < save_mode - anti - stupa < 999999.00:
                                b = 1
                                For_Low(Lot)
                                Thread(target=freeze_float, args=(m_adres, m_adres1, save_mode - 0.01)).start()
                                sleeps = [sleep_stop(), 0.1, 0.25, 0.4, 1]
                                for (coord, Sleep) in zip(coords, sleeps):
                                    click(*coord)
                                    sleep(Sleep)
                                break
                        if time() - start_time >= sleep_stop():
                            break
                    if b == 0:
                        for (coord, Sleep) in zip(coords2, sleeps2):
                            click(*coord)
                            sleep(Sleep)
                    if botg == 1:
                        Thread(target=tgtg, args=(bal1, savemode, price2), daemon=True).start()
                    b = 0
                    price = read_float(m_adres2)
            if 999999.00 > price > price2 > 1 or 999999 > price2 > savemode - stupa - anti > 1:
                price = read_float(m_adres2)


def two_requests_fun(price, w_adres, w_adres1, w_adres2, w_adres3):
    coords = [(Confirmx, Confirmy), (Otmenax, Otmenay), (Otmenax, Otmenay)]
    m_adres = w_adres
    m_adres1 = w_adres1
    m_adres2 = w_adres2
    m_adres3 = w_adres3
    if botg == 1:
        bot1.send_message(tg_ID, "· Request: " + str(round(price, 2)) + "\n· First Lot: " + str(round(read_float(m_adres3), 2)) + "\n· Balance: " + str(round(read_float_balance(balance), 2)))
        bot1.poll_handler(tg_ID)
    while not stop:
        sleep(0.1)
        price = read_float(m_adres2)
        while not stop:
            sleep(0.000001)
            price2 = read_float(m_adres2)
            savemode = read_float(m_adres3)
            stupa = aga
            if -1 < price < price2 < savemode - anti - stupa < 999999.00:
                sleep(myLove / 1000)
                if read_float(m_adres2) < read_float(m_adres3) - anti - stupa:
                    bal1 = read_float_balance(balance)
                    Thread(target=freeze_float, args=(m_adres, m_adres1, price2 + stupa)).start()
                    sleeps = [sleep_stop(), 0.1, 0.25]
                    for (coord, Sleep) in zip(coords, sleeps):
                        click(*coord)
                        sleep(Sleep)
                    click(Zakazatx, Zakazaty)
                    sleep(0.5)
                    price5 = round(read_float(m_adres2), 2)
                    if price5 < round(read_float(m_adres3), 2) - anti - stupa:
                        Thread(target=freeze_float, args=(m_adres, m_adres1, price5 + stupa)).start()
                        sleeps = [sleep_stop(), 0.1, 0.25]
                        for (coord, Sleep) in zip(coords, sleeps):
                            click(*coord)
                            sleep(Sleep)
                    sleep(0.25)
                    click(OKx1, OKy1)
                    sleep(0.4)
                    click(Zakazatx, Zakazaty)
                    sleep(1)
                    if botg == 1:
                        Thread(target=tgtg, args=(bal1, savemode, price2), daemon=True).start()
                    price = read_float(m_adres2)
            if 999999.00 > price > price2 > 1 or 999999 > price2 > savemode - stupa - anti > 1:
                price = read_float(m_adres2)


def Auto_full_fun(price, w_adres, w_adres1, w_adres2, w_adres3):
    m_adres = w_adres
    m_adres1 = w_adres1
    m_adres2 = w_adres2
    m_adres3 = w_adres3
    if botg == 1:
        bot1.send_message(tg_ID, "· Request: " + str(round(price, 2)) + "\n· First Lot: " + str(round(read_float(m_adres3), 2)) + "\n· Balance: " + str(round(read_float_balance(balance), 2)))
        bot1.poll_handler(tg_ID)
    while not stop:
        sleep(0.1)
        price = read_float(m_adres2)
        while not stop:
            sleep(0.000001)
            price2 = read_float(m_adres2)
            savemode = read_float(m_adres3)
            if -1 < price < price2 and round(price2, 2) == round(savemode - 0.01, 2) < 999999.00:
                bal1 = read_float_balance(balance)
                Thread(target=freeze_float, args=(m_adres, m_adres1, savemode - 0.01)).start()
                click(Confirmx, Confirmy)
                click(Prodatx, Prodaty)
                sleep(0.15)
                click(Skinx, Skiny)
                sleep(0.01)
                click(Vibratx, Vibraty)
                sleep(0.2)
                click(Polex, Poley)
                sleep(0.1)
                process.write_float(0xE29DBCA8, price2)
                click(Confirmx, Confirmy)
                sleep(0.1)
                click(Krestikx, Krestiky)
                sleeps = [sleep_stop(), 0.1, 0.25, 0.4, 1]
                for (coord, Sleep) in zip(coords, sleeps):
                    click(*coord)
                    sleep(Sleep)
                if botg == 1:
                    Thread(target=tgtg, args=(bal1, savemode, price2), daemon=True).start()
                break
            if 999999.00 > price > price2 > 1 or 999999 > price2 > savemode - 0.01 > 1:
                price = read_float(m_adres2)


########################################################


def low_mode():
    if Lot == 0:
        sleep(0.24)
    else:
        sleep(0.29)


def For_Low(Lot):
    if Lot == 0:
        click(Otmenax, Otmenay)
        sleep(0.05)
        click(Otmenax, Otmenay)
        sleep(0.2)
        click(Zakazatx, Zakazaty)
        sleep(0.1)
    else:
        sleep(0.1)
        click(Otmenax, Otmenay)
        sleep(0.05)
        click(Otmenax, Otmenay)
        sleep(0.25)
        click(Zakazatx, Zakazaty)
        sleep(0.2)


with open("cfg/dict/tg_bot.txt") as ftg:
    txt_ID = ftg.readlines()
try:
    tg_ID = txt_ID[0]
except:
    ctypes.windll.user32.MessageBoxW(None, u"Chat ID wasn't found", u"Error", 0)


ftg.close()


def tgtg(bal1, save_mode, price_bot):
    global Okup
    print(bal1, read_float_balance(balance))
    if bal1 > read_float_balance(balance):
        screen = screenshot()
        Okup2 = float(round(save_mode / 1.25 - (bal1 - read_float_balance(balance)), 2))
        Okup = Okup + Okup2
        save_mode = round(save_mode, 2)
        if round(price_bot, 2) > round(bal1 - read_float_balance(balance), 2) * 1.8:
            bot1.send_photo(tg_ID, screen, f'✅Skin was bought for ' + str(
                round(bal1 - read_float_balance(balance), 2)) + 'G' + '✅️\n👻Price of 1 Lot: ' + str(
                save_mode) + 'G\n\n💎Balance: ' + str(round(read_float_balance(balance), 2)) + 'G\n\n💰Profit: ' + str(Okup) + "G")
            bot1.poll_handler(tg_ID)
        else:
            bot1.send_photo(tg_ID, screen, f'❌Skin was bought for ' + str(
                round(bal1 - read_float_balance(balance), 2)) + 'G' + '❌\n👻Price of 1 Lot: ' + str(
                save_mode) + 'G\n\n💎Balance: ' + str(round(read_float_balance(balance), 2)) + 'G\n\n💰Profit: ' + str(Okup) + "G")
            bot1.poll_handler(tg_ID)


_proc_num1 = 0
_proc_num2 = 0
with open("cfg/title.txt") as op:
    tnt = op.readlines()
op.close()

window_number = tnt[0].strip()

procs = list(psutil.process_iter(['pid', 'name', 'create_time']))
procs_sorted = sorted(procs, key=lambda p: p.info.get('create_time', 0))

Auto_PID("dnplayer.exe", "Ld9BoxHeadless.exe")

windows = []
win32gui.EnumWindows(enum_window_callback, LD9)
hWnd = win32gui.FindWindow(None, [win32gui.GetWindowText(item) for item in windows][0])
hWnd1 = win32gui.FindWindowEx(hWnd, None, None, None)
h_process = ctypes.windll.kernel32.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, PID)
process = Process(pid=PID)

"""
add = process.pattern_scan(start_address=0x0, end_address=0x120000000, pattern="01 00 00 ?? ?? ?? ?? 00 00 00 00 02")

                click(Zakazatx, Zakazaty)
                sleep(0.7)
                for address in add:
                    if process.read_short(address) == 0 and process.read_short(address + 0x47) == 1:
                        adres = address + 0x43
                        adres1 = adres + 8
                        break
"""

byte_string12 = process.pattern_scan(return_first_found=True, start_address=0x0, end_address=0x120000000, pattern='FF FF FF FF 65 00 00 00 00 ?? ?? ?? 66')

if byte_string12 is None:
    ctypes.windll.user32.MessageBoxW(None, u"Open the game, then open the program", 0)
    abort()
else:
    balance = byte_string12 + 24


def full_request():
    while not stop:
        adreses = [adres39, adres38, adres3a, adres37]
        adreses2 = [adres34, adres33, adres35, adres32]
        for adres2, adres3 in zip(adreses, adreses2):
            price1 = read_float(adres2)
            save = adres3
            sleep(0.1)
            if 1 < price1 < 20000.00:
                full_request_fun(price1, adres, adres1, adres2, save)
                break
        for_unreq()


def polu_api():
    global balance, adres, adres1, adres38, adres39, adres33, adres34, adres37, adres32, adres3a, adres35, stop
    while not stop:
        adreses = [adres39, adres38, adres3a, adres37]
        adreses2 = [adres34, adres33, adres35, adres32]
        for adres2, adres3 in zip(adreses, adreses2):
            price1 = read_float(adres2)
            save = adres3
            sleep(0.1)
            if 1 < price1 < 20000.00:
                polu_api_fun(price1, adres, adres1, adres2, save)
                break
        for_unreq()


def switch():
    global balance, adres, adres1, adres38, adres39, adres33, adres34, adres37, adres32, adres3a, adres35, stop
    while not stop:
        adreses = [adres39, adres38, adres3a, adres37]
        adreses2 = [adres34, adres33, adres35, adres32]
        for adres2, adres3 in zip(adreses, adreses2):
            price1 = read_float(adres2)
            save = adres3
            sleep(0.1)
            if 1 < price1 < 20000.00:
                switcher_fun(price1, adres, adres1, adres2, save)
                break
        for_unreq()


def Two_modes():
    global balance, adres, adres1, adres38, adres39, adres33, adres34, adres37, adres32, adres3a, adres35, stop
    while not stop:
        adreses = [adres39, adres38, adres3a, adres37]
        adreses2 = [adres34, adres33, adres35, adres32]
        for adres2, adres3 in zip(adreses, adreses2):
            price1 = read_float(adres2)
            save = adres3
            sleep(0.1)
            if 1 < price1 < 20000.00:
                apimode_switcher_fun(price1, adres, adres1, adres2, save)
                break
        for_unreq()


def polu_auto():
    global balance, adres, adres1, adres38, adres39, adres33, adres34, adres37, adres32, adres3a, adres35, stop
    while not stop:
        adreses = [adres39, adres38, adres3a, adres37]
        adreses2 = [adres34, adres33, adres35, adres32]
        print(adreses, adreses2)
        for adres2, adres3 in zip(adreses, adreses2):
            price1 = read_float(adres2)
            save = adres3
            sleep(0.1)
            print(price1, hex(adres2), hex(save))
            if 1 < price1 < 20000.00:
                api_mode_fun(price1, adres, adres1, adres2, save)
                break
        for_unreq()


def requests2():
    global balance, adres, adres1, adres38, adres39, adres33, adres34, adres37, adres32, adres3a, adres35, stop
    while not stop:
        adreses = [adres39, adres38, adres3a, adres37]
        adreses2 = [adres34, adres33, adres35, adres32]
        for adres2, adres3 in zip(adreses, adreses2):
            save = adres3
            price1 = read_float(adres2)
            sleep(0.1)
            if 1 < price1 < 20000.00:
                two_requests_fun(price1, adres, adres1, adres2, save)
                break
        for_unreq()


anti = 0
mode = 0 # Анти фулл
mode1 = 0 # 2 реквест
ultra = 0 # Авто фулл
zp = 0 # Фулл зп
botg = 0 # Бот Тг
Lot = 0 # Анти лот
swtch = 0
remv = 0

hover_color = '#3D017E'
bg_color = '#490198'
acce = False
log = True
rem = 0


def get_simple_cpu_hwid() -> str:
    def get_uuid() -> str:
        return check_output('powershell -Command "Get-WmiObject -Class Win32_ComputerSystemProduct | Select-Object -ExpandProperty UUID"', stderr=STDOUT).decode().strip()

    def get_hdd_id() -> str:
        serials = check_output('powershell "Get-WmiObject Win32_PhysicalMedia | Select-Object -Property SerialNumber, Tag"', shell=True).decode().split()
        for i in range(len(serials)):
            if 'DRIVE0' in str(serials[i]):
                return serials[i - 1]


    return get_uuid() + '-' + get_hdd_id()


rg = requests.get('https://pastebin.com/raw/ZUbi2FD4')
sdfhjsdfjsdfhrthshrtydhnrtmn = get_simple_cpu_hwid()

try:
    for a in range(len(rg.text.split())):
        if sdfhjsdfjsdfhrthshrtydhnrtmn == rg.text.splitlines()[a]:
            break
except:
    ctypes.windll.user32.MessageBoxW(None, u"HWID isn't in base", 0)
    abort()

def main(page: ft.Page):
    global Lol2

    def ulov(e):
        global stop, auto, mode1, ultra, zp, botg, swtch
        label1.top = -50
        label2.top = 13
        page.update()
        stop = False
        Thread(target=vvod, daemon=True).start()
        first_function()
        while not stop:
            if swtch == 1 and auto == 0 and mode1 == 0 and zp == 0:
                Thread(target=switch, daemon=True).start()
                break

            if swtch == 1 and auto == 1 and mode1 == 0:
                Thread(target=Two_modes, daemon=True).start()
                break

            if zp == 1 and auto == 0 and swtch == 0:
                Thread(target=full_request, daemon=True).start()
                break

            if auto == 1 and mode1 == 0 and swtch == 0:
                Thread(target=polu_auto, daemon=True).start()
                break

            if mode1 == 0 and zp == 0 and auto == 0 and swtch == 0:
                Thread(target=polu_api, daemon=True).start()
                break

            if mode1 == 1 and zp == 0:
                Thread(target=requests2, daemon=True).start()
                break

    def first_function():
        global byte_string12, lot, balance, adres, adres1, adres38, adres39, adres33, adres34, adres37, adres32, adres3a, adres35, adres14, check_set
        click(Zakazatx, Zakazaty)
        sleep(0.2)
        if not check_set:
            sleep(0.1)
            click(968, 448)
            sleep(0.3)
            write_key("999999")
            sleep(0.2)
            click(1241, 467)
            splash = ft.ProgressBar()
            page.overlay.append(splash)
            page.update()
            req = requests.get('https://pastebin.com/raw/4t56AarB')
            adres = process.pattern_scan(return_first_found=True, start_address=0x0, end_address=0x100000000,
                                         pattern="F0 23 74 49 01 00 00 00 F0 23 74 49")
            adres1 = adres + 8

            splash.value = 0.02
            page.update()

            for i in range(4, 40):
                splash.value = i * 0.005
                sleep(0.002)
                page.update()

            Thread(target=freeze_float, args=(adres, adres1, 0.03)).start()
            click(Confirmx, Confirmy)
            sleep(0.3)

            adres14 = process.pattern_scan(start_address=0x0, end_address=0x100000000, pattern=req.text.splitlines()[1])
            if adres14 is None:
                adres14 = process.pattern_scan(start_address=0x0, end_address=0x100000000,
                                               pattern=req.text.splitlines()[2])

            for i in range(40, 140):
                splash.value = i * 0.005
                sleep(0.0001)
                page.update()

            for addr in adres14:
                if hex(addr).endswith("002"):
                    adres38 = int(addr)
                    break

            for i in range(140, 180):
                splash.value = i * 0.005
                sleep(0.003)
                page.update()

            try:
                adres38 = adres38 + 0x36
            except:
                page.overlay.remove(splash)
                page.update()
                global stop
                label1.top = 13
                label2.top = -50
                page.update()
                stop = True
                dlg_modal = ft.AlertDialog(modal=True,
                    title=ft.Text("❌Error with program's setting\nTry to start again", size=15, text_align=ft.TextAlign.CENTER),
                    actions=[ft.ElevatedButton("OK", on_click=lambda e: page.close(dlg_modal))], actions_alignment=ft.MainAxisAlignment.END)
                page.open(dlg_modal)
            adres39 = adres38 + 1
            adres33 = adres38 - 5
            adres34 = adres38 - 4
            adres37 = adres38 - 1
            adres32 = adres38 - 6
            adres3a = adres38 + 2
            adres35 = adres38 - 3
            check_set = True
            for i in range(180, 202):
                splash.value = i * 0.005
                sleep(0.0001)
                page.update()

            page.overlay.remove(splash)
            page.update()
        else:
            sleep(0.4)
            adres = adres1 - 8
            Thread(target=freeze_float, args=(adres, adres1, 0.03)).start()
            click(Confirmx, Confirmy)
            sleep(1)
        click(Otmenax, Otmenay)
        sleep(0.4)
        click(Zakazatx, Zakazaty)
        sleep(0.4)

    def check_box_func(e):
        global check_able
        check_able += 1
        if check_able == 1:
            Lol4.disabled = False
            page.update()
        else:
            check_able = 0
            Lol4.disabled = True
            page.update()

    def api_mode(e): # Апи Мод
        global auto, mode1, ultra, zp
        auto += 1
        if auto == 1 and mode1 == 0:
            _labels(txt_api_mode, True)
            page.update()
        if auto == 1 and mode1 == 1 and zp == 1:
            _labels(txt_api_mode, True)
            page.update()
        if auto == 2:
            _labels(txt_api_mode, False)
            page.update()
            auto = 0

    def anti_full(e):  # Анти фулл
        global zp, mode
        mode += 1
        if mode == 2:
            _labels(txt_antifull, False)
            mode = 0
        if mode == 1:
            _labels(txt_antifull, True)

    def api_mode1(e):  # 2 зп
        global mode1, auto, ultra, zp, swtch
        mode1 += 1
        if mode1 == 1 and auto == 1 and zp == 0:
            _labels(txt_swt_mode, True)
            _labels(txt_api_mode, False)
            _labels(txt_swt_mode, False)
        if mode1 == 1 and auto == 0 and ultra == 0 and zp == 0:
            _labels(txt_swt_mode, True)
        if mode1 == 2:
            _labels(txt_swt_mode, False)
            mode1 = 0
        if mode1 == 0 and auto == 1 and zp == 0:
            _labels(txt_api_mode, True)
        if mode1 == 0 and swtch == 1:
            _labels(txt_swt_mode, True)
        if mode1 == 1 and ultra == 1:
            _labels(txt_swt_mode, False)

    def full_zp(e):  # фулл зп
        global zp, label11, label9, label8, label7, ultra, label10, mode1, auto, mode, swtch, label14
        zp += 1
        if zp == 2:
            _labels(txt_full_req, False)
            zp = 0
        if zp == 1:
            _labels(txt_full_req, True)
        if zp == 0 and mode1 == 1 and auto == 1:
            _labels(txt_api_mode, False)
        if zp == 1 and mode1 == 1 and auto == 1:
            _labels(txt_api_mode, True)
        if zp == 1 and mode1 == 1:
            _labels(txt_swt_mode, False)
        if zp == 0 and mode1 == 1:
            _labels(txt_swt_mode, True)
        if zp == 1 and mode == 1 and auto == 0:
            _labels(txt_antifull, False)
        if zp == 0 and mode == 1 and auto == 1:
            _labels(txt_antifull, True)
        if swtch == 1 and mode1 == 0:
            _labels(txt_swt_mode, True)

    def bot_tg_special(e):
        global botg
        botg += 1
        if botg == 2:
            _labels(txt_bot_tele, False)
            botg = 0
        if botg == 1:
            _labels(txt_bot_tele, True)

    def Anti_Lot(e):
        global Lot
        Lot += 1
        if Lot == 2:
            _labels(txt_low_mode, False)
            Lot = 0
        if Lot == 1:
            _labels(txt_low_mode, True)

    def Swtch(e):
        global swtch, zp, mode1
        swtch += 1
        if swtch == 2:
            _labels(txt_swt_mode, False)
            swtch = 0
        if swtch == 1 and mode1 == 0:
            _labels(txt_swt_mode, True)

    def vvod():
        global VvodPrice, aga, stop, anti, mode, myLove, stupa, check_able
        while not stop:
            try:
                aga1 = float(Lol3.value)
                if check_able == 0:
                    VvodPrice2 = aga1
                else:
                    VvodPrice2 = float(Lol4.value)
                if mode == 0:
                    anti = float(VvodPrice2)
                if mode == 1:
                    anti = float(Lol1.value)
                myLove = float(Lol.value)
            except ValueError:
                myLove = 0
                aga1 = 0.01
                VvodPrice2 = 0.01
            for _ in range(100):
                if aga1 > VvodPrice2:
                    aga1 = 0.01
                    VvodPrice2 = 0.01
                try:
                    stupa = float(Lol1.value)
                except:
                    stupa = 0
                aga = round(random.uniform(aga1, VvodPrice2), 2)
                sleep(0.024)

    def Remove(e):
        global remv
        remv += 1
        swches = [swch, swch1, swch2, swch3, swch4, swch5, swch6, swch7]
        hints = [hint, hint1, hint2, hint3, hint4, hint5, hint6, hint7]
        if remv == 1:
            _labels(txt_hint_rem, True)
            for Swch in swches:
                Swch.tooltip = ""
            page.update()
        if remv == 2:
            _labels(txt_hint_rem, False)
            for Swch, Hint in zip(swches, hints):
                Swch.tooltip = Hint
            page.update()
            remv = 0

    def Stop(e) -> None:
        global stop
        label1.top = 13
        label2.top = -50
        page.update()
        stop = True

    page.theme_mode = "dark"
    page.title = "API-ZINDORNO 0.03"
    page.bgcolor = "#120B1E"
    page.window.opacity = 0.98
    page.window.width = 527
    page.window.height = 415
    page.window.resizable = False
    page.window.maximizable = False
    page.window.always_on_top = True

    hint = 'Full Request - ставит запрос под фулл'
    hint1 = "Tg Bot - высылает вам в тг уловы"
    hint2 = "Low Mode - Использовать, если у вас\nмало фпс или слабый инет"
    hint3 = "Switcher mode - ставит запрос после того,\nкак первый запрос перебьёт другая апишка"
    hint4 = "2 Requests - ставит 2 запроса"
    hint5 = "AntiFull - не ставит запрос, если лот будет меньше,\nчем запрос - AntiFull (по умол. стоит 5)"
    hint6 = "Api Mode - перебивает ещё раз запрос,\nесли тот запрос был перебит"
    hint7 = "Убирает подсказки"

    ###############################

    Lol = ft.TextField(label="Sleep Request", value='0', border_color="#79289e", border_radius=15, text_size=11)
    Lol1 = ft.TextField(label="AntiFull", value='5.00', border_color="#79289e", border_radius=15, text_size=11)
    Lol2 = ft.TextField(label="Cancel", value='1.00', border_color="#79289e", border_radius=15, text_size=11)
    Lol3 = ft.TextField(label="1 Price", value='0.01', border_color="#79289e", border_radius=15, text_size=11)
    Lol4 = ft.TextField(label="2 Price", value='0.02', disabled=True, border_color="#79289e", border_radius=15, text_size=11)

    stack = ft.Stack()
    stack2 = ft.Stack()
    stack3 = ft.Stack()
    stack4 = ft.Stack()

    e1 = ft.Container(top=150, left=35, width=185, height=35, content=Lol)
    e2 = ft.Container(top=65, left=285, width=92, height=35, content=Lol1)
    e3 = ft.Container(top=65, left=387, width=92, height=35, content=Lol2)
    e4 = ft.Container(top=115, left=285, width=92, height=35, content=Lol3)
    e5 = ft.Container(top=115, left=387, width=92, height=35, content=Lol4)

    swch = ft.Switch(top=200, left=35, label="", width=48, height=31, track_outline_color="gray", on_change=full_zp, tooltip=hint)
    swch1 = ft.Switch(top=235, left=35, label="", width=48, height=31, track_outline_color="gray", on_change=bot_tg_special, tooltip=hint1)
    swch2 = ft.Switch(top=270, left=35, label="", width=48, height=31, track_outline_color="gray", on_change=Anti_Lot, tooltip=hint2)
    swch3 = ft.Switch(top=305, left=35, label="", width=48, height=31, track_outline_color="gray", on_change=Swtch, tooltip=hint3)
    swch4 = ft.Switch(top=210, left=290, label="", width=48, height=31, track_outline_color="gray", on_change=api_mode1, tooltip=hint4)
    swch5 = ft.Switch(top=245, left=290, label="", width=48, height=31, track_outline_color="gray", on_change=anti_full, tooltip=hint5)
    swch6 = ft.Switch(top=280, left=290, label="", width=48, height=31, track_outline_color="gray", on_change=api_mode, tooltip=hint6)
    swch7 = ft.Switch(top=315, left=290, label="", width=48, height=31, track_outline_color="gray", on_change=Remove, tooltip=hint7)

    swch_label = ft.Text("Full Request", top=205, left=85)
    swch_label1 = ft.Text("Tg Bot", top=240, left=85)
    swch_label2 = ft.Text("Low Mode", top=275, left=85)
    swch_label3 = ft.Text("Switcher Mode", top=310, left=85)
    swch_label4 = ft.Text("2 Requests", top=215, left=340)
    swch_label5 = ft.Text("AntiFull Mode", top=250, left=340)
    swch_label6 = ft.Text("Api Mode", top=285, left=340)
    swch_label7 = ft.Text("Remove Hints", top=320, left=340)

    check_box = ft.Checkbox(top=150, left=320, label="Random Price", scale=0.89, on_change=check_box_func)
    start_text = ft.Text(top=2, left=68, value="START", weight=ft.FontWeight.BOLD, font_family="Courier New", size=17)
    stop_text = ft.Text(top=2, left=72, value="STOP", weight=ft.FontWeight.BOLD, font_family="Courier New", size=17)

    stack3.controls.extend([start_text, ft.TextButton(text="", on_click=ulov, width=185, height=27)])
    stack4.controls.extend([stop_text, ft.TextButton(text="", on_click=Stop, width=185, height=27)])

    button_container = ft.Container(content=ft.Row(controls=[stack3]), width=185, height=27, padding=0, gradient=ft.LinearGradient(begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1), colors=["#3D017E", "#3a0054", "#570b7a", "#79289e"], tile_mode=ft.GradientTileMode.MIRROR, rotation=math.pi / 3), top=70, left=35, border_radius=20)
    btn2 = ft.Container(content=ft.Row(controls=[stack4]), width=185, height=27, padding=0, gradient=ft.LinearGradient(begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1), colors=["#79289e", "#570b7a", "#3a0054", "#3D017E"], tile_mode=ft.GradientTileMode.MIRROR, rotation=math.pi / 3), top=110, left=35, border_radius=20)

    label = ft.Text(top=8, left=45, value="ZINDORNO 0.03", size=21, color="White", weight=ft.FontWeight.BOLD)
    label1 = ft.Text(top=13, left=283, value="Program has been stopped", size=15, color="red", weight=ft.FontWeight.BOLD)
    label2 = ft.Text(top=-50, left=305, value="Program is enabled", size=16, color="green", weight=ft.FontWeight.BOLD)

    txt_full_req = ft.Text(top=205, left=170, value="(OFF)", size=13, color="Red")
    txt_bot_tele = ft.Text(top=240, left=133, value="(OFF)", size=13, color="Red")
    txt_low_mode = ft.Text(top=275, left=158, value="(OFF)", size=13, color="Red")
    txt_swt_mode = ft.Text(top=310, left=186, value="(OFF)", size=13, color="Red")
    txt_requests = ft.Text(top=215, left=415, value="(OFF)", size=13, color="Red")
    txt_antifull = ft.Text(top=250, left=438, value="(OFF)", size=13, color="Red")
    txt_api_mode = ft.Text(top=285, left=408, value="(OFF)", size=13, color="Red")
    txt_hint_rem = ft.Text(top=320, left=435, value="(OFF)", size=13, color="Red")

    border_side_outside = ft.BorderSide(width=2, color="#570b7a", stroke_align=ft.BorderSideStrokeAlign.INSIDE)
    container1 = ft.Container(top=50, left=15, border_radius=10, width=225, height=300, bgcolor=ft.Colors.TRANSPARENT, border=ft.Border(border_side_outside, border_side_outside, border_side_outside, border_side_outside))
    container2 = ft.Container(top=50, left=270, border_radius=10, width=225, height=132, bgcolor=ft.Colors.TRANSPARENT, border=ft.Border(border_side_outside, border_side_outside, border_side_outside, border_side_outside))
    container3 = ft.Container(top=195, left=270, border_radius=10, width=225, height=162, bgcolor=ft.Colors.TRANSPARENT, border=ft.Border(border_side_outside, border_side_outside, border_side_outside, border_side_outside))

    def _labels(name, booling):
        labels = [txt_full_req, txt_bot_tele, txt_bot_tele, txt_low_mode, txt_swt_mode, txt_requests, txt_antifull, txt_api_mode, txt_hint_rem]
        for label in labels:
            if label == name:
                if booling:
                    label.value = "(ON)"
                    label.color = "Green"
                else:
                    label.value = "(OFF)"
                    label.color = "Red"
                page.update()

    stack.controls.extend([container1, container2, container3,
                           swch, swch1, swch2, swch3, swch4, swch5, swch6, swch7,
                           btn2, button_container,
                           swch_label, swch_label1, swch_label2, swch_label3, swch_label4, swch_label5, swch_label6, swch_label7,
                           label, label1, label2, check_box,
                           txt_full_req, txt_bot_tele, txt_low_mode, txt_swt_mode, txt_requests, txt_antifull, txt_api_mode, txt_hint_rem,
                           e1, e2, e3, e4, e5])

    stack2.controls.extend([ft.Container(top=-10, left=-10, gradient=ft.LinearGradient(begin=ft.Alignment(0, 0), end=ft.Alignment(1, 0.5),
                colors=["#110a1c", "#130c1f", "#140d21", "#160f24", "#181026", "#211533"],
                tile_mode=ft.GradientTileMode.CLAMP), width=510, height=420, content=ft.Column([stack]))])

    page.add(stack2)

ft.app(main)