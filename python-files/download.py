import sys
import re
import json
import os
import zipfile
import shutil
import requests
import time
from pathlib import Path

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QPushButton, QTextEdit, QSpinBox, QCheckBox, QLabel, QFileDialog, QLineEdit
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

class MangaDownloader(QThread):
    log = pyqtSignal(str)
    finished = pyqtSignal(bool)
    download_started = pyqtSignal()

    def __init__(self, download_all, start_chapter, end_chapter, download_path):
        super().__init__()
        self.url = None
        self.cookies = None
        
        self.download_all = download_all
        self.start_chapter = start_chapter
        self.end_chapter = end_chapter
        self.download_path = Path(download_path) # <<< НОВОЕ: Путь для сохранения

        self.cookie_file = Path("comx_life_cookies_v2.json")
        self.log_file = Path("download_log.json")
        self.headers = {
            "Referer": "https://comx.life/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        self._is_cancelled = False

    def run(self):
        self.cleanup(initial=True)
        try:
            self.log.emit("🌐 Открытие браузера...")
            # Создаем папку для сохранения, если её нет
            self.download_path.mkdir(parents=True, exist_ok=True)
            
            driver = self._open_browser_with_cookies()
            if driver:
                self.log.emit("🔎 Запуск отслеживания страницы манги...")
                self._auto_download_if_manga_page(driver)
        except Exception as e:
            self.log.emit(f"❌ Критическая ошибка в потоке: {e}")
            self.finished.emit(False)

    def cancel(self):
        self._is_cancelled = True

    def cleanup(self, initial=False):
        temp_dirs = ["downloads", "combined_cbz_temp"]
        for dir_name in temp_dirs:
            dir_path = Path(dir_name)
            if dir_path.exists():
                shutil.rmtree(dir_path)
                if not initial:
                    self.log.emit(f"🧹 Очищено: {dir_name}")

    def _load_log(self):
        if not self.log_file.exists(): return {}
        try:
            with open(self.log_file, "r", encoding="utf-8") as f: return json.load(f)
        except (json.JSONDecodeError, IOError): return {}

    def _save_log_entry(self, manga_title, chapter_id):
        log_data = self._load_log()
        log_data.setdefault(manga_title, []).append(chapter_id)
        try:
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
        except IOError as e: self.log.emit(f"⚠️ Не удалось сохранить лог: {e}")

    def _open_browser_with_cookies(self):
        try:
            options = Options()
            options.add_experimental_option("detach", True)
            driver = webdriver.Chrome(options=options)
            driver.get("https://comx.life/")

            if self.cookie_file.exists():
                self.log.emit("🍪 Пробую восстановить сессию...")
                with open(self.cookie_file, "r", encoding="utf-8") as f: cookies = json.load(f)
                driver.delete_all_cookies()
                for c in cookies:
                    c.pop("sameSite", None)
                    try: driver.add_cookie(c)
                    except Exception: pass
                driver.refresh()
                time.sleep(2)
                if driver.get_cookie("dle_user_id"):
                    self.cookies = driver.get_cookies()
                    self.log.emit("✅ Авторизация восстановлена!")
                    return driver
                self.log.emit("⚠️ Сессия устарела, нужна новая авторизация")

            self.log.emit("🔐 Войдите вручную, я запомню cookies")
            self.log.emit("📦 Ожидание страницы манги...")
            while not driver.get_cookie("dle_user_id"):
                if self._is_cancelled:
                    driver.quit()
                    return None
                time.sleep(1)
            self.cookies = driver.get_cookies()
            with open(self.cookie_file, "w", encoding="utf-8") as f:
                json.dump(self.cookies, f, indent=2, ensure_ascii=False)
            return driver
        except Exception as e:
            self.log.emit(f"❌ Ошибка при запуске браузера: {e}")
            return None

    def _auto_download_if_manga_page(self, driver):
        processed_url = None
        while not self._is_cancelled:
            try:
                current_url = driver.current_url
                if current_url and current_url.endswith('/download'):
                    self.url = current_url.replace('/download', '')
                    self.log.emit(f"📍 Начинаем скачивание манги: {self.url}")
                    driver.quit()
                    self.download_manga()
                    return
                elif current_url and ".html" in current_url and current_url != processed_url:
                    self.log.emit(f"🔍 Проверка страницы: {current_url}")
                    try:
                        btn = driver.find_element(By.CSS_SELECTOR, 'a.page__btn-track.js-follow-status')
                        driver.execute_script('''
                            arguments[0].textContent = '⬇️ Скачать';
                            arguments[0].style.backgroundColor = '#28a745';
                            arguments[0].style.color = '#fff';
                            arguments[0].style.fontWeight = 'bold';
                            arguments[0].onclick = () => { window.location.href += '/download'; };
                        ''', btn)
                        self.log.emit("✅ Кнопка заменена на 'Скачать'")
                        processed_url = current_url
                    except Exception: pass
                time.sleep(0.1)
            except Exception as e:
                self.log.emit(f"❌ Ошибка в цикле отслеживания, браузер закрыт: {e}")
                try: driver.quit()
                except: pass
                self.finished.emit(False)
                return

    def download_manga(self):
        self.download_started.emit()
        self.log.emit(f"📥 Скачивание HTML: {self.url}")
        resp = requests.get(self.url, headers=self.headers, cookies={c['name']: c['value'] for c in self.cookies})
        match = re.search(r'window\.__DATA__\s*=\s*({.*?})\s*;', resp.text, re.DOTALL)
        if not match:
            self.log.emit("❌ Не найден window.__DATA__")
            self.finished.emit(False)
            return

        data = json.loads(match.group(1))
        all_chapters = data["chapters"][::-1]
        manga_title = data.get("title", "Manga").strip()
        manga_title_safe = re.sub(r"[^\w\- ]", "_", manga_title)
        self.log.emit(f"📖 Всего глав на странице: {len(all_chapters)}. Идет фильтрация...")
        
        download_log = self._load_log()
        downloaded_ids = download_log.get(manga_title, [])
        chapters_to_process = []
        for i, chapter in enumerate(all_chapters, 1):
            if self.download_all or (self.start_chapter <= i <= self.end_chapter):
                if chapter['id'] not in downloaded_ids:
                    chapters_to_process.append((i, chapter))
                else:
                    self.log.emit(f"⏭️ Пропуск главы {i} ({chapter['title']}), уже скачана.")
        
        if not chapters_to_process:
            self.log.emit("✅ Все главы в указанном диапазоне уже скачаны. Завершение.")
            self.finished.emit(True)
            return

        range_text = "все главы" if self.download_all else f"главы с {self.start_chapter} по {self.end_chapter}"
        self.log.emit(f"✅ Готово к скачиванию: {len(chapters_to_process)} глав ({range_text}).")

        chapter_range_str = f" (Главы {self.start_chapter}-{self.end_chapter})" if not self.download_all else ""
        final_cbz_name = f"{manga_title_safe}{chapter_range_str}.cbz"
        
        # <<< НОВОЕ: Файл сохраняется в выбранную папку
        final_cbz = self.download_path / final_cbz_name
        
        downloads_dir = Path("downloads")
        downloads_dir.mkdir(exist_ok=True)
        combined_dir = Path("combined_cbz_temp")
        combined_dir.mkdir(exist_ok=True)
        
        for idx, (original_index, chapter) in enumerate(chapters_to_process, 1):
            if self._is_cancelled:
                self.log.emit("❌ Скачивание отменено")
                self.cleanup()
                self.finished.emit(False)
                return
            
            # ... (код скачивания главы) ...
            title = chapter["title"]; chapter_id = chapter["id"]; news_id = data["news_id"]
            zip_path = downloads_dir / (re.sub(r"[^\w\- ]", "_", f"{original_index:06}_{title}") + ".zip")
            self.log.emit(f"⬇️ {idx}/{len(chapters_to_process)} (Глава {original_index}): {title}")
            try:
                payload = f"chapter_id={chapter_id}&news_id={news_id}"
                headers = { "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "Referer": self.url, "X-Requested-With": "XMLHttpRequest", "Origin": "https://comx.life", "User-Agent": self.headers["User-Agent"] }
                cookies = {c["name"]: c["value"] for c in self.cookies}
                link_resp = requests.post("https://comx.life/engine/ajax/controller.php?mod=api&action=chapters/download", headers=headers, data=payload, cookies=cookies)
                link_resp.raise_for_status()
                json_data = link_resp.json()
                raw_url = json_data.get("data")
                if not raw_url: raise ValueError("Поле 'data' не найдено")
                download_url = "https:" + raw_url.replace("\\/", "/")
                r = requests.get(download_url, headers=self.headers, cookies=cookies)
                r.raise_for_status()
                with open(zip_path, "wb") as f: f.write(r.content)
                self._save_log_entry(manga_title, chapter_id)
            except Exception as e: self.log.emit(f"❌ Ошибка при обработке главы {title}: {e}")

        if self._is_cancelled:
            self.cleanup()
            return
        
        index = 1
        self.log.emit("📦 Архивация в CBZ...")
        with zipfile.ZipFile(final_cbz, "w", compression=zipfile.ZIP_DEFLATED) as cbz:
            for zip_file in sorted(downloads_dir.glob("*.zip")):
                # ... (код архивации) ...
                if self._is_cancelled: break
                with zipfile.ZipFile(zip_file) as z:
                    for name in sorted(z.namelist()):
                        if self._is_cancelled: break
                        ext = os.path.splitext(name)[1].lower()
                        if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']: continue
                        out_name = f"{index:06}{ext}"
                        source_path = z.extract(name, path=combined_dir)
                        final_path = combined_dir / out_name
                        os.rename(source_path, final_path)
                        cbz.write(final_path, arcname=out_name)
                        index += 1

        self.cleanup()
        if self._is_cancelled:
            if final_cbz.exists():
                try: final_cbz.unlink()
                except Exception as e: self.log.emit(f"⚠️ Не удалось удалить архив: {e}")
            self.finished.emit(False)
            return

        self.log.emit(f"✅ Готово: {final_cbz.resolve()}")
        self.finished.emit(True)

class DownloaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manga Downloader for ComX")
        self.setGeometry(200, 200, 600, 500) # Увеличим высоту окна
        
        # --- НОВЫЙ ИНТЕРФЕЙС С ВЫБОРОМ ПАПКИ ---
        self.config_file = Path("config.json")
        main_layout = QVBoxLayout(self)
        
        # --- Блок выбора папки ---
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit(readOnly=True)
        self.browse_button = QPushButton("Обзор...")
        path_layout.addWidget(QLabel("Папка для сохранения:"))
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_button)
        
        # --- Блок выбора глав ---
        controls_layout = QFormLayout()
        self.all_chapters_checkbox = QCheckBox("Скачать все главы")
        self.all_chapters_checkbox.setChecked(True)
        
        range_layout = QHBoxLayout()
        self.start_chapter_input = QSpinBox(minimum=1, maximum=9999)
        self.end_chapter_input = QSpinBox(minimum=1, maximum=9999, value=100)
        range_layout.addWidget(QLabel("С главы:")); range_layout.addWidget(self.start_chapter_input)
        range_layout.addWidget(QLabel("по главу:")); range_layout.addWidget(self.end_chapter_input)
        
        controls_layout.addRow(self.all_chapters_checkbox)
        controls_layout.addRow(range_layout)
        
        self.button = QPushButton("Открыть сайт и начать отслеживание")
        self.cancel_button = QPushButton("Отмена", visible=False)
        self.logs = QTextEdit(readOnly=True, styleSheet="background-color: #f0f0f0;")
        
        main_layout.addLayout(path_layout)
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(self.button)
        main_layout.addWidget(self.cancel_button)
        main_layout.addWidget(self.logs)

        # --- Подключение сигналов ---
        self.browse_button.clicked.connect(self.select_download_path)
        self.all_chapters_checkbox.stateChanged.connect(self.toggle_range_inputs)
        self.button.clicked.connect(self.start_download)
        self.cancel_button.clicked.connect(self.cancel_download)

        self.load_config()
        self.toggle_range_inputs()

    def load_config(self):
        default_path = str(Path.cwd()) # По умолчанию - текущая папка
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    path = config.get("download_path", default_path)
                    self.path_input.setText(path)
            except (json.JSONDecodeError, IOError):
                self.path_input.setText(default_path)
        else:
            self.path_input.setText(default_path)
            self.save_config()

    def save_config(self):
        config_data = {"download_path": self.path_input.text()}
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)
        except IOError:
            self.logs.append("⚠️ Не удалось сохранить файл конфигурации.")

    def select_download_path(self):
        directory = QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения", self.path_input.text())
        if directory:
            self.path_input.setText(directory)
            self.save_config()

    def toggle_range_inputs(self):
        is_disabled = self.all_chapters_checkbox.isChecked()
        self.start_chapter_input.setDisabled(is_disabled)
        self.end_chapter_input.setDisabled(is_disabled)

    def download_started(self):
        self.button.hide()
        self.cancel_button.show()

    def start_download(self):
        download_path = self.path_input.text()
        if not download_path:
            self.logs.append("⚠️ Ошибка: Не выбрана папка для сохранения.")
            return

        download_all = self.all_chapters_checkbox.isChecked()
        start_chapter = self.start_chapter_input.value()
        end_chapter = self.end_chapter_input.value()
        if not download_all and start_chapter > end_chapter:
            self.logs.append("⚠️ Ошибка: Начальная глава не может быть больше конечной.")
            return

        self.button.setEnabled(False)
        self.logs.clear()
        self.logs.append("▶️ Запуск...")
        
        self.worker = MangaDownloader(
            download_all=download_all,
            start_chapter=start_chapter,
            end_chapter=end_chapter,
            download_path=download_path
        )
        self.worker.download_started.connect(self.download_started)
        self.worker.log.connect(self.logs.append)
        self.worker.finished.connect(self.download_finished)
        self.worker.start()

    def cancel_download(self):
        if hasattr(self, 'worker'):
            self.worker.cancel()
            self.logs.append("🛑 Отмена...")

    def download_finished(self, ok):
        self.button.setEnabled(True)
        self.button.show()
        self.cancel_button.hide()
        if hasattr(self, 'worker') and self.worker._is_cancelled:
            self.logs.append("✋ Скачивание было отменено пользователем.")
        elif ok:
            self.logs.append("\n✅ Скачивание завершено успешно!")
        else:
            self.logs.append("\n❌ Скачивание завершено с ошибкой.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = DownloaderApp()
    win.show()
    sys.exit(app.exec_())