import requests, tkinter as tk, customtkinter as ctk
import datetime, json, os
from tkinter import messagebox
import google.generativeai as genai
from openai import OpenAI
from dateutil import parser

# =====================
# API KEYS
# =====================
FOOTBALL_API_KEY = "cb27b6c89dd5ef422d529a3c23e6a208"
GEMINI_API_KEY = "AIzaSyCIpHtAUohjYf5fcpHndnSgF4SGtKEDReA"
genai.configure(api_key=GEMINI_API_KEY)
OPENROUTER_API_KEY = "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"
openrouter_client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)

HISTORY_FILE = "predictions_history.json"

# =====================
# Football API
# =====================
class FootballAPI:
    def __init__(self, api_key):
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {"x-apisports-key": api_key}

    def get_today_fixtures(self):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        r = requests.get(
            f"{self.base_url}/fixtures?date={today}&timezone=Europe/Istanbul",
            headers=self.headers
        ).json()
        return r.get("response", [])

    def get_live_fixtures(self):
        r = requests.get(
            f"{self.base_url}/fixtures?live=all&timezone=Europe/Istanbul",
            headers=self.headers
        ).json()
        return r.get("response", [])

# =====================
# AI Predictor
# =====================
class AIPredictor:
    def __init__(self, api, model="gemini-flash"):
        self.api, self.model = api, model

    def _call(self, prompt):
        if self.model.startswith("gemini"):
            mname = "gemini-2.5-flash" if self.model=="gemini-flash" else "gemini-2.5-pro"
            resp = genai.GenerativeModel(mname).generate_content(prompt)
            return resp.text
        response = openrouter_client.chat.completions.create(
            model="openai/gpt-4.1-mini",
            messages=[{"role":"system","content":"Profesyonel futbol bahis analisti."},
                      {"role":"user","content":prompt}],
            temperature=0.3, max_tokens=1200)
        return getattr(response.choices[0].message, "content", "⚠ Yanıt alınamadı.")

    def analyze(self, fixtures):
        results = []
        for f in fixtures:
            prompt = f"""
Maç: {f['teams']['home']['name']} vs {f['teams']['away']['name']}
Görev:
1. Son 5 maç formunu ✅ ❌ ⛔ ile tablo halinde yaz.
2. Head-to-Head geçmişini yaz.
3. Kısa uzman yorumu ekle.
4. Aşağıdaki tüm pazarlar için % olasılık ver ve renklendir (🟢 ≥70, 🟡 40-69, 🔴 <40).
MS1, MSX, MS2, 2.5 Alt, 2.5 Üst, KG VAR, KG YOK...
"""
            try:
                ai_text = self._call(prompt)
                results.append((f, ai_text))
                self.save_history(f, ai_text)
            except Exception as e:
                results.append((f, f"⚠ Hata: {e}"))
        return results

    def save_history(self, fixture, text):
        data = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "match": f"{fixture['teams']['home']['name']} vs {fixture['teams']['away']['name']}",
            "league": fixture["league"]["name"],
            "analysis": text
        }
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE,"r",encoding="utf-8") as f:
                history = json.load(f)
        else:
            history = []
        history.append(data)
        if len(history) > 500:  # max 500 kayıt
            history = history[-500:]
        with open(HISTORY_FILE,"w",encoding="utf-8") as f:
            json.dump(history,f,indent=2,ensure_ascii=False)

