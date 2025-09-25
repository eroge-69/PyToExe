import tkinter as tk
from tkinter import ttk, messagebox
import os, json, datetime

# ====== (Opcionális) logókhoz/képekhez Pillow ======
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

# ====== (Opcionális) hangok Windows-on ======
try:
    import winsound
    WINSOUND_AVAILABLE = True
except Exception:
    WINSOUND_AVAILABLE = False

ASSET_DIR = "assets"
SAVE_DIR  = "save"
SCORES_PATH = os.path.join(SAVE_DIR, "scores.jsonl")

LOGO_LEFT_PATH  = os.path.join(ASSET_DIR, "logo_szekesfehervar.png")
LOGO_RIGHT_PATH = os.path.join(ASSET_DIR, "logo_kyndryl.png")
HEADER_HEIGHT = 64

# Kyndryl-színek
KY_ORANGE   = "#FF4F00"
KY_CHARCOAL = "#111111"
KY_BG       = "#FFFFFF"
KY_SURFACE  = "#FAFAFA"
KY_BORDER   = "#E5E7EB"
GREEN_OK    = "#16a34a"
RED_ERR     = "#dc2626"

# -- KISEBB ALAP MÉRETEK, hogy 14"-on is elférjen a "Következő" gomb --
CANVAS_W, CANVAS_H = 420, 240   # kérdés vizuál (kisebb, mint korábban)
HERO_W, HERO_H     = 420, 180   # hős vászon (kisebb, mint korábban)

# ---- Story & kérdések ---------------------------------------------------------
STORY_INTRO = (
    "A Székesfehérvári KiberKaland\n\n"
    "Képzeljétek el, hogy Székesfehérvár polgármestere különös emailt kap: "
    "„Kattints ide, hogy lásd a város titkos térképét!”\n\n"
    "A hackerek át akarják venni az irányítást a város gépei felett. "
    "Ti vagytok a kiberdetektívek! 8 próbán kell átjutnotok, hogy megmentsétek a várost."
)

QUESTIONS = [
    {
        "lead": "Reggel a Városházán egy sürgető üzenet érkezik a polgármester postaládájába. "
                "A feladó ismerősnek tűnik, de valami nem stimmel a hangvételben.",
        "question": "1) Gyanús email érkezik a polgármesternek. Mi árulkodó?",
        "answers": [
            "Helyesírási hibák, sürgetés, gyanús link",
            "Mindig kap térképeket, ez biztosan az",
            "Vicces emojik a tárgyban",
            "Hosszú email, tehát komoly"
        ],
        "correct": 0,
        "explanation": "A phishing gyakran sürget, hibás a szöveg és gyanús linket tartalmaz."
    },
    {
        "lead": "Közelebbről megvizsgáljátok az üzenetben lévő hivatkozást. "
                "A cím önmagában is árulkodó lehet – vajon megbízható?",
        "question": "2) A link: http://szekesfehervar.biz/security – rákattintanál?",
        "answers": ["Igen", "Nem"],
        "correct": 1,
        "explanation": "Nem hivatalos domain és nem HTTPS – ez gyanús."
    },
    {
        "lead": "A támadók nem adják fel: most egy ismeretlen csatolmányt küldenek 'fontos adatok' címmel. "
                "A fájlnév csábító, de a kockázat nagy.",
        "question": "3) Ismeretlen képcsatolmány érkezik. Megnyitod?",
        "answers": ["Igen", "Nem"],
        "correct": 1,
        "explanation": "Ismeretlen csatolmányokat nem nyitunk meg – lehet benne kártevő."
    },
    {
        "lead": "A város rendszergazdája javasolja: ideje megerősíteni a jelszavakat, "
                "mielőtt a támadók további próbálkozásai sikerrel járnának.",
        "question": "4) Melyik a legerősebb jelszó?",
        "answers": [
            "szekesfehervar2024",
            "Sfhv!2024#Cyber",
            "admin123",
            "jelszo"
        ],
        "correct": 1,
        "explanation": "Erős jelszó: hosszú, kis- és nagybetű, szám, speciális jel keveréke."
    },
    {
        "lead": "Közben a közösségi médiában egy ismeretlen profil jelöli be a polgármestert. "
                "A profilképe gyanúsan generáltnak tűnik, alig vannak ismerősei.",
        "question": "5) Hamis profil jelöli be a polgármestert. Mit tegyünk?",
        "answers": ["Elfogadjuk, hátha ismerős", "Jelentjük és nem fogadjuk el"],
        "correct": 1,
        "explanation": "Ismeretlen, gyanús profilokat ne fogadjunk el – jelentsük."
    },
    {
        "lead": "Délután terepre mentek: a főtéren nyilvános Wi-Fi hálózat bukkan fel, csábító névvel. "
                "A támadók gyakran ál-hálózatot állítanak fel az adatlopáshoz.",
        "question": "6) Nyilvános „FreeFehervar_WiFi” hálózatot találsz. Biztonságos?",
        "answers": ["Igen", "Nem"],
        "correct": 1,
        "explanation": "Nyilvános Wi-Fi veszélyes lehet. Ha muszáj, használj VPN-t és ne adj meg érzékeny adatot."
    },
    {
        "lead": "Vissza az irodában: a frissítési központ jelzi, hogy kritikus foltozások érhetők el. "
                "A támadók sokszor ismert sérülékenységeket használnak ki.",
        "question": "7) Miért fontosak a frissítések a város gépein?",
        "answers": [
            "Mert új ikonokat adnak",
            "Mert bezárják a biztonsági réseket",
            "Mert gyorsabban tölt a böngésző"
        ],
        "correct": 1,
        "explanation": "A frissítések javítják a sérülékenységeket, ezért biztonságosabb lesz a rendszer."
    },
    {
        "lead": "Estére egy telefonhívás érkezik: az állítólagos 'rendszeradmin' sürgősen kéri a jelszót "
                "a tűzijáték automatizálásához. A hangja magabiztos, de ez könnyen lehet csalás.",
        "question": "8) Telefonon valaki jelszót kér a tűzijáték miatt. Megadod?",
        "answers": ["Igen", "Nem"],
        "correct": 1,
        "explanation": "Jelszót SOHA nem adunk ki telefonon, emailben vagy üzenetben."
    },
]

