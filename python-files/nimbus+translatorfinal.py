import sys
import time
import joystickapi as joy
import vgamepad as vg
import keyboard as key
import pyautogui
gamepad = vg.VX360Gamepad()

def main():
    num = joy.joyGetNumDevs()
    ret, caps, startinfo = False, None, None

    for id in range(num):
        ret, caps = joy.joyGetDevCaps(id)
        if ret:
            print(f"Gamepad detected: {caps.szPname}")
            ret, startinfo = joy.joyGetPosEx(id)
            break
    else:
        print("No gamepad detected.")
        sys.exit()

    while True:
        try:
            time.sleep(0.1)
            ret, info = joy.joyGetPosEx(id)
            if ret:
                # Map left joystick data
                left_x_value = int((info.dwXpos - 32768) * 32767 / 32768)
                left_y_value = int((info.dwYpos - 32768) * 32767 / 32768)
                gamepad.left_joystick(x_value=left_x_value, y_value=left_y_value)

                # Map right joystick data
                right_x_value = int((info.dwZpos - 32768) * 32767 / 32768)
                right_y_value = int((info.dwRpos - 32768) * 32767 / 32768)
                gamepad.right_joystick(x_value=right_x_value, y_value=right_y_value)

                if info.dwButtons & 128:
                    gamepad.left_trigger(value=255)
                    
                else:
                    gamepad.left_trigger(value=0)
                    

                if info.dwButtons & 64:
                    gamepad.right_trigger(value=255)
                   
                else:
                    gamepad.right_trigger(value=0)
                   

                if info.dwButtons & 16:
                    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
                    
                else:
                    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
                    

                if info.dwButtons & 32:
                    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
                    
                else:
                    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
                    
                if info.dwButtons & 16384:
                    key.press("win+g")
                    
                    
                    
                if info.dwButtons & 65536:
                    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_START)
                 
                else:
                    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_START)
                    
                if info.dwButtons & 32768:
                    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK)
                   
                    
                else:
                    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK)
                    
                if info.dwButtons & 2048:
                    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
                  
                    
                else:
                    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
                    
                if info.dwButtons & 4096:
                    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
                   
                    
                else:
                    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
                   
                if info.dwButtons & 1024:
                    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
                   
                    
                else:
                    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
                 
                if info.dwButtons & 8192:
                    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
     
                    
                    
                else:
                    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
                
                if info.dwButtons & 1:
                    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
                    
                    
                else:
                    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
                if info.dwButtons & 2:
                    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
                    
                    
                else:
                    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
                if info.dwButtons & 4:
                    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
                    
                    
                else:
                    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
                if info.dwButtons & 8:
                    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
                    
                    
                else:
                    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
                
                if info.dwButtons & 512:
                    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB)
                    
                    
                else:
                    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB)
                
                if info.dwButtons & 256:
                    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB)
                    
                    
                else:
                    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB)
                gamepad.update()


        except (KeyboardInterrupt, SystemExit):
            break

if __name__ == "__main__":
    main()
