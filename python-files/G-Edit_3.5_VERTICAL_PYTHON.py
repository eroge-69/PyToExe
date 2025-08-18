import sys
import os
import shutil
from pathlib import Path
import glob

# Импорты из PySide6 для создания GUI
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QHBoxLayout,
    QTreeView, QFileSystemModel, QSplitter, QAbstractItemView, QHeaderView, QFileDialog
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineDownloadRequest
from PySide6.QtCore import Qt, QTimer, QUrl, QSortFilterProxyModel, QModelIndex, QMimeData
from PySide6.QtGui import QDrag

# Импорт для взаимодействия с окнами Windows
import pygetwindow as gw

# --- КОНФИГУРАЦИЯ ---
    """
TARGET_WINDOW_TITLE = "CNC Monitor v10.118.50V"
    """
TARGET_WINDOW_TITLE = "CNC Monitor v10.118.82U"
HTML_FILE_PATH = "C:\\G-Edit 3.0_cleaned.html"
CHECK_INTERVAL_MS = 500

APP_STYLESHEET = """
    /* Общий стиль для виджетов внутри FileExplorer */
    FileExplorer, FileExplorer QHeaderView::section {
        background-color: #1b3666; /* Темно-синий фон, как у панелей */
        color: #e0e0e0; /* Светлый цвет текста */
        border: 1px solid rgba(255, 255, 255, 0.1); /* Тонкая светлая рамка */
        font-family: 'Inter', sans-serif; /* Шрифт как в HTML (если установлен в системе) */
        font-size: 12px;
    }

    /* Стиль для всего виджета QTreeView (проводника) */
    QTreeView {
        outline: 0; /* Убираем рамку фокуса */
    }

    /* Стиль для элементов списка (файлов и папок) */
    QTreeView::item {
        padding: 3px;
        border-radius: 2px;
    }

    /* Стиль для выделенного элемента */
    QTreeView::item:selected {
        background-color: #667eea; /* Фиолетово-синий цвет выделения, как в HTML */
        color: white;
    }

    /* Стиль для элемента при наведении курсора */
    QTreeView::item:hover {
        background-color: rgba(255, 255, 255, 0.1);
    }

    /* Стиль для заголовка таблицы (Имя, Размер, Дата) */
    QHeaderView::section {
        padding: 5px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        font-weight: bold;
    }

    /* Стиль для разделителей между окнами (сплиттеров) */
    QSplitter::handle {
        background-color: #1a2a47; /* Фон в цвет панелей */
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    QSplitter::handle:hover {
        background-color: #667eea; /* Подсветка при наведении */
    }
    QSplitter::handle:pressed {
        background-color: #764ba2;
    }

    /* Стиль для полос прокрутки */
    QScrollBar:vertical, QScrollBar:horizontal {
        border: none;
        background: #1a2a47;
        width: 10px;
        margin: 0px 0px 0px 0px;
    }
    QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
        background: #667eea;
        min-height: 20px;
        border-radius: 5px;
    }
    QScrollBar::add-line, QScrollBar::sub-line {
        height: 0px;
        width: 0px;
    }
"""

