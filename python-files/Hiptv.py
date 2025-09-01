import tkinter as tk
from tkinter import ttk, messagebox, Text
import requests
import vlc
import json
import threading
import time
import os

class IPTVPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced IPTV Player")
        self.root.geometry("1200x800")
        self.root.configure(bg="#6A1B9A")  # تم بنفش اصلی

        # سبک ttk با تم بنفش
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=("Arial", 12), background="#6A1B9A", foreground="white")
        style.configure("TButton", font=("Arial", 12, "bold"), padding=10, background="#AB47BC", foreground="white")
        style.configure("TEntry", font=("Arial", 12))
        style.configure("TNotebook", background="#4A148C")
        style.configure("TNotebook.Tab", background="#AB47BC", foreground="white")

        # پنل چپ: ورودی‌ها و کنترل‌ها
        left_frame = ttk.Frame(root, padding=10)
        left_frame.grid(row=0, column=0, sticky="ns", padx=10, pady=10)
        left_frame.configure(style="TFrame")  # برای سازگاری

        ttk.Label(left_frame, text="DNS Address:").grid(row=0, column=0, pady=5, sticky="w")
        self.dns_entry = ttk.Entry(left_frame, width=30)
        self.dns_entry.grid(row=0, column=1, pady=5)

        ttk.Label(left_frame, text="MAC Address:").grid(row=1, column=0, pady=5, sticky="w")
        self.mac_entry = ttk.Entry(left_frame, width=30)
        self.mac_entry.grid(row=1, column=1, pady=5)

        ttk.Label(left_frame, text="OpenSubtitles API Key:").grid(row=2, column=0, pady=5, sticky="w")
        self.api_key_entry = ttk.Entry(left_frame, width=30)
        self.api_key_entry.grid(row=2, column=1, pady=5)

        self.connect_btn = ttk.Button(left_frame, text="Connect", command=self.connect_to_portal)
        self.connect_btn.grid(row=3, column=0, columnspan=2, pady=10)

        self.record_btn = ttk.Button(left_frame, text="Start Record", command=self.toggle_record, state=tk.DISABLED)
        self.record_btn.grid(row=4, column=0, columnspan=2, pady=10)

        self.sub_btn = ttk.Button(left_frame, text="Find Persian Subs", command=self.find_persian_subs, state=tk.DISABLED)
        self.sub_btn.grid(row=5, column=0, columnspan=2, pady=10)

        self.toggle_info_btn = ttk.Button(left_frame, text="Hide Info", command=self.toggle_info)
        self.toggle_info_btn.grid(row=6, column=0, columnspan=2, pady=10)

        self.info_label = ttk.Label(left_frame, text="Stream Info: N/A", wraplength=300, font=("Arial", 10))
        self.info_label.grid(row=7, column=0, columnspan=2, pady=10)

        # تب‌ها برای Live, VOD, Series, EPG
        self.notebook = ttk.Notebook(root)
        self.notebook.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=1)

        # تب Live
        live_frame = ttk.Frame(self.notebook)
        self.notebook.add(live_frame, text="Live Channels")
        self.channel_listbox = tk.Listbox(live_frame, height=20, width=50, font=("Arial", 12), bg="#FFFFFF")
        self.channel_listbox.pack(fill=tk.BOTH, expand=True)
        self.channel_listbox.bind("<<ListboxSelect>>", self.play_channel)

        # تب VOD
        vod_frame = ttk.Frame(self.notebook)
        self.notebook.add(vod_frame, text="VOD")
        self.vod_listbox = tk.Listbox(vod_frame, height=20, width=50, font=("Arial", 12), bg="#FFFFFF")
        self.vod_listbox.pack(fill=tk.BOTH, expand=True)
        self.vod_listbox.bind("<<ListboxSelect>>", self.play_vod)

        # تب Series
        series_frame = ttk.Frame(self.notebook)
        self.notebook.add(series_frame, text="Series")
        self.series_listbox = tk.Listbox(series_frame, height=20, width=50, font=("Arial", 12), bg="#FFFFFF")
        self.series_listbox.pack(fill=tk.BOTH, expand=True)
        self.series_listbox.bind("<<ListboxSelect>>", self.play_series)

        # تب EPG
        epg_frame = ttk.Frame(self.notebook)
        self.notebook.add(epg_frame, text="EPG")
        self.epg_text = Text(epg_frame, height=20, width=80, font=("Arial", 12), bg="#FFFFFF")
        self.epg_text.pack(fill=tk.BOTH, expand=True)
        self.load_epg_btn = ttk.Button(epg_frame, text="Load EPG for Selected Channel", command=self.load_epg)
        self.load_epg_btn.pack(pady=10)

        # پخش‌کننده
        self.player_frame = tk.Frame(root, bg="black", height=300)
        self.player_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)

        self.instance = vlc.Instance("--no-xlib")
        self.player = self.instance.media_player_new()
        self.player.set_hwnd(self.player_frame.winfo_id())

        # متغیرها
        self.portal_url = ""
        self.token = ""
        self.channels = []
        self.vods = []
        self.series = []
        self.is_recording = False
        self.current_media = None
        self.current_name = ""  # نام فعلی برای زیرنویس
        self.current_type = ""  # live/vod/series
        self.current_id = ""  # id برای EPG
        self.info_visible = True
        self.subtitles = []  # لیست زیرنویس‌ها

    def connect_to_portal(self):
        dns = self.dns_entry.get().strip()
        mac = self.mac_entry.get().strip()
        if not dns or not mac:
            messagebox.showerror("Error", "Please enter DNS and MAC!")
            return

        self.portal_url = f"http://{dns}/c/"
        try:
            auth_url = f"{self.portal_url}portal.php?type=stb&action=handshake&token=&JsHttpRequest=1-xml"
            headers = {
                "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver:2 rev:250 Safari/533.3",
                "X-User-Agent": "Model: MAG250; Link: Ethernet",
                "Referer": self.portal_url,
                "Cookie": f"mac={mac}; stb_lang=en; timezone=GMT"
            }
            response = requests.get(auth_url, headers=headers)
            data = json.loads(response.text)['js']
            self.token = data['token']

            self.get_channels()
            self.get_vods()
            self.get_series()
            self.record_btn.config(state=tk.NORMAL)
            self.sub_btn.config(state=tk.NORMAL)
            messagebox.showinfo("Success", "Connected!")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def get_channels(self):
        if not self.token:
            return
        headers = {"Authorization": f"Bearer {self.token}", "Cookie": f"mac={self.mac_entry.get()}; stb_lang=en; timezone=GMT"}
        channels_url = f"{self.portal_url}portal.php?type=itv&action=get_genres&JsHttpRequest=1-xml"
        response = requests.get(channels_url, headers=headers)
        genres = json.loads(response.text)['js']

        self.channels = []
        self.channel_listbox.delete(0, tk.END)
        for genre in genres:
            genre_id = genre['id']
            genre_channels_url = f"{self.portal_url}portal.php?type=itv&action=get_ordered_list&genre={genre_id}&force_ch_link_check=&fav=0&sortby=number&hd=0&p=1&JsHttpRequest=1-xml"
            response = requests.get(genre_channels_url, headers=headers)
            ch_data = json.loads(response.text)['js']['data']
            for ch in ch_data:
                self.channels.append(ch)
                self.channel_listbox.insert(tk.END, ch['name'])

    def get_vods(self):
        if not self.token:
            return
        headers = {"Authorization": f"Bearer {self.token}", "Cookie": f"mac={self.mac_entry.get()}; stb_lang=en; timezone=GMT"}
        vod_url = f"{self.portal_url}portal.php?type=vod&action=get_genres&JsHttpRequest=1-xml"
        response = requests.get(vod_url, headers=headers)
        genres = json.loads(response.text)['js']

        self.vods = []
        self.vod_listbox.delete(0, tk.END)
        for genre in genres:
            genre_id = genre['id']
            genre_vod_url = f"{self.portal_url}portal.php?type=vod&action=get_ordered_list&genre={genre_id}&p=1&JsHttpRequest=1-xml"
            response = requests.get(genre_vod_url, headers=headers)
            vod_data = json.loads(response.text)['js']['data']
            for vod in vod_data:
                self.vods.append(vod)
                self.vod_listbox.insert(tk.END, vod['name'])

    def get_series(self):
        if not self.token:
            return
        headers = {"Authorization": f"Bearer {self.token}", "Cookie": f"mac={self.mac_entry.get()}; stb_lang=en; timezone=GMT"}
        series_url = f"{self.portal_url}portal.php?type=series&action=get_genres&JsHttpRequest=1-xml"
        response = requests.get(series_url, headers=headers)
        genres = json.loads(response.text)['js']

        self.series = []
        self.series_listbox.delete(0, tk.END)
        for genre in genres:
            genre_id = genre['id']
            genre_series_url = f"{self.portal_url}portal.php?type=series&action=get_ordered_list&genre={genre_id}&p=1&JsHttpRequest=1-xml"
            response = requests.get(genre_series_url, headers=headers)
            series_data = json.loads(response.text)['js']['data']
            for ser in series_data:
                self.series.append(ser)
                self.series_listbox.insert(tk.END, ser['name'])

    def play_channel(self, event):
        selected = self.channel_listbox.curselection()
        if not selected:
            return
        item = self.channels[selected[0]]
        self.current_name = item['name']
        self.current_type = "live"
        self.current_id = item['id']
        cmd = item['cmd'].split(' ')[-1]
        self.play_media(cmd)

    def play_vod(self, event):
        selected = self.vod_listbox.curselection()
        if not selected:
            return
        item = self.vods[selected[0]]
        self.current_name = item['name']
        self.current_type = "vod"
        cmd = item['cmd'].split(' ')[-1]  # یا get_vod_stream_url اگر لازم
        self.play_media(cmd)

    def play_series(self, event):
        selected = self.series_listbox.curselection()
        if not selected:
            return
        item = self.series[selected[0]]
        self.current_name = item['name']
        self.current_type = "series"
        cmd = item['cmd'].split(' ')[-1]  # ممکنه نیاز به get_seasons/episodes باشه
        self.play_media(cmd)

    def play