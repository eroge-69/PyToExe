import cv2
import numpy as np
import pyautogui
import time

# Disable PyAutoGUI delays for speed
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = True  # Move mouse to top-left to emergency stop

# Screen setup (1920x1080, center at 960x540)
center_x, center_y = 960, 540
crop_size = 200  # Half-size of capture region (400x400 total)
radius = 150  # Circle radius; adjust based on minigame size

# Light blue HSV range (tune with a screenshot if needed; ~cyan-blue)
lower_blue = np.array([90, 50, 50])
upper_blue = np.array([130, 255, 255])

# Detection tolerance
tolerance = 5  # Degrees for bar-zone overlap

def get_bar_angle(edges, local_cx, local_cy):
    """Detect bar angle using Hough lines (assumes radial line from center)."""
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=50,  # Min votes for line; increase if noisy
        minLineLength=100,  # Min bar length; ~2/3 radius
        maxLineGap=10
    )
    if lines is None:
        return None
    
    for line in lines:
        x1, y1, x2, y2 = line[0]
        dist1 = np.sqrt((x1 - local_cx)**2 + (y1 - local_cy)**2)
        dist2 = np.sqrt((x2 - local_cx)**2 + (y2 - local_cy)**2)
        if min(dist1, dist2) < 20:  # One end near center
            # Use farther end for angle
            if dist1 < dist2:
                dx, dy = x2 - local_cx, y2 - local_cy
            else:
                dx, dy = x1 - local_cx, y1 - local_cy
            angle = np.arctan2(dy, dx) * 180 / np.pi
            if angle < 0:
                angle += 360
            return angle
    return None

def get_zone_angles(img_hsv, local_cx, local_cy, r):
    """Sample perimeter for light blue zone; return start/end angles (degrees)."""
    angles_rad = np.linspace(0, 2 * np.pi, 360, endpoint=False)
    blue_angles = []
    for theta in angles_rad:
        x = int(local_cx + r * np.cos(theta))
        y = int(local_cy + r * np.sin(theta))
        h, w = img_hsv.shape[:2]
        if 0 <= x < w and 0 <= y < h:
            pixel = img_hsv[y, x]
            if (lower_blue <= pixel).all() and (pixel <= upper_blue).all():
                blue_angles.append(theta * 180 / np.pi)
    
    if not blue_angles:
        return None, None
    
    blue_angles = np.array(blue_angles)
    min_a, max_a = np.min(blue_angles), np.max(blue_angles)
    if max_a - min_a < 180:  # Assume single arc < half-circle
        return min_a, max_a
    return None, None  # Wrapped or invalid zone

def is_in_zone(bar_angle, zone_start, zone_end):
    """Check if bar angle overlaps zone (handle 0-360 wrap)."""
    if zone_start > zone_end:
        zone_end += 360
    if bar_angle < zone_start:
        bar_angle += 360
    return zone_start - tolerance <= bar_angle <= zone_end + tolerance

# Main loop
print("Auto-lockpick started. Minigame must be visible. Ctrl+C to stop.")
try:
    while True:
        # Capture center region
        screenshot = pyautogui.screenshot(region=(center_x - crop_size, center_y - crop_size, 2 * crop_size, 2 * crop_size))
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Local center in cropped image
        local_cx, local_cy = crop_size, crop_size
        
        # Detect bar and zone
        bar_angle = get_bar_angle(edges, local_cx, local_cy)
        zone_start, zone_end = get_zone_angles(img_hsv, local_cx, local_cy, radius)
        
        if bar_angle is not None and zone_start is not None:
            if is_in_zone(bar_angle, zone_start, zone_end):
                pyautogui.press('e')
                print(f"Pressed E! Bar at {bar_angle:.1f}°, Zone {zone_start:.1f}-{zone_end:.1f}°")
        
        time.sleep(0.01)  # ~100 FPS loop; adjust if too CPU-heavy
        
except KeyboardInterrupt:
    print("Stopped.")