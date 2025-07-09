import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import threading
from PIL import Image, ImageTk
import json
from tkinter import colorchooser
import tempfile

# 全局儲存使用者預覽資料
preview_data = {"text": "輸入文字", "x": 400, "y": 225}

CONFIG_FILE = "ff_config.json"

def select_directory(var):
    path = filedialog.askdirectory()
    if path:
        var.set(path)

def select_file(var, filetypes):
    path = filedialog.askopenfilename(filetypes=filetypes)
    if path:
        var.set(path)

def append_log(text):
    log_text.configure(state='normal')
    log_text.insert(tk.END, text + '\n')
    log_text.see(tk.END)
    log_text.configure(state='disabled')

def run_ffmpeg(cmd):
    # 執行 ffmpeg 指令，並即時顯示 log 到日誌區塊
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    while True:
        line = process.stdout.readline()
        if line == '' and process.poll() is not None:
            break
        if line:
            append_log(line.strip())
    return process.poll()

def open_edit_text_window(parent, canvas, text_content, text_rule_var):
    global edit_text_window
    edit_text_window = None  # 直接設為 None，避免重複定義

def preview_edit():
    global preview_window
    # 只允許同時開一個預覽編輯視窗
    if preview_window is not None and tk.Toplevel.winfo_exists(preview_window):
        preview_window.lift()
        preview_window.focus_force()
        return
    preview_window = tk.Toplevel(root)
    preview_window.title("預覽編輯（拖曳文字）")

    text_content = tk.StringVar(value=preview_data["text"])
    text_rule_var = tk.StringVar(value=preview_data.get("rule", ""))

    # 參數區塊（字型、顏色、位置等）
    preview_window.rowconfigure(0, weight=0)
    preview_window.rowconfigure(1, weight=1)
    preview_window.columnconfigure(0, weight=1)
    param_frame = ttk.LabelFrame(preview_window, text="字型與參數", padding=10)
    param_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=(0, 10))
    param_frame.columnconfigure(0, weight=0)
    param_frame.columnconfigure(1, weight=1)
    param_frame.columnconfigure(2, weight=1)
    # --- 設定封面文字可展開區塊（放在 param_frame 內部最上方） ---
    edit_text_toggle = tk.BooleanVar(value=False)
    def toggle_edit_text():
        if edit_text_toggle.get():
            edit_text_frame.grid(row=0, column=0, columnspan=3, sticky='we', padx=0, pady=(0,10))
            edit_text_btn.config(text="收合設定封面文字 ▲")
        else:
            edit_text_frame.grid_remove()
            edit_text_btn.config(text="設定封面文字 ▼")
    edit_text_btn = ttk.Button(param_frame, text="設定封面文字 ▼", command=lambda: edit_text_toggle.set(not edit_text_toggle.get()) or toggle_edit_text())
    edit_text_btn.grid(row=0, column=0, columnspan=3, sticky='w', pady=(0, 5))
    edit_text_frame = ttk.Frame(param_frame, relief='groove', padding=10)
    # 內容
    mode_var = tk.StringVar(value="固定文字" if preview_data.get("rule","")=="" else "特殊文字")
    def on_mode_change():
        if mode_var.get() == "固定文字":
            fixed_entry.config(state="normal")
            prefix_entry.config(state="disabled")
            suffix_entry.config(state="disabled")
        else:
            fixed_entry.config(state="disabled")
            prefix_entry.config(state="normal")
            suffix_entry.config(state="normal")
    mode_frame = ttk.Frame(edit_text_frame)
    mode_frame.pack(anchor='w')
    ttk.Radiobutton(mode_frame, text="固定文字", variable=mode_var, value="固定文字", command=on_mode_change).pack(side='left')
    ttk.Radiobutton(mode_frame, text="特殊文字（自動取中間）", variable=mode_var, value="特殊文字", command=on_mode_change).pack(side='left', padx=(10,0))
    # 固定文字
    ttk.Label(edit_text_frame, text="固定文字內容：").pack(anchor='w', pady=(10, 0))
    fixed_entry = tk.Entry(edit_text_frame, width=40, textvariable=text_content)
    fixed_entry.pack(pady=(0, 5))
    # 特殊文字
    ttk.Label(edit_text_frame, text="前置字串（不含）：").pack(anchor='w', pady=(10, 0))
    prefix_entry = tk.Entry(edit_text_frame, width=40)
    prefix_entry.pack(pady=(0, 5))
    ttk.Label(edit_text_frame, text="後置字串（不含）：").pack(anchor='w', pady=(5, 0))
    suffix_entry = tk.Entry(edit_text_frame, width=40)
    suffix_entry.pack(pady=(0, 5))
    # 初始化特殊文字欄位
    rule = preview_data.get("rule", "")
    if rule.startswith("/cut|"):
        parts = rule[5:].split('|')
        prefix_entry.insert(0, parts[0])
        suffix_entry.insert(0, parts[1] if len(parts)>1 else "")
    # 預覽區
    preview_label = ttk.Label(edit_text_frame, text="預覽結果：", foreground="gray")
    preview_label.pack(anchor='w', pady=(10, 0))
    preview_result = ttk.Label(edit_text_frame, text="", foreground="blue")
    preview_result.pack(anchor='w', pady=(0, 10))
    # 預覽邏輯
    def get_preview_text():
        if mode_var.get() == "固定文字":
            return fixed_entry.get()
        else:
            name = preview_window.get_first_video_name() if hasattr(preview_window, 'get_first_video_name') else ""
            prefix = prefix_entry.get()
            suffix = suffix_entry.get()
            s = name
            if prefix and prefix in s:
                s = s.split(prefix,1)[1]
            if suffix and suffix in s:
                s = s.split(suffix,1)[0]
            return s.strip()
    def update_preview_label(*args):
        preview_result.config(text=get_preview_text())
    fixed_entry.bind('<KeyRelease>', update_preview_label)
    prefix_entry.bind('<KeyRelease>', update_preview_label)
    suffix_entry.bind('<KeyRelease>', update_preview_label)
    mode_var.trace_add('write', lambda *a: update_preview_label())
    update_preview_label()
    # 確認按鈕：同步資料到 preview_data 並觸發預覽
    def save_text():
        if mode_var.get() == "固定文字":
            preview_data["rule"] = ""
            preview_data["text"] = fixed_entry.get()
            text_rule_var.set("")
            text_content.set(fixed_entry.get())
        else:
            preview_data["rule"] = f"/cut|{prefix_entry.get()}|{suffix_entry.get()}"
            text_rule_var.set(preview_data["rule"])
        if hasattr(preview_window, 'update_preview'):
            preview_window.update_preview()
    ttk.Button(edit_text_frame, text="確認", command=save_text).pack(pady=(0, 10))
    on_mode_change()
    # toggle 綁定
    edit_text_toggle.trace_add('write', lambda *args: toggle_edit_text())
    # 預設收合
    toggle_edit_text()

    # 字型來源
    ttk.Label(param_frame, text="字型來源：").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    font_combo = ttk.Combobox(param_frame, textvariable=font_choice_var, values=["預設", "自訂"], width=10, state="readonly")
    font_combo.grid(row=1, column=1, sticky="w", padx=5, pady=5)
    font_button = ttk.Button(param_frame, text="選擇字型", command=lambda: select_file(font_path_var, [("TTF 字型", "*.ttf")]), state="normal" if font_choice_var.get()=="自訂" else "disabled")
    font_button.grid(row=1, column=2, padx=5, pady=5)
    # 字型大小
    ttk.Label(param_frame, text="字型大小：").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    fontsize_spin = ttk.Spinbox(param_frame, from_=10, to=200, textvariable=fontsize_var, width=7)
    fontsize_spin.grid(row=2, column=1, sticky="w", padx=5, pady=5)
    # 字型顏色
    ttk.Label(param_frame, text="字型顏色：").grid(row=3, column=0, sticky="e", padx=5, pady=5)
    def choose_color():
        color_code = colorchooser.askcolor(title="選擇顏色", initialcolor=fontcolor_var.get())
        if color_code[1]:
            fontcolor_var.set(color_code[1])
            color_preview.config(bg=color_code[1])
    color_btn = ttk.Button(param_frame, text="選擇顏色", command=choose_color)
    color_btn.grid(row=3, column=1, sticky="w", padx=(5,0), pady=5)
    # 顏色小色塊
    color_preview = tk.Label(param_frame, bg=fontcolor_var.get(), width=2, height=1, relief='groove')
    color_preview.grid(row=3, column=2, sticky="w", padx=(5,0), pady=5)
    ttk.Entry(param_frame, textvariable=fontcolor_var, width=12, state='readonly').grid(row=3, column=1, sticky="w", padx=(90,5), pady=5)
    # X/Y 滑桿
    from PIL import Image as PILImage
    try:
        img = PILImage.open(thumbnail_var.get())
        img_width, img_height = img.size
    except Exception:
        img_width, img_height = 800, 450
    ttk.Label(param_frame, text="X 位置：").grid(row=4, column=0, sticky="e", padx=5, pady=5)
    x_scale = tk.Scale(param_frame, from_=0, to=img_width, orient='horizontal', resolution=1, showvalue=0, length=300)
    x_scale.set(min(preview_data["x"], img_width))
    x_scale.grid(row=4, column=1, columnspan=2, sticky="we", padx=5, pady=5)
    ttk.Label(param_frame, text="Y 位置：").grid(row=5, column=0, sticky="e", padx=5, pady=5)
    y_scale = tk.Scale(param_frame, from_=0, to=img_height, orient='horizontal', resolution=1, showvalue=0, length=300)
    y_scale.set(min(preview_data["y"], img_height))
    y_scale.grid(row=5, column=1, columnspan=2, sticky="we", padx=5, pady=5)

    # 畫布
    canvas = tk.Canvas(preview_window, bg="black")
    canvas.grid(row=1, column=0, sticky="nsew")
    # canvas 動態縮放預覽圖
    def render_preview_image(event=None):
        tmp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        tmp_img.close()
        name = get_first_video_name()
        rule = preview_data.get("rule", "")
        if rule == "":
            overlay_text = preview_data.get("text", "")
        elif rule.startswith("/cut|"):
            parts = rule[5:].split('|')
            prefix = parts[0]
            suffix = parts[1] if len(parts)>1 else ""
            s = name
            if prefix and prefix in s:
                s = s.split(prefix,1)[1]
            if suffix and suffix in s:
                s = s.split(suffix,1)[0]
            overlay_text = s.strip()
        else:
            overlay_text = name
        font_choice = font_choice_var.get()
        font_path = font_path_var.get() if font_choice == "自訂" else None
        fontsize = fontsize_var.get()
        fontcolor = fontcolor_var.get()
        fontfile_part = f"fontfile='{font_path}':" if font_path else ""
        x = int(x_scale.get())
        y = int(y_scale.get())
        drawtext = (
            f"drawtext={fontfile_part}text='{overlay_text}':fontcolor={fontcolor}:fontsize={fontsize}:x={x}:y={y}:borderw=2:bordercolor=white"
        )
        cmd = ["ffmpeg", "-y", "-i", thumbnail_var.get(), "-vf", drawtext, "-compression_level", "100", tmp_img.name]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            img = PILImage.open(tmp_img.name)
            # canvas 寬高
            c_w = canvas.winfo_width() or 800
            c_h = canvas.winfo_height() or 450
            scale = min(c_w/img_width, c_h/img_height)
            disp_w, disp_h = int(img_width*scale), int(img_height*scale)
            img = img.resize((disp_w, disp_h), PILImage.Resampling.LANCZOS)
            bg_image = ImageTk.PhotoImage(img)
            canvas.delete("all")
            canvas.create_image((c_w-disp_w)//2, (c_h-disp_h)//2, anchor='nw', image=bg_image)
            canvas.bg_image = bg_image
        except Exception as e:
            canvas.delete("all")
        finally:
            try:
                os.unlink(tmp_img.name)
            except Exception:
                pass
    # 取得第一個影片檔名（找資料夾下第一個 mp4 檔，回傳不含副檔名的檔名）
    def get_first_video_name():
        base_dir = base_dir_var.get()
        for root_dir, _, files in os.walk(base_dir):
            for file in files:
                if file.endswith(".mp4"):
                    return os.path.splitext(file)[0]
        return ""
    preview_window.get_first_video_name = get_first_video_name

    def update_preview(*args):
        render_preview_image()
    preview_window.update_preview = update_preview  # 讓子視窗可呼叫
    # 綁定所有參數
    font_choice_var.trace_add('write', update_preview)
    font_path_var.trace_add('write', update_preview)
    fontsize_var.trace_add('write', update_preview)
    fontcolor_var.trace_add('write', update_preview)
    # 滑桿釋放=觸發
    x_scale.bind('<ButtonRelease-1>', lambda e: update_preview())
    y_scale.bind('<ButtonRelease-1', lambda e: update_preview())

    # 刪除產生真實預覽圖按鈕
    # ttk.Button(preview_window, text="產生真實預覽圖", command=render_preview_image).pack(pady=(0, 10))
    # 關閉預覽視窗時，儲存目前參數到 preview_data
    def on_close():
        global preview_window
        preview_data["x"] = x_scale.get()
        preview_data["y"] = y_scale.get()
        preview_data["text"] = text_content.get()
        preview_data["rule"] = text_rule_var.get()
        preview_window.destroy()
        preview_window = None
    preview_window.protocol("WM_DELETE_WINDOW", on_close)

def process_videos():
    base_dir = base_dir_var.get()
    thumbnail = thumbnail_var.get()
    output_dir = output_dir_var.get()
    font_choice = font_choice_var.get()
    font_path = font_path_var.get() if font_choice == "自訂" else None
    font_used = font_path if font_path else "Arial"
    fontsize = fontsize_var.get()
    fontcolor = fontcolor_var.get()

    if not (base_dir and thumbnail and output_dir):
        messagebox.showerror("錯誤", "請完整選擇所有必要資料夾和圖片")
        start_button.config(state='normal')
        return
    if font_choice == "自訂" and not font_path:
        messagebox.showerror("錯誤", "請選擇字型檔")
        start_button.config(state='normal')
        return

    mp4_files = []
    for root_dir, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".mp4"):
                mp4_files.append(os.path.join(root_dir, file))

    if not mp4_files:
        messagebox.showinfo("提示", "找不到任何 mp4 檔案")
        start_button.config(state='normal')
        return

    progress_bar['maximum'] = len(mp4_files)
    progress_bar['value'] = 0
    append_log(f"找到 {len(mp4_files)} 個 mp4 檔案，開始處理...")

    # 修改 process_videos 內 overlay_text 決策
    for idx, filepath in enumerate(mp4_files, 1):
        filename = os.path.basename(filepath)
        name = os.path.splitext(filename)[0]
        output_img = os.path.join(output_dir, f"{name}.png")

        rule = preview_data.get("rule", "/file")
        if rule == "":
            overlay_text = preview_data.get("text", "")
        elif rule.startswith("/file"):
            # 支援 /file | lambda name: ...
            if '|' in rule:
                try:
                    func_code = rule.split('|', 1)[1].strip()
                    func = eval(func_code)
                    overlay_text = func(name)
                except Exception as e:
                    overlay_text = name
            else:
                overlay_text = name
        elif rule.startswith("/regex:"):
            import re
            pattern = rule[7:]
            m = re.search(pattern, name)
            overlay_text = m.group(1) if m else name
        elif rule.startswith("/cut|"):
            parts = rule[5:].split('|')
            prefix = parts[0]
            suffix = parts[1] if len(parts)>1 else ""
            s = name
            if prefix and prefix in s:
                s = s.split(prefix,1)[1]
            if suffix and suffix in s:
                s = s.split(suffix,1)[0]
            overlay_text = s.strip()
        else:
            overlay_text = name  # fallback 成檔名
        fontfile_part = f"fontfile='{font_path}':" if font_path else ""
        drawtext = (
            f"drawtext={fontfile_part}"
            f"text='{overlay_text}':fontcolor={fontcolor}:fontsize={fontsize}:"
            f"x={int(preview_data['x'])}:y={int(preview_data['y'])}:"
            f"borderw=2:bordercolor=white"
        )

        cmd = ["ffmpeg", "-y", "-i", thumbnail, "-vf", drawtext, "-compression_level", "100", output_img]
        append_log(f"處理 {filename} 中...")
        result = run_ffmpeg(cmd)
        if result != 0:
            append_log(f"錯誤: {filename} 處理失敗")
        else:
            append_log(f"完成: {name}.png")
        progress_bar['value'] = idx
        root.update_idletasks()

    append_log("全部處理完畢！")
    messagebox.showinfo("完成", "全部檔案已處理完畢！")
    start_button.config(state='normal')

