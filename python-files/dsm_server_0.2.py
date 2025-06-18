import tkinter as tk
from tkinter import filedialog, messagebox
from ttkthemes import ThemedTk
from tkinter import ttk
import threading
import socket
import rasterio
from rasterio.enums import ColorInterp
import numpy as np
from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from rio_tiler.io import Reader
from rio_tiler.utils import render
from rio_tiler.errors import TileOutsideBounds
import os
import uuid  # Импортируем для создания уникальных имен файлов

# --- Часть 1: Обработка DEM в RGB (без изменений) ---
# Эта функция уже готова к работе с одним файлом за раз, мы будем вызывать ее в цикле.

def process_dem_to_terrarium(input_path: str, output_path: str) -> str:
    """
    Конвертирует одноканальный DEM GeoTIFF в 3-канальный RGB GeoTIFF
    в соответствии с форматом кодирования высот Terrarium.
    """
    try:
        with rasterio.open(input_path) as src:
            if src.count != 1:
                # В GUI-контексте лучше показывать ошибку один раз
                raise ValueError("Для конвертации высот в RGB необходим одноканальный GeoTIFF.\n"
                                 "Если ваши файлы уже в формате RGB, снимите галочку.")

            dem = src.read(1).astype(np.float32)
            profile = src.profile
            nodata = src.nodata
            if nodata is not None:
                dem[dem == nodata] = -10000

            value = dem + 32768
            value = np.clip(value, 0, 65535)

            r = (value / 256).astype(np.uint8)
            g = (value % 256).astype(np.uint8)
            b = np.round((value - np.floor(value)) * 256).astype(np.uint8)

            profile.update(
                count=3,
                dtype=np.uint8,
                nodata=None,
                photometric='RGB',
                interleave='pixel'
            )

            with rasterio.open(output_path, 'w', **profile) as dst:
                dst.colorinterp = [ColorInterp.red, ColorInterp.green, ColorInterp.blue]
                dst.write(r, 1)
                dst.write(g, 2)
                dst.write(b, 3)
        
        return output_path
    
    except Exception as e:
        # Передаем ошибку наверх, чтобы обработать ее в GUI
        raise e


# --- Часть 2: Веб-сервер для раздачи тайлов ---
# ИЗМЕНЕНИЕ: Функция теперь принимает список путей к растрам

def create_fastapi_app(raster_paths: list[str], port: int) -> FastAPI:
    """
    Создает и конфигурирует экземпляр FastAPI для раздачи тайлов из НЕСКОЛЬКИХ источников.
    """
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get(f"/tiles{port}/{{z}}/{{x}}/{{y}}.png")
    def get_tile(z: int, x: int, y: int):
        # ИЗМЕНЕНИЕ: Логика композитинга тайлов из нескольких источников
        
        final_tile = None
        final_mask = None

        # Проходим по всем растрам в обратном порядке, чтобы первый в списке был "сверху"
        for raster_path in reversed(raster_paths):
            try:
                with Reader(raster_path) as image_reader:
                    # Пытаемся получить тайл из текущего файла
                    tile, mask = image_reader.tile(x, y, z, tilesize=256)
            except TileOutsideBounds:
                # Если тайла нет в этом файле, просто переходим к следующему
                continue
            except Exception as e:
                # Пропускаем "сломанные" файлы, но логируем ошибку
                print(f"Ошибка чтения тайла из {raster_path}: {e}")
                continue

            if final_tile is None:
                # Если это первый найденный тайл, он становится нашей основой
                final_tile = tile
                final_mask = mask
            else:
                # Если у нас уже есть тайл-основа, накладываем новый поверх него.
                # np.where работает как тернарный оператор для массивов.
                # Условие: где в маске нового тайла есть данные (mask > 0)?
                # Если да: берем пиксель из нового тайла (tile).
                # Если нет: оставляем пиксель из старого (final_tile).
                # np.newaxis нужен для согласования размерностей маски (H, W) и тайла (C, H, W).
                final_tile = np.where(mask[np.newaxis, ...], tile, final_tile)
                
                # Объединяем маски: пиксель видим, если он был виден хотя бы в одной маске
                final_mask = np.maximum(final_mask, mask)

        # После проверки всех файлов, рендерим результат
        if final_tile is not None:
            content = render(final_tile, final_mask, img_format="PNG")
            return Response(content=content, media_type="image/png")
        else:
            # Если тайл не найден ни в одном из файлов, возвращаем прозрачный тайл
            transparent = np.zeros((256, 256, 4), dtype=np.uint8)
            content = render(transparent, img_format="PNG")
            return Response(content=content, media_type="image/png")

    return app

# --- Часть 3: GUI на Tkinter и управление потоками ---

class TileServerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DSM.Server")
        self.root.geometry("300x280")
        icon = tk.PhotoImage(file="icon.png")
        self.root.iconphoto(True, icon)
        self.root.resizable(False, False)

        self.server_thread = None
        self.uvicorn_server = None
        # ИЗМЕНЕНИЕ: Теперь это список путей для очистки
        self.paths_to_cleanup = []

        self.label = ttk.Label(root, text="Выберите GeoTIFF-файлы для запуска сервера", justify="center")
        self.label.pack(pady=(20, 5))

        self.convert_var = tk.BooleanVar(value=True)
        self.convert_check = ttk.Checkbutton(
            root,
            text="  Конвертировать высоты в RGB",
            variable=self.convert_var
        )
        self.convert_check.pack(pady=5)

        button_frame = ttk.Frame(root)
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(button_frame, text="Выбрать и запустить", command=self.start_process)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.copy_button = ttk.Button(button_frame, text="Скопировать URL", command=self.copy_url)
        self.copy_button.pack(side=tk.LEFT, padx=5)

        self.status_label = ttk.Label(root, text="Статус: Ожидание", foreground="blue")
        self.status_label.pack(pady=5)

        self.url_label = ttk.Label(root, text="URL для вставки в DSM.Gallery:")
        self.url_label.pack()

        self.url_entry = ttk.Entry(root, width=43, justify='center')
        self.url_entry.pack(pady=5, padx=20, ipady=4)

        self.stop_button = ttk.Button(
            root, width=41, text="Остановить сервер и выйти", command=self.stop_and_exit, state=tk.DISABLED
        )
        self.stop_button.pack(pady=(10, 20))

        self.root.protocol("WM_DELETE_WINDOW", self.stop_and_exit)

    def find_free_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]

    def copy_url(self):
        url = self.url_entry.get()
        if url:
            self.root.clipboard_clear()
            self.root.clipboard_append(url)
            self.root.update()
            messagebox.showinfo("Скопировано", "URL успешно скопирован в буфер обмена.")
        else:
            messagebox.showwarning("Пустой URL", "Нет данных для копирования.")

    def start_process(self):
        # ИЗМЕНЕНИЕ: Используем askopenfilenames для выбора нескольких файлов
        file_paths = filedialog.askopenfilenames(
            title="Выберите входные GeoTIFF файлы",
            filetypes=[("GeoTIFF files", "*.tif *.tiff")]
        )
        if not file_paths:
            self.status_label.config(text="Статус: Выбор файлов отменен", foreground="#FFA500")
            return

        # ИЗМЕНЕНИЕ: Логика обработки списка файлов
        paths_to_serve = []
        self.paths_to_cleanup = [] # Очищаем список перед новым запуском

        if self.convert_var.get():
            try:
                for i, file_path in enumerate(file_paths):
                    status_text = f"Статус: Конвертация файла {i+1}/{len(file_paths)}..."
                    self.status_label.config(text=status_text, foreground="#800080")
                    self.root.update_idletasks()
                    
                    # Генерируем уникальное имя для каждого конвертированного файла
                    output_path = f"terrarium_output_{uuid.uuid4()}.tif"
                    processed_path = process_dem_to_terrarium(file_path, output_path)
                    
                    paths_to_serve.append(processed_path)
                    self.paths_to_cleanup.append(processed_path)
                
                self.status_label.config(text="Статус: Конвертация завершена. Запуск...", foreground="#800080")

            except Exception as e:
                messagebox.showerror("Ошибка конвертации", f"Не удалось обработать файл:\n{e}")
                self.status_label.config(text="Статус: Ошибка обработки", foreground="red")
                # Очищаем созданные файлы, если произошла ошибка на полпути
                self.cleanup_files()
                return
        else:
            self.status_label.config(text="Статус: Пропускаем конвертацию. Запуск...", foreground="#800080")
            paths_to_serve = list(file_paths) # Просто используем исходные файлы
            self.paths_to_cleanup = [] # Ничего не создавали - нечего чистить

        self.root.update_idletasks()
        self.start_server(paths_to_serve)

    # ИЗМЕНЕНИЕ: start_server теперь принимает список путей
    def start_server(self, raster_paths: list[str]):
        try:
            port = self.find_free_port()
            app = create_fastapi_app(raster_paths, port)
            config = uvicorn.Config(app, host="localhost", port=port, log_level="info")
            self.uvicorn_server = uvicorn.Server(config)
            self.server_thread = threading.Thread(target=self.uvicorn_server.run)
            self.server_thread.daemon = True
            self.server_thread.start()
            url = f"http://localhost:{port}/tiles{port}/{{z}}/{{x}}/{{y}}.png"
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, url)
            self.status_label.config(text=f"Статус: Сервер запущен на порту {port}", foreground="green")
            self.start_button.config(state=tk.DISABLED)
            self.convert_check.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Ошибка запуска сервера", f"Не удалось запустить веб-сервер:\n{e}")
            self.status_label.config(text="Статус: Ошибка сервера", foreground="red")

    def cleanup_files(self):
        # ИЗМЕНЕНИЕ: Функция для очистки списка временных файлов
        if self.paths_to_cleanup:
            print("Начинается очистка временных файлов...")
            for path in self.paths_to_cleanup:
                if os.path.exists(path):
                    try:
                        os.remove(path)
                        print(f"Временный файл {path} успешно удален.")
                    except Exception as e:
                        print(f"Не удалось удалить временный файл {path}: {e}")
            self.paths_to_cleanup = []

    def stop_and_exit(self):
        if self.uvicorn_server:
            self.uvicorn_server.should_exit = True
        if self.server_thread:
            self.server_thread.join(timeout=1.0)
        
        # ИЗМЕНЕНИЕ: Вызов новой функции очистки
        self.cleanup_files()
        
        self.root.destroy()


if __name__ == "__main__":
    main_root = ThemedTk(theme="yaru") 
    app = TileServerApp(main_root)
    main_root.mainloop()