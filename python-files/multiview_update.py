import cv2
import numpy as np
from PIL import ImageGrab

# Configuration
GRID_SPACING = 5
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (32, 32, 32)
FONT_SCALE = 0.6
FONT_THICKNESS = 1

# Screen capture settings
BAR_HEIGHT = 1
BAR_OFFSET = 5  # from bottom
KEY_COLOR_MAP = {
    "Q": (255, 0, 0),
    "W": (255, 127, 0),
    "E": (255, 255, 0),
    "R": (0, 255, 0),
    "T": (0, 0, 255),
    "Y": (75, 0, 130),
    "U": (138, 43, 226),
    "I": (255, 20, 147),
    "O": (255, 215, 0),
    "P": (200, 200, 200),
    "A": (0, 255, 255),
    "S": (255, 0, 255),
}

# Layout (3 rows x 4 cols)
CAM_KEYS = ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "A", "S"]
ROWS, COLS = 3, 4
BAR_SEGMENTS = len(CAM_KEYS)
cached_frames = {key: np.full((100, 100, 3), BLACK, dtype=np.uint8) for key in CAM_KEYS}

def capture_color_bar():
    screen = ImageGrab.grab()
    width, height = screen.size
    y = height - BAR_OFFSET
    return screen.crop((0, y, width, y + BAR_HEIGHT))

def capture_fullscreen():
    return ImageGrab.grab()

def render_multiview_window(win_name="OBS Multiview"):
    cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(win_name, 1280, 720)

    while True:
        try:
            color_bar = capture_color_bar()
            pixels = color_bar.load()
            bar_width = color_bar.size[0]
            segment_width = bar_width // BAR_SEGMENTS

            full_screenshot = None

            for i, key in enumerate(CAM_KEYS):
                segment_x = i * segment_width + segment_width // 2
                r, g, b = pixels[segment_x, 0]
                current = (r, g, b)
                expected = KEY_COLOR_MAP[key]

                if current == expected:
                    print(f"[MATCH] {key} - {current}")
                    if full_screenshot is None:
                        full_screenshot = capture_fullscreen()
                    img = full_screenshot.copy().resize((320, 240))
                    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                    cached_frames[key] = img
                else:
                    print(f"[SKIP ] {key} - got {current}, expected {expected}")

        except Exception as e:
            print("Screen capture failed:", e)
            break

        try:
            _, _, win_w, win_h = cv2.getWindowImageRect(win_name)
        except:
            win_w, win_h = 1280
            win_h = 720

        box_w = (win_w - (COLS - 1) * GRID_SPACING) // COLS
        box_h = (win_h - (ROWS - 1) * GRID_SPACING) // ROWS

        full_view = np.full((win_h, win_w, 3), GREY, dtype=np.uint8)

        for idx, key in enumerate(CAM_KEYS):
            row = idx // COLS
            col = idx % COLS
            x = col * (box_w + GRID_SPACING)
            y = row * (box_h + GRID_SPACING)

            frame = cached_frames[key]
            if frame.shape[:2] != (box_h, box_w):
                frame = cv2.resize(frame, (box_w, box_h))
                cached_frames[key] = frame

            frame = frame.copy()
            label = f"Camera {key}"
            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE, FONT_THICKNESS)[0]
            cv2.rectangle(frame, (0, 0), (text_size[0] + 10, text_size[1] + 10), GREY, -1)
            cv2.putText(frame, label, (5, text_size[1] + 5), cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE, WHITE, FONT_THICKNESS)

            full_view[y:y + box_h, x:x + box_w] = frame

        cv2.imshow(win_name, full_view)

        if (
            cv2.getWindowProperty(win_name, cv2.WND_PROP_VISIBLE) < 1
            or cv2.waitKey(30) & 0xFF == 27
        ):
            break
    cv2.destroyAllWindows()

render_multiview_window()
