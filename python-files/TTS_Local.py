import os
import sys

# [终极修复] 解决顽固的 OpenMP DLL 冲突问题
# 必须在任何其他导入 (尤其是 torch) 之前设置此环境变量。
# KMP_DUPLICATE_LIB_OK=TRUE 告诉 Intel OpenMP 运行时库，允许加载多个 OpenMP 库的副本，
# 从而避免因冲突而导致的 WinError 1114 初始化失败。
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'


# [核心修复] PyInstaller + PyTorch DLL 冲突修复 (继续保留)
# 之前的预加载步骤仍然是一个好的实践，我们将其保留。
try:
    import torch
    import torch.multiprocessing
    if sys.platform == 'win32':
        torch.multiprocessing.set_start_method('spawn', force=True)
    
    _ = torch.tensor([1, 2, 3]).to('cpu') 
    print("PyTorch pre-initialization successful.")

except (ImportError, RuntimeError) as e:
    print(f"Warning during PyTorch pre-initialization: {e}")
    pass


import argparse
import json
import time
import shutil
import traceback
from pathlib import Path
from datetime import datetime
import subprocess

# --- Imports & Exception Handler ---
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer


def global_exception_handler(exc_type, exc_value, exc_traceback):
    """全局异常处理器。"""
    sys.__excepthook__(exc_type, exc_value, exc_traceback)
    error_message = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    def show_error_dialog():
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("严重错误")
        msg_box.setText("<b>程序遇到一个无法恢复的错误，即将退出。</b>")
        msg_box.setInformativeText("错误详情已记录，请向开发者反馈。")
        msg_box.setDetailedText(error_message)
        msg_box.exec_()
        if QApplication.instance():
            QApplication.instance().quit()

    QTimer.singleShot(0, show_error_dialog)

sys.excepthook = global_exception_handler

try:
    from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                                 QPushButton, QLabel, QComboBox, QPlainTextEdit,
                                 QProgressBar, QFileDialog, QListWidget, QListWidgetItem,
                                 QLineEdit, QSplitter, QGroupBox, QTableWidget,
                                 QTableWidgetItem, QHeaderView, QAbstractItemView, QFormLayout)
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, QSize
    from PyQt5.QtGui import QIcon, QPalette

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'modules')))
    from modules.icon_manager import IconManager
    from modules.language_detector_module import detect_language_for_xtts
    
    import torch
    import sounddevice as sd
    import soundfile as sf
    from TTS.api import TTS
    import requests

    import torch.serialization
    from TTS.tts.configs.xtts_config import XttsConfig
    from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
    from TTS.config.shared_configs import BaseDatasetConfig
    trusted_classes = [XttsConfig, XttsAudioConfig, BaseDatasetConfig, XttsArgs]
    torch.serialization.add_safe_globals(trusted_classes)
except ImportError as e:
    QMessageBox.critical(None, "依赖库缺失", f"启动失败，缺少必要的库: {e}\n\n请确保已根据 `requirements_tts.txt` 安装所有依赖。")
    sys.exit(1)

