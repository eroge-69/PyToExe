import os
import time
import json
import threading
from docx import Document
from PIL import Image, ImageTk

import tkinter.filedialog
import ttkbootstrap as ttkb
from tkinter import messagebox
from ttkbootstrap.constants import *

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Global
klasor_adi = metin = klasor_yolu = None
driver = None
second_window = None
folder_label = None
folder_photo = None
sfolder_photo = None
baslik_var = None
icerik_var = None


def klasor_sec():
    global klasor_adi, metin, klasor_yolu
    global folder_label, baslik_var, icerik_var, sfolder_photo

    klasor_yolu = tkinter.filedialog.askdirectory(title="Bir klasör seçin")
    if not klasor_yolu:
        return

    try:
        klasor_adi = os.path.basename(klasor_yolu.rstrip(os.sep))
        docx_dosyasi = next((os.path.join(klasor_yolu, f) for f in os.listdir(klasor_yolu) if f.endswith(".docx")), None)
        if not docx_dosyasi:
            raise FileNotFoundError("Açıklama dosyası bulunamadı. Klasöre bir açıklama dosyası ekleyin.")

        doc = Document(docx_dosyasi)
        paragraflar = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        baslik = klasor_adi
        icerik = "\n\n".join(paragraflar)

        if folder_label and sfolder_photo:
            folder_label.configure(image=sfolder_photo)
            folder_label.image = sfolder_photo

        if baslik_var is not None:
            baslik_var.set(baslik)

        if icerik_var is not None:
            icerik_var.delete("1.0", "end")
            icerik_var.insert("1.0", icerik)

    except Exception as e:
        messagebox.showerror("Hata", str(e))


def login_panel(url, username, password):
    global driver
    try:
        driver = webdriver.Chrome()
        driver.set_window_size(960, 1080)
        driver.set_window_position(960, 0)
        driver.get(url)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "k_user_name"))).send_keys(username)
        driver.find_element(By.NAME, "k_user_pwd").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "button.btn.btn-primary").click()
    except Exception as e:
        messagebox.showerror("Giriş Hatası", f"Panel giriş başarısız: {e}")


def addnews():
    global klasor_adi, klasor_yolu, driver, baslik_var, icerik_var

    if driver is None:
        messagebox.showerror("Hata", "Web tarayıcı başlatılmamış.")
        return

    baslik = baslik_var.get().strip() if baslik_var else ""
    icerik = icerik_var.get("1.0", "end").strip() if icerik_var else ""

    if not klasor_adi or not baslik or not icerik:
        messagebox.showwarning("Uyarı", "Lütfen klasör seçin ve başlık ile içerik alanlarını doldurun.")
        return

    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[@title='haberler.php']"))).click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[@data-title='Yeni Sayfa']"))).click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "f_k_page_title"))).send_keys(baslik)

        iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//iframe[contains(@title, 'f_content')]")))
        driver.switch_to.frame(iframe)
        body = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//body")))
        body.send_keys(icerik)
        driver.switch_to.default_content()

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "f_image_button"))).click()       

    except Exception as e:
        messagebox.showerror("Haber Ekleme Hatası", f"Haber eklenirken bir hata oluştu: {e}")


def addproject():
    global klasor_adi, klasor_yolu, driver, baslik_var, icerik_var

    if driver is None:
        messagebox.showerror("Hata", "Web tarayıcı başlatılmamış.")
        return

    baslik = baslik_var.get().strip() if baslik_var else ""
    icerik = icerik_var.get("1.0", "end").strip() if icerik_var else ""

    if not klasor_adi or not baslik or not icerik:
        messagebox.showwarning("Uyarı", "Lütfen klasör seçin ve başlık ile içerik alanlarını doldurun.")
        return

    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[@title='projeler.php']"))).click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[@data-title='Yeni Sayfa']"))).click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "f_k_page_title"))).send_keys(baslik)

        iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//iframe[contains(@title, 'f_content')]")))
        driver.switch_to.frame(iframe)
        body = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//body")))
        body.send_keys(icerik)
        driver.switch_to.default_content()

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "f_image_button"))).click()       

    except Exception as e:
        messagebox.showerror("Haber Ekleme Hatası", f"Haber eklenirken bir hata oluştu: {e}")


