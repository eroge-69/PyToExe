# -- coding: utf-8 --
"""
Détection de pastilles + angle d'orientation stabilisé
Caméra MindVision  |  OpenCV 4.x   |  ORB + RANSAC + lissage EMA
Streaming monochrome

Nouveautés (v2.1)
-----------------
1. *Angle stable* :
   • estimation robuste avec **RANSAC** (cv2.estimateAffinePartial2D).
   • **score + nombre d'inliers** pour filtrer les mauvaises estimations.
   • **lissage exponentiel** (EMA) frame-par-frame pour chaque pastille.
2. *Aide visuelle* :
   • un **mini cercle trigonométrique** (axes + flèche) est dessiné
     sur chaque centre de pastille pour contrôler l’orientation.
3. Références inchangées : images 0° et 90° toujours utilisées.
4. Aucune signature de fonction externe n'a été modifiée.
"""

import sys, threading, msvcrt, os
from ctypes import *
import cv2, numpy as np, csv, datetime, math
import argparse,tkinter as tk
from tkinter import ttk

# ───────────── 1. Constantes ─────────────
PixelType_Gvsp_Mono8        = 0x01080001
PixelType_Gvsp_RGB8_Packed  = 0x02180014
PixelType_Gvsp_BayerRG8     = 0x010c0005

script_dir = os.path.dirname(os.path.abspath(__file__))
os.makedirs(script_dir, exist_ok=True)

SCALE_MM_PER_PX = 0.0336
MIN_AREA = 10_000
MAX_AREA = 120_000
CIRC_MIN = 0.60
BLUR_K   = 5
TH_INV   = False
GRID_STEP_MM = 10
GRID_COLOR   = (200, 200, 200)
LABEL_COLOR  = (50, 50, 255)

REF_IMG0_PATH  = os.path.join(script_dir, "ref_pastille_0deg.png")
REF_IMG90_PATH = os.path.join(script_dir, "ref_pastille_90deg.png")
ORB_FEATURES   = 700  # un peu plus de keypoints pour la robustesse

sys.path.append(os.getenv('MVCAM_COMMON_RUNENV') + "/Samples/Python/MvImport")
from MvCameraControl_class import *

g_exit = False  # drapeau d'arrêt

# ───────────── 2. Références ORB ─────────────
orb_detector = cv2.ORB_create(ORB_FEATURES)
bf_matcher   = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

def _load_ref(path):
    if not os.path.exists(path):
        print(f"[!] Image de référence manquante : {path}")
        return None, None
    g = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    kp, des = orb_detector.detectAndCompute(g, None)
    if des is None or len(kp) < 6:
        print(f"[!] Référence {path} insuffisante en points ORB")
        return None, None
    return (kp, des), g.shape

REF0_FEATS, REF0_SHAPE   = _load_ref(REF_IMG0_PATH)
REF90_FEATS, REF90_SHAPE = _load_ref(REF_IMG90_PATH)

# ───────────── 3. Utilitaire : mini cercle trigonométrique ─────────────
def draw_trig_circle(img, center, base_r, ang_deg, r_factor=1.1):
    """
    Dessine un petit cercle + axes + flèche d’angle a `center`
    - img      : image BGR sur laquelle dessiner
    - center   : tuple (cx, cy)
    - base_r   : rayon de la pastille (px) pour l’échelle
    - ang_deg  : angle lissé (°) ou None
    - r_factor : facteur de taille du petit cercle
    """
    cx, cy = center
    r = max(int(base_r * r_factor), 12)   # taille mini pour visibilité
    axis_col  = (200, 255, 255)           # axes cardinaux
    arrow_col = (0,   64, 255)            # flèche d’orientation

    # Cercle extérieur
    cv2.circle(img, (cx, cy), r, axis_col, 1, cv2.LINE_AA)

    # Axes 0° / 90° / 180° / 270°
    for dx, dy in ((1,0), (-1,0), (0,-1), (0,1)):
        cv2.line(img, (cx, cy),
                 (cx + dx*r, cy + dy*r),
                 axis_col, 1, cv2.LINE_AA)

    # Flèche pointant vers l’angle mesuré
    if ang_deg is not None:
        theta = -math.radians(ang_deg)                 # Y inversé
        ex = int(cx + r*math.cos(theta))
        ey = int(cy + r*math.sin(theta))
        cv2.arrowedLine(img, (cx, cy), (ex, ey),
                        arrow_col, 1, tipLength=0.25, line_type=cv2.LINE_AA)

