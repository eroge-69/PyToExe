import tkinter as tk
from tkinter import messagebox
import yt_dlp

def get_stream_url():
    url = entry.get().strip()
    if not url:
        messagebox.showerror("���", "�� ���� ���� ���� ������ �����")
        return

    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'format': 'best',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            stream_url = info['url']
            result_box.delete(0, tk.END)
            result_box.insert(0, stream_url)
    except Exception as e:
        messagebox.showerror("���", f"��� ��� ����� ��� ������:\n{e}")

# ����� �������
root = tk.Tk()
root.title("YouTube Stream Link Extractor")
root.geometry("400x150")

tk.Label(root, text="���� ���� ������:").pack(pady=5)
entry = tk.Entry(root, width=50)
entry.pack()

tk.Button(root, text="��� ���� ��������", command=get_stream_url).pack(pady=5)

tk.Label(root, text="���� ��������:").pack()
result_box = tk.Entry(root, width=50)
result_box.pack()

root.mainloop()
