import tkinter as tk
from tkinter import ttk
from googletrans import Translator

# ===== 메롱어 사전 =====
CHAR_TO_MERONG = {
    'A': '메롱', 'B': '롱메', 'C': '메메', 'D': '롱롱',
    'E': '메에', 'F': '로옹', 'G': '메롱메', 'H': '롱메롱',
    'I': '메롱롱', 'J': '메에메', 'K': '로옹롱', 'L': '메롱메에',
    'M': '롱롱롱', 'N': '메에롱', 'O': '메메메', 'P': '로옹메',
    'Q': '메롱로옹', 'R': '롱메메', 'S': '메에로옹', 'T': '로옹메에',
    'U': '메메롱', 'V': '롱메에', 'W': '메에메에', 'X': '로옹로옹',
    'Y': '롱롱메', 'Z': '메롱메롱',
    '0': '메롱메롱메', '1': '롱롱메메', '2': '메에메롱', '3': '메메로옹',
    '4': '로옹메롱', '5': '롱메메에', '6': '메메메에', '7': '로옹로옹롱',
    '8': '메에메메', '9': '롱롱롱롱'
}
MERONG_TO_CHAR = {v: k for k, v in CHAR_TO_MERONG.items()}
translator = Translator()

# ===== 메롱어 인코딩 =====
def encode_to_merong(text):
    result = []
    for ch in text.upper():
        if ch == " ":
            result.append("/")
        elif ch in CHAR_TO_MERONG:
            result.append(CHAR_TO_MERONG[ch])
    return ' '.join(result)

# ===== 메롱어 디코딩 =====
def decode_from_merong(text):
    result = []
    for word in text.strip().split():
        if word == "/":
            result.append(" ")
        elif word in MERONG_TO_CHAR:
            result.append(MERONG_TO_CHAR[word])
    return ''.join(result)

# ===== 번역 실행 함수 =====
def translate(event=None):
    tab_index = notebook.index(notebook.select())
    if tab_index == 0:
        src = encoder_input.get("1.0", tk.END).strip()
        try:
            translated = translator.translate(src, src='ko', dest='en').text
        except Exception:
            translated = "[번역 실패]"
        result = encode_to_merong(translated)
        encoder_output.config(state="normal")
        encoder_output.delete("1.0", tk.END)
        encoder_output.insert(tk.END, result)
        encoder_output.config(state="disabled")
    else:
        # 디코더: 메롱어 → 영어 → 한국어
        src = decoder_input.get("1.0", tk.END).strip()
        raw_english = decode_from_merong(src)

        try:
            translated = translator.translate(raw_english, src='en', dest='ko').text
        except Exception:
            translated = "[번역 실패]"

        decoder_output.config(state="normal")
        decoder_output.delete("1.0", tk.END)
        decoder_output.insert(tk.END, translated)
        decoder_output.config(state="disabled")
    return "break"

# ===== 복사하기 함수 =====
def copy_output(tab_index):
    if tab_index == 0:
        encoder_output.config(state="normal")
        text = encoder_output.get("1.0", tk.END).strip()
        encoder_output.config(state="disabled")
    else:
        decoder_output.config(state="normal")
        text = decoder_output.get("1.0", tk.END).strip()
        decoder_output.config(state="disabled")
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()

# ===== 붙여넣기 지원 함수 =====
def bind_paste_shortcut(text_widget):
    def paste_event(event=None):
        try:
            pasted = root.clipboard_get()
            text_widget.insert(tk.INSERT, pasted)
        except:
            pass
        return "break"
    text_widget.bind("<Control-v>", paste_event)
    text_widget.bind("<Command-v>", paste_event)
    text_widget.bind("<Button-3>", paste_event)

# ===== GUI 구성 =====
root = tk.Tk()
root.title("메롱통신기")
root.geometry("500x430")

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

# --- 인코더 탭 ---
encoder_tab = ttk.Frame(notebook)
notebook.add(encoder_tab, text="인코더")

encoder_input = tk.Text(encoder_tab, height=5)
encoder_input.pack(padx=10, pady=10, fill="x")
encoder_input.bind("<Return>", translate)
bind_paste_shortcut(encoder_input)

encoder_output = tk.Text(encoder_tab, height=5, state="disabled")
encoder_output.pack(padx=10, pady=(0, 5), fill="x")

btn_frame1 = tk.Frame(encoder_tab)
btn_frame1.pack()
tk.Button(btn_frame1, text="번역하기", command=translate).pack(side="left", padx=5)
tk.Button(btn_frame1, text="복사하기", command=lambda: copy_output(0)).pack(side="left")

# --- 디코더 탭 ---
decoder_tab = ttk.Frame(notebook)
notebook.add(decoder_tab, text="디코더")

decoder_input = tk.Text(decoder_tab, height=5)
decoder_input.pack(padx=10, pady=10, fill="x")
decoder_input.bind("<Return>", translate)

decoder_output = tk.Text(decoder_tab, height=5, state="disabled")
decoder_output.pack(padx=10, pady=(0, 5), fill="x")

# 복사 대신 붙여넣기 버튼 추가
btn_frame2 = tk.Frame(decoder_tab)
btn_frame2.pack()

def paste_to_decoder():
    try:
        pasted = root.clipboard_get()
        decoder_input.insert(tk.INSERT, pasted)
    except:
        pass

tk.Button(btn_frame2, text="번역하기", command=translate, bg="#e0e0e0", fg="black", activebackground="#cccccc", relief="raised").pack(side="left", padx=5)
tk.Button(btn_frame2, text="붙여넣기", command=paste_to_decoder, bg="#e0e0e0", fg="black", activebackground="#cccccc", relief="raised").pack(side="left")


root.mainloop()
