import os
import re
import shutil

try:
    from PyPDF2 import PdfMerger
except ImportError:
    try:
        from pypdf import PdfMerger
    except ImportError:
        raise SystemExit("Установите библиотеку: pip install PyPDF2 или pip install pypdf")

# 📂 Корневая папка
ROOT = r"C:\Users\hayda\OneDrive\Desktop\GHJ"

CODE_RE = re.compile(r'([A-ZА-Я]{2,}\d{2,})', re.UNICODE | re.IGNORECASE)
NUM_RE  = re.compile(r'(\d{4,})')

def normalize(s: str) -> str:
    return s.upper().replace("Ё", "Е")

def extract_tokens(filename: str):
    name = normalize(os.path.splitext(os.path.basename(filename))[0])
    codes = set(CODE_RE.findall(name))
    nums  = set(NUM_RE.findall(name))
    return codes, nums

# Сканируем корень
for fname in os.listdir(ROOT):
    fpath = os.path.join(ROOT, fname)
    if not fname.lower().endswith(".pdf"):
        continue  # пропускаем не PDF
    codes, nums = extract_tokens(fname)

    # делаем "чистую копию", если ещё не сделали
    base, ext = os.path.splitext(fpath)
    orig_fpath = base + "_ORIG" + ext
    if not os.path.exists(orig_fpath):
        shutil.copy2(fpath, orig_fpath)

    # ищем подпапки с совпадающим кодом
    for code in codes:
        subfolder1 = os.path.join(ROOT, code)
        subfolder2 = os.path.join(ROOT, code.lower())

        for subfolder in [subfolder1, subfolder2]:
            if not os.path.isdir(subfolder):
                continue

            # ищем PDF в подпапке
            for sf in os.listdir(subfolder):
                if not sf.lower().endswith(".pdf"):
                    continue
                sfpath = os.path.join(subfolder, sf)
                codes2, nums2 = extract_tokens(sf)

                # совпадение и по коду, и по номеру
                if codes & codes2 and nums & nums2:
                    print(f"✅ Пара найдена:\n   {orig_fpath}\n   {sfpath}")

                    merger = PdfMerger()
                    merger.append(orig_fpath)  # берём оригинал длинного
                    merger.append(sfpath)      # короткий
                    merger.write(fpath)        # сохраняем под именем длинного
                    merger.close()

                    print(f"👉 Итог сохранён: {fpath}")
                    # берём только один короткий
                    break  
            else:
                continue
            break



