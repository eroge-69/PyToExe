import time
import pytesseract
from PIL import ImageGrab
import pyautogui

# Interval v sekundách
INTERVAL = 3

# Souřadnice výřezu (levý horní x, y, pravý dolní x, y)
REGION = (672, 384, 1038, 428)

# Soubor, kam se má ukládat výstup
OUTPUT_FILE = 'data.txt'

# Souřadnice kliknutí
CLICK_POSITION = (1231, 426)

# Hlavní smyčka
def main():
    print("Program spuštěn. Ukonči ho zavřením okna nebo stisknutím Ctrl+C.")
    while True:
        # Screenshot výřezu
        screenshot = ImageGrab.grab(bbox=REGION)

        # OCR (rozpoznání textu)
        text = pytesseract.image_to_string(screenshot, lang='eng')

        # Úprava textu: nový řádek → středník
        cleaned_text = text.replace('\n', ';').strip()

        # Zápis do souboru
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            f.write(cleaned_text + '\n')

        # Kliknutí myši
        pyautogui.click(x=CLICK_POSITION[0], y=CLICK_POSITION[1])

        # Čekání
        time.sleep(INTERVAL)

if __name__ == '__main__':
    main()
