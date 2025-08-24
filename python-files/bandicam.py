import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time
import cv2
import mss
import numpy as np
import os
import subprocess
from datetime import datetime, timedelta
import json

class ScreenRecorder:
    def __init__(self, master):
        self.master = master
        
        master.withdraw()
        
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        
        # Значения по умолчанию
        self.record_width = 742 
        self.record_height = 340
        self.fps = 60
        self.output_folder = os.getcwd()
        self.video_format = ".wmv"
        self.window_width = 750
        self.window_height = 50
        self.window_x = None
        self.window_y = None
        self.is_full_screen_mode = tk.BooleanVar(value=False)
        
        # Загрузка настроек из файла
        self.load_settings()

        # Если координаты или размеры не загружены, используем значения по умолчанию
        if self.window_x is None:
            self.window_x = (screen_width / 2) - (self.window_width / 2)
        if self.window_y is None:
            self.window_y = (screen_height / 2) - (self.window_height / 2) - 100
        
        # Если в настройках есть is_full_screen_mode, используем его для инициализации.
        # Если запись была в режиме полного экрана, сбрасываем область на значения по умолчанию.
        if self.is_full_screen_mode.get():
             self.record_width = 742 
             self.record_height = 340
        
        master.geometry(f"{int(self.window_width)}x{int(self.window_height)}+{int(self.window_x)}+{int(self.window_y)}")
        master.deiconify()

        master.resizable(True, False) # Теперь можно менять ширину окна
        
        master.attributes('-topmost', True) 

        self.recording = False
        self.paused = False
        self.output_filename = "" 
        self.video_writer = None
        self.record_thread = None

        self.record_x = 0
        self.record_y = 0
        
        self.start_time = None
        self.pause_start_time = None
        self.elapsed_time_on_pause = timedelta(seconds=0)
        self.timer_id = None
        
        self.frames = []
        
        self.frame_thickness = 10
        
        self.resize_mode = None 
        self.start_x = 0
        self.start_y = 0
        self.initial_width = self.record_width
        self.initial_height = self.record_height
        
        # Переменные для перетаскивания
        self.drag_x = 0
        self.drag_y = 0
        self.is_dragging = False

        self.video_format_var = tk.StringVar(self.master)
        self.video_format_var.set(self.video_format)
        self.video_format_var.trace('w', self.save_format_setting)
        
        self.create_widgets()
        
        self.default_start_button_bg = self.start_button.cget('bg')
        
        self.create_frames()
        self.master.bind("<Configure>", self.on_main_window_move)
        
        self.update_window_title()

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        button_frame = tk.Frame(self.master)
        button_frame.pack(expand=True, fill=tk.BOTH)

        self.start_button = tk.Button(button_frame, text="▶️", font=("Segoe UI Symbol", 14), command=self.start_recording)
        self.start_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.pause_button = tk.Button(button_frame, text="⏸️", font=("Segoe UI Symbol", 14), command=self.pause_recording, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.stop_button = tk.Button(button_frame, text="⏹️", font=("Segoe UI Symbol", 14), command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.screenshot_button = tk.Button(button_frame, text="📷", font=("Segoe UI Symbol", 14), command=self.take_screenshot)
        self.screenshot_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.open_folder_button = tk.Button(button_frame, text="📁", font=("Segoe UI Symbol", 14))
        self.open_folder_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.open_folder_button.bind("<Button-1>", self.open_output_folder)
        self.open_folder_button.bind("<Button-3>", self.ask_output_folder)
        
        format_label = tk.Label(button_frame, text="Формат:", font=("Segoe UI", 12))
        format_label.pack(side=tk.LEFT, padx=(10, 0), pady=5)

        formats = [".wmv", ".mp4"]
        format_menu = tk.OptionMenu(button_frame, self.video_format_var, *formats)
        format_menu.config(font=("Segoe UI", 12))
        format_menu.pack(side=tk.LEFT, padx=5, pady=5)
        
        fps_label = tk.Label(button_frame, text="FPS:", font=("Segoe UI", 12))
        fps_label.pack(side=tk.RIGHT, padx=5, pady=5)
        self.fps_entry = tk.Entry(button_frame, width=4, font=("Segoe UI", 12))
        self.fps_entry.insert(0, str(self.fps)) 
        self.fps_entry.pack(side=tk.RIGHT, pady=5)

        self.timer_label = tk.Label(button_frame, text="00:00:00", font=("Segoe UI", 14), fg="red")
        self.timer_label.pack(side=tk.RIGHT, padx=5, pady=5)
        
        self.capture_mode_switch = tk.Checkbutton(
            button_frame,
            text="Весь экран",
            variable=self.is_full_screen_mode,
            command=self.toggle_capture_mode
        )
        self.capture_mode_switch.pack(side=tk.RIGHT, padx=5, pady=5)
        
    def save_format_setting(self, *args):
        self.video_format = self.video_format_var.get()
        self.save_settings()

    def create_frames(self):
        if not self.frames:
            for i in range(4):
                frame = tk.Toplevel(self.master)
                frame.overrideredirect(True)
                frame.attributes('-topmost', True)
                frame.config(bg='red')
                # Теперь привязываем события к каждой рамке
                frame.bind("<ButtonPress-1>", self.on_frame_drag_start)
                frame.bind("<B1-Motion>", self.on_frame_drag)
                frame.bind("<ButtonRelease-1>", self.on_frame_drag_end)
                self.frames.append(frame)
        
        close_button = tk.Button(self.frames[0], text="x", fg="black", bg="red",
                                 font=("Arial", 12, "bold"), bd=0, highlightthickness=0,
                                 command=self.close_capture_frames, padx=5, pady=1)
        close_button.pack(side=tk.RIGHT, padx=2)
        
        # Для боковых рамок привязываем и ресайз, и перетаскивание
        self.frames[1].bind("<ButtonPress-1>", lambda event: self.on_frame_press(event, 'height') or self.on_frame_drag_start(event))
        self.frames[1].bind("<B1-Motion>", self.on_frame_drag_or_resize)
        self.frames[1].bind("<ButtonRelease-1>", lambda event: self.on_frame_release(event) or self.on_frame_drag_end(event))
        self.frames[1].config(cursor='sb_down_arrow')

        self.frames[3].bind("<ButtonPress-1>", lambda event: self.on_frame_press(event, 'width') or self.on_frame_drag_start(event))
        self.frames[3].bind("<B1-Motion>", self.on_frame_drag_or_resize)
        self.frames[3].bind("<ButtonRelease-1>", lambda event: self.on_frame_release(event) or self.on_frame_drag_end(event))
        self.frames[3].config(cursor='sb_right_arrow')

        if not self.is_full_screen_mode.get():
            self.show_frames()
        else:
            self.hide_frames()

    # Функции для перетаскивания рамок
    def on_frame_drag_start(self, event):
        self.drag_x = event.x_root
        self.drag_y = event.y_root
        self.is_dragging = True

    def on_frame_drag_or_resize(self, event):
        if self.resize_mode:
            self.on_frame_drag(event)
        elif self.is_dragging:
            self.on_frame_drag(event)

    def on_frame_drag(self, event):
        if self.is_dragging and not self.resize_mode:
            delta_x = event.x_root - self.drag_x
            delta_y = event.y_root - self.drag_y

            for frame in self.frames:
                new_x = frame.winfo_x() + delta_x
                new_y = frame.winfo_y() + delta_y
                frame.geometry(f"+{new_x}+{new_y}")

            self.drag_x = event.x_root
            self.drag_y = event.y_root
            self.update_capture_area()
            self.update_window_title()
        
        elif self.resize_mode:
            if self.resize_mode == 'width':
                left_capture_area_x = self.frames[2].winfo_x() + self.frame_thickness
                new_record_width = event.x_root - left_capture_area_x

                if new_record_width > 50:
                    self.record_width = new_record_width
                    self.on_main_window_move(None)
                    self.update_window_title()

            elif self.resize_mode == 'height':
                new_height = self.initial_height + (event.y_root - self.frames[1].winfo_y())
                if new_height > 50:
                    self.record_height = new_height
                    self.on_main_window_move(None)
                    self.update_window_title()


    def on_frame_drag_end(self, event):
        self.is_dragging = False

    def update_capture_area(self):
        if not self.frames:
            return
        
        self.record_x = self.frames[2].winfo_x() + self.frame_thickness
        self.record_y = self.frames[0].winfo_y() + self.frame_thickness
        self.record_width = self.frames[0].winfo_width() - self.frame_thickness * 2
        self.record_height = self.frames[2].winfo_height()

    def close_capture_frames(self):
        self.is_full_screen_mode.set(True)
        self.toggle_capture_mode()

    def show_frames(self):
        for frame in self.frames:
            frame.deiconify()
        self.on_main_window_move(None)

    def hide_frames(self):
        for frame in self.frames:
            frame.withdraw()

    def toggle_capture_mode(self):
        if self.is_full_screen_mode.get():
            self.hide_frames()
            self.capture_mode_switch.config(text="Область")
            
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                self.record_x = monitor['left']
                self.record_y = monitor['top']
                self.record_width = monitor['width']
                self.record_height = monitor['height']
        else:
            self.capture_mode_switch.config(text="Весь экран")
            
            # При переключении в режим области, используем сохраненные размеры
            self.record_width = 742
            self.record_height = 340
            
            self.show_frames()
            self.master.update()
            
        self.update_window_title()
        
    def update_window_title(self):
        if not self.frames:
            return
        
        try:
            if self.is_full_screen_mode.get():
                self.master.title(f"📸 Запись экрана (Захват: ВЕСЬ ЭКРАН)")
            else:
                width = self.frames[0].winfo_width() - self.frame_thickness * 2
                height = self.frames[2].winfo_height()
                self.master.title(f"📸 Запись экрана (Размер захвата: {width}x{height} px)")
        except tk.TclError:
            self.master.title(f"📸 Запись экрана")

    def on_frame_press(self, event, mode):
        self.resize_mode = mode
        self.start_x = event.x
        self.start_y = event.y
        self.initial_width = self.record_width
        self.initial_height = self.record_height

    def on_frame_release(self, event):
        self.resize_mode = None

    def on_main_window_move(self, event):
        if self.is_full_screen_mode.get() or not self.frames:
            return
        
        x, y = self.master.winfo_x(), self.master.winfo_y()
        main_width, main_height = self.master.winfo_width(), self.master.winfo_height()
        
        offset_y = y + main_height + 40 
        offset_x = 10
        
        horizontal_width = self.record_width + self.frame_thickness * 2
        vertical_height = self.record_height
        
        # Обновление размеров и позиции рамок с учетом новой толщины
        self.frames[0].geometry(f"{horizontal_width}x{self.frame_thickness}+{x - self.frame_thickness + offset_x}+{offset_y}")
        self.frames[1].geometry(f"{horizontal_width}x{self.frame_thickness}+{x - self.frame_thickness + offset_x}+{offset_y + vertical_height + self.frame_thickness}")
        self.frames[2].geometry(f"{self.frame_thickness}x{vertical_height}+{x - self.frame_thickness + offset_x}+{offset_y + self.frame_thickness}")
        self.frames[3].geometry(f"{self.frame_thickness}x{vertical_height}+{x + self.record_width + offset_x}+{offset_y + self.frame_thickness}")
        
        self.update_capture_area()

        self.update_window_title()

    def load_settings(self):
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
                self.record_width = settings.get("record_width", self.record_width)
                self.record_height = settings.get("record_height", self.record_height)
                self.fps = settings.get("fps", self.fps)
                self.output_folder = settings.get("output_folder", self.output_folder)
                self.video_format = settings.get("video_format", self.video_format)
                self.window_x = settings.get("window_x", None)
                self.window_y = settings.get("window_y", None)
                self.window_width = settings.get("window_width", self.window_width)
                self.window_height = settings.get("window_height", self.window_height)
                self.is_full_screen_mode.set(settings.get("is_full_screen_mode", False))
                
        except (FileNotFoundError, json.JSONDecodeError):
            print("Файл настроек не найден или поврежден. Используются значения по умолчанию.")

    def save_settings(self):
        try:
            fps_value = int(self.fps_entry.get())
        except (ValueError, IndexError):
            fps_value = self.fps

        settings = {
            "record_width": self.record_width,
            "record_height": self.record_height,
            "fps": fps_value,
            "output_folder": self.output_folder,
            "video_format": self.video_format,
            "window_x": self.master.winfo_x(),
            "window_y": self.master.winfo_y(),
            "window_width": self.master.winfo_width(),
            "window_height": self.master.winfo_height(),
            "is_full_screen_mode": self.is_full_screen_mode.get()
        }
        
        try:
            with open("settings.json", "w") as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            print(f"Не удалось сохранить настройки: {e}")

    def on_closing(self):
        # Если закрываем в режиме полного экрана, сбрасываем размеры захвата на дефолтные
        if self.is_full_screen_mode.get():
            self.record_width = 742
            self.record_height = 340

        self.stop_recording()
        self.save_settings()
        self.master.destroy()
        
    def ask_output_folder(self, event=None):
        new_folder = filedialog.askdirectory(initialdir=self.output_folder)
        if new_folder:
            self.output_folder = new_folder
            print(f"Новая папка для сохранения: {self.output_folder}")
            self.open_folder_button.config(fg="green") 
            self.master.after(1000, lambda: self.open_folder_button.config(fg="black"))


    def open_output_folder(self, event=None):
        if not self.output_folder or not os.path.exists(self.output_folder): 
            folder_path = os.getcwd()
        else:
            folder_path = self.output_folder

        try:
            if os.name == 'nt':
                os.startfile(folder_path)
            elif os.uname().sysname == 'Darwin':
                subprocess.run(['open', folder_path])
            else:
                subprocess.run(['xdg-open', folder_path])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть папку: {e}")

    def update_timer(self):
        if self.recording and not self.paused and self.start_time:
            current_elapsed_time = (datetime.now() - self.start_time) - self.elapsed_time_on_pause
            
            total_seconds = int(current_elapsed_time.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            
            time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            self.timer_label.config(text=time_str)
        
        self.timer_id = self.master.after(1000, self.update_timer)

    def record_screen(self):
        try:
            fps = int(self.fps_entry.get())
            if fps <= 0:
                fps = 30
        except (ValueError, IndexError):
            fps = 30
        
        sct = mss.mss()
        
        if self.is_full_screen_mode.get():
            monitor = sct.monitors[1]
        else:
            monitor = {"top": self.record_y, "left": self.record_x,
                       "width": self.record_width, "height": self.record_height}

        if self.video_format == ".mp4":
            fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
            extension = ".mp4"
        else:
            fourcc = cv2.VideoWriter_fourcc(*'WMV2')
            extension = ".wmv"

        width_aligned = monitor["width"] - (monitor["width"] % 2)
        height_aligned = monitor["height"] - (monitor["height"] % 2)

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder, exist_ok=True)
            
        self.output_filename = os.path.join(self.output_folder, f"screen_record_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}{extension}")
        self.video_writer = cv2.VideoWriter(self.output_filename, fourcc, fps, (width_aligned, height_aligned))

        if not self.video_writer.isOpened():
            messagebox.showerror("Ошибка", f"Не удалось инициализировать VideoWriter для формата {extension}. Возможно, кодек не поддерживается.")
            self.stop_recording()
            return

        while self.recording:
            if not self.paused:
                try:
                    sct_img = sct.grab(monitor)
                    img = np.array(sct_img)
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

                    if img_rgb.shape[1] != width_aligned or img_rgb.shape[0] != height_aligned:
                        img_rgb = cv2.resize(img_rgb, (width_aligned, height_aligned))

                    self.video_writer.write(img_rgb)
                except mss.exception.ScreenShotError as e:
                    print(f"Ошибка захвата экрана: {e}. Возможно, область записи выходит за границы экрана.")
                    self.stop_recording()
                    break
                except Exception as e:
                    print(f"Произошла ошибка во время записи: {e}")
                    self.stop_recording()
                    break
            time.sleep(1 / fps)

        if self.video_writer:
            self.video_writer.release()
        print(f"Видео сохранено в: {os.path.abspath(self.output_filename)}")

    def start_recording(self):
        if self.recording:
            return

        self.recording = True
        self.paused = False
        
        self.start_time = datetime.now()
        self.pause_start_time = None
        self.elapsed_time_on_pause = timedelta(seconds=0)
        self.timer_label.config(text="00:00:00") 
        self.update_timer()

        self.start_button.config(state=tk.DISABLED, bg="red")
        self.pause_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL)
        self.screenshot_button.config(state=tk.DISABLED) 

        self.record_thread = threading.Thread(target=self.record_screen)
        self.record_thread.start()

    def pause_recording(self):
        if self.recording:
            self.paused = not self.paused
            if self.paused:
                self.pause_button.config(text="▶️")
                if self.timer_id:
                    self.master.after_cancel(self.timer_id)
                self.pause_start_time = datetime.now() 
            else:
                self.pause_button.config(text="⏸️")
                if self.pause_start_time:
                    self.elapsed_time_on_pause += (datetime.now() - self.pause_start_time)
                self.pause_start_time = None
                self.update_timer()

    def stop_recording(self):
        if not self.recording:
            return

        self.recording = False
        if self.timer_id:
            self.master.after_cancel(self.timer_id)
        self.timer_label.config(text="00:00:00")

        if self.record_thread and self.record_thread.is_alive():
            self.record_thread.join(timeout=5)
            if self.record_thread.is_alive():
                print("Предупреждение: Поток записи не завершился вовремя.")

        self.start_button.config(state=tk.NORMAL, bg=self.default_start_button_bg)
        self.pause_button.config(state=tk.DISABLED, text="⏸️")
        self.stop_button.config(state=tk.DISABLED)
        self.screenshot_button.config(state=tk.NORMAL) 
        
        print(f"Видео сохранено в: {os.path.abspath(self.output_filename)}")

    def take_screenshot(self):
        try:
            with mss.mss() as sct:
                if self.is_full_screen_mode.get():
                    monitor = sct.monitors[1]
                else:
                    monitor = {"top": self.record_y, "left": self.record_x,
                               "width": self.record_width, "height": self.record_height}
                
                sct_img = sct.grab(monitor)
                img = np.array(sct_img)
                img_rgb = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
                
                if not os.path.exists(self.output_folder):
                    os.makedirs(self.output_folder, exist_ok=True)
                
                now = datetime.now()
                timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
                
                screenshot_filename = os.path.join(self.output_folder, f"screenshot_{timestamp}.jpg")
                
                is_success, buffer = cv2.imencode(".jpg", img_rgb)
                if is_success:
                    with open(screenshot_filename, "wb") as f:
                        f.write(buffer)
                else:
                    raise Exception("Не удалось закодировать изображение для сохранения.")
                
                self.screenshot_button.config(text="✅") 
                self.master.after(1000, lambda: self.screenshot_button.config(text="📷")) 

                print(f"Скриншот сохранен в: {os.path.abspath(screenshot_filename)}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сделать скриншот: {e}")
            print(f"Ошибка скриншота: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenRecorder(root)
    root.mainloop()
