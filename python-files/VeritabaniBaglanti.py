import os
import tkinter as tk
from tkinter import (
    Label, Entry, Button, Frame, messagebox, Text, Toplevel,
    Scrollbar, RIGHT, Y, Canvas, END, filedialog, BooleanVar, ttk
)
import mysql.connector

import cv2
from PIL import Image, ImageTk
from deepface import DeepFace
import threading
import time
import speech_recognition as sr
import sounddevice as sd
import soundfile as sf

from collections import Counter
import google.genai as genai
from google.genai.types import HttpOptions
import json
from PyPDF2 import PdfReader

# --- MySQL ve Gemini API Konfigürasyonu ---
DB_CONFIG = {
    'host': 'bigital.net',
    'user': 'bigital_biveyos',
    'password': 'biveyos',
    'database': 'bigital_crm',
    'raise_on_warnings': True
}
client = genai.Client(
    api_key="AIzaSyBMQi7huSbyf8WcNESZdlYfwDBx5Y91Kyw",
    http_options=HttpOptions(api_version="v1")
)

def extract_text_from_pdf(path):
    try:
        reader = PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        print(f"PDF okunurken hata: {e}")
        return ""

def start_login():
    root = tk.Tk()
    root.title("Biveyos CRM Giriş")
    root.geometry("300x210")
    root.resizable(False, False)
    Label(root, text="Kullanıcı Adı:").pack(pady=(20,5))
    username = Entry(root); username.pack()
    Label(root, text="Şifre:").pack(pady=5)
    password = Entry(root, show='*'); password.pack()
    def login():
        user = username.get().strip()
        pwd = password.get().strip()
        if not user or not pwd:
            messagebox.showwarning("Hata", "Lütfen kullanıcı adı ve şifre girin.")
            return
        try:
            cnx = mysql.connector.connect(**DB_CONFIG)
            cursor = cnx.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM kullanicilar WHERE isim=%s AND sifre=%s", (user, pwd)
            )
            if cursor.fetchone():
                cursor.close(); cnx.close()
                root.destroy(); start_interview_info()
            else:
                messagebox.showerror("Hata", "Kullanıcı adı veya şifre hatalı.")
        except Exception as e:
            messagebox.showerror("DB Hatası", str(e))
    Button(root, text="Giriş Yap", width=15, command=login).pack(pady=20)
    root.mainloop()

