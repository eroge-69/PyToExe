#!/usr/bin/env python3
# coding: utf-8

import os
import threading
import time
from datetime import datetime
import cv2
import numpy as np
import pandas as pd
from collections import defaultdict

# =========================
#  НАСТРОЙКИ / ФАЙЛЫ
# =========================
DEFAULT_MODEL_PATH = "yolo11s.pt"          # можно yolo11s-seg.pt / yolo11n-seg.pt
APP_TITLE = "Счётчик посетителей — YOLO11"
WINDOW_VIDEO = "Просмотр и подсчёт"
# Use the same OpenCV window for both video display and zone setup so that
# users interact with a single window rather than multiple windows.
WINDOW_SETUP = WINDOW_VIDEO
SAVE_EVENTS_XLSX = "traffic_events.xlsx"
SAVE_EVENTS_CSV  = "traffic_events.csv"
SAVE_SUMMARY_XLSX = "traffic_summary.xlsx"
SAVE_SUMMARY_CSV  = "traffic_summary.csv"
SAVE_HEATMAP_PNG  = "traffic_heatmap.png"

# Детекция
YOLO_CONF = 0.45                 # порог уверенности
MIN_BOX_AREA = 22 * 22           # отсечь слишком маленькие боксы
MASK_THRESHOLD = 0.5             # порог бинаризации масок для seg-моделей

# Трекинг
TRACK_DISTANCE_THRESHOLD = 0.68  # порог метрики

# Работа приложения
AUTOSAVE_SEC = 120                # автосохранение
DRAW_MASK_ALPHA = 0.35
DRAW_HEAT_ALPHA = 0.40
SHOW_FPS_EVERY = 10
TARGET_SIZE = (1280, 720)         # масштаб для детекции/разметки

# =========================
#  УСКОРЕНИЕ / ОПЦИИ
# =========================
# 1) Пропуск пустых кадров (детектор движения на фоне)
MOTION_SKIP_ENABLED   = True
MOTION_HISTORY        = 300
MOTION_THRESH_LOW     = 0.001   # доля пикселей в движении -> "почти пусто"
MOTION_THRESH_HIGH    = 0.005   # доля пикселей в движении -> "точно движение"
MOTION_COOLDOWN       = 12       # продолжать детекцию ещё N обработанных кадров после события
ADAPTIVE_MAX_STRIDE   = 3        # максимум "шаг" обработки (каждый N-й кадр)

# 2) Пропуск кадров-дубликатов (если очень маленькая разница с предыдущим)
DIFF_SKIP_ENABLED     = True
DIFF_DOWNSCALE        = (240, 135)  # размер для дешёвой оценки
DIFF_THRESH_MEANABS   = 0.1         # ср. по |Δ| (0..255)

# 3) Детектить только внутри объединённого ROI зон (если зоны заданы)
DETECT_IN_ROI_ONLY    = True
ROI_PAD_PX            = 24         # расширение зоны для детекции

# 4) Параметры выполнения модели
USE_HALF_IF_CUDA      = True       # FP16 на CUDA
FORCE_DEVICE          = None       # Например: "cuda:0" / "cpu" / None -> авто

# =========================
#  Зависимости: ultralytics, norfair
# =========================
try:
    from ultralytics import YOLO
except Exception as e:
    raise RuntimeError("Не найден пакет ultralytics. Установите: pip install ultralytics") from e

try:
    from norfair import Detection, Tracker
except Exception as e:
    raise RuntimeError("Не найден пакет norfair. Установите: pip install norfair") from e

# Pillow для рендера кириллицы (если доступна)
try:
    from PIL import Image, ImageDraw, ImageFont
    # Также импортируем ImageTk для отображения кадров в Tkinter
    from PIL import ImageTk
    PIL_AVAILABLE = True
    # ищем доступный шрифт с кириллицей
    _font_path = None
    for candidate in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "C:\\Windows\\Fonts\\Arial.ttf",
        "C:\\Windows\\Fonts\\DejaVuSans.ttf",
    ]:
        if os.path.isfile(candidate):
            _font_path = candidate
            break
    if _font_path:
        DEFAULT_FONT = ImageFont.truetype(_font_path, 18)
    else:
        DEFAULT_FONT = ImageFont.load_default()
except Exception:
    PIL_AVAILABLE = False
    DEFAULT_FONT = None

# простой translit (запасной вариант если кириллица недоступна)
_TRANSLIT = str.maketrans({
    "А":"A","Б":"B","В":"V","Г":"G","Д":"D","Е":"E","Ё":"E","Ж":"Zh","З":"Z","И":"I","Й":"Y",
    "К":"K","Л":"L","М":"M","Н":"N","О":"O","П":"P","Р":"R","С":"S","Т":"T","У":"U","Ф":"F",
    "Х":"Kh","Ц":"Ts","Ч":"Ch","Ш":"Sh","Щ":"Sch","Ъ":"","Ы":"Y","Ь":"","Э":"E","Ю":"Yu","Я":"Ya",
    "а":"a","б":"b","в":"v","г":"g","д":"d","е":"e","ё":"e","ж":"zh","з":"z","и":"i","й":"y",
    "к":"k","л":"l","м":"m","н":"n","о":"o","п":"p","р":"r","с":"s","т":"t","у":"u","ф":"f",
    "х":"kh","ц":"ts","ч":"ch","ш":"sh","щ":"sch","ъ":"","ы":"y","ь":"","э":"e","ю":"yu","я":"ya",
})

def translit(text: str) -> str:
    try:
        return text.translate(_TRANSLIT)
    except Exception:
        return text

