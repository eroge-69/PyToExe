# -*- coding: utf-8 -*-
import PySimpleGUI as sg
import yt_dlp
import os
import threading
import winsound

# ---------------- GUI 介面 ----------------
layout = [
    [sg.Text("貼上 YouTube 連結 (每行一個)")],
    [sg.Multiline(size=(60,10), key="-URLS-")],
    [sg.Text("下載資料夾:"), sg.Input(key="-FOLDER-"), sg.FolderBrowse()],
    [sg.Button("下載"), sg.Button("離開")],
    [sg.Text("下載狀態:")],
    [sg.Output(size=(80,20))],
]

window = sg.Window("YouTube 轉 MP3", layout, finalize=True)

# ---------------- 下載進度 Hook ----------------
def progress_hook(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded = d.get('downloaded_bytes', 0)
        if total:
            percent = downloaded / total * 100
            print(f"下載中: {d['filename']} - {percent:.1f}%")
    elif d['status'] == 'finished':
        print(f"下載完成: {d['filename']}")
        try:
            winsound.Beep(800, 300)
        except:
            pass

# ---------------- 下載函數 ----------------
def download(urls, folder):
    for url in urls:
        url = url.strip()
        if not url:
            continue
        print(f"開始下載: {url}")
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '0',
            }],
            'progress_hooks': [progress_hook],
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            print(f"下載失敗: {url} - {e}")

    # 全部完成提示音
    try:
        winsound.Beep(1000, 500)
        winsound.Beep(1200, 500)
    except:
        pass
    print("全部下載完成!")

# ---------------- GUI 事件處理 ----------------
while True:
    event, values = window.read()
    if event in (sg.WINDOW_CLOSED, "離開"):
        break
    if event == "下載":
        urls = values["-URLS-"].splitlines()
        folder = values["-FOLDER-"] or os.getcwd()
        threading.Thread(target=download, args=(urls, folder), daemon=True).start()

window.close()
