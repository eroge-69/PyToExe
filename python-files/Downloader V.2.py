import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import subprocess
import threading
import os
import sys
import time

process = None  # global process handle
script_dir = os.path.dirname(os.path.abspath(__file__))

# --- helper: update log safely ---
def update_log(msg):
    log_text.config(state="normal")
    log_text.insert(tk.END, msg + "\n")
    log_text.see(tk.END)
    log_text.config(state="disabled")

# --- pilih folder save ---
def select_directory():
    folder = filedialog.askdirectory()
    if folder:
        folder_var.set(folder)

# --- stop download ---
def stop_download():
    global process
    if process and process.poll() is None:
        update_log("⛔ Menghentikan proses...")
        try:
            process.terminate()
            # beri waktu proses berhenti
            time.sleep(1.0)
            if process.poll() is None:
                process.kill()
        except Exception as e:
            update_log(f"Error ketika menghentikan proses: {e}")
        finally:
            progress_bar.stop()
            update_log("⛔ Proses dihentikan.")
            process = None
    else:
        update_log("Tidak ada proses yang berjalan.")

# --- start download ---
def start_download():
    global process
    links = link_textbox.get("1.0", "end-1c").strip()
    save_path = folder_var.get().strip()

    if not links:
        messagebox.showerror("Error", "Masukkan minimal 1 link TikTok!")
        return
    if not save_path:
        messagebox.showerror("Error", "Pilih folder penyimpanan terlebih dahulu!")
        return

    # pastikan tiktokBulkDownloader.py ada di folder script
    downloader_py = os.path.join(script_dir, "tiktokBulkDownloader.py")
    if not os.path.exists(downloader_py):
        messagebox.showerror("Error", f"File tiktokBulkDownloader.py tidak ditemukan di:\n{script_dir}\n\nLetakkan file tersebut di folder yang sama dengan Downloader.py.")
        return

    # tulis links.txt di folder script (jangan di cwd yang random)
    temp_file = os.path.join(script_dir, "links.txt")
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(links)
    except Exception as e:
        messagebox.showerror("Error", f"Gagal menulis {temp_file}: {e}")
        return

    update_log("🚀 Memulai download...")
    progress_bar.start(10)

    def run_proc():
        global process
        try:
            # panggil script menggunakan absolute path, dan set cwd ke script_dir
            cmd = [sys.executable, downloader_py, "--links", temp_file]
            process = subprocess.Popen(
                cmd,
                cwd=script_dir,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1  # line-buffered
            )

            # segera kirimkan folder tujuan ke stdin (jawaban untuk input() di script)
            try:
                process.stdin.write(save_path + "\n")
                process.stdin.flush()
            except Exception as e:
                update_log(f"⚠️ Gagal mengirim folder ke script: {e}")

            # baca output baris demi baris
            for line in process.stdout:
                if line is None:
                    break
                update_log(line.rstrip())

            process.wait()

            if process.returncode == 0:
                update_log("✅ Download selesai!")
                messagebox.showinfo("Selesai", "Download selesai!")
            else:
                update_log(f"❌ Script keluar dengan kode {process.returncode}")
                messagebox.showerror("Error", f"Script keluar dengan kode {process.returncode}. Lihat log untuk detail.")

        except FileNotFoundError as fnf:
            update_log(f"❌ File or command not found: {fnf}")
            messagebox.showerror("Error", f"File not found: {fnf}")
        except Exception as e:
            update_log(f"❌ Error saat menjalankan downloader: {e}")
            messagebox.showerror("Error", f"Gagal menjalankan downloader:\n{e}")
        finally:
            try:
                progress_bar.stop()
            except:
                pass
            process = None
            # optionally delete links.txt? keep it for debugging
            # if os.path.exists(temp_file): os.remove(temp_file)

    # run in thread agar GUI tetap responsive
    threading.Thread(target=run_proc, daemon=True).start()

# --- GUI layout ---
root = tk.Tk()
root.title("TikTok Bulk Downloader GUI")
root.geometry("820x680")
root.resizable(False, False)

style = ttk.Style()
style.configure("TButton", font=("Segoe UI", 10))
style.configure("TLabel", font=("Segoe UI", 10))

# links frame
frame_links = tk.LabelFrame(root, text="📋 Masukkan link TikTok (1 baris = 1 link)", padx=8, pady=8)
frame_links.place(x=10, y=10, width=790, height=260)

link_textbox = tk.Text(frame_links, font=("Consolas", 11), wrap="none")
link_textbox.pack(side="left", fill="both", expand=True)

scroll_y = tk.Scrollbar(frame_links, orient="vertical", command=link_textbox.yview)
scroll_y.pack(side="right", fill="y")
link_textbox.config(yscrollcommand=scroll_y.set)

scroll_x = tk.Scrollbar(root, orient="horizontal", command=link_textbox.xview)
scroll_x.place(x=12, y=268, width=770)
link_textbox.config(xscrollcommand=scroll_x.set)

# folder picker
frame_folder = tk.LabelFrame(root, text="📂 Folder Penyimpanan", padx=8, pady=8)
frame_folder.place(x=10, y=290, width=790, height=60)

folder_var = tk.StringVar()
entry_folder = tk.Entry(frame_folder, textvariable=folder_var, font=("Consolas", 11))
entry_folder.pack(side="left", fill="x", expand=True, padx=(2,8))
btn_browse = ttk.Button(frame_folder, text="Browse", command=select_directory)
btn_browse.pack(side="left")

# buttons
btn_start = tk.Button(root, text="⬇️ Mulai Download", command=start_download, bg="#4CAF50", fg="white", font=("Segoe UI", 11, "bold"))
btn_start.place(x=200, y=360, width=200, height=40)
btn_stop = tk.Button(root, text="⛔ Stop", command=stop_download, bg="#f44336", fg="white", font=("Segoe UI", 11, "bold"))
btn_stop.place(x=420, y=360, width=120, height=40)

# progress bar
progress_bar = ttk.Progressbar(root, mode="indeterminate")
progress_bar.place(x=20, y=420, width=770, height=18)
progress_bar.stop()

# log area
frame_log = tk.LabelFrame(root, text="🖥️ Log", padx=8, pady=8)
frame_log.place(x=10, y=450, width=790, height=220)

log_text = tk.Text(frame_log, font=("Consolas", 10), bg="black", fg="lime", state="disabled")
log_text.pack(side="left", fill="both", expand=True)

log_scroll = tk.Scrollbar(frame_log, command=log_text.yview)
log_scroll.pack(side="right", fill="y")
log_text.config(yscrollcommand=log_scroll.set)

# start GUI
root.mainloop()
