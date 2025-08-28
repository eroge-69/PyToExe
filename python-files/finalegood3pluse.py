"""
مشغل فيديوهات Google Drive - Tkinter + VLC
الإصدار 4.4 (وضع المشاهدة الذكي):
- ... (كل الميزات السابقة) ...
- إضافة جديدة:
  - زر "وضع المشاهدة" يقوم بتكبير نافذة البرنامج لتناسب الشاشة وإخفاء عناصر التحكم.
  - الزر يتغير إلى "العودة للواجهة" للعودة للحجم الطبيعي.
  - مفتاح 'Esc' يعمل أيضاً للعودة من وضع المشاهدة.
"""

import sys, subprocess

def ensure_package(pkg):
    try: __import__(pkg)
    except ImportError:
        print(f"[INFO] تثبيت {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        __import__(pkg)

for p in ["vlc", "gdown", "requests"]: ensure_package(p)

import tkinter as tk
from tkinter import ttk, messagebox
import vlc, gdown
import os, re, tempfile, shutil, threading, pathlib

COOKIES_FILE = "cookies.json"
if not os.path.exists(COOKIES_FILE):
    print(f"[WARNING] ملف '{COOKIES_FILE}' غير موجود. قد تفشل بعض التحميلات.")
    print("[INFO] يرجى اتباع التعليمات لاستخراج ملف الكوكيز لضمان عمل البرنامج بشكل صحيح.")

def is_drive_folder_url(url: str) -> bool: return "drive.google.com/drive/folders" in url
def is_drive_file_url(url: str) -> bool: return "/file/d/" in url or "drive.google.com/open?id=" in url

def extract_file_id(url: str) -> str | None:
    m = re.search(r"/d/([a-zA-Z0-9_-]+)", url) or re.search(r"[?&]id=([a-zA-Z0-9_-]+)", url)
    return m.group(1) if m else None

def build_direct_download_url_from_id(file_id: str) -> str: return f"https://drive.google.com/uc?export=download&id={file_id}"

class DrivePlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("مشغل فيديوهات - Google Drive (وضع المشاهدة 4.4)")
        self.original_geometry = "1080x720"
        self.root.geometry(self.original_geometry)
        
        self.vlc_instance = vlc.Instance(); self.player = self.vlc_instance.media_player_new()
        self.items = []; self.order = []
        self.current_index = 0; self.repeat_left = -1; self.playing = False
        self.temp_dir = tempfile.mkdtemp(prefix="driveplayer_")
        print(f"[INFO] تم إنشاء المجلد المؤقت: {self.temp_dir}")
        self.tracking_enabled = tk.BooleanVar(value=False)
        self.tracker_id = None; self.data_lock = threading.Lock()
        
        # (## تم التعديل ##) متغير جديد لتتبع الحالة
        self.is_player_mode = False

        self._build_ui(); self._set_vlc_handle()
        ev = self.player.event_manager()
        ev.event_attach(vlc.EventType.MediaPlayerEndReached, self._on_media_end)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        print("[INFO] جاري إغلاق البرنامج...")
        self.player.stop()
        if self.tracker_id: self.root.after_cancel(self.tracker_id)
        if self.temp_dir and os.path.exists(self.temp_dir):
            try: shutil.rmtree(self.temp_dir); print(f"[INFO] تم تنظيف المجلد المؤقت بنجاح.")
            except Exception as e: print(f"[ERROR] فشل في حذف المجلد المؤقت: {e}")
        self.root.destroy()

    def _build_ui(self):
        self.main_frame = tk.Frame(self.root, bg="#0f1630")
        self.main_frame.pack(fill="both", expand=True)
        
        self.video_panel = tk.Frame(self.main_frame, bg="black")
        self.video_panel.pack(fill="both", expand=True)
        
        player_controls_frame = tk.Frame(self.main_frame, bg="#0f1630")
        player_controls_frame.pack(fill="x", padx=12, pady=(5, 5))
        self.fullscreen_button = tk.Button(player_controls_frame, text="وضع المشاهدة", command=self._toggle_player_mode)
        self.fullscreen_button.pack(side="left")

        self.content_frame = tk.Frame(self.main_frame)
        self.content_frame.pack(fill="both", expand=False) # يبدأ بدون توسع

        self.root.bind("<Escape>", self._toggle_player_mode)
        
        link_frame = tk.Frame(self.content_frame); link_frame.pack(fill="x", padx=12, pady=6)
        tk.Label(link_frame,text="رابط ملف / مجلد Google Drive:").pack(side="right");self.link_entry=tk.Entry(link_frame,font=("Arial",12));self.link_entry.pack(side="right",fill="x",expand=True,padx=6);tk.Button(link_frame,text="لصق",command=self._paste_from_clipboard).pack(side="right",padx=4);tk.Button(link_frame,text="تشغيل الرابط",command=self._play_link).pack(side="right",padx=4);tk.Button(link_frame,text="جلب (مجلد)",command=self._fetch_folder_thread).pack(side="right",padx=4);self.track_button=tk.Checkbutton(link_frame,text="تتبع التغييرات تلقائياً",variable=self.tracking_enabled,command=self._toggle_tracking);self.track_button.pack(side="right",padx=10);self.progress=ttk.Progressbar(link_frame,length=200,mode="determinate");self.progress.pack(side="left",padx=6);self.progress_lbl=tk.Label(link_frame,text="في انتظار العملية...");self.progress_lbl.pack(side="left")

        bottom_frame = tk.Frame(self.content_frame); bottom_frame.pack(fill="both", expand=True)
        list_frame=tk.Frame(bottom_frame,bd=1,relief="sunken");list_frame.pack(side="left",fill="both",expand=True,padx=6,pady=6);tk.Label(list_frame,text="قائمة الفيديوهات",font=("Arial",12,"bold")).pack(anchor="w",padx=6,pady=6);self.tree=ttk.Treeview(list_frame,columns=("name","format","duration"),show="headings",height=12);self.tree.heading("name",text="اسم الفيديو");self.tree.heading("format",text="الصيغة");self.tree.heading("duration",text="المدة");self.tree.column("name",width=350);self.tree.column("format",width=80,anchor="center");self.tree.column("duration",width=100,anchor="center");self.tree.pack(fill="both",expand=True,padx=6,pady=(0,6))
        order_frame=tk.Frame(bottom_frame,bd=1,relief="sunken",width=220);order_frame.pack(side="left",fill="y",padx=6,pady=6);tk.Label(order_frame,text="ترتيب التشغيل",font=("Arial",12,"bold")).pack(padx=6,pady=6);self.order_listbox=tk.Listbox(order_frame,height=12);self.order_listbox.pack(fill="both",expand=True,padx=6);tk.Button(order_frame,text="▲ أعلى",command=self._move_up).pack(pady=2);tk.Button(order_frame,text="▼ أسفل",command=self._move_down).pack(pady=2)
        right=tk.Frame(bottom_frame,bd=1,relief="sunken",width=260);right.pack(side="left",fill="y",padx=6,pady=6);tk.Label(right,text="إعدادات",font=("Arial",12,"bold")).pack(padx=6,pady=6);self.start_time=tk.Entry(right,width=8);self.start_time.insert(0,"00:00");self.start_time.pack(pady=2);self.end_time=tk.Entry(right,width=8);self.end_time.insert(0,"23:59");self.end_time.pack(pady=2);self.rep_spin=tk.Spinbox(right,from_=0,to=9999,width=6);self.rep_spin.pack(pady=4);self.rep_spin.delete(0,"end");self.rep_spin.insert(0,"0");tk.Button(right,text="▶️ تشغيل الكل",command=self._start_playback).pack(pady=4);tk.Button(right,text="⏹️ إيقاف",command=self._stop_playback).pack(pady=4)
        self.now_playing_var=tk.StringVar(value="لا يوجد تشغيل حالياً");tk.Label(self.content_frame,textvariable=self.now_playing_var,anchor="w").pack(fill="x",padx=12,pady=6)

    def _toggle_player_mode(self, event=None):
        """ (## تم التعديل ##) التبديل بين وضع المشاهدة والوضع العادي."""
        if not self.is_player_mode:
            # الدخول إلى وضع المشاهدة
            self.content_frame.pack_forget() # إخفاء كل شيء
            
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            self.root.geometry(f"{screen_width}x{screen_height}+0+0")
            
            self.fullscreen_button.config(text="العودة للواجهة")
            self.is_player_mode = True
        else:
            # الخروج من وضع المشاهدة
            self.content_frame.pack(fill="both", expand=False) # إظهار كل شيء
            self.root.geometry(self.original_geometry) # العودة للحجم الأصلي
            
            self.fullscreen_button.config(text="وضع المشاهدة")
            self.is_player_mode = False

    def _set_vlc_handle(self):
        handle=self.video_panel.winfo_id();
        if sys.platform.startswith("win"):self.player.set_hwnd(handle)
        elif sys.platform.startswith("linux"):self.player.set_xwindow(handle)
    
    # --- باقي دوال البرنامج تبقى كما هي ---
    def _paste_from_clipboard(self):
        try:self.link_entry.delete(0,"end");self.link_entry.insert(0,self.root.clipboard_get())
        except:messagebox.showerror("خطأ","لا يوجد نص منسوخ")
    def _move_up(self):
        sel=self.order_listbox.curselection();
        if sel and sel[0]>0:i=sel[0];self.order[i-1],self.order[i]=self.order[i],self.order[i-1];self._refresh_lists();self.order_listbox.selection_set(i-1)
    def _move_down(self):
        sel=self.order_listbox.curselection()
        if sel and sel[0]<len(self.order)-1:i=sel[0];self.order[i+1],self.order[i]=self.order[i],self.order[i+1];self._refresh_lists();self.order_listbox.selection_set(i+1)
    def _play_link(self):
        url=self.link_entry.get().strip()
        if not url:return
        if is_drive_file_url(url):self._play_url(build_direct_download_url_from_id(extract_file_id(url)),name="GoogleDriveFile")
        elif url.startswith("http"):self._play_url(url,name="Link")
        else:messagebox.showerror("خطأ","الرابط غير صحيح")
    def _play_url(self,url,name=""):
        self.player.set_media(self.vlc_instance.media_new(url));self.player.play();self.playing=True;self.now_playing_var.set(f"يشغل الآن: {name}")
    def _start_playback(self):
        if not self.order:return
        rc=int(self.rep_spin.get()or 0);self.repeat_left=-1 if rc==0 else rc;self.current_index=0;self.playing=True;self._play_current()
    def _stop_playback(self):
        self.playing=False;self.player.stop();self.now_playing_var.set("تم الإيقاف.")
    def _play_current(self):
        if not self.playing:return
        if self.current_index>=len(self.order):
            if self.repeat_left==-1:self.current_index=0
            elif self.repeat_left>0:
                self.repeat_left-=1
                if self.repeat_left==0:return self._stop_playback()
                self.current_index=0
        if self.current_index<len(self.order):idx=self.order[self.current_index];item=self.items[idx];self._play_url(item["path"],name=item["name"])
    def _on_media_end(self,ev):
        if not self.playing:return
        self.current_index+=1;self.root.after(500,self._play_current)
    def _refresh_lists(self):
        for row in self.tree.get_children():self.tree.delete(row)
        for it in self.items:self.tree.insert("","end",values=(it["name"],it["format"],it["duration"]))
        self.order_listbox.delete(0,"end")
        for idx in self.order:self.order_listbox.insert("end",self.items[idx]["name"])
    def _fetch_folder_thread(self):
        url = self.link_entry.get().strip()
        if not is_drive_folder_url(url): return messagebox.showerror("خطأ", "الرابط ليس مجلد Google Drive")
        threading.Thread(target=self._fetch_folder_worker, args=(url,), daemon=True).start()
    def _fetch_folder_worker(self, folder_url):
        self.root.after(0, lambda: self.progress_lbl.config(text="جاري التحميل..."))
        self.root.after(0, lambda: self.progress.config(mode="indeterminate"))
        self.root.after(0, self.progress.start)
        try:
            for item in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, item))
            synced_paths = gdown.download_folder(url=folder_url, output=self.temp_dir, quiet=False, use_cookies=True)
            with self.data_lock:
                self.items.clear(); self.order.clear()
                for p in synced_paths:
                    if p.lower().endswith(".part"): continue
                    name = os.path.basename(p); fmt = pathlib.Path(p).suffix.lstrip(".") or "file"
                    self.items.append({"name": name, "format": fmt, "duration": "—", "path": p})
                self.order = list(range(len(self.items)))
            self.root.after(0, self._refresh_lists)
            self.root.after(0, lambda: self.progress_lbl.config(text="تم التحميل."))
        except Exception as e: self.root.after(0, self._update_status_with_error, str(e))
        finally: self.root.after(0, self.progress.stop)
    def _toggle_tracking(self):
        if self.tracking_enabled.get():
            url = self.link_entry.get().strip()
            if not is_drive_folder_url(url):
                messagebox.showwarning("تنبيه", "الرجاء إدخال رابط مجلد Google Drive صالح أولاً.")
                self.tracking_enabled.set(False); return
            print("[INFO] تم تفعيل تتبع المجلد..."); self.progress_lbl.config(text="التتبع مفعل. في انتظار التغييرات...")
            self._track_folder_changes()
        else:
            if self.tracker_id:
                self.root.after_cancel(self.tracker_id); self.tracker_id = None
                print("[INFO] تم إيقاف تتبع المجلد."); self.progress_lbl.config(text="تم إيقاف التتبع.")
    def _track_folder_changes(self):
        if not self.tracking_enabled.get(): return
        folder_url = self.link_entry.get().strip()
        threading.Thread(target=self._track_folder_worker, args=(folder_url,), daemon=True).start()
        self.tracker_id = self.root.after(60000, self._track_folder_changes)
    def _track_folder_worker(self, folder_url):
        try:
            synced_paths = gdown.download_folder(url=folder_url, output=self.temp_dir, quiet=True, use_cookies=True)
            remote_files_map = {os.path.basename(p): p for p in synced_paths if not p.lower().endswith(".part")}
            changes_made = False
            items_to_remove_from_app = []
            with self.data_lock:
                app_files_map = {item['name']: item for item in self.items}
                deleted_filenames = set(app_files_map.keys()) - set(remote_files_map.keys())
                if deleted_filenames:
                    changes_made = True
                    for filename in deleted_filenames:
                        items_to_remove_from_app.append(app_files_map[filename])
                        print(f"[INFO] تم اكتشاف حذف ملف: {filename}")
                added_filenames = set(remote_files_map.keys()) - set(app_files_map.keys())
                if added_filenames:
                    changes_made = True
                    for filename in added_filenames:
                        path = remote_files_map[filename]
                        fmt = pathlib.Path(path).suffix.lstrip(".") or "file"
                        new_item = {"name": filename, "format": fmt, "duration": "—", "path": path}
                        self.items.append(new_item)
                        print(f"[INFO] تم اكتشاف إضافة ملف: {filename}")
                if items_to_remove_from_app:
                    self.items = [item for item in self.items if item not in items_to_remove_from_app]
                if changes_made:
                    self.order = list(range(len(self.items)))
            for item in items_to_remove_from_app:
                try:
                    if os.path.exists(item['path']):
                        os.remove(item['path'])
                        print(f"[INFO] تم حذف الملف المحلي: {item['path']}")
                except OSError as e:
                    print(f"[ERROR] فشل في حذف الملف المحلي {item['path']}: {e}")
            if changes_made:
                self.root.after(0, self._refresh_lists)
                self.root.after(0, lambda: self.progress_lbl.config(text="تمت مزامنة المجلد بنجاح!"))
        except Exception as e:
            self.root.after(0, self._update_status_with_error, str(e))
    def _update_status_with_error(self, error_text):
        user_message = "خطأ: "
        if "Cannot retrieve the public link" in error_text or "Permission denied" in error_text:
            user_message += "فشل تحميل. تحقق من صلاحيات المشاركة أو ملف الكوكيز!"
        elif "No such file or directory: 'cookies.json'" in error_text:
             user_message += "ملف 'cookies.json' غير موجود!"
        else:
            user_message += "حدث خطأ أثناء المزامنة."
        self.progress_lbl.config(text=user_message)
        print(f"[ERROR] Full error: {error_text}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DrivePlayerApp(root)
    root.mainloop()