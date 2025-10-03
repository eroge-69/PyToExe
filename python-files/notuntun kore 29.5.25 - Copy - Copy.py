# -*- coding: utf-8 -*-
import os
import re
import sys
import json
import base64
import shutil
import subprocess
import tempfile
import threading
import time
import mimetypes
import unicodedata
import queue
import html
from urllib.parse import urlparse, urljoin, unquote

import requests
import pandas as pd
from PIL import Image, EpsImagePlugin
from PIL.PngImagePlugin import PngInfo
try:
    from iptcinfo3 import IPTCInfo
    HAVE_IPTC = True
except Exception:
    HAVE_IPTC = False
import webbrowser

# OpenCV (optional, for video preview)
try:
    import cv2
    CV2_AVAILABLE = True
except Exception:
    CV2_AVAILABLE = False

# PySide6
from PySide6 import QtCore, QtGui, QtWidgets

# ---------------- Ghostscript helpers (EPS) ----------------
def find_ghostscript_binary():
    try_paths = []
    if os.name == 'nt':
        env_cand = os.environ.get("GHOSTSCRIPT_PATH") or os.environ.get("GSWIN64C") or os.environ.get("GSWIN32C")
        try_paths += [env_cand, shutil.which("gswin64c"), shutil.which("gswin32c")]
        try_paths += [
            r"C:\Program Files\gs\gs10.04.0\bin\gswin64c.exe",
            r"C:\Program Files\gs\gs10.03.1\bin\gswin64c.exe",
            r"C:\Program Files\gs\gs10.03.0\bin\gswin64c.exe",
            r"C:\Program Files\gs\gs10.02.1\bin\gswin64c.exe",
            r"C:\Program Files\gs\gs10.01.2\bin\gswin64c.exe",
            r"C:\Program Files\gs\gs9.56.1\bin\gswin64c.exe",
            r"C:\Program Files\gs\gs9.55.0\bin\gswin64c.exe",
            r"C:\Program Files (x86)\gs\gs10.03.1\bin\gswin32c.exe",
            r"C:\Program Files (x86)\gs\gs10.01.2\bin\gswin32c.exe",
        ]
    else:
        env_cand = os.environ.get("GHOSTSCRIPT_PATH")
        try_paths += [env_cand, shutil.which("gs")]

    for p in try_paths:
        if p and os.path.exists(p):
            return p
    return None

def _auto_setup_ghostscript():
    try:
        if os.name != 'nt':
            return
        if getattr(EpsImagePlugin, "gs_windows_binary", None):
            return
        gsbin = find_ghostscript_binary()
        if gsbin:
            EpsImagePlugin.gs_windows_binary = gsbin
    except Exception:
        pass

_auto_setup_ghostscript()

# -------------- Clouds scraper optional --------------
try:
    import cloudscraper
    HAVE_CLOUDSCRAPER = True
except Exception:
    HAVE_CLOUDSCRAPER = False

# -------------- Constants / Theme --------------
API_KEY_TXT = "gemini_api_key.txt"
KEYS_JSON = "gemini_keys.json"
MODEL = "gemini-2.0-flash"

PLATFORMS = ["Adobe Stock", "Shutterstock", "Dreamstime", "Vecteezy"]
VIDEO_EXTS = (".mp4", ".mov", ".avi", ".mkv", ".wmv")
SUPPORTED_EXTS = (".png", ".jpg", ".jpeg", ".eps") + VIDEO_EXTS

BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
)
BROWSER_HEADERS_HTML = {
    "User-Agent": BROWSER_UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Upgrade-Insecure-Requests": "1",
}
IMAGE_ACCEPT = "image/avif,image/webp,image/apng,image/*,*/*;q=0.8"

# -------------- Utils --------------
def resource_path(p):
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, p)

def ensure_assets_dir():
    p = resource_path("assets")
    try:
        os.makedirs(p, exist_ok=True)
    except Exception:
        pass
    return p

def image_to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def get_mime_type(filename):
    ext = filename.lower().split(".")[-1]
    if ext in ("jpg", "jpeg"):
        return "image/jpeg"
    if ext == "png":
        return "image/png"
    if ext == "eps":
        return "application/postscript"
    if ext == "mp4":
        return "video/mp4"
    if ext in ("mov", "qt"):
        return "video/quicktime"
    if ext == "avi":
        return "video/x-msvideo"
    if ext == "mkv":
        return "video/x-matroska"
    if ext == "wmv":
        return "video/x-ms-wmv"
    return "application/octet-stream"

def smart_trim_title(text: str, max_len: int) -> str:
    t = str(text or "").strip()
    if max_len <= 0:
        return ""
    if len(t) <= max_len:
        return t
    cut = t[:max_len]
    sp = cut.rfind(" ")
    if sp >= 40:
        cut = cut[:sp]
    return cut.strip(" ,.;:-–—_|")

def _normalize_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", s or " ").strip()

def sanitize_title_no_symbols(text: str, max_len: int = None) -> str:
    if not text:
        return ""
    t = unicodedata.normalize("NFKC", str(text))
    t = "".join(ch for ch in t if unicodedata.category(ch)[0] != "C")
    t = re.sub(r"[^0-9A-Za-z\u00C0-\u024F ,\.\-&/:]", " ", t)
    t = _normalize_spaces(t)
    if max_len:
        t = smart_trim_title(t, int(max_len))
    return t

def extend_title_no_symbols(title: str, kw_list, limit: int, ratio: float = 0.9) -> str:
    limit = int(limit or 120)
    ratio = float(ratio or 0.9)
    base = sanitize_title_no_symbols(title or "")
    out = base
    for kw in kw_list or []:
        k = str(kw or "").strip()
        if not k:
            continue
        if k.lower() in out.lower():
            continue
        trial = sanitize_title_no_symbols((out + " " + k).strip())
        if len(trial) <= int(limit * ratio):
            out = trial
        else:
            break
    return sanitize_title_no_symbols(out, max_len=limit)

def apply_title_prefixes(title: str, prefixes, limit: int) -> str:
    limit = int(limit or 120)
    t = sanitize_title_no_symbols(title or "")
    if not prefixes:
        return smart_trim_title(t, limit)
    wanted = []
    tl = t.lower()
    for p in prefixes:
        ps = str(p or "").strip()
        if not ps:
            continue
        if ps.lower() in tl:
            continue
        wanted.append(ps)
    if wanted:
        t = ((" ".join(wanted)) + " " + t).strip()
    return smart_trim_title(sanitize_title_no_symbols(t), limit)

def parse_word_list(s: str):
    if not s:
        return []
    parts = re.split(r"[,\n;|]+", s)
    out = []
    for p in parts:
        p = p.strip()
        if p:
            out.append(p)
    return out

# -------- Smart Clean helpers --------
STOPWORDS = {"a","an","the","and","or","of","in","to","on","for","with","by","at","from","as","is","are"}
TM_SYMBOLS_RE = re.compile(r"[™®©℠]", re.UNICODE)
TM_TEXT_RE = re.compile(r"KATEX_INLINE_OPEN(tm|r|c)KATEX_INLINE_CLOSE", re.I)

def _norm_word(w):
    return re.sub(r"[^a-z0-9]+", "", (w or "").lower())

def smart_clean_fields(title, description, keywords, cfg):
    banned = set(_norm_word(x) for x in (cfg.get("clean_banned") or []))
    mislead = set(_norm_word(x) for x in (cfg.get("clean_mislead") or []))
    ban_all = {x for x in banned.union(mislead) if x}

    def strip_tm(s):
        s = TM_SYMBOLS_RE.sub("", s or "")
        s = TM_TEXT_RE.sub("", s)
        return _normalize_spaces(s)

    title = strip_tm(title)
    description = strip_tm(description)

    if ban_all:
        def remove_words(text):
            if not text: return text
            tokens = re.split(r"(\W+)", text)
            out = []
            for t in tokens:
                if re.match(r"\w", t, re.UNICODE):
                    if _norm_word(t) in ban_all:
                        continue
                out.append(t)
            return _normalize_spaces("".join(out))
        title = remove_words(title)
        description = remove_words(description)

    if cfg.get("clean_dedupe_title", True):
        seen = set()
        words = title.split()
        new = []
        for w in words:
            nw = _norm_word(w)
            if len(nw) >= 3 and nw not in STOPWORDS:
                if nw in seen:
                    continue
                seen.add(nw)
            new.append(w)
        title = _normalize_spaces(" ".join(new))

    kw_list = [k.strip() for k in (keywords or "").split(",") if k.strip()]
    out_kw = []
    seen_kw = set()
    for k in kw_list:
        k0 = strip_tm(k)
        nk = _norm_word(k0)
        if not nk:
            continue
        if nk in ban_all:
            continue
        if cfg.get("clean_dedupe_kw", True):
            if nk in seen_kw:
                continue
            seen_kw.add(nk)
        out_kw.append(k0)
    limit = int(cfg.get("keywords_count", 50) or 50)
    out_kw = out_kw[:limit]
    keywords = ", ".join(out_kw)

    tlimit = int(cfg.get("title_len", 120) or 120)
    title = sanitize_title_no_symbols(title, max_len=tlimit)
    description = _normalize_spaces(description)
    return title, description, keywords

# -------------- ExifTool helpers --------------
def _run_exiftool_no_backup(cmd_list, timeout=40):
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    p = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout, creationflags=flags)
    return p.returncode == 0

def find_exiftool():
    candidates = []
    env = os.environ.get("EXIFTOOL_PATH")
    if env:
        candidates.append(env)
    if os.name == 'nt':
        candidates.extend([
            shutil.which("exiftool.exe"),
            shutil.which("exiftool(-k).exe"),
            r"C:\Program Files\ExifTool\exiftool.exe",
            r"C:\Program Files\ExifTool\exiftool(-k).exe",
            r"C:\Windows\exiftool.exe",
            r"C:\Windows\exiftool(-k).exe",
        ])
    else:
        candidates.append(shutil.which("exiftool"))
        candidates.append("/usr/bin/exiftool")
        candidates.append("/usr/local/bin/exiftool")
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None

def _xml_escape(s: str) -> str:
    return html.escape(s or "", quote=True)

def build_xmp_packet(title: str, description: str, keywords_list):
    kws_xml = "".join(f"<rdf:li>{_xml_escape(k)}</rdf:li>" for k in (keywords_list or []))
    return f"""<?xpacket begin='﻿' id='W5M0MpCehiHzreSzNTczkc9d'?>
<x:xmpmeta xmlns:x='adobe:ns:meta/'>
 <rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'>
  <rdf:Description xmlns:dc='http://purl.org/dc/elements/1.1/'>
   <dc:title><rdf:Alt><rdf:li xml:lang='x-default'>{_xml_escape(title)}</rdf:li></rdf:Alt></dc:title>
   <dc:description><rdf:Alt><rdf:li xml:lang='x-default'>{_xml_escape(description)}</rdf:li></rdf:Alt></dc:description>
   <dc:subject><rdf:Bag>{kws_xml}</rdf:Bag></dc:subject>
  </rdf:Description>
 </rdf:RDF>
</x:xmpmeta>
<?xpacket end='w'?>"""

# ------------------ EMBED HELPERS (updated) ------------------
def embed_metadata_eps_exiftool(path, title, description, keywords):
    exiftool = find_exiftool()
    if not exiftool:
        return False
    kw_list = [k.strip() for k in (keywords or "").split(",") if k.strip()]
    try:
        subj = ", ".join(kw_list)
        base_cmd = [
            exiftool, "-P", "-m", "-charset", "filename=UTF8", "-sep", ", ",
            f"-XMP-dc:Title={title}",
            f"-XMP-dc:Description={description}",
            f"-XMP-dc:Subject={subj}",
            "-overwrite_original",
            path
        ]
        return _run_exiftool_no_backup(base_cmd, timeout=40)
    except Exception as e:
        print("ExifTool EPS embed error:", e)
        return False

