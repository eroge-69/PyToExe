# main.py
# Täydellinen Scolia-tyylinen automaattinen Darts 501 -järjestelmä (kaksikamera)
# Kaikki tekstit suomeksi. HD-ikkuna (1920x1080). Ei terminaalia.
# Riippuvuudet: opencv-python, numpy, pygame

import cv2
import numpy as np
import pygame
import threading
import time
import math
import csv
from collections import deque

# -----------------------
# Perusasetukset
# -----------------------
WINDOW_W, WINDOW_H = 1920, 1080
CAM_PREVIEW_W, CAM_PREVIEW_H = 320, 240  # smaller preview-koko per kamera
FPS = 30

# Dartboard geometria (proportion of radius)
BULL_INNER_R = 0.05
BULL_OUTER_R = 0.12
TRIPLE_IN_R = 0.45
TRIPLE_OUT_R = 0.52
DOUBLE_IN_R = 0.85
DOUBLE_OUT_R = 0.95

SECTORS = [6,13,4,18,1,20,5,12,9,14,11,8,16,7,19,3,17,2,15,10]  # starts at 0deg (+x)

# Colors
COLOR_BG = (12,12,12)
COLOR_PANEL = (28,28,28)
COLOR_ACCENT = (200,20,20)
COLOR_TEXT = (235,235,235)
COLOR_WARN = (255,100,100)

# Detection params
DIFF_HISTORY = 4
MIN_BLOB_AREA = 80
MAX_BLOB_AREA = 4000
DETECTION_COOLDOWN = 0.6  # seconds between accepting hits

# UI layout
LEFT_MARGIN = 40
TOP_MARGIN = 40

# -----------------------
# Kamera-thread
# -----------------------
class CameraThread(threading.Thread):
    def __init__(self, cam_idx=0, w=CAM_PREVIEW_W, h=CAM_PREVIEW_H):
        super().__init__()
        self.cam_idx = cam_idx
        self.w = w
        self.h = h
        self.cap = None
        self.frame = None
        self.lock = threading.Lock()
        self.running = False

    def run(self):
        self.cap = cv2.VideoCapture(self.cam_idx, cv2.CAP_DSHOW if hasattr(cv2, 'CAP_DSHOW') else 0)
        if not self.cap.isOpened():
            # try without DSHOW flag
            self.cap = cv2.VideoCapture(self.cam_idx)
        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.w)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.h)
        self.running = True
        while self.running:
            if self.cap is None:
                time.sleep(0.1)
                continue
            ret, f = self.cap.read()
            if not ret:
                time.sleep(0.05)
                continue
            with self.lock:
                # mirror for user-friendliness
                self.frame = cv2.flip(f, 1)
            time.sleep(0)  # yield

    def stop(self):
        self.running = False
        self.join(timeout=1.0)
        if self.cap is not None:
            try: self.cap.release()
            except: pass

    def get_frame(self):
        with self.lock:
            if self.frame is None:
                return None
            return self.frame.copy()

