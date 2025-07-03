from PIL import ImageGrab
import pyautogui as pag
import keyboard
import time

# Центр экрана
x = pag.size().width / 2
y = pag.size().height / 2


# Получение цвета пикселей
def get_pixel_color(x, y):
    screenshot = ImageGrab.grab()
    pixel1 = screenshot.getpixel((x-2, y-2))
    pixel2 = screenshot.getpixel((x-2, y+2))``
    pixel3 = screenshot.getpixel((x+2, y-2))
    pixel4 = screenshot.getpixel((x+2, y+2))
    return pixel1, pixel2, pixel3, pixel4

def main():
    while True:
        if keyboard.is_pressed("alt"):
            p1, p2, p3, p4 = get_pixel_color(x,y)

            newp1, newp2, newp3, newp4 = get_pixel_color(x,y)
            if newp1 != p1 and newp1 != (255, 255, 255):
                time.sleep(0.2)
                pag.leftClick()
            elif newp2 != p2 and newp2 != (255, 255, 255):
                time.sleep(0.2)
                pag.leftClick()
            elif newp3 != p3 and newp3 != (255, 255, 255):
                time.sleep(0.2)
                pag.leftClick()
            elif newp4 != p4 and newp4 != (255, 255, 255):
                time.sleep(0.2)
                pag.leftClick()

        if keyboard.is_pressed("l"):
            break
if __name__ == "__main__":
    main()