def _embed_xmp_into_eps(path, xmp_xml):
    def _xml_to_ascii_entities(s: str) -> str:
        out = []
        for ch in s:
            code = ord(ch)
            if code < 128:
                out.append(ch)
            else:
                out.append(f"&#x{code:X};")
        return "".join(out)

    try:
        with open(path, "rb") as f:
            data = f.read()

        if b"\r\n" in data:
            nl = b"\r\n"
        elif b"\r" in data and b"\n" not in data:
            nl = b"\r"
        else:
            nl = b"\n"

        xmp_ascii = _xml_to_ascii_entities(xmp_xml).encode("ascii")
        block = b"%%BeginResource: XMP" + nl + xmp_ascii + nl + b"%%EndResource" + nl

        m = re.search(br"%%BeginResource:\s*XMP.*?%%EndResource\s*(?:\r?\n)?", data, flags=re.S)
        if m:
            new_data = data[:m.start()] + block + data[m.end():]
        else:
            endc = re.search(br"^%%EndComments\s*$", data, flags=re.M)
            if endc:
                pos = endc.start()
                new_data = data[:pos] + block + data[pos:]
            else:
                header = re.search(br"^%![^\r\n]*\r?\n", data, flags=re.M)
                if header:
                    pos = header.end()
                    new_data = data[:pos] + block + data[pos:]
                else:
                    new_data = block + data

        fd, tmp = tempfile.mkstemp(suffix=".eps", prefix="mm_eps_")
        os.close(fd)
        with open(tmp, "wb") as f:
            f.write(new_data)
        os.replace(tmp, path)
        return True
    except Exception as e:
        print("EPS XMP inline embed (bytes-safe) failed:", e)
        try:
            if 'tmp' in locals() and os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass
        return False

def embed_metadata_eps(path, title, description, keywords):
    if embed_metadata_eps_exiftool(path, title, description, keywords):
        return True
    kw_list = [k.strip() for k in (keywords or "").split(",") if k.strip()]
    xmp_data = build_xmp_packet(title, description, kw_list)
    try:
        sidecar = path + ".xmp"
        with open(sidecar, "w", encoding="utf-8") as f:
            f.write(xmp_data)
        return True
    except Exception as e:
        print("EPS sidecar write failed:", e)
    if os.environ.get("EPS_INLINE", "").strip().lower() in ("1", "true", "yes", "inline"):
        ok = _embed_xmp_into_eps(path, xmp_data)
        if ok:
            return True
        print("EPS inline embed failed.")
    return False

def embed_metadata_jpeg(path, title, description, keywords):
    """
    Prefer ExifTool: write full-length XMP (dc:title/description/subject) +
    Photoshop:Headline (<=64) + IPTC Caption/Keywords.
    Fallback to iptcinfo3 if exiftool missing.
    """
    exiftool = find_exiftool()
    if exiftool:
        try:
            kw_list = [k.strip() for k in (keywords or "").split(",") if k.strip()]
            subj = ", ".join(kw_list)
            headline64 = (title or "")[:64]
            cmd = [
                exiftool, "-P", "-m", "-charset", "filename=UTF8", "-sep", ", ",
                f"-XMP-dc:Title={title}",
                f"-XMP-dc:Description={description}",
                f"-XMP-dc:Subject={subj}",
                f"-Photoshop:Headline={headline64}",
                f"-IPTC:Caption-Abstract={description}",
                f"-IPTC:Keywords={subj}",
                "-overwrite_original",
                path
            ]
            if _run_exiftool_no_backup(cmd, timeout=40):
                return True
            else:
                print("ExifTool JPEG write failed, trying IPTC fallback…")
        except Exception as e:
            print(f"ExifTool JPEG error: {e} -> IPTC fallback")
    # Fallback to IPTC only (limited headline length in some viewers)
    if not HAVE_IPTC:
        return False
    try:
        info = IPTCInfo(path, force=True)
        info["object name"] = (title or "")[:64]  # many viewers show this; limit 64
        info["caption/abstract"] = description or ""
        info["keywords"] = [k.strip() for k in (keywords or "").split(",") if k.strip()]
        info.save()
        return True
    except Exception as e:
        print(f"JPEG IPTC embed error: {e}")
        return False

def embed_metadata_png(path, title, description, keywords):
    exiftool = find_exiftool()
    kw_list = [k.strip() for k in (keywords or "").split(",") if k.strip()]
    if exiftool:
        try:
            subj = ", ".join(kw_list)
            base_cmd = [
                exiftool, "-P", "-m", "-charset", "filename=UTF8", "-sep", ", ",
                f"-XMP-dc:Title={title}",
                f"-XMP-dc:Description={description}",
                f"-XMP-dc:Subject={subj}",
                "-PNG:Title=" + (title or ""),
                "-PNG:Description=" + (description or ""),
                "-PNG:Keywords=" + (keywords or ""),
                "-PNG:Software=MetaMaker",
                "-overwrite_original",
                path
            ]
            if _run_exiftool_no_backup(base_cmd, timeout=40):
                return True
            else:
                print("ExifTool PNG failed. Using Pillow fallback.")
        except Exception as e:
            print(f"ExifTool PNG error: {e} -> Pillow fallback")
    try:
        xmp_data = build_xmp_packet(title, description, kw_list)
        with Image.open(path) as im:
            info = im.info or {}
            pnginfo = PngInfo()
            pnginfo.add_text("Title", title or "")
            pnginfo.add_text("Description", description or "")
            pnginfo.add_text("Keywords", keywords or "")
            pnginfo.add_text("Software", "MetaMaker")
            pnginfo.add_text("XML:com.adobe.xmp", xmp_data)
            save_kwargs = {"pnginfo": pnginfo}
            if "icc_profile" in info:
                save_kwargs["icc_profile"] = info["icc_profile"]
            fd, tmp_path = tempfile.mkstemp(suffix=".png", prefix="mm_")
            os.close(fd)
            im.save(tmp_path, "PNG", **save_kwargs)
            os.replace(tmp_path, path)
        return True
    except Exception as e:
        print(f"Pillow PNG embed error: {e}")
        try:
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
        return False

def embed_metadata_video(path, title, description, keywords):
    exiftool = find_exiftool()
    if not exiftool:
        print("Video embed skipped (ExifTool not available).")
        return False
    kw_list = [k.strip() for k in (keywords or "").split(",") if k.strip()]
    try:
        subj = ", ".join(kw_list)
        base_cmd = [
            exiftool, "-P", "-m", "-charset", "filename=UTF8", "-sep", ", ",
            f"-XMP-dc:Title={title}",
            f"-XMP-dc:Description={description}",
            f"-XMP-dc:Subject={subj}",
            f"-QuickTime:Title={title}",
            f"-QuickTime:Comment={description}",
            "-overwrite_original",
            path
        ]
        if _run_exiftool_no_backup(base_cmd, timeout=60):
            return True
    except Exception as e:
        print("Video embed error:", e)
    print("Video embed failed (no sidecar created).")
    return False

def embed_metadata_universal(path, title, description, keywords):
    ext = os.path.splitext(path)[1].lower()
    if ext in (".jpg", ".jpeg"):
        return embed_metadata_jpeg(path, title, description, keywords)
    if ext == ".png":
        return embed_metadata_png(path, title, description, keywords)
    if ext == ".eps":
        return embed_metadata_eps(path, title, description, keywords)
    if ext in VIDEO_EXTS:
        return embed_metadata_video(path, title, description, keywords)
    return False

def eps_to_temp_jpeg(path, dpi=300):
    last_err = None
    try:
        fd, tmp = tempfile.mkstemp(suffix=".jpg", prefix="mmx_eps_")
        os.close(fd)
        with Image.open(path) as im:
            im.load(scale=1)
            im.convert("RGB").save(tmp, "JPEG", quality=95, dpi=(dpi, dpi))
        return tmp
    except Exception as e:
        last_err = e

    gsbin = find_ghostscript_binary()
    if not gsbin:
        raise RuntimeError(
            f"Ghostscript not found. Install from https://ghostscript.com or set GHOSTSCRIPT_PATH. "
            f"Original error: {last_err}"
        )
    fd, tmp = tempfile.mkstemp(suffix=".jpg", prefix="mmx_eps_")
    os.close(fd)
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    cmd = [
        gsbin,
        "-dSAFER", "-dBATCH", "-dNOPAUSE",
        "-dEPSCrop",
        f"-r{int(dpi)}",
        "-sDEVICE=jpeg",
        "-dJPEGQ=95",
        "-dUseFastColor=true",
        f"-sOutputFile={tmp}",
        path
    ]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=flags)
    if r.returncode != 0 or not os.path.exists(tmp) or os.path.getsize(tmp) == 0:
        try:
            if os.path.exists(tmp): os.remove(tmp)
        except Exception:
            pass
        tail = "\n".join((r.stderr or r.stdout or "").splitlines()[-12:])
        raise RuntimeError("Ghostscript conversion failed.\n" + tail)
    return tmp

def _ffmpeg_available():
    return shutil.which("ffmpeg") is not None

def video_to_temp_jpeg(path, time_s=0.5):
    if CV2_AVAILABLE:
        cap = cv2.VideoCapture(path)
        if not cap or not cap.isOpened():
            raise RuntimeError("Cannot open video for preview.")
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        total = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 1
        target_frame = int(min(total - 1, max(0, time_s * fps)))
        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        ok, frame = cap.read()
        if not ok:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ok, frame = cap.read()
        cap.release()
        if not ok or frame is None:
            raise RuntimeError("Failed to grab a video frame.")
        fd, tmp = tempfile.mkstemp(suffix=".jpg", prefix="mmx_vid_")
        os.close(fd)
        ok = cv2.imwrite(tmp, frame)
        if not ok:
            raise RuntimeError("Failed to write temp jpeg from video.")
        return tmp
    elif _ffmpeg_available():
        fd, tmp = tempfile.mkstemp(suffix=".jpg", prefix="mmx_vid_")
        os.close(fd)
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        cmd = ["ffmpeg", "-y", "-ss", str(time_s), "-i", path, "-frames:v", "1", "-q:v", "2", "-vf", "scale='min(1280,iw)':-2", tmp]
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=flags)
        if r.returncode == 0 and os.path.exists(tmp) and os.path.getsize(tmp) > 0:
            return tmp
        raise RuntimeError("FFmpeg failed to extract frame.")
    else:
        raise RuntimeError("Video preview requires OpenCV or FFmpeg.")

# -------------- URL helpers and scraping --------------
def is_url(s):
    return isinstance(s, str) and re.match(r"^(https?|ftp)://", s.strip(), re.I)

def normalize_input_url(u: str) -> str:
    s = (u or "").strip()
    if not s:
        return s
    if is_url(s):
        return s
    if re.match(r'^[a-z0-9\-\._]+\.[a-z]{2,}(?:/.*)?$', s, re.I):
        return "https://" + s
    return s

ASSET_REF_MAP = {
    "stock.adobe.com": "https://stock.adobe.com/",
    "ftcdn.net": "https://stock.adobe.com/",
    "shutterstock.com": "https://www.shutterstock.com/",
    "image.shutterstock.com": "https://www.shutterstock.com/",
    "istockphoto.com": "https://www.istockphoto.com/",
    "gettyimages.com": "https://www.gettyimages.com/",
    "dreamstime.com": "https://www.dreamstime.com/",
    "depositphotos.com": "https://depositphotos.com/",
    "123rf.com": "https://www.123rf.com/",
    "alamy.com": "https://www.alamy.com/",
    "stocksy.com": "https://www.stocksy.com/",
    "bigstockphoto.com": "https://www.bigstockphoto.com/",
    "bigstock.com": "https://www.bigstockphoto.com/",
    "pond5.com": "https://www.pond5.com/",
    "elements.envato.com": "https://elements.envato.com/",
    "envato.com": "https://envato.com/",
    "freepik.com": "https://www.freepik.com/",
    "m.freepik.com": "https://www.freepik.com/",
    "img.freepik.com": "https://www.freepik.com/",
    "vecteezy.com": "https://www.vecteezy.com/",
    "static.vecteezy.com": "https://www.vecteezy.com/",
    "unsplash.com": "https://unsplash.com/",
    "images.unsplash.com": "https://unsplash.com/",
    "pexels.com": "https://www.pexels.com/",
    "images.pexels.com": "https://www.pexels.com/",
    "pixabay.com": "https://pixabay.com/",
    "rawpixel.com": "https://www.rawpixel.com/",
}

def _preferred_referer(asset_url, fallback):
    host = urlparse(asset_url).netloc.lower()
    for key, ref in ASSET_REF_MAP.items():
        if key in host:
            return ref
    return fallback

def _make_session():
    if HAVE_CLOUDSCRAPER:
        s = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "windows", "mobile": False})
    else:
        s = requests.Session()
    s.headers.update(BROWSER_HEADERS_HTML.copy())
    return s

def _fetch_via_jina(url):
    if url.startswith("https://"):
        prox = "https://r.jina.ai/http://" + url[len("https://"):]
    elif url.startswith("http://"):
        prox = "https://r.jina.ai/http://" + url[len("http://"):]
    else:
        prox = "https://r.jina.ai/http://" + url
    r = requests.get(prox, headers={"User-Agent": BROWSER_UA, "Accept": "text/plain; charset=utf-8"}, timeout=40)
    r.raise_for_status()
    return r.text, url