def start_thread():
    start_button.config(state='disabled')
    log_text.configure(state='normal')
    log_text.delete(1.0, tk.END)
    log_text.configure(state='disabled')
    threading.Thread(target=process_videos, daemon=True).start()

def on_font_choice_change(event):
    font_button.config(state="normal" if font_choice_var.get() == "自訂" else "disabled")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                base_dir_var.set(config.get('base_dir', ''))
                thumbnail_var.set(config.get('thumbnail', ''))
                output_dir_var.set(config.get('output_dir', ''))
                font_path_var.set(config.get('font_path', ''))
                font_choice_var.set(config.get('font_choice', '預設'))
                fontsize_var.set(config.get('fontsize', 80))
                fontcolor_var.set(config.get('fontcolor', '#DA70D6'))
        except Exception as e:
            print(f"讀取設定檔失敗: {e}")

def save_config():
    config = {
        'base_dir': base_dir_var.get(),
        'thumbnail': thumbnail_var.get(),
        'output_dir': output_dir_var.get(),
        'font_path': font_path_var.get(),
        'font_choice': font_choice_var.get(),
        'fontsize': fontsize_var.get(),
        'fontcolor': fontcolor_var.get(),
    }
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"儲存設定檔失敗: {e}")

# 建立 GUI
root = tk.Tk()
root.title("影片封面自動生成器")
root.minsize(700, 500)

