
import pyautogui
import keyboard
import time
import threading

aktif = False
ilk_giris = True
komutlar = {
    'zıpla': 'ctrl+shift+z',
    'yürü': 'ctrl+shift+w',
    'dur': 'ctrl+shift+s',
    'odun': 'ctrl+shift+o',
    'obsidyen': 'ctrl+shift+b',
    'envanter': 'ctrl+shift+e',
    'tplen': 'ctrl+shift+t'
}

def giris_yap():
    global ilk_giris
    print("5 saniye içinde Minecraft'ı aç ve karakterle sunucuya gir.")
    time.sleep(5)
    if ilk_giris:
        pyautogui.write('/register chatgpt34 chatgpt34')
        pyautogui.press('enter')
        ilk_giris = False
    else:
        pyautogui.write('/login chatgpt34')
        pyautogui.press('enter')
    time.sleep(2)
    pyautogui.write('/tpa ReyKaan1545')
    pyautogui.press('enter')
    print("Komut bekleniyor...")

def komut_dinle():
    global aktif
    while True:
        if keyboard.is_pressed(komutlar['zıpla']):
            print("Zıplama başlatıldı.")
            aktif = True
            while aktif:
                pyautogui.press('space')
                time.sleep(0.5)

        elif keyboard.is_pressed(komutlar['yürü']):
            print("Yürümeye başladı.")
            aktif = True
            pyautogui.keyDown('w')
            while aktif:
                time.sleep(0.1)
            pyautogui.keyUp('w')

        elif keyboard.is_pressed(komutlar['dur']):
            print("Bot durduruldu.")
            aktif = False

        elif keyboard.is_pressed(komutlar['odun']):
            print("Odun toplama başladı.")
            aktif = True
            pyautogui.write('/warp oduncu')
            pyautogui.press('enter')
            time.sleep(3)
            while aktif:
                pyautogui.mouseDown()
                time.sleep(5)
                pyautogui.mouseUp()
                time.sleep(1)

        elif keyboard.is_pressed(komutlar['obsidyen']):
            print("Obsidyen toplama başladı.")
            aktif = True
            pyautogui.write('/warp edit')
            pyautogui.press('enter')
            time.sleep(3)
            while aktif:
                pyautogui.mouseDown()
                time.sleep(5)
                pyautogui.mouseUp()
                time.sleep(1)

        elif keyboard.is_pressed(komutlar['envanter']):
            print("Envanter boşaltılıyor.")
            pyautogui.press('e')  # envanter aç
            time.sleep(1)
            for i in range(20):
                pyautogui.keyDown('shift')
                pyautogui.click()
                pyautogui.keyUp('shift')
                time.sleep(0.1)
            pyautogui.press('e')  # envanter kapat

        elif keyboard.is_pressed(komutlar['tplen']):
            print("TPA gönderiliyor.")
            pyautogui.write('/tpa ReyKaan1545')
            pyautogui.press('enter')

        time.sleep(0.1)

# Başlatıcı
giris_yap()
komut_thread = threading.Thread(target=komut_dinle)
komut_thread.start()