class OverlayButton(QWidget):
    """
    Класс для создания прозрачной кнопки, которая будет отображаться поверх целевого окна.
    """

    def __init__(self, main_window_instance):
        super().__init__()
        self.main_window = main_window_instance
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.button = QPushButton("G-Edit", self)
        self.button.setFixedSize(120, 60)
        self.button.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 128);
                color: white;
                font-size: 16px;
                font-weight: bold;
                border: 1px solid rgba(255, 255, 255, 100);
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 180);
            }
            QPushButton:pressed {
                background-color: rgba(20, 20, 20, 200);
            }
        """)
        self.button.clicked.connect(self.show_main_window)
        self.setFixedSize(self.button.size())



    def show_main_window(self):
        self.main_window.reset_and_show()

    def update_position(self, target_window):
        if target_window:
            x_pos = target_window.left + target_window.width - self.width() 
            y_pos = target_window.top + target_window.height - 415
            self.move(x_pos, y_pos)


class AncFilterProxyModel(QSortFilterProxyModel):
    """
    Прокси-модель для фильтрации файлов.
    """

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        source_index = self.sourceModel().index(source_row, 0, source_parent)
        if not source_index.isValid():
            return False

        if self.sourceModel().isDir(source_index):
            return True

        file_info = self.sourceModel().fileInfo(source_index)
        if file_info.fileName().lower().endswith('.anc'):
            return True

        return False


# Новый класс для форматирования размера файла
class FileSizeProxyModel(AncFilterProxyModel):
    """
    Прокси-модель, которая наследует фильтрацию от AncFilterProxyModel
    и дополнительно форматирует столбец с размером файла.
    """

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        # Нас интересует только столбец с размером (индекс 1) и роль отображения
        if index.column() == 1 and role == Qt.ItemDataRole.DisplayRole:
            # Получаем оригинальный размер в байтах из исходной модели
            source_index = self.mapToSource(index)
            size_in_bytes = self.sourceModel().size(source_index)

            # Если это папка, у нее нет размера, возвращаем пустую строку
            if self.sourceModel().isDir(source_index):
                return ""

            # Конвертируем байты в килобайты
            if size_in_bytes < 1024:
                return "1 KB"  # Отображаем как минимум 1 КБ для очень маленьких файлов

            size_in_kb = size_in_bytes / 1024
            # Форматируем строку с одним знаком после запятой и добавляем "KB"
            return f"{size_in_kb:.1f} KB"

        # Для всех остальных случаев возвращаем данные без изменений
        return super().data(index, role)

class FileExplorer(QTreeView):
    """
    Виджет для отображения файловой системы с полностью кастомной реализацией Drag & Drop.
    """

    def __init__(self, root_path: str):
        super().__init__()
        self.drag_start_position = None

        self.source_model = QFileSystemModel()
        self.source_model.setRootPath(root_path)
        self.source_model.setNameFilters(["*.anc"])
        self.source_model.setNameFilterDisables(False)

        self.proxy_model = FileSizeProxyModel()
        self.proxy_model.setSourceModel(self.source_model)

        self.setModel(self.proxy_model)

        source_root_index = self.source_model.index(root_path)
        proxy_root_index = self.proxy_model.mapFromSource(source_root_index)
        self.setRootIndex(proxy_root_index)

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        self.hideColumn(2)
        # Устанавливаем режим ИНТЕРАКТИВНОГО изменения размера для нужных столбцов.
        # Теперь пользователь сможет сам менять их ширину мышкой.
        # Индекс 0: Имя файла
        # Индекс 1: Размер
        # Индекс 3: Дата изменения
        self.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.header().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)

        # Задаем удобную начальную ширину для столбцов, чтобы они выглядели хорошо при запуске
        self.setColumnWidth(0, 250)  # Начальная ширина для столбца "Имя"
        self.setColumnWidth(1, 100)  # Начальная ширина для столбца "Размер"
        self.setColumnWidth(3, 150)  # Начальная ширина для столбца "Дата изменения"

        self.setSortingEnabled(True)
        self.sortByColumn(3, Qt.SortOrder.DescendingOrder)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if self.drag_start_position is None:
            return
        if (event.position().toPoint() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        mime_data = QMimeData()
        urls = []
        for index in self.selectionModel().selectedRows():
            if index.column() == 0:
                source_index = self.proxy_model.mapToSource(index)
                file_path = self.source_model.filePath(source_index)
                if os.path.isfile(file_path):
                    urls.append(QUrl.fromLocalFile(file_path))

        if not urls:
            return

        mime_data.setUrls(urls)
        drag.setMimeData(mime_data)
        drag.exec(Qt.DropAction.CopyAction)
        self.drag_start_position = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if not event.mimeData().hasUrls():
            super().dropEvent(event)
            return

        drop_index = self.indexAt(event.position().toPoint())
        source_drop_index = self.proxy_model.mapToSource(drop_index)

        if source_drop_index.isValid():
            dest_path = self.source_model.filePath(source_drop_index)
            if not self.source_model.isDir(source_drop_index):
                dest_path = os.path.dirname(dest_path)
        else:
            dest_path = self.source_model.filePath(self.proxy_model.mapToSource(self.rootIndex()))

        for url in event.mimeData().urls():
            source_path = url.toLocalFile()
            if os.path.isfile(source_path):
                try:
                    shutil.copy2(source_path, dest_path)
                    print(f"Скопирован файл: {source_path} -> {dest_path}")
                except Exception as e:
                    print(f"Ошибка копирования файла: {e}")

        event.acceptProposedAction()

    def set_root_path(self, path):
        source_root_index = self.source_model.index(path)
        proxy_root_index = self.proxy_model.mapFromSource(source_root_index)
        self.setRootIndex(proxy_root_index)


class MainVisualizerWindow(QMainWindow):
    """
    Основное окно приложения с новой компоновкой (проводники справа).
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("G-Code Visualizer")
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint)
        self.setStyleSheet(APP_STYLESHEET)
        self.init_ui()

    def init_ui(self):
        # Создаем виджеты, как и раньше
        downloads_path = str(Path.home() / "Downloads")
        explorer_downloads = FileExplorer(downloads_path)
        explorer_disk_c = FileExplorer("F:\\")

        self.web_view = QWebEngineView()
        self.web_view.page().setBackgroundColor(Qt.GlobalColor.transparent)
        QWebEngineProfile.defaultProfile().setHttpCacheType(QWebEngineProfile.HttpCacheType.NoCache)

        # --- НОВАЯ ВЕРТИКАЛЬНАЯ КОМПОНОВКА ---

        # 1. Создаем ГОРИЗОНТАЛЬНЫЙ сплиттер для верхних проводников
        top_explorers_splitter = QSplitter(Qt.Orientation.Horizontal)
        top_explorers_splitter.addWidget(explorer_downloads)
        top_explorers_splitter.addWidget(explorer_disk_c)
        # Устанавливаем равные начальные размеры для проводников
        top_explorers_splitter.setSizes([100, 100])

        # 2. Создаем основной ВЕРТИКАЛЬНЫЙ сплиттер для всего окна
        main_splitter = QSplitter(Qt.Orientation.Vertical)

        # 3. Добавляем панель с проводниками наверх, а веб-просмотрщик вниз
        main_splitter.addWidget(top_explorers_splitter)
        main_splitter.addWidget(self.web_view)

        # 4. Устанавливаем пропорции: 1/5 для проводников, 4/5 для визуализатора
        main_splitter.setSizes([100, 400])

        # Подключаем обработчик скачивания
        profile = self.web_view.page().profile()
        profile.downloadRequested.connect(self.handle_download_request)
        
        self.setCentralWidget(main_splitter)

        # Сохраняем ссылки на проводники для метода reset_and_show
        self.explorer_downloads = explorer_downloads
        self.explorer_disk_c = explorer_disk_c
        
    # Вспомогательный метод для создания уникального имени файла
    def _get_unique_filename(self, path):
        """Проверяет, существует ли файл, и добавляет (n) к имени, если нужно."""
        if not os.path.exists(path):
            return path

        base, ext = os.path.splitext(path)
        counter = 1
        while True:
            new_path = f"{base}({counter}){ext}"
            if not os.path.exists(new_path):
                return new_path
            counter += 1

    # Новый, автоматический метод для обработки запросов на скачивание
    def handle_download_request(self, download_item: QWebEngineDownloadRequest):
        """
        Этап 1: Перехватывает запрос, подписывается на сигнал ИЗМЕНЕНИЯ СОСТОЯНИЯ
        и разрешает скачивание во временный файл.
        """
        # Подключаем наш обработчик к правильному сигналу 'stateChanged'.
        # Используем lambda, чтобы передать и сам объект download_item, и его новое состояние.
        download_item.stateChanged.connect(
            lambda state: self.on_download_state_changed(download_item, state)
        )

        # Разрешаем движку начать скачивание во временное место
        download_item.accept()

    def on_download_state_changed(self, download_item: QWebEngineDownloadRequest,
                                  state: QWebEngineDownloadRequest.DownloadState):
        """
        Этап 2: Срабатывает при каждом изменении состояния скачивания.
        Если состояние - 'DownloadCompleted', перемещает файл.
        """
        # Нас интересует только финальное состояние успешного завершения
        if state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
            # 1. Получаем путь к временному файлу, куда всё скачалось
            temp_path = download_item.path()

            # 2. Получаем ПРАВИЛЬНОЕ имя файла
            final_filename = download_item.downloadFileName()

            # 3. Формируем конечный путь в папке "Загрузки"
            downloads_path = str(Path.home() / "Downloads")
            destination_path = os.path.join(downloads_path, final_filename)

            # 4. Проверяем уникальность имени файла
            unique_destination_path = self._get_unique_filename(destination_path)

            # 5. Перемещаем временный файл
            try:
                # Проверяем, что временный файл существует, прежде чем перемещать
                if os.path.exists(temp_path):
                    shutil.move(temp_path, unique_destination_path)
                    print(f"Файл успешно сохранен: {unique_destination_path}")
                else:
                    print(f"Ошибка: временный файл не найден по пути {temp_path}")
            except Exception as e:
                print(f"Ошибка при перемещении файла: {e}")

        elif state == QWebEngineDownloadRequest.DownloadState.DownloadCancelled:
            print("Скачивание отменено.")
        elif state == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted:
            print(f"Скачивание прервано: {download_item.interruptReasonString()}")

    def load_html(self):

        search_directory = "C:\\"
        html_files = glob.glob(os.path.join(search_directory, "G-Edit*.html"))

        if html_files:

            html_files.sort()
            found_html_file_path = html_files[0]

            html_file_url = QUrl.fromLocalFile(found_html_file_path)
            self.web_view.load(html_file_url)
            print(f"Загружен файл: {found_html_file_path}") # Для отладки
        else:
            error_html = f"<h1>Ошибка</h1><p>Файл G-Edit*.html не найден в директории: {os.path.abspath(search_directory)}</p>"
            self.web_view.setHtml(error_html)
            print(f"Ошибка: {error_html}") # Для отладки

    def reset_and_show(self):
        self.load_html()

        # Сбрасываем проводники к корневым папкам
        self.explorer_downloads.set_root_path(str(Path.home() / "Downloads"))
        self.explorer_disk_c.set_root_path("F:\\")

        self.showMaximized()
        self.activateWindow()

    def closeEvent(self, event):
        self.hide()
        event.ignore()


def main_loop():
    """
    Основной цикл, который выполняется по таймеру.
    """
    try:
        target_windows = gw.getWindowsWithTitle(TARGET_WINDOW_TITLE)

        if target_windows:
            target_window = target_windows[0]
            active_window = gw.getActiveWindow()

            if active_window and active_window.title == TARGET_WINDOW_TITLE:
                overlay_button.update_position(target_window)
                if not overlay_button.isVisible():
                    overlay_button.show()
            else:
                if overlay_button.isVisible():
                    overlay_button.hide()
        else:
            if overlay_button.isVisible():
                overlay_button.hide()
    except Exception:
        if overlay_button.isVisible():
            overlay_button.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainVisualizerWindow()
    overlay_button = OverlayButton(main_window)

    timer = QTimer()
    timer.timeout.connect(main_loop)
    timer.start(CHECK_INTERVAL_MS)

    print(f"Ожидание окна с заголовком: '{TARGET_WINDOW_TITLE}'...")
    print(f"Кнопка появится справа, на высоте 450px от низа активного окна.")

    sys.exit(app.exec())