# 單一預覽編輯視窗控制
preview_window = None
edit_text_window = None

# 先宣告所有變數
base_dir_var = tk.StringVar()
thumbnail_var = tk.StringVar()
output_dir_var = tk.StringVar()
font_path_var = tk.StringVar()
font_choice_var = tk.StringVar(value="預設")
fontsize_var = tk.IntVar(value=80)
fontcolor_var = tk.StringVar(value="#DA70D6")

# 設定 ttk 主題
style = ttk.Style()
try:
    style.theme_use('clam')
except:
    pass

main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill='both', expand=True)

# 標題
ttk.Label(main_frame, text="影片封面自動生成器", font=("Arial", 20, "bold")).pack(pady=(0, 15))

# 區塊1：路徑設定
path_frame = ttk.LabelFrame(main_frame, text="路徑設定", padding=15)
path_frame.pack(fill='x', pady=(0, 15))

def add_row(label, var, browse_type, row, filetypes=None):
    ttk.Label(path_frame, text=label).grid(row=row, column=0, sticky="e", padx=5, pady=5)
    ttk.Entry(path_frame, textvariable=var, width=50).grid(row=row, column=1, padx=5, pady=5)
    ttk.Button(path_frame, text="選擇", width=8, command=lambda: select_directory(var) if browse_type == 'dir' else select_file(var, filetypes)).grid(row=row, column=2, padx=5, pady=5)