def upload_images():
    threading.Thread(target=foto_ekle_kcfinder, daemon=True).start()


def foto_ekle_kcfinder():
    try:
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe"))
        )
        driver.switch_to.frame(iframe)

        for resim in os.listdir(klasor_yolu):
            if resim.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                tam_yol = os.path.join(klasor_yolu, resim)
                try:
                    file_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//input[@type="file" and @name="upload[]"]'))
                    )
                    file_input.send_keys(tam_yol)
                    time.sleep(1)
                except Exception as dosya_hatasi:
                    print(f"[Uyarı] {resim} yüklenirken hata oluştu: {dosya_hatasi}")

        try:
            driver.switch_to.default_content()
        except Exception:
            print("iframe zaten kapanmış olabilir.")

        print("✅ Fotoğraflar başarıyla yüklendi.")

    except Exception as genel_hata:
        print(f"[Uyarı] Yükleme sırasında genel bir hata oluştu: {genel_hata}")


def clear():
    global baslik_var, icerik_var, driver

    # Tkinter arayüzünü temizle
    if baslik_var:
        baslik_var.set("")
    if icerik_var:
        icerik_var.delete("1.0", "end")

    # Web tarayıcıda açık sayfada başlığı ve içeriği temizle
    try:
        if driver:
            # Başlık input'unu temizle
            baslik_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.NAME, "f_k_page_title"))
            )
            baslik_input.clear()

            # İçerik iframe'ine geç
            iframe = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//iframe[contains(@title, 'f_content')]"))
            )
            driver.switch_to.frame(iframe)

            # <body> içeriğini temizle
            body = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//body"))
            )
            body.send_keys(Keys.CONTROL + "a")
            body.send_keys(Keys.BACKSPACE)

            driver.switch_to.default_content()

    except Exception as e:
        print(f"[Uyarı] Web içeriği temizlenemedi: {e}")


def goback():
    global second_window, driver
    if second_window:
        second_window.destroy()
        second_window = None
        app.after(100, app.deiconify)
        try:
            if driver:
                threading.Thread(target=driver.quit, daemon=True).start()
        except Exception as e:
            print("Tarayıcı kapatma hatası:", e)


def save():
    global driver
    try:
        if driver:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "btn_submit"))).click()
            messagebox.showinfo("", "Kaydedildi!")
        else:
            messagebox.showwarning("Uyarı", "Kaydetme işlemi için web tarayıcı aktif değil.")
    except Exception as e:
        messagebox.showerror("Kaydetme Hatası", f"Kaydetme işlemi sırasında hata: {e}")