def fetch_page_html_anyhow(url):
    s = _make_session()
    try:
        r = s.get(url, allow_redirects=True, timeout=40)
        if r.status_code in (403, 429, 503):
            root = f"{urlparse(url).scheme}://{urlparse(url).netloc}/"
            r = s.get(url, headers={"Referer": root, **BROWSER_HEADERS_HTML}, allow_redirects=True, timeout=40)
        r.raise_for_status()
        return r.text, r.url
    except Exception:
        return _fetch_via_jina(url)

_IMG_EXTS = (".jpg",".jpeg",".png",".gif",".webp",".bmp",".tif",".tiff")
_VID_EXTS = (".mp4",".webm",".mov",".mkv")

def _looks_like_media_url(u: str) -> bool:
    p = urlparse(u).path.lower()
    return any(p.endswith(e) for e in (_IMG_EXTS + _VID_EXTS))

def _choose_best_from_srcset(srcset_value):
    parts = [p.strip() for p in (srcset_value or "").split(",") if p.strip()]
    best = None
    best_w = -1
    for p in parts:
        urlp = p.split()[0]
        m = re.search(r'(\d+)\s*w', p)
        w = int(m.group(1)) if m else 0
        if w >= best_w:
            best_w = w
            best = urlp
    return best or (parts[-1].split()[0] if parts else "")

def _add_candidate(cands, base_url, u):
    if not u:
        return
    u = u.strip().strip('"').strip("'")
    if not u:
        return
    if u.startswith("//"):
        u = "https:" + u
    if not (u.startswith("http://") or u.startswith("https://")):
        u = urljoin(base_url, u)
    if u not in cands:
        cands.append(u)

def _extract_asset_candidates_from_html(html, base_url):
    cands = []
    for m in re.findall(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.I):
        _add_candidate(cands, base_url, m)
    for m in re.findall(r'<meta[^>]+name=["\']twitter:image(?::src)?["\'][^>]+content=["\']([^"\']+)["\']', html, re.I):
        _add_candidate(cands, base_url, m)
    for m in re.findall(r'<link[^>]+rel=["\']image_src["\'][^>]+href=["\']([^"\']+)["\']', html, re.I):
        _add_candidate(cands, base_url, m)
    for block in re.findall(r'<script[^>]*>(.*?)</script>', html, re.I | re.S):
        for u in re.findall(r'"(?:contentUrl|thumbnailUrl|image|imageUrl|imageURL|image_url|url|src)"\s*:\s*"([^"]+)"', block, re.I):
            if "http" in u or u.startswith("//") or u.startswith("/"):
                _add_candidate(cands, base_url, u)
    img_attrs = [
        "src","data-src","data-lazy","data-lazy-src","data-original","data-original-src","data-zoom-src",
        "data-zoom-image","data-large_image","data-image","data-full","data-full-src","data-url",
        "data-thumb","data-thumbnail","data-preview","data-desktop-src","data-src-large","data-main-image"
    ]
    for attr in img_attrs:
        for m in re.findall(fr'<img[^>]+{attr}=["\']([^"\']+)["\']', html, re.I):
            _add_candidate(cands, base_url, m)
    for m in re.findall(r'<img[^>]+srcset=["\']([^"\']+)["\']', html, re.I):
        _add_candidate(cands, base_url, _choose_best_from_srcset(m))
    for m in re.findall(r'<amp-img[^>]+src=["\']([^"\']+)["\']', html, re.I):
        _add_candidate(cands, base_url, m)
    for m in re.findall(r'<amp-img[^>]+srcset=["\']([^"\']+)["\']', html, re.I):
        _add_candidate(cands, base_url, _choose_best_from_srcset(m))
    for m in re.findall(r'<source[^>]+srcset=["\']([^"\']+)["\']', html, re.I):
        _add_candidate(cands, base_url, _choose_best_from_srcset(m))
    for m in re.findall(r'<source[^>]+src=["\']([^"\']+)["\']', html, re.I):
        _add_candidate(cands, base_url, m)
    for m in re.findall(r'<video[^>]+poster=["\']([^"\']+)["\']', html, re.I):
        _add_candidate(cands, base_url, m)
    # CSS background-image url(...)
    for _, u in re.findall(r'background(?:-image)?\s*:\s*urlKATEX_INLINE_OPEN(["\']?)(?!data:)([^)\'"]+)\1KATEX_INLINE_CLOSE', html, re.I):
        _add_candidate(cands, base_url, u)
    for m in re.findall(r'https?://[^\s\'"]+\.(?:jpg|jpeg|png|gif|webp|bmp|tif|tiff|mp4|webm|mov|mkv)(?:\?[^\s\'"]*)?', html, re.I):
        _add_candidate(cands, base_url, m)

    filtered = []
    seen = set()
    for u in cands:
        if not _looks_like_media_url(u):
            if not (re.search(r'([?&](format|ext)=|/images?/|/thumbs?/|/thumbnails?/|/photo/|/image/)', u, re.I)):
                continue
        if u not in seen:
            seen.add(u)
            filtered.append(u)
    return filtered

def extract_assets_from_page(page_url, max_count=120):
    html, final_url = fetch_page_html_anyhow(page_url)
    base_url = final_url
    cands = _extract_asset_candidates_from_html(html, base_url)
    if not cands:
        return []
    out = []
    s = _make_session()
    headers = {"User-Agent": BROWSER_UA, "Accept": IMAGE_ACCEPT, "Accept-Language": "en-US,en;q=0.9"}
    for cu in cands:
        try:
            gr = s.get(cu, headers=headers, stream=True, timeout=25)
            ctype = gr.headers.get("Content-Type", "")
            code = gr.status_code
            gr.close()
            if code == 200 and (ctype.startswith("image/") or ctype.startswith("video/") or _looks_like_media_url(cu)):
                out.append((cu, base_url))
        except Exception:
            continue
        if len(out) >= max_count:
            break
    return out

def _guess_ext_from(url, content_type):
    ctype = (content_type or "").split(";")[0].strip().lower()
    ext = mimetypes.guess_extension(ctype) if ctype else None
    if not ext:
        path = urlparse(url).path
        _, ext = os.path.splitext(path)
    ext = (ext or "").lower()
    if ext in (".jpeg", ".jpe"):
        ext = ".jpg"
    if not ext:
        if ctype in ("image/jpeg", "image/jpg"):
            ext = ".jpg"
        elif ctype == "image/png":
            ext = ".png"
        elif ctype == "image/webp":
            ext = ".webp"
        elif ctype == "video/mp4":
            ext = ".mp4"
        else:
            ext = ".jpg"
    return ext

def _normalize_downloaded_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in SUPPORTED_EXTS:
        return path
    try:
        with Image.open(path) as im:
            new = os.path.splitext(path)[0] + ".png"
            im.save(new, "PNG")
        os.remove(path)
        return new
    except Exception:
        return path

def _is_media_ctype(ct):
    ct = (ct or "").split(";")[0].lower().strip()
    return ct.startswith("image/") or ct.startswith("video/")

def download_direct_with_referer(asset_url, referer, out_dir=None):
    out_dir = out_dir or os.path.join(ensure_assets_dir(), "downloads")
    os.makedirs(out_dir, exist_ok=True)
    s = _make_session()
    real_ref = _preferred_referer(asset_url, referer or asset_url)
    headers = {"User-Agent": BROWSER_UA, "Accept": IMAGE_ACCEPT, "Accept-Language": "en-US,en;q=0.9", "Referer": real_ref}
    r = s.get(asset_url, headers=headers, stream=True, timeout=50)
    if r.status_code in (403, 429, 503):
        try:
            if not HAVE_CLOUDSCRAPER:
                domain = urlparse(real_ref).netloc or urlparse(asset_url).netloc
                headers["Referer"] = f"https://{domain}/"
                r = s.get(asset_url, headers=headers, stream=True, timeout=50)
            else:
                sc = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "windows", "mobile": False})
                r = sc.get(asset_url, headers=headers, stream=True, timeout=50)
        except Exception:
            pass
    r.raise_for_status()
    ctype_final = r.headers.get("Content-Type", "")
    if not _is_media_ctype(ctype_final) and not _looks_like_media_url(asset_url):
        raise RuntimeError("URL is not a direct image/video.")
    ext = _guess_ext_from(asset_url, ctype_final)
    name = os.path.basename(urlparse(asset_url).path) or "image"
    name = re.sub(r"[^A-Za-z0-9_\-\.]+", "-", unquote(name)).strip("-") or "image"
    stem = os.path.splitext(name)[0]
    dest = os.path.join(out_dir, stem + ext)
    k = 1
    while os.path.exists(dest):
        dest = os.path.join(out_dir, f"{stem}_{k}{ext}")
        k += 1
    size = 0
    with open(dest, "wb") as f:
        for chunk in r.iter_content(8192):
            if chunk:
                f.write(chunk)
                size += len(chunk)
    if size == 0:
        raise RuntimeError("Downloaded zero bytes")
    return _normalize_downloaded_file(dest)

def download_url_as_file(url, out_dir=None):
    out_dir = out_dir or os.path.join(ensure_assets_dir(), "downloads")
    os.makedirs(out_dir, exist_ok=True)
    s = _make_session()
    gr = s.get(url, stream=True, timeout=50)
    if gr.status_code in (403, 429, 503):
      domain = urlparse(url).netloc
      gr = s.get(url, headers={"Referer": f"https://{domain}/", "User-Agent": BROWSER_UA, "Accept": IMAGE_ACCEPT}, stream=True, timeout=50)
    gr.raise_for_status()
    ctype = gr.headers.get("Content-Type", "")
    if not _is_media_ctype(ctype):
        raise RuntimeError("URL is not an image/video")
    ext = _guess_ext_from(url, ctype)
    name = os.path.basename(urlparse(url).path) or "image"
    name = re.sub(r"[^A-Za-z0-9_\-\.]+", "-", unquote(name)).strip("-") or "image"
    stem = os.path.splitext(name)[0]
    dest = os.path.join(out_dir, stem + ext)
    k = 1
    while os.path.exists(dest):
        dest = os.path.join(out_dir, f"{stem}_{k}{ext}")
        k += 1
    size = 0
    with open(dest, "wb") as f:
        for chunk in gr.iter_content(8192):
            if chunk:
                f.write(chunk)
                size += len(chunk)
    if size == 0:
        raise RuntimeError("Downloaded zero bytes")
    return _normalize_downloaded_file(dest)

def download_one_from_url_or_page(url):
    try:
        if _looks_like_media_url(url):
            return download_direct_with_referer(url, referer=url)
        s = _make_session()
        r = s.get(url, stream=True, timeout=25)
        ct = r.headers.get("Content-Type", "")
        r.close()
        if _is_media_ctype(ct):
            return download_direct_with_referer(url, referer=url)
        assets = extract_assets_from_page(url, max_count=20)
        if not assets:
            raise RuntimeError("Could not find image on that page.")
        au, ref = assets[0]
        return download_direct_with_referer(au, ref)
    except Exception as e:
        raise

# -------------- Robust Gemini API (fast JSON, session keep-alive) --------------
class ApiClient:
    def __init__(self, label, key):
        self.label = label
        self.key = key
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": BROWSER_UA,
            "Accept": "application/json",
            "Content-Type": "application/json"
        })

class KeyCycler:
    def __init__(self, clients):
        self.clients = list(clients or [])
        self._i = 0
        self._lock = threading.Lock()
    def next(self):
        with self._lock:
            if not self.clients:
                raise RuntimeError("No API clients available")
            c = self.clients[self._i % len(self.clients)]
            self._i += 1
            return c

def _post_gemini_session(session, url, payload, attempts=5):
    delay = 0.8
    last = None
    for _ in range(attempts):
        try:
            r = session.post(url, data=json.dumps(payload), timeout=60)
            if r.status_code in (429, 500, 503):
                last = f"{r.status_code}: {r.text[:200]}"
                time.sleep(delay)
                delay = min(delay * 1.7, 8)
                continue
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            last = str(e)
            time.sleep(delay)
            delay = min(delay * 1.7, 8)
    raise RuntimeError(last or "Gemini request failed")

