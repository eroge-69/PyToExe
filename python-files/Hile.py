import pymem
import pymem.process
import pygame
import time

# === ASSAULTCUBE SABİT OFFSETS ===
ENTITY_LIST = 0x10F4F8
ENTITY_SIZE = 0x4
POS_X = 0x4
POS_Y = 0x8
POS_Z = 0xC
HEALTH = 0xEC

# === PYGAME EKRAN ===
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("QUANTUM ESP v2")

# === PYMEM BAĞLANTI ===
try:
    pm = pymem.Pymem("ac_client.exe")
    print("✅ AssaultCube bulundu.")
except Exception as e:
    print("❌ Oyun bulunamadı:", e)
    exit()

try:
    base_address = pm.read_int(pm.base_address + ENTITY_LIST)
    print(f"✅ Entity list adresi: {hex(base_address)}")
except Exception as e:
    print("❌ Entity list okunamadı:", e)
    exit()

# === EKRAN DÖNÜŞÜM ===
def world_to_screen(x, y):
    sx = int((x % 1000) / 1000 * 800)
    sy = int((y % 1000) / 1000 * 600)
    return sx, sy

# === ANA DÖNGÜ ===
running = True
while running:
    screen.fill((0, 0, 0))

    for i in range(1, 32):
        try:
            entity = pm.read_int(base_address + i * ENTITY_SIZE)
            if entity == 0:
                continue

            health = pm.read_int(entity + HEALTH)
            if health <= 0 or health > 1337:
                continue

            x = pm.read_float(entity + POS_X)
            y = pm.read_float(entity + POS_Y)
            z = pm.read_float(entity + POS_Z)

            sx, sy = world_to_screen(x, y)
            pygame.draw.rect(screen, (255, 0, 0), (sx, sy, 40, 60), 2)

            print(f"[{i}] HP: {health} | Pos: {x:.1f}, {y:.1f}, {z:.1f}")

        except Exception as e:
            print(f"[{i}] HATA: {e}")
            continue

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    pygame.display.update()
    time.sleep(0.01)

pygame.quit()
