import pyperclip as clip
import keyboard
import time
import math

# Stores the copied command from clipboard
command = []
i = 0

print("This is Minecraft Stronghold Finder")
print("For help, press Ctrl+h")
chat = input("Enter the chat open key: ")


def copy():
    """
    Copies the last F3+C output from clipboard and parses x, z, yaw.
    Returns (x, z, yaw) as floats.
    """
    copied_line = clip.paste()
    command[:] = copied_line.split(' ')
    try:
        x = float(command[6])
        z = float(command[8])
        yaw = float(command[9])
        return x, z, yaw
    except (IndexError, ValueError):
        print("Error: Command not copied")
        x = 0
        z = 0
        yaw = 0
    return x, z, yaw


def maths():
    """
    Calculates the estimated stronghold position based on two F3+C readings.
    Returns (delta_x, delta_z, neither_x, neither_z).
    """
    theta = yaw - yaw1
    AB = math.sqrt((x1 - x) ** 2 + (z1 - z) ** 2)
    BC = AB / math.sin(math.radians(theta))
    vtheta = yaw1
    delta_x = x1 - math.sin(math.radians(vtheta)) * BC
    delta_z = z1 + math.cos(math.radians(vtheta)) * BC
    neither_x = delta_x / 8
    neither_z = delta_z / 8
    return delta_x, delta_z, neither_x, neither_z


while True:
    # First F3+C: get first position and yaw, prompt user to turn
    if keyboard.is_pressed('f3') and keyboard.is_pressed('c') and i == 0:
        print("F3+C detected!")
        time.sleep(0.5)  # Wait for clipboard to update
        x, z, yaw = copy()
        print(f"x: {x}, z: {z}, yaw: {yaw}")
        # Calculate new yaw for user to turn to
        new_yaw = ((yaw + 90 + 180) % 360) - 180
        keyboard.press_and_release(chat)
        time.sleep(0.1)
        keyboard.write(f"Turn to {new_yaw}")
        time.sleep(0.1)
        time
        keyboard.press_and_release('enter')
        i = 1
    # Second F3+C: get second position and yaw, calculate stronghold location
    elif keyboard.is_pressed('f3') and keyboard.is_pressed('c') and i == 1:
        print("F3+C detected again!")
        time.sleep(0.5)
        x1, z1, yaw1 = copy()
        print(f"x1: {x1}, z1: {z1}, yaw: {yaw1}")
        delta_x, delta_z, neither_x, neither_z = maths()
        keyboard.press_and_release(chat)
        time.sleep(0.1)
        keyboard.write(
            f"Stronghold is approximately at: {delta_x} ~ {delta_z}  Nether: {neither_x} ~ {neither_z}"
        )
        i = 0
    # Reset state if F3+= is pressed
    elif keyboard.is_pressed('f3') and keyboard.is_pressed('='):
        i = 0
        print("Resetting...")
        time.sleep(0.5)
    elif keyboard.is_pressed('ctrl') and keyboard.is_pressed('h'):
        print("""Help: 
      1. Press F3
      Press F3+C to copy coordinates while looking at the ender eye.
      Then turn to the direction indicated by the chat message and sprint and jump.
      Press F3+C again to copy the second set of coordinates.
      The stronghold location will be calculated and displayed in chat.
      Press F3+= to reset the state.""")
        time.sleep(0.5)

    time.sleep(0.01)