def call_gemini_meta_fast(client: ApiClient, b64_data, mime, cfg):
    # Compact JSON output for speed
    kw_limit = int(cfg.get("keywords_count", 30))
    title_limit = int(cfg.get("title_len", 120))
    platform = cfg.get("platform", "Adobe Stock")
    prompt_text = (
        f"You create stock metadata for {platform}. "
        f"Return compact JSON only with keys: "
        f'{{"title":"<max {title_limit} chars, no brands/emojis>",'
        f'"description":"<clean factual one or two sentences>",'
        f'"keywords":["k1","k2", "..."]}}. '
        f"Up to {kw_limit} keywords, no duplicates, no hashtags, English only."
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={client.key}"
    payload = {
        "contents": [{
            "role": "user",
            "parts": [
                {"text": prompt_text},
                {"inline_data": {"mime_type": mime, "data": b64_data}}
            ]
        }],
        "generationConfig": {"temperature": 0.3, "topP": 0.9, "topK": 32, "maxOutputTokens": 300}
    }
    data = _post_gemini_session(client.session, url, payload, attempts=5)
    cands = data.get("candidates", [])
    if not cands:
        raise RuntimeError("Empty response from model.")
    parts = cands[0].get("content", {}).get("parts", [])
    text_out = "".join(p.get("text", "") for p in parts if "text" in p).strip()
    if not text_out:
        raise RuntimeError("Model returned no text.")
    # Parse JSON robustly
    try:
        meta = json.loads(text_out)
    except Exception:
        m = re.search(r"\{.*\}", text_out, re.DOTALL)
        if not m:
            raise RuntimeError("Could not parse metadata JSON.")
        meta = json.loads(m.group(0))
    title = str(meta.get("title", "") or "")
    description = str(meta.get("description", "") or "")
    kws = meta.get("keywords", [])
    if isinstance(kws, list):
        keywords = ", ".join([str(x).strip() for x in kws if str(x).strip()])
    else:
        keywords = str(kws or "")
    return title, description, keywords

def call_quality_api(client: ApiClient, b64_data, mime, cfg):
    prompt_text = (
        "You are a strict stock image quality reviewer. Return JSON ONLY.\n"
        "- Reject if: brand names/logos/trademarks/watermarks present; faces or identifiable people without release; "
        "license plates/QR/barcodes; explicit/violent/illegal content; offensive/obscene text; "
        "obvious AI artifacts/anatomy errors; very low resolution, heavy noise/compression, severe motion blur.\n"
        'JSON: {"decision":"PASS|REJECT","score":0..1,"flags":[{"category":"logo|brand|watermark|face|anatomy|text|copyright|nudity|violence|lowres|noise|blur|other","severity":"low|medium|high|critical","message":"short"}],"notes":"short"}'
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={client.key}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt_text}, {"inline_data": {"mime_type": mime, "data": b64_data}}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 320},
    }
    data = _post_gemini_session(client.session, url, payload, attempts=5)
    cands = data.get("candidates", [])
    if not cands:
        raise RuntimeError("Empty response from model.")
    parts = cands[0].get("content", {}).get("parts", [])
    text_out = "".join(p.get("text", "") for p in parts if "text" in p).strip()
    if not text_out:
        raise RuntimeError("Model returned no text.")
    try:
        result = json.loads(text_out)
    except Exception:
        m = re.search(r"\{.*\}", text_out, re.DOTALL)
        if not m:
            raise RuntimeError("Could not parse quality JSON.")
        result = json.loads(m.group(0))
    decision = str(result.get("decision", "REJECT") or "REJECT").upper()
    if decision not in ("PASS", "REJECT"):
        decision = "REJECT"
    score = float(result.get("score", 0.0) or 0.0)
    flags = result.get("flags", [])
    notes = result.get("notes", "")
    flag_texts = []
    if isinstance(flags, list):
        for fl in flags[:10]:
            if isinstance(fl, dict):
                cat = fl.get("category", "")
                sev = fl.get("severity", "")
                msg = fl.get("message", "")
                parts2 = []
                if cat: parts2.append(str(cat))
                if sev: parts2.append(str(sev))
                if msg: parts2.append(str(msg))
                if parts2:
                    flag_texts.append(" | ".join(parts2))
            else:
                flag_texts.append(str(fl))
    flags_joined = "; ".join(flag_texts)
    return {"decision": decision, "score": max(0.0, min(1.0, score)), "flags": flags_joined, "notes": notes}

# -------------- File URI helpers --------------
def is_file_uri(s):
    return isinstance(s, str) and s.strip().lower().startswith("file://")

def file_uri_to_path(uri):
    try:
        parsed = urlparse(uri)
        if parsed.scheme != "file":
            return None
        path = unquote(parsed.path)
        if os.name == "nt" and re.match(r"^/[A-Za-z]:", path):
            path = path[1:]
        return os.path.normpath(path)
    except Exception:
        return None

# -------------- Qt UI: Drop area --------------
class DropArea(QtWidgets.QFrame):
    dropped = QtCore.Signal(list)
    clicked = QtCore.Signal()
    def __init__(self, parent=None, height=170):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMinimumHeight(height)
        self.setProperty("hover", False)
        self.setStyleSheet("""
            QFrame {
                background-color: #111827;
                border: 2px dashed #2A3854;
                border-radius: 12px;
            }
            QFrame[hover="true"] {
                border-color: #60A5FA;
                background-color: #0F172A;
            }
            QLabel { color: #DCE7F4; }
        """)
        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(6)
        self.lbl1 = QtWidgets.QLabel("🗂️ Drop files, folders, or URLs")
        f = self.lbl1.font(); f.setPointSize(10); f.setBold(True); self.lbl1.setFont(f)
        self.lbl1.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl2 = QtWidgets.QLabel("…or click to browse")
        self.lbl2.setStyleSheet("color:#8EA1B2;")
        self.lbl2.setAlignment(QtCore.Qt.AlignCenter)
        lay.addWidget(self.lbl1); lay.addWidget(self.lbl2)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            self.setProperty("hover", True)
            self.style().unpolish(self); self.style().polish(self); self.update()
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.setProperty("hover", False)
        self.style().unpolish(self); self.style().polish(self); self.update()

    def dropEvent(self, event):
        self.setProperty("hover", False)
        self.style().unpolish(self); self.style().polish(self); self.update()
        paths = []
        if event.mimeData().hasUrls():
            for u in event.mimeData().urls():
                if u.isLocalFile():
                    paths.append(u.toLocalFile())
                else:
                    paths.append(u.toString())
        elif event.mimeData().hasText():
            txt = event.mimeData().text()
            for ln in txt.splitlines():
                s = ln.strip()
                if s:
                    paths.append(s)
        self.dropped.emit(paths)