def draw_text(img_bgr, text, org, color=(255,255,255), font_size=18):
    """
    Рисуем текст с поддержкой кириллицы. Если Pillow доступен и найден шрифт — используем его.
    Иначе падаем назад на cv2.putText с транслитерацией.
    img_bgr — numpy array, BGR
    """
    if PIL_AVAILABLE and DEFAULT_FONT is not None:
        try:
            # конвертируем в RGB
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            pil = Image.fromarray(img_rgb)
            draw = ImageDraw.Draw(pil)
            # если хотим масштабировать, можно создать шрифт с другим size, но DEFAULT_FONT may be fine
            draw.text(org, text, font=DEFAULT_FONT, fill=tuple(int(c) for c in color))
            img_out = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
            img_bgr[:,:,:] = img_out  # in-place
            return
        except Exception:
            pass
    # fallback: transliteration and cv2.putText
    t = translit(text)
    cv2.putText(img_bgr, t, org, cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

# =========================
#  ВСПОМОГАТЕЛЬНОЕ — ГЕОМЕТРИЯ / форма зон
# =========================
def center_of_shape(shape):
    if shape is None:
        return None
    typ = shape.get("type")
    if typ == "rect":
        (x1,y1),(x2,y2) = shape["coords"]
        return ((x1+x2)//2, (y1+y2)//2)
    if typ == "poly":
        pts = np.array(shape["coords"], dtype=np.float32)
        if len(pts)==0:
            return None
        M = cv2.moments(pts)
        if M["m00"] != 0:
            cx = int(M["m10"]/M["m00"]); cy = int(M["m01"]/M["m00"])
            return (cx, cy)
        else:
            return tuple(map(int, pts.mean(axis=0)))
    if typ == "circle":
        cx, cy, r = shape["coords"]
        return (int(cx), int(cy))
    if typ == "line":
        (a,b) = shape["coords"]
        return ((a[0]+b[0])//2, (a[1]+b[1])//2)
    return None

def point_in_shape(x, y, shape):
    if shape is None:
        return False
    typ = shape.get("type")
    if typ == "rect":
        (x1,y1),(x2,y2) = shape["coords"]
        return x1 <= x <= x2 and y1 <= y <= y2
    if typ == "poly":
        pts = np.array(shape["coords"], dtype=np.int32)
        if pts.shape[0] < 3:
            return False
        res = cv2.pointPolygonTest(pts, (x,y), False)
        return res >= 0
    if typ == "circle":
        cx, cy, r = shape["coords"]
        return (x - cx)**2 + (y - cy)**2 <= r*r
    if typ == "line":
        # точка на линии считается False (линия — не зона)
        return False
    return False

def rect_from_two_points(pt1, pt2):
    try:
        (x1, y1) = pt1
        (x2, y2) = pt2
        x_min = int(min(x1, x2))
        x_max = int(max(x1, x2))
        y_min = int(min(y1, y2))
        y_max = int(max(y1, y2))
        return (x_min, y_min), (x_max, y_max)
    except Exception:
        return pt1, pt2

def point_side_of_line(pt, a, b):
    try:
        x, y = float(pt[0]), float(pt[1])
        x1, y1 = float(a[0]), float(a[1])
        x2, y2 = float(b[0]), float(b[1])
        return (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1)
    except Exception:
        return 0.0

def iou_xyxy(boxA, boxB):
    try:
        xA1, yA1, xA2, yA2 = [float(v) for v in boxA]
        xB1, yB1, xB2, yB2 = [float(v) for v in boxB]
        x_left   = max(xA1, xB1)
        y_top    = max(yA1, yB1)
        x_right  = min(xA2, xB2)
        y_bottom = min(yA2, yB2)
        if x_right <= x_left or y_bottom <= y_top:
            return 0.0
        inter_area = (x_right - x_left) * (y_bottom - y_top)
        areaA = max(0.0, (xA2 - xA1)) * max(0.0, (yA2 - yA1))
        areaB = max(0.0, (xB2 - xB1)) * max(0.0, (yB2 - yB1))
        if areaA <= 0 or areaB <= 0:
            return 0.0
        return float(inter_area) / float(areaA + areaB - inter_area)
    except Exception:
        return 0.0

# =========================
#  ДЕТЕКТОР (Ultralytics YOLO v11) + авто-устройство/FP16
# =========================
class Detector:
    def __init__(self, model_path, conf=YOLO_CONF):
        if not os.path.isfile(model_path):
            raise FileNotFoundError(f"Не найден файл модели: {model_path}")
        self.model = YOLO(model_path)
        self.conf = conf

        # попытаемся выбрать устройство и включить fp16
        self.device = FORCE_DEVICE or self._auto_device()
        self.half = False
        if USE_HALF_IF_CUDA and isinstance(self.device, str) and self.device.startswith("cuda"):
            self.half = True

        # По возможности слить слои для ускорения
        try:
            if hasattr(self.model, "fuse"):
                self.model.fuse()
            elif hasattr(self.model, "model") and hasattr(self.model.model, "fuse"):
                self.model.model.fuse()
        except Exception:
            pass

    @staticmethod
    def _auto_device():
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda:0"
            # MPS (Apple) — половинки обычно не поддерживает
            if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
                return "mps"
            return "cpu"
        except Exception:
            return "cpu"

    def detect(self, frame_bgr):
        """
        Возвращает:
          boxes: [(x1,y1,x2,y2,conf), ...]  -- в координатах frame_bgr
          masks: [np.uint8 HxW {0,1}] или []
        Только класс person (0).
        """
        # В некоторых версиях ultralytics параметры half/device поддерживаются напрямую
        kwargs = dict(verbose=False, conf=self.conf, classes=[0], max_det=80)
        # безопасно добавить device/half если доступны
        kwargs["device"] = self.device
        if self.half:
            kwargs["half"] = True

        try:
            res = self.model(frame_bgr, **kwargs)[0]
        except TypeError:
            # fallback без half
            kwargs.pop("half", None)
            res = self.model(frame_bgr, **kwargs)[0]

        boxes, masks = [], []
        if getattr(res, "boxes", None) is None or len(res.boxes) == 0:
            return boxes, masks

        xyxy = res.boxes.xyxy.cpu().numpy()
        confs = res.boxes.conf.cpu().numpy()

        has_masks = getattr(res, "masks", None) is not None and res.masks is not None
        if has_masks:
            mdata = res.masks.data.cpu().numpy()  # (N, h', w')
            h, w = frame_bgr.shape[:2]

        for i, ((x1, y1, x2, y2), c) in enumerate(zip(xyxy, confs)):
            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
            if (x2 - x1) * (y2 - y1) < MIN_BOX_AREA:
                continue
            boxes.append((x1, y1, x2, y2, float(c)))

            if has_masks:
                m = (mdata[i] > MASK_THRESHOLD).astype(np.uint8)
                mh, mw = m.shape
                if (mh, mw) != (h, w):
                    m = cv2.resize(m, (w, h), interpolation=cv2.INTER_NEAREST)
                k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
                m = cv2.morphologyEx(m, cv2.MORPH_OPEN, k, iterations=1)
                m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, k, iterations=1)
                masks.append(m)

        return boxes, masks

# =========================
#  ТРЕКЕР (Norfair) с улучшенной метрикой
# =========================
class NorfairPersonTracker:
    def __init__(self, distance_threshold=TRACK_DISTANCE_THRESHOLD):
        self.tracker = Tracker(distance_function=self._distance, distance_threshold=distance_threshold)

    @staticmethod
    def _distance(det: Detection, trk) -> float:
        try:
            pts_det = det.points.astype(np.float32)
            pts_trk = trk.estimate.astype(np.float32)
            d_eu = float(np.linalg.norm(pts_det - pts_trk, axis=1).mean())
            bb = det.data.get("bbox") if isinstance(det.data, dict) else None
            if bb:
                bx1, by1, bx2, by2 = bb
                diag = max(1.0, float(np.hypot(bx2 - bx1, by2 - by1)))
            else:
                diag = 1.0
            d_eu_norm = d_eu / diag
        except Exception:
            d_eu_norm = 1.0

        d_iou = 1.0
        try:
            prev = getattr(trk, "last_detection", None)
            if prev is not None and hasattr(prev, "data"):
                prev_bbox = prev.data.get("bbox")
                bb = det.data.get("bbox")
                if prev_bbox is not None and bb is not None:
                    d_iou = 1.0 - iou_xyxy(prev_bbox, bb)
        except Exception:
            d_iou = 1.0

        return 0.65 * d_eu_norm + 0.35 * d_iou

    @staticmethod
    def _det_to_norfair(boxes):
        dets = []
        for x1, y1, x2, y2, conf in boxes:
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            bx, by = cx, y2
            points = np.array([[cx, cy], [bx, by]], dtype=np.float32)
            dets.append(Detection(points=points,
                                  scores=np.array([conf, conf], dtype=np.float32),
                                  data={"bbox": (int(x1), int(y1), int(x2), int(y2))}))
        return dets

    def update(self, boxes):
        dets = self._det_to_norfair(boxes)
        return self.tracker.update(detections=dets)

# =========================
#  АНАЛИТИКА / СОБЫТИЯ (на русском)
# =========================
class Analytics:
    def __init__(self, fps):
        self.events = []
        self.fps = float(fps or 25.0)
        self.per_track = defaultdict(lambda: {
            "in_mall": False,
            "counted_mall": False,
            "store_in": False,
            "last_pt": None,
            "last_frame": 0,
            "mall_time": 0.0,
            "store_time": 0.0
        })

    def _append(self, frame_idx, track_id, event):
        tsec = frame_idx / self.fps if self.fps>0 else 0.0
        self.events.append({
            "Время (с)": round(tsec, 3),
            "Кадр": int(frame_idx),
            "Час": int(tsec // 3600),
            "ID трека": int(track_id),
            "Событие": event,
        })

    def update_track_state(self, frame_idx, track_id, pt, mall_shape, store_shape,
                            line_shape, side_mall, side_store):
        st = self.per_track[track_id]
        prev_in_mall = st["in_mall"]
        now_in_mall = point_in_shape(pt[0], pt[1], mall_shape)
        now_in_store = point_in_shape(pt[0], pt[1], store_shape)

        dt_frames = max(0, frame_idx - st["last_frame"])
        dt = dt_frames / self.fps if self.fps > 0 else 0.0
        st["last_frame"] = frame_idx
        if prev_in_mall:
            st["mall_time"] += dt
        if now_in_store:
            st["store_time"] += dt

        if now_in_mall and not st["counted_mall"] and not prev_in_mall:
            st["counted_mall"] = True
            self._append(frame_idx, track_id, "Вход в ТЦ")

        # линейное пересечение (line_shape)
        if line_shape is not None and not st["store_in"] and st["last_pt"] is not None:
            a, b = line_shape["coords"]
            prev_side = int(np.sign(point_side_of_line(st["last_pt"], a, b)))
            cur_side = int(np.sign(point_side_of_line(pt, a, b)))
            if side_mall is None or side_store is None or side_mall == side_store:
                crossed = (prev_side != cur_side) and (prev_side != 0 or cur_side != 0)
                if crossed:
                    st["store_in"] = True
                    self._append(frame_idx, track_id, "Вход в магазин")
            else:
                if prev_side == side_mall and cur_side == side_store:
                    st["store_in"] = True
                    self._append(frame_idx, track_id, "Вход в магазин")

        st["in_mall"] = now_in_mall
        st["last_pt"] = pt

    def export(self):
        df_events = pd.DataFrame(self.events)
        if df_events.empty:
            df_events = pd.DataFrame(columns=["Время (с)", "Кадр", "Час", "ID трека", "Событие"])
        try:
            df_events["Час"] = df_events["Час"].astype(int)
        except Exception:
            pass

        if not df_events.empty:
            hourly = (
                df_events.groupby(["Час"])["Событие"].value_counts()
                .unstack(fill_value=0)
                .reset_index()
            )
            if "Вход в ТЦ" in hourly.columns:
                hourly = hourly.rename(columns={"Вход в ТЦ": "Входы в ТЦ"})
            if "Вход в магазин" in hourly.columns:
                hourly = hourly.rename(columns={"Вход в магазин": "Входы в магазин"})
        else:
            hourly = pd.DataFrame(columns=["Час", "Входы в ТЦ", "Входы в магазин"])

        total_in_mall = int((df_events["Событие"] == "Вход в ТЦ").sum()) if not df_events.empty else 0
        total_store_in = int((df_events["Событие"] == "Вход в магазин").sum()) if not df_events.empty else 0
        conversion = (total_store_in / total_in_mall * 100.0) if total_in_mall > 0 else 0.0

        dwell = pd.DataFrame([
            {
                "ID трека": tid,
                "Время в ТЦ, с": round(st["mall_time"], 2),
                "Время в магазине, с": round(st["store_time"], 2),
            }
            for tid, st in self.per_track.items()
        ])
        return df_events, hourly, dwell, total_in_mall, total_store_in, conversion

    @staticmethod
    def _save_excel_or_csv(df, path_xlsx, path_csv, index=False):
        try:
            df.to_excel(path_xlsx, index=index)
            print(f"[INFO] Сохранено Excel: {path_xlsx}")
        except Exception as e:
            df.to_csv(path_csv, index=index)
            print(f"[WARN] Excel не сохранён ({e}). Сохранено CSV: {path_csv}")

    def save_all(self):
        df_events, hourly, dwell, total_in_mall, total_store_in, conversion = self.export()
        self._save_excel_or_csv(df_events, SAVE_EVENTS_XLSX, SAVE_EVENTS_CSV, index=False)
        summary = hourly.copy()
        if "Входы в ТЦ" not in summary.columns:
            summary["Входы в ТЦ"] = 0
        if "Входы в магазин" not in summary.columns:
            summary["Входы в магазин"] = 0
        total_row = {
            "Час": "ИТОГО",
            "Входы в ТЦ": int(summary["Входы в ТЦ"].sum()) if not summary.empty else total_in_mall,
            "Входы в магазин": int(summary["Входы в магазин"].sum()) if not summary.empty else total_store_in,
            "Конверсия, %": round(conversion, 2),
        }
        if "Конверсия, %" not in summary.columns:
            summary["Конверсия, %"] = np.nan
        summary = pd.concat([summary, pd.DataFrame([total_row])], ignore_index=True)
        try:
            with pd.ExcelWriter(SAVE_SUMMARY_XLSX) as xw:
                summary.to_excel(xw, sheet_name="Сводка", index=False)
                dwell.to_excel(xw, sheet_name="Время по трекам", index=False)
            print(f"[INFO] Сохранено Excel: {SAVE_SUMMARY_XLSX}")
        except Exception as e:
            summary.to_csv(SAVE_SUMMARY_CSV, index=False)
            print(f"[WARN] Excel не сохранён ({e}). Сохранено CSV: {SAVE_SUMMARY_CSV}")

# =========================
#  ПОДГОТОВКА КАДРА / ROI
# =========================
def optimize_frame(frame, size=TARGET_SIZE):
    f = cv2.resize(frame, size)
    f = cv2.GaussianBlur(f, (3, 3), 0)
    return f

def apply_roi_mask(frame, shapes):
    """
    shapes: list of shape dicts (rect, poly, circle). line ignored.
    Возвращает (masked_frame, mask) где mask = None если не задано.
    """
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    for s in shapes:
        if s is None:
            continue
        typ = s.get("type")
        if typ == "rect":
            (x1,y1),(x2,y2) = s["coords"]
            cv2.rectangle(mask, (x1,y1), (x2,y2), 255, -1)
        elif typ == "poly":
            pts = np.array(s["coords"], dtype=np.int32)
            if pts.shape[0] >= 3:
                cv2.fillPoly(mask, [pts], 255)
        elif typ == "circle":
            cx, cy, r = s["coords"]
            cv2.circle(mask, (int(cx),int(cy)), int(r), 255, -1)
        # линия не участвует в ROI
    if mask.max() == 0:
        return frame, None
    masked = frame.copy()
    masked[mask == 0] = 0
    return masked, mask

def _shape_bbox(shape):
    """Огибающий прямоугольник для shape в координатах кадра"""
    if shape is None:
        return None
    typ = shape.get("type")
    if typ == "rect":
        (x1,y1),(x2,y2) = shape["coords"]
        return [min(x1,x2), min(y1,y2), max(x1,x2), max(y1,y2)]
    if typ == "poly":
        pts = np.array(shape["coords"], dtype=np.int32)
        if pts.shape[0] < 3:
            return None
        x,y,w,h = cv2.boundingRect(pts)
        return [x, y, x+w, y+h]
    if typ == "circle":
        cx, cy, r = shape["coords"]
        return [int(cx-r), int(cy-r), int(cx+r), int(cy+r)]
    return None

def _union_bbox(shapes, w, h, pad=0):
    """Объединение огибающих. Возвращает (x1,y1,x2,y2) или None."""
    boxes = []
    for s in shapes:
        b = _shape_bbox(s)
        if b is not None:
            boxes.append(b)
    if not boxes:
        return None
    arr = np.array(boxes, dtype=np.int32)
    x1 = max(0, int(arr[:,0].min()) - pad)
    y1 = max(0, int(arr[:,1].min()) - pad)
    x2 = min(w, int(arr[:,2].max()) + pad)
    y2 = min(h, int(arr[:,3].max()) + pad)
    if x2 <= x1 or y2 <= y1:
        return None
    return (x1, y1, x2, y2)

# =========================
#  ЗОНЫ / НАПРАВЛЕНИЕ ЛИНИИ
# =========================
class ZoneManager:
    def __init__(self):
        self.mall = None    # shape dict
        self.store = None
        self.entry_line = None  # shape dict of type 'line'
        self.side_mall = None
        self.side_store = None

    def set(self, mall_shape, store_shape, entry_line_shape):
        self.mall = mall_shape
        self.store = store_shape
        self.entry_line = entry_line_shape
        self._recompute_sides()

    def _recompute_sides(self):
        self.side_mall = self.side_store = None
        if self.entry_line and self.mall and self.store:
            a,b = self.entry_line["coords"]
            mall_c = center_of_shape(self.mall)
            store_c = center_of_shape(self.store)
            if mall_c is not None:
                self.side_mall = int(np.sign(point_side_of_line(mall_c, a, b)))
            if store_c is not None:
                self.side_store = int(np.sign(point_side_of_line(store_c, a, b)))

# =========================
#  Движение / Пропуск пустых кадров
# =========================
class MotionGate:
    """
    Лёгкая оценка движения на кадре (после optimize_frame).
    Управляет адаптивным шагом (stride) и "охлаждением", чтобы не пропустить события.
    """
    def __init__(self, frame_shape):
        h, w = frame_shape[:2]
        # KNN без теней — быстрее, чем MOG2 с тенями, и меньше ложных от дрожания яркости
        self.bg = cv2.createBackgroundSubtractorKNN(history=MOTION_HISTORY, dist2Threshold=400.0, detectShadows=False)
        self.cooldown = 0
        self.stride = 1
        self._prev_small = None

    def _cheap_diff_skip(self, frame_bgr):
        if not DIFF_SKIP_ENABLED:
            return False
        small = cv2.resize(frame_bgr, DIFF_DOWNSCALE)
        small = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        if self._prev_small is None:
            self._prev_small = small
            return False
        mad = float(np.mean(np.abs(small.astype(np.int16) - self._prev_small.astype(np.int16))))
        self._prev_small = small
        return mad < DIFF_THRESH_MEANABS

    def update(self, frame_bgr):
        """Возвращает (motion_ratio: float, should_skip_now: bool, stride_suggestion: int)"""
        # дешёвый "дубликат" — можно пропустить прямо сейчас
        if self._cheap_diff_skip(frame_bgr):
            # на таких кадрах тоже полезно немного увеличить шаг
            self.stride = min(ADAPTIVE_MAX_STRIDE, self.stride + 1)
            return 0.0, True, self.stride

        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        fg = self.bg.apply(gray, learningRate=-1)
        # подавим шум/зерно
        fg = cv2.medianBlur(fg, 3)
        _, fg = cv2.threshold(fg, 200, 255, cv2.THRESH_BINARY)
        motion_ratio = float(np.mean(fg > 0))

        # логика триггеров
        strong_motion = motion_ratio >= MOTION_THRESH_HIGH
        weak_motion = motion_ratio >= MOTION_THRESH_LOW

        if strong_motion:
            self.cooldown = MOTION_COOLDOWN
            self.stride = 1
            return motion_ratio, False, 1

        if self.cooldown > 0:
            self.cooldown -= 1
            self.stride = 1
            return motion_ratio, False, 1

        if weak_motion:
            # есть слабое движение — обработаем, но шаг оставим 1
            self.stride = 1
            return motion_ratio, False, 1

        # движения нет — можно пропускать часть кадров
        self.stride = min(ADAPTIVE_MAX_STRIDE, self.stride + 1)
        return motion_ratio, True, self.stride

# =========================
#  ПРИЛОЖЕНИЕ (Tkinter + OpenCV)
# =========================
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class App:
    def __init__(self, root):
        # небольшой буст OpenCV
        try:
            cv2.setUseOptimized(True)
        except Exception:
            pass

        self.root = root
        self.root.title(APP_TITLE)
        self.model_path = DEFAULT_MODEL_PATH

        # Верхние кнопки
        top = tk.Frame(root)
        top.pack(fill="x", padx=10, pady=8)
        tk.Button(top, text="1) Выбрать модель", command=self.choose_model).pack(side="left", padx=4)
        tk.Button(top, text="2) Выбрать видео", command=self.choose_video).pack(side="left", padx=4)
        tk.Button(top, text="3) Разметить зоны", command=self.select_zones).pack(side="left", padx=4)
        tk.Button(top, text="Старт", command=self.start).pack(side="left", padx=8)
        tk.Button(top, text="Стоп", command=self.stop).pack(side="left", padx=4)
        tk.Button(top, text="Сохранить отчёты", command=self.save_now).pack(side="left", padx=8)

        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(padx=10, pady=(5, 0), fill="x")
        self.lbl_status = tk.Label(root, text="Статус: ожидание")
        self.lbl_status.pack(padx=10, pady=(2, 8), anchor="w")

        self.video_panel = tk.Label(root)
        self.video_panel.pack(padx=10, pady=5)

        import queue
        self._frame_queue = queue.Queue()

        self._selecting_zones = False
        self._zone_sel_win = None
        self._zone_base_frame = None
        self._zone_shapes = {"mall": None, "store": None, "line": None}
        self._zone_target = tk.StringVar(value="mall")
        self._zone_shape_type = tk.StringVar(value="rect")
        self._zone_poly_points = []
        self._zone_drag_start = None

        self._update_video_panel()

        self.video_path = None
        self.detector = None
        self.tracker = NorfairPersonTracker()
        self.zones = ZoneManager()
        self.analytics = None

        self.running = False
        self.thread = None
        self.heatmap = None
        self.last_heat_masks = False

        # counters
        self._fps_value = 0.0
        self._fps_counter = 0
        self._fps_t0 = None
        self._frame_idx = 0
        self._total_frames = 0
        self._last_autosave = time.time()

        # ускоритель пустых кадров
        self.motion_gate = None

        self._schedule_status_update()

    # UI actions
    def choose_model(self):
        path = filedialog.askopenfilename(title="Выберите файл модели YOLO (.pt)", filetypes=[("PyTorch модели", "*.pt")])
        if path:
            self.model_path = path
            messagebox.showinfo("Модель выбрана", os.path.basename(path))

    def choose_video(self):
        path = filedialog.askopenfilename(title="Видео", filetypes=[("Видео", "*.mp4;*.avi;*.mov;*.mkv")])
        if path:
            self.video_path = path
            cap = cv2.VideoCapture(self.video_path)
            self._total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
            cap.release()
            messagebox.showinfo("Видео выбрано", os.path.basename(path))

    def select_zones(self):
        if self.video_path is None:
            messagebox.showwarning("Нет видео", "Сначала выберите видео.")
            return
        cap = cv2.VideoCapture(self.video_path)
        ok, frame0 = cap.read()
        cap.release()
        if not ok:
            messagebox.showerror("Ошибка", "Не удалось прочитать видео.")
            return
        frame = optimize_frame(frame0)
        self._zone_base_frame = frame.copy()
        self._zone_shapes = {"mall": None, "store": None, "line": None}
        self._zone_poly_points = []
        self._zone_drag_start = None
        self._selecting_zones = True

        zone_win = tk.Toplevel(self.root)
        zone_win.title("Разметка зон")
        def on_close():
            self._selecting_zones = False
            zone_win.destroy()
        zone_win.protocol("WM_DELETE_WINDOW", on_close)

        h, w = frame.shape[:2]
        zone_img_label = tk.Label(zone_win)
        zone_img_label.pack(padx=5, pady=5)

        ctrl = tk.Frame(zone_win)
        ctrl.pack(fill="x", padx=5, pady=5)
        tk.Label(ctrl, text="Зона:").pack(side="left")
        zone_menu = ttk.OptionMenu(ctrl, self._zone_target, self._zone_target.get(), "mall", "store", "line")
        zone_menu.pack(side="left", padx=4)
        tk.Label(ctrl, text="Фигура:").pack(side="left")
        shape_menu = ttk.OptionMenu(ctrl, self._zone_shape_type, self._zone_shape_type.get(), "rect", "poly", "circle", "line")
        shape_menu.pack(side="left", padx=4)
        def finish_poly():
            target = self._zone_target.get()
            stype = self._zone_shape_type.get()
            if stype == "poly" and target in ("mall", "store") and len(self._zone_poly_points) >= 3:
                self._zone_shapes[target] = {"type": "poly", "coords": list(self._zone_poly_points)}
                self._zone_poly_points = []
                self._zone_drag_start = None
                update_display()
        tk.Button(ctrl, text="Завершить полигон", command=finish_poly).pack(side="left", padx=4)
        def cancel_poly():
            self._zone_poly_points = []
            self._zone_drag_start = None
            update_display()
        tk.Button(ctrl, text="Очистить", command=cancel_poly).pack(side="left", padx=4)
        def reset_all():
            self._zone_shapes = {"mall": None, "store": None, "line": None}
            self._zone_poly_points = []
            self._zone_drag_start = None
            update_display()
        tk.Button(ctrl, text="Сброс", command=reset_all).pack(side="left", padx=4)
        def save_zones():
            self.zones.set(self._zone_shapes.get("mall"), self._zone_shapes.get("store"), self._zone_shapes.get("line"))
            self._selecting_zones = False
            zone_win.destroy()
            messagebox.showinfo("Готово", "Зоны и линия заданы.")
        tk.Button(ctrl, text="Сохранить", command=save_zones).pack(side="right", padx=4)

        def render_zone_frame():
            img = self._zone_base_frame.copy()
            for key, s in self._zone_shapes.items():
                if s is None:
                    continue
                if s["type"] == "rect":
                    (a, b) = s["coords"]
                    cv2.rectangle(img, a, b, (0, 200, 0) if key == "mall" else (0, 165, 255) if key == "store" else (0, 0, 255), 2)
                elif s["type"] == "poly":
                    pts = np.array(s["coords"], dtype=np.int32)
                    if pts.shape[0] >= 3:
                        cv2.polylines(img, [pts], True, (0, 200, 0) if key == "mall" else (0, 165, 255) if key == "store" else (0, 0, 255), 2)
                elif s["type"] == "circle":
                    cx, cy, r = s["coords"]
                    cv2.circle(img, (int(cx), int(cy)), int(r), (0, 200, 0) if key == "mall" else (0, 165, 255) if key == "store" else (0, 0, 255), 2)
                elif s["type"] == "line":
                    a, b = s["coords"]
                    cv2.line(img, a, b, (0, 0, 255), 2)
                c = center_of_shape(s)
                if c is not None:
                    if key == "mall":
                        draw_text(img, "ТЦ", (max(5, c[0] - 10), max(20, c[1])), (0, 200, 0))
                    elif key == "store":
                        draw_text(img, "Магазин", (max(5, c[0] - 10), max(20, c[1])), (0, 165, 255))
                    elif key == "line":
                        a, _ = s["coords"]
                        draw_text(img, "Линия входа", (a[0], a[1] - 20), (0, 0, 255))
            if self._zone_poly_points:
                for p in self._zone_poly_points:
                    cv2.circle(img, p, 4, (0, 200, 200), -1)
                if len(self._zone_poly_points) >= 2:
                    cv2.polylines(img, [np.array(self._zone_poly_points, dtype=np.int32)], False, (0, 200, 200), 2)
            if self._zone_drag_start is not None:
                stype = self._zone_shape_type.get()
                x0, y0 = self._zone_drag_start
                if hasattr(render_zone_frame, "_drag_last"):
                    x1, y1 = render_zone_frame._drag_last
                    if stype == "rect":
                        cv2.rectangle(img, (x0, y0), (x1, y1), (255, 255, 0), 2)
                    elif stype == "circle":
                        r = int(max(1, np.hypot(x1 - x0, y1 - y0)))
                        cv2.circle(img, (x0, y0), r, (255, 255, 0), 2)
                    elif stype == "line":
                        cv2.line(img, (x0, y0), (x1, y1), (255, 255, 0), 2)
            return img

        def update_display():
            img = render_zone_frame()
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img_rgb)
            imgtk = ImageTk.PhotoImage(image=pil_img)
            zone_img_label.imgtk = imgtk
            zone_img_label.config(image=imgtk)

        def on_motion(event):
            if self._zone_drag_start is not None:
                render_zone_frame._drag_last = (event.x, event.y)
                update_display()
        def on_press(event):
            target = self._zone_target.get()
            stype = self._zone_shape_type.get()
            if stype == "poly" and target in ("mall", "store"):
                self._zone_poly_points.append((event.x, event.y))
                update_display()
            else:
                self._zone_drag_start = (event.x, event.y)
        def on_release(event):
            if self._zone_drag_start is None:
                return
            x0, y0 = self._zone_drag_start
            x1, y1 = event.x, event.y
            target = self._zone_target.get()
            stype = self._zone_shape_type.get()
            if stype == "rect" and target in ("mall", "store"):
                rect = rect_from_two_points((x0, y0), (x1, y1))
                self._zone_shapes[target] = {"type": "rect", "coords": rect}
            elif stype == "circle" and target in ("mall", "store"):
                r = int(max(1, np.hypot(x1 - x0, y1 - y0)))
                self._zone_shapes[target] = {"type": "circle", "coords": (x0, y0, r)}
            elif stype == "line" and target == "line":
                self._zone_shapes["line"] = {"type": "line", "coords": ((x0, y0), (x1, y1))}
            self._zone_drag_start = None
            if hasattr(render_zone_frame, "_drag_last"):
                delattr(render_zone_frame, "_drag_last")
            update_display()

        zone_img_label.bind("<ButtonPress-1>", on_press)
        zone_img_label.bind("<ButtonRelease-1>", on_release)
        zone_img_label.bind("<B1-Motion>", on_motion)

        update_display()
        self.root.wait_window(zone_win)

    # Основной цикл
    def start(self):
        if self.video_path is None:
            messagebox.showwarning("Нет видео", "Сначала выберите видео.")
            return
        if self.running:
            return
        try:
            self.detector = Detector(self.model_path, conf=YOLO_CONF)
        except Exception as e:
            messagebox.showerror("Модель", str(e))
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _fast_forward(self, cap, n_to_skip: int):
        """Быстрый пропуск кадров (без decode), корректно обновляя счётчики."""
        skipped = 0
        while skipped < n_to_skip:
            ok = cap.grab()
            if not ok:
                return False, skipped
            self._frame_idx += 1
            skipped += 1
            # обновим прогресс/FPS чуть-чуть, чтобы UI не отставал
            self._update_fps()
            self._update_progress()
        return True, skipped

    def _run_loop(self):
        cap = cv2.VideoCapture(self.video_path)
        ok, frame = cap.read()
        if not ok:
            cap.release()
            messagebox.showerror("Ошибка", "Не удалось прочитать видео.")
            self.running = False
            return

        fps_meta = cap.get(cv2.CAP_PROP_FPS) or 25.0
        self.analytics = Analytics(fps=fps_meta)
        self._frame_idx = 0
        self._fps_counter = 0
        self._fps_t0 = time.time()
        self.heatmap = None

        # инициализация детектора движения после первого optimize_frame
        first_proc = optimize_frame(frame)
        if MOTION_SKIP_ENABLED:
            self.motion_gate = MotionGate(first_proc.shape)
        else:
            self.motion_gate = None

        # Вставим назад первый кадр в цикл
        cur_frame = frame

        while self.running and ok:
            # учёт кадра (read для cur_frame уже сделан раньше)
            self._frame_idx += 1

            # подготовка
            proc = optimize_frame(cur_frame)
            h, w = proc.shape[:2]
            if self.heatmap is None:
                self.heatmap = np.zeros((h, w), dtype=np.float32)

            # -------------------------
            # ЭТАП: решение "пропускать?" по движению
            # -------------------------
            if self.motion_gate is not None:
                motion_ratio, should_skip, stride = self.motion_gate.update(proc)
                # если пусто — быстро "перематываем" несколько кадров и переходим к следующей итерации
                if should_skip:
                    # попробуем пропустить stride-1 дополнительных кадров (кроме текущего)
                    to_skip = max(1, min(ADAPTIVE_MAX_STRIDE, stride))  # сколько дополнительно пропустить сейчас
                    ok, skipped = self._fast_forward(cap, to_skip)
                    if not ok:
                        break
                    ok, cur_frame = cap.read()
                    if not ok:
                        break
                    # Никакой тяжёлой детекции на пустых кадрах не делаем
                    # Периодически всё же отправляем кадр в UI, чтобы была "живая" картинка
                    try:
                        if (self._frame_idx % (SHOW_FPS_EVERY*2)) == 0:
                            vis = proc.copy()
                            draw_text(vis, f"Пусто: skip x{to_skip} | motion={motion_ratio:.4f}", (10, 28), (200,200,200))
                            while not self._frame_queue.empty():
                                self._frame_queue.get_nowait()
                            self._frame_queue.put_nowait(vis)
                    except Exception:
                        pass
                    # продолжаем следующий цикл
                    self._update_fps()
                    self._update_progress()
                    continue

            # -------------------------
            # ЭТАП: детекция (с опцией ROI-кропа)
            # -------------------------
            det_frame = proc
            offset_xy = (0, 0)
            used_crop = False

            if DETECT_IN_ROI_ONLY and (self.zones.mall or self.zones.store):
                ub = _union_bbox([self.zones.mall, self.zones.store], w, h, pad=ROI_PAD_PX)
                if ub is not None:
                    x1, y1, x2, y2 = ub
                    area = (x2-x1)*(y2-y1)
                    if area > 0 and area < 0.85*w*h:  # не обрезаем если почти весь кадр
                        det_frame = proc[y1:y2, x1:x2]
                        offset_xy = (x1, y1)
                        used_crop = True

            boxes, masks = self.detector.detect(det_frame)

            # Если был кроп — смаппим координаты назад в полный кадр
            if used_crop:
                ox, oy = offset_xy
                if boxes:
                    boxes = [(x1+ox, y1+oy, x2+ox, y2+oy, conf) for (x1,y1,x2,y2,conf) in boxes]
                if masks:
                    full_masks = []
                    for m in masks:
                        # m — размером с det_frame; впишем в full
                        full_m = np.zeros((h, w), dtype=np.uint8)
                        mh, mw = m.shape
                        full_m[oy:oy+mh, ox:ox+mw] = m
                        full_masks.append(full_m)
                    masks = full_masks

            tracked = self.tracker.update(boxes)

            # -------------------------
            # Теплокарта
            # -------------------------
            roi_shapes = [s for s in (self.zones.mall, self.zones.store) if s is not None]
            _, roi_mask = apply_roi_mask(proc, roi_shapes)

            if masks:
                for m in masks:
                    if roi_mask is not None:
                        m = cv2.bitwise_and(m, roi_mask)
                    self.heatmap[m > 0] += 1.0
                self.last_heat_masks = True
            else:
                for tr in tracked:
                    try:
                        cx, cy = int(tr.estimate[0][0]), int(tr.estimate[0][1])
                        cv2.circle(self.heatmap, (cx, cy), 7, 1.0, -1)
                    except Exception:
                        pass
                self.last_heat_masks = False

            # -------------------------
            # События / подсчёт / рендер
            # -------------------------
            mall_now = 0
            store_now = 0
            frame_vis = proc.copy()

            for tr in tracked:
                tid = tr.id
                try:
                    cx, cy = int(tr.estimate[0][0]), int(tr.estimate[0][1])
                except Exception:
                    continue
                pt = (cx, cy)
                if point_in_shape(cx, cy, self.zones.mall):
                    mall_now += 1
                if point_in_shape(cx, cy, self.zones.store):
                    store_now += 1

                self.analytics.update_track_state(
                    frame_idx=self._frame_idx,
                    track_id=tid,
                    pt=pt,
                    mall_shape=self.zones.mall,
                    store_shape=self.zones.store,
                    line_shape=self.zones.entry_line,
                    side_mall=self.zones.side_mall,
                    side_store=self.zones.side_store,
                )

                cv2.circle(frame_vis, (cx, cy), 4, (0, 255, 0), -1)
                draw_text(frame_vis, f"ID {tid}", (cx + 6, cy - 18), (0,255,0))

            for x1, y1, x2, y2, conf in boxes:
                cv2.rectangle(frame_vis, (x1, y1), (x2, y2), (110, 220, 0), 2)
                draw_text(frame_vis, f"{conf:.2f}", (x1, max(5, y1 - 18)), (110,220,0))

            if masks:
                overlay = np.zeros_like(frame_vis)
                for m in masks:
                    overlay[m.astype(bool)] = (0, 255, 0)
                frame_vis = cv2.addWeighted(frame_vis, 1.0, overlay, DRAW_MASK_ALPHA, 0)

            if self.zones.mall:
                s = self.zones.mall
                if s["type"] == "rect":
                    (a,b) = s["coords"]; cv2.rectangle(frame_vis,a,b,(0,200,0),2)
                elif s["type"] == "poly":
                    pts = np.array(s["coords"], dtype=np.int32)
                    if pts.shape[0]>=3:
                        cv2.polylines(frame_vis,[pts],True,(0,200,0),2)
                elif s["type"] == "circle":
                    cx,cy,r = s["coords"]; cv2.circle(frame_vis,(int(cx),int(cy)),int(r),(0,200,0),2)
                c = center_of_shape(s) or (10,10)
                draw_text(frame_vis, "ТЦ", (max(5,c[0]-10), max(20,c[1])) , (0,200,0))

            if self.zones.store:
                s = self.zones.store
                if s["type"] == "rect":
                    (a,b) = s["coords"]; cv2.rectangle(frame_vis,a,b,(0,165,255),2)
                elif s["type"] == "poly":
                    pts = np.array(s["coords"], dtype=np.int32)
                    if pts.shape[0]>=3:
                        cv2.polylines(frame_vis,[pts],True,(0,165,255),2)
                elif s["type"] == "circle":
                    cx,cy,r = s["coords"]; cv2.circle(frame_vis,(int(cx),int(cy)),int(r),(0,165,255),2)
                c = center_of_shape(s) or (10,40)
                draw_text(frame_vis, "Магазин", (max(5,c[0]-10), max(20,c[1])) , (0,165,255))

            if self.zones.entry_line:
                a,b = self.zones.entry_line["coords"]
                cv2.line(frame_vis, a, b, (0, 0, 255), 2)
                draw_text(frame_vis, "Линия входа", (a[0], a[1]-20), (0,0,255))

            df_events, _, _, total_in_mall, total_store_in, conv = self.analytics.export()
            mode_txt = "SEG" if self.last_heat_masks else "BOX"
            draw_text(frame_vis, f"Сейчас: ТЦ={mall_now}  Магазин={store_now}", (10, 28))
            draw_text(frame_vis, f"Итого: ТЦ={total_in_mall}  Магазин={total_store_in}  Конверсия={conv:.1f}%", (10, 52))
            draw_text(frame_vis, f"{mode_txt} | FPS:{self._fps_value:.1f}", (10, 76), (180,255,180))

            # Теплокарта поверх
            heat_vis = self._heatmap_to_bgr(self.heatmap)
            frame_vis = cv2.addWeighted(frame_vis, 1.0, heat_vis, DRAW_HEAT_ALPHA, 0)

            # (необязательно) показать прямоугольник кропа детекции
            if DETECT_IN_ROI_ONLY and used_crop:
                x1, y1 = offset_xy
                x2 = x1 + det_frame.shape[1]
                y2 = y1 + det_frame.shape[0]
                cv2.rectangle(frame_vis, (x1,y1), (x2,y2), (255,255,0), 1)
                draw_text(frame_vis, "ROI детекции", (x1+4, max(15,y1-8)), (255,255,0))

            # в UI — последний готовый кадр
            try:
                while not self._frame_queue.empty():
                    self._frame_queue.get_nowait()
                self._frame_queue.put_nowait(frame_vis.copy())
            except Exception:
                pass

            # FPS / прогресс / автосейв
            self._update_fps()
            self._update_progress()
            now = time.time()
            if now - self._last_autosave >= AUTOSAVE_SEC:
                self._last_autosave = now
                try:
                    self.analytics.save_all()
                    if self.heatmap is not None:
                        self._save_heatmap_png(SAVE_HEATMAP_PNG)
                    print("[INFO] Автосохранение выполнено")
                except Exception as e:
                    print(f"[WARN] Автосохранение не удалось: {e}")

            # читаем следующий исходный кадр
            ok, cur_frame = cap.read()

        cap.release()
        try:
            self.analytics.save_all()
            if self.heatmap is not None:
                self._save_heatmap_png(SAVE_HEATMAP_PNG)
        except Exception as e:
            messagebox.showwarning("Сохранение", f"Не удалось сохранить отчёты/теплокарту: {e}")
        self.running = False

    # сервисы
    def save_now(self):
        try:
            if self.analytics is not None:
                self.analytics.save_all()
            if self.heatmap is not None:
                self._save_heatmap_png(SAVE_HEATMAP_PNG)
            messagebox.showinfo("Сохранение", "Отчёты сохранены.")
        except Exception as e:
            messagebox.showwarning("Сохранение", f"Не удалось сохранить: {e}")

    def _schedule_status_update(self):
        if self.running:
            df_events, _, _, total_in_mall, total_store_in, conv = (self.analytics.export() if self.analytics else (pd.DataFrame(), None, None, 0, 0, 0.0))
            st = f"Кадр: {self._frame_idx}/{self._total_frames or '?'} | FPS: {self._fps_value:.1f} | Итого ТЦ: {total_in_mall} | Магазин: {total_store_in} | Конверсия: {conv:.1f}%"
        else:
            st = "Статус: ожидание"
        self.lbl_status.config(text=st)
        self.root.after(200, self._schedule_status_update)

    def _update_fps(self):
        self._fps_counter += 1
        if self._fps_t0 is None:
            self._fps_t0 = time.time()
        if self._fps_counter % SHOW_FPS_EVERY == 0:
            t1 = time.time()
            dt = max(1e-6, t1 - self._fps_t0)
            self._fps_value = self._fps_counter / dt
            self._fps_t0 = t1
            self._fps_counter = 0

    def _update_progress(self):
        if self._total_frames > 0:
            val = min(100, int(self._frame_idx * 100 / self._total_frames))
            self.progress["value"] = val

    def _heatmap_to_bgr(self, hm_float):
        if hm_float is None:
            hm = np.zeros((1, 1), dtype=np.uint8)
        else:
            hm = np.array(hm_float, copy=True)
            if hm.size == 0:
                hm = np.zeros((1, 1), dtype=np.uint8)
        try:
            if hm.max() > 0:
                hm_uint8 = (hm / float(hm.max()) * 255.0).astype(np.uint8)
            else:
                hm_uint8 = hm.astype(np.uint8)
        except Exception:
            hm_uint8 = np.zeros_like(hm, dtype=np.uint8)
        if hm_uint8.ndim == 3:
            hm_uint8 = hm_uint8[..., 0]
        return cv2.applyColorMap(hm_uint8, cv2.COLORMAP_JET)

    def _update_video_panel(self):
        try:
            if not self._selecting_zones:
                frame = self._frame_queue.get_nowait()
                img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(img_rgb)
                imgtk = ImageTk.PhotoImage(image=pil_img)
                self.video_panel.imgtk = imgtk
                self.video_panel.config(image=imgtk)
        except Exception:
            pass
        self.root.after(30, self._update_video_panel)

    def _save_heatmap_png(self, path_png):
        if self.heatmap is not None:
            vis = self._heatmap_to_bgr(self.heatmap)
            cv2.imwrite(path_png, vis)

# -------------------- Запуск приложения --------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