# ───────────── 4. Estimation d'angle robuste ─────────────
def _angle_ransac(ref_feats, roi):
    kp_ref, des_ref = ref_feats
    kp_roi, des_roi = orb_detector.detectAndCompute(roi, None)
    if des_roi is None or len(kp_roi) < 6:
        return None, None, 0  # angle, score, inliers
    matches = bf_matcher.match(des_ref, des_roi)
    if len(matches) < 6:
        return None, None, 0
    matches = sorted(matches, key=lambda m: m.distance)
    keep = matches[:max(6, int(len(matches)*0.4))]      # top 40 %
    pts_ref = np.float32([kp_ref[m.queryIdx].pt for m in keep])
    pts_roi = np.float32([kp_roi[m.trainIdx].pt for m in keep])
    M, mask = cv2.estimateAffinePartial2D(
        pts_ref, pts_roi,
        method=cv2.RANSAC,
        ransacReprojThreshold=3.0,
        maxIters=4000,
        confidence=0.995
    )
    if M is None:
        return None, None, 0
    inliers = int(mask.sum()) if mask is not None else 0
    angle = math.degrees(math.atan2(M[0,1], M[0,0]))
    score = np.mean([keep[i].distance for i in range(len(keep)) if mask[i]]) \
            if mask is not None else 999
    return angle, score, inliers

def _norm_0_90(a):
    a = a % 180
    return abs(180 - a) if a > 90 else abs(a)

def compute_angle(roi_gray):
    """Retourne angle [0,90] ou None"""
    best = {'angle': None, 'score': 1e9, 'inliers': 0}
    for ref_feats, ref_shape, offset in [
        (REF0_FEATS,  REF0_SHAPE,  0),
        (REF90_FEATS, REF90_SHAPE, 90)]:
        if ref_feats is None:
            continue
        roi_r = cv2.resize(roi_gray, (ref_shape[1], ref_shape[0]))
        ang_raw, score, inliers = _angle_ransac(ref_feats, roi_r)
        if ang_raw is None or inliers < 6:
            continue
        ang = _norm_0_90(ang_raw - offset)
        if (score < best['score'] and inliers >= best['inliers']):
            best.update(angle=ang, score=score, inliers=inliers)
    return best['angle']

# ───────────── 5. Détection pastilles avec lissage EMA ─────────────
angle_hist = {}    # clef (approx cx,cy) → angle lissé
EMA_ALPHA  = 0.25  # 0<α≤1, plus petit = plus lisse

def _smooth_angle(key, ang):
    if ang is None:
        return None
    prev = angle_hist.get(key, ang)
    blended = prev + EMA_ALPHA*(ang - prev)
    angle_hist[key] = blended
    return blended