# =====================
# Uygulama
# =====================
class App:
    def __init__(self, root):
        self.api = FootballAPI(FOOTBALL_API_KEY)
        self.match_vars, self.last_scores = {}, {}
        self.live_visible = tk.BooleanVar(value=True)

        root.title("PredictAI HexPro - Günlük Maçlar")
        root.geometry("1700x950")

        # Sol panel
        p1 = ctk.CTkFrame(root, width=220)
        p1.pack(side="left", fill="y", padx=5, pady=5)
        ctk.CTkLabel(p1, text="⚙️ Ayarlar").pack(pady=10)
        self.model_var = tk.StringVar(value="gemini-flash")
        ctk.CTkOptionMenu(p1, values=["gemini-flash","gemini-pro","openrouter"], variable=self.model_var,
                          command=self.model_warning).pack(pady=10)
        ctk.CTkButton(p1, text="📅 Bugünkü Maçları Listele", command=self.list_fixtures).pack(pady=10)
        ctk.CTkButton(p1, text="⚽ Seçilenleri Analiz Et", command=self.load_selected).pack(pady=10)
        ctk.CTkButton(p1, text="👑 Kim Kazanır?", command=self.who_wins).pack(pady=10)
        ctk.CTkButton(p1, text="📂 Geçmiş Tahminleri Göster", command=self.show_history).pack(pady=10)
        ctk.CTkCheckBox(p1, text="⚡ Canlı Maçları Göster", variable=self.live_visible, command=self.list_fixtures).pack(pady=10)

        # Orta panel - maç listesi
        p2 = ctk.CTkFrame(root, width=500)
        p2.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        ctk.CTkLabel(p2, text="📌 Bugünkü Maçlar").pack(pady=5)

        self.can = tk.Canvas(p2, bg="#1e1e1e", highlightthickness=0)
        self.sb_y = tk.Scrollbar(p2, orient="vertical", command=self.can.yview)
        self.scroll_frame = ctk.CTkFrame(self.can, fg_color="transparent")
        self.scroll_frame.bind("<Configure>", lambda e: self.can.configure(scrollregion=self.can.bbox("all")))
        self.can.create_window((0,0), window=self.scroll_frame, anchor="nw")
        self.can.configure(yscrollcommand=self.sb_y.set)
        self.can.pack(side="left", fill="both", expand=True)
        self.sb_y.pack(side="right", fill="y")

        # Sağ panel - analizler
        p3 = ctk.CTkFrame(root, width=800)
        p3.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        ctk.CTkLabel(p3, text="🤖 Tahmin & Analizler").pack(pady=5)
        self.analysis_box = ctk.CTkTextbox(p3, wrap="word", font=("Segoe UI",13))
        self.analysis_box.pack(fill="both", expand=True, padx=10, pady=10)

        # Emoji renk tagları
        self.analysis_box.tag_config("green", foreground="lime")
        self.analysis_box.tag_config("yellow", foreground="gold")
        self.analysis_box.tag_config("red", foreground="tomato")

        # Canlı güncelleme başlat
        self.refresh_live()

    def model_warning(self, choice):
        if choice.startswith("gemini"):
            messagebox.showinfo("Uyarı", "Bu modelde sonuçlar 1–3 dk sürebilir.")
        elif choice == "openrouter":
            messagebox.showinfo("Uyarı", "Bu modelde sonuçlar 1–2 dk sürebilir.")

    def list_fixtures(self):
        for w in self.scroll_frame.winfo_children():
            w.destroy()
        self.match_vars = {}

        # Canlı maçlar
        if self.live_visible.get():
            live = self.api.get_live_fixtures()
            if live:
                header = ctk.CTkLabel(self.scroll_frame, text="⚡ CANLI MAÇLAR",
                                      font=("Segoe UI", 14, "bold"), text_color="orange")
                header.pack(anchor="w", pady=5)
                for f in live:
                    dt = parser.parse(f["fixture"]["date"])
                    date_str = dt.strftime("%d.%m.%Y %H:%M")
                    hs, as_ = f["goals"]["home"], f["goals"]["away"]
                    home, away = f["teams"]["home"]["name"], f["teams"]["away"]["name"]
                    minute = f["fixture"]["status"]["elapsed"]

                    var = tk.BooleanVar()
                    cb = ctk.CTkCheckBox(self.scroll_frame,
                        text=f"{date_str}  {home} {hs}-{as_} {away}  CANLI {minute}'",
                        font=("Segoe UI", 13), text_color="red", variable=var)
                    cb.pack(anchor="w", pady=2)
                    self.match_vars[f["fixture"]["id"]] = (var, f)

        # Günlük maçlar - filtre
        matches = self.api.get_today_fixtures()
        leagues_filter = ["UEFA Champions League", "UEFA Europa League", "World Cup", "Süper Lig", "1. Lig", "2. Lig", "3. Lig"]
        for f in matches:
            if not any(l in f["league"]["name"] for l in leagues_filter):
                continue
            dt = parser.parse(f["fixture"]["date"])
            date_str = dt.strftime("%d.%m.%Y %H:%M")
            home, away = f["teams"]["home"]["name"], f["teams"]["away"]["name"]

            var = tk.BooleanVar()
            cb = ctk.CTkCheckBox(self.scroll_frame,
                text=f"{date_str}  {home} - {away}",
                font=("Segoe UI", 13),
                text_color="white", variable=var)
            cb.pack(anchor="w", padx=20, pady=2)
            self.match_vars[f["fixture"]["id"]] = (var, f)

    def refresh_live(self):
        try:
            live = self.api.get_live_fixtures()
            for f in live:
                fid = f["fixture"]["id"]
                hs, as_ = f["goals"]["home"], f["goals"]["away"]
                score = f"{hs}-{as_}"
                if fid in self.last_scores and self.last_scores[fid] != score:
                    messagebox.showinfo("⚽ Gol!", f"{f['teams']['home']['name']} {hs}-{as_} {f['teams']['away']['name']}")
                self.last_scores[fid] = score
        except: pass
        self.list_fixtures()
        self.can.after(30000, self.refresh_live)

    def load_selected(self):
        selected = [f for fid,(var,f) in self.match_vars.items() if var.get()]
        if not selected:
            messagebox.showwarning("Uyarı", "Hiç maç seçmedin!")
            return

        preds = AIPredictor(self.api, model=self.model_var.get()).analyze(selected)
        self.analysis_box.delete("1.0","end")
        for f, text in preds:
            self.analysis_box.insert("end", f"\n📌 {f['teams']['home']['name']} vs {f['teams']['away']['name']} ({f['league']['name']})\n", "bold")
            # emoji renklendirme
            for line in text.splitlines():
                if "🟢" in line:
                    self.analysis_box.insert("end", line+"\n", "green")
                elif "🟡" in line:
                    self.analysis_box.insert("end", line+"\n", "yellow")
                elif "🔴" in line:
                    self.analysis_box.insert("end", line+"\n", "red")
                else:
                    self.analysis_box.insert("end", line+"\n")
            self.analysis_box.insert("end", "\n")

    def who_wins(self):
        selected = [f for fid,(var,f) in self.match_vars.items() if var.get()]
        if not selected:
            messagebox.showwarning("Uyarı", "Hiç maç seçmedin!")
            return

        predictor = AIPredictor(self.api, model=self.model_var.get())
        self.analysis_box.delete("1.0","end")
        for f in selected:
            prompt = f"""
Maç: {f['teams']['home']['name']} vs {f['teams']['away']['name']}
Tahmin: MS1, MSX, MS2 yüzdelik dağılımı ver.
"""
            result = predictor._call(prompt)
            self.analysis_box.insert("end", f"\n👑 {f['teams']['home']['name']} vs {f['teams']['away']['name']}\n")
            self.analysis_box.insert("end", result + "\n\n")

    def show_history(self):
        if not os.path.exists(HISTORY_FILE):
            messagebox.showinfo("Geçmiş", "Henüz tahmin kaydedilmedi.")
            return
        with open(HISTORY_FILE,"r",encoding="utf-8") as f:
            history = json.load(f)
        self.analysis_box.delete("1.0","end")
        self.analysis_box.insert("end", "📂 GEÇMİŞ TAHMİNLER\n\n")
        for h in history[-10:]:
            self.analysis_box.insert("end", f"{h['date']} | {h['match']} ({h['league']})\n")
            self.analysis_box.insert("end", h['analysis'] + "\n\n")

# =====================
# Çalıştır
# =====================
if __name__ == "__main__":
    ctk.set_appearance_mode("dark"); ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    App(root)
    root.mainloop()
