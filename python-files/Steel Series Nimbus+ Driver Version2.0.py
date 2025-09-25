import sys
import time
import joystickapi as joy
import vgamepad as vg
import keyboard as key
import customtkinter as ctk
import threading

gamepad = vg.VX360Gamepad()

# Default button mappings
default_button_mappings = {
    "A": vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
    "B": vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
    "X": vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
    "Y": vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
    "LB": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
    "RB": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
    "LT": "LT",
    "RT": "RT",
    "START": vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
    "BACK": vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
    "DPAD_UP": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
    "DPAD_DOWN": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
    "DPAD_LEFT": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
    "DPAD_RIGHT": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
    "LEFT_THUMB": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
    "RIGHT_THUMB": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB
}

button_mappings = default_button_mappings.copy()

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
                    gamepad.press_button(button=button_mappings["LB"])
                else:
                    gamepad.release_button(button=button_mappings["LB"])

                if info.dwButtons & 32:
                    gamepad.press_button(button=button_mappings["RB"])
                else:
                    gamepad.release_button(button=button_mappings["RB"])

                if info.dwButtons & 16384:
                    key.press("win+g")

                if info.dwButtons & 65536:
                    gamepad.press_button(button=button_mappings["START"])
                else:
                    gamepad.release_button(button=button_mappings["START"])

                if info.dwButtons & 32768:
                    gamepad.press_button(button=button_mappings["BACK"])
                else:
                    gamepad.release_button(button=button_mappings["BACK"])

                if info.dwButtons & 2048:
                    gamepad.press_button(button=button_mappings["DPAD_DOWN"])
                else:
                    gamepad.release_button(button=button_mappings["DPAD_DOWN"])

                if info.dwButtons & 4096:
                    gamepad.press_button(button=button_mappings["DPAD_RIGHT"])
                else:
                    gamepad.release_button(button=button_mappings["DPAD_RIGHT"])

                if info.dwButtons & 1024:
                    gamepad.press_button(button=button_mappings["DPAD_LEFT"])
                else:
                    gamepad.release_button(button=button_mappings["DPAD_LEFT"])

                if info.dwButtons & 8192:
                    gamepad.press_button(button=button_mappings["DPAD_UP"])
                else:
                    gamepad.release_button(button=button_mappings["DPAD_UP"])

                if info.dwButtons & 1:
                    gamepad.press_button(button=button_mappings["A"])
                else:
                    gamepad.release_button(button=button_mappings["A"])

                if info.dwButtons & 2:
                    gamepad.press_button(button=button_mappings["B"])
                else:
                    gamepad.release_button(button=button_mappings["B"])

                if info.dwButtons & 4:
                    gamepad.press_button(button=button_mappings["X"])
                else:
                    gamepad.release_button(button=button_mappings["X"])

                if info.dwButtons & 8:
                    gamepad.press_button(button=button_mappings["Y"])
                else:
                    gamepad.release_button(button=button_mappings["Y"])

                if info.dwButtons & 512:
                    gamepad.press_button(button=button_mappings["RIGHT_THUMB"])
                else:
                    gamepad.release_button(button=button_mappings["RIGHT_THUMB"])

                if info.dwButtons & 256:
                    gamepad.press_button(button=button_mappings["LEFT_THUMB"])
                else:
                    gamepad.release_button(button=button_mappings["LEFT_THUMB"])
                gamepad.update()

        except (KeyboardInterrupt, SystemExit):
            break

def start_program():
    threading.Thread(target=main).start()

def stop_program():
    sys.exit()

def update_mapping(button, mapping):
    button_mappings[button] = default_button_mappings[mapping]

def reset_mappings():
    global button_mappings
    button_mappings = default_button_mappings.copy()
    for button, option_menu in option_menus.items():
        option_menu.set(button)

# GUI setup
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue")

root = ctk.CTk()
root.title("Steel series Nimbus+ controller driver version 2.0")

# Main frame
main_frame = ctk.CTkFrame(master=root)
main_frame.pack(pady=20, padx=60, fill="both", expand=True)

label = ctk.CTkLabel(master=main_frame, text="Steel Series Nimbus+", font=("Franklin Gothic Medium", 24))
label.pack(pady=12, padx=10)

start_button = ctk.CTkButton(master=main_frame, text="Start", command=start_program)
start_button.pack(pady=10)

stop_button = ctk.CTkButton(master=main_frame, text="Stop", command=stop_program)
stop_button.pack(pady=10)

remap_button = ctk.CTkButton(master=main_frame, text="Remap Buttons", command=lambda: show_frame(remap_frame))
remap_button.pack(pady=10)

# Remap frame
remap_frame = ctk.CTkFrame(master=root)

label = ctk.CTkLabel(master=remap_frame, text="Remap Buttons", font=("Roboto", 24))
label.pack(pady=12, padx=10)

buttons = ["A", "B", "X", "Y", "LB", "RB", "LT", "RT", "START", "BACK", "DPAD_UP", "DPAD_DOWN", "DPAD_LEFT", "DPAD_RIGHT", "LEFT_THUMB", "RIGHT_THUMB"]
mappings = ["A", "B", "X", "Y", "LB", "RB", "LT", "RT", "START", "BACK", "DPAD_UP", "DPAD_DOWN", "DPAD_LEFT", "DPAD_RIGHT", "LEFT_THUMB", "RIGHT_THUMB"]

option_menus = {}

for button in buttons:
    frame = ctk.CTkFrame(master=remap_frame)
    frame.pack(pady=5, padx=10, fill="x")

    label = ctk.CTkLabel(master=frame, text=f"Map {button} to:")
    label.pack(side="left", padx=10)

    option_menu = ctk.CTkOptionMenu(master=frame, values=mappings, command=lambda mapping, b=button: update_mapping(b, mapping))
    option_menu.pack(side="right", padx=10)
    option_menu.set(button)
    option_menus[button] = option_menu

reset_button = ctk.CTkButton(master=remap_frame, text="Reset to Default", command=reset_mappings)
reset_button.pack(pady=10)

back_button = ctk.CTkButton(master=remap_frame, text="Back", command=lambda: show_frame(main_frame))
back_button.pack(pady=10)

def show_frame(frame):
    frame.tkraise()

for frame in (main_frame, remap_frame):
    frame.grid(row=0, column=0, sticky='nsew')

show_frame(main_frame)

root.mainloop()
