from pynput.keyboard import Controller, Key
import time


time.sleep(5)



keyboard = Controller()


with keyboard.pressed(Key.cmd_l):
    keyboard.press('r')
    keyboard.release('r')

time.sleep(0.5)


keyboard.type('cmd')
keyboard.press(Key.enter)
keyboard.release(Key.enter)

time.sleep(1)


keyboard.type('color 2')
keyboard.press(Key.enter)
keyboard.release(Key.enter)
time.sleep(0.5)
keyboard.type('cd')
keyboard.press(Key.enter)
keyboard.release(Key.enter)
time.sleep(0.5)
keyboard.type('dir/s')
keyboard.press(Key.enter)
keyboard.release(Key.enter)