# ---- Segéd: logók / asset képek ------------------------------------------------
def load_logo(path, target_h=HEADER_HEIGHT):
    if not os.path.exists(path):
        return None
    try:
        if PIL_AVAILABLE:
            img = Image.open(path).convert("RGBA")
            w, h = img.size
            if h != target_h:
                r = target_h / float(h)
                img = img.resize((max(1, int(w*r)), target_h), Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        return tk.PhotoImage(file=path)
    except Exception:
        return None

def load_asset_scaled(base_no_ext, max_w, max_h):
    """assets/<base>.(png|jpg|jpeg|gif|webp) -> PhotoImage arányosan méretezve, vagy None"""
    if not PIL_AVAILABLE:
        for ext in (".png", ".gif"):
            p = os.path.join(ASSET_DIR, base_no_ext + ext)
            if os.path.exists(p):
                try:
                    return tk.PhotoImage(file=p)
                except Exception:
                    pass
        return None
    for ext in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
        p = os.path.join(ASSET_DIR, base_no_ext + ext)
        if os.path.exists(p):
            try:
                img = Image.open(p).convert("RGBA")
                w, h = img.size
                scale = min(max_w / w, max_h / h, 1.0)
                img = img.resize((max(1, int(w*scale)), max(1, int(h*scale))), Image.LANCZOS)
                return ImageTk.PhotoImage(img)
            except Exception:
                return None
    return None

# ---- Modern „flat” vizuálok (kérdéskártya) ------------------------------------
def rounded_rect(c, x1, y1, x2, y2, r=16, fill=KY_BG, outline=KY_BORDER, width=1):
    pts = [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r, x2,y2-r, x2,y2, x2-r,y2, x1+r,y2, x1,y2, x1,y2-r, x1,y1+r, x1,y1]
    return c.create_polygon(pts, smooth=True, fill=fill, outline=outline, width=width)

def card_header(c, title, subtitle=None, icon="✉️", fg=KY_CHARCOAL):
    rounded_rect(c, 10, 10, CANVAS_W-10, CANVAS_H-10, r=18, fill=KY_BG, outline=KY_BORDER)
    c.create_text(34, 36, text=icon, font=("Arial", 22), anchor="w")
    c.create_text(72, 36, text=title, font=("Arial", 16, "bold"), fill=fg, anchor="w")
    if subtitle:
        c.create_text(34, 70, text=subtitle, font=("Arial", 12), fill="#6b7280", anchor="w")

def vis_q1(c):
    # Két panel: Bal = Phishing jelzések; Jobb = Megbízható email jelzések
    card_header(c, "Phishing vs. megbízható email", "Árulkodó jelek összehasonlítása", "🚩")
    # Bal (phishing)
    rounded_rect(c, 22, 104, 206, 152, r=10, fill="#FFF1ED", outline="")
    c.create_text(114, 114, text="Phishing", font=("Arial", 12, "bold"), fill=RED_ERR)
    rounded_rect(c, 34, 120, 200, 146, r=10, fill=KY_ORANGE, outline="")
    c.create_text(117, 133, text="KATTINTSON IDE", fill="white", font=("Arial", 10, "bold"))
    c.create_text(114, 152, text="Hibás szöveg • Sürgetés • Gyanús link", fill=RED_ERR, font=("Arial", 10), anchor="n")

    # Jobb (megbízható)
    rounded_rect(c, 214, 104, 398, 152, r=10, fill="#ECFDF5", outline="")
    c.create_text(306, 114, text="Megbízható", font=("Arial", 12, "bold"), fill=GREEN_OK)
    rounded_rect(c, 226, 120, 392, 146, r=10, fill="#E5E7EB", outline="")
    c.create_text(238, 133, text="https://szekesfehervar.hu/security", font=("Arial", 10), anchor="w")
    c.create_text(CANVAS_W-60, 133, text="🔒", font=("Arial", 16))
    c.create_text(306, 152, text="Hivatalos domain • HTTPS • normál hangvétel", fill=GREEN_OK, font=("Arial", 10), anchor="n")

def vis_q2(c):
    card_header(c, "Gyanús link", "HTTP + kamu domain", "🔗")
    rounded_rect(c, 34, 112, CANVAS_W-34, 148, r=10, fill="#F3F4F6", outline=KY_BORDER)
    c.create_text(52, 130, text="http://szekesfehervar.biz/security", font=("Arial", 12), anchor="w")
    c.create_text(CANVAS_W-60, 130, text="🔓", font=("Arial", 16))

def vis_q3(c):
    card_header(c, "Ismeretlen melléklet", "ZIP/EXE = rizikó", "📎")
    rounded_rect(c, 34, 108, 200, 164, r=12, fill="#EEF2FF", outline=KY_BORDER)
    c.create_text(117, 136, text="payment_info.zip", font=("Arial", 11, "bold"))
    c.create_text(310, 136, text="⚠️ Ne nyisd meg!", font=("Arial", 12, "bold"), fill=RED_ERR)

def vis_q4(c):
    card_header(c, "Jelszó erősség", "Hossz + mix + egyediség", "🔐")
    rounded_rect(c, 34, 116, CANVAS_W-34, 144, r=12, fill="#E5E7EB", outline="")
    rounded_rect(c, 34, 116, 300, 144, r=12, fill=GREEN_OK, outline="")
    c.create_text(335, 130, text="Erős", font=("Arial", 12, "bold"), fill=GREEN_OK)

def vis_q5(c):
    card_header(c, "Hamis profil", "Furcsa név/kép, kevés ismerős", "🧑‍💻")
    rounded_rect(c, 34, 108, 180, 164, r=12, fill="#F3F4F6", outline=KY_BORDER)
    c.create_text(320, 136, text="HAMIS PROFIL → Jelentés", font=("Arial", 12, "bold"), fill=RED_ERR)

def vis_q6(c):
    card_header(c, "Nyilvános Wi-Fi csapda", "FreeFehervar_WiFi", "📶")
    c.create_text(120, 136, text="📶", font=("Arial", 38))
    c.create_text(315, 134, text="Használj VPN-t,\nne add meg a jelszavad!", font=("Arial", 12), fill=KY_CHARCOAL)

def vis_q7(c):
    card_header(c, "Frissítések", "Sérülékenységek javítása", "🛡️")
    c.create_text(120, 136, text="⟳", font=("Arial", 40))
    c.create_text(320, 134, text="Telepítsd időben a frissítéseket!", font=("Arial", 12), fill=KY_CHARCOAL)

def vis_q8(c):
    card_header(c, "Telefonos jelszócsapda", "Jelszót soha!", "📱")
    c.create_text(120, 136, text="📵", font=("Arial", 38))
    c.create_text(330, 134, text="„Mondja meg a jelszavát…” – NEM!", font=("Arial", 12, "bold"), fill=RED_ERR)

QUESTION_VIS = [vis_q1, vis_q2, vis_q3, vis_q4, vis_q5, vis_q6, vis_q7, vis_q8]

# ---- 3D-s (pszeudo) Minecraft-stílusú hősök -----------------------------------
from functools import lru_cache

def _clamp(x, lo=0, hi=255):
    return max(lo, min(hi, int(round(x))))

@lru_cache(maxsize=256)
def shade_hex(hex_color, factor=1.0):
    s = hex_color.lstrip('#')
    r, g, b = int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
    r = _clamp(r * factor)
    g = _clamp(g * factor)
    b = _clamp(b * factor)
    return f"#{r:02x}{g:02x}{b:02x}"

def draw_block(c, x, y, w=18, h=18, depth=6, base="#7aa2ff"):
    top_col   = shade_hex(base, 1.20)
    side_col  = shade_hex(base, 0.85)
    # front
    c.create_rectangle(x, y, x+w, y+h, fill=base, outline="")
    # top
    c.create_polygon(
        x, y, x+depth, y-depth, x+w+depth, y-depth, x+w, y,
        fill=top_col, outline=""
    )
    # right side
    c.create_polygon(
        x+w, y, x+w+depth, y-depth, x+w+depth, y+h-depth, x+w, y+h,
        fill=side_col, outline=""
    )
    # finom kontúr
    c.create_rectangle(x, y, x+w, y+h, outline=shade_hex(base, 0.6), width=1)

def draw_mc_defender(c, base_x=26, base_y=16, scale=1.0):
    B = int(16 * scale)
    D = int(5 * scale)

    skin   = "#f5c29e"
    hair   = "#2b2b2b"
    suit   = KY_CHARCOAL
    accent = KY_ORANGE
    boot   = "#1b1b1b"

    def blk(cx, cy, col):
        draw_block(c, base_x + cx*B, base_y + cy*B, w=B, h=B, depth=D, base=col)

    # Fej (4x4)
    for i in range(4):
        for j in range(4):
            blk(2+i, 0+j, skin)
    # Haj
    for i in range(4):
        blk(2+i, -1, hair)
    blk(1, 0, hair); blk(6, 0, hair)

    # Törzs (4x5)
    for y in range(4, 9):
        for x in range(2, 6):
            blk(x, y, suit)

    # Embléma
    blk(3, 5, accent); blk(4, 5, accent)

    # Karok
    for y in range(4, 9):
        for x in (0, 1):
            blk(x, y, suit)
        for x in (6, 7):
            blk(x, y, suit)

    # Kesztyű dísz
    blk(1, 8, accent); blk(6, 8, accent)

    # Lábak
    for y in range(9, 13):
        for x in (2, 3):
            blk(x, y, suit)
        for x in (4, 5):
            blk(x, y, suit)

    for x in (2, 3, 4, 5):
        blk(x, 13, boot)

def draw_mc_hacker(c, base_x=250, base_y=16, scale=1.0):
    B = int(16 * scale)
    D = int(5 * scale)

    skin   = "#e6d2c3"
    hoodie = "#222222"
    neon   = "#35ff7a"
    boot   = "#151515"

    def blk(cx, cy, col):
        draw_block(c, base_x + cx*B, base_y + cy*B, w=B, h=B, depth=D, base=col)

    # Fej
    for i in range(4):
        for j in range(4):
            blk(2+i, 0+j, skin)

    # Kapucni perem
    for i in range(6):
        blk(1+i, -1, hoodie)
    blk(1, 0, hoodie); blk(6, 0, hoodie)

    # Törzs
    for y in range(4, 9):
        for x in range(2, 6):
            blk(x, y, hoodie)

    # Neon csík
    for x in (2, 3, 4, 5):
        blk(x, 6, neon)

    # Karok
    for y in range(4, 9):
        for x in (0, 1, 6, 7):
            blk(x, y, hoodie)

    # Lábak
    for y in range(9, 13):
        for x in (2, 3, 4, 5):
            blk(x, y, hoodie)

    for x in (2, 3, 4, 5):
        blk(x, 13, boot)

def hero_bubble(c, x, y, w, h, text, fill="#FFF1ED", outline=KY_ORANGE, fg=KY_CHARCOAL):
    rounded_rect(c, x, y, x+w, y+h, r=12, fill=fill, outline=outline, width=2)
    return c.create_text(x+10, y+h/2, text=text, anchor="w", font=("Arial", 11, "bold"), fill=fg)

# ---- App ----------------------------------------------------------------------
class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Székesfehérvári KiberKaland – Kattintgatós Kvíz")

        # -- ÚJ: automatikus, 14"-ra optimalizált ablakméret --
        self._auto_geometry()
        self.root.minsize(980, 640)

        self.root.configure(bg=KY_BG)

        # font fallback
        import tkinter.font as tkfont
        fams = set(tkfont.families())
        for fam in ("Inter", "IBM Plex Sans", "Segoe UI", "Arial"):
            if fam in fams:
                self.FONT = fam
                break
        else:
            self.FONT = "Arial"

        # runtime állapot
        self.score = 0
        self.hacker = 0
        self.index = 0
        self.locked = False
        self._style_ready = False
        self.asset_mode = "auto"  # "auto" = pixar ha van, különben voxel
        self.hero_left_img = None
        self.hero_right_img = None
        self.hero_left_id = None
        self.hero_right_id = None
        self.bubble_left_id = None
        self.bubble_right_id = None

        # hang asset utak
        self.sfx = {
            "click":  os.path.join(ASSET_DIR, "sfx_click.wav"),
            "ok":     os.path.join(ASSET_DIR, "sfx_correct.wav"),
            "wrong":  os.path.join(ASSET_DIR, "sfx_wrong.wav"),
        }

        # UI gyökér
        self.container = tk.Frame(root, bg=KY_BG)
        self.container.pack(fill="both", expand=True, padx=28, pady=28)

        # logók
        self.logo_left_img = load_logo(LOGO_LEFT_PATH)
        self.logo_right_img = load_logo(LOGO_RIGHT_PATH)

        # Intro képernyő
        self.build_intro()

        # wraplength reszponzív finomhang
        self.root.bind("<Configure>", self._on_resize)

    # -- ÚJ: automatikus méretezés, hogy 14" kijelzőn is minden elférjen --
    def _auto_geometry(self):
        try:
            self.root.update_idletasks()
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            # cél: 80% szélesség/magasság, de maradjunk a korábbi maximumok alatt
            target_w = min(1120, max(980, int(sw * 0.8)))
            target_h = min(820,  max(640, int(sh * 0.8)))
            # legyen egy biztos fejterünk az OS tálcának/menüsornak
            if target_h > sh - 80:
                target_h = sh - 80
            x = (sw - target_w) // 2
            y = (sh - target_h) // 2
            self.root.geometry(f"{target_w}x{target_h}+{x}+{y}")
        except Exception:
            # safe fallback
            self.root.geometry("1024x700")

    # --------- util ---------
    def f(self, size, bold=False, italic=False):
        if italic and bold:
            return (self.FONT, size, "bold italic")
        if italic:
            return (self.FONT, size, "italic")
        return (self.FONT, size, "bold") if bold else (self.FONT, size)

    def clear(self):
        for w in self.container.winfo_children():
            w.destroy()

    def build_header(self, parent, title_text):
        header = tk.Frame(parent, bg=KY_BG)
        header.pack(fill="x", pady=(0, 14))

        left = tk.Label(header, bg=KY_BG)
        left.pack(side="left", padx=(0, 12))

        center = tk.Label(header, text=title_text, bg=KY_BG, fg=KY_CHARCOAL, font=self.f(22, True))
        center.pack(side="left", expand=True)

        right = tk.Label(header, bg=KY_BG)
        right.pack(side="right", padx=(12, 0))

        if self.logo_left_img is not None:
            left.config(image=self.logo_left_img)
        else:
            left.config(text="Székesfehérvár", fg="#6b7280", font=self.f(12, True))

        if self.logo_right_img is not None:
            right.config(image=self.logo_right_img)
        else:
            right.config(text="Kyndryl", fg="#6b7280", font=self.f(12, True))

        underline = tk.Frame(parent, height=3, bg=KY_ORANGE)
        underline.pack(fill="x", pady=(0, 10))

    def _ensure_style(self):
        if self._style_ready:
            return
        style = ttk.Style()
        try:
            style.theme_use('default')
        except Exception:
            pass
        style.configure("TProgressbar", thickness=12)
        self._style_ready = True

    def _on_resize(self, event):
        # dinamikus wraplength a kérdés és lead szöveghez, + gombszöveg tördelés
        try:
            if hasattr(self, "lead_label") and self.lead_label.winfo_exists():
                w = max(520, min(720, int(event.width * 0.55)))
                self.lead_label.config(wraplength=w)
            if hasattr(self, "question_label") and self.question_label.winfo_exists():
                w = max(520, min(720, int(event.width * 0.55)))
                self.question_label.config(wraplength=w)
            if hasattr(self, "answer_buttons"):
                compact = event.height < 740
                for btn in self.answer_buttons:
                    if btn.winfo_exists():
                        btn.config(
                            wraplength=max(380, min(600, int(event.width * 0.4))),
                            pady=(8 if compact else 10)
                        )
        except Exception:
            pass
    # --------- kezdő képernyő ---------
    def build_intro(self):
        self.clear()
        self.build_header(self.container, "A Székesfehérvári KiberKaland")

        card = tk.Frame(self.container, bg=KY_SURFACE)
        card.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(
            card,
            text="Kattints a Start gombra és mentsd meg a várost a kiberbűnözőktől!",
            bg=KY_SURFACE, fg=KY_CHARCOAL, font=self.f(16, True)
        ).pack(pady=(18, 6))

        tk.Label(
            card, text=STORY_INTRO, justify="left",
            bg=KY_SURFACE, fg=KY_CHARCOAL, font=self.f(12), wraplength=980
        ).pack(padx=24, pady=8, anchor="w")

        start_btn = tk.Button(
            card, text="Start ▶", command=self.start_quiz,
            bg=KY_ORANGE, fg="white", activebackground=KY_ORANGE,
            font=self.f(16, True), bd=0, padx=18, pady=10, cursor="hand2"
        )
        start_btn.pack(pady=20)

        tk.Label(
            card,
            text="Tipp: Figyeld a gyanús jeleket! https, domain, csatolmány, jelszó, frissítés…",
            bg=KY_SURFACE, fg="#6b7280", font=self.f(11)
        ).pack(pady=(0, 16))

        # Egyszerű módváltó a képi stílushoz
        toggle_frame = tk.Frame(card, bg=KY_SURFACE)
        toggle_frame.pack(pady=(0, 12))
        tk.Label(toggle_frame, text="Stílus:", bg=KY_SURFACE, fg=KY_CHARCOAL, font=self.f(11, True)).pack(side="left")
        var = tk.StringVar(value=self.asset_mode)

        def on_style_change():
            self.asset_mode = var.get()
        for mode, text in (("auto", "Auto (Pixar ha van)"), ("voxel", "Voxel")):
            tk.Radiobutton(toggle_frame, text=text, variable=var, value=mode,
                           command=on_style_change, bg=KY_SURFACE, fg=KY_CHARCOAL,
                           selectcolor="#F3F4F6", font=self.f(11)).pack(side="left", padx=8)

    # --------- játék indítása ---------
    def start_quiz(self):
        self._play_sfx("click")
        os.makedirs(ASSET_DIR, exist_ok=True)

        # Pixar preferencia (auto esetben próbáljuk a pixar_* képeket)
        use_pixar = False
        if self.asset_mode == "voxel":
            use_pixar = False
        else:
            # auto: pixar ha elérhető
            if any(os.path.exists(os.path.join(ASSET_DIR, f"pixar_defender{ext}"))
                   for ext in (".png", ".webp", ".jpg", ".jpeg", ".gif")) and \
               any(os.path.exists(os.path.join(ASSET_DIR, f"pixar_hacker{ext}"))
                   for ext in (".png", ".webp", ".jpg", ".jpeg", ".gif")):
                use_pixar = True

        if use_pixar:
            self.hero_left_img  = load_asset_scaled("pixar_defender", HERO_W//2-20, HERO_H-20)
            self.hero_right_img = load_asset_scaled("pixar_hacker",   HERO_W//2-20, HERO_H-20)
        else:
            self.hero_left_img  = load_asset_scaled("mc_defender", HERO_W//2-20, HERO_H-20)
            self.hero_right_img = load_asset_scaled("mc_hacker",   HERO_W//2-20, HERO_H-20)

        self.score = 0
        self.hacker = 0
        self.index = 0
        self.build_quiz_ui()
        self.show_question()

    def build_quiz_ui(self):
        self.clear()
        self.build_header(self.container, "Kiberdetektív küldetés")

        top = tk.Frame(self.container, bg=KY_BG)
        top.pack(fill="x")
        self.score_lbl = tk.Label(top, text="Pont: 0", bg=KY_BG, fg=KY_CHARCOAL, font=self.f(14))
        self.score_lbl.pack(side="left", pady=6)

        self._ensure_style()
        self.progress = ttk.Progressbar(top, mode="determinate", length=360, maximum=100)
        self.progress.pack(side="right", pady=6)

        body = tk.Frame(self.container, bg=KY_SURFACE)
        body.pack(fill="both", expand=True, pady=12)

        content = tk.Frame(body, bg=KY_SURFACE)
        content.pack(fill="both", expand=True, padx=14, pady=14)

        left = tk.Frame(content, bg=KY_SURFACE)
        left.pack(side="left", fill="both", expand=True)
        right = tk.Frame(content, bg=KY_SURFACE)
        right.pack(side="right", fill="y")

        # Lead (rávezetés) és kérdés
        self.lead_label = tk.Label(
            left, text="", bg=KY_SURFACE, fg="#374151", font=self.f(13, italic=True),
            wraplength=660, justify="left"
        )
        self.lead_label.pack(padx=6, pady=(0, 6), anchor="w")

        self.question_label = tk.Label(
            left, text="", bg=KY_SURFACE, fg=KY_CHARCOAL, font=self.f(18, True),
            wraplength=660, justify="left"
        )
        self.question_label.pack(padx=6, pady=(4, 10), anchor="w")

        self.buttons_frame = tk.Frame(left, bg=KY_SURFACE)
        self.buttons_frame.pack(padx=6, pady=4, anchor="w")

        self.answer_buttons = []
        for i in range(4):
            btn = tk.Button(
                self.buttons_frame, text="", bg="#F1F3F5", fg=KY_CHARCOAL,
                activebackground="#F1F3F5", font=self.f(14), bd=0, padx=14, pady=10,
                cursor="hand2", command=lambda i=i: self.on_answer(i),
                wraplength=520, justify="left"
            )
            btn.grid(row=i, column=0, sticky="w", pady=8)
            btn.configure(highlightthickness=2, highlightbackground=KY_ORANGE)
            self.answer_buttons.append(btn)

        # kérdés vizuál
        self.q_canvas = tk.Canvas(
            right, width=CANVAS_W, height=CANVAS_H,
            bg=KY_BG, highlightthickness=1, highlightbackground=KY_BORDER
        )
        self.q_canvas.pack(padx=6, pady=(6, 8))

        # hősök vászon
        self.hero_canvas = tk.Canvas(
            right, width=HERO_W, height=HERO_H,
            bg=KY_BG, highlightthickness=1, highlightbackground=KY_BORDER
        )
        self.hero_canvas.pack(padx=6, pady=(0, 6))

        bottom = tk.Frame(self.container, bg=KY_BG)
        bottom.pack(fill="x")
        self.counter_lbl = tk.Label(
            bottom, text="🛡️ Védők: 0   |   🕶️ Hacker: 0",
            bg=KY_BG, fg=KY_CHARCOAL, font=self.f(13, True)
        )
        self.counter_lbl.pack(side="left", pady=4)

        self.next_btn = tk.Button(
            bottom, text="Következő ▶", command=self.next_question, state="disabled",
            bg=KY_ORANGE, fg="white", activebackground=KY_ORANGE, font=self.f(14, True),
            bd=0, padx=16, pady=10, cursor="hand2"
        )
        self.next_btn.pack(side="right", pady=4)

    def show_question(self):
        self.locked = False
        q = QUESTIONS[self.index]
        self.progress['value'] = (self.index / len(QUESTIONS)) * 100
        self.lead_label.config(text=q.get("lead", ""))
        self.question_label.config(text=q["question"])
        self.next_btn.config(state="disabled")

        # válaszok
        for i, btn in enumerate(self.answer_buttons):
            if i < len(q["answers"]):
                btn.config(text=f"{chr(65+i)}) {q['answers'][i]}", state="normal", bg="#F1F3F5", fg=KY_CHARCOAL)
                btn.grid()
            else:
                btn.grid_remove()

        # kérdés vizuál
        self.q_canvas.delete("all")
        # a megfelelő vizualizáció meghívása az aktuális indexhez (← JAVÍTVA)
        QUESTION_VIS[self.index](self.q_canvas)

        # hősök
        self.draw_heroes("neutral")

        self.counter_lbl.config(text=f"🛡️ Védők: {self.score}   |   🕶️ Hacker: {self.hacker}")

    # --------- hősök és animáció ---------
    def draw_heroes(self, mood="neutral"):
        c = self.hero_canvas
        c.delete("all")
        self.hero_left_id = None
        self.hero_right_id = None
        self.bubble_left_id = None
        self.bubble_right_id = None

        # bal: védő
        if self.hero_left_img is not None:
            self.hero_left_id = c.create_image(110, HERO_H//2, image=self.hero_left_img)
        else:
            draw_mc_defender(c, base_x=26, base_y=16, scale=1.0)

        # jobb: hacker
        if self.hero_right_img is not None:
            self.hero_right_id = c.create_image(HERO_W-110, HERO_H//2, image=self.hero_right_img)
        else:
            draw_mc_hacker(c, base_x=250, base_y=16, scale=1.0)

        # beszédbubik
        if mood == "correct":
            self.bubble_left_id = hero_bubble(c, 20, 130, 210, 48, "Szép munka! 🛡️", fill="#E8FFF1", outline=GREEN_OK)
            if self.hero_left_id:
                self._bounce(c, self.hero_left_id)
            else:
                self._float(c, self.bubble_left_id)
        elif mood == "wrong":
            self.bubble_right_id = hero_bubble(c, HERO_W-230, 130, 210, 48, "Hoppá! Próbáld újra 😈", fill="#FFECEC", outline=RED_ERR)
            if self.hero_right_id:
                self._bounce(c, self.hero_right_id)
            else:
                self._float(c, self.bubble_right_id)
        else:
            self.bubble_left_id  = hero_bubble(c, 20, 130, 210, 48, "Indul a küldetés!", fill="#FFF8F3", outline=KY_ORANGE)
            self.bubble_right_id = hero_bubble(c, HERO_W-230, 130, 210, 48, "Hehe… nem lesz könnyű!", fill="#F3F4F6", outline=KY_BORDER)

    def _bounce(self, canvas, item_id, height=12, duration_ms=220):
        # egyszerű fel-le ugrás
        steps = 10
        up_steps = steps // 2
        down_steps = steps - up_steps
        dy_up = -height / up_steps
        dy_down = height / down_steps
        interval = max(12, duration_ms // steps)

        def step(i=0):
            if i < up_steps:
                canvas.move(item_id, 0, dy_up)
                canvas.after(interval, step, i+1)
            elif i < steps:
                canvas.move(item_id, 0, dy_down)
                canvas.after(interval, step, i+1)

        step(0)

    def _float(self, canvas, item_id, amplitude=6, duration_ms=300):
        # buborék kis lebegő animáció
        steps = 12
        interval = max(12, duration_ms // steps)
        seq = [-1,-1,-1,0,0,1,1,1,0,0,-1,0]

        def step(i=0):
            if i >= len(seq):
                return
            canvas.move(item_id, 0, seq[i])
            canvas.after(interval, step, i+1)

        step(0)

    # --------- hang ---------
    def _play_sfx(self, kind):
        path = self.sfx.get(kind)
        if path and os.path.exists(path) and WINSOUND_AVAILABLE:
            try:
                winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                return
            except Exception:
                pass
        # fallback
        try:
            self.root.bell()
        except Exception:
            pass
    # --------- válaszkezelés ---------
    def on_answer(self, idx):
        if self.locked:
            return
        self.locked = True

        q = QUESTIONS[self.index]
        correct = q["correct"]

        for i, btn in enumerate(self.answer_buttons):
            if not btn.winfo_viewable():
                continue
            if i == correct:
                btn.config(bg="#D1FAE5", fg="#065f46")
            elif i == idx:
                btn.config(bg="#FEE2E2", fg="#7f1d1d")
            else:
                btn.config(state="disabled")

        if idx == correct:
            self.score += 1
            self.draw_heroes("correct")
            self._play_sfx("ok")
            messagebox.showinfo("Helyes! 🛡️", q["explanation"])
        else:
            self.hacker += 1
            self.draw_heroes("wrong")
            self._play_sfx("wrong")
            messagebox.showerror("Hoppá! 🕶️", q["explanation"])

        self.score_lbl.config(text=f"Pont: {self.score}")
        self.counter_lbl.config(text=f"🛡️ Védők: {self.score}   |   🕶️ Hacker: {self.hacker}")
        self.next_btn.config(state="normal")

    def next_question(self):
        self._play_sfx("click")
        self.index += 1
        if self.index >= len(QUESTIONS):
            self.show_result()
        else:
            self.show_question()

    # --------- eredmény + mentés + statisztika ---------
    def _save_score(self, record: dict):
        os.makedirs(SAVE_DIR, exist_ok=True)
        try:
            with open(SCORES_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception as e:
            print("Mentési hiba:", e)

    def _read_scores(self):
        if not os.path.exists(SCORES_PATH):
            return []
        rows = []
        try:
            with open(SCORES_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rows.append(json.loads(line))
                    except Exception:
                        pass
        except Exception:
            pass
        return rows

    def _open_stats(self):
        data = self._read_scores()
        win = tk.Toplevel(self.root)
        win.title("Statisztika")
        win.configure(bg=KY_BG)
        tk.Label(win, text="Játékstatisztika", bg=KY_BG, fg=KY_CHARCOAL, font=self.f(18, True)).pack(pady=(10, 6))

        if not data:
            tk.Label(win, text="Még nincs mentett eredmény.", bg=KY_BG, fg="#6b7280", font=self.f(12)).pack(pady=10)
            return

        total_games = len(data)
        best_pct = max(d.get("pct", 0) for d in data)
        avg_pct = sum(d.get("pct", 0) for d in data)/total_games
        last5 = data[-5:]

        info = f"Lejátszott körök: {total_games}\nLegjobb: {best_pct:.0f}%\nÁtlag: {avg_pct:.1f}%"
        tk.Label(win, text=info, bg=KY_BG, fg=KY_CHARCOAL, font=self.f(13)).pack(pady=8)

        frame = tk.Frame(win, bg=KY_BG)
        frame.pack(padx=12, pady=8, fill="x")
        tk.Label(frame, text="Utolsó 5 kör:", bg=KY_BG, fg=KY_CHARCOAL, font=self.f(12, True)).pack(anchor="w")
        for d in last5:
            ts = d.get("ts", "")
            sc = d.get("score", 0)
            tot = d.get("total", 0)
            pct = d.get("pct", 0)
            res = f" - {ts}: {sc}/{tot} pont • {pct:.0f}% (V:{d.get('def',0)} | H:{d.get('hack',0)})"
            tk.Label(frame, text=res, bg=KY_BG, fg="#374151", font=self.f(11)).pack(anchor="w")

    def show_result(self):
        self.clear()
        self.build_header(self.container, "Küldetés vége")

        card = tk.Frame(self.container, bg=KY_SURFACE)
        card.pack(fill="both", expand=True, padx=10, pady=10)

        total = len(QUESTIONS)
        pct = float(self.score)/total*100 if total else 0.0
        defenders_win = self.score >= self.hacker

        tk.Label(card, text="Eredmény", bg=KY_SURFACE, fg=KY_CHARCOAL, font=self.f(26, True)).pack(pady=(24, 6))
        tk.Label(
            card,
            text=f"{self.score}/{total} pont  •  {pct:.0f}%   |   🛡️ Védők: {self.score}  •  🕶️ Hacker: {self.hacker}",
            bg=KY_SURFACE, fg=KY_CHARCOAL, font=self.f(16)
        ).pack(pady=(0, 16))

        msg = ("Fantasztikus! Székesfehérvár biztonságban – igazi kiberhősök vagytok! 🌟"
               if defenders_win else "Most a hackerek állnak jobban, de tanultunk – jöhet még egy kör! 🔄")
        tk.Label(card, text=msg, wraplength=980, justify="left", bg=KY_SURFACE, fg=KY_CHARCOAL, font=self.f(13)).pack(padx=24, pady=(0, 16), anchor="w")

        canv = tk.Canvas(card, width=HERO_W, height=HERO_H, bg=KY_BG, highlightthickness=1, highlightbackground=KY_BORDER)
        canv.pack(pady=6)
        if self.hero_left_img is not None:
            canv.create_image(110, HERO_H//2, image=self.hero_left_img)
        else:
            draw_mc_defender(canv, base_x=26, base_y=16, scale=1.0)

        if self.hero_right_img is not None:
            canv.create_image(HERO_W-110, HERO_H//2, image=self.hero_right_img)
        else:
            draw_mc_hacker(canv, base_x=250, base_y=16, scale=1.0)

        if defenders_win:
            hero_bubble(canv, 20, 130, 210, 48, "Győzelem! 🎉", fill="#E8FFF1", outline=GREEN_OK)
        else:
            hero_bubble(canv, HERO_W-230, 130, 210, 48, "Legközelebb mi nyerünk! 💥", fill="#FFF1ED", outline=KY_ORANGE)

        # gombok
        btns = tk.Frame(card, bg=KY_SURFACE)
        btns.pack(pady=12)
        tk.Button(
            btns, text="Újrajátszás ↻", command=self.start_quiz,
            bg=KY_ORANGE, fg="white", activebackground=KY_ORANGE,
            font=self.f(14, True), bd=0, padx=16, pady=10, cursor="hand2"
        ).pack(side="left", padx=6)
        tk.Button(
            btns, text="Statisztika 📊", command=self._open_stats,
            bg="#F1F3F5", fg=KY_CHARCOAL, activebackground="#F1F3F5",
            font=self.f(13), bd=0, padx=16, pady=10, cursor="hand2"
        ).pack(side="left", padx=6)
        tk.Button(
            btns, text="Kilépés", command=self.root.destroy,
            bg="#F1F3F5", fg=KY_CHARCOAL, activebackground="#F1F3F5",
            font=self.f(13), bd=0, padx=16, pady=10, cursor="hand2"
        ).pack(side="left", padx=6)

        # mentés
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rec = {"ts": ts, "score": self.score, "hack": self.hacker, "def": self.score, "total": len(QUESTIONS), "pct": round(pct, 2)}
        self._save_score(rec)

# ---- Futtatás -----------------------------------------------------------------
def main():
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
