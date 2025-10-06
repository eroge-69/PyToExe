import pyautogui as pag
import random as rd
import time as tm
import vgamepad as vg
import keyboard as kb

gamepad = vg.VX360Gamepad()

pag.hotkey('alt', 'tab')

tm.sleep(1)

action = rd.randint(1, 7)
while True:
        gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
        gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
        gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
        gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
        gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
        if action == 1:
            gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
            print("right")
        elif action == 2:
            gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
            print("left")  
        elif action == 3:
            gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
            print("up")
        elif action == 4:
            gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
            print("down")
        elif action == 5:
            gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
            print("jump")
        elif action == 6:
            gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
            print("dash")
        elif action == 7:
            gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
            print("climb")

        gamepad.update()
        tm.sleep(0.2)
        gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
        gamepad.update()
        if kb.is_pressed('q'):
            break
        action = rd.randint(1, 7)
        tm.sleep(0.8)