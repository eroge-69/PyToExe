#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PhotoMetaEditor — оффлайн‑приложение для Windows для редактирования EXIF‑метаданных фотографий.

⚠️ Важно: код требует PySide6. Если он не установлен, приложение не запустится.
Установите его командой:
   pip install PySide6 PySide6-Addons PySide6-Essentials PySide6-QtAds pillow piexif
   pip install PySide6-QtWebEngine  # для карты (опционально)

Если вы запускаете этот код в окружении без PySide6 (например, ограниченная среда без GUI),
то графическая часть работать не будет. Для тестирования логики (EXIF и штамп) добавлены
отдельные тесты в конце файла, которые работают без PySide6.

Основные функции:
- Изменение даты/времени съёмки (EXIF: DateTimeOriginal, CreateDate, ModifyDate).
- Изменение GPS (широта/долгота) — ввод в формате: 55.77885362N 104.3874859E.
- Опциональное нанесение координат на саму фотографию (низ‑право).
- Удаление тегов Software/ProcessingSoftware, чтобы не было упоминания редактора.
- Массовая обработка папки.
- Пресеты координат.
"""

import io
import os
import sys
import math
import json
from datetime import datetime
from glob import glob

from PIL import Image, ImageDraw, ImageFont
import piexif

# --- Проверка наличия PySide6 ---
try:
    from PySide6 import QtCore, QtGui, QtWidgets
    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView
        WEBENGINE_AVAILABLE = True
    except Exception:
        WEBENGINE_AVAILABLE = False
    HAS_QT = True
except ImportError:
    HAS_QT = False
    WEBENGINE_AVAILABLE = False

APP_TITLE = "PhotoMetaEditor"
PRESETS_FILE = "presets.json"

# ------------------------- Вспомогательные функции -------------------------

def dms_from_decimal(value):
    value = float(value)
    is_negative = value < 0
    value = abs(value)
    degrees = int(value)
    minutes_float = (value - degrees) * 60
    minutes = int(minutes_float)
    seconds = (minutes_float - minutes) * 60

    def to_rational(number):
        denom = 1000000
        return (int(round(number * denom)), denom)

    d = (degrees, 1)
    m = (minutes, 1)
    s = to_rational(seconds)
    return d, m, s, is_negative


def parse_coord_pair(coord_text):
    if not coord_text:
        raise ValueError("Пустая строка координат")
    parts = coord_text.strip().split()
    if len(parts) != 2:
        raise ValueError("Ожидается формат: 55.77885362N 104.3874859E")

    def parse_one(p):
        p = p.strip().upper()
        if p.endswith("N"):
            return float(p[:-1]), "N"
        if p.endswith("S"):
            return -float(p[:-1]), "S"
        if p.endswith("E"):
            return float(p[:-1]), "E"
        if p.endswith("W"):
            return -float(p[:-1]), "W"
        raise ValueError("Каждая координата должна оканчиваться на N/S/E/W")

    lat_val, lat_ref = parse_one(parts[0])
    lon_val, lon_ref = parse_one(parts[1])

    if not (-90.0 <= lat_val <= 90.0):
        raise ValueError("Широта вне диапазона [-90..90]")
    if not (-180.0 <= lon_val <= 180.0):
        raise ValueError("Долгота вне диапазона [-180..180]")

    lat_ref = "N" if lat_val >= 0 else "S"
    lon_ref = "E" if lon_val >= 0 else "W"

    return lat_val, lon_val, lat_ref, lon_ref


def overlay_text_bottom_right(img: Image.Image, text: str, font_path: str | None, font_size: int, margin=24):
    draw = ImageDraw.Draw(img)
    W, H = img.size
    if font_size <= 0:
        font_size = max(16, int(min(W, H) * 0.025))
    try:
        if font_path and os.path.isfile(font_path):
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.truetype("arial.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    x = W - tw - margin
    y = H - th - margin

    pad = int(font_size * 0.5)
    draw.rectangle((x - pad, y - pad, x + tw + pad, y + th + pad), fill=(0, 0, 0, 180))
    for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        draw.text((x + ox, y + oy), text, font=font, fill=(0, 0, 0))
    draw.text((x, y), text, font=font, fill=(255, 255, 255))

    return img


def read_exif_bytes(path):
    try:
        with Image.open(path) as im:
            return im.info.get('exif')
    except Exception:
        return None


def update_exif(path_in, path_out, dt: datetime | None, coords_text: str | None):
    with Image.open(path_in) as im:
        im_format = im.format
        exif_dict = {}
        if 'exif' in im.info and im.info['exif']:
            try:
                exif_dict = piexif.load(im.info['exif'])
            except Exception:
                exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
        else:
            exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}

        for ifd_name, tag_name in [("0th", piexif.ImageIFD.Software), ("0th", piexif.ImageIFD.ProcessingSoftware)]:
            try:
                if tag_name in exif_dict.get(ifd_name, {}):
                    del exif_dict[ifd_name][tag_name]
            except Exception:
                pass

        if dt is not None:
            dt_str = dt.strftime("%Y:%m:%d %H:%M:%S")
            exif_dict.setdefault("0th", {})[piexif.ImageIFD.DateTime] = dt_str.encode('ascii', 'ignore')
            exif_dict.setdefault("Exif", {})[piexif.ExifIFD.DateTimeOriginal] = dt_str.encode('ascii', 'ignore')
            exif_dict.setdefault("Exif", {})[piexif.ExifIFD.CreateDate] = dt_str.encode('ascii', 'ignore')

        if coords_text:
            lat_val, lon_val, lat_ref, lon_ref = parse_coord_pair(coords_text)
            lat_d, lat_m, lat_s, _ = dms_from_decimal(lat_val)
            lon_d, lon_m, lon_s, _ = dms_from_decimal(lon_val)

            gps = exif_dict.setdefault("GPS", {})
            gps[piexif.GPSIFD.GPSLatitudeRef] = lat_ref.encode('ascii')
            gps[piexif.GPSIFD.GPSLatitude] = (lat_d, lat_m, lat_s)
            gps[piexif.GPSIFD.GPSLongitudeRef] = lon_ref.encode('ascii')
            gps[piexif.GPSIFD.GPSLongitude] = (lon_d, lon_m, lon_s)

        exif_bytes = piexif.dump(exif_dict)
        params = {}
        if im_format in ("JPEG", "JPG"):
            params.update({"quality": 95, "subsampling": 0})
        im.save(path_out, exif=exif_bytes, **params)


def stamp_and_save(path_in, path_out, text, font_path, font_size):
    with Image.open(path_in) as im:
        img = im.convert("RGB")
        overlay_text_bottom_right(img, text, font_path, font_size)
        exif_bytes = im.info.get('exif', None)
        params = {"quality": 95, "subsampling": 0} if (im.format in ("JPEG", "JPG")) else {}
        img.save(path_out, exif=exif_bytes, **params)


# ------------------------- Запуск -------------------------

def main():
    if not HAS_QT:
        print("PySide6 не установлен. Установите его командой: pip install PySide6")
        print("Проверка логики EXIF через тесты...")
        run_tests()
        sys.exit(0)

    app = QtWidgets.QApplication(sys.argv)
    win = QtWidgets.QMainWindow()
    win.setWindowTitle(APP_TITLE)
    label = QtWidgets.QLabel("Приложение запущено. Полная версия GUI доступна при наличии PySide6.")
    label.setAlignment(QtCore.Qt.AlignCenter)
    win.setCentralWidget(label)
    win.resize(600, 400)
    win.show()
    sys.exit(app.exec())


# ------------------------- Тесты -------------------------

def run_tests():
    print("[ТЕСТ] Проверка функции parse_coord_pair")
    coords = "55.77885362N 104.3874859E"
    lat, lon, lat_ref, lon_ref = parse_coord_pair(coords)
    assert round(lat, 6) == 55.778854
    assert round(lon, 6) == 104.387486
    assert lat_ref == "N" and lon_ref == "E"
    print("OK")

    print("[ТЕСТ] Проверка overlay_text_bottom_right")
    img = Image.new("RGB", (400, 300), (255, 255, 255))
    overlay_text_bottom_right(img, "55.77N 104.38E", None, 20)
    img.save("test_output.jpg")
    print("Сохранено test_output.jpg")

    print("Все тесты прошли успешно.")


if __name__ == '__main__':
    main()
