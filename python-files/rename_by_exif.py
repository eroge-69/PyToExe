
import os
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
from collections import defaultdict

used = defaultdict(int)

def get_date_taken(path):
    try:
        img = Image.open(path)
        exif = img._getexif() or {}
        for t_id, val in exif.items():
            if TAGS.get(t_id) == 'DateTimeOriginal':
                return val
    except:
        return None

for f in os.listdir('.'):
    if f.lower().endswith(('.jpg', '.jpeg', '.png')):
        dt_str = get_date_taken(f)
        if not dt_str:
            print(f"⚠️ No EXIF date in {f}")
            continue
        try:
            dt = datetime.strptime(dt_str, "%Y:%m:%d %H:%M:%S")
        except ValueError:
            print(f"⚠️ Bad EXIF format in {f}")
            continue

        base = dt.strftime("IMG_%Y%m%d_%H%M%S")
        idx = used[base]
        used[base] += 1

        name = base + (f"_{idx}" if idx else "") + os.path.splitext(f)[1]
        os.rename(f, name)
        print(f"✅ {f} → {name}")
