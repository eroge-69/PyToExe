# dualsense_right_stick_filter.py
# Gereksinimler: Python 3.8+, pygame, vgamepad, ViGEmBus (Windows için)
# pip install pygame vgamepad

import time
import sys

try:
    import pygame
except Exception as e:
    print("pygame yok veya yüklenemedi. Yüklemek için: pip install pygame")
    raise

try:
    import vgamepad as vg
    VGAME_AVAILABLE = True
except Exception:
    VGAME_AVAILABLE = False

# ======= KONFİGÜRASYON =======
# Sağ analog X ekseni indeksini buraya koy (program başında otomatik gösterilecek)
right_stick_x_axis = None  # None -> program açılışında hangi eksenin sağ analog x olduğuna karar verip ayarlayabilirsin

# İstenilen davranış:
# "clamp_zero" -> negatif X değerlerini (sola) tamamen 0 yapar
# "soft" -> sola yönündeki değerleri yumuşatır (low-pass + clamp min)
MODE = "clamp_zero"

# Eğer MODE == "soft" ise kullanılacak ayarlar:
soft_alpha = 0.2          # low-pass filtresi katsayısı (0..1). Küçük -> daha yumuşak
soft_neg_clamp = -0.25    # -X tarafında izin verilecek en negatif değer

# Döngü gecikmesi (saniye)
LOOP_DELAY = 1.0 / 120.0  # 120 Hz

# Hangi joysticki kullanmak istersin (0 = ilk görülen)
JOYSTICK_INDEX = 0
# =============================

def print_info(joy):
    print("Cihaz bulundu:")
    print("Name:", joy.get_name())
    axes = joy.get_numaxes()
    buttons = joy.get_numbuttons()
    hats = joy.get_numhats()
    print(f"Açık: axes={axes}, buttons={buttons}, hats={hats}")
    print("Her eksenin anlık değerlerini görmek için Ctrl+C ile durdurup doğru eksen indeksini not et.")
    print("Eksen indeksleri 0..n şeklindedir.")

def main():
    global right_stick_x_axis

    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("Hiç joystick bulunamadı. DualSense bağlı mı kontrol et.")
        return

    joystick = pygame.joystick.Joystick(JOYSTICK_INDEX)
    joystick.init()

    print_info(joystick)

    if right_stick_x_axis is None:
        print("\nSağ analogu sola/sağa oynat, hangi eksenin değiştiğini 5 sn boyunca izle.")
        t0 = time.time()
        try:
            while time.time() - t0 < 5.0:
                pygame.event.pump()
                axes = joystick.get_numaxes()
                vals = [round(joystick.get_axis(i), 3) for i in range(axes)]
                print("axes:", vals, end="\r")
                time.sleep(0.05)
            print("\nBitti. Sağ analog X ekseni indexini bul ve kodda right_stick_x_axis değişkenine yaz.")
        except KeyboardInterrupt:
            print("\nManuel durduruldu.")
        return

    if VGAME_AVAILABLE:
        try:
            gamepad = vg.VX360Gamepad()
            print("Sanal XInput gamepad yaratıldı (VX360Gamepad).")
        except Exception as e:
            print("ViGEm başlatılamadı:", e)
            gamepad = None
    else:
        gamepad = None
        print("vgamepad bulunamadı. Sadece okuma yapılacak.")

    last_filtered_x = 0.0
    print("Filtre çalışıyor. MODE =", MODE)
    try:
        while True:
            pygame.event.pump()
            raw_x = joystick.get_axis(right_stick_x_axis)  # -1.0 .. 1.0
            if MODE == "clamp_zero":
                out_x = max(raw_x, 0.0)
            elif MODE == "soft":
                last_filtered_x = (1 - soft_alpha) * last_filtered_x + soft_alpha * raw_x
                out_x = max(last_filtered_x, soft_neg_clamp)
            else:
                out_x = raw_x

            if gamepad is not None:
                try:
                    raw_y = joystick.get_axis(right_stick_x_axis + 1) if joystick.get_numaxes() > right_stick_x_axis + 1 else 0.0
                    gamepad.right_joystick_float(x_value_float=out_x, y_value_float=raw_y)
                    gamepad.update()
                except Exception:
                    pass

            print(f"\rraw_x={raw_x:+.3f} -> out_x={out_x:+.3f}    ", end="")
            time.sleep(LOOP_DELAY)

    except KeyboardInterrupt:
        print("\nÇıkış yapılıyor...")
    finally:
        joystick.quit()
        pygame.quit()

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        try:
            right_stick_x_axis = int(sys.argv[1])
        except:
            pass
    main()
