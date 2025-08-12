import os, time, tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.font as tkfont

# ===== Defaults (Settings에서 바꾸면 즉시 반영) =====
ASSETS = {
    "bg": "",            # background image
    "ring_empty": "",    # empty ring texture
    "ring_fill": "",     # filled sector texture
    "inner_face": "",    # inner circle texture
    "alarm": ""          # mp3/ogg/flac/wav
}
# ===================================================

# ----- Look & Timing -----
BG_COLOR      = "#EBEBEB"
PLATE_FILL    = "#F5F5F5"
SECTOR_COL    = "#DC2323"
INNER_FILL    = "#2b2b2b"
TEXT_MAIN     = "#FFFFFF"

FPS_PIL       = 60    # 부드럽게
FPS_TK        = 30

# 사이즈/그림자
OUTER_SCALE   = 0.36   # ring diameter ratio (배경 여백 폭)
INNER_RATIO   = 0.56   # inner circle ratio
DARKEN_ALPHA  = 0.15   # 미채워진 이미지 톤다운
SOFT_SHADOW   = 0.65   # 중앙 그림자 진하게

# 타이머 폰트(설정에서 변경 가능)
TIMER_FONT_FAMILY = "Consolas"
TIMER_FONT_BOLD   = True

# ---- Optional libs ----
try:
    from PIL import Image, ImageDraw, ImageOps, ImageFilter, ImageTk, ImageColor
    PIL_OK = True
except Exception:
    PIL_OK = False

# ---- 오디오 백엔드 ----
BACKENDS = {}
try:
    import pygame
    BACKENDS["pygame"] = True
except Exception:
    BACKENDS["pygame"] = False
try:
    import simpleaudio
    from pydub import AudioSegment
    BACKENDS["pydub"] = True
except Exception:
    BACKENDS["pydub"] = False
try:
    import winsound
    BACKENDS["winsound"] = True
except Exception:
    BACKENDS["winsound"] = False

# =================== 공통 유틸 ===================
def fmt_time(ms_left: int, show_hours: bool) -> str:
    if ms_left < 0: ms_left = 0
    h, rem = divmod(ms_left, 3_600_000)
    m, rem = divmod(rem,        60_000)
    s, _   = divmod(rem,         1_000)
    return f"{h:02d}:{m:02d}:{s:02d}" if show_hours else f"{h*60+m:02d}:{s:02d}"

class TimerCore:
    def __init__(self, total_seconds: int):
        self.total_ms   = max(1, int(total_seconds*1000))
        self.show_hours = (total_seconds >= 3600)
        self.paused = False; self.pause_accum = 0.0
        self.start_t = time.perf_counter(); self.pause_t = self.start_t
    def reset(self):
        self.paused=False; self.pause_accum=0.0; self.start_t=time.perf_counter()
    def toggle_pause(self):
        if not self.paused:
            self.paused=True; self.pause_t=time.perf_counter()
        else:
            self.paused=False; self.pause_accum += time.perf_counter()-self.pause_t
    def elapsed_ms(self)->int:
        t = self.pause_t if self.paused else time.perf_counter()
        return int((t - self.start_t - self.pause_accum) * 1000)

# =================== 그리기 ===================
class PainterBase:
    def __init__(self):
        self._font_cache = {}  # (key) -> (family,size,weight)

    def set_assets(self, assets: dict): ...
    def draw(self, canvas: tk.Canvas, ms_left: int, total_ms: int, show_hours: bool, *, for_hud=False): ...

    def _get_cached_font(self, canvas, text, maxw, maxh, *, family, bold, key):
        """key가 같으면 같은 폰트 크기를 계속 사용"""
        if not hasattr(self, "_font_cache"):
            self._font_cache = {}
        if key not in self._font_cache:
            weight = "bold" if bold else "normal"
            self._font_cache[key] = self._auto_font(canvas, text, maxw, maxh, family=family, weight=weight)
        return self._font_cache[key]

    @staticmethod
    def _auto_font(canvas, text, maxw, maxh, family="Consolas", weight="bold"):
        lo, hi, best = 10, 128, 10
        while lo <= hi:
            mid=(lo+hi)//2
            f=tkfont.Font(family=family,size=mid,weight=weight)
            if f.measure(text)<=maxw and (f.metrics("ascent")+f.metrics("descent"))<=maxh:
                best=mid; lo=mid+1
            else: hi=mid-1
        return (family,best,weight)

