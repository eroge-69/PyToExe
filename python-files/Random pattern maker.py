import cv2
import numpy as np
import math
import random

# -----------------------------
# Professional Screensaver
# -----------------------------
# Full screen dimensions
screen_res = (1920, 1080)  # You can adapt to your screen, e.g., MacBook 14" 3024x1964
width, height = screen_res

num_waves = 6
num_circles = 6
num_rects = 8
trail_strength = 0.85  # Controls fading of previous frames
t = 0
speed = 0.05

# Initialize window full-screen
cv2.namedWindow("Professional Screensaver", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Professional Screensaver", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Initialize moving circles data
circles = []
for i in range(num_circles):
    radius = random.randint(30, 60)
    circles.append({
        "radius": radius,
        "angle": random.uniform(0, 2*math.pi),
        "speed": random.uniform(0.02, 0.08),
        "phase": random.uniform(0, 2*math.pi)
    })

# Initialize rectangles data
rects = []
for i in range(num_rects):
    rects.append({
        "x": random.randint(0, width),
        "y": random.randint(0, height),
        "w": random.randint(40, 120),
        "h": random.randint(20, 80),
        "dx": random.uniform(-2,2),
        "dy": random.uniform(-2,2),
        "color_phase": random.uniform(0, 2*math.pi)
    })

# Initialize blank frame
frame = np.zeros((height, width, 3), dtype=np.float32)

try:
    while True:
        # 1. Fade previous frame
        frame = frame * trail_strength

        # 2. Draw sine waves
        for i in range(num_waves):
            color = np.array([
                128 + 127 * math.sin(t + i),
                128 + 127 * math.sin(t + i + 2),
                128 + 127 * math.sin(t + i + 4)
            ])
            amplitude = 50 + i*20
            frequency = 0.01 + i*0.005
            phase = t + i
            for x in range(0, width, 3):
                y = int(height/2 + amplitude * math.sin(frequency * x + phase))
                if 0 <= y < height:
                    frame[y, x] = color

        # 3. Draw moving circles
        for c in circles:
            center_x = int((width/2) + (width/3) * math.sin(t*c["speed"] + c["phase"]))
            center_y = int((height/2) + (height/3) * math.cos(t*c["speed"] + c["phase"]))
            color = np.array([
                128 + 127 * math.sin(t + c["angle"]),
                128 + 127 * math.sin(t + c["angle"] + 2),
                128 + 127 * math.sin(t + c["angle"] + 4)
            ])
            cv2.circle(frame, (center_x, center_y), c["radius"], color.tolist(), 2)

        # 4. Draw moving rectangles
        for r in rects:
            r["x"] += r["dx"]
            r["y"] += r["dy"]

            # Wrap around screen edges
            if r["x"] < 0: r["x"] = width
            if r["x"] > width: r["x"] = 0
            if r["y"] < 0: r["y"] = height
            if r["y"] > height: r["y"] = 0

            color = np.array([
                128 + 127 * math.sin(t + r["color_phase"]),
                128 + 127 * math.sin(t + r["color_phase"] + 2),
                128 + 127 * math.sin(t + r["color_phase"] + 4)
            ])
            top_left = (int(r["x"]), int(r["y"]))
            bottom_right = (int(r["x"]+r["w"]), int(r["y"]+r["h"]))
            cv2.rectangle(frame, top_left, bottom_right, color.tolist(), 2)

        # 5. Display frame
        display_frame = np.clip(frame, 0, 255).astype(np.uint8)
        cv2.imshow("Professional Screensaver", display_frame)

        # 6. Increment time
        t += speed

        # 7. Exit if 'q' pressed
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("\nScreensaver stopped by user.")

cv2.destroyAllWindows()