# -----------------------
# Tikka-tunnistin
# -----------------------
class Detector:
    def __init__(self):
        self.hist = deque(maxlen=DIFF_HISTORY)
        self.last_hits = []
        # color mask thresholds (HSV) tuned for bright setups with orange/wood dart tips or white highlights
        # We will combine color mask + frame-diff for robust detection
        # These are conservative defaults (may need light tweaking)
        self.hsv_low = np.array([0, 20, 120])   # low value: includes warm colors / bright dots
        self.hsv_high = np.array([180, 255, 255])

    def update(self, frame):
        # frame BGR
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.hist.append(gray)
        hits = []

        # frame-diff detection
        if len(self.hist) >= 2:
            bg = np.median(np.stack(list(self.hist), axis=0), axis=0).astype(np.uint8)
            diff = cv2.absdiff(gray, bg)
            _, th = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
            # morphological
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
            th = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel, iterations=1)
            th = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel, iterations=1)
        else:
            th = np.zeros_like(gray)

        # color mask (to capture bright tip reflection)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.hsv_low, self.hsv_high)
        # combine mask and th
        comb = cv2.bitwise_and(mask, th)

        contours, _ = cv2.findContours(comb, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < MIN_BLOB_AREA or area > MAX_BLOB_AREA:
                continue
            M = cv2.moments(cnt)
            if M['m00'] == 0:
                continue
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            hits.append((cx, cy, area))
        self.last_hits = hits
        return hits

# -----------------------
# Homography / taulun suoristus
# -----------------------
def auto_find_board(frame):
    # Returns (warped, M_inv) where warped is square crop of board (size 800x800) and M_inv maps from warped->orig coords
    # If not found, returns (None, None)
    h, w = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7,7), 0)
    _, th = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    # find contours
    cnts, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return None, None
    cnt = max(cnts, key=cv2.contourArea)
    area = cv2.contourArea(cnt)
    if area < (w*h)*0.01:
        return None, None
    # approximate polygon
    peri = cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, 0.02*peri, True)
    if len(approx) >= 4:
        # find bounding quad by convex hull then minAreaRect->box
        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)
        box = box.astype(np.intp)

        # order points (tl,tr,br,bl)
        def order_pts(pts):
            pts = pts.reshape(4,2)
            s = pts.sum(axis=1)
            diff = np.diff(pts, axis=1)
            tl = pts[np.argmin(s)]
            br = pts[np.argmax(s)]
            tr = pts[np.argmin(diff)]
            bl = pts[np.argmax(diff)]
            return np.array([tl,tr,br,bl], dtype='float32')
        src = order_pts(box)
        size = 800
        dst = np.array([[0,0],[size-1,0],[size-1,size-1],[0,size-1]], dtype='float32')
        M = cv2.getPerspectiveTransform(src, dst)
        warped = cv2.warpPerspective(frame, M, (size, size))
        M_inv = cv2.getPerspectiveTransform(dst, src)  # map warped->orig
        return warped, M_inv
    else:
        return None, None

