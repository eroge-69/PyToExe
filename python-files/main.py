from datetime import datetime
import os, yaml, logging, re
from typing import Dict, List
from .utils import ensure_dir, make_logger, sanitize
from .downloader import download_best_mp4, _convert_to_mp4
from .filters import build_vf
from .processed_db import base_root_from_out
from .export import export_clip

def _next_free_index(lab_dir: str, base: str, width: int = 4, ext: str = "mp4") -> int:
    try:
        os.makedirs(lab_dir, exist_ok=True)
        n = 0
        rx = re.compile(rf"^{re.escape(base)}_(\d+)\.{re.escape(ext)}$", re.IGNORECASE)
        for fn in os.listdir(lab_dir):
            m = rx.match(fn)
            if m:
                try:
                    n = max(n, int(m.group(1)))
                except Exception:
                    pass
        return n + 1
    except Exception:
        return 1

def process(url, base_name, output_dir, cfg_path, logger, on_download_progress=None, on_detect_progress=None, on_new_identity=None, single_mode=False, cfg_override=None):
    """
    SIMPLE PIPELINE (sin detección de rostro ni modo manual).
    - Aplica zoom/máscaras desde cfg.
    - Clipa TODO el video en fragmentos de 6-7 s secuenciales (configurable con min_clip_seconds/max_clip_seconds).
    """
    ensure_dir(output_dir)
    input_dir = os.path.join(output_dir, 'input'); ensure_dir(input_dir)
    clips_root = output_dir
    try:
        base_last = os.path.basename(os.path.normpath(output_dir)).lower()
    except Exception:
        base_last = ''
    if base_last != 'clips':
        clips_root = os.path.join(output_dir, 'clips')
    ensure_dir(clips_root)
    root_dir = base_root_from_out(output_dir)
    logs_dir = os.path.join(root_dir, 'logs'); ensure_dir(logs_dir)
    log_path = os.path.join(logs_dir, f"{sanitize(base_name)}_"+datetime.now().strftime("%Y%m%d_%H%M%S")+".log")
    for h in list(logger.handlers):
        if isinstance(h, logging.FileHandler):
            logger.removeHandler(h)
    if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
        fh = logging.FileHandler(log_path, encoding='utf-8')
        fmt = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s', '%H:%M:%S')
        fh.setFormatter(fmt); logger.addHandler(fh)

    # Cargar cfg
    try:
        with open(cfg_path, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f) or {}
    except Exception:
        cfg = {}
    if cfg_override:
        try:
            for k,v in (cfg_override or {}).items():
                cfg[k] = v
        except Exception:
            pass

    # Resolver video
    if os.path.isfile(url):
        video_path = _convert_to_mp4(url)
        if on_download_progress: on_download_progress(100, 'Video local listo')
    else:
        video_path = download_best_mp4(url, input_dir, logger, on_progress=on_download_progress)
        video_path = _convert_to_mp4(video_path)

    # Duración con ffprobe
    def _ffprobe_duration_sec(path: str) -> float:
        try:
            import subprocess
            out = subprocess.check_output(
                ['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1', path],
                stderr=subprocess.STDOUT
            )
            return float(out.decode('utf-8','ignore').strip())
        except Exception:
            return 0.0

    duration = _ffprobe_duration_sec(video_path)
    if duration <= 0.1:
        logger.warning('No se pudo obtener la duración del video.')
        return {'total':0,'by_label':{},'durations':{},'labels_all':[],'skipped_similar':0}

    # Slicing 6-7 s (configurable)
    min_len = float(cfg.get('min_clip_seconds', 6))
    max_len = float(cfg.get('max_clip_seconds', 7))
    if min_len <= 0: min_len = 6.0
    if max_len < min_len: max_len = min_len

    parts = []
    t = 0.0
    import random as _rnd
    while t + min_len <= duration + 1e-6:
        seg = _rnd.uniform(min_len, max_len)
        if t + seg > duration:
            seg = max(0.0, duration - t)
        if seg < 0.5:
            break
        parts.append((t, seg))
        t += seg

    label = sanitize(base_name or 'personaje')
    lab_dir = os.path.join(clips_root, sanitize(label)); ensure_dir(lab_dir)
    crf = int(cfg.get('crf', 23)); preset = str(cfg.get('preset', 'veryfast'))
    vf = build_vf(cfg)

    # Fondo opcional
    bg_cfg = (cfg.get('bg') or {})
    bg_enabled = bool(bg_cfg.get('enabled'))
    bg_dir = (bg_cfg.get('dir') or '').strip()
    bg_mode = (bg_cfg.get('mode') or 'uno').lower()
    bg_files = []
    if bg_enabled and bg_dir and os.path.isdir(bg_dir):
        for fn in os.listdir(bg_dir):
            lower = fn.lower()
            if lower.endswith(('.jpg','.jpeg','.png','.webp','.bmp')):
                bg_files.append(os.path.join(bg_dir, fn))

    counters = {label: 0}; durations = {label: 0.0}; labels_all = [label]
    for i,(start,dur) in enumerate(parts, start=1):
        selected_bg = None
        n = _next_free_index(lab_dir, sanitize(base_name), width=4, ext='mp4')
        out_path = os.path.join(lab_dir, f"{sanitize(base_name)}_{n:04d}.mp4")
        try:
            export_clip(video_path, float(start), float(dur), out_path, vf, crf=crf, preset=preset, logger=logger, bg_path=selected_bg)
            counters[label] += 1; durations[label] += float(dur)
        except Exception as e:
            logger.error(f'Error al exportar clip {i}: {e}')

    total = sum(counters.values())
    logger.info(f'Exportados {total} clips (modo simple).')
    return {'total': total, 'by_label': counters, 'durations': durations, 'labels_all': labels_all, 'skipped_similar': 0}