def detect_pills(gray, bgr):
    clahe = cv2.createCLAHE(2.0, (8, 8))
    g_eq  = cv2.GaussianBlur(clahe.apply(gray), (BLUR_K, BLUR_K), 0)
    mask = cv2.adaptiveThreshold(g_eq, 255,
                                 cv2.ADAPTIVE_THRESH_MEAN_C,
                                 cv2.THRESH_BINARY_INV if not TH_INV else cv2.THRESH_BINARY,
                                 11, 2)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  k, 2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k, 2)
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    centers, infos_mm, angles = [], [], []
    for c in cnts:
        area = cv2.contourArea(c)
        if not MIN_AREA < area < MAX_AREA:
            continue
        peri = cv2.arcLength(c, True)
        if peri == 0:
            continue
        circ = 4*np.pi*area/(peri*peri)
        if circ < CIRC_MIN:
            continue
        (x, y), r = cv2.minEnclosingCircle(c)
        cx, cy, r_int = int(x), int(y), int(r)
        centers.append((cx, cy))
        diam_px = 2*r
        x_mm, y_mm = x*SCALE_MM_PER_PX, y*SCALE_MM_PER_PX
        diam_mm   = diam_px*SCALE_MM_PER_PX
        infos_mm.append((x_mm, y_mm, diam_mm))
        pad = int(r*1.3)
        x0, y0 = max(cx-pad, 0), max(cy-pad, 0)
        x1, y1 = min(cx+pad, gray.shape[1]-1), min(cy+pad, gray.shape[0]-1)
        roi = gray[y0:y1, x0:x1]
        ang_raw = compute_angle(roi) if roi.size else None
        key = (cx//20, cy//20)          # quantisation pour suivi
        ang = _smooth_angle(key, ang_raw)
        angles.append(ang)

        # Dessins
        cv2.circle(bgr, (cx, cy), r_int, (0,255,0), 2)
        cv2.circle(bgr, (cx, cy), 3, (0,0,255), -1)
        label = f"X:{x_mm:.1f} Y:{y_mm:.1f} D:{diam_mm:.1f}mm"
        if ang is not None:
            label += f" A:{ang:+.1f}deg"
        cv2.putText(bgr, label, (cx-90, cy+r_int+25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 1, cv2.LINE_AA)

        # Mini cercle trigonométrique
        draw_trig_circle(bgr, (cx, cy), r_int, ang)

    return len(centers), centers, bgr, infos_mm, angles


# ------------------------tableau -------------------
def setup_table():
    root = tk.Tk()
    root.title('Comptage des pastilles')
    tree = ttk.Treeview(root, columns=('idx', 'diam'), show='headings',
                        height=10)
    tree.heading('idx', text='N°')
    tree.heading('diam', text='Diamètre (mm)')
    tree.column('idx', width=60, anchor='center')
    tree.column('diam', width=120, anchor='center')
    tree.pack(fill='both', expand=True)
    # Ajout d'un label total
    total_var = tk.StringVar(value='Total : 0')
    lbl_total = ttk.Label(root, textvariable=total_var)
    lbl_total.pack(pady=4)
    return root, tree, total_var

def update_table(tree, total_var, diam_mm_list ):
    # Efface contenu
    for row in tree.get_children():
        tree.delete(row)
    for i, d in enumerate(diam_mm_list , start=1):
        tree.insert('', 'end', values=(i, f'{d:.1f}'))
    total_var.set(f'Total : {len(diam_mm_list )}')


# ───────────── 6. Grille de repères ─────────────
def draw_grid_axes(img, scale, step_mm=10):
    h, w = img.shape[:2]
    step_px = int(step_mm/scale)
    for x in range(0, w, step_px):
        cv2.line(img, (x,0), (x,h), GRID_COLOR, 1)
        cv2.putText(img, f"{x*scale:.0f}", (x+2, 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, LABEL_COLOR, 2)
    for y in range(0, h, step_px):
        cv2.line(img, (0,y), (w,y), GRID_COLOR, 1)
        cv2.putText(img, f"{y*scale:.0f}", (2, y-2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, LABEL_COLOR, 2)
    return img

# ───────────── 7. Thread capture ─────────────
def grab_loop(cam):
    global g_exit
    frm = MV_FRAME_OUT(); memset(byref(frm), 0, sizeof(frm))
    csv_path = os.path.join(script_dir, f"pills_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    with open(csv_path, "w", newline="") as fcsv:
        writer = csv.writer(fcsv, delimiter=";")
        writer.writerow(["Frame","Index","X_mm","Y_mm","Diam_mm","Angle_deg"])
        root, tree, total_var = setup_table()

        while not g_exit:
            ret = cam.MV_CC_GetImageBuffer(frm, 1000)
            if frm.pBufAddr and ret == 0:
                w,h = frm.stFrameInfo.nWidth, frm.stFrameInfo.nHeight
                fnum = frm.stFrameInfo.nFrameNum
                ptype= frm.stFrameInfo.enPixelType
                buf = cast(frm.pBufAddr, POINTER(c_ubyte*frm.stFrameInfo.nFrameLen)).contents
                arr = np.frombuffer(buf, dtype=np.uint8)

                if ptype==PixelType_Gvsp_Mono8:
                    gray = arr.reshape((h,w))
                elif ptype==PixelType_Gvsp_RGB8_Packed:
                    rgb  = arr.reshape((h,w,3))
                    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
                elif ptype==PixelType_Gvsp_BayerRG8:
                    raw  = arr.reshape((h,w))
                    bgr  = cv2.cvtColor(raw, cv2.COLOR_BAYER_RG2BGR)
                    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
                else:
                    print(f"[!] PixelType non géré : {ptype}")
                    cam.MV_CC_FreeImageBuffer(frm)
                    continue

                base = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
                n, centers, out, infos, angs = detect_pills(gray, base)
                cv2.putText(out, f"Pastilles detectees : {n}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
                out = draw_grid_axes(out, SCALE_MM_PER_PX, GRID_STEP_MM)
                cv2.imshow("MindVision Live", out)

                diam_mm_list = [d for (_, _, d) in infos]
                update_table(tree, total_var, diam_mm_list)
                root.update_idletasks()
                root.update()

                print(f"Frame {fnum:05d} • pastilles = {n}")
                for idx, ((x_mm,y_mm,d_mm), ang) in enumerate(zip(infos, angs),1):
                    a_str = "None" if ang is None else f"{ang:+.1f}°"
                    print(f"  #{idx}  X={x_mm:.2f}  Y={y_mm:.2f}  D={d_mm:.2f} mm  A={a_str}")
                    writer.writerow([fnum, idx, f"{x_mm:.3f}", f"{y_mm:.3f}",
                                     f"{d_mm:.3f}", a_str])
                cam.MV_CC_FreeImageBuffer(frm)
            else:
                print(f"no data 0x{ret:x}")

    cv2.destroyAllWindows()
    root.destroy()


# -- coding: utf-8 --
"""
Détection de pastilles + angle d'orientation stabilisé
Caméra MindVision  |  OpenCV 4.x   |  ORB + RANSAC + lissage EMA
Streaming monochrome

Nouveautés (v2.1)
-----------------
1. *Angle stable* :
   • estimation robuste avec **RANSAC** (cv2.estimateAffinePartial2D).
   • **score + nombre d'inliers** pour filtrer les mauvaises estimations.
   • **lissage exponentiel** (EMA) frame-par-frame pour chaque pastille.
2. *Aide visuelle* :
   • un **mini cercle trigonométrique** (axes + flèche) est dessiné
     sur chaque centre de pastille pour contrôler l’orientation.
3. Références inchangées : images 0° et 90° toujours utilisées.
4. Aucune signature de fonction externe n'a été modifiée.
"""

import sys, threading, msvcrt, os
from ctypes import *
import cv2, numpy as np, csv, datetime, math
import argparse,tkinter as tk
from tkinter import ttk

# ───────────── 1. Constantes ─────────────
PixelType_Gvsp_Mono8        = 0x01080001
PixelType_Gvsp_RGB8_Packed  = 0x02180014
PixelType_Gvsp_BayerRG8     = 0x010c0005

script_dir = os.path.dirname(os.path.abspath(__file__))
os.makedirs(script_dir, exist_ok=True)

SCALE_MM_PER_PX = 0.0336
MIN_AREA = 10_000
MAX_AREA = 120_000
CIRC_MIN = 0.60
BLUR_K   = 5
TH_INV   = False
GRID_STEP_MM = 10
GRID_COLOR   = (200, 200, 200)
LABEL_COLOR  = (50, 50, 255)

REF_IMG0_PATH  = os.path.join(script_dir, "ref_pastille_0deg.png")
REF_IMG90_PATH = os.path.join(script_dir, "ref_pastille_90deg.png")
ORB_FEATURES   = 700  # un peu plus de keypoints pour la robustesse

sys.path.append(os.getenv('MVCAM_COMMON_RUNENV') + "/Samples/Python/MvImport")
from MvCameraControl_class import *

g_exit = False  # drapeau d'arrêt

# ───────────── 2. Références ORB ─────────────
orb_detector = cv2.ORB_create(ORB_FEATURES)
bf_matcher   = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

def _load_ref(path):
    if not os.path.exists(path):
        print(f"[!] Image de référence manquante : {path}")
        return None, None
    g = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    kp, des = orb_detector.detectAndCompute(g, None)
    if des is None or len(kp) < 6:
        print(f"[!] Référence {path} insuffisante en points ORB")
        return None, None
    return (kp, des), g.shape

REF0_FEATS, REF0_SHAPE   = _load_ref(REF_IMG0_PATH)
REF90_FEATS, REF90_SHAPE = _load_ref(REF_IMG90_PATH)

# ───────────── 3. Utilitaire : mini cercle trigonométrique ─────────────
def draw_trig_circle(img, center, base_r, ang_deg, r_factor=1.1):
    """
    Dessine un petit cercle + axes + flèche d’angle a `center`
    - img      : image BGR sur laquelle dessiner
    - center   : tuple (cx, cy)
    - base_r   : rayon de la pastille (px) pour l’échelle
    - ang_deg  : angle lissé (°) ou None
    - r_factor : facteur de taille du petit cercle
    """
    cx, cy = center
    r = max(int(base_r * r_factor), 12)   # taille mini pour visibilité
    axis_col  = (200, 255, 255)           # axes cardinaux
    arrow_col = (0,   64, 255)            # flèche d’orientation

    # Cercle extérieur
    cv2.circle(img, (cx, cy), r, axis_col, 1, cv2.LINE_AA)

    # Axes 0° / 90° / 180° / 270°
    for dx, dy in ((1,0), (-1,0), (0,-1), (0,1)):
        cv2.line(img, (cx, cy),
                 (cx + dx*r, cy + dy*r),
                 axis_col, 1, cv2.LINE_AA)

    # Flèche pointant vers l’angle mesuré
    if ang_deg is not None:
        theta = -math.radians(ang_deg)                 # Y inversé
        ex = int(cx + r*math.cos(theta))
        ey = int(cy + r*math.sin(theta))
        cv2.arrowedLine(img, (cx, cy), (ex, ey),
                        arrow_col, 1, tipLength=0.25, line_type=cv2.LINE_AA)

# ───────────── 4. Estimation d'angle robuste ─────────────
def _angle_ransac(ref_feats, roi):
    kp_ref, des_ref = ref_feats
    kp_roi, des_roi = orb_detector.detectAndCompute(roi, None)
    if des_roi is None or len(kp_roi) < 6:
        return None, None, 0  # angle, score, inliers
    matches = bf_matcher.match(des_ref, des_roi)
    if len(matches) < 6:
        return None, None, 0
    matches = sorted(matches, key=lambda m: m.distance)
    keep = matches[:max(6, int(len(matches)*0.4))]      # top 40 %
    pts_ref = np.float32([kp_ref[m.queryIdx].pt for m in keep])
    pts_roi = np.float32([kp_roi[m.trainIdx].pt for m in keep])
    M, mask = cv2.estimateAffinePartial2D(
        pts_ref, pts_roi,
        method=cv2.RANSAC,
        ransacReprojThreshold=3.0,
        maxIters=4000,
        confidence=0.995
    )
    if M is None:
        return None, None, 0
    inliers = int(mask.sum()) if mask is not None else 0
    angle = math.degrees(math.atan2(M[0,1], M[0,0]))
    score = np.mean([keep[i].distance for i in range(len(keep)) if mask[i]]) \
            if mask is not None else 999
    return angle, score, inliers

def _norm_0_90(a):
    a = a % 180
    return abs(180 - a) if a > 90 else abs(a)

def compute_angle(roi_gray):
    """Retourne angle [0,90] ou None"""
    best = {'angle': None, 'score': 1e9, 'inliers': 0}
    for ref_feats, ref_shape, offset in [
        (REF0_FEATS,  REF0_SHAPE,  0),
        (REF90_FEATS, REF90_SHAPE, 90)]:
        if ref_feats is None:
            continue
        roi_r = cv2.resize(roi_gray, (ref_shape[1], ref_shape[0]))
        ang_raw, score, inliers = _angle_ransac(ref_feats, roi_r)
        if ang_raw is None or inliers < 6:
            continue
        ang = _norm_0_90(ang_raw - offset)
        if (score < best['score'] and inliers >= best['inliers']):
            best.update(angle=ang, score=score, inliers=inliers)
    return best['angle']

# ───────────── 5. Détection pastilles avec lissage EMA ─────────────
angle_hist = {}    # clef (approx cx,cy) → angle lissé
EMA_ALPHA  = 0.25  # 0<α≤1, plus petit = plus lisse

def _smooth_angle(key, ang):
    if ang is None:
        return None
    prev = angle_hist.get(key, ang)
    blended = prev + EMA_ALPHA*(ang - prev)
    angle_hist[key] = blended
    return blended

def detect_pills(gray, bgr):
    clahe = cv2.createCLAHE(2.0, (8, 8))
    g_eq  = cv2.GaussianBlur(clahe.apply(gray), (BLUR_K, BLUR_K), 0)
    mask = cv2.adaptiveThreshold(g_eq, 255,
                                 cv2.ADAPTIVE_THRESH_MEAN_C,
                                 cv2.THRESH_BINARY_INV if not TH_INV else cv2.THRESH_BINARY,
                                 11, 2)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  k, 2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k, 2)
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    centers, infos_mm, angles = [], [], []
    for c in cnts:
        area = cv2.contourArea(c)
        if not MIN_AREA < area < MAX_AREA:
            continue
        peri = cv2.arcLength(c, True)
        if peri == 0:
            continue
        circ = 4*np.pi*area/(peri*peri)
        if circ < CIRC_MIN:
            continue
        (x, y), r = cv2.minEnclosingCircle(c)
        cx, cy, r_int = int(x), int(y), int(r)
        centers.append((cx, cy))
        diam_px = 2*r
        x_mm, y_mm = x*SCALE_MM_PER_PX, y*SCALE_MM_PER_PX
        diam_mm   = diam_px*SCALE_MM_PER_PX
        infos_mm.append((x_mm, y_mm, diam_mm))
        pad = int(r*1.3)
        x0, y0 = max(cx-pad, 0), max(cy-pad, 0)
        x1, y1 = min(cx+pad, gray.shape[1]-1), min(cy+pad, gray.shape[0]-1)
        roi = gray[y0:y1, x0:x1]
        ang_raw = compute_angle(roi) if roi.size else None
        key = (cx//20, cy//20)          # quantisation pour suivi
        ang = _smooth_angle(key, ang_raw)
        angles.append(ang)

        # Dessins
        cv2.circle(bgr, (cx, cy), r_int, (0,255,0), 2)
        cv2.circle(bgr, (cx, cy), 3, (0,0,255), -1)
        label = f"X:{x_mm:.1f} Y:{y_mm:.1f} D:{diam_mm:.1f}mm"
        if ang is not None:
            label += f" A:{ang:+.1f}deg"
        cv2.putText(bgr, label, (cx-90, cy+r_int+25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 1, cv2.LINE_AA)

        # Mini cercle trigonométrique
        draw_trig_circle(bgr, (cx, cy), r_int, ang)

    return len(centers), centers, bgr, infos_mm, angles


# ------------------------tableau -------------------
def setup_table():
    root = tk.Tk()
    root.title('Comptage des pastilles')
    tree = ttk.Treeview(root, columns=('idx', 'diam'), show='headings',
                        height=10)
    tree.heading('idx', text='N°')
    tree.heading('diam', text='Diamètre (mm)')
    tree.column('idx', width=60, anchor='center')
    tree.column('diam', width=120, anchor='center')
    tree.pack(fill='both', expand=True)
    # Ajout d'un label total
    total_var = tk.StringVar(value='Total : 0')
    lbl_total = ttk.Label(root, textvariable=total_var)
    lbl_total.pack(pady=4)
    return root, tree, total_var

def update_table(tree, total_var, diam_mm_list ):
    # Efface contenu
    for row in tree.get_children():
        tree.delete(row)
    for i, d in enumerate(diam_mm_list , start=1):
        tree.insert('', 'end', values=(i, f'{d:.1f}'))
    total_var.set(f'Total : {len(diam_mm_list )}')


# ───────────── 6. Grille de repères ─────────────
def draw_grid_axes(img, scale, step_mm=10):
    h, w = img.shape[:2]
    step_px = int(step_mm/scale)
    for x in range(0, w, step_px):
        cv2.line(img, (x,0), (x,h), GRID_COLOR, 1)
        cv2.putText(img, f"{x*scale:.0f}", (x+2, 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, LABEL_COLOR, 2)
    for y in range(0, h, step_px):
        cv2.line(img, (0,y), (w,y), GRID_COLOR, 1)
        cv2.putText(img, f"{y*scale:.0f}", (2, y-2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, LABEL_COLOR, 2)
    return img

# ───────────── 7. Thread capture ─────────────
def grab_loop(cam):
    global g_exit
    frm = MV_FRAME_OUT(); memset(byref(frm), 0, sizeof(frm))
    csv_path = os.path.join(script_dir, f"pills_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    with open(csv_path, "w", newline="") as fcsv:
        writer = csv.writer(fcsv, delimiter=";")
        writer.writerow(["Frame","Index","X_mm","Y_mm","Diam_mm","Angle_deg"])
        root, tree, total_var = setup_table()

        while not g_exit:
            ret = cam.MV_CC_GetImageBuffer(frm, 1000)
            if frm.pBufAddr and ret == 0:
                w,h = frm.stFrameInfo.nWidth, frm.stFrameInfo.nHeight
                fnum = frm.stFrameInfo.nFrameNum
                ptype= frm.stFrameInfo.enPixelType
                buf = cast(frm.pBufAddr, POINTER(c_ubyte*frm.stFrameInfo.nFrameLen)).contents
                arr = np.frombuffer(buf, dtype=np.uint8)

                if ptype==PixelType_Gvsp_Mono8:
                    gray = arr.reshape((h,w))
                elif ptype==PixelType_Gvsp_RGB8_Packed:
                    rgb  = arr.reshape((h,w,3))
                    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
                elif ptype==PixelType_Gvsp_BayerRG8:
                    raw  = arr.reshape((h,w))
                    bgr  = cv2.cvtColor(raw, cv2.COLOR_BAYER_RG2BGR)
                    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
                else:
                    print(f"[!] PixelType non géré : {ptype}")
                    cam.MV_CC_FreeImageBuffer(frm)
                    continue

                base = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
                n, centers, out, infos, angs = detect_pills(gray, base)
                cv2.putText(out, f"Pastilles detectees : {n}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
                out = draw_grid_axes(out, SCALE_MM_PER_PX, GRID_STEP_MM)
                cv2.imshow("MindVision Live", out)

                diam_mm_list = [d for (_, _, d) in infos]
                update_table(tree, total_var, diam_mm_list)
                root.update_idletasks()
                root.update()

                print(f"Frame {fnum:05d} • pastilles = {n}")
                for idx, ((x_mm,y_mm,d_mm), ang) in enumerate(zip(infos, angs),1):
                    a_str = "None" if ang is None else f"{ang:+.1f}°"
                    print(f"  #{idx}  X={x_mm:.2f}  Y={y_mm:.2f}  D={d_mm:.2f} mm  A={a_str}")
                    writer.writerow([fnum, idx, f"{x_mm:.3f}", f"{y_mm:.3f}",
                                     f"{d_mm:.3f}", a_str])
                cam.MV_CC_FreeImageBuffer(frm)
            else:
                print(f"no data 0x{ret:x}")

    cv2.destroyAllWindows()
    root.destroy()


# ───────────── 8. Main ─────────────
if __name__ == "__main__":
    MvCamera.MV_CC_Initialize()
    devs = MV_CC_DEVICE_INFO_LIST()
    tlay = (MV_GIGE_DEVICE | MV_USB_DEVICE | MV_GENTL_CAMERALINK_DEVICE |
            MV_GENTL_CXP_DEVICE | MV_GENTL_XOF_DEVICE)
    if MvCamera.MV_CC_EnumDevices(tlay, devs)!=0 or devs.nDeviceNum==0:
        sys.exit("Aucune caméra détectée")
    for i in range(devs.nDeviceNum):
        inf = cast(devs.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
        if inf.nTLayerType == MV_GIGE_DEVICE:
            name = "".join(chr(c) for c in inf.SpecialInfo.stGigEInfo.chModelName if c)
            ip = inf.SpecialInfo.stGigEInfo.nCurrentIp
            print(f"[{i}] GIGE {name} {ip>>24&255}.{ip>>16&255}.{ip>>8&255}.{ip&255}")
        else:
            name = "".join(chr(c) for c in inf.SpecialInfo.stUsb3VInfo.chModelName if c)
            sn   = "".join(chr(c) for c in inf.SpecialInfo.stUsb3VInfo.chSerialNumber if c)
            print(f"[{i}] USB3 {name} SN:{sn}")
    idx = 0
    cam = MvCamera()
    if cam.MV_CC_CreateHandle(cast(devs.pDeviceInfo[idx], POINTER(MV_CC_DEVICE_INFO)).contents) or \
       cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0):
        sys.exit("Erreur ouverture caméra")
    inf = cast(devs.pDeviceInfo[idx], POINTER(MV_CC_DEVICE_INFO)).contents
    if inf.nTLayerType == MV_GIGE_DEVICE:
        pk = cam.MV_CC_GetOptimalPacketSize()
        if pk > 0:
            cam.MV_CC_SetIntValue("GevSCPSPacketSize", pk)
    cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
    if cam.MV_CC_StartGrabbing():
        sys.exit("StartGrabbing failed")
    thr = threading.Thread(target=grab_loop, args=(cam,), daemon=True)
    thr.start()
    print('  Appuie sur une touche console OU "q" dans la fenêtre vidéo pour stopper…')
    msvcrt.getch()
    g_exit = True
    thr.join()
    cam.MV_CC_StopGrabbing()
    cam.MV_CC_CloseDevice()
    cam.MV_CC_DestroyHandle()
    MvCamera.MV_CC_Finalize()
    cv2.destroyAllWindows()
    print("Capture terminée")