# -----------------------
# Pisteen laskenta laudalta (oletetaan square warped)
# -----------------------
def get_score_from_warped_point(px, py, warped_size=800):
    # px,py are coordinates in warped image (0..size-1)
    cx = warped_size/2
    cy = warped_size/2
    dx = px - cx
    dy = cy - py  # invert y to standard coords
    r = math.hypot(dx, dy) / (warped_size/2)  # normalized [0..]
    # bull/outer
    if r <= BULL_INNER_R:
        return 50, 'DB'
    if r <= BULL_OUTER_R:
        return 25, 'SB'
    # sector angle
    angle = (math.degrees(math.atan2(dy, dx)) + 360) % 360
    idx = int((angle + 9) // 18) % 20
    base = SECTORS[idx]
    if TRIPLE_IN_R <= r <= TRIPLE_OUT_R:
        return base*3, 'T'
    if DOUBLE_IN_R <= r <= DOUBLE_OUT_R:
        return base*2, 'D'
    return base, 'S'

# -----------------------
# Fusion / hit selection
# -----------------------
def fuse_hits(left_hits, right_hits, left_Minv=None, right_Minv=None):
    """
    left_hits: list of (cx,cy,area) in left raw camera coords
    right_hits: same for right
    Minv: mapping from warped->orig coords for each camera, optional
    Returns list of fused hits in unified warped coordinates (x,y,val,label)
    Strategy: map camera hits to their warped board coords (if warps exist), else ignore that camera.
    Then cluster by proximity and average.
    """
    mapped = []
    # left_hits and right_hits are tuples (cx,cy,area,warped_px,warped_py,val,label)
    # But we will assume incoming lists already mapped to warped coords (px,py,val,label) if upstream did mapping.
    # To be robust, accept both formats
    for h in left_hits:
        if len(h) >= 5:
            mapped.append(h[:5])
        # else skip
    for h in right_hits:
        if len(h) >= 5:
            mapped.append(h[:5])
    if not mapped:
        return []
    # cluster by proximity (distance threshold)
    used = [False]*len(mapped)
    clusters = []
    for i, m in enumerate(mapped):
        if used[i]: continue
        x0,y0,val0,label0 = m[0],m[1],m[2],m[3]
        xs = [x0]; ys=[y0]; vals=[val0]; labs=[label0]
        used[i] = True
        for j in range(i+1, len(mapped)):
            if used[j]: continue
            x1,y1,val1,label1 = mapped[j][0],mapped[j][1],mapped[j][2],mapped[j][3]
            if math.hypot(x1-x0, y1-y0) < 40:  # pixels in warped space
                xs.append(x1); ys.append(y1); vals.append(val1); labs.append(label1)
                used[j] = True
        avgx = sum(xs)/len(xs); avgy = sum(ys)/len(ys)
        # pick highest value among cluster
        best_idx = int(np.argmax(vals))
        best_val = vals[best_idx]
        best_label = labs[best_idx]
        clusters.append((avgx, avgy, best_val, best_label))
    # sort by value descending (prefer high scoring)
    clusters.sort(key=lambda t: t[2], reverse=True)
    return clusters

# -----------------------
# Pygame UI components
# -----------------------
pygame.font.init()
FONT_SMALL = pygame.font.SysFont('Arial', 18)
FONT_MED = pygame.font.SysFont('Arial', 26)
FONT_LG = pygame.font.SysFont('Arial', 34)
FONT_XL = pygame.font.SysFont('Arial', 48)

def draw_text(surface, text, pos, font=FONT_MED, color=COLOR_TEXT):
    surf = font.render(str(text), True, color)
    surface.blit(surf, pos)

class Button:
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.hover = False
    def draw(self, surf):
        color = COLOR_PANEL if not self.hover else (50,50,50)
        pygame.draw.rect(surf, color, self.rect, border_radius=8)
        draw_text(surf, self.text, (self.rect.x+10, self.rect.y+8), FONT_SMALL)
    def handle(self, ev):
        if ev.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(ev.pos)
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.rect.collidepoint(ev.pos):
                return True
        return False

class InputBox:
    def __init__(self, rect, text=''):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.active = False
    def draw(self, surf):
        color = (60,60,60) if self.active else (40,40,40)
        pygame.draw.rect(surf, color, self.rect, border_radius=6)
        draw_text(surf, self.text, (self.rect.x+6, self.rect.y+6), FONT_SMALL)
    def handle(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            self.active = self.rect.collidepoint(ev.pos)
            return
        if self.active and ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif ev.key == pygame.K_RETURN:
                self.active = False
            else:
                ch = ev.unicode
                if ch:
                    self.text += ch

# -----------------------
# Application / state
# -----------------------
class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption("eDarts")
        self.clock = pygame.time.Clock()

        # cameras
        self.left_cam_idx = 0
        self.right_cam_idx = 1
        self.left_cam = CameraThread(self.left_cam_idx)
        self.right_cam = CameraThread(self.right_cam_idx)
        self.left_cam.start()
        self.right_cam.start()

        self.det_left = Detector()
        self.det_right = Detector()

        # calibration/wraps
        self.left_warp = None  # (warped_img, M_inv)
        self.right_warp = None

        # UI / registration
        self.mode = 'register'  # 'register' or 'playing'
        self.player_count = 2
        self.name_boxes = [InputBox((60, 140 + i*66, 300, 40), text=f'P{i+1}') for i in range(4)]
        self.start_boxes = [InputBox((380, 140 + i*66, 120, 40), text='501' if i<2 else '') for i in range(4)]
        self.count_buttons = [Button((60 + i*140, 90, 120, 36), f"{v} pelaajaa") for i,v in enumerate([2,3,4])]
        self.btn_start_game = Button((560, 420, 180, 44), "Aloita peli")
        self.info = ''

        # playing UI
        self.btn_calibrate = Button((40, 28, 160, 36), "Kalibroi kamerat")
        self.btn_start_detect = Button((220, 28, 180, 36), "Aloita tunnistus")
        self.btn_stop_detect = Button((420, 28, 140, 36), "Lopeta tunnistus")
        self.btn_next = Button((580, 28, 160, 36), "Seuraava pelaaja")
        self.btn_reset = Button((760, 28, 160, 36), "Nollaa peli")
        self.btn_save = Button((940, 28, 160, 36), "Tallenna CSV")
        self.detecting = False

        # game state
        self.players = []
        self.scores = []
        self.history = []  # per player lists
        self.current_idx = 0
        self.turn_start_score = None
        self.turn_throws = []
        self.throw_count = 0

        # detection flow
        self.last_detection_time = 0

        # visual effects
        self.glow_active = False
        self.glow_at = (0,0)
        self.glow_start = 0

    # -------------------
    # Registration screen
    # -------------------
    def draw_registration(self):
        s = self.screen
        s.fill(COLOR_BG)
        draw_text(s, "eDarts - Pelaajamankelointi", (60, 30), FONT_XL, COLOR_ACCENT)
        draw_text(s, "Valitse ekana pelaajamäärä ja syötä nimet sekä pisteet.", (60, 70), FONT_SMALL)
        # draw count buttons and highlight the selected one
        for val, btn in zip([2,3,4], self.count_buttons):
            if val == self.player_count:
                # highlighted style for selected button
                sel_rect = btn.rect.inflate(6, 6)
                pygame.draw.rect(s, COLOR_ACCENT, sel_rect, border_radius=10)
                # draw inner panel darker for contrast
                pygame.draw.rect(s, (40,40,40), btn.rect, border_radius=8)
                # draw white text for selected
                draw_text(s, btn.text, (btn.rect.x+10, btn.rect.y+8), FONT_SMALL, COLOR_TEXT)
            else:
                btn.draw(s)
        for i in range(4):
            draw_text(s, f"Pelaaja {i+1}:", (60, 120 + i*66), FONT_SMALL)
            self.name_boxes[i].draw(s)
            draw_text(s, "Pisteet:", (360, 120 + i*66), FONT_SMALL)
            self.start_boxes[i].draw(s)
        self.btn_start_game.draw(s)
        draw_text(s, "Kamerat: vasen indeksi {} | oikea indeksi {}".format(self.left_cam.cam_idx, self.right_cam.cam_idx), (60, 520), FONT_SMALL)
        draw_text(s, "Paina 'Aloita peli' kun valmista.", (60, 560), FONT_SMALL)
        if self.info:
            draw_text(s, self.info, (60, 600), FONT_SMALL, COLOR_WARN)

    def handle_registration_event(self, ev):
        for i,(val, btn) in enumerate(zip([2,3,4], self.count_buttons)):
            btn.handle(ev)
            if btn.handle(ev):
                self.player_count = val
                # clear extras
                for j in range(self.player_count, 4):
                    self.name_boxes[j].text = ''
                    self.start_boxes[j].text = ''
        for i in range(self.player_count):
            self.name_boxes[i].handle(ev)
            self.start_boxes[i].handle(ev)
        if self.btn_start_game.handle(ev):
            # validate and create players
            players = []
            starts = []
            ok = True
            for i in range(self.player_count):
                name = self.name_boxes[i].text.strip() or f"P{i+1}"
                st_str = self.start_boxes[i].text.strip()
                if not st_str.isdigit():
                    self.info = "Pisteiden pitäis olla numero (esim. 501)."
                    ok = False; break
                st = int(st_str)
                if st <= 0:
                    self.info = "Ei pisteitä mistään miinuksista aleta laskemaan hölmö."
                    ok = False; break
                players.append(name); starts.append(st)
            if ok:
                self.players = players
                self.scores = starts[:]
                self.history = [[] for _ in players]
                self.current_idx = 0
                self.turn_start_score = self.scores[self.current_idx]
                self.turn_throws = []
                self.throw_count = 0
                self.mode = 'playing'
                self.info = ''
                # try calibrate once
                self.calibrate_cameras()

    # -------------------
    # Calibration
    # -------------------
    def calibrate_cameras(self):
        # Grab frames and run auto_find_board
        left_frame = self.left_cam.get_frame()
        right_frame = self.right_cam.get_frame()
        if left_frame is None or right_frame is None:
            self.info = "Kamerat ei valmiina kalibrointiin."
            return
        lw, Lminv = auto_find_board(left_frame)
        rw, Rminv = auto_find_board(right_frame)
        if lw is None or rw is None:
            self.info = "Taulua ei löydy yhdestä tai molemmista kameroista. Säädä kameraa ja yritä uudelleen."
            self.left_warp = None; self.right_warp = None
            return
        # store Minv matrices to map warped->orig
        self.left_warp = (lw, Lminv)
        self.right_warp = (rw, Rminv)
        self.info = "Kalibrointi onnistui molemmilta kameroilta."

    # -------------------
    # Playing screen draw
    # -------------------
    def draw_playing(self):
        s = self.screen
        s.fill(COLOR_BG)
        # left preview
        left_frame = self.left_cam.get_frame()
        right_frame = self.right_cam.get_frame()
        # show placeholders if none
        if left_frame is None:
            lf_surf = pygame.Surface((CAM_PREVIEW_W, CAM_PREVIEW_H))
            lf_surf.fill((30,30,30))
        else:
            # draw overlay with board grid if calibrated
            lf_display = left_frame.copy()
            if self.left_warp is not None:
                # draw overlay warped board border onto original (map back overlay)
                warped, _ = self.left_warp
                overlay = draw_board_overlay_image(warped.shape[0])
                # warp overlay back to camera
                M_inv = self.left_warp[1]
                overlay_bgr = overlay.copy()
                # convert overlay to BGR (it is RGBA)
                overlay_bgr = cv2.cvtColor(overlay_bgr, cv2.COLOR_RGBA2BGRA) if overlay_bgr.shape[2]==4 else overlay_bgr
                # warp perspective
                warped_back = cv2.warpPerspective(overlay_bgr, M_inv, (left_frame.shape[1], left_frame.shape[0]), borderMode=cv2.BORDER_TRANSPARENT)
                # combine for display
                alpha_mask = (warped_back[...,3] / 255.0) if warped_back.shape[2]==4 else None
                if alpha_mask is not None:
                    for c in range(3):
                        lf_display[...,c] = (lf_display[...,c] * (1-alpha_mask) + warped_back[...,c] * alpha_mask).astype(np.uint8)
                else:
                    lf_display = cv2.addWeighted(lf_display, 0.6, warped_back, 0.4, 0)
            lf_rgb = cv2.cvtColor(lf_display, cv2.COLOR_BGR2RGB)
            lf_rgb = cv2.resize(lf_rgb, (CAM_PREVIEW_W, CAM_PREVIEW_H))
            lf_surf = pygame.surfarray.make_surface(np.rot90(lf_rgb))
        if right_frame is None:
            rf_surf = pygame.Surface((CAM_PREVIEW_W, CAM_PREVIEW_H))
            rf_surf.fill((30,30,30))
        else:
            rf_display = right_frame.copy()
            if self.right_warp is not None:
                warped, _ = self.right_warp
                overlay = draw_board_overlay_image(warped.shape[0])
                M_inv = self.right_warp[1]
                warped_back = cv2.warpPerspective(overlay, M_inv, (right_frame.shape[1], right_frame.shape[0]), borderMode=cv2.BORDER_TRANSPARENT)
                alpha_mask = (warped_back[...,3] / 255.0) if warped_back.shape[2]==4 else None
                if alpha_mask is not None:
                    for c in range(3):
                        rf_display[...,c] = (rf_display[...,c] * (1-alpha_mask) + warped_back[...,c] * alpha_mask).astype(np.uint8)
                else:
                    rf_display = cv2.addWeighted(rf_display, 0.6, warped_back, 0.4, 0)
            rf_rgb = cv2.cvtColor(rf_display, cv2.COLOR_BGR2RGB)
            rf_rgb = cv2.resize(rf_rgb, (CAM_PREVIEW_W, CAM_PREVIEW_H))
            rf_surf = pygame.surfarray.make_surface(np.rot90(rf_rgb))

        # Place camera previews stacked in the top-right corner
        preview_x = WINDOW_W - LEFT_MARGIN - CAM_PREVIEW_W
        s.blit(lf_surf, (preview_x, TOP_MARGIN))
        s.blit(rf_surf, (preview_x, TOP_MARGIN + CAM_PREVIEW_H + 12))

        # UI buttons
        self.btn_calibrate.draw(s)
        self.btn_start_detect.draw(s)
        self.btn_stop_detect.draw(s)
        self.btn_next.draw(s)
        self.btn_reset.draw(s)
        self.btn_save.draw(s)

        # players widget area centered on screen (avoid overlapping right previews)
        # compute available width leaving space for the right preview column
        max_w = WINDOW_W - (CAM_PREVIEW_W + LEFT_MARGIN*3)
        w_w = min(900, max_w)
        widget_x = (WINDOW_W - w_w) // 2
        # compute total stacked height to center vertically
        container_h = 160
        spacing = 18
        total_h = len(self.players) * (container_h + spacing) - spacing if self.players else container_h
        widget_y = max(TOP_MARGIN, (WINDOW_H - total_h) // 2)

         # Draw each player widget stacked
        for i, name in enumerate(self.players):
            y = widget_y + i*(container_h + spacing)
            pygame.draw.rect(s, COLOR_PANEL, (widget_x, y, w_w, container_h), border_radius=10)
            # highlight current
            if i == self.current_idx:
                pygame.draw.rect(s, COLOR_ACCENT, (widget_x-3, y-3, w_w+6, container_h+6), 3, border_radius=12)
            # name and score (top area)
            draw_text(s, name, (widget_x+18, y+12), FONT_LG, COLOR_TEXT)
            draw_text(s, f"Pisteet: {self.scores[i]}", (widget_x+18, y+56), FONT_LG, COLOR_TEXT)
            # last 3 throws (boxes placed at bottom of container)
            last3 = self.history[i][-3:]
            box_w = 80; box_h = 52
            bx0 = widget_x + w_w - 18 - (box_w*3 + 12*2)
            box_y = y + container_h - box_h - 16
            for k in range(3):
                bx = bx0 + k*(box_w+12)
                pygame.draw.rect(s, (40,40,40), (bx, box_y, box_w, box_h), border_radius=8)
                val = last3[k] if k < len(last3) else ''
                # center the value text inside the slot
                txt = str(val)
                txt_surf = FONT_LG.render(txt, True, COLOR_TEXT)
                tx = bx + max(6, (box_w - txt_surf.get_width())//2)
                ty = box_y + max(6, (box_h - txt_surf.get_height())//2)
                s.blit(txt_surf, (tx, ty))

        # info
        draw_text(s, f"Tila: {'Tunnistamassa' if self.detecting else 'Valmiustila'}", (LEFT_MARGIN, TOP_MARGIN + CAM_PREVIEW_H + 20), FONT_SMALL)
        if self.info:
            draw_text(s, self.info, (LEFT_MARGIN, TOP_MARGIN + CAM_PREVIEW_H + 54), FONT_SMALL, COLOR_WARN)

        # glow effect
        if self.glow_active:
            t = time.time() - self.glow_start
            if t > 0.7:
                self.glow_active = False
            else:
                alpha = int(255 * (1 - t/0.7))
                gx, gy = self.glow_at
                glow_surf = pygame.Surface((200,200), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (255,80,80,alpha), (100,100), int(80*(1-t/0.7)))
                self.screen.blit(glow_surf, (gx-100, gy-100), special_flags=pygame.BLEND_RGBA_ADD)

    # -------------------
    # Events and actions
    # -------------------
    def handle_event(self, ev):
        if self.mode == 'register':
            for btn in self.count_buttons:
                btn.handle(ev)
            for box in self.name_boxes + self.start_boxes:
                box.handle(ev)
            if self.btn_start_game.handle(ev):
                # build players
                players = []
                starts = []
                for i in range(self.player_count):
                    n = self.name_boxes[i].text.strip() or f"P{i+1}"
                    s_text = self.start_boxes[i].text.strip()
                    if not s_text.isdigit():
                        self.info = "Pisteiden tulee olla numero (esim. 501)."
                        return
                    s_val = int(s_text)
                    players.append(n); starts.append(s_val)
                # init game data
                self.players = players
                self.scores = starts[:]
                self.history = [[] for _ in players]
                self.current_idx = 0
                self.turn_start_score = self.scores[0]
                self.turn_throws = []
                self.throw_count = 0
                self.mode = 'playing'
                self.info = ''
                # attempt auto calib
                self.calibrate_cameras()
        else:
            # playing
            if self.btn_calibrate.handle(ev):
                self.calibrate_cameras()
            if self.btn_start_detect.handle(ev):
                if self.left_warp is None or self.right_warp is None:
                    self.info = "Kalibroi ensin molemmat kamerat!"
                else:
                    self.detecting = True
                    self.info = "Tunnistus käynnissä."
            if self.btn_stop_detect.handle(ev):
                self.detecting = False
                self.info = "Tunnistus pysäytetty."
            if self.btn_next.handle(ev):
                self.end_turn(reset=False)
            if self.btn_reset.handle(ev):
                self.reset_game()
            if self.btn_save.handle(ev):
                self.save_csv()

    # -------------------
    # Detection loop step (called each frame update)
    # -------------------
    def step_detection(self):
        # get frames
        lf = self.left_cam.get_frame()
        rf = self.right_cam.get_frame()
        left_hits = []; right_hits = []
        # For each camera, perform auto-find board warp if not present
        if self.left_warp is None and lf is not None:
            lw, Lminv = auto_find_board(lf)
            if lw is not None:
                self.left_warp = (lw, Lminv)
        if self.right_warp is None and rf is not None:
            rw, Rminv = auto_find_board(rf)
            if rw is not None:
                self.right_warp = (rw, Rminv)
        # detect on warped images (preferred)
        if lf is not None and self.left_warp is not None:
            warped_left = self.left_warp[0]
            # run detector on warped
            hits = self.det_left.update(warped_left)
            # map hits to warped coordinates (they are already in warped space)
            # each hit: (cx,cy,area) -> compute score
            for (cx,cy,area) in hits:
                val,label = get_score_label_from_warp(cx, cy, warped_left.shape[0])
                left_hits.append((cx, cy, val, label))
        if rf is not None and self.right_warp is not None:
            warped_right = self.right_warp[0]
            hits = self.det_right.update(warped_right)
            for (cx,cy,area) in hits:
                val,label = get_score_label_from_warp(cx, cy, warped_right.shape[0])
                right_hits.append((cx, cy, val, label))
        # fuse
        fused = fuse_hits(left_hits, right_hits)
        if fused and self.detecting:
            now = time.time()
            if now - self.last_detection_time > DETECTION_COOLDOWN:
                # accept highest scoring hit
                fx,fy,val,label = fused[0]
                self.register_throw(int(val), label, fx, fy)
                self.last_detection_time = now

    # -------------------
    # Register throw logic (double-finish rule)
    # -------------------
    def register_throw(self, val, label, warped_x, warped_y):
        p = self.current_idx
        # store
        self.history[p].append(val)
        self.scores[p] -= val
        self.turn_throws.append((val, label))
        self.throw_count += 1
        # visual glow: map warped coords to screen approx location: place somewhere near left preview center
        # Use left preview screen coords as reference: left preview top-left at (LEFT_MARGIN, TOP_MARGIN)
        screen_x = LEFT_MARGIN + int((warped_x / 800.0) * CAM_PREVIEW_W)
        screen_y = TOP_MARGIN + int((warped_y / 800.0) * CAM_PREVIEW_H)
        self.glow_active = True; self.glow_at = (screen_x, screen_y); self.glow_start = time.time()
        # check win/bust
        if self.scores[p] < 0:
            # bust -> restore
            self.scores[p] = self.turn_start_score
            # remove the added throws from history
            for _ in range(len(self.turn_throws)):
                if self.history[p]: self.history[p].pop()
            self.info = "Nollille lyö!"
            # end turn
            self.end_turn(bust=True)
            return
        if self.scores[p] == 0:
            # only win if last was double or DB
            last_label = self.turn_throws[-1][1] if self.turn_throws else ''
            if last_label in ('D','DB'):
                self.info = f"Pelaaja {self.players[p]} voitti!"
                self.detecting = False
            else:
                # bust
                self.scores[p] = self.turn_start_score
                for _ in range(len(self.turn_throws)):
                    if self.history[p]: self.history[p].pop()
                self.info = "Nollaus ilman tuplaa — Nollille lyö!"
                self.end_turn(bust=True)
                return
        # normal flow: if 3 throws done -> end turn
        if self.throw_count >= 3:
            self.end_turn()

    def end_turn(self, bust=False, reset=False):
        # advance
        self.current_idx = (self.current_idx + 1) % len(self.players)
        self.turn_start_score = self.scores[self.current_idx]
        self.turn_throws = []
        self.throw_count = 0
        if reset:
            # reset all to starting points
            self.scores = [int(b.text) if b.text.isdigit() else 501 for b in self.start_boxes[:self.player_count]]
            self.history = [[] for _ in self.players]
            self.current_idx = 0
            self.turn_start_score = self.scores[0]
            self.info = "Peli nollattu."

    def reset_game(self):
        self.mode = 'register'
        self.info = 'Peli palautettu rekisteröintitilaan.'

    def save_csv(self):
        try:
            fn = f"darts_scores_{int(time.time())}.csv"
            with open(fn, 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(['Pelaaja','Aloitus','Lopullinen','Heitot'])
                for i, name in enumerate(self.players):
                    w.writerow([name, '', self.scores[i], ';'.join(map(str,self.history[i]))])
            self.info = f"Tallennettu {fn}"
        except Exception as e:
            self.info = f"Tallennus epäonnistui: {e}"

# -----------------------
# Helper: draw overlay image for warped board (RGBA)
# -----------------------
def draw_board_overlay_image(size):
    """
    Returns an RGBA image with board drawing (so it can be alpha-blended)
    size: integer (square)
    """
    overlay = np.zeros((size, size, 4), dtype=np.uint8)
    cx = size//2; cy = size//2
    R = int(size*0.48)
    # draw rings as translucent shapes
    # draw double ring, triple ring, single areas, bull
    # We'll draw simple colored rings for visibility
    cv2.circle(overlay, (cx,cy), int(R*DOUBLE_OUT_R), (0,0,0,0), -1)  # keep base
    # sectors: draw alternating dark/light backgrounds and numbers
    for i, val in enumerate(SECTORS):
        start = -9 + i*18
        end = start + 18
        # draw triangle-like sector by approximating arc as polygon of points
        pts = []
        for a in np.linspace(start, end, num=20):
            rad = math.radians(a)
            x = int(cx + math.cos(rad)*R)
            y = int(cy - math.sin(rad)*R)
            pts.append((x,y))
        # add center
        pts.append((cx,cy))
        color = (40,40,40,80) if i%2==0 else (60,60,60,80)
        cv2.fillPoly(overlay, [np.array(pts, dtype=np.int32)], color)
        # draw sector number
        mid = math.radians(start + 9)
        tx = int(cx + math.cos(mid)*(R+40))
        ty = int(cy - math.sin(mid)*(R+40))
        cv2.putText(overlay, str(val), (tx-15, ty+8), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255,200), 2, cv2.LINE_AA)
    # draw triple ring and double ring boundaries (visual)
    r_tr_outer = int(size*TRIPLE_OUT_R/1.0)
    r_tr_inner = int(size*TRIPLE_IN_R/1.0)
    r_db_outer = int(size*DOUBLE_OUT_R/1.0)
    r_db_inner = int(size*DOUBLE_IN_R/1.0)
    # rings: draw as translucent circles
    cv2.circle(overlay, (cx,cy), r_tr_outer, (180,20,20,150), thickness=8)
    cv2.circle(overlay, (cx,cy), r_tr_inner, (180,20,20,150), thickness=8)
    cv2.circle(overlay, (cx,cy), r_db_outer, (20,180,20,150), thickness=8)
    cv2.circle(overlay, (cx,cy), r_db_inner, (20,180,20,150), thickness=8)
    # bull
    cv2.circle(overlay, (cx,cy), int(size*BULL_INNER_R), (0,200,0,255), -1)
    cv2.circle(overlay, (cx,cy), int(size*BULL_OUTER_R), (180,180,180,180), -1)
    return overlay

# -----------------------
# Helper: compute score+label from warped coords (cx,cy)
# -----------------------
def get_score_label_from_warp(px, py, warped_size):
    val, label = get_score_label(px, py, warped_size)
    return val, label

def get_score_label(px, py, size):
    cx = size/2; cy = size/2
    dx = px - cx; dy = cy - py
    r_norm = math.hypot(dx, dy) / (size/2)
    if r_norm <= BULL_INNER_R:
        return 50, 'DB'
    if r_norm <= BULL_OUTER_R:
        return 25, 'SB'
    angle = (math.degrees(math.atan2(dy, dx)) + 360) % 360
    idx = int((angle + 9)//18) % 20
    base = SECTORS[idx]
    if TRIPLE_IN_R <= r_norm <= TRIPLE_OUT_R:
        return base*3, 'T'
    if DOUBLE_IN_R <= r_norm <= DOUBLE_OUT_R:
        return base*2, 'D'
    return base, 'S'

# -----------------------
# Main loop
# -----------------------
def main():
    app = App()
    running = True
    fps_clock = pygame.time.Clock()
    # For performance, pre-generate warped overlay of size 800
    warped_overlay = draw_board_overlay_image(800)

    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            else:
                if app.mode == 'register':
                    # count buttons handle click
                    for i,btn in enumerate(app.count_buttons):
                        btn.handle(ev)
                        if btn.handle(ev):
                            app.player_count = [2,3,4][i]
                    app.handle_event(ev)
                else:
                    # propagate to app
                    app.handle_event(ev)
        # draw appropriate screen
        if app.mode == 'register':
            app.draw_registration()
        else:
            # detection step
            if app.detecting:
                try:
                    app.step_detection()
                except Exception as e:
                    app.info = f"Tunnistusvirhe: {e}"
            app.draw_playing()
        pygame.display.flip()
        fps_clock.tick(FPS)

    # cleanup
    try: app.left_cam.stop()
    except: pass
    try: app.right_cam.stop()
    except: pass
    pygame.quit()

if __name__ == "__main__":
    main()