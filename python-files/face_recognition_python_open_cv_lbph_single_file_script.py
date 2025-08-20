#!/usr/bin/env python3
"""
Face Recognition on PC using OpenCV's LBPH recognizer (CPU‑friendly, works offline)

VERSION: 2025-08-20
- Fix A: Robust BASE_DIR when __file__ is undefined (interactive/sandboxed runs).
- Fix B: Handle missing CLI subcommand gracefully (avoid SystemExit: 2).
- Fix C: Avoid raising SystemExit(0) when main() returns 0 (swallow normal zero exit).
- Add: `selftest` includes CLI checks + synthetic LBPH tests.

Usage (run from terminal):
  1) Collect face images via webcam for each person (creates dataset/PersonName):
       python face_rec.py collect --person "Abhijeet"

  2) Train a model from the dataset and save to models/:
       python face_rec.py train

  3) Real‑time recognition from webcam:
       python face_rec.py recognize

  4) Recognize faces in a single image and save annotated copy:
       python face_rec.py recognize --image path/to/photo.jpg --out out.jpg

  5) Run built‑in tests (no webcam needed):
       python face_rec.py selftest

Requirements (install once):
  pip install opencv-contrib-python numpy

Notes:
- Dataset layout expected by trainer:
    dataset/
      PersonA/ img_001.jpg, img_002.jpg, ...
      PersonB/ img_001.jpg, ...
- You can run `collect` multiple times with the same --person to add more samples.
- The LBPH algorithm is robust on CPU and small datasets; for large‑scale/production, consider deep models (FaceNet, ArcFace) + embeddings + classifier.
- Base directory selection:
    • If running as a script, files are saved relative to the script location.
    • If running interactively (no __file__), files are saved to the current working directory.
    • You can override with env var FACE_REC_BASE_DIR.
"""

import os
import sys
import cv2
import json
import time
import glob
import argparse
import numpy as np
from datetime import datetime

# ------------------ Paths & Constants ------------------
# Robust BASE_DIR selection to avoid NameError when __file__ is undefined (e.g., notebooks/sandboxes).
BASE_DIR = (
    os.environ.get("FACE_REC_BASE_DIR")
    or (os.path.abspath(os.path.dirname(__file__)) if "__file__" in globals() else os.getcwd())
)
DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
MODEL_DIR = os.path.join(BASE_DIR, 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'lbph_model.xml')
LABELS_PATH = os.path.join(MODEL_DIR, 'labels.json')

os.makedirs(DATASET_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# Haar cascade for face detection (ships with OpenCV)
HAAR_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(HAAR_PATH)
if face_cascade.empty():
    raise RuntimeError('Failed to load Haar cascade at: ' + HAAR_PATH)

# Ensure we have opencv-contrib (LBPH lives in cv2.face)

def _require_contrib():
    if not hasattr(cv2, 'face'):
        raise RuntimeError(
            "OpenCV contrib modules not found. Install with: pip install opencv-contrib-python"
        )

# ------------------ Utilities ------------------

def _timestamp():
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def detect_faces_gray(image_bgr, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)):
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=scaleFactor, minNeighbors=minNeighbors, minSize=minSize
    )
    return gray, faces


def crop_and_normalize(gray_img, x, y, w, h, out_size=(200, 200)):
    roi = gray_img[y:y+h, x:x+w]
    roi_resized = cv2.resize(roi, out_size, interpolation=cv2.INTER_AREA)
    return roi_resized


def list_people(dataset_dir=DATASET_DIR):
    people = [d for d in os.listdir(dataset_dir)
              if os.path.isdir(os.path.join(dataset_dir, d)) and not d.startswith('.')]
    people.sort()
    return people


# ------------------ Collect Mode ------------------

def collect_samples(person: str, num_samples: int = 60, cam_index: int = 0, delay: float = 0.1):
    person_dir = os.path.join(DATASET_DIR, person)
    os.makedirs(person_dir, exist_ok=True)

    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        raise RuntimeError(f'Cannot open webcam index {cam_index}')

    print(f"[Collect] Capturing samples for '{person}'. Press 'q' to quit early.")
    saved = 0
    while saved < num_samples:
        ret, frame = cap.read()
        if not ret:
            print('Frame grab failed; retrying...')
            continue
        gray, faces = detect_faces_gray(frame)

        # Draw rectangles to guide the user
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv2.putText(frame, f"Person: {person} | Saved: {saved}/{num_samples}", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imshow('Collect Faces', frame)

        # Save the first face found in the frame (if any)
        if len(faces) > 0:
            x, y, w, h = faces[0]
            face_img = crop_and_normalize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), x, y, w, h)
            fname = os.path.join(person_dir, f'{_timestamp()}_{saved:03d}.jpg')
            cv2.imwrite(fname, face_img)
            saved += 1
            time.sleep(delay)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"[Collect] Saved {saved} images to {person_dir}")


# ------------------ Train Mode ------------------