def start_interview_info():
    root = tk.Tk()
    root.title("Mülakat Bilgileri")
    root.geometry("400x250")
    root.resizable(False, False)

    Label(root, text="Ad:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
    first_name = Entry(root); first_name.grid(row=0, column=1)
    Label(root, text="Soyad:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
    last_name = Entry(root); last_name.grid(row=1, column=1)
    Label(root, text="İş Ünvanı:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
    job_title = Entry(root); job_title.grid(row=2, column=1)
    Label(root, text="Eğitim Seviyesi:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
    edu_combo = ttk.Combobox(
        root, values=["İlkokul","Ortaokul","Lise","Üniversite","Yüksek Lisans","Master"],
        state='readonly'
    )
    edu_combo.grid(row=3, column=1)
    Label(root, text="Deneyim (Yıl):").grid(row=4, column=0, padx=10, pady=5, sticky='e')
    exp_years = Entry(root); exp_years.grid(row=4, column=1)

    cv_text = ""
    cv_label = Label(root, text="CV Yüklenmedi"); cv_label.grid(row=5, column=1, pady=5)
    def load_cv():
        nonlocal cv_text
        path = filedialog.askopenfilename(filetypes=[("PDF Dosyaları","*.pdf")])
        if path:
            cv_text = extract_text_from_pdf(path); cv_label.config(text="CV Yüklendi")
    Button(root, text="CV Yükle", command=load_cv).grid(row=5, column=0)

    def proceed():
        fn = first_name.get().strip()
        ln = last_name.get().strip()
        jt = job_title.get().strip()
        ed = edu_combo.get()
        exp = exp_years.get().strip()
        if not fn or not ln:
            messagebox.showwarning("Hata", "Lütfen ad ve soyad girin."); return
        root.destroy()
        InterviewApp(
            applicant_name=f"{fn} {ln}",
            job_title=jt, education=ed,
            experience_years=exp, cv_text=cv_text
        )
    Button(root, text="Devam Et", width=15, command=proceed).grid(row=6, column=1, pady=20)
    root.mainloop()

class InterviewApp:
    def __init__(self, applicant_name, job_title, education, experience_years, cv_text):
        self.applicant = applicant_name
        self.job_title = job_title
        self.education = education
        self.experience_years = experience_years
        self.cv_text = cv_text
        self.extra_data = []
        self.emotion_log = []
        self.speech_log = []  # store speech segments
        self.running = False
        self.paused = False
        self.pre_eval = ""
        self.suggested_questions = ""
        self.root = tk.Tk()
        self.root.title("Mülakat Modülü")
        self.root.geometry("1200x900")
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        self._build_ui()
        self._update_frame()
        self.root.mainloop()

    def _build_ui(self):
        hdr = Frame(self.root); hdr.pack(pady=5)
        for txt in [
            f"Aday: {self.applicant}", f"Pozisyon: {self.job_title}",
            f"Eğitim: {self.education}", f"Deneyim: {self.experience_years} yıl"
        ]:
            Label(hdr, text=txt, font=(None,12)).pack(side='left', padx=10)

        self.frame1 = Frame(self.root); self.frame1.pack(fill='both', expand=True)
        Button(self.frame1, text="Kriter Ekle", command=self.add_data).pack(pady=5)
        self.criteria_list = Frame(self.frame1); self.criteria_list.pack(fill='both', expand=True)
        Button(self.frame1, text="Ön Değerlendirmeyi Yap", command=self.perform_pre_eval).pack(pady=5)

        self.frame2 = Frame(self.root)
        ctrl = Frame(self.frame2); ctrl.pack(pady=10)
        self.start_btn = Button(ctrl, text="Başlat", command=self.start, state='disabled')
        self.start_btn.grid(row=0, column=0, padx=5)
        self.pause_btn = Button(ctrl, text="Duraklat", command=self.pause, state='disabled')
        self.pause_btn.grid(row=0, column=1, padx=5)
        self.end_btn = Button(ctrl, text="Sonlandır", command=self.end_interview, state='disabled')
        self.end_btn.grid(row=0, column=2, padx=5)
        self.status_label = Label(self.frame2, text="Duygu: ---", font=(None,14))
        self.status_label.pack(pady=5)
        self.panel = Label(self.frame2); self.panel.pack()

        tabs_ctrl = Frame(self.frame2); tabs_ctrl.pack(pady=5)
        self.speech_text = Text(self.frame2, wrap='word', height=8)
        self.ai_text = Text(self.frame2, wrap='word', height=8)
        self.questions_text = Text(self.frame2, wrap='word', height=8)
        self.scroll_speech = Scrollbar(self.frame2, command=self.speech_text.yview)
        self.scroll_ai = Scrollbar(self.frame2, command=self.ai_text.yview)
        self.scroll_q = Scrollbar(self.frame2, command=self.questions_text.yview)
        self.speech_text.configure(yscrollcommand=self.scroll_speech.set)
        self.ai_text.configure(yscrollcommand=self.scroll_ai.set)
        self.questions_text.configure(yscrollcommand=self.scroll_q.set)

        self.tabs = {
            "Konuşma & Duygu": (self.speech_text, self.scroll_speech),
            "Analiz & Rapor": (self.ai_text, self.scroll_ai),
            "Önerilen Sorular": (self.questions_text, self.scroll_q)
        }
        for name in self.tabs:
            Button(tabs_ctrl, text=name, command=lambda n=name: self.switch_tab(n)).pack(side='left', padx=5)
        self.switch_tab("Konuşma & Duygu")

    def refresh_criteria_list(self):
        for w in self.criteria_list.winfo_children(): w.destroy()
        for i, d in enumerate(self.extra_data):
            f = Frame(self.criteria_list); f.pack(fill='x', pady=2)
            Label(f, text=f"{d['title']}: {d['value']}").pack(side='left')
            Button(f, text="Düzenle", command=lambda i=i: self.add_data(i)).pack(side='left')
            Button(f, text="Sil", command=lambda i=i: self.delete_data(i)).pack(side='left')

    def add_data(self, edit_index=None):
        win = Toplevel(self.root); win.title("Kriter Ekle")
        Label(win, text="Başlık:").grid(row=0, column=0, padx=5, pady=5)
        title_e = Entry(win); title_e.grid(row=0, column=1)
        no_val = BooleanVar()
        chk = tk.Checkbutton(win, text="Değer yok", variable=no_val,
            command=lambda: val_e.config(state='disabled' if no_val.get() else 'normal')
        )
        chk.grid(row=1, column=0, pady=5)
        Label(win, text="Değer:").grid(row=2, column=0, padx=5, pady=5)
        val_e = Entry(win); val_e.grid(row=2, column=1)
        if edit_index is not None:
            title_e.insert(0, self.extra_data[edit_index]['title'])
            if self.extra_data[edit_index]['value']:
                val_e.insert(0, self.extra_data[edit_index]['value'])
        def save():
            t = title_e.get().strip()
            v = None if no_val.get() else val_e.get().strip()
            if not t: return
            if edit_index is None:
                self.extra_data.append({'title': t, 'value': v})
            else:
                self.extra_data[edit_index] = {'title': t, 'value': v}
            win.destroy(); self.refresh_criteria_list()
        Button(win, text="Kaydet", command=save).grid(row=3, column=1, pady=10)

    def delete_data(self, i):
        self.extra_data.pop(i); self.refresh_criteria_list()

    def perform_pre_eval(self):
        payload = {
            'cv': self.cv_text,
            'job_title': self.job_title,
            'education': self.education,
            'experience_years': self.experience_years,
            'custom_criteria': {d['title']: d['value'] for d in self.extra_data}
        }
        prompt = ("Aşağıda bir adayın verileri var. Gerçekçi ve objektif ön değerlendirme yap (hiç bir şekilde markup kullanmadan düz yazıyla cevap ver)\n" +
                  json.dumps(payload, ensure_ascii=False))
        try:
            resp = client.models.generate_content(model="gemini-2.0-flash-001", contents=[prompt])
            self.pre_eval = resp.text.strip()
        except Exception as e:
            self.pre_eval = f"Ön değerlendirme hatası: {e}"

        try:
            q_prompt = ("Aşağıdaki aday bilgilerine ve iş tanımına göre, mülakat için önerilen 10 ar tane soruları madde madde listele:(hiç bir şekilde markup kullanma düz yazıyla cevap ver lütfen)\n" +
                        json.dumps(payload, ensure_ascii=False))
            q_resp = client.models.generate_content(model="gemini-2.0-flash-001", contents=[q_prompt])
            self.suggested_questions = q_resp.text.strip()
        except Exception as e:
            self.suggested_questions = f"Önerilen sorular oluşturulurken hata: {e}"

        prewin = Toplevel(self.root)
        prewin.title("Ön Değerlendirme Sonucu"); prewin.geometry("600x400")
        txt = Text(prewin, wrap='word'); sb = Scrollbar(prewin, command=txt.yview)
        txt.configure(yscrollcommand=sb.set); sb.pack(side=RIGHT, fill=Y); txt.pack(fill='both', expand=True)
        txt.insert(END, self.pre_eval); txt.config(state='disabled')
        Button(prewin, text="Tamam", command=prewin.destroy).pack(pady=5)

        self.questions_text.delete('1.0', END)
        self.questions_text.insert(END, self.suggested_questions)

        self.frame1.pack_forget(); self.frame2.pack(fill='both', expand=True)
        self.start_btn.config(state='normal')

    def switch_tab(self, name):
        for w, s in self.tabs.values():
            w.pack_forget(); s.pack_forget()
        txt, sc = self.tabs[name]; sc.pack(side=RIGHT, fill=Y); txt.pack(fill='both', expand=True)

    def start(self):
        self.running = True
        self.start_btn.config(state='disabled')
        self.pause_btn.config(state='normal', text='Duraklat')
        self.end_btn.config(state='normal')
        threading.Thread(target=self._analyze_loop, daemon=True).start()
        threading.Thread(target=self._speech_loop, daemon=True).start()

    def pause(self):
        self.paused = not self.paused
        self.pause_btn.config(text='Devam' if self.paused else 'Duraklat')

    def end_interview(self):
        self.running = False
        self.start_btn.config(state='disabled')
        self.pause_btn.config(state='disabled')
        self.end_btn.config(state='disabled')

        modal = Toplevel(self.root); modal.title("Rapor Başlığı Gir")
        Label(modal, text="Rapor Başlığı:").pack(pady=5)
        title_e = Entry(modal, width=50); title_e.pack(pady=5)
        def save_report():
            t = title_e.get().strip()
            if not t:
                messagebox.showwarning("Hata", "Başlık gerekli."); return
            # AI ile rapor oluşturma
            # Toplanan verileri derle
            speech_log = self.speech_text.get('1.0', END).strip()
            emotion_log = self.emotion_log  # liste
            custom_criteria = {d['title']: d['value'] for d in self.extra_data}
            payload = {
                'applicant': self.applicant,
                'job_title': self.job_title,
                'education': self.education,
                'experience_years': self.experience_years,
                'cv': self.cv_text,
                'custom_criteria': custom_criteria,
                'speech_log': speech_log,
                'emotion_log': emotion_log
            }
            prompt = ("Aşağıda adayın mülakat sırasında toplanan veriler var Onlarıda göz önünde bulundurarak düz yazı formatında kalın yazı kullanmadan mark-up sız cevaplar ver. "
                      "Bu verileri ve iş unvanını göz önünde bulundurarak, "
                      "adayın pozisyona uygunluğunu değerlendiren kapsamlı bir rapor oluştur. "
                      "Raporda güçlü ve zayıf yönler, eğitim ve deneyim uyumu, duygu analiz sonuçları, konuşma metinlerinden çıkarımlar yer almalı (hiç bir şekilde mark up kullanmadan düz yazıyla cevap ver).\n"
                      + json.dumps(payload, ensure_ascii=False))
            try:
                resp = client.models.generate_content(model="gemini-2.0-flash-001", contents=[prompt])
                report_content = resp.text.strip()
            except Exception as e:
                report_content = f"Rapor oluşturulurken hata: {e}"
            # Veritabanına kaydet
            try:
                cnx = mysql.connector.connect(**DB_CONFIG)
                cursor = cnx.cursor()
                cursor.execute(
                    "INSERT INTO interview_reports (applicant_name, report_title, full_report_content) VALUES (%s, %s, %s)",
                    (self.applicant, t, report_content)
                )
                cnx.commit()
                cursor.close(); cnx.close()
                messagebox.showinfo("Başarılı", "Rapor oluşturuldu ve veritabanına kaydedildi.")
                modal.destroy(); self.root.destroy()
            except Exception as e:
                messagebox.showerror("DB Hatası", str(e))
        Button(modal, text="Oluştur ve Kaydet", command=save_report).pack(pady=10)

    def _analyze_loop(self):
        while self.running:
            if self.paused:
                time.sleep(0.1); continue
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.1); continue
            try:
                res = DeepFace.analyze(img_path=frame, actions=['emotion'],
                                        detector_backend='opencv', enforce_detection=False)
                if isinstance(res, list):
                    res = res[0]
                dom = res['dominant_emotion']
                emos = res['emotion']
                total = sum(emos.values()) or 1
                score = emos.get(dom, 0) / total
                ts = time.time()
                self.emotion_log.append({'ts': ts, 'emotion': dom, 'score': score})
                self.root.after(0, lambda: self.status_label.config(
                    text=f"Duygu: {dom} ({score*100:.1f}%)"))
            except:
                pass
            time.sleep(1)

    def _speech_loop(self):
        recognizer = sr.Recognizer()
        fs, dur = 16000, 10
        while self.running:
            if self.paused:
                time.sleep(0.1); continue
            start = time.time()
            rec = sd.rec(int(dur * fs), samplerate=fs, channels=1); sd.wait()
            sf.write('speech.wav', rec, fs)
            try:
                with sr.AudioFile('speech.wav') as src:
                    audio = recognizer.record(src)
                text = recognizer.recognize_google(audio, language='tr-TR')
            except:
                text = "(anlaşılamadı)"
            end = time.time()
            seg = [e for e in self.emotion_log if start <= e['ts'] <= end]
            avg = sum(e['score'] for e in seg) / len(seg) if seg else 0
            mc = Counter(e['emotion'] for e in seg).most_common(1)[0][0] if seg else '---'
            distrib = {k: v/len(seg) for k, v in Counter(e['emotion'] for e in seg).items()} if seg else {}
            tstr = time.strftime('%H:%M:%S', time.localtime(start))
            entry = f"[{tstr}] {text}\n    Ortalama: {mc} ({avg*100:.1f}%)\n    Dağılım: {', '.join(f'{k}({v*100:.1f}%)' for k, v in distrib.items())}\n\n"
            self.speech_log.append(entry)
            self.root.after(0, lambda e=entry: self.speech_text.insert(END, e))
            if len(self.emotion_log) > 3:
                payload = {
                    'cv': self.cv_text,
                    'job_title': self.job_title,
                    'custom_criteria': {d['title']: d['value'] for d in self.extra_data},
                    'recent_segment': {'timestamp': start, 'text': text,
                                       'avg_emotion_score': avg, 'dominant_emotion': mc, 'distribution': distrib}
                }
                prompt = ("Aşağıda adayın en son konuşma ve duygu durumu var."
                          "İş tanımı ve veriler göz önünde bulundurularak sadece konuşma ve duygu durumuyla ilgili Kısa net rapor ver. (herhangi bir markup kullanmadan düz yazıyla cevap ver):\n"
                          + json.dumps(payload, ensure_ascii=False))
                try:
                    resp = client.models.generate_content(model="gemini-2.0-flash-001", contents=[prompt])
                    ai_out = resp.text.strip()
                except Exception as e:
                    ai_out = f"AI rapor hatası: {e}"
                self.root.after(0, lambda: self.ai_text.insert(END, ai_out + "\n\n"))
            time.sleep(0.1)

    def _update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            img = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            self.panel.config(image=img); self.panel.image = img
        self.root.after(50, self._update_frame)

if __name__ == '__main__':
    start_login()