def open_panel(ad, url, username, password, icon):
    global second_window, folder_photo, sfolder_photo, folder_label
    global baslik_var, icerik_var

    app.withdraw()
    second_window = ttkb.Toplevel(app)
    second_window.geometry("600x700")
    second_window.title(f"{ad} Panel")

    try:
        second_window.iconbitmap(icon)
    except:
        pass

    baslik_var = ttkb.StringVar()

    notebook = ttkb.Notebook(second_window)
    notebook.pack(fill=BOTH, expand=True, padx=10, pady=50)

    frame_haber = ttkb.Frame(notebook)
    notebook.add(frame_haber, text="Haber Ekle")

    frame_proje = ttkb.Frame(notebook)
    notebook.add(frame_proje, text="Proje Ekle")

    folder_img = Image.open("App data/Icons/folder.png").resize((24, 24), Image.LANCZOS)
    folder_photo = ImageTk.PhotoImage(folder_img)

    sfolder_img = Image.open("App data/Icons/sfolder.png").resize((24, 24), Image.LANCZOS)
    sfolder_photo = ImageTk.PhotoImage(sfolder_img)

    folder_label = ttkb.Label(second_window, image=folder_photo, cursor="hand2")
    folder_label.image = folder_photo
    folder_label.place(x=560, y=10)
    folder_label.bind("<Button-1>", lambda e: klasor_sec())

    # Geri Butonu

    back_img = Image.open("App data/Icons/back.png").resize((24, 24), Image.LANCZOS)
    back_photo = ImageTk.PhotoImage(back_img)
    back_label = ttkb.Label(second_window, image=back_photo, cursor="hand2")
    back_label.image = back_photo
    back_label.place(x=10, y=10)
    back_label.bind("<Button-1>", lambda e: goback())

    # Haber Frame

    ttkb.Label(frame_haber, text="Başlık:", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
    baslik_entry = ttkb.Entry(frame_haber, textvariable=baslik_var, font=("Segoe UI", 11))
    baslik_entry.pack(fill=X, padx=10, pady=(0, 10))

    ttkb.Label(frame_haber, text="İçerik:", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10)
    icerik_var = ttkb.Text(frame_haber, height=15, font=("Segoe UI", 10))
    icerik_var.pack(fill=BOTH, padx=10, pady=(0, 10), expand=True)

    ttkb.Button(frame_haber, text="Yeni Haber Ekle", command=addnews, bootstyle=PRIMARY).pack(pady=5)
    ttkb.Button(frame_haber, text="Fotoğraf Ekle", command=upload_images, bootstyle=INFO).pack(pady=5)
    ttkb.Button(frame_haber, text="Temizle", command=clear, bootstyle=WARNING).pack(pady=5)

    # Proje frame

    ttkb.Label(frame_proje, text="Başlık:", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
    baslik_entry = ttkb.Entry(frame_proje, textvariable=baslik_var, font=("Segoe UI", 11))
    baslik_entry.pack(fill=X, padx=10, pady=(0, 10))

    ttkb.Label(frame_proje, text="İçerik:", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10)
    icerik_var = ttkb.Text(frame_proje, height=15, font=("Segoe UI", 10))
    icerik_var.pack(fill=BOTH, padx=10, pady=(0, 10), expand=True)

    ttkb.Button(frame_proje, text="Yeni Proje Ekle", command=addnews, bootstyle=PRIMARY).pack(pady=5)
    ttkb.Button(frame_proje, text="Fotoğraf Ekle", command=upload_images, bootstyle=INFO).pack(pady=5)
    ttkb.Button(frame_proje, text="Temizle", command=clear, bootstyle=WARNING).pack(pady=5)

    # Kaydet Butonu

    save_img = Image.open("App data/Icons/save.png").resize((50, 50), Image.LANCZOS)
    save_photo = ImageTk.PhotoImage(save_img)
    save_label = ttkb.Label(second_window, image=save_photo, cursor="hand2")
    save_label.image = save_photo
    save_label.pack(anchor="n")
    save_label.bind("<Button-1>", lambda e: save())

    threading.Thread(target=login_panel, args=(url, username, password), daemon=True).start()


def on_closing():
    global driver
    if messagebox.askokcancel("Çıkış", "Uygulamadan çıkmak istiyor musunuz?"):
        try:
            if driver:
                threading.Thread(target=driver.quit, daemon=True).start()
        except:
            pass
        app.after(100, app.destroy)

# Ana uygulama

app = ttkb.Window(title="Web Panel Yöneticisi", themename="flatly")
app.geometry("600x500")

mainframe = ttkb.Frame(app, padding=20)
mainframe.pack(fill=BOTH, expand=True)

ttkb.Label(mainframe, text="Web Panel Yöneticisi", font=("Segoe UI", 18, "bold")).pack(pady=20)

try:
    with open("App data/Json files/Panels.json", "r", encoding="utf-8") as f:
        panel_bilgileri = json.load(f)
except Exception as e:
    messagebox.showerror("Hata", f"Panel dosyası okunamadı: {e}")
    panel_bilgileri = []

for panel in panel_bilgileri:
    ad = panel.get("ad")
    url = panel.get("url")
    username = panel.get("username")
    password = panel.get("password")
    icon = panel.get("icon")

    ttkb.Button(
        mainframe,
        text=ad,
        width=30,
        command=lambda a=ad, u=url, un=username, p=password, i=icon: open_panel(a, u, un, p, i),
        bootstyle=PRIMARY
    ).pack(pady=5)

app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()