def load_images_and_labels(dataset_dir=DATASET_DIR):
    people = list_people(dataset_dir)
    if not people:
        raise RuntimeError('No people found in dataset/. Add data with the collect command.')

    X = []  # images (grayscale)
    y = []  # numeric labels
    label_map = {name: idx for idx, name in enumerate(people)}

    for person in people:
        pdir = os.path.join(dataset_dir, person)
        for img_path in glob.glob(os.path.join(pdir, '*.jpg')) + glob.glob(os.path.join(pdir, '*.png')):
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            # Ensure training size consistency
            img = cv2.resize(img, (200, 200), interpolation=cv2.INTER_AREA)
            X.append(img)
            y.append(label_map[person])

    if len(X) < 10:
        print('[Warn] Very few training images; recognition quality may be poor.')

    return X, y, label_map


def train_model():
    _require_contrib()
    X, y, label_map = load_images_and_labels()

    # Create LBPH recognizer
    recognizer = cv2.face.LBPHFaceRecognizer_create(radius=2, neighbors=16, grid_x=8, grid_y=8)
    recognizer.train(X, np.array(y))

    recognizer.write(MODEL_PATH)
    with open(LABELS_PATH, 'w', encoding='utf-8') as f:
        json.dump(label_map, f, ensure_ascii=False, indent=2)

    print(f"[Train] Saved model -> {MODEL_PATH}")
    print(f"[Train] Saved labels -> {LABELS_PATH}")


# ------------------ Recognize Mode ------------------

def load_model():
    _require_contrib()
    if not os.path.exists(MODEL_PATH) or not os.path.exists(LABELS_PATH):
        raise RuntimeError('Model not found. Train first with: python face_rec.py train')

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(MODEL_PATH)
    with open(LABELS_PATH, 'r', encoding='utf-8') as f:
        label_map = json.load(f)
    # reverse map: id -> name
    id_to_name = {int(v): k for k, v in label_map.items()}
    return recognizer, id_to_name


def predict_face(gray_img, face_rect, recognizer, id_to_name, threshold=70.0):
    x, y, w, h = face_rect
    roi = crop_and_normalize(gray_img, x, y, w, h)
    label_id, confidence = recognizer.predict(roi)  # LBPH: lower confidence is better
    name = id_to_name.get(label_id, 'Unknown')
    is_known = confidence < (100 - threshold)  # Convert threshold to LBPH scale
    # More intuitive: we map LBPH confidence to a pseudo "match%"
    match_pct = max(0, min(100, int(100 - confidence)))
    return name if is_known else 'Unknown', confidence, match_pct


