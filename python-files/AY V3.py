import tkinter as tk
from threading import Thread, Event
import cv2
import mss
import numpy as np
import os
import sys

try:
    import win32api
    import win32con
except ImportError:
    print("Error: 'pywin32' library not found. Install it with: pip install pywin32")
    sys.exit(1)

try:
    from pynput.mouse import Listener as MouseListener, Button
    from pynput.keyboard import Listener as KeyboardListener, Key, KeyCode
except ImportError:
    print("Error: 'pynput' library not found. Install it with: pip install pynput")
    sys.exit(1)

try:
    import onnxruntime as ort
except ImportError:
    print("Error: 'onnxruntime' library not found. Install it with: pip install onnxruntime-directml")
    sys.exit(1)

# --- CONFIG ---
FOV_SIZE = 550
RUNNING, AIM_ACTIVE, E_KEY_MODE_ENABLED = Event(), Event(), False
MODEL, MODEL_INPUT_NAME, MODEL_OUTPUT_NAMES = None, None, None
MODEL_INPUT_SHAPE = (1, 3, 320, 320)
ONNX_MODEL_NAME = os.path.join(os.path.dirname(__file__), "yolov8n_320.onnx")
CONF_THRESHOLD, IOU_THRESHOLD = 0.25, 0.45
MONITOR_INFO = {}
PERSON_CLASS_ID = 0
FOV_WINDOW_NAME = "Detection Feed"
CROSSHAIR_WINDOW = None
CHROMA_KEY_COLOR = 'fuchsia'
SMOOTH_FACTOR = 5
TARGET_PART = "Head"  # Head, Chest, Full Body
AIM_KEY = "Right Mouse"

keyboard_listener, mouse_listener = None, None


def load_model():
    global MODEL, MODEL_INPUT_NAME, MODEL_OUTPUT_NAMES, MONITOR_INFO
    status_label.config(text="Status: Loading model...", fg="orange")
    if not os.path.exists(ONNX_MODEL_NAME):
        status_label.config(text=f"Status: ERROR! '{ONNX_MODEL_NAME}' not found.", fg="red")
        return
    try:
        providers = ["DmlExecutionProvider", "CPUExecutionProvider"]
        MODEL = ort.InferenceSession(ONNX_MODEL_NAME, providers=providers)
        MODEL_INPUT_NAME, MODEL_OUTPUT_NAMES = MODEL.get_inputs()[0].name, [o.name for o in MODEL.get_outputs()]

        with mss.mss() as sct:
            MONITOR_INFO = sct.monitors[1]

        create_crosshair_window()
        status_label.config(text=f"Status: Ready ({MODEL.get_providers()[0]})", fg="green")
        start_button.config(state=tk.NORMAL)
    except Exception as e:
        status_label.config(text="Status: Model load failed!", fg="red")
        print(f"Error: {e}")


def post_process(output, model_dims, fov_dims):
    output = output[0].T
    boxes_raw = output[:, :4]
    scores = np.max(output[:, 4:], axis=1)
    class_ids = np.argmax(output[:, 4:], axis=1)
    mask = (scores > CONF_THRESHOLD) & (class_ids == PERSON_CLASS_ID)
    if not np.any(mask):
        return [], []
    filtered_boxes_raw, filtered_scores = boxes_raw[mask], scores[mask]
    model_h, model_w = model_dims
    fov_h, fov_w = fov_dims
    x_scale, y_scale = fov_w / model_w, fov_h / model_h
    x_center, y_center, w, h = filtered_boxes_raw.T
    x1, y1 = (x_center - w / 2) * x_scale, (y_center - h / 2) * y_scale
    scaled_w, scaled_h = w * x_scale, h * y_scale
    nms_boxes = [[int(b[0]), int(b[1]), int(b[2]), int(b[3])] for b in zip(x1, y1, scaled_w, scaled_h)]
    indices = cv2.dnn.NMSBoxes(nms_boxes, filtered_scores.tolist(), CONF_THRESHOLD, IOU_THRESHOLD)
    if not len(indices):
        return [], []
    return np.array(nms_boxes)[indices.flatten()], filtered_scores[indices.flatten()]


def get_target_point(x, y, w, h):
    if TARGET_PART == "Head":
        return x + w // 2, y + int(h * 0.25)
    elif TARGET_PART == "Chest":
        return x + w // 2, y + int(h * 0.5)
    elif TARGET_PART == "Full Body":
        return x + w // 2, y + h // 2
    else:
        return x + w // 2, y + h // 2


