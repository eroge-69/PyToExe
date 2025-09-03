import pyautogui
import time
import math
from pynput.keyboard import Key, Controller
from pynput.mouse import Button, Controller
import keyboard
from win32api import GetKeyState
import win32api
import win32con
mouse = Controller()

print("Input desired speed [normal, fast, slow]--fast recommended")
resp = input()
delayTime = (.01 if resp == "fast" else .015 if resp == "normal" else .02)
delay = delayTime
heal_delay = delayTime
print("macro speed set to " + str(delayTime) + " (" + resp + ")")
boost_spikeu = False

chat_toggle = 0
item = '1'
pittype = 'pit'
insta_type = 'stacked'
boost_spike_delay = .005
boost_spike_delay_int = .005
boost_tospike = .1
bull_helmet = -14.5
turret_gear = -18.5
healer = False
mp = 0
boost = '9'
spike = '7'
food = 'q'
autoheal = False

print('Go Become GOD? lmao')

def press(k, d):
    if k == "space":
        click()
        return
    keyboard.press(k)
    time.sleep(d)
    keyboard.release(k)
    return


def say(t):
    press('enter', .01)
    keyboard.write(t)
    press('enter', .01)
    return


def click():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(.03)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    return


def equip(h):
    mouse.scroll(0, 50)
    time.sleep(.05)
    mouse.scroll(0, h)
    return


def boost_spike(bx, by, sx1, sy1, sx2, sy2, d):
    mouse.position = (bx, by)
    place(boost, d)
    mouse.position = (sx1, sy1)
    place(spike, d)
    mouse.position = (sx2, sy2)
    place(spike, d)
    return


def place(p, d):
    press(p, d)
    press('space', d)
    press(item, d)
    return


def place_boost(d):
    place(boost, d)
    return


def place_spike(d):
    place(spike, d)
    return


while True:
    if keyboard.is_pressed('enter'):
        chat_toggle = 1
    if keyboard.is_pressed('esc'):
        chat_toggle = 0
    if chat_toggle == 0:
        if keyboard.is_pressed('1'):
            item = '1'
        if keyboard.is_pressed('2'):
            item = '2'
        if keyboard.is_pressed('k'):
            autoheal = not autoheal
            while keyboard.is_pressed('k'):
                time.sleep(0)
        if win32api.GetAsyncKeyState(70):  # f
            if keyboard.is_pressed('f'):
                place(boost, delay)
        if win32api.GetAsyncKeyState(86):  # v
            if keyboard.is_pressed('v'):
                place(spike, delay)
        if win32api.GetAsyncKeyState(71):
            if keyboard.is_pressed('g'):
                press("1", delay)
                press("e", delay)
                place(spike, delay)
                time.sleep(.2)
                press("e", delay)
        if win32api.GetAsyncKeyState(81) or autoheal:  # q
            #press('space', heal_delay)
            press('2', heal_delay)
            press('space', heal_delay)
            press(item, heal_delay)
        if healer:
            press('space', heal_delay)
            press('2', heal_delay)
            press('space', heal_delay)
            press(item, heal_delay)
        if keyboard.is_pressed('h'):
            press('8', delay)
            press('space', delay)
            press(item, delay)
        if win32api.GetAsyncKeyState(78):  # n
            if keyboard.is_pressed('n'):
                press('6', delay)
                press('space', delay)
                press(item, delay)
                press("7", delay)
        if keyboard.is_pressed('end'):
            heal_delay = heal_delay+.0053
            say(str(heal_delay))
            while keyboard.is_pressed('end'):
                time.sleep(0)
        if keyboard.is_pressed('home'):
            heal_delay = heal_delay-.005
            say(str(heal_delay))
            while keyboard.is_pressed('home'):
                time.sleep(0)