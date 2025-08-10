"""
obs_face_censor.py
Face censoring virtual camera for OBS with persistence.


Modes:
  0 - solid color box
  1 - gaussian blur
  2 - mosaic (pixelate)

Controls:
  - 'q' or ESC : quit
  - 'm' : cycle mode (color -> blur -> mosaic)
  - 'p' : pause/unpause processing
"""

import cv2
import mediapipe as mp
import numpy as np
import pyvirtualcam
from pyvirtualcam import PixelFormat
import time

# --- Settings ---
CAM_INDEX = 0
FPS = 20
MIN_DETECTION_CONFIDENCE = 0.6
PERSISTENCE_TIME = 0.5  # seconds to keep last face after losing detection
# ----------------

mp_face = mp.solutions.face_detection

def nothing(x):
    pass

def apply_solid(frame, bbox, color_bgr):
    x1, y1, x2, y2 = bbox
    cv2.rectangle(frame, (x1, y1), (x2, y2), color_bgr, thickness=-1)

def apply_blur(frame, bbox, ksize):
    x1, y1, x2, y2 = bbox
    roi = frame[y1:y2, x1:x2]
    if roi.size == 0:
        return
    k = max(1, (ksize // 2) * 2 + 1)
    blurred = cv2.GaussianBlur(roi, (k, k), 0)
    frame[y1:y2, x1:x2] = blurred

def apply_mosaic(frame, bbox, block_size):
    x1, y1, x2, y2 = bbox
    roi = frame[y1:y2, x1:x2]
    if roi.size == 0:
        return
    h, w = roi.shape[:2]
    bs = max(1, block_size)
    small = cv2.resize(roi, (max(1, w//bs), max(1, h//bs)), interpolation=cv2.INTER_LINEAR)
    pixelated = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
    frame[y1:y2, x1:x2] = pixelated

def bbox_from_detection(detection, w, h, pad=0.15):
    r = detection.location_data.relative_bounding_box
    xmin = int(r.xmin * w)
    ymin = int(r.ymin * h)
    bw = int(r.width * w)
    bh = int(r.height * h)
    px = int(bw * pad)
    py = int(bh * pad)
    x1 = max(0, xmin - px)
    y1 = max(0, ymin - py)
    x2 = min(w, xmin + bw + px)
    y2 = min(h, ymin + bh + py)
    return x1, y1, x2, y2

def main():
    cap = cv2.VideoCapture(CAM_INDEX)
    if not cap.isOpened():
        print("Cannot open webcam index", CAM_INDEX)
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cam_fps = FPS

    cv2.namedWindow("Controls", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Controls", 420, 180)
    cv2.createTrackbar("Mode (0=color,1=blur,2=mos)", "Controls", 0, 2, nothing)
    cv2.createTrackbar("Color-B", "Controls", 0, 255, nothing)
    cv2.createTrackbar("Color-G", "Controls", 0, 255, nothing)
    cv2.createTrackbar("Color-R", "Controls", 0, 255, nothing)
    cv2.createTrackbar("Blur Size", "Controls", 21, 101, nothing)
    cv2.createTrackbar("Mosaic Block", "Controls", 20, 100, nothing)
    cv2.createTrackbar("Detection Conf %", "Controls", int(MIN_DETECTION_CONFIDENCE*100), 100, nothing)

    paused = False
    last_bbox = None
    last_detect_time = 0

    with pyvirtualcam.Camera(width=width, height=height, fps=cam_fps, fmt=PixelFormat.BGR) as cam:
        print(f'Virtual camera started: {cam.device} ({width}x{height} @ {cam.fps}fps)')
        last_frame = None
        with mp_face.FaceDetection(model_selection=0, min_detection_confidence=MIN_DETECTION_CONFIDENCE) as detector:
            while True:
                if not paused:
                    ret, frame = cap.read()
                    if not ret:
                        print("Failed to read frame from webcam.")
                        break

                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    det_conf = cv2.getTrackbarPos("Detection Conf %", "Controls") / 100.0
                    results = detector.process(frame_rgb)

                    bbox = None
                    if results.detections:
                        best = max(results.detections, key=lambda d: d.location_data.relative_bounding_box.width * d.location_data.relative_bounding_box.height)
                        score = best.score[0] if best.score else 0.0
                        if score >= det_conf:
                            bbox = bbox_from_detection(best, width, height, pad=0.20)
                            last_bbox = bbox
                            last_detect_time = time.time()

                    # Persistence: reuse last bbox if recent
                    if bbox is None and last_bbox and (time.time() - last_detect_time) < PERSISTENCE_TIME:
                        bbox = last_bbox

                    if bbox:
                        mode = cv2.getTrackbarPos("Mode (0=color,1=blur,2=mos)", "Controls")
                        if mode == 0:
                            b = cv2.getTrackbarPos("Color-B", "Controls")
                            g = cv2.getTrackbarPos("Color-G", "Controls")
                            r = cv2.getTrackbarPos("Color-R", "Controls")
                            apply_solid(frame, bbox, (b, g, r))
                        elif mode == 1:
                            ksize = cv2.getTrackbarPos("Blur Size", "Controls")
                            apply_blur(frame, bbox, ksize)
                        else:
                            bs = cv2.getTrackbarPos("Mosaic Block", "Controls")
                            apply_mosaic(frame, bbox, bs)

                    last_frame = frame.copy()
                    cam.send(frame)
                    cam.sleep_until_next_frame()
                else:
                    if last_frame is not None:
                        cam.send(last_frame)
                        cam.sleep_until_next_frame()
                    time.sleep(0.01)

                preview = cv2.resize(last_frame if last_frame is not None else frame, (int(width*0.6), int(height*0.6)))
                cv2.imshow('Preview', preview)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:
                    break
                elif key == ord('m'):
                    cur = cv2.getTrackbarPos("Mode (0=color,1=blur,2=mos)", "Controls")
                    cv2.setTrackbarPos("Mode (0=color,1=blur,2=mos)", "Controls", (cur + 1) % 3)
                elif key == ord('p'):
                    paused = not paused

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        # Replace this with your main function or code block
        main()  # if you have a main function
    except Exception as e:
        import traceback
        print("Error:", e)
        traceback.print_exc()
    input("Press Enter to exit...")