def aim_tool_loop():
    global SMOOTH_FACTOR
    sct = mss.mss()
    screen_center_x = MONITOR_INFO['left'] + MONITOR_INFO['width'] // 2
    screen_center_y = MONITOR_INFO['top'] + MONITOR_INFO['height'] // 2
    model_h, model_w = MODEL_INPUT_SHAPE[2], MODEL_INPUT_SHAPE[3]

    cv2.namedWindow(FOV_WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(FOV_WINDOW_NAME, cv2.WND_PROP_TOPMOST, 1)

    while RUNNING.is_set():
        # Full screen for display
        screen_img = np.array(sct.grab({
            "left": MONITOR_INFO['left'],
            "top": MONITOR_INFO['top'],
            "width": MONITOR_INFO['width'],
            "height": MONITOR_INFO['height']
        }), dtype=np.uint8)[:, :, :3].copy()

        # FOV crop for detection
        fov_left = screen_center_x - (FOV_SIZE // 2)
        fov_top = screen_center_y - (FOV_SIZE // 2)
        fov_img = np.array(sct.grab({
            "left": fov_left,
            "top": fov_top,
            "width": FOV_SIZE,
            "height": FOV_SIZE
        }), dtype=np.uint8)[:, :, :3].copy()

        # Prepare for model
        resized_img = cv2.resize(fov_img, (model_w, model_h), interpolation=cv2.INTER_LINEAR)
        input_tensor = np.expand_dims(np.transpose(resized_img, (2, 0, 1)).astype(np.float32) / 255.0, axis=0)
        outputs = MODEL.run(MODEL_OUTPUT_NAMES, {MODEL_INPUT_NAME: input_tensor})
        boxes, _ = post_process(outputs[0], (model_h, model_w), (FOV_SIZE, FOV_SIZE))

        # Draw FOV circle
        cv2.circle(screen_img, (screen_center_x, screen_center_y), FOV_SIZE // 2, (255, 255, 0), 2)

        # Inside FOV detection
        target_center = None
        if len(boxes) > 0:
            min_dist_sq = float('inf')
            for x, y, w, h in boxes:
                abs_x = fov_left + x
                abs_y = fov_top + y
                px, py = get_target_point(abs_x, abs_y, w, h)
                dist_sq = (px - screen_center_x) ** 2 + (py - screen_center_y) ** 2
                if dist_sq <= (FOV_SIZE // 2) ** 2:
                    cv2.rectangle(screen_img, (abs_x, abs_y), (abs_x + w, abs_y + h), (255, 0, 0), 2)
                    if dist_sq < min_dist_sq:
                        min_dist_sq, target_center = dist_sq, (px, py)

        if target_center and AIM_ACTIVE.is_set():
            move_x = int((target_center[0] - screen_center_x) / SMOOTH_FACTOR)
            move_y = int((target_center[1] - screen_center_y) / SMOOTH_FACTOR)
            if abs(move_x) > 0 or abs(move_y) > 0:
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, move_x, move_y, 0, 0)

        cv2.imshow(FOV_WINDOW_NAME, screen_img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_tool()
            break

    cv2.destroyAllWindows()


def on_press(key):
    try:
        if str(key) == AIM_KEY:
            AIM_ACTIVE.set()
    except:
        pass


def on_release(key):
    try:
        if str(key) == AIM_KEY:
            AIM_ACTIVE.clear()
    except:
        pass


def on_click(x, y, button, pressed):
    if AIM_KEY == "Right Mouse" and button == Button.right:
        AIM_ACTIVE.set() if pressed else AIM_ACTIVE.clear()
    elif AIM_KEY == "Left Mouse" and button == Button.left:
        AIM_ACTIVE.set() if pressed else AIM_ACTIVE.clear()


def start_listeners():
    global keyboard_listener, mouse_listener
    if keyboard_listener is None:
        keyboard_listener = KeyboardListener(on_press=on_press, on_release=on_release)
        mouse_listener = MouseListener(on_click=on_click)
        keyboard_listener.start()
        mouse_listener.start()


def start_tool():
    if not RUNNING.is_set() and MODEL is not None:
        RUNNING.set()
        Thread(target=aim_tool_loop, daemon=True).start()
        status_label.config(text=f"Status: Running ({MODEL.get_providers()[0]})", fg="blue")


def stop_tool():
    if RUNNING.is_set():
        RUNNING.clear()
        AIM_ACTIVE.clear()
        if MODEL is not None:
            status_label.config(text=f"Status: Ready ({MODEL.get_providers()[0]})", fg="green")
        else:
            status_label.config(text=f"Status: ERROR! '{ONNX_MODEL_NAME}' not found.", fg="red")


def update_fov(val):
    global FOV_SIZE
    FOV_SIZE = int(val)


def update_smooth(val):
    global SMOOTH_FACTOR
    SMOOTH_FACTOR = int(val)


def update_target_part(choice):
    global TARGET_PART
    TARGET_PART = choice


def update_aim_key(choice):
    global AIM_KEY
    AIM_KEY = choice


def create_crosshair_window():
    global CROSSHAIR_WINDOW
    if CROSSHAIR_WINDOW is not None or not MONITOR_INFO:
        return
    CROSSHAIR_WINDOW = tk.Toplevel()
    CROSSHAIR_WINDOW.overrideredirect(True)
    CROSSHAIR_WINDOW.attributes('-topmost', True)
    CROSSHAIR_WINDOW.attributes('-transparentcolor', CHROMA_KEY_COLOR)
    CROSSHAIR_WINDOW.config(bg=CHROMA_KEY_COLOR)
    dot_size = 4
    dot = tk.Label(CROSSHAIR_WINDOW, bg='lime', width=1, height=1)
    dot.pack()
    win_size = dot_size + 2
    pos_x = (MONITOR_INFO['left'] + MONITOR_INFO['width'] // 2) - (win_size // 2)
    pos_y = (MONITOR_INFO['top'] + MONITOR_INFO['height'] // 2) - (win_size // 2)
    CROSSHAIR_WINDOW.geometry(f'{win_size}x{win_size}+{pos_x}+{pos_y}')


def create_gui():
    global start_button, status_label
    root = tk.Tk()
    root.title("MersekUD")
    root.geometry("350x400")
    root.configure(bg="#2a003f")
    root.attributes('-topmost', True)

    style_fg = "#b19cd9"
    style_btn = "#4b0082"
    style_btn_txt = "#ffffff"

    tk.Label(root, text="Field of View Size (px):", bg="#2a003f", fg=style_fg).pack(pady=(5, 0))
    tk.Scale(root, from_=100, to=1000, orient=tk.HORIZONTAL, length=300, resolution=50,
             command=update_fov, variable=tk.IntVar(value=FOV_SIZE), bg="#2a003f", fg=style_fg).pack()

    tk.Label(root, text="Aim Smoothness (Lower = Faster):", bg="#2a003f", fg=style_fg).pack(pady=(5, 0))
    tk.Scale(root, from_=1, to=20, orient=tk.HORIZONTAL, length=300,
             command=update_smooth, variable=tk.IntVar(value=SMOOTH_FACTOR), bg="#2a003f", fg=style_fg).pack()

    tk.Label(root, text="Target Body Part:", bg="#2a003f", fg=style_fg).pack(pady=(5, 0))
    body_options = ["Head", "Chest", "Full Body"]
    body_menu = tk.OptionMenu(root, tk.StringVar(value=TARGET_PART), *body_options, command=update_target_part)
    body_menu.config(bg=style_btn, fg=style_btn_txt)
    body_menu.pack(pady=5)

    tk.Label(root, text="Aim Activation Key:", bg="#2a003f", fg=style_fg).pack(pady=(5, 0))
    key_options = ["Right Mouse", "Left Mouse", "'e'", "'shift'", "'ctrl'"]
    key_menu = tk.OptionMenu(root, tk.StringVar(value=AIM_KEY), *key_options, command=update_aim_key)
    key_menu.config(bg=style_btn, fg=style_btn_txt)
    key_menu.pack(pady=5)

    start_button = tk.Button(root, text="Start AIM Tool", command=start_tool,
                             state=tk.DISABLED, bg=style_btn, fg=style_btn_txt)
    start_button.pack(pady=5)

    tk.Button(root, text="Stop AIM Tool", command=stop_tool, bg=style_btn, fg=style_btn_txt).pack(pady=5)
    status_label = tk.Label(root, text="Status: Initializing...", fg=style_fg, bg="#2a003f")
    status_label.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

    start_listeners()
    Thread(target=load_model, daemon=True).start()

    def on_closing():
        stop_tool()
        if keyboard_listener and keyboard_listener.is_alive():
            keyboard_listener.stop()
        if mouse_listener and mouse_listener.is_alive():
            mouse_listener.stop()
        if CROSSHAIR_WINDOW:
            CROSSHAIR_WINDOW.destroy()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == '__main__':
    if not os.path.exists(ONNX_MODEL_NAME):
        print(f"--- WARNING ---\nModel file '{ONNX_MODEL_NAME}' not found.")
    create_gui()
