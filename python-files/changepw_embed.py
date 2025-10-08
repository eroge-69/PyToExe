#!/usr/bin/env python3
# -- coding: utf-8 --

"""
CHANGE PASSWORD PB — GUI + Excel + HWID Google Sheet
- Excel: AKUNPOINTBLANK.xlsx (A:ID, B:PASSWORD LAMA, C:PASSWORD BARU, D:STATUS, E:WAKTU)
- Hasil ditulis ke kolom D/E
- HWID wajib aktif (Google Sheet: kolom C=HWID, kolom D='active')
- Tidak bikin folder debug permanen (opsi Debug mode => screenshot saat gagal ke ./_screenshots)
"""

# ---------- auto install helper ----------
def _ensure(pkgs):
    import importlib, subprocess, sys
    for p in pkgs:
        mod = p.split("==")[0].split(">=")[0].strip()
        try:
            importlib.import_module(mod)
        except ImportError:
            try:
                print(f"[auto-install] Installing {p} ...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", p])
            except Exception as e:
                print(f"[auto-install] Gagal install {p}: {e}")

_ensure([
    "selenium>=4.24",
    "webdriver-manager>=4.0",
    "pandas>=2.0",
    "openpyxl>=3.1.0",
    "gspread>=6.0.0",
    "google-auth>=2.0.0",
])
# -----------------------------------------

import os, sys, time, json, threading, queue, traceback, socket
from datetime import datetime