def recognize_realtime(cam_index=0, threshold=70.0):
    recognizer, id_to_name = load_model()

    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        raise RuntimeError(f'Cannot open webcam index {cam_index}')

    print("[Recognize] Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        gray, faces = detect_faces_gray(frame)
        for (x, y, w, h) in faces:
            name, conf, match_pct = predict_face(gray, (x, y, w, h), recognizer, id_to_name, threshold)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, f"{name} ({match_pct}%)", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow('Face Recognition', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def recognize_image(image_path: str, out_path: str = None, threshold: float = 70.0):
    if not os.path.exists(image_path):
        raise FileNotFoundError(image_path)

    recognizer, id_to_name = load_model()
    img = cv2.imread(image_path)
    if img is None:
        raise RuntimeError('Failed to read image: ' + image_path)

    gray, faces = detect_faces_gray(img)

    for (x, y, w, h) in faces:
        name, conf, match_pct = predict_face(gray, (x, y, w, h), recognizer, id_to_name, threshold)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        label = f"{name} ({match_pct}%)"
        cv2.putText(img, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    if out_path:
        cv2.imwrite(out_path, img)
        print(f"[Recognize] Saved annotated image -> {out_path}")
    else:
        cv2.imshow('Face Recognition (Image)', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


# ------------------ CLI helpers & Self Tests ------------------
# Self tests are basic runtime checks and a tiny synthetic LBPH training to ensure deps & logic work.


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Face Recognition (OpenCV LBPH)',
        formatter_class=argparse.RawTextHelpFormatter,
    )
    sub = parser.add_subparsers(dest='cmd')  # not required; we'll handle missing cmd

    p_collect = sub.add_parser('collect', help='Collect face samples via webcam')
    p_collect.add_argument('--person', required=True, help='Person name (folder will be created)')
    p_collect.add_argument('--num', type=int, default=60, help='Number of samples to collect (default 60)')
    p_collect.add_argument('--cam', type=int, default=0, help='Webcam index (default 0)')
    p_collect.add_argument('--delay', type=float, default=0.1, help='Delay between saves in seconds (default 0.1)')

    sub.add_parser('train', help='Train LBPH model from dataset')

    p_rec = sub.add_parser('recognize', help='Recognize faces (webcam or single image)')
    p_rec.add_argument('--image', help='Path to image for one‑off recognition')
    p_rec.add_argument('--out', help='If --image is set, save annotated result to this path')
    p_rec.add_argument('--cam', type=int, default=0, help='Webcam index (default 0)')
    p_rec.add_argument('--threshold', type=float, default=70.0,
                       help='Match threshold (higher = stricter). 70 is a good start.')

    sub.add_parser('selftest', help='Run built‑in tests (no webcam required)')

    return parser


def print_friendly_usage(parser: argparse.ArgumentParser):
    print(parser.format_help())
    print("Examples:\n"
          "  python face_rec.py collect --person \"Abhijeet\"\n"
          "  python face_rec.py train\n"
          "  python face_rec.py recognize\n"
          "  python face_rec.py recognize --image path/to/photo.jpg --out out.jpg\n"
          "  python face_rec.py selftest\n")


def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    parser = build_parser()

    # If no arguments supplied, show friendly help & examples instead of argparse error (SystemExit: 2)
    if not argv:
        print_friendly_usage(parser)
        return 0

    args = parser.parse_args(argv)

    if args.cmd == 'collect':
        collect_samples(args.person, args.num, args.cam, args.delay)
    elif args.cmd == 'train':
        train_model()
    elif args.cmd == 'recognize':
        if args.image:
            recognize_image(args.image, args.out, args.threshold)
        else:
            recognize_realtime(args.cam, args.threshold)
    elif args.cmd == 'selftest':
        _selftest()
    else:
        # Unrecognized path; show help and return error code 2 for compatibility
        print_friendly_usage(parser)
        return 2

    return 0


def _selftest():
    print("[SelfTest] BASE_DIR:", BASE_DIR)
    print("[SelfTest] DATASET_DIR exists:", os.path.isdir(DATASET_DIR))
    print("[SelfTest] MODEL_DIR exists:", os.path.isdir(MODEL_DIR))

    # 0) CLI parser sanity checks (ensure no SystemExit on empty args & thresholds parse)
    parser = build_parser()
    # Should not raise SystemExit; should return Namespace with cmd=None
    ns = parser.parse_args([])
    assert getattr(ns, 'cmd', None) is None, "Empty args should not set a command"
    # Threshold parsing
    ns2 = parser.parse_args(['recognize', '--threshold', '65'])
    assert ns2.threshold == 65.0 and ns2.cmd == 'recognize', "Threshold parsing failed"
    print("[SelfTest] CLI parser checks passed.")

    # 0.5) Ensure main([]) returns 0 (this avoids SystemExit(0) being raised by the script runner)
    rv = main([])
    assert rv == 0, "main([]) should return 0 (friendly help shown)"
    print("[SelfTest] main([]) returned 0 as expected.")

    # 1) Cascade should load and detect no faces on a blank image
    blank = np.zeros((400, 400, 3), dtype=np.uint8)
    _, faces = detect_faces_gray(blank)
    assert len(faces) == 0, "Haar should detect 0 faces on blank image"
    print("[SelfTest] Haar cascade basic check passed.")

    # 2) Contrib presence & tiny synthetic LBPH training
    _require_contrib()
    # Create two synthetic classes (circle vs rectangle) as 200x200 gray images
    def synth_sample(cls, n=20):
        samples = []
        for i in range(n):
            img = np.zeros((200, 200), dtype=np.uint8)
            if cls == 0:
                cv2.circle(img, (100, 100), 50 + (i % 5), 255, -1)
            else:
                cv2.rectangle(img, (60, 60), (140 + (i % 5), 140), 255, -1)
            # add slight noise
            noise = np.random.randint(0, 15, img.shape, dtype=np.uint8)
            img = cv2.add(img, noise)
            samples.append(img)
        return samples

    X = synth_sample(0, 25) + synth_sample(1, 25)
    y = [0]*25 + [1]*25

    recognizer = cv2.face.LBPHFaceRecognizer_create(radius=2, neighbors=8, grid_x=8, grid_y=8)
    recognizer.train(X, np.array(y))

    # Evaluate on a couple of fresh samples
    testA = synth_sample(0, 5)
    testB = synth_sample(1, 5)
    correct = 0
    for img in testA:
        pred, conf = recognizer.predict(img)
        correct += (pred == 0)
    for img in testB:
        pred, conf = recognizer.predict(img)
        correct += (pred == 1)
    acc = correct / 10.0
    print(f"[SelfTest] Synthetic LBPH accuracy: {acc*100:.1f}% (expect > 70%)")
    assert acc >= 0.7, "Synthetic LBPH accuracy too low; check OpenCV build."

    # Ensure we do not overwrite real model files during selftest
    tmp_model = os.path.join(MODEL_DIR, 'lbph_model_selftest.xml')
    recognizer.write(tmp_model)
    print("[SelfTest] Wrote temporary model:", tmp_model)

    print("[SelfTest] ALL TESTS PASSED ✅")


if __name__ == '__main__':
    # Run main() and only call sys.exit on non-zero return codes to avoid SystemExit(0) showing up in some runners.
    try:
        rc = main()
    except KeyboardInterrupt:
        print('\n[Interrupted] Exiting.')
        rc = 1
    except SystemExit as e:
        # If an internal SystemExit was raised, re-raise for non-zero codes but swallow zero-exit.
        code = e.code if hasattr(e, 'code') else 1
        if code != 0:
            raise
        rc = 0

    if rc != 0:
        sys.exit(rc)
