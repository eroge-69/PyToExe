import os
import socket
import threading
import time
import hashlib
import pyotp
import qrcode
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import simpledialog, messagebox
from flask import Flask, request, jsonify

SECRET_FILE = "secret.key"
PASSWORD_FILE = "password.key"   
OTP_INTERVAL = 30
FLASK_PORT = 5000
QR_SIZE = 400
AUTO_LOCK_AFTER = 5  


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def load_or_create_secret(path=SECRET_FILE):
    if os.path.exists(path):
        with open(path, "r") as f:
            s = f.read().strip()
            if s:
                return s
    s = pyotp.random_base32()
    with open(path, "w") as f:
        f.write(s)
    return s

def ensure_password():
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, "r") as f:
            return f.read().strip()
    return None

def set_password_hash(h):
    with open(PASSWORD_FILE, "w") as f:
        f.write(h)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

secret = load_or_create_secret()
totp = pyotp.TOTP(secret, interval=OTP_INTERVAL)
LOCAL_IP = get_local_ip()


app = Flask(__name__)
state = {"unlocked": False, "last_unlock_time": None, "last_attempt_ok": None, "last_method": None}

@app.route("/unlock", methods=["GET"])
def unlock_route():
    otp = request.args.get("otp", "")
    current = totp.now()
    valid = (otp == current) or (otp == totp.at(int(time.time()) - OTP_INTERVAL)) or (otp == totp.at(int(time.time()) + OTP_INTERVAL))
    state["last_attempt_ok"] = valid
    state["last_method"] = "qr"
    if valid:
        state["unlocked"] = True
        state["last_unlock_time"] = time.time()
        return jsonify({"status": "ok", "message": "Kilit açıldı."})
    else:
        return jsonify({"status": "error", "message": "Geçersiz OTP."}), 401

@app.route("/status", methods=["GET"])
def status_route():
    return jsonify(state)

def run_flask():
    app.run(host=LOCAL_IP, port=FLASK_PORT, debug=False, threaded=True)


