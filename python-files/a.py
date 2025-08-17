{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import tkinter as tk\
from tkinter import messagebox\
import requests\
from datetime import datetime\
from elevenlabs import ElevenLabs\
import os\
\
# API key dari ElevenLabs\
API_KEY = "sk_5b1fe7586d985a91b0102508595cb1522a89455a65f22c4f"\
client = ElevenLabs(api_key=API_KEY)\
\
# Voice ID untuk bahasa Indonesia (Rachel)\
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"\
\
def download_text():\
    url = "https://bebek.my.id/a.txt"\
    response = requests.get(url)\
    response.raise_for_status()\
    return response.text\
\
def get_today_text():\
    all_text = download_text()\
    today = datetime.now().strftime("%A, %-d %B")  # contoh: Minggu, 17 Agustus\
    sections = all_text.split("\\n\\n")\
    for section in sections:\
        if today in section:\
            return section\
    return "Teks untuk hari ini tidak ditemukan."\
\
def generate_audio():\
    try:\
        text_to_read = get_today_text()\
\
        # Konversi teks ke audio\
        response = client.text_to_speech.convert(\
            voice_id=VOICE_ID,\
            text=text_to_read,\
            model_id="eleven_multilingual_v2",\
            output_format="mp3_44100_128"\
        )\
\
        filename = f"bacaan_\{datetime.now().strftime('%Y%m%d')\}.mp3"\
        with open(filename, "wb") as f:\
            for chunk in response:\
                f.write(chunk)\
\
        messagebox.showinfo("Sukses", f"File audio berhasil dibuat: \{filename\}")\
\
    except Exception as e:\
        messagebox.showerror("Error", str(e))\
\
# GUI\
root = tk.Tk()\
root.title("Bacaan Harian - Audio")\
root.geometry("300x150")\
\
label = tk.Label(root, text="Klik tombol untuk buat audio\\nbacaan harian hari ini.", pady=10)\
label.pack()\
\
btn = tk.Button(root, text="Buat Audio", command=generate_audio, bg="green", fg="white")\
btn.pack(pady=20)\
\
root.mainloop()}