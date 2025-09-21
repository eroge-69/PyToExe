import time
import cv2
import numpy as np
from mss import mss

# ===== CONFIG =====
alive_template_path = "alive_template.png"  # small image of boss HP bar or unique UI
region = {"left": 500, "top": 160, "width": 920, "height": 120}  # screen region to search
threshold = 0.8   # template matching threshold (0.7-0.95)
respawn_seconds = 15 * 60  # 15 minutes
dead_confirm_needed = 3    # number of consecutive misses to confirm death

# ===== SETUP =====
sct = mss()
alive_template = cv2.imread(alive_template_path, cv2.IMREAD_GRAYSCALE)
template_h, template_w = alive_template.shape

fight_active = False
dead_debounce = 0

print("Starting boss monitor. Press Ctrl+C to exit.")

try:
    while True:
        # Capture screen region
        screenshot = np.array(sct.grab(region))[:, :, :3]
        screen_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        # Template matching
        res = cv2.matchTemplate(screen_gray, alive_template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)

        found_alive = len(loc[0]) > 0

        if found_alive:
            dead_debounce = 0
            if not fight_active:
                fight_active = True
                start_time = time.time()
                print("Boss detected — fight timer started.")
            else:
                elapsed = time.time() - start_time
                print(f"\rFight ongoing — {int(elapsed)//60:02d}:{int(elapsed)%60:02d}", end="")
        else:
            if fight_active:
                dead_debounce += 1
                if dead_debounce >= dead_confirm_needed:
                    fight_active = False
                    fight_seconds = int(time.time() - start_time)
                    print(f"\nBoss defeated in {fight_seconds//60:02d}:{fight_seconds%60:02d}")
                    respawn_end = time.time() + respawn_seconds
                    # Respawn countdown
                    while time.time() < respawn_end:
                        remaining = int(respawn_end - time.time())
                        print(f"\rRespawn in {remaining//60:02d}:{remaining%60:02d}", end="")
                        time.sleep(1)
                    print("\nRespawn time reached. Monitoring resumed.")
        time.sleep(0.15)

except KeyboardInterrupt:
    print("\nMonitoring stopped.")