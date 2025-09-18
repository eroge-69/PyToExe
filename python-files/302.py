# download_gui_autostop.py  （輸出檔名輸入框已放大）
import os
import sys
import threading
import requests
import re
from pathlib import Path
from subprocess import run, CalledProcessError
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext

def resource_path(relative_path):
    """Return path to resource, works for dev and for PyInstaller onefile bundle."""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS  # type: ignore
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class HLSDownloaderApp:
    def __init__(self, root):
        self.root = root
        root.title("HLS 下載器（自動停止）")
        root.geometry("820x520")  # 增加寬度以容納加寬欄位

        frm = ttk.Frame(root, padding=12)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="TS 範例連結（例如 ..._1.ts 或 ...0001.ts）:").grid(column=0, row=0, sticky=tk.W)
        self.url_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.url_var, width=110).grid(column=0, row=1, columnspan=5, sticky=tk.W)

        ttk.Label(frm, text="起始段號:").grid(column=0, row=2, sticky=tk.W, pady=(8,0))
        self.start_var = tk.StringVar(value="1")
        ttk.Entry(frm, textvariable=self.start_var, width=12).grid(column=0, row=3, sticky=tk.W)

        ttk.Label(frm, text="連續失敗門檻 (連續 N 段找不到就停止):").grid(column=1, row=2, sticky=tk.W, pady=(8,0))
        self.miss_threshold_var = tk.StringVar(value="5")
        ttk.Entry(frm, textvariable=self.miss_threshold_var, width=8).grid(column=1, row=3, sticky=tk.W)

        ttk.Label(frm, text="最大段數上限 (選填，避免意外長度):").grid(column=2, row=2, sticky=tk.W, pady=(8,0))
        self.max_segments_var = tk.StringVar(value="10000")
        ttk.Entry(frm, textvariable=self.max_segments_var, width=12).grid(column=2, row=3, sticky=tk.W)

        # 輸出檔名欄位放大：寬度改為 50，並讓它跨兩欄以取得更多空間
        ttk.Label(frm, text="輸出檔名 (mp4):").grid(column=3, row=2, sticky=tk.W, pady=(8,0))
        self.outname_var = tk.StringVar(value="lecture_output.mp4")
        ttk.Entry(frm, textvariable=self.outname_var, width=50).grid(column=3, row=3, columnspan=2, sticky="we")

        ttk.Button(frm, text="選擇輸出資料夾（預設 Downloads）", command=self.choose_outfolder).grid(column=0, row=4, columnspan=2, pady=(10,0), sticky=tk.W)
        self.outfolder = Path.home() / "Downloads"

        self.status_label = ttk.Label(frm, text="準備就緒")
        self.status_label.grid(column=0, row=5, columnspan=5, sticky=tk.W, pady=(6,0))

        self.progress = ttk.Progressbar(frm, orient='horizontal', mode='determinate')
        self.progress.grid(column=0, row=6, columnspan=5, sticky="ew", pady=(8,0))

        btn_frame = ttk.Frame(frm)
        btn_frame.grid(column=0, row=7, columnspan=5, pady=(10,0))
        self.start_btn = ttk.Button(btn_frame, text="開始", command=self.start)
        self.start_btn.pack(side=tk.LEFT, padx=6)
        self.cancel_btn = ttk.Button(btn_frame, text="取消", command=self.cancel, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.LEFT, padx=6)

        ttk.Label(frm, text="日誌:").grid(column=0, row=8, sticky=tk.W, pady=(12,0))
        self.log = scrolledtext.ScrolledText(frm, height=16)
        self.log.grid(column=0, row=9, columnspan=5, sticky="nsew", pady=(4,0))
        frm.rowconfigure(9, weight=1)
        # 讓最後兩個欄位能伸展，避免輸出欄位被擠壓
        frm.columnconfigure(3, weight=1)
        frm.columnconfigure(4, weight=1)

        self._stop_event = threading.Event()
        self.worker = None

    def choose_outfolder(self):
        chosen = filedialog.askdirectory(initialdir=str(self.outfolder))
        if chosen:
            self.outfolder = Path(chosen)
            self.log_write(f"選擇輸出資料夾: {self.outfolder}")

    def log_write(self, txt):
        self.log.insert(tk.END, txt + "\n")
        self.log.see(tk.END)

    def start(self):
        url = self.url_var.get().strip()
        try:
            start = int(self.start_var.get())
            miss_threshold = int(self.miss_threshold_var.get())
            max_segments = int(self.max_segments_var.get()) if self.max_segments_var.get().strip() else None
        except ValueError:
            messagebox.showerror("輸入錯誤", "請輸入合法的數字（起始、門檻、上限）。")
            return
        if not url:
            messagebox.showerror("輸入錯誤", "請輸入一條 .ts 範例連結 (例如 ..._1.ts)。")
            return

        self.start_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self._stop_event.clear()
        self.progress['value'] = 0
        self.status_label.config(text="準備下載中...")
        self.worker = threading.Thread(target=self._run_job, args=(url, start, miss_threshold, max_segments), daemon=True)
        self.worker.start()

    def cancel(self):
        self._stop_event.set()
        self.log_write("用戶要求取消，正在嘗試停止作業...")

    def _find_ffmpeg(self):
        candidate = resource_path("ffmpeg.exe")
        if os.path.isfile(candidate):
            return candidate
        from shutil import which
        w = which("ffmpeg")
        if w:
            return w
        return None

    def _derive_base(self, ts_url):
        # Try regex like (prefix)(number).ts  -> keep prefix and how to format number (we'll just append int)
        m = re.match(r"^(.*?)(\d+)\.ts$", ts_url)
        if m:
            base = m.group(1)  # e.g. ..._
            return base
        # fallback: try splitting on last underscore
        if "_" in ts_url:
            prefix = ts_url.rsplit("_", 1)[0]
            return prefix + "_"
        # fallback: strip extension and append underscore
        if ts_url.endswith(".ts"):
            return ts_url[:-3] + "_"
        # otherwise just return as-is (will probably produce wrong url, but we try)
        return ts_url

    def _run_job(self, ts_url, start, miss_threshold, max_segments):
        try:
            base = self._derive_base(ts_url)
        except Exception:
            base = ts_url.rsplit(".", 1)[0] + "_"

        downloads_folder = self.outfolder
        segments_folder = downloads_folder / "video_segments"
        segments_folder.mkdir(parents=True, exist_ok=True)

        consecutive_misses = 0
        downloaded = 0
        current = start
        # Use indeterminate mode since we don't know total
        self.progress.config(mode='indeterminate')
        self.progress.start(10)

        while True:
            if self._stop_event.is_set():
                self.log_write("[已取消] 中斷下載流程。")
                break
            if max_segments is not None and (current - start) >= max_segments:
                self.log_write(f"[到達上限] 已嘗試 {max_segments} 段，停止。")
                break

            segment_url = f"{base}{current}.ts"
            filename = segments_folder / f"{current}.ts"

            # 如果檔案已存在，視為下載成功（跳過）
            if filename.exists():
                self.log_write(f"[跳過] 已存在: {filename.name}")
                downloaded += 1
                consecutive_misses = 0
                current += 1
                self.status_label.config(text=f"已下載 {downloaded} 段，當前段 {current}，連續失敗 {consecutive_misses}")
                continue

            self.log_write(f"[下載] {segment_url}")
            try:
                resp = requests.get(segment_url, stream=True, timeout=20)
            except requests.RequestException as e:
                self.log_write(f"[例外] {segment_url} -> {e}")
                consecutive_misses += 1
                self.status_label.config(text=f"已下載 {downloaded} 段，當前段 {current}，連續失敗 {consecutive_misses}")
                if consecutive_misses >= miss_threshold:
                    self.log_write(f"[停止] 連續 {miss_threshold} 段失敗，停止下載。")
                    break
                current += 1
                continue

            if resp.status_code == 200:
                try:
                    # Some servers may return 200 but empty content; check content-length if provided
                    content_length = resp.headers.get("Content-Length")
                    if content_length is not None and int(content_length) == 0:
                        self.log_write(f"[空檔] {segment_url} (Content-Length=0)")
                        consecutive_misses += 1
                        if consecutive_misses >= miss_threshold:
                            self.log_write(f"[停止] 連續 {miss_threshold} 段失敗，停止下載。")
                            break
                        current += 1
                        continue

                    with open(filename, "wb") as f:
                        for chunk in resp.iter_content(chunk_size=1024*512):
                            if chunk:
                                f.write(chunk)
                    downloaded += 1
                    consecutive_misses = 0
                    self.log_write(f"[完成] {filename.name}")
                    self.status_label.config(text=f"已下載 {downloaded} 段，當前段 {current}, 連續失敗 {consecutive_misses}")
                except Exception as e:
                    self.log_write(f"[寫檔失敗] {filename.name} -> {e}")
                    consecutive_misses += 1
                    if consecutive_misses >= miss_threshold:
                        self.log_write(f"[停止] 連續 {miss_threshold} 段失敗，停止下載。")
                        break
            else:
                self.log_write(f"[HTTP {resp.status_code}] {segment_url}")
                consecutive_misses += 1
                self.status_label.config(text=f"已下載 {downloaded} 段，當前段 {current}, 連續失敗 {consecutive_misses}")
                if consecutive_misses >= miss_threshold:
                    self.log_write(f"[停止] 連續 {miss_threshold} 段失敗，停止下載。")
                    break

            current += 1

        # 下載迴圈結束
        self.progress.stop()
        self.progress.config(mode='determinate')
        self.progress['value'] = 100

        # 檢查是否有下載到任何檔案
        ts_files = sorted(segments_folder.glob("*.ts"), key=lambda p: int(p.stem) if p.stem.isdigit() else p.stem)
        if not ts_files:
            self.log_write("[結束] 未下載到任何段，沒有可合併的檔案。")
            messagebox.showwarning("未下載任何檔案", "沒有下載到任何 .ts 檔案，請檢查 URL 或起始段號。")
            self._finish_run(success=False)
            return

        # 生成 file_list.txt（只包含存在的段）
        file_list_path = segments_folder / "file_list.txt"
        with open(file_list_path, "w", encoding="utf-8") as f:
            for ts_path in ts_files:
                f.write(f"file '{ts_path.as_posix()}'\n")

        output_path = downloads_folder / self.outname_var.get()
        self.log_write(f"[合併] 生成 {output_path}")

        ffmpeg_path = self._find_ffmpeg()
        if not ffmpeg_path:
            self.log_write("[錯誤] 找不到 ffmpeg。請將 ffmpeg.exe 放旁邊或安裝並加入 PATH。")
            messagebox.showerror("找不到 ffmpeg", "請將 ffmpeg.exe 放在同資料夾或加入環境變數 PATH，或在打包時使用 --add-binary 將 ffmpeg 一起包進 exe。")
            self._finish_run(success=False)
            return

        cmd = [
            ffmpeg_path,
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(file_list_path),
            "-c", "copy",
            "-bsf:a", "aac_adtstoasc",
            str(output_path)
        ]
        try:
            self.log_write(f"[ffmpeg] 執行: {cmd}")
            res = run(cmd, check=True)
            self.log_write("[完成] 合併成功。")
            messagebox.showinfo("完成", f"影片已儲存到：\n{output_path}")
            self._finish_run(success=True)
        except CalledProcessError as e:
            self.log_write(f"[ffmpeg 失敗] returncode={e.returncode}")
            messagebox.showerror("ffmpeg 失敗", f"ffmpeg 執行失敗，回傳碼：{e.returncode}\n請檢查日誌。")
            self._finish_run(success=False)
        except Exception as e:
            self.log_write(f"[例外] {e}")
            messagebox.showerror("錯誤", str(e))
            self._finish_run(success=False)

    def _finish_run(self, success):
        self.start_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        if not success:
            self.log_write("[結束] 未完全成功或被取消。")
            self.status_label.config(text="結束（未完全成功或被取消）")
        else:
            self.log_write("[結束] 成功結束。")
            self.status_label.config(text="完成：已合併影片")

if __name__ == "__main__":
    root = tk.Tk()
    app = HLSDownloaderApp(root)
    root.mainloop()
