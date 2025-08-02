import os
import time
import subprocess
import signal
import tkinter as tk
from tkinter import ttk


class GStreamerConfigApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GStreamer Configurator")

        # Параметры по умолчанию
        self.defaults = {
            'stream_url': 'rtsp://192.168.1.119:554',
            'latency': '50',
            'width': '640',
            'height': '360',
            'bitrate': '100',
            'speed_preset': 'slow',
            'host': '192.168.1.114',
            'port': '8554'
        }

        self.create_widgets()

    def create_widgets(self):
        # Создаем фрейм для полей ввода
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Поля ввода
        ttk.Label(main_frame, text="RTSP Stream URL:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.stream_url = ttk.Entry(main_frame, width=40)
        self.stream_url.grid(row=0, column=1, pady=2)
        self.stream_url.insert(0, self.defaults['stream_url'])

        ttk.Label(main_frame, text="Latency:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.latency = ttk.Entry(main_frame, width=10)
        self.latency.grid(row=1, column=1, sticky=tk.W, pady=2)
        self.latency.insert(0, self.defaults['latency'])

        ttk.Label(main_frame, text="Width:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.width = ttk.Entry(main_frame, width=10)
        self.width.grid(row=2, column=1, sticky=tk.W, pady=2)
        self.width.insert(0, self.defaults['width'])

        ttk.Label(main_frame, text="Height:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.height = ttk.Entry(main_frame, width=10)
        self.height.grid(row=3, column=1, sticky=tk.W, pady=2)
        self.height.insert(0, self.defaults['height'])

        ttk.Label(main_frame, text="Bitrate:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.bitrate = ttk.Entry(main_frame, width=10)
        self.bitrate.grid(row=4, column=1, sticky=tk.W, pady=2)
        self.bitrate.insert(0, self.defaults['bitrate'])

        ttk.Label(main_frame, text="Speed Preset:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.speed_preset = ttk.Combobox(main_frame,
                                         values=['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium',
                                                 'slow', 'slower', 'veryslow', 'placebo'], width=10)
        self.speed_preset.grid(row=5, column=1, sticky=tk.W, pady=2)
        self.speed_preset.set(self.defaults['speed_preset'])

        ttk.Label(main_frame, text="Host:").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.host = ttk.Entry(main_frame, width=15)
        self.host.grid(row=6, column=1, sticky=tk.W, pady=2)
        self.host.insert(0, self.defaults['host'])

        ttk.Label(main_frame, text="Port:").grid(row=7, column=0, sticky=tk.W, pady=2)
        self.port = ttk.Entry(main_frame, width=10)
        self.port.grid(row=7, column=1, sticky=tk.W, pady=2)
        self.port.insert(0, self.defaults['port'])

        # Кнопки
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.grid(row=1, column=0, sticky=tk.E)

        ttk.Button(button_frame, text="Start", command=self.start_stream).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Exit", command=self.root.destroy).grid(row=0, column=1, padx=5)

    def start_stream(self):
        # Получаем параметры из GUI
        params = {
            'stream_url': self.stream_url.get(),
            'latency': self.latency.get(),
            'width': self.width.get(),
            'height': self.height.get(),
            'bitrate': self.bitrate.get(),
            'speed_preset': self.speed_preset.get(),
            'host': self.host.get(),
            'port': self.port.get()
        }

        # Закрываем окно конфигурации
        self.root.destroy()

        # Запускаем основной цикл с полученными параметрами
        run_main_loop(params)


def run_gstreamer(params, gstreamer_path):
    """Запускает GStreamer с указанными параметрами"""
    command = (
        f"gst-launch-1.0.exe rtspsrc location={params['stream_url']} latency={params['latency']} "
        f"! rtph265depay ! avdec_h265 ! videoconvert ! videoscale "
        f"! video/x-raw,width={params['width']},height={params['height']} "
        f"! x265enc bitrate={params['bitrate']} speed-preset={params['speed_preset']} "
        f"tune=zerolatency key-int-max=10 ! h265parse ! mpegtsmux ! "
        f"rtpmp2tpay ! udpsink host={params['host']} port={params['port']} sync=false"
    )

    full_cmd = f'cd {gstreamer_path} && {command}'

    return subprocess.Popen(
        ["cmd.exe", "/c", full_cmd],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )


def kill_gstreamer(process):
    """Завершает процесс GStreamer"""
    try:
        # Сначала пробуем "мягко" завершить (Ctrl+C)
        os.kill(process.pid, signal.CTRL_C_EVENT)
        time.sleep(0.3)  # Короткая пауза на обработку

        # Если не сработало - принудительно
        if process.poll() is None:
            os.system('taskkill /f /im gst-launch-1.0.exe >nul 2>&1')
    except:
        os.system('taskkill /f /im gst-launch-1.0.exe >nul 2>&1')


def run_main_loop(params):
    """Основной цикл работы GStreamer"""
    GSTREAMER_PATH = r"C:\gstreamer\1.0\msvc_x86_64\bin"

    try:
        while True:
            print("Запуск GStreamer...")
            print(f"Параметры: {params}")
            proc = run_gstreamer(params, GSTREAMER_PATH)

            # Ждём 15 секунд
            time.sleep(15)

            print("Остановка GStreamer...")
            kill_gstreamer(proc)

            # Минимальная пауза перед перезапуском (~0.1 сек)
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nОстановка скрипта...")
        os.system('taskkill /f /im gst-launch-1.0.exe >nul 2>&1')


if __name__ == "__main__":
    root = tk.Tk()
    app = GStreamerConfigApp(root)
    root.mainloop()