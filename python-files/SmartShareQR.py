import threading
import re
import tkinter as tk
import webbrowser
import time
import os
import sys

# Try to import optional modules with fallbacks
try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False
    print("QRCode module not available. QR generation will be disabled.")

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False
    print("Pyperclip not available. Clipboard monitoring will be disabled.")

try:
    import winsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False
    print("Winsound not available. Sound effects will be disabled.")

try:
    from PIL import Image, ImageTk, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL/Pillow not available. Image processing will be disabled.")

# ----------------------------
# Config
# ----------------------------
WINDOW_W = 440
WINDOW_H = 720
CLIP_CHECK_MS = 900
FADE_STEPS = 12
FADE_DELAY_MS = 34
ICON_PATH = r"C:\Users\Pumal Wijesundara\Desktop\chat.ico"

# ----------------------------
# Custom Modern Widgets
# ----------------------------
class ModernEntry(tk.Frame):
    def __init__(self, master, width=36, height=36, **kwargs):
        super().__init__(master, bg="#1e1e1e")
        self.canvas = tk.Canvas(self, width=width*10, height=height, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack()
        self.entry = tk.Entry(self, bd=0, bg="#2e2e2e", fg="white",
                              font=("Segoe UI", 12), insertbackground="white")
        self.entry.place(x=5, y=5, width=width*10-10, height=height-10)
    def get(self):
        return self.entry.get()
    def delete(self, start, end):
        self.entry.delete(start, end)
    def insert(self, index, string):
        self.entry.insert(index, string)
    def bind(self, event, callback):
        self.entry.bind(event, callback)

class ModernButton(tk.Canvas):
    def __init__(self, master, text, command=None, width=150, height=40):
        super().__init__(master, width=width, height=height, highlightthickness=0, bg="#1e1e1e")
        self.command = command
        self.width = width
        self.height = height
        self.rect = self.create_rounded_rect(2, 2, width-2, height-2, 12, fill="#0078D7")
        self.text_id = self.create_text(width//2, height//2, text=text, fill="white", font=("Segoe UI Semibold", 12))
        self.bind("<Button-1>", lambda e: self.on_click())
        self.bind("<Enter>", lambda e: self.itemconfig(self.rect, fill="#005A9E"))
        self.bind("<Leave>", lambda e: self.itemconfig(self.rect, fill="#0078D7"))
    def create_rounded_rect(self, x1, y1, x2, y2, r=25, **kwargs):
        points = [
            x1+r, y1, x1+r, y1,
            x2-r, y1, x2-r, y1,
            x2, y1, x2, y1+r, x2, y1+r,
            x2, y2-r, x2, y2-r,
            x2, y2, x2-r, y2, x2-r, y2,
            x1+r, y2, x1+r, y2,
            x1, y2, x1, y2-r, x1, y2-r,
            x1, y1+r, x1, y1+r, x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    def on_click(self):
        if self.command:
            self.command()

# ----------------------------
# Main App
# ----------------------------
class SmartShareQR:
    def __init__(self, master):
        self.master = master
        self.master.title("Smart Share QR")
        self.master.geometry(f"{WINDOW_W}x{WINDOW_H}")
        self.master.configure(bg="#1e1e1e")
        self.master.resizable(False, False)

        # Set custom window icon
        try:
            self.master.iconbitmap(ICON_PATH)
        except Exception as e:
            print(f"Could not load icon: {e}")
            # Continue without custom icon

        # Title
        self.title_label = tk.Label(master, text="📱 Smart Share QR", font=("Segoe UI Semibold", 17),
                                    fg="white", bg="#1e1e1e")
        self.title_label.pack(pady=(12,4))

        # Contact link
        self.contact_label = tk.Label(master, text="Contact Pumal :)", font=("Segoe UI", 9, "underline"),
                                      fg="#6cb2eb", bg="#1e1e1e", cursor="hand2")
        self.contact_label.pack()
        self.contact_label.bind("<Button-1>", lambda e: webbrowser.open("https://cloud.pumalwije.workers.dev/"))
        self.contact_label.bind("<Enter>", lambda e: self.contact_label.config(fg="#8fcfff"))
        self.contact_label.bind("<Leave>", lambda e: self.contact_label.config(fg="#6cb2eb"))

        # URL Section
        self.url_frame = tk.Frame(master, bg="#1e1e1e")
        tk.Label(self.url_frame, text="Enter URL:", fg="white", bg="#1e1e1e", font=("Segoe UI",10,"bold")).pack(pady=2)
        self.url_entry = ModernEntry(self.url_frame)
        self.url_entry.pack(pady=2)
        self.url_entry.entry.bind("<Return>", lambda e: self.generate_qr())  # Enter key triggers QR
        
        # Disable generate button if QR not available
        if QR_AVAILABLE and PIL_AVAILABLE:
            self.url_generate_btn = ModernButton(self.url_frame, text="Generate URL QR", command=self.generate_qr)
        else:
            self.url_generate_btn = ModernButton(self.url_frame, text="QR Feature Disabled", command=None)
            self.url_generate_btn.config(state="disabled")
        self.url_generate_btn.pack(pady=6)
        self.url_frame.pack()

        # QR Display
        self.qr_label = tk.Label(master, bg="#1e1e1e")
        self.qr_label.pack(pady=10)

        # Glowing separator
        self.separator = tk.Frame(master, bg="#2cfcff", height=2)
        self.separator.pack(fill=tk.X, padx=60, pady=(6, 6))

        # Bottom card for dynamic text
        self.bottom_card = tk.Frame(master, bg="#2e2e2e", bd=1, relief=tk.SOLID)
        self.bottom_card.pack(fill=tk.X, padx=20, pady=(4,10))

        # Status messages based on available features
        status_messages = []
        if not QR_AVAILABLE:
            status_messages.append("QR generation disabled - missing qrcode module")
        if not PIL_AVAILABLE:
            status_messages.append("Image processing disabled - missing PIL/Pillow")
        if not CLIPBOARD_AVAILABLE:
            status_messages.append("Clipboard monitoring disabled - missing pyperclip")
            
        if status_messages:
            status_text = " | ".join(status_messages)
        else:
            status_text = "Waiting for a link..."

        # Typing paragraph
        self.typing_text = tk.Label(self.bottom_card, text="", fg="#6cb2eb",
                                    bg="#2e2e2e", font=("Segoe UI", 9), wraplength=400, justify=tk.CENTER)
        self.typing_text.pack(pady=6)

        # Status
        self.status_label = tk.Label(self.bottom_card, text=status_text, font=("Segoe UI", 10),
                                     fg="#a0a0a0", bg="#2e2e2e")
        self.status_label.pack(pady=(0,6))

        # Internals
        self.last_clipboard = ""
        self.qr_image_pil = None
        self.fade_step = 0

        # Dynamic typing text
        self.tips = [
            "Tip: Scan QR with your phone camera!",
            "Hover over 'Contact Pumal' to visit the website!",
            "Copy a URL and it will auto-generate a QR code!",
            "Generated QR codes support neon frame style."
        ]
        self.tip_index = 0
        self.master.after(2000, self.rotate_tips)

        # Clipboard monitor
        if CLIPBOARD_AVAILABLE:
            self.master.after(80, self.monitor_clipboard)

    # ---------------------------- Rotate Tips ----------------------------
    def rotate_tips(self):
        self.typing_text.config(text=self.tips[self.tip_index])
        self.tip_index = (self.tip_index + 1) % len(self.tips)
        self.master.after(4000, self.rotate_tips)

    # ---------------------------- URL QR ----------------------------
    def is_url(self, text):
        if not text: return False
        pattern = re.compile(r'^(https?:\/\/)?(([A-Za-z0-9-]+\.)+[A-Za-z]{2,})(:\d+)?(\/[^\s]*)?$')
        return bool(pattern.match(text))
    def normalize_url(self, url):
        if not url.startswith(("http://","https://")):
            return "https://" + url
        return url
        
    def generate_qr(self):
        if not QR_AVAILABLE or not PIL_AVAILABLE:
            self.status_label.config(text="QR generation disabled - install qrcode and pillow modules")
            return
            
        url = self.url_entry.get().strip()
        if not url: return
        if not self.is_url(url): return
        url = self.normalize_url(url)
        self.url_entry.delete(0, 'end')
        self.url_entry.insert(0, url)
        self.status_label.config(text="Generating QR code…")
        threading.Thread(target=self._generate_qr_thread, args=(url,), daemon=True).start()

    # ---------------------------- QR Generation ----------------------------
    def _generate_qr_thread(self, data):
        if not QR_AVAILABLE or not PIL_AVAILABLE:
            return
            
        qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_H,
                           box_size=10, border=3)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
        img = img.resize((300, 300), Image.LANCZOS)

        # Neon Frame
        draw = ImageDraw.Draw(img)
        glow_color = (44, 252, 255, 255)
        thickness = 6
        for i in range(thickness):
            draw.rectangle([i, i, img.width-i-1, img.height-i-1], outline=glow_color)

        self.qr_image_pil = img
        self.fade_step = 0
        self.master.after(0, self._fade_in_qr)

    def _fade_in_qr(self):
        if self.fade_step <= FADE_STEPS:
            alpha = int(255 * self.fade_step / FADE_STEPS)
            img_copy = self.qr_image_pil.copy()
            alpha_layer = Image.new("L", img_copy.size, color=alpha)
            img_copy.putalpha(alpha_layer)
            tk_img = ImageTk.PhotoImage(img_copy)
            self.qr_label.config(image=tk_img)
            self.qr_label.image = tk_img
            self.fade_step += 1
            self.master.after(FADE_DELAY_MS, self._fade_in_qr)
        else:
            final_img = self.qr_image_pil.convert("RGB")
            tk_final = ImageTk.PhotoImage(final_img)
            self.qr_label.config(image=tk_final)
            self.qr_label.image = tk_final
            self.status_label.config(text="Scan the QR code with your phone")
            if SOUND_AVAILABLE:
                try:
                    winsound.Beep(1000, 120)
                except: 
                    pass

    # ---------------------------- Clipboard ----------------------------
    def monitor_clipboard(self):
        if not CLIPBOARD_AVAILABLE:
            return
            
        try:
            content = pyperclip.paste().strip()
            if content and content != self.last_clipboard and self.is_url(content):
                self.last_clipboard = content
                normalized = self.normalize_url(content)
                self.url_entry.delete(0,'end')
                self.url_entry.insert(0, normalized)
                if QR_AVAILABLE and PIL_AVAILABLE:
                    threading.Thread(target=self._generate_qr_thread, args=(normalized,), daemon=True).start()
        except: 
            pass
        self.master.after(CLIP_CHECK_MS, self.monitor_clipboard)

# ---------------------------- Run ----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    
    # Set custom window icon
    try:
        root.iconbitmap(ICON_PATH)
    except Exception as e:
        print(f"Could not load icon: {e}")
        # Continue without custom icon
    
    app = SmartShareQR(root)
    root.mainloop()