class SectionCard(QtWidgets.QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame { background-color: #0F1626; border: 1px solid #1E2A44; border-radius: 12px; }
            QLabel[role="header"] { background-color: #0F1C33; color: #E6EEF8; padding:10px 12px; border-top-left-radius:12px; border-top-right-radius:12px; }
        """)
        self.v = QtWidgets.QVBoxLayout(self)
        self.v.setContentsMargins(0,0,0,0)
        header = QtWidgets.QLabel(title)
        header.setProperty("role", "header")
        self.v.addWidget(header)
        self.body = QtWidgets.QWidget()
        self.body.setStyleSheet("QWidget{background-color:#0F1626;}")
        self.v.addWidget(self.body)
        self.body_layout = QtWidgets.QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(12, 10, 12, 12)
        self.body_layout.setSpacing(8)

class LabeledSlider(QtWidgets.QWidget):
    valueChanged = QtCore.Signal(int)
    def __init__(self, title, minv, maxv, val):
        super().__init__()
        v = QtWidgets.QVBoxLayout(self); v.setContentsMargins(0,0,0,0); v.setSpacing(4)
        self.lbl = QtWidgets.QLabel(f"{title}: {val}")
        self.lbl.setStyleSheet("color:#CAD4DE;")
        self.sld = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.sld.setRange(minv, maxv); self.sld.setValue(val)
        self.sld.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #1E2A44;
                height: 8px; margin: 0px 8px; border-radius: 4px;
                background: #172035;
            }
            QSlider::sub-page:horizontal {
                height: 8px; border-radius: 4px; border: 1px solid #1E2A44;
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #20E3B2, stop:1 #3B82F6);
            }
            QSlider::add-page:horizontal { height: 8px; border-radius: 4px; background: transparent; }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #22D3EE, stop:1 #3B82F6);
                border: 1px solid #2E4F7A; width: 14px; height: 14px; margin: -5px 0; border-radius: 7px;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #38F0C2, stop:1 #4C8DFF);
            }
        """)
        v.addWidget(self.lbl); v.addWidget(self.sld)
        self.sld.valueChanged.connect(self._on_change)
        self.title = title
    def _on_change(self, x):
        self.lbl.setText(f"{self.title}: {x}")
        self.valueChanged.emit(int(x))
    def value(self):
        return int(self.sld.value())
    def setValue(self, x):
        self.sld.setValue(int(x))

# -------------- Parallel File Worker (auto key rotation per request) --------------
class FileWorker(QtCore.QObject):
    sig_status = QtCore.Signal(str)
    sig_preview = QtCore.Signal(str, str, str)  # image_path, key_label, filename
    sig_update_row = QtCore.Signal(str, dict)
    sig_rename = QtCore.Signal(str, str, str)
    sig_file_done = QtCore.Signal(str)

    def __init__(self, worker_id, key_cycler: KeyCycler, task_queue, cfg, pause_event, cancel_event):
        super().__init__()
        self.worker_id = worker_id
        self.key_cycler = key_cycler
        self.q = task_queue
        self.cfg = cfg
        self.pause_event = pause_event
        self.cancel_event = cancel_event

    def run(self):
        while not self.cancel_event.is_set():
            if self.pause_event.is_set():
                time.sleep(0.12)
                continue
            try:
                path = self.q.get_nowait()
            except queue.Empty:
                break
            try:
                self._process_one(path)
            finally:
                self.q.task_done()
                self.sig_file_done.emit(path)

    def _process_one(self, path):
        client = self.key_cycler.next()
        filename = os.path.basename(path)
        mime = get_mime_type(path)
        ext = os.path.splitext(path)[1].lower()
        temp = None

        try:
            if ext in VIDEO_EXTS:
                temp = video_to_temp_jpeg(path)
                self.sig_preview.emit(temp, client.label, filename)
                data = image_to_base64(temp); mime_send = "image/jpeg"
            elif mime == "application/postscript":
                temp = eps_to_temp_jpeg(path)
                self.sig_preview.emit(temp, client.label, filename)
                data = image_to_base64(temp); mime_send = "image/jpeg"
            else:
                self.sig_preview.emit(path, client.label, filename)
                data = image_to_base64(path); mime_send = mime
        except Exception as e:
            self._emit_error(path, e, phase="preview")
            return

        self.sig_status.emit(f"Processing • {filename} • Key: {client.label}")

        try:
            mode_cur = self.cfg["mode"]
            if mode_cur == "Metadata":
                self.sig_update_row.emit(path, {"description": "Processing..."})
                title, description, keywords = call_gemini_meta_fast(client, data, mime_send, self.cfg)

                kw_list = [k.strip() for k in (keywords or "").split(",") if k.strip()]
                ex_list = self.cfg.get("excludes", [])
                kw_list = [k for k in kw_list if not any(ex in k.lower() for ex in ex_list)]
                if self.cfg["platform"] == "Adobe Stock":
                    kw_list = kw_list[:50]; description = smart_trim_title(description, 100)
                elif self.cfg["platform"] == "Shutterstock":
                    kw_list = kw_list[:50]; description = smart_trim_title(description, 200)
                elif self.cfg["platform"] == "Dreamstime":
                    kw_list = kw_list[:70]; description = smart_trim_title(description, 200)
                elif self.cfg["platform"] == "Vecteezy":
                    kw_list = kw_list[:100]; description = smart_trim_title(description, 200)
                kw_list = kw_list[: int(self.cfg["keywords_count"])]
                keywords = ", ".join(kw_list)

                limit = int(self.cfg["title_len"])
                title = sanitize_title_no_symbols(title)
                title = extend_title_no_symbols(title, kw_list, limit, 0.9)
                title = apply_title_prefixes(title, self.cfg["prefixes"], limit)
                if not title:
                    title = sanitize_title_no_symbols(" ".join(kw_list), max_len=limit)

                if self.cfg.get("auto_clean", True):
                    title, description, keywords = smart_clean_fields(title, description, keywords, self.cfg)

                self.sig_update_row.emit(path, {"title": title, "description": description, "keywords": keywords})

                if self.cfg["rename"]:
                    safe = sanitize_title_no_symbols(title)
                    safe = re.sub(r'[\/\\:?*"<>|]', "", safe)
                    new_name = safe + os.path.splitext(filename)[1]
                    new_path = os.path.join(os.path.dirname(path), new_name)
                    if not os.path.exists(new_path):
                        try:
                            os.rename(path, new_path)
                            self.sig_rename.emit(path, new_path, new_name)
                            path = new_path
                        except Exception as err:
                            print("Rename error:", err)
                if self.cfg["embed"]:
                    try:
                        embed_metadata_universal(path, title, description, keywords)
                    except Exception as ee:
                        print("Embed error:", ee)

            elif mode_cur == "Quality Checker":
                self.sig_update_row.emit(path, {"decision": "Processing...", "notes": "Working..."})
                result = call_quality_api(client, data, mime_send, self.cfg)
                self.sig_update_row.emit(path, {"decision": result.get("decision", "REJECT"),
                                                "score": result.get("score", 0.0),
                                                "flags": result.get("flags", ""),
                                                "notes": result.get("notes", "")})
            else:
                # Image -> Prompt (reuse metadata fast call text for speed; simple prompt)
                client_prompt = client
                prompt_text = (
                    "Describe this image briefly for image generation. Return one line, ~40-60 words, "
                    "concise, no brands, no file type words."
                )
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={client_prompt.key}"
                payload = {
                    "contents": [{"role": "user", "parts": [{"text": prompt_text}, {"inline_data": {"mime_type": mime_send, "data": data}}]}],
                    "generationConfig": {"temperature": 0.5, "maxOutputTokens": 180},
                }
                resp = _post_gemini_session(client_prompt.session, url, payload, attempts=5)
                parts = resp.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                text_out = "".join(p.get("text", "") for p in parts if "text" in p).strip()
                self.sig_update_row.emit(path, {"prompt": text_out or "(empty)"})

        except Exception as e:
            self._emit_error(path, e, phase="api")
        finally:
            if temp and os.path.exists(temp):
                try: os.remove(temp)
                except Exception: pass

    def _emit_error(self, path, e, phase=""):
        msg = f"{phase} error: {e}"
        mode = self.cfg["mode"]
        if mode == "Metadata":
            self.sig_update_row.emit(path, {"title": "Error", "description": msg, "keywords": ""})
        elif mode == "Quality Checker":
            self.sig_update_row.emit(path, {"decision": "REJECT", "score": 0.0, "flags": msg, "notes": "API/Preview error"})
        else:
            self.sig_update_row.emit(path, {"prompt": "Error: " + msg})

# -------------- Keys Dialog --------------
class KeysDialog(QtWidgets.QDialog):
    def __init__(self, parent, keys_store):
        super().__init__(parent)
        self.setWindowTitle("Manage API Keys")
        self.resize(780, 420)
        self.setStyleSheet("""
            QDialog { background-color:#0C1221; color:#E6EEF8; }
            QLineEdit, QComboBox, QTextEdit {
                background:#131B2D; border:1px solid #233254; color:#E6EEF8; padding:6px; border-radius:8px;
            }
            QPushButton {
                min-width:68px; min-height:30px; border-radius:8px; padding:6px 10px; font-size:13px; font-weight:600;
                border:1px solid #2A3854; color:#EAF6FF; background-color:#1D2A3D;
            }
            QPushButton:hover { background-color:#25374F; }
            QTableWidget { background:#0F1626; color:#E6EEF8; gridline-color:#1E2A44; }
            QHeaderView::section { background:#0F1C33; color:#9FB4D9; padding:6px; border:0px; }
            QCheckBox { color:#E6EEF8; }
            QCheckBox::indicator {
                width:18px; height:18px; border-radius:4px; border:2px solid #475569; background:#0F141B;
            }
            QCheckBox::indicator:hover { border-color:#60A5FA; }
            QCheckBox::indicator:checked {
                border:2px solid #2E4F7A;
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #20E3B2, stop:1 #3B82F6);
            }
            QCheckBox::indicator:disabled { border-color:#334155; background:#111827; }
            QLabel#logoBadge { /* keep consistent in dialog if used */ }
        """)
        self.store = keys_store
        lay = QtWidgets.QVBoxLayout(self)
        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Label", "Key (masked)", "Enabled"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        lay.addWidget(self.table)
        form = QtWidgets.QHBoxLayout()
        self.e_label = QtWidgets.QLineEdit(); self.e_label.setPlaceholderText("Label")
        self.e_key = QtWidgets.QLineEdit(); self.e_key.setPlaceholderText("API Key"); self.e_key.setEchoMode(QtWidgets.QLineEdit.Password)
        self.cb_enabled = QtWidgets.QCheckBox("Enabled"); self.cb_enabled.setChecked(True)
        form.addWidget(self.e_label); form.addWidget(self.e_key); form.addWidget(self.cb_enabled)
        lay.addLayout(form)
        btns = QtWidgets.QHBoxLayout()
        self.btn_add = QtWidgets.QPushButton("Add")
        self.btn_update = QtWidgets.QPushButton("Update")
        self.btn_toggle = QtWidgets.QPushButton("Enable/Disable")
        self.btn_delete = QtWidgets.QPushButton("Delete")
        self.btn_import = QtWidgets.QPushButton("Import .txt")
        self.btn_close = QtWidgets.QPushButton("Close")
        for b in [self.btn_add, self.btn_update, self.btn_toggle, self.btn_delete, self.btn_import]:
            btns.addWidget(b)
        btns.addStretch(1); btns.addWidget(self.btn_close)
        lay.addLayout(btns)
        self.btn_add.clicked.connect(self.add_key)
        self.btn_update.clicked.connect(self.update_key)
        self.btn_toggle.clicked.connect(self.toggle_keys)
        self.btn_delete.clicked.connect(self.delete_keys)
        self.btn_import.clicked.connect(self.import_txt)
        self.btn_close.clicked.connect(self.accept)
        self.reload()
    def mask_key(self, key):
        s = str(key or "")
        if len(s) <= 6: return "*" * len(s)
        return f"{s[:3]}***{s[-3:]}"
    def reload(self):
        self.table.setRowCount(0)
        for k in self.store:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QtWidgets.QTableWidgetItem(k.get("label", "")))
            self.table.setItem(r, 1, QtWidgets.QTableWidgetItem(self.mask_key(k.get("key", ""))))
            self.table.setItem(r, 2, QtWidgets.QTableWidgetItem("On" if k.get("enabled") else "Off"))
        self.table.resizeColumnsToContents()
    def add_key(self):
        label = self.e_label.text().strip() or f"Key {len(self.store) + 1}"
        key = self.e_key.text().strip()
        if not key:
            QtWidgets.QMessageBox.critical(self, "Error", "Key cannot be empty.")
            return
        self.store.append({"label": label, "key": key, "enabled": self.cb_enabled.isChecked()})
        self.e_label.clear(); self.e_key.clear(); self.cb_enabled.setChecked(True)
        self.reload()
    def selected_indexes(self):
        return sorted(set(i.row() for i in self.table.selectedItems()))
    def update_key(self):
        idxs = self.selected_indexes()
        if not idxs:
            QtWidgets.QMessageBox.critical(self, "Error", "Select a row to update.")
            return
        idx = idxs[0]
        if self.e_label.text().strip(): self.store[idx]["label"] = self.e_label.text().strip()
        if self.e_key.text().strip(): self.store[idx]["key"] = self.e_key.text().strip()
        self.store[idx]["enabled"] = self.cb_enabled.isChecked()
        self.reload()
    def toggle_keys(self):
        idxs = self.selected_indexes()
        if not idxs:
            QtWidgets.QMessageBox.critical(self, "Error", "Select row(s).")
            return
        for idx in idxs:
            self.store[idx]["enabled"] = not self.store[idx]["enabled"]
        self.reload()
    def delete_keys(self):
        idxs = self.selected_indexes()
        if not idxs:
            QtWidgets.QMessageBox.critical(self, "Error", "Select row(s) to delete.")
            return
        if QtWidgets.QMessageBox.question(self, "Confirm", f"Delete {len(idxs)} selected key(s)?") == QtWidgets.QMessageBox.Yes:
            for offset, idx in enumerate(sorted(idxs)):
                del self.store[idx - offset]
            self.reload()
    def import_txt(self):
        paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Import .txt with keys", "", "Text (*.txt);;All Files (*)")
        if not paths: return
        try:
            new = 0
            existing = {k["key"] for k in self.store if k.get("key")}
            for p in paths:
                with open(p, "r", encoding="utf-8") as f:
                    for ln in f:
                        s = ln.strip()
                        if not s: continue
                        label = None; key = None
                        if "|" in s: label, key = s.split("|", 1)
                        elif ":" in s: label, key = s.split(":", 1)
                        elif "," in s: label, key = s.split(",", 1)
                        else: key = s
                        label = (label or "").strip() or f"Key {len(self.store) + 1}"
                        key = (key or "").strip()
                        if not key or key in existing: continue
                        self.store.append({"label": label, "key": key, "enabled": True})
                        existing.add(key); new += 1
            self.reload()
            QtWidgets.QMessageBox.information(self, "Imported", f"Added {new} key(s).")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

# -------------- Main Window --------------
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MetaMaker — PySide6 Edition")
        self.resize(1340, 820)

        # Neon theme
        self.setStyleSheet("""
            QMainWindow { background-color: #0B1120; }
            QLabel, QCheckBox, QRadioButton { color:#E6EEF8; }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
                background:#111A2E; border:1px solid #1E2A44; color:#E6EEF8; padding:8px; border-radius:10px;
                selection-background-color:#1E2A44;
            }
            QPushButton {
                min-width:76px; min-height:34px; border-radius:8px; padding:6px 12px; font-size:13px; font-weight:600;
                border:1px solid #2A3854; color:#FFFFFF; background-color:#1D2A3D;
            }
            QPushButton#tiny {
                min-width:36px; max-width:36px; min-height:18px; max-height:18px;
                padding:2px 6px; font-size:12px; border-radius:6px;
            }
            QPushButton#primary { background-color: #3B82F6; }
            QPushButton#primary:hover { background-color: #2563EB; }
            QPushButton#accent {
                background-color: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #20E3B2, stop:1 #3B82F6);
                border:1px solid #2E4F7A; color:#FFFFFF;
            }
            QPushButton#accent:hover {
                background-color: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #38F0C2, stop:1 #4C8DFF);
            }
            QPushButton#danger {
                background-color: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #EF4444, stop:1 #F43F5E);
                border:1px solid #7A2C35; color:#FFFFFF;
            }
            QPushButton#danger:hover {
                background-color: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #F25A5A, stop:1 #F65C74);
            }
            QPushButton#neutral {
                background-color:#3B4A63; color:#EAF0F7; border:1px solid #4D5E78;
            }
            QPushButton#neutral:hover { background-color:#506487; }
            QPushButton#surface {
                background-color:#1D2A3D; color:#E6EEF8; border:1px solid #2A3854;
            }
            QPushButton#surface:hover { background-color:#24354E; }
            QPushButton:disabled { background-color:#273246; color:#9AA7B4; border-color:#273246; }

            QCheckBox { color:#E6EEF8; spacing:8px; }
            QCheckBox::indicator {
                width:18px; height:18px; border-radius:6px; border:2px solid #475569; background:#0F141B;
            }
            QCheckBox::indicator:hover { border-color:#60A5FA; }
            QCheckBox::indicator:checked {
                border:2px solid #2E4F7A;
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #20E3B2, stop:1 #3B82F6);
            }

            QProgressBar {
                background:#10192D; border:1px solid #1E2A44; color:#DDE7F4; height:18px; border-radius:9px;
            }
            QProgressBar::chunk {
                border-radius:9px;
                background-color: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #18D5C2, stop:1 #3B82F6);
            }

            QTableWidget { background:#0F1626; color:#E6EEF8; gridline-color:#1E2A44; }
            QHeaderView::section { background:#0F1C33; color:#9FB4D9; padding:6px; border:0px; }
            QGroupBox { color:#9FB4D9; border:1px solid #1E2A44; border-radius:12px; margin-top:10px; }
            QGroupBox::title { subcontrol-origin: margin; left:10px; padding:3px 6px; }

            QLabel#logoBadge {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #20E3B2, stop:1 #3B82F6);
                border:1px solid #2E4F7A;
                border-radius:8px;
            }
        """)
        self.central = QtWidgets.QWidget()
        self.setCentralWidget(self.central)
        self.keys_store = self.load_keys_store()
        self.records_by_path = {}
        self.row_by_path = {}
        self.path_by_row = {}
        self.selected_files = []
        self.mode = "Metadata"
        self.platform = "Adobe Stock"
        self.key_mode = "Rotate All"
        self.selected_key_label = ""
        self.pause_event = threading.Event()
        self.cancel_event = threading.Event()
        self._completed = False
        # Remember last parallel value when toggle OFF
        self._prev_parallel_value = 4

        # Parallel control
        self.task_queue = None
        self.worker_threads = []
        self.workers = []
        self.total_tasks = 0
        self.done_tasks = 0

        # Accept drops globally
        self.setAcceptDrops(True)

        self.build_ui()

    # ---------- Global drop handlers ----------
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        paths = []
        if event.mimeData().hasUrls():
            for u in event.mimeData().urls():
                if u.isLocalFile():
                    paths.append(u.toLocalFile())
                else:
                    paths.append(u.toString())
        elif event.mimeData().hasText():
            for ln in event.mimeData().text().splitlines():
                s = ln.strip()
                if s:
                    paths.append(s)
        if paths:
            self.add_files(paths)

    # ---------- Keys store ----------
    def load_keys_store(self):
        if os.path.exists(KEYS_JSON):
            try:
                with open(KEYS_JSON, "r", encoding="utf-8") as f:
                    data = json.load(f)
                out = []
                for i, d in enumerate(data):
                    out.append({"label": d.get("label") or f"Key {i+1}", "key": d.get("key") or "", "enabled": bool(d.get("enabled", True))})
                return out
            except Exception as e:
                print("Load keys error:", e)
        if os.path.exists(API_KEY_TXT):
            with open(API_KEY_TXT, "r", encoding="utf-8") as f:
                lines = [ln.strip() for ln in f if ln.strip()]
            data = [{"label": f"Key {i+1}", "key": k, "enabled": True} for i, k in enumerate(lines)]
            with open(KEYS_JSON, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return data
        return []

    def save_keys_store(self):
        with open(KEYS_JSON, "w", encoding="utf-8") as f:
            json.dump(self.keys_store, f, ensure_ascii=False, indent=2)

    def enabled_keys(self):
        return [k for k in self.keys_store if k.get("enabled") and k.get("key")]

    # ---------- UI ----------
    def build_ui(self):
        main_v = QtWidgets.QVBoxLayout(self.central)

        # Header with two rows
        header = QtWidgets.QWidget()
        header_v = QtWidgets.QVBoxLayout(header)
        header_v.setContentsMargins(0,0,0,0)
        header_v.setSpacing(6)

        # Row 1: Title + buttons
        row1 = QtWidgets.QHBoxLayout()
        row1.setSpacing(8)

        # Gradient badge next to title
        self.logo_badge = QtWidgets.QLabel()
        self.logo_badge.setObjectName("logoBadge")
        self.logo_badge.setFixedSize(26, 26)

        title = QtWidgets.QLabel("MetaMaker")
        tf = title.font(); tf.setPointSize(18); tf.setBold(True); title.setFont(tf)

        row1.addWidget(self.logo_badge)
        row1.addWidget(title)
        row1.addStretch(1)

        # Small buttons
        self.btn_keys = QtWidgets.QPushButton("Keys"); self.btn_keys.setObjectName("tiny")
        self.btn_getapi = QtWidgets.QPushButton("API"); self.btn_getapi.setObjectName("tiny")
        self.btn_keys.setFixedSize(40, 20)
        self.btn_getapi.setFixedSize(40, 20)
        self.btn_keys.setToolTip("Manage API keys")
        self.btn_getapi.setToolTip("Get API key")

        # Action buttons
        self.btn_start = QtWidgets.QPushButton("Start"); self.btn_start.setObjectName("primary")
        self.btn_export = QtWidgets.QPushButton("Export"); self.btn_export.setObjectName("accent")
        self.btn_cancel = QtWidgets.QPushButton("Cancel"); self.btn_cancel.setObjectName("neutral")
        self.btn_reset = QtWidgets.QPushButton("Reset"); self.btn_reset.setObjectName("danger")
        self.btn_pause = QtWidgets.QPushButton("Pause"); self.btn_pause.setObjectName("neutral"); self.btn_pause.setEnabled(False)

        row1.addWidget(self.btn_keys)
        row1.addWidget(self.btn_getapi)
        row1.addSpacing(6)
        row1.addWidget(self.btn_start)
        row1.addWidget(self.btn_export)
        row1.addWidget(self.btn_cancel)
        row1.addWidget(self.btn_reset)
        row1.addWidget(self.btn_pause)
        header_v.addLayout(row1)

        # Row 2: right-aligned Mode + Platform + API rotation + Parallel
        row2 = QtWidgets.QHBoxLayout()
        row2.setSpacing(8)

        self.cbo_mode = QtWidgets.QComboBox()
        self.cbo_mode.addItems(["Metadata", "Image → Prompt", "Quality Checker"])
        self.cbo_mode.setToolTip("Processing mode")
        self.cbo_mode.currentTextChanged.connect(self.on_mode_change)

        self.cbo_platform = QtWidgets.QComboBox()
        self.cbo_platform.addItems(PLATFORMS)
        self.cbo_platform.setToolTip("Target stock platform")
        self.cbo_platform.currentTextChanged.connect(lambda s: setattr(self, "platform", s))

        self.cbo_keymode = QtWidgets.QComboBox(); self.cbo_keymode.addItems(["Rotate All", "Use Selected"])
        self.cbo_keymode.setToolTip("Use all enabled keys in rotation or a selected one")
        self.cbo_keymode.currentTextChanged.connect(self.on_keymode_change)
        self.cbo_keyselect = QtWidgets.QComboBox(); self.reload_keyselect()
        self.cbo_keyselect.setToolTip("Pick a specific API key when 'Use Selected' is chosen")
        self.cbo_keyselect.currentTextChanged.connect(lambda s: setattr(self, "selected_key_label", s))

        # parallel toggle + jobs
        self.ck_parallel = QtWidgets.QCheckBox("Parallel")
        self.ck_parallel.setChecked(True)
        self.ck_parallel.setToolTip("Toggle parallel processing. Off = process one file at a time.")
        self.ck_parallel.toggled.connect(self.on_parallel_toggle)

        self.spn_parallel = QtWidgets.QSpinBox()
        self.spn_parallel.setRange(1, 16)
        self.spn_parallel.setValue(4)
        self.spn_parallel.setToolTip("Total parallel jobs (when Parallel is ON)")

        row2.addStretch(1)
        row2.addWidget(QtWidgets.QLabel("Mode:"))
        row2.addWidget(self.cbo_mode)
        row2.addSpacing(12)
        row2.addWidget(QtWidgets.QLabel("Platform:"))
        row2.addWidget(self.cbo_platform)
        row2.addSpacing(12)
        row2.addWidget(QtWidgets.QLabel("API Keys:"))
        row2.addWidget(self.cbo_keymode)
        row2.addWidget(self.cbo_keyselect)
        row2.addSpacing(12)
        row2.addWidget(QtWidgets.QLabel("Parallel:"))
        row2.addWidget(self.ck_parallel)
        row2.addWidget(QtWidgets.QLabel("Jobs:"))
        row2.addWidget(self.spn_parallel)
        header_v.addLayout(row2)

        main_v.addWidget(header)

        # Splitter: left controls, right preview/results
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.setHandleWidth(8)
        splitter.setOpaqueResize(True)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        main_v.addWidget(splitter, 1)

        left_scroll = QtWidgets.QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setMinimumWidth(520)
        left_widget = QtWidgets.QWidget()
        left_scroll.setWidget(left_widget)
        splitter.addWidget(left_scroll)

        right_widget = QtWidgets.QWidget()
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        # Left cards
        left_v = QtWidgets.QVBoxLayout(left_widget)
        left_v.setContentsMargins(6,6,6,6); left_v.setSpacing(10)

        # Step 1
        c1 = SectionCard("1) Add media & URLs"); left_v.addWidget(c1)
        self.drop = DropArea(height=170); c1.body_layout.addWidget(self.drop)
        self.drop.clicked.connect(self.select_files)
        self.drop.dropped.connect(self.handle_drop)
        tip = QtWidgets.QLabel("Tips: Drop PNG/JPG/EPS/MP4 or folders • Paste a page URL and click Fetch • Or import URLs from .txt")
        tip.setStyleSheet("color:#8EA1B2;")
        c1.body_layout.addWidget(tip)

        url_row = QtWidgets.QHBoxLayout()
        self.e_url = QtWidgets.QLineEdit(); self.e_url.setPlaceholderText("https://example.com/page"); self.e_url.setClearButtonEnabled(True)
        self.btn_fetch = QtWidgets.QPushButton("Fetch Images"); self.btn_fetch.setObjectName("accent")
        self.btn_import_urls = QtWidgets.QPushButton("Import URLs (.txt)"); self.btn_import_urls.setObjectName("surface")
        url_row.addWidget(QtWidgets.QLabel("Page URL"))
        url_row.addWidget(self.e_url, 1)
        url_row.addWidget(self.btn_fetch)
        url_row.addWidget(self.btn_import_urls)
        c1.body_layout.addLayout(url_row)

        # Step 2 (Generation settings + preferences)
        c3 = SectionCard("2) Generation Settings"); left_v.addWidget(c3)
        sliders_row = QtWidgets.QHBoxLayout(); c3.body_layout.addLayout(sliders_row)
        self.s_title = LabeledSlider("Title Length", 50, 150, 150); sliders_row.addWidget(self.s_title, 1)
        self.s_kw = LabeledSlider("Max Keywords", 10, 50, 30); sliders_row.addWidget(self.s_kw, 1)
        self.s_prompt = LabeledSlider("Prompt Words", 30, 500, 50); sliders_row.addWidget(self.s_prompt, 1)
        toggles = QtWidgets.QHBoxLayout()
        self.ck_rename = QtWidgets.QCheckBox("Rename files based on title"); self.ck_rename.setChecked(True)
        self.ck_embed = QtWidgets.QCheckBox("Embed metadata (JPG/PNG/EPS/VIDEO)"); self.ck_embed.setChecked(True)
        toggles.addWidget(self.ck_rename); toggles.addWidget(self.ck_embed); toggles.addStretch(1)
        c3.body_layout.addLayout(toggles)

        prefs_group = QtWidgets.QGroupBox("Title & Keywords Preferences")
        pg_v = QtWidgets.QVBoxLayout(prefs_group)
        chips = QtWidgets.QHBoxLayout()
        self.ck_sil = QtWidgets.QCheckBox("Silhouette")
        self.ck_transp = QtWidgets.QCheckBox("Transparent")
        self.ck_iso = QtWidgets.QCheckBox("Isolated")
        self.ck_cut = QtWidgets.QCheckBox("Cutout")
        chips.addWidget(self.ck_sil); chips.addWidget(self.ck_transp); chips.addWidget(self.ck_iso); chips.addWidget(self.ck_cut); chips.addStretch(1)
        pg_v.addLayout(chips)
        grid4 = QtWidgets.QGridLayout()
        self.e_prefixes = QtWidgets.QLineEdit(); self.e_prefixes.setPlaceholderText("e.g., Minimalist, Studio lighting")
        self.e_exclude = QtWidgets.QLineEdit(); self.e_exclude.setPlaceholderText("words to exclude, comma separated")
        grid4.addWidget(QtWidgets.QLabel("Custom prefixes"), 0,0); grid4.addWidget(self.e_prefixes, 0,1)
        grid4.addWidget(QtWidgets.QLabel("Exclude keywords"), 1,0); grid4.addWidget(self.e_exclude, 1,1)
        pg_v.addLayout(grid4)
        c3.body_layout.addWidget(prefs_group)

        # Step 3 Smart Clean
        c35 = SectionCard("3) Post-process (Smart Clean)"); left_v.addWidget(c35)
        v35 = c35.body_layout
        row35a = QtWidgets.QHBoxLayout()
        self.ck_auto_clean = QtWidgets.QCheckBox("Auto clean after generation"); self.ck_auto_clean.setChecked(True)
        self.ck_clean_title_dup = QtWidgets.QCheckBox("Deduplicate title words"); self.ck_clean_title_dup.setChecked(True)
        self.ck_clean_kw_dup = QtWidgets.QCheckBox("Deduplicate keywords"); self.ck_clean_kw_dup.setChecked(True)
        row35a.addWidget(self.ck_auto_clean); row35a.addWidget(self.ck_clean_title_dup); row35a.addWidget(self.ck_clean_kw_dup); row35a.addStretch(1)
        v35.addLayout(row35a)
        grid35 = QtWidgets.QGridLayout()
        self.e_banned = QtWidgets.QLineEdit()
        self.e_banned.setPlaceholderText("Banned words (e.g., ™, ®, ©, (tm), brand, trademark, copyright)")
        self.e_mislead = QtWidgets.QLineEdit()
        self.e_mislead.setPlaceholderText("Misleading words (e.g., free, best, official, 100%)")
        grid35.addWidget(QtWidgets.QLabel("Banned words"), 0,0); grid35.addWidget(self.e_banned, 0,1)
        grid35.addWidget(QtWidgets.QLabel("Misleading words"), 1,0); grid35.addWidget(self.e_mislead, 1,1)
        v35.addLayout(grid35)
        self.btn_clean_now = QtWidgets.QPushButton("Run Smart Clean now"); self.btn_clean_now.setObjectName("accent")
        v35.addWidget(self.btn_clean_now, 0, QtCore.Qt.AlignLeft)

        # Removed: Step 4 Export Rules (as requested)

        left_v.addStretch(1)

        # Right side: Preview + progress + Results
        rv = QtWidgets.QVBoxLayout(right_widget)

        pb = QtWidgets.QGroupBox("Preview"); rv.addWidget(pb, 0)
        pb_layout = QtWidgets.QGridLayout(pb)
        self.preview_label = QtWidgets.QLabel()
        self.preview_label.setFixedSize(360, 220)
        self.preview_label.setStyleSheet("background:#10192D; border:1px solid #1E2A44;")
        self.preview_label.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_file = QtWidgets.QLabel("No file")
        self.lbl_info = QtWidgets.QLabel(f"Model: {MODEL} • Key: –"); self.lbl_info.setStyleSheet("color:#9FB4D9;")
        pb_layout.addWidget(self.preview_label, 0, 0, 2, 1)
        pb_layout.addWidget(self.lbl_file, 0, 1)
        pb_layout.addWidget(self.lbl_info, 1, 1)

        prog_row = QtWidgets.QHBoxLayout()
        self.progress = QtWidgets.QProgressBar(); self.progress.setRange(0, 100); self.progress.setValue(0)
        self.lbl_status = QtWidgets.QLabel("Ready"); self.lbl_status.setStyleSheet("color:#9FB4D9;")
        prog_row.addWidget(self.progress, 1); prog_row.addWidget(self.lbl_status, 0)
        rv.addLayout(prog_row)

        gb = QtWidgets.QGroupBox("Results"); rv.addWidget(gb, 1)
        gb_v = QtWidgets.QVBoxLayout(gb)
        head_row = QtWidgets.QHBoxLayout()
        head_row.addStretch(1)
        self.btn_clear_results = QtWidgets.QPushButton("Clear"); self.btn_clear_results.setObjectName("danger")
        head_row.addWidget(self.btn_clear_results)
        gb_v.addLayout(head_row)
        self.table = QtWidgets.QTableWidget()
        gb_v.addWidget(self.table)
        self.create_table()

        # selection → preview
        self.table.itemSelectionChanged.connect(self.on_table_selection_changed)

        # context menu
        self.table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.on_table_context_menu)

        # Connections
        self.btn_fetch.clicked.connect(self.fetch_page_images)
        self.btn_import_urls.clicked.connect(self.import_urls_txt)
        self.btn_start.clicked.connect(self.start_process)
        self.btn_export.clicked.connect(self.export_data)
        self.btn_cancel.clicked.connect(self.cancel_process)
        self.btn_reset.clicked.connect(self.reset_all)
        self.btn_pause.clicked.connect(self.toggle_pause)
        self.btn_keys.clicked.connect(self.open_keys)
        self.btn_getapi.clicked.connect(lambda: webbrowser.open("https://aistudio.google.com/app/apikey"))
        self.btn_clear_results.clicked.connect(self.clear_results)
        self.btn_clean_now.clicked.connect(self.run_smart_clean_now)

        self.cbo_mode.setCurrentText("Metadata")

    def on_keymode_change(self, s):
        self.key_mode = s

    def on_parallel_toggle(self, checked):
        if checked:
            self.spn_parallel.setEnabled(True)
            if getattr(self, "_prev_parallel_value", 0) and self._prev_parallel_value > 1:
                self.spn_parallel.setValue(self._prev_parallel_value)
            else:
                if self.spn_parallel.value() < 2:
                    self.spn_parallel.setValue(4)
        else:
            self._prev_parallel_value = self.spn_parallel.value()
            self.spn_parallel.setValue(1)
            self.spn_parallel.setEnabled(False)

    def reload_keyselect(self):
        if not hasattr(self, "cbo_keyselect"):
            return
        self.cbo_keyselect.clear()
        labels = [k["label"] for k in self.enabled_keys()]
        if labels:
            self.cbo_keyselect.addItems(labels)
        else:
            self.cbo_keyselect.addItem("—")

    def on_mode_change(self, s):
        self.mode = s
        self.create_table()
        for path in self.selected_files:
            self.ensure_row_for_path(path)

    # ---------- Table helpers ----------
    def _set_cell_text(self, r, c, text, align_center=False):
        it = self.table.item(r, c)
        if it is None:
            it = QtWidgets.QTableWidgetItem("")
            if align_center:
                it.setTextAlignment(QtCore.Qt.AlignCenter)
            self.table.setItem(r, c, it)
        it.setText(str(text))

    # ---------- Table ----------
    def create_table(self):
        if self.mode == "Metadata":
            cols = ["#", "Filename", "Title", "Description", "Keywords"]
        elif self.mode == "Quality Checker":
            cols = ["#", "Filename", "Decision", "Score", "Flags", "Notes"]
        else:
            cols = ["Filename", "Prompt"]
        self.table.setColumnCount(len(cols))
        self.table.setHorizontalHeaderLabels(cols)
        self.table.setRowCount(0)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.row_by_path.clear()
        self.path_by_row.clear()
        for path in self.selected_files:
            self.ensure_row_for_path(path)

    def ensure_row_for_path(self, path):
        if path in self.row_by_path:
            return self.row_by_path[path]
        r = self.table.rowCount()
        self.table.insertRow(r)
        filename = os.path.basename(path)
        if self.mode == "Metadata":
            vals = ["", filename, "", "Queued", ""]
        elif self.mode == "Quality Checker":
            vals = ["", filename, "Queued", "", "", ""]
        else:
            vals = [filename, ""]
        for c, v in enumerate(vals):
            it = QtWidgets.QTableWidgetItem(str(v))
            if c == 0 and self.mode != "Image → Prompt":
                it.setTextAlignment(QtCore.Qt.AlignCenter)
            self.table.setItem(r, c, it)
        self.row_by_path[path] = r
        self.path_by_row[r] = path
        self.records_by_path.setdefault(path, {"filename": filename})
        self.update_seq_numbers()
        return r

    def update_seq_numbers(self):
        if self.mode == "Image → Prompt": return
        for r in range(self.table.rowCount()):
            self._set_cell_text(r, 0, str(r+1), align_center=True)

    def update_row(self, path, updates):
        rec = self.records_by_path.get(path, {"filename": os.path.basename(path)})
        rec.update(updates or {})
        self.records_by_path[path] = rec
        r = self.ensure_row_for_path(path)
        if self.mode == "Metadata":
            mapping = {"#": str(r+1), "Filename": rec.get("filename",""),
                       "Title": rec.get("title",""), "Description": rec.get("description",""), "Keywords": rec.get("keywords","")}
            cols = ["#", "Filename", "Title", "Description", "Keywords"]
        elif self.mode == "Quality Checker":
            score = rec.get("score","")
            if isinstance(score, (int,float)): score = f"{int(float(score)*100)}%"
            mapping = {"#": str(r+1), "Filename": rec.get("filename",""),
                       "Decision": rec.get("decision",""), "Score": score,
                       "Flags": rec.get("flags",""), "Notes": rec.get("notes","")}
            cols = ["#", "Filename", "Decision", "Score", "Flags", "Notes"]
        else:
            mapping = {"Filename": rec.get("filename",""), "Prompt": rec.get("prompt","")}
            cols = ["Filename", "Prompt"]
        for c, col in enumerate(cols):
            self._set_cell_text(r, c, mapping.get(col, ""), align_center=(c==0 and self.mode!="Image → Prompt"))

    def rename_record_path(self, old_path, new_path, new_filename):
        if old_path not in self.row_by_path:
            return
        r = self.row_by_path.pop(old_path)
        self.row_by_path[new_path] = r
        self.path_by_row[r] = new_path
        rec = self.records_by_path.pop(old_path, {"filename": new_filename})
        rec["filename"] = new_filename
        self.records_by_path[new_path] = rec
        headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
        if "Filename" in headers:
            ci = headers.index("Filename")
            self._set_cell_text(r, ci, new_filename)

    # ---------- Selection → Preview ----------
    def on_table_selection_changed(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        r = rows[0].row()
        path = self.path_by_row.get(r)
        if path and os.path.exists(path):
            self.show_preview_static(path)
            self.lbl_file.setText(os.path.basename(path))

    # ---------- Context menu ----------
    def on_table_context_menu(self, pos):
        idx = self.table.indexAt(pos)
        if not idx.isValid():
            return
        r = idx.row()
        self.table.selectRow(r)
        menu = QtWidgets.QMenu(self)
        headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
        def copy_col(col_name):
            if col_name in headers:
                ci = headers.index(col_name)
                it = self.table.item(r, ci)
                QtWidgets.QApplication.clipboard().setText("" if it is None else it.text())
        it = self.table.item(r, idx.column())
        menu.addAction("Copy cell", lambda: QtWidgets.QApplication.clipboard().setText("" if it is None else it.text()))
        if "Filename" in headers: menu.addAction("Copy Filename", lambda: copy_col("Filename"))
        if "Title" in headers: menu.addAction("Copy Title", lambda: copy_col("Title"))
        if "Description" in headers: menu.addAction("Copy Description", lambda: copy_col("Description"))
        if "Keywords" in headers: menu.addAction("Copy Keywords", lambda: copy_col("Keywords"))
        if "Prompt" in headers: menu.addAction("Copy Prompt", lambda: copy_col("Prompt"))
        if "Decision" in headers: menu.addAction("Copy Decision", lambda: copy_col("Decision"))
        if "Score" in headers: menu.addAction("Copy Score", lambda: copy_col("Score"))
        if "Flags" in headers: menu.addAction("Copy Flags", lambda: copy_col("Flags"))
        if "Notes" in headers: menu.addAction("Copy Notes", lambda: copy_col("Notes"))
        menu.exec(self.table.viewport().mapToGlobal(pos))

    # ---------- Drop / Adding ----------
    def _norm_path(self, p):
        try:
            return os.path.normcase(os.path.abspath(p))
        except Exception:
            return p

    def handle_drop(self, items):
        if not items:
            QtWidgets.QMessageBox.information(self, "No input", "Please drop files/folders/URLs.")
            return
        self.add_files(items)

    def select_files(self):
        exts = "Images/Videos (*.png *.jpg *.jpeg *.eps *.mp4 *.mov *.avi *.mkv *.wmv);;All Files (*)"
        paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select files", "", exts)
        if not paths: return
        self.add_files(paths)

    def add_files(self, paths):
        collected = []
        for p in paths:
            if not p: continue
            s = p.strip().strip("{}").strip('"')
            if s.lower().endswith(".txt") and os.path.isfile(s):
                self._import_urls_from_txt_path(s); continue
            if is_file_uri(s):
                local = file_uri_to_path(s)
                if local and os.path.exists(local): s = local
            if os.path.isdir(s):
                for root, _, files in os.walk(s):
                    for fn in files:
                        if fn.lower().endswith(SUPPORTED_EXTS):
                            collected.append(os.path.join(root, fn))
            elif is_url(normalize_input_url(s)) or re.match(r"^[a-z0-9\-\._]+\.[a-z]{2,}", s, re.I):
                url = normalize_input_url(s)
                try:
                    path = download_one_from_url_or_page(url)
                    if path: collected.append(path)
                except Exception:
                    print("Could not resolve URL to image:", url)
            elif s.lower().endswith(SUPPORTED_EXTS) and os.path.exists(s):
                collected.append(s)
        if not collected:
            return
        existing = {self._norm_path(x) for x in self.selected_files}
        new_added = []
        for x in collected:
            nx = self._norm_path(x)
            if nx not in existing:
                existing.add(nx)
                self.selected_files.append(nx)
                self.ensure_row_for_path(nx)
                new_added.append(nx)
        if new_added:
            self.show_preview_static(new_added[-1])
            self.lbl_file.setText(os.path.basename(new_added[-1]))

    def fetch_page_images(self):
        page = normalize_input_url(self.e_url.text().strip())
        if not page or not is_url(page):
            QtWidgets.QMessageBox.critical(self, "Invalid URL", "Please provide a valid http(s) URL.")
            return
        self.set_status("Fetching images from page…")
        QtWidgets.QApplication.processEvents()
        try:
            assets = extract_assets_from_page(page, max_count=120)
            if not assets:
                QtWidgets.QMessageBox.warning(self, "No images", "No downloadable images found on that page.")
                self.set_status("Ready"); return
            local = []
            for au, ref in assets:
                try:
                    p = download_direct_with_referer(au, ref); local.append(p)
                except Exception:
                    continue
            if not local:
                QtWidgets.QMessageBox.warning(self, "No images", "Could not download any image from that page.")
                self.set_status("Ready"); return
            self.add_files(local)
            QtWidgets.QMessageBox.information(self, "Fetched", f"Imported {len(local)} image(s) from page.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Fetch Error", str(e))
        finally:
            self.set_status("Ready")

    def import_urls_txt(self):
        paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Import URLs from .txt", "", "Text (*.txt);;All Files (*)")
        if not paths: return
        added = []
        for p in paths:
            try:
                self._import_urls_from_txt_path(p, added_list=added)
            except Exception as e:
                print("Import .txt error:", e)
        if added: self.add_files(added)
        QtWidgets.QMessageBox.information(self, "Imported", f"Added {len(added)} item(s) from {len(paths)} file(s).")

    def _import_urls_from_txt_path(self, txt_path, added_list=None):
        added_list = added_list or []
        with open(txt_path, "r", encoding="utf-8") as f:
            for ln in f:
                u = ln.strip()
                if not u or u.startswith("#"): continue
                url = normalize_input_url(u)
                if not is_url(url): continue
                try:
                    path = download_one_from_url_or_page(url)
                    if path: added_list.append(path)
                except Exception:
                    print("URL import (single) failed:", url)
        return len(added_list)

    # ---------- Start / Parallel Manager ----------
    def build_cfg(self):
        prefixes = []
        if self.ck_sil.isChecked(): prefixes.append("Silhouette")
        if self.ck_transp.isChecked(): prefixes.append("Transparent")
        if self.ck_iso.isChecked(): prefixes.append("Isolated")
        if self.ck_cut.isChecked(): prefixes.append("Cutout")
        prefixes += parse_word_list(self.e_prefixes.text())
        return {
            "mode": self.mode,
            "platform": self.cbo_platform.currentText(),
            "title_len": self.s_title.value(),
            "keywords_count": self.s_kw.value(),
            "prompt_word_count": self.s_prompt.value(),
            "rename": self.ck_rename.isChecked(),
            "embed": self.ck_embed.isChecked(),
            "prefixes": prefixes,
            "excludes": parse_word_list(self.e_exclude.text()),
            # Smart clean
            "auto_clean": self.ck_auto_clean.isChecked(),
            "clean_banned": parse_word_list(self.e_banned.text()),
            "clean_mislead": parse_word_list(self.e_mislead.text()),
            "clean_dedupe_title": self.ck_clean_title_dup.isChecked(),
            "clean_dedupe_kw": self.ck_clean_kw_dup.isChecked(),
        }

    def start_process(self):
        if not self.selected_files:
            QtWidgets.QMessageBox.critical(self, "Error", "Please add files first."); return
        enabled = self.enabled_keys()
        if not enabled:
            QtWidgets.QMessageBox.critical(self, "Error", "No API keys available. Use Keys to add/import."); return

        # Build clients
        clients = []
        if self.cbo_keymode.currentText() == "Use Selected":
            label = self.cbo_keyselect.currentText().strip()
            sel = [k for k in enabled if k["label"] == label]
            if not sel:
                QtWidgets.QMessageBox.critical(self, "Error", f"Selected key '{label}' missing/disabled."); return
            clients.append(ApiClient(sel[0]["label"], sel[0]["key"]))
        else:
            for k in enabled:
                clients.append(ApiClient(k["label"], k["key"]))

        self.key_cycler = KeyCycler(clients)

        # Build queue
        self.task_queue = queue.Queue()
        for p in self.selected_files:
            self.ensure_row_for_path(p)
            self.task_queue.put(p)
        self.total_tasks = len(self.selected_files)
        self.done_tasks = 0
        self.progress.setValue(0)
        self._completed = False

        cfg = self.build_cfg()
        self.pause_event.clear()
        self.cancel_event.clear()

        # Worker count controlled by Parallel toggle
        worker_count = 1 if not self.ck_parallel.isChecked() else max(1, int(self.spn_parallel.value()))
        self.workers = []
        self.worker_threads = []
        for i in range(worker_count):
            worker = FileWorker(i, self.key_cycler, self.task_queue, cfg, self.pause_event, self.cancel_event)
            th = QtCore.QThread(self)
            worker.moveToThread(th)
            th.started.connect(worker.run)
            worker.sig_status.connect(self.set_status)
            worker.sig_preview.connect(self.on_preview)
            worker.sig_update_row.connect(self.update_row)
            worker.sig_rename.connect(self.rename_record_path)
            worker.sig_file_done.connect(self.on_file_done)
            self.workers.append(worker)
            self.worker_threads.append(th)

        for th in self.worker_threads:
            th.start()

        self.btn_pause.setEnabled(True)
        self.btn_start.setEnabled(False)
        self.set_status(f"Started • {len(self.worker_threads)} worker(s) • rotating across {len(clients)} key(s)")

    def on_file_done(self, path):
        self.done_tasks += 1
        pct = int(self.done_tasks / max(1, self.total_tasks) * 100)
        self.progress.setValue(pct)
        self.set_status(f"{pct}% • {self.done_tasks}/{self.total_tasks} • {len(self.worker_threads)} worker(s)")
        if self.done_tasks >= self.total_tasks:
            QtCore.QTimer.singleShot(200, self._maybe_finish)

    def _maybe_finish(self):
        if self._completed:
            return
        if self.task_queue and self.task_queue.empty():
            self.on_complete(self.cancel_event.is_set())

    def cancel_process(self):
        if not self.worker_threads:
            return
        self.cancel_event.set()
        self.pause_event.clear()
        self.set_status("Cancelling...")

    def toggle_pause(self):
        if not self.worker_threads:
            return
        if not self.pause_event.is_set():
            self.pause_event.set()
            self.btn_pause.setText("Resume")
            self.set_status("Paused")
        else:
            self.pause_event.clear()
            self.btn_pause.setText("Pause")
            self.set_status("Resuming...")

    def on_complete(self, cancelled):
        if self._completed:
            return
        self._completed = True
        self.set_status("Complete" if not cancelled else "Cancelled")
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_pause.setText("Pause")
        for th in self.worker_threads:
            try:
                th.quit()
                th.wait()
            except Exception:
                pass
        self.worker_threads.clear()
        self.workers.clear()

    def on_preview(self, image_path, key_label, filename):
        self.show_preview_static(image_path)
        self.lbl_file.setText(filename)
        self.lbl_info.setText(f"Model: {MODEL} • Key: {key_label}")

    def show_preview_static(self, image_path):
        try:
            pix = QtGui.QPixmap(image_path)
            if pix.isNull():
                raise Exception("Invalid image for preview")
            self.preview_label.setPixmap(pix.scaled(self.preview_label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        except Exception:
            self.preview_label.setText("No preview")

    def set_status(self, text):
        self.lbl_status.setText(text)

    def reset_all(self):
        if any(th.isRunning() for th in self.worker_threads):
            QtWidgets.QMessageBox.information(self, "Busy", "Stop current process first."); return
        self.progress.setValue(0); self.set_status("Ready")
        self.records_by_path.clear(); self.row_by_path.clear(); self.path_by_row.clear(); self.selected_files.clear()
        self.create_table()
        self.preview_label.clear(); self.lbl_file.setText("No file"); self.lbl_info.setText(f"Model: {MODEL} • Key: –")
        self.btn_start.setEnabled(True); self.btn_pause.setEnabled(False); self.btn_pause.setText("Pause")

    def clear_results(self):
        if any(th.isRunning() for th in self.worker_threads):
            QtWidgets.QMessageBox.information(self, "Busy", "Stop current process first."); return
        self.table.setRowCount(0)
        self.records_by_path.clear()
        self.row_by_path.clear()
        self.path_by_row.clear()
        self.selected_files.clear()
        self.set_status("Results cleared")


    # ---------- Smart Clean now ----------
    def run_smart_clean_now(self):
        if not self.records_by_path:
            QtWidgets.QMessageBox.information(self, "Info", "Nothing to clean."); return
        cfg = self.build_cfg()
        changed = 0
        for path, rec in list(self.records_by_path.items()):
            if self.mode != "Metadata":
                continue
            title = rec.get("title","")
            description = rec.get("description","")
            keywords = rec.get("keywords","")
            if not (title or description or keywords):
                continue
            t2, d2, k2 = smart_clean_fields(title, description, keywords, cfg)
            if (t2 != title) or (d2 != description) or (k2 != keywords):
                changed += 1
                self.records_by_path[path].update({"title": t2, "description": d2, "keywords": k2})
                self.update_row(path, {"title": t2, "description": d2, "keywords": k2})
        QtWidgets.QMessageBox.information(self, "Smart Clean", f"Cleaned {changed} item(s).")

    # ---------- Export ----------
    def export_data(self):
        if self.table.rowCount() == 0:
            QtWidgets.QMessageBox.information(self, "Info", "Nothing to export!"); return

        def ensure_ext(path, sel_filter, default_ext):
            if os.path.splitext(path)[1]:
                return path
            # derive from selected filter like "CSV (*.csv)"
            m = re.search(r"\*\.(\w+)", sel_filter or "")
            ext = f".{m.group(1)}" if m else default_ext
            return path + ext

        mode = self.mode

        if mode == "Metadata":
            rows = []
            for path, rec in self.records_by_path.items():
                rows.append({
                    "filename": rec.get("filename",""),
                    "title": rec.get("title",""),
                    "description": rec.get("description",""),
                    "keywords": rec.get("keywords","")
                })
            out, sel = QtWidgets.QFileDialog.getSaveFileName(self, "Export metadata", "metadata_output.csv", "CSV (*.csv);;JSON (*.json)")
            if not out: return
            out = ensure_ext(out, sel, ".csv")
            if out.lower().endswith(".csv"):
                pd.DataFrame(rows)[["filename","title","description","keywords"]].to_csv(out, index=False, encoding="utf-8")
            else:
                with open(out, "w", encoding="utf-8") as f:
                    json.dump(rows, f, ensure_ascii=False, indent=2)

        elif mode == "Quality Checker":
            rows = []
            for path, rec in self.records_by_path.items():
                score = rec.get("score","")
                if isinstance(score, (int,float)): score = f"{int(float(score)*100)}%"
                rows.append({
                    "filename": rec.get("filename",""),
                    "decision": rec.get("decision",""),
                    "score": score,
                    "flags": rec.get("flags",""),
                    "notes": rec.get("notes","")
                })
            out, sel = QtWidgets.QFileDialog.getSaveFileName(self, "Export quality results", "quality_output.csv", "CSV (*.csv);;JSON (*.json)")
            if not out: return
            out = ensure_ext(out, sel, ".csv")
            if out.lower().endswith(".csv"):
                pd.DataFrame(rows)[["filename","decision","score","flags","notes"]].to_csv(out, index=False, encoding="utf-8")
            else:
                with open(out, "w", encoding="utf-8") as f:
                    json.dump(rows, f, ensure_ascii=False, indent=2)

        else:  # Image → Prompt
            prompts = [(rec.get("filename",""), (rec.get("prompt","") or "").strip())
                       for rec in self.records_by_path.values() if (rec.get("prompt","") or "").strip()]
            out, sel = QtWidgets.QFileDialog.getSaveFileName(self, "Export prompts", "prompt_output.txt", "Text (*.txt);;CSV (*.csv);;JSON (*.json)")
            if not out: return
            out = ensure_ext(out, sel, ".txt")
            if out.lower().endswith(".txt"):
                with open(out, "w", encoding="utf-8") as f:
                    f.write("\n".join([p for _, p in prompts]))
            elif out.lower().endswith(".csv"):
                df = pd.DataFrame([{"filename": fn, "prompt": pr} for fn, pr in prompts])
                df.to_csv(out, index=False, encoding="utf-8")
            else:
                with open(out, "w", encoding="utf-8") as f:
                    json.dump([p for _, p in prompts], f, ensure_ascii=False, indent=2)

        QtWidgets.QMessageBox.information(self, "Exported", f"Saved to:\n{out}")

    # ---------- Keys dialog ----------
    def open_keys(self):
        dlg = KeysDialog(self, self.keys_store)
        if dlg.exec():
            self.save_keys_store()
            self.reload_keyselect()

# -------------- App --------------
def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor("#0B1120"))
    palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor("#E6EEF8"))
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor("#0F1626"))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor("#0F1C33"))
    palette.setColor(QtGui.QPalette.Text, QtGui.QColor("#E6EEF8"))
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor("#1D2A3D"))
    palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor("#E6EEF8"))
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor("#3B82F6"))
    palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor("#0B1016"))
    app.setPalette(palette)

    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()