class KioskUnlockGUI:
    def __init__(self, secret, totp, ip, port):
        self.secret = secret
        self.totp = totp
        self.ip = ip
        self.port = port
        self.root = tk.Tk()
        self.root.title("E-Kilit - Kiosk")
        
        self.root.attributes("-fullscreen", True)
        
        self.root.overrideredirect(True)
        self.root.configure(bg="#0b0c10")
        
        self.root.attributes("-topmost", True)

        self.root.protocol("WM_DELETE_WINDOW", self.block_close)

        
        self.root.bind_all("<Alt-F4>", lambda e: "break")
        self.root.bind_all("<Escape>", lambda e: "break")
        self.root.bind_all("<Control-w>", lambda e: "break")
        self.root.bind_all("<Control-q>", lambda e: "break")

       
        hdr = tk.Label(self.root, text="🔒 E-Kilit — Lütfen QR'ı okutun veya şifre girin", font=("Segoe UI", 26, "bold"),
                       fg="#ffffff", bg="#0b0c10")
        hdr.pack(pady=(20,10))

        
        frame = tk.Frame(self.root, bg="#0b0c10")
        frame.pack(expand=True, fill="both", padx=60, pady=20)

        
        left = tk.Frame(frame, bg="#0b0c10")
        left.pack(side="left", expand=True, fill="both", padx=(20,40))

        lbl_info = tk.Label(left, text="Şifre (veya Authenticator'dan OTP):", font=("Segoe UI", 18),
                            fg="#c9d1d9", bg="#0b0c10")
        lbl_info.pack(anchor="w", pady=(10,8))

        self.pw_entry = tk.Entry(left, font=("Segoe UI", 18), show="*")
        self.pw_entry.pack(anchor="w", pady=(0,12), ipady=8, fill="x")

        btn_frame = tk.Frame(left, bg="#0b0c10")
        btn_frame.pack(anchor="w", pady=(6,6))

        self.login_btn = tk.Button(btn_frame, text="Giriş Yap", font=("Segoe UI", 14), command=self.try_password)
        self.login_btn.pack(side="left", padx=(0,10))

        
        
        self.msg_var = tk.StringVar(value="")
        self.msg_label = tk.Label(left, textvariable=self.msg_var, font=("Segoe UI", 12), fg="#ff6666", bg="#0b0c10")
        self.msg_label.pack(anchor="w", pady=(8,0))

      
        right = tk.Frame(frame, bg="#0b0c10")
        right.pack(side="right", padx=(40,20))

        qinfo = tk.Label(right, text=f"Telefonla tara:", font=("Segoe UI", 12),
                         fg="#c9d1d9", bg="#0b0c10", justify="center")
        qinfo.pack(pady=(0,10))

        self.qr_label = tk.Label(right, bg="#0b0c10")
        self.qr_label.pack()

        
        self.status_var = tk.StringVar(value="Durum: KAPALI")
        self.status_label = tk.Label(self.root, textvariable=self.status_var, font=("Segoe UI", 16, "bold"),
                                     fg="#ffd369", bg="#0b0c10")
        self.status_label.pack(pady=(10,18))

        
        self.update_thread = threading.Thread(target=self.qr_update_loop, daemon=True)
        self.update_thread.start()

        self.state_thread = threading.Thread(target=self.state_watcher, daemon=True)
        self.state_thread.start()

    def block_close(self):
        
        pass

    def try_password(self):
        entered = self.pw_entry.get().strip()
        if not entered:
            self.msg_var.set("Lütfen parola veya OTP girin.")
            return
        
        stored_hash = None
        if os.path.exists(PASSWORD_FILE):
            with open(PASSWORD_FILE, "r") as f:
                stored_hash = f.read().strip()
        if stored_hash and sha256_hex(entered) == stored_hash:
            self.unlock("password")
            return
        
        current = self.totp.now()
        valid = (entered == current) or (entered == self.totp.at(int(time.time()) - OTP_INTERVAL)) or (entered == self.totp.at(int(time.time()) + OTP_INTERVAL))
        if valid:
            self.unlock("manual_otp")
            return
        self.msg_var.set("Yanlış parola/OTP.")
        

    def show_current_otp(self):
        
        msg = f"Mevcut OTP: {self.totp.now()}"
        messagebox.showinfo("Current OTP (dev)", msg)

    def unlock(self, method):
        state["unlocked"] = True
        state["last_unlock_time"] = time.time()
        state["last_attempt_ok"] = True
        state["last_method"] = method
       
        self.status_var.set("Durum: AÇILDI")
        self.status_label.config(fg="#66ff99")
        self.msg_var.set("Giriş başarılı. Bilgisayar açılıyor...")
       
        def do_close():
            time.sleep(AUTO_LOCK_AFTER)
            
            state["unlocked"] = False
            self.status_var.set("Durum: KAPALI")
            self.status_label.config(fg="#ffd369")
            self.msg_var.set("")
            
            try:
                self.root.destroy()
            except Exception:
                pass
        threading.Thread(target=do_close, daemon=True).start()

    def qr_update_loop(self):
        while True:
            otp = self.totp.now()
            url = f"http://{self.ip}:{self.port}/unlock?otp={otp}"
            qr = qrcode.QRCode(box_size=10, border=2)
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white").resize((QR_SIZE, QR_SIZE))
            photo = ImageTk.PhotoImage(img)
            def set_img():
                self.qr_label.config(image=photo)
                self.qr_label.image = photo
            self.root.after(0, set_img)
         
            for _ in range(OTP_INTERVAL):
                time.sleep(1)

    def state_watcher(self):
        while True:
            if state.get("unlocked"):
                ts = state.get("last_unlock_time")
                if ts:
                    timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))
                    self.root.after(0, lambda: self.status_var.set(f"Durum: AÇILDI ({state.get('last_method')})"))
                    self.root.after(0, lambda: self.status_label.config(fg="#66ff99"))
                    self.root.after(0, lambda: self.msg_var.set(f"Açıldı: {timestr}"))
                    
                    time.sleep(AUTO_LOCK_AFTER)
                    state["unlocked"] = False
                    self.root.after(0, lambda: self.status_var.set("Durum: KAPALI"))
                    self.root.after(0, lambda: self.status_label.config(fg="#ffd369"))
                    self.root.after(0, lambda: self.msg_var.set(""))
            else:
                time.sleep(1)

    def run(self):
        self.root.mainloop()



def setup_password_if_missing():
    stored = ensure_password()
    if stored:
        return stored
    
    tmp = tk.Tk()
    tmp.withdraw()
    messagebox.showinfo("Kurulum", "İlk kurulum. Lütfen E-Kilit için bir parola belirleyin.")
    while True:
        p1 = simpledialog.askstring("Parola belirle", "Yeni parola:", show="*")
        if p1 is None:
         
            messagebox.showwarning("Durduruldu", "Kurulum iptal edildi. Program sonlandırılıyor.")
            tmp.destroy()
            raise SystemExit()
        p2 = simpledialog.askstring("Parola tekrar", "Yeni parola (tekrar):", show="*")
        if p2 is None:
            messagebox.showwarning("Durduruldu", "Kurulum iptal edildi. Program sonlandırılıyor.")
            tmp.destroy()
            raise SystemExit()
        if p1 != p2:
            messagebox.showerror("Hata", "Parolalar eşleşmedi, tekrar deneyin.")
            continue
      
        h = sha256_hex(p1)
        set_password_hash(h)
        messagebox.showinfo("Tamam", "Parola kaydedildi.")
        tmp.destroy()
        return h


if __name__ == "__main__":
    print("E-Kilit kiosk başlatılıyor...")
    print("Local IP:", LOCAL_IP)
    print("Secret dosyası:", SECRET_FILE)
    print("Secret (gizli, saklayın):", secret)
   
    try:
        setup_password_if_missing()
    except SystemExit:
        print("Kurulum iptal edildi.")
        raise

    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    
    gui = KioskUnlockGUI(secret, totp, LOCAL_IP, FLASK_PORT)
    gui.run()
