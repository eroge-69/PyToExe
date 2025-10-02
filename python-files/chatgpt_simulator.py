"""
ChatGPT Simulator (V2) — Python app với giao diện đẹp & animation chill
--------------------------------------------------
- tkinter + ttkbootstrap (theme đẹp, hiện đại)
- Animation typing mượt
- Random bot replies (template, Markov, biến đổi ngẫu nhiên)
- Có lọc text chống ký tự rác
- Tùy chỉnh theme (Dark/Light/Flatly/Cosmo…)
- Persona chọn được (Friendly, Sassy, Philosopher, Coder, Poet)

Chạy: pip install ttkbootstrap
       python chatgpt_simulator.py
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as tb
import threading, random, time, json, re

# -----------------------------
# Data corpus
# -----------------------------
SAMPLE_CORPUS = [
    "Xin chào! Mình là trợ lý ảo — bạn cần gì nào?",
    "Bạn đang làm gì hôm nay? Mình thích học ngôn ngữ mới.",
    "Nếu bạn cần ý tưởng, mình có thể gợi ý trò chơi hoặc công thức nấu ăn.",
    "Có một chú mèo bay trên đám mây tìm thấy chiếc bánh pizza.",
    "Hãy chia việc khó thành nhiều bước nhỏ, sẽ dễ dàng hơn.",
    "Bạn muốn nghe một gợi ý sáng tạo? Kết hợp hai ý tưởng trái ngược.",
    "Thời tiết trong trí tưởng tượng: trời nắng, mây nhảy múa.",
    "Luôn giữ tinh thần tò mò và nhẹ nhàng nhé!"
]

# -----------------------------
# Clean text
# -----------------------------
def clean_text(txt):
    return re.sub(r"[^0-9a-zA-ZÀ-ỹ .,!?-]", "", txt)

# -----------------------------
# Markov Generator
# -----------------------------
class MarkovGenerator:
    def __init__(self, corpus=None, k=1):
        self.k = k
        self.corpus = corpus or SAMPLE_CORPUS
        self.model = {}
        self._build()

    def _build(self):
        self.model.clear()
        for line in self.corpus:
            tokens = line.split()
            if len(tokens) <= self.k:
                continue
            for i in range(len(tokens) - self.k):
                key = tuple(tokens[i:i+self.k])
                nxt = tokens[i+self.k]
                self.model.setdefault(key, []).append(nxt)
        starts = []
        for line in self.corpus:
            t = line.split()
            if len(t) >= self.k:
                starts.append(tuple(t[:self.k]))
        if starts:
            self.model['_starts'] = starts

    def generate(self, max_words=25):
        if not self.model:
            return random.choice(self.corpus)
        starts = self.model.get('_starts') or list(self.model.keys())
        key = random.choice(starts)
        out = list(key)
        for _ in range(max_words - self.k):
            choices = self.model.get(tuple(out[-self.k:]))
            if not choices:
                break
            out.append(random.choice(choices))
        return clean_text(' '.join(out))

# -----------------------------
# Random response
# -----------------------------
PERSONAS = {
    'Friendly': '🙂',
    'Sassy': '😏',
    'Philosopher': '💭',
    'Coder': '👨‍💻',
    'Poet': '🎵'
}

GREETINGS = ["Chào", "Xin chào", "Hey", "Hiya"]
FOLLOWUPS = ["mình có vài gợi ý.", "cứ tiếp tục — mình lắng nghe.", "bạn muốn mình dí dỏm hay nghiêm túc?"]
OPINIONS = ["đi bộ buổi sáng tốt cho não", "cà phê ngon hơn khi ấm", "AI giúp sáng tạo nếu dùng đúng"]
IDEAS = ["app nhắc tưới cây", "trò chơi puzzle âm nhạc", "blog ảnh mỗi ngày"]
SUGGESTIONS = ["Pomodoro 25 phút", "viết 3 ý tưởng trong 10 phút", "dọn hộp mail bằng zero-inbox"]
ANSWERS = ["Có lẽ", "Không chắc", "Rất có thể", "Còn tuỳ"]

TEMPLATES = [
    "{greeting}! {followup}",
    "Mình nghĩ rằng {opinion}.",
    "Bạn hỏi: '{question}' — có thể là {answer}.",
    "Ý tưởng ngẫu nhiên: {idea}.",
    "Thử nhé: {suggestion}."
]

def gen_from_template(user_msg):
    tpl = random.choice(TEMPLATES)
    subs = {
        'greeting': random.choice(GREETINGS),
        'followup': random.choice(FOLLOWUPS),
        'opinion': random.choice(OPINIONS),
        'question': user_msg,
        'answer': random.choice(ANSWERS) + ', ' + random.choice(OPINIONS),
        'idea': random.choice(IDEAS),
        'suggestion': random.choice(SUGGESTIONS)
    }
    return clean_text(tpl.format(**subs))

# -----------------------------
# App
# -----------------------------
class ChatSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.style = tb.Style("flatly")  # default đẹp
        root.title("ChatGPT Simulator — Local")
        root.geometry("850x600")

        self.markov = MarkovGenerator()
        self.chat_history = []
        self.persona = tk.StringVar(value='Friendly')

        self._build_ui()
        self._append_bot(self._greet())

    def _build_ui(self):
        top = tb.Frame(self.root)
        top.pack(side='top', fill='x', pady=6)
        tb.Button(top, text="Ván mới", command=self.new_chat).pack(side='left', padx=4)
        tb.Button(top, text="Lưu", command=self.save_chat).pack(side='left', padx=4)
        tb.OptionMenu(top, self.persona, *PERSONAS.keys()).pack(side='left', padx=10)

        self.chat_text = tk.Text(self.root, wrap='word', font=("Segoe UI", 11), bg="white", fg="black")
        self.chat_text.pack(expand=True, fill='both', padx=10, pady=6)
        self.chat_text.config(state='disabled')

        bottom = tb.Frame(self.root)
        bottom.pack(side='bottom', fill='x', pady=8)
        self.entry = tb.Entry(bottom)
        self.entry.pack(side='left', fill='x', expand=True, padx=6)
        self.entry.bind('<Return>', lambda e: self.on_send())
        tb.Button(bottom, text="Gửi", bootstyle="success", command=self.on_send).pack(side='right', padx=6)

    # ----------------
    def _append_text(self, txt, tag=None, delay=0):
        self.chat_text.config(state='normal')
        for ch in txt:
            self.chat_text.insert('end', ch, tag)
            self.chat_text.see('end')
            self.chat_text.update_idletasks()
            time.sleep(delay)
        self.chat_text.insert('end', "\n")
        self.chat_text.config(state='disabled')

    def _append_user(self, text):
        self.chat_history.append({'role': 'user', 'text': text})
        self._append_text("Bạn: " + text, delay=0)

    def _append_bot(self, text):
        self.chat_history.append({'role': 'bot', 'text': text})
        self._append_text("Bot: " + text, delay=0.01)

    def _greet(self):
        return random.choice(GREETINGS) + "! " + random.choice(FOLLOWUPS)

    def on_send(self):
        msg = self.entry.get().strip()
        if not msg:
            return
        self.entry.delete(0, 'end')
        self._append_user(msg)
        threading.Thread(target=self._reply, args=(msg,), daemon=True).start()

    def _reply(self, user_msg):
        time.sleep(0.3)
        persona = self.persona.get()
        reply = random.choice([
            gen_from_template(user_msg),
            self.markov.generate(),
            f"Mình nghe bạn nói: '{user_msg}', thú vị đấy!"
        ])
        reply = PERSONAS.get(persona, '') + " " + reply
        self._append_bot(reply)

    def new_chat(self):
        self.chat_text.config(state='normal')
        self.chat_text.delete('1.0', 'end')
        self.chat_text.config(state='disabled')
        self.chat_history.clear()
        self._append_bot(self._greet())

    def save_chat(self):
        if not self.chat_history:
            messagebox.showinfo("Lưu", "Không có gì để lưu.")
            return
        f = filedialog.asksaveasfilename(defaultextension='.json')
        if f:
            with open(f, 'w', encoding='utf-8') as fh:
                json.dump(self.chat_history, fh, ensure_ascii=False, indent=2)
            messagebox.showinfo("Lưu", f"Đã lưu vào: {f}")

# -----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatSimulatorApp(root)
    root.mainloop()