# ---------- single instance (hindari banyak proses) ----------
def acquire_single_instance(lock_port=51673):
    """Return True kalau sukses lock (artinya instance pertama)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("127.0.0.1", lock_port))
        s.listen(1)
        return True
    except OSError:
        return False

# ---------- path helper ----------
def resource_path(relative: str) -> str:
    base = getattr(sys, "_MEIPASS", None) or os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(base, relative)

BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))

# ---------- KONFIG ----------
APP_TITLE = "CHANGE PASSWORD by IG@JASAGBWSDC_PB"
COPYRIGHT_TEXT = "© 2025 IG@WSDCJASAGBWSDC_PB — FB: RIFKI IVANDI. All Rights Reserved."

# Excel
EXCEL_FILE = os.path.join(BASE_DIR, "AKUNPOINTBLANK.xlsx")

# Google Sheets lisensi (kolom C: HWID, kolom D: STATUS=active)
SERVICE_ACCOUNT_FILE = resource_path("service_account.json")
SPREADSHEET_ID = "1lvbh3mAl8UohpHj5SgQrLqaaqXz9sUMcZIcdfIzyibU"
SHEET_NAME = "Sheet1"

# Situs
LOGIN_URL = "https://www.pointblank.id/login/form"
MYINFO_URL = "https://www.pointblank.id/mypage/info"
WAIT_TIMEOUT = 18

# ---------- bridge log ke GUI ----------
_GUI_PUSH = None
def _gui_emit(line: str):
    if callable(_GUI_PUSH):
        try: _GUI_PUSH(line)
        except Exception: pass

def log(msg: str):
    line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    _gui_emit(line)

def now_str(fmt="%Y-%m-%d %H:%M:%S"):
    return datetime.now().strftime(fmt)

def mask_pw(pw, left=2, right=0):
    s = f"{pw}"
    if len(s) <= left + right:
        return "*" * len(s)
    return s[:left] + "*" * (len(s) - left - right) + (s[-right:] if right else "")

def ensure_tmp_screenshot_dir():
    path = os.path.join(BASE_DIR, "_screenshots")
    os.makedirs(path, exist_ok=True)
    return path

# ---------- Excel helpers ----------
import pandas as pd

def read_accounts_from_excel(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Excel tidak ditemukan: {path}")
    df = pd.read_excel(path, engine="openpyxl")

    # pastikan kolom
    if "STATUS" not in df.columns: df["STATUS"] = ""
    if "WAKTU" not in df.columns:  df["WAKTU"]  = ""

    cols_lower = [str(c).strip().lower() for c in df.columns.tolist()]
    col_id  = next((i for i,c in enumerate(cols_lower) if c in ("id","akun","userid","user id")), 0)
    col_old = next((i for i,c in enumerate(cols_lower) if "password lama" in c or c in ("lama","old","old password")), 1)
    col_new = next((i for i,c in enumerate(cols_lower) if "password baru" in c or c in ("baru","new","new password")), 2)

    accounts = []
    for idx, row in df.iterrows():
        uid = "" if pd.isna(row.iloc[col_id]) else str(row.iloc[col_id]).strip()
        opw = "" if pd.isna(row.iloc[col_old]) else str(row.iloc[col_old]).strip()
        npw = "" if pd.isna(row.iloc[col_new]) else str(row.iloc[col_new]).strip()
        if uid and opw and npw:
            accounts.append({
                "row_pandas": idx,
                "id": uid,
                "old_password": opw,
                "new_password": npw
            })
    return df, accounts

def write_result_to_excel(df, row_idx, status_text):
    df.at[row_idx, "STATUS"] = status_text
    df.at[row_idx, "WAKTU"]  = now_str()

def save_excel(df, path):
    df.to_excel(path, index=False, engine="openpyxl")

# ---------- Selenium core ----------
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException

def _robust_new_driver(options):
    """Coba Selenium Manager → fallback webdriver_manager (clear cache dulu)."""
    # 1) Selenium Manager
    try:
        return webdriver.Chrome(options=options)
    except Exception as e1:
        last_err = e1
        # 2) bersihkan cache webdriver_manager biar ambil versi baru
        try:
            import shutil
            cache_dir = os.path.join(os.path.expanduser("~"), ".wdm")
            shutil.rmtree(cache_dir, ignore_errors=True)
        except Exception:
            pass
        # 3) webdriver_manager
        try:
            from selenium.webdriver.chrome.service import Service as ChromeService
            from webdriver_manager.chrome import ChromeDriverManager
            service = ChromeService(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)
        except Exception as e2:
            raise RuntimeError(
                "Gagal memulai Chrome WebDriver.\n"
                f"Selenium Manager error: {last_err}\n"
                f"webdriver_manager error: {e2}"
            )

def _find_login_fields(driver):
    # Heuristik fleksibel
    inputs = driver.find_elements(By.CSS_SELECTOR, "input")
    vis = [x for x in inputs if x.is_displayed()]
    user_el, pass_el = None, None

    for el in vis:
        t = (el.get_attribute("type") or "").lower()
        attrs = " ".join([(el.get_attribute(k) or "").lower()
                          for k in ("name","id","placeholder","aria-label")])
        if t == "password" or "pass" in attrs:
            pass_el = el; break

    for el in vis:
        t = (el.get_attribute("type") or "").lower()
        attrs = " ".join([(el.get_attribute(k) or "").lower()
                          for k in ("name","id","placeholder","aria-label")])
        if t == "email" or any(k in attrs for k in ("user","id","login","account","username","mail")):
            user_el = el; break

    if not user_el and pass_el:
        try:
            i = vis.index(pass_el)
            for prev in reversed(vis[:i]):
                tt = (prev.get_attribute("type") or "").lower()
                if tt in ("text","email",""):
                    user_el = prev; break
        except Exception:
            pass

    if not user_el and vis: user_el = vis[0]
    if not pass_el and len(vis) > 1: pass_el = vis[1]
    return user_el, pass_el

def _click_edit_and_find_popup(driver):
    # coba klik tombol edit/ubah
    candidates = [
        ("xpath","//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'ubah') or contains(., 'Ganti') or contains(., 'Edit')]"),
        ("css","button.btn-edit"), ("css","a.btn-edit"), ("css","button.edit"),
        ("xpath","//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'edit')]"),
    ]
    clicked = False
    for typ, sel in candidates:
        try:
            el = driver.find_element(By.XPATH, sel) if typ=="xpath" else driver.find_element(By.CSS_SELECTOR, sel)
            if el.is_displayed():
                driver.execute_script("arguments[0].scrollIntoView(true); arguments[0].click();", el)
                clicked = True; break
        except Exception:
            pass

    if not clicked:
        try:
            for e in driver.find_elements(By.XPATH, "//button|//a"):
                txt = (e.text or "").lower()
                if any(k in txt for k in ("ubah","ganti","edit","profil","profile")) and e.is_displayed():
                    driver.execute_script("arguments[0].scrollIntoView(true); arguments[0].click();", e)
                    clicked = True; break
        except Exception:
            pass

    time.sleep(0.8)

    # cari field old/new/confirm di popup/form
    pw_inputs = [el for el in driver.find_elements(By.CSS_SELECTOR, "input[type='password']") if el.is_displayed()]
    old_el = new_el = confirm_el = None
    for el in pw_inputs:
        attrs = " ".join([(el.get_attribute(k) or "").lower() for k in ("name","id","placeholder","aria-label")])
        if any(x in attrs for x in ("old","lama","current")): old_el = el
        elif any(x in attrs for x in ("confirm","ulang","repeat")): confirm_el = el
        elif any(x in attrs for x in ("new","baru")): new_el = el
    if not old_el and pw_inputs: old_el = pw_inputs[0]
    if not new_el and len(pw_inputs) >= 2: new_el = pw_inputs[1]
    if not confirm_el and len(pw_inputs) >= 3: confirm_el = pw_inputs[2]

    # tombol simpan
    save_btn = None
    try:
        save_btn = driver.find_element(By.XPATH, "//button[contains(., 'Simpan') or contains(., 'Save') or contains(., 'Ubah') or contains(., 'Confirm') or contains(., 'OK') or contains(., 'Submit')]")
        if not save_btn.is_displayed(): save_btn = None
    except Exception:
        try: save_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        except Exception: save_btn = None

    return old_el, new_el, confirm_el, save_btn

def _click_ok_like_button(driver):
    X = [
        "//button[contains(@class,'swal2-confirm')]",
        "//button[normalize-space(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'))='ok']",
        "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'ok')]",
        "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'confirm')]",
        "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'simpan')]",
        "//button[contains(., 'Ya') or contains(., 'YA') or contains(., 'ya')]",
        "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'tutup') or contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'close')]",
    ]
    for xp in X:
        try:
            for b in driver.find_elements(By.XPATH, xp):
                if b.is_displayed():
                    try: b.click()
                    except Exception: driver.execute_script("arguments[0].click();", b)
                    return True
        except Exception:
            pass
    return False

def _success_notice_present(driver):
    keys = ["password telah diubah","password berhasil diubah","berhasil","sukses","success","updated"]
    try:
        for c in driver.find_elements(By.CSS_SELECTOR, ".swal2-container, .swal2-popup, .modal.show, .alert-success, .toast"):
            if c.is_displayed() and any(k in (c.text or "").lower() for k in keys):
                return True
    except Exception:
        pass
    try:
        page = (driver.page_source or "").lower()
        if any(k in page for k in keys): return True
    except Exception:
        pass
    return False

def change_password_for_account(acc, debug_screenshot=False):
    user_id = str(acc["id"]).strip()
    old_pw  = str(acc["old_password"]).strip()
    new_pw  = str(acc["new_password"]).strip()

    log(f"[{user_id}] START old={mask_pw(old_pw)} new={mask_pw(new_pw)}")
    result = {"id": user_id, "status": "FAILED", "reason": "", "screenshot": ""}

    if not new_pw:
        result["status"] = "SKIPPED"; result["reason"] = "new_password_empty"
        log(f"[{user_id}] SKIPPED: password baru kosong"); return result

    def save_ss(tag):
        if not debug_screenshot:
            return ""
        try:
            ssdir = ensure_tmp_screenshot_dir()
            fn = os.path.join(ssdir, f"{user_id}{tag}{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            driver.save_screenshot(fn)
            return fn
        except Exception:
            return ""

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = _robust_new_driver(options)
    wait = WebDriverWait(driver, WAIT_TIMEOUT)

    def js_set_value(el, val):
        try:
            driver.execute_script("""
                const el = arguments[0]; const v = arguments[1];
                el.focus(); el.value = v;
                el.dispatchEvent(new Event('input', {bubbles:true}));
                el.dispatchEvent(new Event('change', {bubbles:true}));
            """, el, val)
        except Exception:
            try: el.clear(); el.send_keys(val)
            except Exception: pass

    try:
        # --- login ---
        driver.get(LOGIN_URL); time.sleep(0.8)
        user_el, pass_el = _find_login_fields(driver)
        if not user_el or not pass_el:
            result["reason"] = "login_fields_not_found"
            result["screenshot"] = save_ss("login_fields_not_found")
            return result

        js_set_value(user_el, user_id)
        js_set_value(pass_el, old_pw)
        try:
            driver.execute_script("if(typeof sendIt==='function'){sendIt();}else{const b=document.querySelector('button[type=submit],input[type=submit]'); if(b) b.click();}")
        except Exception:
            pass
        time.sleep(1.1)

        # alert login?
        try:
            a = driver.switch_to.alert
            txt = (a.text or "")
            a.accept()
            result["reason"] = f"login_alert: {txt}"
            result["screenshot"] = save_ss("login_alert")
            return result
        except NoAlertPresentException:
            pass

        # --- buka myinfo + langkah verifikasi old password kalau muncul ---
        driver.get(MYINFO_URL); time.sleep(0.9)
        pw_inputs = [el for el in driver.find_elements(By.CSS_SELECTOR, "input[type='password']") if el.is_displayed()]
        if pw_inputs:
            js_set_value(pw_inputs[0], old_pw)
            try:
                pw_inputs[0].send_keys(Keys.ENTER)
            except Exception:
                pass
            time.sleep(1.0)
            # alert setelah verify?
            try:
                a = driver.switch_to.alert
                txt = (a.text or "")
                a.accept()
                result["reason"] = f"verify_alert: {txt}"
                result["screenshot"] = save_ss("verify_alert")
                return result
            except NoAlertPresentException:
                pass

        # --- buka dialog ubah & isi field ---
        old_el, new_el, confirm_el, save_btn = _click_edit_and_find_popup(driver)
        if not (old_el and new_el):
            result["reason"] = "popup_fields_not_found"
            result["screenshot"] = save_ss("popup_fields_not_found")
            return result

        if not confirm_el:
            # fallback: cari lagi
            vis = [el for el in driver.find_elements(By.CSS_SELECTOR, "input[type='password']") if el.is_displayed()]
            for el in vis:
                if el not in (old_el, new_el):
                    confirm_el = el; break
        if not confirm_el:
            result["reason"] = "confirm_field_not_found"
            result["screenshot"] = save_ss("confirm_field_not_found")
            return result

        js_set_value(old_el, old_pw)
        js_set_value(new_el, new_pw)
        js_set_value(confirm_el, new_pw)
        time.sleep(0.15)

        clicked = False
        if save_btn and save_btn.is_displayed():
            try:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", save_btn)
                time.sleep(0.05)
                try: save_btn.click()
                except Exception: driver.execute_script("arguments[0].click();", save_btn)
                clicked = True
            except Exception:
                pass
        if not clicked:
            try:
                confirm_el.send_keys(Keys.ENTER)
                clicked = True
            except Exception:
                pass

        time.sleep(0.6)

        # --- deteksi sukses ---
        end = time.time() + 10
        ok = False
        while time.time() < end:
            try:
                a = driver.switch_to.alert
                t = (a.text or "").lower()
                if any(k in t for k in ("berhasil","sukses","success","telah diubah","updated")):
                    a.accept(); ok = True; break
                else:
                    a.accept()
            except NoAlertPresentException:
                pass
            if _success_notice_present(driver):
                ok = True; break
            time.sleep(0.3)

        if ok:
            _click_ok_like_button(driver)
            result["status"] = "OK"
            log(f"[{user_id}] ✅ Password diubah.")
        else:
            page = (driver.page_source or "").lower()
            if any(k in page for k in ("berhasil","sukses","success","password berhasil","telah diubah","updated")):
                result["status"] = "OK"
                log(f"[{user_id}] ✅ Password kemungkinan besar berhasil (teks halaman).")
            else:
                result["status"] = "FAILED"
                result["reason"] = "no_success_notice_after_change"
                result["screenshot"] = save_ss("no_success_notice_after_change")
                log(f"[{user_id}] ⚠️ Tidak ada notifikasi sukses.")
    except Exception as e:
        result["status"] = "FAILED"
        result["reason"] = f"exception: {e}"
        result["screenshot"] = save_ss("exception")
        log(f"[{user_id}] ERROR: {e}")
        log(traceback.format_exc())
    finally:
        try: driver.quit()
        except Exception: pass

    return result

# ---------- HWID / lisensi ----------
def get_hwid():
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography")
        val, _ = winreg.QueryValueEx(key, "MachineGuid")
        return str(val).strip()
    except Exception:
        return "UNKNOWN"

def gsheet_hwid_active(hwid: str):
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        if not os.path.exists(SERVICE_ACCOUNT_FILE):
            return False, f"service_account.json tidak ditemukan"
        creds = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
        )
        gc = gspread.authorize(creds)
        ws = gc.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
        for r in ws.get_all_values()[1:]:
            if len(r) >= 4 and (r[2] or "").strip() == hwid:
                status = (r[3] or "").strip().lower()
                return (status == "active"), f"status: {status or 'kosong'}"
        return False, "HWID tidak terdaftar"
    except Exception as e:
        return False, f"Sheets error: {e}"

# ---------- GUI ----------
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        if not acquire_single_instance():
            # sudah ada instance lain
            try:
                from tkinter import messagebox as mb
                mb.showinfo("ChangePasswordPB", "Aplikasi sudah berjalan, tutup instance lama dulu.")
            except Exception:
                pass
            sys.exit(0)

        global _GUI_PUSH
        _GUI_PUSH = self._push_log_from_core

        self.title(APP_TITLE)
        self.geometry("1000x650"); self.minsize(900, 520)
        try:
            style = ttk.Style(self); style.theme_use('clam')
        except Exception: pass
        self.configure(bg="white")

        top = ttk.Frame(self); top.pack(fill="x", padx=12, pady=10)
        ttk.Label(top, text="Status HWID:", font=("Segoe UI",10)).pack(side="left")
        self.hwid_lbl = ttk.Label(top, text="mengecek...", foreground="blue", font=("Segoe UI",10))
        self.hwid_lbl.pack(side="left", padx=(6,12))
        ttk.Button(top, text="Copy HWID", command=self.copy_hwid).pack(side="left", padx=(6,8))
        ttk.Button(top, text="CEK HWID ULANG", command=self.check_hwid_async).pack(side="left", padx=(6,8))
        self.debug_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(top, text="Debug mode (screenshot saat gagal)", variable=self.debug_var).pack(side="right")

        btns = ttk.Frame(self); btns.pack(fill="x", padx=12, pady=(0,8))
        self.btn_start = ttk.Button(btns, text="Mulai", command=self.start_batch, state="disabled")
        self.btn_stop  = ttk.Button(btns, text="Stop", command=self.stop_batch, state="disabled")
        self.btn_save  = ttk.Button(btns, text="Download Log (TXT)", command=self.save_log)
        self.btn_start.pack(side="left"); self.btn_stop.pack(side="left", padx=(8,0)); self.btn_save.pack(side="right")

        mid = ttk.Frame(self); mid.pack(fill="both", expand=True, padx=12, pady=8)
        self.log_txt = tk.Text(mid, height=24, wrap="none", bg="white", fg="black", font=("Segoe UI",10))
        self.log_txt.pack(fill="both", expand=True)
        try: self.log_txt.config(insertbackground="black")
        except Exception: pass
        self._write_log(APP_TITLE)
        self._write_log(COPYRIGHT_TEXT)

        foot = ttk.Frame(self); foot.pack(fill="x", padx=12, pady=(4,10))
        ttk.Label(foot, text=COPYRIGHT_TEXT, font=("Segoe UI",9)).pack(side="left")

        self.q = queue.Queue()
        self.worker = None
        self.stop_flag = threading.Event()

        self.after(150, self.check_hwid_async)
        self.after(120, self._drain)

    # ---- HWID
    def copy_hwid(self):
        hwid = get_hwid()
        self.clipboard_clear(); self.clipboard_append(hwid)
        self._write_log(f"HWID {hwid} disalin")

    def check_hwid_async(self):
        self.hwid_lbl.configure(text="mengecek...", foreground="blue")
        self.btn_start.configure(state="disabled")
        threading.Thread(target=self._do_check_hwid_bg, daemon=True).start()

    def _do_check_hwid_bg(self):
        hwid = get_hwid()
        self._write_log(f"HWID: {hwid}")
        ok, reason = gsheet_hwid_active(hwid)
        if ok:
            self._set_hwid_status(f"AKTIF ({hwid})", "green", True)
            self._write_log(f"Lisensi OK - {reason}")
        else:
            self._set_hwid_status(f"TIDAK AKTIF ({hwid}) - {reason}", "red", False)
            self._write_log(f"Lisensi TIDAK AKTIF - {reason}")

    def _set_hwid_status(self, text, color, enable_start):
        self.after(0, lambda: (
            self.hwid_lbl.configure(text=text, foreground=color),
            self.btn_start.configure(state="normal" if enable_start else "disabled")
        ))

    # ---- logging
    def _write_log(self, line: str):
        msg = f"[{datetime.now().strftime('%H:%M:%S')}] {line}\n"
        self.log_txt.configure(state="normal")
        self.log_txt.insert("end", msg)
        self.log_txt.see("end")
        self.log_txt.configure(state="disabled")

    def _push_log_from_core(self, line: str):
        self.q.put(line)

    def _drain(self):
        try:
            while True:
                line = self.q.get_nowait()
                self._write_log(line)
        except queue.Empty:
            pass
        self.after(120, self._drain)

    # ---- batch
    def start_batch(self):
        if self.worker and self.worker.is_alive():
            return
        try:
            self.df, self.accounts = read_accounts_from_excel(EXCEL_FILE)
        except Exception as e:
            messagebox.showerror("Excel", f"Gagal membaca {EXCEL_FILE}\n{e}")
            return
        if not self.accounts:
            messagebox.showwarning("Excel", "Tidak ada baris valid (ID/PASS LAMA/PASS BARU).")
            return
        self.stop_flag.clear()
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self._write_log(f"== Mulai proses batch ({len(self.accounts)} akun) ==")
        self.worker = threading.Thread(target=self._batch_thread, daemon=True)
        self.worker.start()

    def stop_batch(self):
        self.stop_flag.set()
        self.btn_stop.configure(state="disabled")
        self._write_log("== Stop diminta, menunggu proses saat ini selesai ==")

    def _batch_thread(self):
        try:
            for acc in self.accounts:
                if self.stop_flag.is_set():
                    self._write_log("Dihentikan oleh pengguna."); break
                uid = acc["id"]; npw = acc["new_password"]
                self._write_log(f"Proses: {uid} ...")
                try:
                    res = change_password_for_account(acc, debug_screenshot=self.debug_var.get())
                except Exception as e:
                    res = {"id": uid, "status":"FAILED", "reason":f"runtime_error: {e}", "screenshot":""}

                if res["status"] == "OK":
                    write_result_to_excel(self.df, acc["row_pandas"], "DONE")
                    self._write_log(f"{uid} {npw} DONE")
                elif res["status"] == "SKIPPED":
                    write_result_to_excel(self.df, acc["row_pandas"], "SKIPPED")
                    self._write_log(f"{uid} {npw} SKIPPED (password baru kosong)")
                else:
                    reason = res.get("reason","FAILED")
                    write_result_to_excel(self.df, acc["row_pandas"], f"FAILED: {reason}")
                    self._write_log(f"{uid} {npw} FAILED ({reason})")
                time.sleep(0.3)
        finally:
            try:
                save_excel(self.df, EXCEL_FILE)
                self._write_log(f"Hasil ditulis ke Excel: {EXCEL_FILE}")
            except Exception as e:
                self._write_log(f"Gagal menyimpan Excel: {e}")
            self.btn_start.configure(state="normal")
            self.btn_stop.configure(state="disabled")
            self._write_log("== Selesai ==")

    # ---- save log
    def save_log(self):
        path = filedialog.asksaveasfilename(
            title="Simpan LOG sebagai", defaultextension=".txt",
            filetypes=[("Text Files","*.txt")]
        )
        if not path: return
        content = self.log_txt.get("1.0","end").strip()
        with open(path,"w",encoding="utf-8") as f:
            f.write(content)
        messagebox.showinfo("Download Log", f"Log disimpan ke:\n{path}")

# ---------- run ----------
if __name__ == "__main__":
    app = App()
    app.mainloop()