# --- Globals & Constants ---
def get_base_path():
    """获取程序运行的基础路径，兼容打包后的 .exe 和源码运行。"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.abspath(".")

BASE_PATH = get_base_path()
APP_VERSION = "1.0.2" # 版本号更新
MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
MODEL_CACHE_DIR = "tts_models_cache"
XTTS_LANGUAGES = {
    "英语 (en)": "en", "西班牙语 (es)": "es", "法语 (fr)": "fr", "德语 (de)": "de",
    "意大利语 (it)": "it", "葡萄牙语 (pt)": "pt", "波兰语 (pl)": "pl", "土耳其语 (tr)": "tr",
    "俄语 (ru)": "ru", "荷兰语 (nl)": "nl", "捷克语 (cs)": "cs", "阿拉伯语 (ar)": "ar",
    "中文 (zh-cn)": "zh-cn", "日语 (ja)": "ja", "匈牙利语 (hu)": "hu", "韩语 (ko)": "ko",
    "印地语 (hi)": "hi"
}
LANG_FLAG_MAP = {
    'en': 'us', 'es': 'es', 'fr': 'fr', 'de': 'de', 'it': 'it', 'pt': 'pt',
    'pl': 'pl', 'tr': 'tr', 'ru': 'ru', 'nl': 'nl', 'cs': 'cz', 'ar': 'sa',
    'zh-cn': 'cn', 'ja': 'jp', 'hu': 'hu', 'ko': 'kr', 'hi': 'in'
}
ADD_NEW_ROW_ROLE = Qt.UserRole + 1

# --- Worker Classes ---
class ModelLoaderWorker(QObject):
    finished = pyqtSignal(object, str)
    log_message = pyqtSignal(str)
    
    def __init__(self, models_path):
        super().__init__()
        self.models_path = models_path

    def run(self):
        original_stdout, sys.stdout = sys.stdout, self
        original_stderr, sys.stderr = sys.stderr, self
        try:
            # 设置环境变量以指定模型目录并自动同意许可
            os.environ['TTS_HOME'] = self.models_path
            os.environ['COQUI_TOS_AGREED'] = '1'
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.log_message.emit(f"使用的设备: {device}")
            self.log_message.emit(f"设置 TTS 模型目录 (TTS_HOME): {self.models_path}")
            self.log_message.emit("已自动同意 Coqui TTS 许可协议。")
            
            self.log_message.emit(f"正在加载/下载模型: {MODEL_NAME}...")
            tts_instance = TTS(MODEL_NAME).to(device)
            
            self.finished.emit(tts_instance, None)
        except Exception as e:
            error_msg = f"模型加载失败: {e}\n请检查网络连接或 '{self.models_path}' 目录的权限。"
            self.finished.emit(None, error_msg)
        finally:
            sys.stdout, sys.stderr = original_stdout, original_stderr

    def write(self, text):
        """直接将捕获到的所有非空文本行发送出去。"""
        cleaned_text = text.strip()
        if cleaned_text:
            self.log_message.emit(cleaned_text)

    def flush(self): pass

class TTSWorker(QObject):
    progress = pyqtSignal(int, str); task_result = pyqtSignal(int, str, str); finished = pyqtSignal()
    def __init__(self, tts, tasks, speaker_wav):
        super().__init__(); self.tts, self.tasks, self.speaker_wav = tts, tasks, speaker_wav
    def run(self):
        total_tasks = len(self.tasks)
        for i, task in enumerate(self.tasks):
            row, text, lang, output_path = task['row'], task['text'], task['lang'], task['output_path']
            progress_val = int((i / total_tasks) * 100); progress_text = f"({i+1}/{total_tasks}) 正在处理: {text[:20]}..."
            self.progress.emit(progress_val, progress_text)
            try:
                # [核心修复] 添加 split_sentences=False 参数
                wav_data = self.tts.tts(
                    text=text, 
                    speaker_wav=self.speaker_wav, 
                    language=lang,
                    split_sentences=False
                )
                sf.write(output_path, wav_data, self.tts.synthesizer.output_sample_rate)
                self.task_result.emit(row, "success", output_path)
            except Exception as e: self.task_result.emit(row, "failure", f"{type(e).__name__}: {e}")
        self.progress.emit(100, "批量任务完成！"); self.finished.emit()

# --- Main Window Class ---
class LocalTTSWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tts_instance, self.thread = None, None
        self.speaker_wav_path, self.phonacq_root_path, self.flags_path = None, None, None
        self.models_path = os.path.join(BASE_PATH, MODEL_CACHE_DIR)

        self.setWindowTitle(f"PhonAcq 本地TTS工作台 (XTTS) - {APP_VERSION}")
        self.setGeometry(200, 200, 1000, 600)
        self.setAcceptDrops(True)

        self._find_phonacq_root()
        self._setup_icon_manager()
        self._init_ui()
        self._connect_signals()
        self.apply_theme()
        
        self.set_ui_busy(True, loading_model=True)
        self.log_message("正在后台初始化XTTS引擎...")
        QTimer.singleShot(100, self.initialize_tts)

    def _init_ui(self):
        self.central_widget = QWidget(); self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout(self.central_widget); splitter = QSplitter(Qt.Horizontal)
        
        left_panel = QWidget(); left_layout = QVBoxLayout(left_panel)
        task_header_layout = QHBoxLayout()
        task_header_layout.addWidget(QLabel("<b>任务列表</b>"), 1)
        self.load_wordlist_btn = QPushButton("加载词表..."); self.load_wordlist_btn.setToolTip("从JSON词表文件 (standard_wordlist) 加载任务。")
        task_header_layout.addWidget(self.load_wordlist_btn)
        self.task_table = QTableWidget(); self.task_table.setColumnCount(3)
        self.task_table.setHorizontalHeaderLabels(["待合成文本", "语言", "状态"])
        self.task_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.task_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.task_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.task_table.setSelectionBehavior(QAbstractItemView.SelectRows); self.task_table.setToolTip("在此添加、编辑和管理批量合成任务。\n- 生成成功后，双击行即可试听。\n- 生成失败后，双击行可重新编辑。")
        table_btn_layout = QHBoxLayout()
        self.add_row_btn = QPushButton("添加行"); self.add_row_btn.setToolTip("在列表末尾添加一个新的任务行。")
        self.remove_row_btn = QPushButton("删除行"); self.remove_row_btn.setToolTip("删除所有选中的任务行。")
        self.auto_detect_lang_btn = QPushButton("自动检测语言"); self.auto_detect_lang_btn.setToolTip("为所有选中的行自动检测文本语言。")
        table_btn_layout.addWidget(self.add_row_btn); table_btn_layout.addWidget(self.remove_row_btn); table_btn_layout.addStretch(); table_btn_layout.addWidget(self.auto_detect_lang_btn)
        left_layout.addLayout(task_header_layout); left_layout.addWidget(self.task_table); left_layout.addLayout(table_btn_layout)

        right_panel = QWidget(); right_layout = QVBoxLayout(right_panel)
        params_group = QGroupBox("全局参数"); params_layout = QFormLayout(params_group)
        self.speaker_wav_btn = QPushButton("参考音频..."); self.speaker_wav_btn.setToolTip("选择一个WAV或MP3文件作为声音克隆的源。")
        self.speaker_wav_path_label = QLineEdit("未选择参考音频"); self.speaker_wav_path_label.setReadOnly(True); self.speaker_wav_path_label.setToolTip("当前选择的参考音频文件名。")
        self.output_dir_input = QLineEdit(); self.output_dir_input.setPlaceholderText("留空则使用默认名称 (local_tts_util_YYYYMMDD)"); self.output_dir_input.setToolTip("指定生成的音频文件保存的文件夹名称。\n将创建在主程序 'audio_tts' 目录下。")
        self.open_output_dir_btn = QPushButton("打开"); self.open_output_dir_btn.setToolTip("打开最终的输出文件夹。")
        output_controls_layout = QHBoxLayout(); output_controls_layout.setContentsMargins(0, 0, 0, 0)
        output_controls_layout.addWidget(self.output_dir_input, 1); output_controls_layout.addWidget(self.open_output_dir_btn)
        params_layout.addRow(self.speaker_wav_btn, self.speaker_wav_path_label); params_layout.addRow(QLabel("自定义输出文件夹:")); params_layout.addRow(output_controls_layout)
        action_layout = QVBoxLayout(); action_layout.setSpacing(10)
        self.generate_btn = QPushButton("开始批量生成"); self.generate_btn.setObjectName("AccentButton"); self.generate_btn.setFixedHeight(40); self.generate_btn.setToolTip("开始处理左侧列表中的所有任务。\n如果未选择参考音频，将自动下载一个默认样本。")
        self.save_all_btn = QPushButton("全部另存为..."); self.save_all_btn.setFixedHeight(40); self.save_all_btn.setToolTip("将所有成功生成的音频文件保存到您选择的文件夹。")
        action_layout.addWidget(self.generate_btn); action_layout.addWidget(self.save_all_btn)
        log_group = QGroupBox("日志与进度"); log_layout = QVBoxLayout(log_group)
        self.progress_bar = QProgressBar(); self.progress_bar.setRange(0, 100); self.progress_bar.setFormat("准备就绪"); self.progress_bar.setToolTip("显示批量任务的总体进度。")
        self.log_output = QListWidget(); self.log_output.setAlternatingRowColors(True); self.log_output.setToolTip("显示详细的操作日志和错误信息。")
        log_layout.addWidget(self.progress_bar); log_layout.addWidget(self.log_output)
        right_layout.addWidget(params_group); right_layout.addLayout(action_layout); right_layout.addWidget(log_group, 1)

        splitter.addWidget(left_panel); splitter.addWidget(right_panel)
        splitter.setSizes([600, 400]); main_layout.addWidget(splitter)
        self._add_placeholder_row()

    def _connect_signals(self):
        self.load_wordlist_btn.clicked.connect(self.load_wordlist_from_dialog)
        self.speaker_wav_btn.clicked.connect(self.select_speaker_wav)
        self.generate_btn.clicked.connect(self.start_tts_generation)
        self.save_all_btn.clicked.connect(self.save_all_generated)
        self.add_row_btn.clicked.connect(lambda: self.add_table_row())
        self.remove_row_btn.clicked.connect(self.remove_selected_rows)
        self.task_table.cellDoubleClicked.connect(self.handle_cell_double_click)
        self.task_table.cellClicked.connect(self.handle_cell_single_click)
        self.auto_detect_lang_btn.clicked.connect(self._detect_languages_for_selection)
        self.open_output_dir_btn.clicked.connect(self.open_output_directory)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            if url.isLocalFile() and url.toLocalFile().lower().endswith('.json'):
                event.acceptProposedAction()

    def dropEvent(self, event):
        filepath = event.mimeData().urls()[0].toLocalFile()
        self._load_wordlist_from_path(filepath)

    def load_wordlist_from_dialog(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "选择词表文件", "", "JSON 文件 (*.json)")
        if filepath: self._load_wordlist_from_path(filepath)

    def _load_wordlist_from_path(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f: data = json.load(f)
            if data.get("meta", {}).get("format") != "standard_wordlist": raise ValueError("不支持的词表格式，需要 'standard_wordlist'。")
            items_to_add = [item for group in data.get("groups", []) for item in group.get("items", []) if item.get("text")]
            if not items_to_add: self.log_message("词表中未找到有效的文本条目。", "warn"); return
            reply = QMessageBox.question(self, "加载词表", f"将从 '{os.path.basename(filepath)}' 加载 {len(items_to_add)} 个任务。\n这将清空当前列表，是否继续？", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No: return
            self._remove_placeholder_row(); self.task_table.setRowCount(0)
            for item in items_to_add:
                new_row_index = self.add_table_row(item['text'])
                lang_combo = self.task_table.cellWidget(new_row_index, 1)
                if lang_combo and item.get('lang'):
                    index = lang_combo.findData(item['lang'])
                    if index != -1: lang_combo.setCurrentIndex(index)
            self.log_message(f"成功从 '{os.path.basename(filepath)}' 加载 {len(items_to_add)} 个任务。", "success")
        except Exception as e:
            error_msg = f"加载词表失败: {e}"; self.log_message(error_msg, "error"); QMessageBox.critical(self, "加载失败", f"无法加载或解析词表文件:\n{e}")

    def select_speaker_wav(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "选择参考音频文件", "", "音频文件 (*.wav *.mp3 *.flac)")
        if filepath: self.speaker_wav_path = filepath; self.speaker_wav_path_label.setText(os.path.basename(filepath)); self.log_message(f"已选择参考音频: {os.path.basename(filepath)}", "info")

    def start_tts_generation(self):
        if not self.speaker_wav_path:
            self.log_message("未选择参考音频，将尝试下载默认样本...", "warn"); QApplication.processEvents()
            default_wav = self._download_default_speaker_wav()
            if default_wav: self.speaker_wav_path = default_wav; self.speaker_wav_path_label.setText(os.path.basename(default_wav)); self.log_message("默认参考音频准备就绪。", "success")
            else: self.log_message("无法获取参考音频，任务中止。", "error"); return
        output_root = os.path.join(self.phonacq_root_path, "audio_tts") if self.phonacq_root_path else os.path.join(BASE_PATH, "audio_tts")
        custom_name = self.output_dir_input.text().strip()
        folder_name = "".join(x for x in custom_name if x.isalnum() or x in " _-").strip() if custom_name else f"local_tts_util_{datetime.now().strftime('%Y%m%d')}"
        output_dir = os.path.join(output_root, folder_name); os.makedirs(output_dir, exist_ok=True)
        self.log_message(f"音频将保存到: {output_dir}", "info")
        tasks = []
        for row in range(self.task_table.rowCount()):
            text_item = self.task_table.item(row, 0)
            if not text_item or text_item.data(ADD_NEW_ROW_ROLE): continue
            text = text_item.text().strip()
            if text:
                lang_combo = self.task_table.cellWidget(row, 1)
                safe_filename = "".join(x for x in text if x.isalnum() or x in " _-").strip()[:50] + ".wav"
                tasks.append({ "row": row, "text": text, "lang": lang_combo.currentData(), "output_path": os.path.join(output_dir, safe_filename)})
                self.update_task_status(row, "processing")
        if not tasks: self.log_message("任务列表为空或无有效文本。", "warn"); return
        self.task_table.horizontalHeader().model().setHeaderData(0, Qt.Horizontal, "已合成音频 (双击试听)"); self.set_ui_busy(True)
        self.thread = QThread(self); self.worker = TTSWorker(self.tts_instance, tasks, self.speaker_wav_path); self.worker.moveToThread(self.thread)
        self.worker.progress.connect(self.update_progress); self.worker.task_result.connect(self.on_task_result); self.worker.finished.connect(self.on_batch_finished)
        self.thread.started.connect(self.worker.run); self.thread.finished.connect(self.on_thread_finished); self.thread.start()
    
    def add_table_row(self, text="", at_row=None):
        self._remove_placeholder_row()
        row_pos = self.task_table.rowCount() if at_row is None else at_row
        self.task_table.insertRow(row_pos); self.task_table.setItem(row_pos, 0, QTableWidgetItem(text))
        lang_combo = self._create_language_combo(); self.task_table.setCellWidget(row_pos, 1, lang_combo)
        self.update_task_status(row_pos, "pending"); self._add_placeholder_row(); return row_pos
    
    def _create_language_combo(self):
        combo = QComboBox(); combo.setIconSize(QSize(20, 14)); all_langs = list(XTTS_LANGUAGES.items()); pinned_codes = ['zh-cn', 'en']
        for code in pinned_codes:
            display_name = next((name for name, c in all_langs if c == code), None)
            if display_name:
                flag_code = LANG_FLAG_MAP.get(code, ''); icon = QIcon(os.path.join(self.flags_path, f"{flag_code}.png")) if self.flags_path and flag_code else QIcon()
                combo.addItem(icon, display_name, code)
        combo.insertSeparator(len(pinned_codes))
        for name, code in sorted(all_langs):
            if code not in pinned_codes:
                flag_code = LANG_FLAG_MAP.get(code, ''); icon = QIcon(os.path.join(self.flags_path, f"{flag_code}.png")) if self.flags_path and flag_code else QIcon()
                combo.addItem(icon, name, code)
        return combo
    
    def _detect_languages_for_selection(self):
        selected_rows = sorted(list(set(index.row() for index in self.task_table.selectedIndexes())))
        if not selected_rows: QMessageBox.information(self, "无选中项", "请先在任务列表中选择要检测的行。"); return
        detected_count = 0
        for row in selected_rows:
            text_item = self.task_table.item(row, 0)
            if text_item and text_item.text().strip():
                text = text_item.text().strip(); detected_code = detect_language_for_xtts(text)
                if detected_code:
                    lang_combo = self.task_table.cellWidget(row, 1)
                    if lang_combo:
                        index = lang_combo.findData(detected_code)
                        if index != -1: lang_combo.setCurrentIndex(index); detected_count += 1
        self.log_message(f"为 {detected_count}/{len(selected_rows)} 个选中行成功检测并设置了语言。", "success")
    
    def open_output_directory(self):
        output_root = os.path.join(self.phonacq_root_path, "audio_tts") if self.phonacq_root_path else os.path.join(BASE_PATH, "audio_tts")
        custom_name = self.output_dir_input.text().strip(); folder_name = custom_name if custom_name else f"local_tts_util_{datetime.now().strftime('%Y%m%d')}"
        target_dir = os.path.join(output_root, folder_name)
        if not os.path.exists(target_dir):
            reply = QMessageBox.question(self, "目录不存在", f"目录 '{target_dir}' 尚不存在。\n是否要创建它？", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                try: os.makedirs(target_dir, exist_ok=True)
                except Exception as e: QMessageBox.critical(self, "创建失败", f"无法创建目录: {e}"); return
            else: return
        try:
            if sys.platform == 'win32': os.startfile(os.path.realpath(target_dir))
            else: subprocess.run(['xdg-open', target_dir], check=True)
        except Exception as e: QMessageBox.critical(self, "打开失败", f"无法打开文件夹: {e}")

    def _setup_icon_manager(self):
        if self.phonacq_root_path:
            default_icon_path = os.path.join(self.phonacq_root_path, "assets", "icons"); self.flags_path = os.path.join(self.phonacq_root_path, "assets", "flags")
        else:
            local_assets = os.path.join(BASE_PATH, "assets")
            default_icon_path = os.path.join(local_assets, "icons"); self.flags_path = os.path.join(local_assets, "flags")
        self.icon_manager = IconManager(default_icon_path)
    
    def update_icons(self):
        icon_path = os.path.join(BASE_PATH, "assets", "icon.ico")
        if os.path.exists(icon_path): self.setWindowIcon(QIcon(icon_path))
        else: self.setWindowIcon(self.icon_manager.get_icon("tts_local_logo"))
        self.generate_btn.setIcon(self.icon_manager.get_icon("start_session")); self.save_all_btn.setIcon(self.icon_manager.get_icon("save_all"))
        self.speaker_wav_btn.setIcon(self.icon_manager.get_icon("open_file")); self.add_row_btn.setIcon(self.icon_manager.get_icon("add_row"))
        self.remove_row_btn.setIcon(self.icon_manager.get_icon("remove_row")); self.auto_detect_lang_btn.setIcon(self.icon_manager.get_icon("magic_wand"))
        self.open_output_dir_btn.setIcon(self.icon_manager.get_icon("open_folder")); self.load_wordlist_btn.setIcon(self.icon_manager.get_icon("open_file"))

    def on_task_result(self, row, status, result): self.update_task_status(row, status, result)
    
    def on_batch_finished(self):
        self.set_ui_busy(False)
        if self.thread: self.thread.quit()
        self.log_message("批量任务处理完毕。", "success")
    
    def remove_selected_rows(self):
        rows = sorted(list(set(index.row() for index in self.task_table.selectedIndexes())), reverse=True)
        for row in rows:
            item = self.task_table.item(row, 0)
            if not (item and item.data(ADD_NEW_ROW_ROLE)): self.task_table.removeRow(row)
    
    def handle_cell_double_click(self, row, column):
        if column == 0:
            item = self.task_table.item(row, 0)
            if item and not (item.flags() & Qt.ItemIsEditable): self.play_audio_from_row(row)

    def play_audio_from_row(self, row):
        status_item = self.task_table.item(row, 2)
        if status_item and status_item.data(Qt.UserRole):
            filepath = status_item.data(Qt.UserRole)
            if filepath and os.path.exists(filepath):
                try: data, fs = sf.read(filepath, dtype='float32'); sd.play(data, fs)
                except Exception as e: self.log_message(f"播放失败: {e}", "error")
    
    def save_all_generated(self):
        successful_files = []
        for row in range(self.task_table.rowCount()):
            status_item = self.task_table.item(row, 2)
            if status_item and status_item.data(Qt.UserRole): successful_files.append({"text": self.task_table.item(row, 0).text(), "path": status_item.data(Qt.UserRole)})
        if not successful_files: QMessageBox.information(self, "无文件", "没有成功生成的音频文件。"); return
        target_dir = QFileDialog.getExistingDirectory(self, "选择保存所有音频的文件夹")
        if not target_dir: return
        saved_count = 0
        for file_info in successful_files:
            try:
                safe_filename = "".join(x for x in file_info['text'] if x.isalnum() or x in " _-").strip()[:50] + ".wav"
                shutil.copy(file_info['path'], os.path.join(target_dir, safe_filename)); saved_count += 1
            except Exception as e: self.log_message(f"保存 '{file_info['text']}' 失败: {e}", "error")
        self.log_message(f"成功保存 {saved_count}/{len(successful_files)} 个文件到 '{target_dir}'", "success")
    
    def set_ui_busy(self, busy, loading_model=False):
        is_ready = not busy and self.tts_instance is not None
        self.task_table.setEnabled(not loading_model); self.add_row_btn.setEnabled(not busy); self.remove_row_btn.setEnabled(not busy)
        self.speaker_wav_btn.setEnabled(not busy); self.auto_detect_lang_btn.setEnabled(not busy)
        self.output_dir_input.setEnabled(not busy); self.load_wordlist_btn.setEnabled(not busy)
        self.generate_btn.setEnabled(is_ready); self.save_all_btn.setEnabled(is_ready)
        if loading_model: self.progress_bar.setFormat("正在加载模型...")
        elif busy: self.progress_bar.setFormat("处理中...")
        else: self.progress_bar.setFormat("准备就绪"); self.task_table.horizontalHeader().model().setHeaderData(0, Qt.Horizontal, "待合成文本 (双击编辑)")

    def handle_cell_single_click(self, row, column):
        item = self.task_table.item(row, 0)
        if item and item.data(ADD_NEW_ROW_ROLE):
            new_row_index = self.add_table_row(at_row=row)
            self.task_table.setCurrentCell(new_row_index, 0)
            self.task_table.editItem(self.task_table.item(new_row_index, 0))

    def _add_placeholder_row(self):
        current_rows = self.task_table.rowCount()
        self.task_table.insertRow(current_rows)
        add_item = QTableWidgetItem(" 点击此处或按'添加行'按钮添加新任务..."); add_item.setData(ADD_NEW_ROW_ROLE, True)
        add_item.setForeground(self.palette().color(QPalette.Disabled, QPalette.Text)); add_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        add_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable); self.task_table.setItem(current_rows, 0, add_item)
        self.task_table.setSpan(current_rows, 0, 1, self.task_table.columnCount())
    
    def _remove_placeholder_row(self):
        last_row = self.task_table.rowCount() - 1
        if last_row >= 0 and self.task_table.item(last_row, 0) and self.task_table.item(last_row, 0).data(ADD_NEW_ROW_ROLE):
            self.task_table.removeRow(last_row)
    
    def update_task_status(self, row, status, data=None):
        text_item = self.task_table.item(row, 0); lang_combo = self.task_table.cellWidget(row, 1); status_item = self.task_table.item(row, 2)
        if not status_item: status_item = QTableWidgetItem(); self.task_table.setItem(row, 2, status_item)
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable; lang_combo_enabled = True
        if status == "pending": status_item.setText("待处理"); status_item.setIcon(QIcon()); flags |= Qt.ItemIsEditable
        elif status == "processing": status_item.setText("处理中..."); status_item.setIcon(self.icon_manager.get_icon("loading")); lang_combo_enabled = False
        elif status == "success": status_item.setText("成功"); status_item.setIcon(self.icon_manager.get_icon("success")); status_item.setData(Qt.UserRole, data); lang_combo_enabled = False; text_item.setFlags(flags) # 成功后文本不可编辑
        elif status == "failure": status_item.setText("失败"); status_item.setIcon(self.icon_manager.get_icon("error")); status_item.setToolTip(data); flags |= Qt.ItemIsEditable
        if text_item: text_item.setFlags(flags)
        if lang_combo: lang_combo.setEnabled(lang_combo_enabled)
        status_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
    
    def initialize_tts(self):
        if not os.path.exists(self.models_path):
            self.log_message("未找到本地模型缓存，将开始自动下载。", "warn")
            self.log_message("XTTSv2模型较大(约2.2GB)，请确保网络连接稳定并耐心等待...", "info")
            QApplication.processEvents()
        self.thread = QThread(self)
        self.model_loader_worker = ModelLoaderWorker(models_path=self.models_path)
        self.model_loader_worker.moveToThread(self.thread)
        self.model_loader_worker.log_message.connect(lambda msg: self.log_message(msg, "info"))
        self.model_loader_worker.finished.connect(self.on_model_loaded)
        self.thread.started.connect(self.model_loader_worker.run)
        self.thread.finished.connect(self.on_thread_finished)
        self.thread.start()
    
    def on_model_loaded(self, tts_instance, error_message):
        if self.thread: self.thread.quit()
        if error_message:
            self.log_message(error_message, "error")
            QMessageBox.critical(self, "模型加载失败", error_message)
        else:
            self.tts_instance = tts_instance
            if self.log_output.count() > 0:
                 last_item = self.log_output.item(self.log_output.count() - 1)
                 if last_item and last_item.data(Qt.UserRole) == 'progress':
                     last_item.setText("模型文件下载/校验完成。")
                     last_item.setData(Qt.UserRole, None)
            self.log_message("XTTS 模型加载成功！", "success")
        self.set_ui_busy(False)
    
    def _download_default_speaker_wav(self):
        internal_dir = os.path.join(BASE_PATH, "_internal"); os.makedirs(internal_dir, exist_ok=True)
        filename = os.path.join(internal_dir, "speaker_sample.wav")
        if os.path.exists(filename): return filename
        reply = QMessageBox.information(self, "下载提示", "将从网络下载一个默认的英文女声样本 (约200KB)。\n这只会发生一次。", QMessageBox.Ok | QMessageBox.Cancel)
        if reply == QMessageBox.Cancel: return None
        url = "https://github.com/coqui-ai/TTS/raw/main/tests/data/ljspeech/wavs/LJ001-0001.wav"
        try:
            self.progress_bar.setFormat("正在下载参考音频..."); QApplication.processEvents()
            response = requests.get(url, stream=True, timeout=15); response.raise_for_status()
            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192): f.write(chunk)
            self.progress_bar.setFormat("准备就绪"); return filename
        except Exception as e: QMessageBox.critical(self, "下载失败", f"无法下载默认参考音频: {e}"); self.progress_bar.setFormat("下载失败"); return None
    
    def on_thread_finished(self): self.thread = None
    
    def closeEvent(self, event):
        if self.thread and self.thread.isRunning(): self.thread.quit(); self.thread.wait(100)
        event.accept()
    
    def _find_phonacq_root(self):
        current_path = Path(BASE_PATH)
        for _ in range(5):
            if (current_path / "config" / "settings.json").is_file():
                self.phonacq_root_path = str(current_path); self.phonacq_themes_path = str(current_path / "themes"); return
            current_path = current_path.parent
            
    def apply_theme(self):
        stylesheet = ""
        themes_dir_to_use = os.path.join(BASE_PATH, "themes")
        theme_to_load = "默认.qss"
        if self.phonacq_root_path:
            try:
                settings_path = os.path.join(self.phonacq_root_path, "config", "settings.json")
                with open(settings_path, 'r', encoding='utf-8') as f: main_config = json.load(f)
                theme_to_load = main_config.get("theme", theme_to_load); themes_dir_to_use = self.phonacq_themes_path
            except Exception: pass
        theme_path = os.path.join(themes_dir_to_use, theme_to_load)
        if os.path.exists(theme_path):
            with open(theme_path, "r", encoding="utf-8") as f: stylesheet = f.read()
        self.setStyleSheet(stylesheet); self.update_icons()

    def update_progress(self, value, message): self.progress_bar.setValue(value); self.progress_bar.setFormat(message)
    
    def log_message(self, message, level="info"):
        if not message.strip(): return
        is_progress_message = ('%' in message and '|' in message and 'Downloading' in message)
        last_item = self.log_output.item(self.log_output.count() - 1) if self.log_output.count() > 0 else None
        was_last_item_progress = last_item and last_item.data(Qt.UserRole) == 'progress'
        if is_progress_message and was_last_item_progress:
            last_item.setText(message)
        else:
            icon_name = level if level in ["info", "success", "warn", "error"] else "info"
            icon = self.icon_manager.get_icon(icon_name)
            new_item = QListWidgetItem(icon, message)
            if is_progress_message:
                new_item.setData(Qt.UserRole, 'progress')
            self.log_output.addItem(new_item)
        self.log_output.scrollToBottom()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LocalTTSWindow()
    window.show()
    print("TTS_LOCAL_UI_READY", flush=True)
    sys.exit(app.exec_())