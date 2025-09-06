try:
    import fade
    import colorama
    from colorama import Fore
    import time
    import os
    from pynput.mouse import Listener as MouseListener
    from pynput.mouse import Button
    from pynput import keyboard
    from pynput.mouse import Controller
except:
    os.system('pip install fade')
    os.system('pip install colorama')
    os.system('pip install time')
    os.system('pip install pynput')

colorama.init()
keyboard_controller = keyboard.Controller()
mouse = Controller()

print(Fore.BLUE + "SOURCE: @XORA // discord.gg/Xora (python 1st person macro)" + Fore.RESET)

question = input(Fore.WHITE+"If you want to use mouse buttons type below (mouse) next to 'KEYBINDS'. \nOr if you want to use a keyboard keybind type your keybind below.\n\nKEYBIND: ").lower()

key_to_start = None

if question == "mouse":
    middlemousebutton = input("Enter your preferred MouseButton: (Middle, M1, or M2): ").lower()
    if middlemousebutton == "middle":
        key_to_start = Button.middle
    elif middlemousebutton == "m1":
        key_to_start = Button.x1
    elif middlemousebutton == "m2":
        key_to_start = Button.x2
else:
    key_to_start = keyboard.KeyCode.from_char(question)

mode = input("Do you want the macro to toggle or hold? (toggle/hold): ").lower()

macro_enabled = False

def on_press(key):
    global macro_enabled
    try:
        if key == key_to_start:
            if mode == "toggle":
                macro_enabled = not macro_enabled
            elif mode == "hold":
                macro_enabled = True
            print_status()
    except AttributeError:
        pass

def on_release(key):
    global macro_enabled
    if mode == "hold" and key == key_to_start:
        macro_enabled = False
        print_status()

def print_status():
    os.system("cls")
    fade.water(f"Press {key_to_start} to {mode} the macro.\n")
    if macro_enabled:
        print(Fore.BLUE + "SOURCE: @FWAKAAZZ // discord.gg/akaazz (python 1st person macro)" + Fore.RESET)
        print(Fore.GREEN + "MACRO RUNNING" + Fore.RESET)
    else:
        print(Fore.BLUE + "SOURCE: @FWAKAAZZ // discord.gg/akaazz (python 1st person macro)" + Fore.RESET)
        print(Fore.RED + "MACRO STOPPED" + Fore.RESET)
def run_macro():
    if macro_enabled:
        mouse.scroll(0, 0)
        time.sleep(0.004)

        mouse.scroll(0, 1)
        time.sleep(0.004)

        mouse.scroll(0, -1)
        time.sleep(0.004)

        mouse.scroll(0, 0)
        time.sleep(0.004)

def on_click(x, y, button, pressed):
    global macro_enabled
    if button == key_to_start:
        if mode == "toggle" and pressed:
            macro_enabled = not macro_enabled
        elif mode == "hold":
            macro_enabled = pressed
        print_status()

def main():
    print_status()

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener, MouseListener(on_click=on_click) as mouse_listener:
        while True:
            run_macro()
            time.sleep(0.01)

if __name__ == "__main__":
    main()

input()