class PainterTk(PainterBase):
    def __init__(self):
        super().__init__()
        self.assets={}
        self._bg=None; self._mid=None
    def set_assets(self, assets: dict):
        self.assets=assets
        self._font_cache.clear()
        self._bg  = self._load(assets.get("bg"))
        self._mid = self._load(assets.get("inner_face"))
    def _load(self,path):
        try: return tk.PhotoImage(file=path) if path and os.path.exists(path) else None
        except: return None
    def draw(self, canvas, ms_left, total_ms, show_hours, *, for_hud=False):
        W,H=canvas.winfo_width(),canvas.winfo_height()
        if W<=2 or H<=2: return
        canvas.delete("all")
        # HUD에선 배경 이미지 표시 금지
        if self._bg and not for_hud:
            canvas.create_image(W//2,H//2,image=self._bg)
        else:
            canvas.configure(bg=BG_COLOR)
        cx,cy=W/2,H/2
        outerR=int(min(W,H)*OUTER_SCALE); innerR=int(outerR*INNER_RATIO)

        # 빈 링
        canvas.create_oval(cx-outerR,cy-outerR,cx+outerR,cy+outerR,fill=PLATE_FILL,outline="")

        # 진행 섹터(각도는 부동소수)
        frac=max(0.0,min(1.0,(total_ms-ms_left)/total_ms))
        if frac>0:
            canvas.create_arc(cx-outerR,cy-outerR,cx+outerR,cy+outerR,
                              start=-90.0, extent=-(frac*360.0),
                              fill=SECTOR_COL, outline="")

        # 중앙면
        if self._mid:
            canvas.create_image(cx,cy,image=self._mid)
        else:
            canvas.create_oval(cx-innerR,cy-innerR,cx+innerR,cy+innerR,fill=INNER_FILL,outline="")

        # 텍스트(캐시 사용)
        t=fmt_time(ms_left, show_hours)
        font_key=("tk", int(innerR*2), bool(TIMER_FONT_BOLD), TIMER_FONT_FAMILY)
        font=self._get_cached_font(canvas, t, innerR*2*0.9, innerR*2*0.62,
                                   family=TIMER_FONT_FAMILY, bold=TIMER_FONT_BOLD, key=font_key)
        canvas.create_text(cx,cy,text=t,fill=TEXT_MAIN,font=font)

class PainterPIL(PainterBase):
    """
    정적 레이어 캐시(일반/HUD): [배경(일반만), 빈 링(톤다운), 중앙면(톤다운), 중앙 그림자].
    매 프레임: 정적 복사 + '도넛 섹터(부동소수 각도)' 합성 + 텍스트.
    """
    def __init__(self):
        super().__init__()
        self.assets={}
        self.cache={}
        self.static={}
        self.tkimg={}

    def set_assets(self, assets: dict):
        self.assets=dict(assets)
        self.cache.clear(); self.static.clear(); self.tkimg.clear()
        self._font_cache.clear()

    # ---------- 내부 유틸 ----------
    def _open_rgba(self, key):
        p=self.assets.get(key,"")
        try:
            return Image.open(p).convert("RGBA") if p and os.path.exists(p) else None
        except Exception:
            return None
    def _fit_rgba(self, img, size):
        return ImageOps.fit(img, size, method=Image.Resampling.LANCZOS)
    def _darken(self, img, alpha=DARKEN_ALPHA):
        if alpha<=0: return img
        dark=Image.new("RGBA", img.size, (0,0,0,int(255*alpha)))
        out=img.copy(); out.alpha_composite(dark); return out
    def _circle_mask(self, d, r):
        k=("c",d,r); m=self.cache.get(k)
        if m is None:
            m=Image.new("L",(d,d),0); ImageDraw.Draw(m).ellipse((d//2-r,d//2-r,d//2+r,d//2+r),fill=255)
            self.cache[k]=m
        return m
    def _donut_sector_mask_dynamic(self, d, outerR, innerR, start_deg, extent_deg):
        """각도 손실 없이 프레임마다 만드는 도넛 섹터 마스크."""
        m=Image.new("L",(d,d),0); dr=ImageDraw.Draw(m)
        bbox=(d//2-outerR,d//2-outerR,d//2+outerR,d//2+outerR)
        dr.pieslice(bbox, start=float(start_deg), end=float(start_deg+extent_deg), fill=255)
        dr.ellipse((d//2-innerR,d//2-innerR,d//2+innerR,d//2+innerR), fill=0)
        return m
    def _inner_shadow(self, d, innerR, strength=SOFT_SHADOW, offset=5):
        k=("ish",d,innerR,round(strength,2),offset); m=self.cache.get(k)
        if m is None:
            grad=Image.new("L",(d,d),0); dr=ImageDraw.Draw(grad)
            max_a=int(170*strength)
            R=int(innerR*1.12)
            for r in range(R, 0, -2):
                a=int(max_a * (1 - r/R))
                dr.ellipse((d//2-r, d//2-r+offset, d//2+r, d//2+r+offset), fill=a)
            grad=grad.filter(ImageFilter.GaussianBlur(radius=max(8,d//36)))
            sh=Image.new("RGBA",(d,d),(0,0,0,0)); sh.putalpha(grad)
            self.cache[k]=sh; m=sh
        return m

    # ---------- 정적 레이어 ----------
    def _build_static(self, d, hud=False):
        key=(d, "hud" if hud else "main")
        if key in self.static: return
        cx=cy=d//2
        outerR=int(d*OUTER_SCALE); innerR=int(outerR*INNER_RATIO)

        img=Image.new("RGBA",(d,d),(0,0,0,0))

        # 배경: HUD(마스크) 상태에서는 표시하지 않음
        if not hud:
            bg=self._open_rgba("bg")
            if bg: img.alpha_composite(self._fit_rgba(bg,(d,d)))

        # 빈 링 (이미지면 톤다운)
        ring=self._open_rgba("ring_empty")
        if ring:
            tex=self._darken(self._fit_rgba(ring,(outerR*2,outerR*2)), DARKEN_ALPHA)
            lay=Image.new("RGBA",(d,d),(0,0,0,0))
            lay.paste(tex,(cx-outerR,cy-outerR), self._circle_mask(outerR*2,outerR))
            img.alpha_composite(lay)
        else:
            ImageDraw.Draw(img).ellipse((cx-outerR,cy-outerR,cx+outerR,cy+outerR), fill=PLATE_FILL)

        # 중앙 섀도우 + 중앙면 (바깥 그림자 없음!)
        img.alpha_composite(self._inner_shadow(d, innerR))
        face=self._open_rgba("inner_face")
        if face:
            tex=self._darken(self._fit_rgba(face,(innerR*2,innerR*2)), DARKEN_ALPHA)
            lay=Image.new("RGBA",(d,d),(0,0,0,0))
            lay.paste(tex,(cx-innerR,cy-innerR), self._circle_mask(innerR*2,innerR))
            img.alpha_composite(lay)
        else:
            ImageDraw.Draw(img).ellipse((cx-innerR,cy-innerR,cx+innerR,cy+innerR), fill=INNER_FILL)

        self.static[key]=(img, outerR, innerR)

    # ---------- 프레임 렌더 ----------
    def draw(self, canvas, ms_left, total_ms, show_hours, *, for_hud=False):
        W,H=canvas.winfo_width(),canvas.winfo_height()
        if W<=2 or H<=2: return
        canvas.delete("all")
        d=min(W,H)

        self._build_static(d, hud=for_hud)
        base, outerR, innerR = self.static[(d, "hud" if for_hud else "main")]
        frame=base.copy()

        # 섹터(채워진 부분) – 각도 소수점 그대로
        frac=max(0.0,min(1.0,(total_ms-ms_left)/total_ms))
        if frac>0:
            extent=-(frac*360.0)
            mask=self._donut_sector_mask_dynamic(d, outerR, innerR, -90.0, extent)
            fill=self._open_rgba("ring_fill")
            if fill:
                tex=self._fit_rgba(fill,(d,d))
                lay=Image.new("RGBA",(d,d),(0,0,0,0)); lay.paste(tex,(0,0), mask)
                frame.alpha_composite(lay)
            else:
                col=Image.new("RGBA",(d,d), (*ImageColor.getrgb(SECTOR_COL),255))
                lay=Image.new("RGBA",(d,d),(0,0,0,0)); lay.paste(col,(0,0), mask)
                frame.alpha_composite(lay)

        tki=ImageTk.PhotoImage(frame); self.tkimg[d]=tki
        canvas.create_image(W//2,H//2,image=tki)

        # 텍스트(캐시 사용)
        t=fmt_time(ms_left, show_hours)
        cx,cy=W/2,H/2
        font_key=("pil","hud" if for_hud else "main", int(innerR*2), bool(TIMER_FONT_BOLD), TIMER_FONT_FAMILY)
        font=self._get_cached_font(canvas, t, innerR*2*0.9, innerR*2*0.62,
                                   family=TIMER_FONT_FAMILY, bold=TIMER_FONT_BOLD, key=font_key)
        canvas.create_text(cx,cy,text=t,fill=TEXT_MAIN,font=font)

def BG_COLOR_to_rgba():
    c=BG_COLOR.lstrip("#")
    return tuple(int(c[i:i+2],16) for i in (0,2,4))

# =================== 뷰/앱 ===================
class TimerView(tk.Frame):
    def __init__(self, master, secs: int, on_exit_to_start):
        super().__init__(master, bg=BG_COLOR); self.pack(fill="both", expand=True)
        self.root=master; self.on_exit_to_start=on_exit_to_start
        self.core=TimerCore(secs)
        self.painter = (PainterPIL() if PIL_OK else PainterTk())
        self.painter.set_assets(ASSETS)
        self._fps = FPS_PIL if PIL_OK else FPS_TK

        # 캔버스(위)
        self.canvas=tk.Canvas(self, highlightthickness=0, bg=BG_COLOR)
        self.canvas.pack(fill="both", expand=True, padx=0, pady=(10,4))

        # 컨트롤 바(아래)
        bar=tk.Frame(self, bg=BG_COLOR); bar.pack(fill="x", padx=10, pady=(0,10))
        self.btn_pause=ttk.Button(bar,text="Pause",command=self._toggle_pause); self.btn_pause.pack(side="left",padx=6)
        ttk.Button(bar,text="Reset",command=self._reset).pack(side="left",padx=6)
        ttk.Button(bar,text="Mask",command=self._toggle_mask).pack(side="left",padx=6)
        ttk.Button(bar,text="Settings",command=self._open_settings).pack(side="left",padx=6)
        ttk.Button(bar,text="Exit",command=self._exit_to_start).pack(side="left",padx=6)

        # HUD/Overlay
        self._overlay=self._hud=self._hud_canvas=None
        self._hud_painter=(PainterPIL() if PIL_OK else PainterTk())
        self._hud_painter.set_assets(ASSETS)

        # 키
        self.bind_all("<space>", lambda e:self._toggle_pause())
        self.bind_all("<Escape>", self._esc)
        self.bind_all("r", lambda e:self._reset()); self.bind_all("R", lambda e:self._reset())

        self._alarm_fired=False
        self.after(self._fps,self._tick)

    # ---- control ----
    def _toggle_pause(self):
        self.core.toggle_pause()
        self.btn_pause.config(text=("Resume" if self.core.paused else "Pause"))
    def _reset(self):
        self.core.reset(); self._alarm_fired=False
        self.btn_pause.config(text="Pause")
    def _exit_to_start(self):
        self._destroy_mask(); self.on_exit_to_start()

    # ---- settings ----
    def _open_settings(self):
        global TIMER_FONT_FAMILY, TIMER_FONT_BOLD
        win=tk.Toplevel(self.root); win.title("Settings"); win.geometry("+20+20")
        frm=ttk.Frame(win,padding=10); frm.pack(fill="both",expand=True)

        def row(label,key,ft):
            lf=ttk.Frame(frm); lf.pack(fill="x",pady=4)
            ttk.Label(lf,text=label,width=12).pack(side="left")
            var=tk.StringVar(value=ASSETS.get(key,""))
            ent=ttk.Entry(lf,textvariable=var,width=40); ent.pack(side="left",padx=6,fill="x",expand=True)
            ttk.Button(lf,text="Browse",command=lambda:var.set(filedialog.askopenfilename(filetypes=ft) or var.get())).pack(side="left")
            return var
        v_bg   =row("Background","bg",[("Images","*.png;*.jpg;*.jpeg;*.webp;*.bmp"),("All","*.*")])
        v_emp  =row("Ring Empty","ring_empty",[("Images","*.png;*.jpg;*.jpeg;*.webp;*.bmp"),("All","*.*")])
        v_fill =row("Ring Fill","ring_fill",[("Images","*.png;*.jpg;*.jpeg;*.webp;*.bmp"),("All","*.*")])
        v_face =row("Inner Face","inner_face",[("Images","*.png;*.jpg;*.jpeg;*.webp;*.bmp"),("All","*.*")])
        v_alarm=row("Alarm","alarm",[("Audio","*.mp3;*.ogg;*.flac;*.wav"),("All","*.*")])

        # 폰트 선택
        fonts = sorted(set(tkfont.families()))
        lf=ttk.Frame(frm); lf.pack(fill="x",pady=(12,4))
        ttk.Label(lf,text="Timer Font",width=12).pack(side="left")
        font_var=tk.StringVar(value=TIMER_FONT_FAMILY if TIMER_FONT_FAMILY in fonts else (fonts[0] if fonts else "Consolas"))
        font_box=ttk.Combobox(lf, textvariable=font_var, values=fonts or ["Consolas"], width=28, state="readonly")
        font_box.pack(side="left",padx=6)
        bold_var=tk.BooleanVar(value=TIMER_FONT_BOLD)
        ttk.Checkbutton(lf, text="Bold", variable=bold_var).pack(side="left",padx=6)

        def apply_close():
            ASSETS.update({"bg":v_bg.get().strip(),"ring_empty":v_emp.get().strip(),
                           "ring_fill":v_fill.get().strip(),"inner_face":v_face.get().strip(),
                           "alarm":v_alarm.get().strip()})
            # 폰트 반영 + 폰트 캐시 리셋
            globals()["TIMER_FONT_FAMILY"] = font_var.get().strip() or "Consolas"
            globals()["TIMER_FONT_BOLD"]   = bool(bold_var.get())
            self.painter.set_assets(ASSETS); self._hud_painter.set_assets(ASSETS)
            if hasattr(self.painter, "_font_cache"): self.painter._font_cache.clear()
            if hasattr(self._hud_painter, "_font_cache"): self._hud_painter._font_cache.clear()
            win.destroy()
        ttk.Button(frm,text="Apply",command=apply_close).pack(anchor="e",pady=(10,0))

    # ---- mask/HUD ----
    def _toggle_mask(self):
        if (self._overlay and tk.Toplevel.winfo_exists(self._overlay)) or (self._hud and tk.Toplevel.winfo_exists(self._hud)):
            self._destroy_mask(); return
        ov=tk.Toplevel(self.root); ov.overrideredirect(True); ov.attributes("-topmost",True)
        ov.configure(bg="#000000"); ov.attributes("-alpha",0.5)
        sw,sh=ov.winfo_screenwidth(),ov.winfo_screenheight()
        ov.geometry(f"{sw}x{sh}+0+0")
        ov.bind("<Button-1>",lambda e:self._toggle_mask()); ov.bind("<Key>",lambda e:self._toggle_mask())
        self._overlay=ov; self.root.withdraw()

        hud=tk.Toplevel(self.root); hud.overrideredirect(True); hud.attributes("-topmost",True)
        chroma="#00ff00"; hud.configure(bg=chroma)
        try: hud.attributes("-transparentcolor",chroma)
        except Exception: pass
        d=int(min(sw,sh)*OUTER_SCALE*2.8); d=max(220, d)-2
        x=(sw-d)//2; y=(sh-d)//2; hud.geometry(f"{d}x{d}+{x}+{y}")
        cv=tk.Canvas(hud,highlightthickness=0,bg=chroma,bd=0); cv.pack(fill="both",expand=True)
        hud.lift(); 
        try: ov.lower(hud)
        except: pass
        hud.attributes("-topmost",True); hud.lift()
        self._hud=hud; self._hud_canvas=cv

    def _destroy_mask(self):
        if self._overlay and tk.Toplevel.winfo_exists(self._overlay): self._overlay.destroy()
        if self._hud and tk.Toplevel.winfo_exists(self._hud): self._hud.destroy()
        self._overlay=self._hud=self._hud_canvas=None
        try: self.root.deiconify(); self.root.lift()
        except: pass

    def _esc(self,_=None):
        if (self._overlay and tk.Toplevel.winfo_exists(self._overlay)) or (self._hud and tk.Toplevel.winfo_exists(self._hud)):
            self._destroy_mask()
        else:
            self._toggle_pause()

    # ---- audio ----
    def _play_alarm(self):
        p=ASSETS.get("alarm","")
        if not (p and os.path.exists(p)):
            try: self.root.bell()
            except: pass
            return
        if BACKENDS.get("pygame"):
            try:
                if not pygame.get_init(): pygame.init()
                if not pygame.mixer.get_init(): pygame.mixer.init()
                pygame.mixer.music.load(p); pygame.mixer.music.play(); return
            except: pass
        if BACKENDS.get("pydub"):
            try:
                seg=AudioSegment.from_file(p)
                simpleaudio.play_buffer(seg.raw_data, seg.channels, seg.sample_width, seg.frame_rate); return
            except: pass
        if BACKENDS.get("winsound") and p.lower().endswith(".wav"):
            try: winsound.PlaySound(p, winsound.SND_FILENAME | winsound.SND_ASYNC); return
            except: pass
        if not getattr(self,"_warned_audio",False):
            self._warned_audio=True
            messagebox.showwarning("Audio", "음악을 재생할 수 없습니다.\n추천: pip install pygame\n대안: pip install pydub simpleaudio (FFmpeg 필요)")
        try: self.root.bell()
        except: pass

    # ---- loop ----
    def _tick(self):
        ms_left=self.core.total_ms - max(0,self.core.elapsed_ms())
        if ms_left<0: ms_left=0
        # main
        if not (self._overlay or self._hud):
            self.painter.draw(self.canvas, ms_left, self.core.total_ms, self.core.show_hours, for_hud=False)
        # HUD
        if self._hud_canvas:
            self._hud_painter.draw(self._hud_canvas, ms_left, self.core.total_ms, self.core.show_hours, for_hud=True)

        # alarm once
        if ms_left==0 and not self.core.paused:
            if not self._alarm_fired:
                self._alarm_fired=True; self._play_alarm()
        else:
            self._alarm_fired=False

        self.after(self._fps, self._tick)

# ---- Start ----
class StartView(tk.Frame):
    def __init__(self, master, on_start):
        super().__init__(master,bg=BG_COLOR); self.on_start=on_start; self.pack(fill="both",expand=True)
        c=tk.Frame(self,bg=BG_COLOR); c.pack(pady=24)
        tk.Label(c,text="Set Timer",bg=BG_COLOR,fg="#222",font=("Segoe UI",16,"bold")).grid(row=0,column=0,columnspan=6,pady=(0,10))
        def sb(p,a,b,v0): 
            v=tk.StringVar(value=v0)
            w=tk.Spinbox(p,from_=a,to=b,wrap=True,textvariable=v,width=4,justify="center",font=("Consolas",14))
            # 비워두면 자동 0 채우기
            def normalize(_e=None):
                s=v.get().strip()
                if s=="" or not s.isdigit(): v.set("0")
            w.bind("<FocusOut>", normalize)
            return w,v
        h_sb,self.h=sb(c,0,23,"0"); m_sb,self.m=sb(c,0,59,"25"); s_sb,self.s=sb(c,0,59,"0")
        h_sb.grid(row=1,column=0,padx=(0,4)); tk.Label(c,text="h",bg=BG_COLOR,fg="#444").grid(row=1,column=1,padx=(0,10))
        m_sb.grid(row=1,column=2,padx=(0,4)); tk.Label(c,text="m",bg=BG_COLOR,fg="#444").grid(row=1,column=3,padx=(0,10))
        s_sb.grid(row=1,column=4,padx=(0,4)); tk.Label(c,text="s",bg=BG_COLOR,fg="#444").grid(row=1,column=5)
        p=tk.Frame(self,bg=BG_COLOR); p.pack(pady=8)
        for txt,sec in [("Pomodoro 25m",25*60),("Short break 5m",5*60),("Long break 15m",15*60),("60m",60*60)]:
            ttk.Button(p,text=txt,command=lambda s=sec:self.on_start(s)).pack(side="left",padx=6)
        ttk.Button(self,text="Start",command=self.start_from_fields).pack(pady=10)
        self.bind_all("<Return>", lambda e:self.start_from_fields())
    def start_from_fields(self):
        # 비어있으면 0으로 간주
        def val(v): 
            s=str(v.get()).strip()
            return int(s) if s.isdigit() else 0
        h=val(self.h); m=val(self.m); s=val(self.s)
        self.on_start(max(1,h*3600+m*60+s))

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Visual Timer"); self.configure(bg=BG_COLOR); self.geometry("720x760")
        self._cur=None; self.show_start()
    def show_start(self):
        self._switch(StartView(self, self.start_timer))
    def start_timer(self, secs:int):
        self._switch(TimerView(self, secs, on_exit_to_start=self.show_start))
    def _switch(self,w):
        if self._cur is not None: self._cur.destroy()
        self._cur=w

if __name__=="__main__":
    App().mainloop()
