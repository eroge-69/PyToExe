import pyautogui
import cv2
import numpy as np
import time
from PIL import ImageGrab

def mob_bul_ve_saldir(mob_gorsel, hassasiyet=0.8):
    ekran = ImageGrab.grab()
    ekran_np = np.array(ekran)
    ekran_gray = cv2.cvtColor(ekran_np, cv2.COLOR_BGR2GRAY)

    mob_template = cv2.imread(mob_gorsel, 0)
    sonuc = cv2.matchTemplate(ekran_gray, mob_template, cv2.TM_CCOEFF_NORMED)

    konumlar = np.where(sonuc >= hassasiyet)
    for pt in zip(*konumlar[::-1]):
        merkez = (pt[0] + mob_template.shape[1]//2, pt[1] + mob_template.shape[0]//2)
        pyautogui.moveTo(merkez)
        pyautogui.click()
        print("Mob bulundu ve tıklandı.")
        return True
    return False

def hp_kontrolu_ve_pot_bas():
    # HP kontrolünü sen yapacaksın, bu placeholder olarak bırakıldı
    pyautogui.press("1")
    print("Pot basıldı (örnek).")

def main():
    while True:
        mob_bul_ve_saldir("mob1.png")
        hp_kontrolu_ve_pot_bas()
        pyautogui.press("z")
        time.sleep(5)

if __name__ == "__main__":
    main()
