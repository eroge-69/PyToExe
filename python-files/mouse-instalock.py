import pyautogui
import time

# Ajan adına göre ilk konumlar
ajan_konumlari = {
    "reyna": (285, 649),
    "jett": (85, 550),
    "yoru": (183, 843),
    "neon": (285, 550),
    "clove": (384, 350),
    "cypher": (87, 453),
    "fade": (185, 450),
    "sage": (380, 650),
    "sova": (180, 750),
    "ıso": (380, 450),
    "killjoy": (185, 450),
    "breach": (90, 350),
    "gekko": (285, 450),
    "chamber": (280, 350),
    "waylay": (85, 845)
}

ikinci_konum = (951, 754)
click_delay = 0.001
duration = 0
total_time = 5

ajan = input("Hangi ajanı istersin? (" + " / ".join(ajan_konumlari.keys()) + "): ").lower()

if ajan in ajan_konumlari:
    ilk_konum = ajan_konumlari[ajan]
    start_time = time.time()

    while time.time() - start_time < total_time:
        pyautogui.moveTo(*ilk_konum, duration=duration)
        pyautogui.click()
        time.sleep(click_delay)

        pyautogui.moveTo(*ikinci_konum, duration=duration)
        pyautogui.click()
        time.sleep(click_delay)
else:
    print("Geçersiz ajan ismi. Mevcut ajanlar:", ", ".join(ajan_konumlari.keys()))
