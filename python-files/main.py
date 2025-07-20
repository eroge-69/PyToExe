import time
import pyautogui

# Move the mouse to absolute coordinates (x, y) and click
# Example: move to (100, 200) and click

def move_and_click(x: int, y: int, clicks: int = 1, interval: float = 0.0, button: str = 'left'):
    """
    Moves the mouse to the specified (x, y) position and performs clicks.

    Args:
        x (int): The x-coordinate on the screen.
        y (int): The y-coordinate on the screen.
        clicks (int, optional): Number of clicks to perform. Defaults to 1.
        interval (float, optional): Seconds between clicks. Defaults to 0.
        button (str, optional): Button to click: 'left', 'right', or 'middle'. Defaults to 'left'.
    """
    # Move the mouse smoothly over 0.5 seconds
    pyautogui.moveTo(x, y, duration=0.5)
    # Perform the click(s)
    pyautogui.click(x=x, y=y, clicks=clicks, interval=interval, button=button)


if __name__ == '__main__':
    print("You have 5 seconds to switch to the target window...")
    time.sleep(5)
    move_and_click(440, 416, clicks=1, interval=1, button='left') #clicca su chatGPT
    while True:
        colore_notifica = pyautogui.screenshot().getpixel((1750, 436)) #get colore
        
        if colore_notifica == (33, 192, 99):
            move_and_click(2007, 1378, clicks=1, interval=0.25, button='right') #clicca su messaggio

            move_and_click(2070, 950, clicks=1, interval=1, button='left') #copia messaggio

            move_and_click(552, 1341, clicks=1, interval=1, button='right') #clicca su chatGPT

            move_and_click(652, 857, clicks=1, interval=1, button='left') #incolla su chatGPT

            move_and_click(1213, 1414, clicks=1, interval=1, button='left') #invia a chatGPT

            time.sleep(3) #aumentare un pochino dopo

            move_and_click(440, 416, clicks=3, interval=0.3, button='left') #evidenzia il messaggio

            move_and_click(440, 416, clicks=1, interval=1, button='right') #clicca il messaggio

            move_and_click(480, 456, clicks=1, interval=1, button='left') #clicca su copia

            move_and_click(2035, 1472, clicks=1, interval=1, button='right') #whatsapp

            move_and_click(2130, 1293, clicks=1, interval=1, button='left') #incolla su whatsapp

            move_and_click(2500, 1469, clicks=1, interval=1, button='left') #invia su whatsapp

            move_and_click(440, 416, clicks=1, interval=1, button='left') #clicca su chatGPT
        
        time.sleep(2) #10 secondi