add_row("影片資料夾：", base_dir_var, 'dir', 0)
add_row("縮圖圖片(.png)：", thumbnail_var, 'file', 1, [("PNG Images", "*.png")])
add_row("輸出資料夾：", output_dir_var, 'dir', 2)

# 分隔線
sep = ttk.Separator(main_frame, orient='horizontal')
sep.pack(fill='x', pady=10)

# 預覽與啟動按鈕
btn_frame = ttk.Frame(main_frame)
btn_frame.pack(fill='x', pady=(0, 10))

ttk.Button(btn_frame, text="預覽編輯", command=preview_edit, style="Accent.TButton").pack(side='left', padx=5)
start_button = ttk.Button(btn_frame, text="開始處理", command=start_thread, style="Accent.TButton")
start_button.pack(side='right', padx=5)
start_button.configure(style="Accent.TButton")

# 進度條
progress_bar = ttk.Progressbar(main_frame, length=600)
progress_bar.pack(pady=(5,0))

# 日誌區塊（可收合）
log_frame = ttk.LabelFrame(main_frame, text="處理日誌", padding=10)
log_frame.pack(fill='x', pady=(10, 0))

# 收合/展開按鈕
log_toggle = tk.BooleanVar(value=False)

def toggle_log():
    if log_toggle.get():
        log_text.pack(fill='both', expand=True)
        log_toggle_btn.config(text="隱藏日誌 ▲")
    else:
        log_text.pack_forget()
        log_toggle_btn.config(text="顯示日誌 ▼")

log_toggle_btn = ttk.Button(log_frame, text="顯示日誌 ▼", command=lambda: log_toggle.set(not log_toggle.get()) or toggle_log())
log_toggle_btn.pack(anchor='w', pady=(0, 5))

log_text = tk.Text(log_frame, height=12, width=80, state='disabled', bg='#f8f8f8', fg='black', relief='flat', font=("Consolas", 11))
# 預設隱藏
# log_text.pack(fill='both', expand=True)

log_toggle.trace_add('write', lambda *args: toggle_log())

# 載入上次設定
load_config()

# 關閉時自動儲存設定
root.protocol("WM_DELETE_WINDOW", lambda: (save_config(), root.destroy()))

root.mainloop()



