import sys
import json
import csv
import re
import os
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLineEdit, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QLabel, 
    QAbstractItemView, QMessageBox, QProgressDialog,
    QFileDialog, QComboBox, QInputDialog
)
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- 1. 포터블 환경 설정 ---

def get_app_directory():
    """실행 파일이 있는 디렉토리 경로 반환 (exe/py 모두 지원)"""
    if getattr(sys, 'frozen', False):
        # PyInstaller로 빌드된 exe 파일인 경우
        return Path(sys.executable).parent
    else:
        # 일반 Python 스크립트인 경우
        return Path(__file__).parent

def get_data_directory():
    """데이터 저장 디렉토리 (없으면 생성)"""
    data_dir = get_app_directory() / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir

def get_config_path():
    """설정 파일 경로"""
    return get_app_directory() / "config.json"

def load_config():
    """설정 파일에서 API 키 로드"""
    config_path = get_config_path()
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('api_key')
        except Exception as e:
            print(f"설정 파일 읽기 오류: {e}")
    return None

def save_config(api_key):
    """API 키를 설정 파일에 저장"""
    config_path = get_config_path()
    try:
        config = {'api_key': api_key}
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"설정 파일 저장 오류: {e}")
        return False

# --- 2. 유틸리티 함수 ---

def format_duration(duration):
    """ISO 8601 형식을 [H:MM:SS] 형식으로 변환"""
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
    if not match:
        return "N/A"
    
    hours, minutes, seconds = [int(x) if x else 0 for x in match.groups()]
    total_seconds = hours * 3600 + minutes * 60 + seconds
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60

    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"

def format_count(count):
    """큰 숫자를 한국어 포맷으로 변환"""
    if count >= 100000000:
        return f"{count / 100000000:.1f}억"
    if count >= 10000:
        return f"{count / 10000:.1f}만"
    return f"{count:,}"

# --- 3. YouTube API 통신 로직 (별도 스레드) ---

class YouTubeSearchThread(QThread):
    """YouTube API 호출을 별도 스레드에서 처리"""
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, keyword, api_key, max_results=20):
        super().__init__()
        self.keyword = keyword
        self.api_key = api_key
        self.max_results = max_results
    
    def run(self):
        try:
            self.progress.emit("YouTube API 연결 중...")
            youtube = build("youtube", "v3", developerKey=self.api_key)
            
            # 1. 키워드 검색
            self.progress.emit(f"'{self.keyword}' 검색 중...")
            search_response = youtube.search().list(
                q=self.keyword,
                part="snippet",
                type="video",
                maxResults=self.max_results,
                order="relevance"
            ).execute()
            
            video_ids = [item['id']['videoId'] for item in search_response.get('items', []) 
                        if item['id']['kind'] == 'youtube#video']
            
            if not video_ids:
                self.error.emit("검색 결과가 없습니다.")
                return
            
            # 2. 영상 상세 정보 수집
            self.progress.emit(f"{len(video_ids)}개 영상 정보 수집 중...")
            video_response = youtube.videos().list(
                part="contentDetails,statistics,snippet",
                id=",".join(video_ids)
            ).execute()
            
            results = []
            channel_ids = set()
            
            for item in video_response.get('items', []):
                channel_ids.add(item['snippet']['channelId'])
                
                view_count = int(item['statistics'].get('viewCount', 0))
                like_count = int(item['statistics'].get('likeCount', 0))
                comment_count = int(item['statistics'].get('commentCount', 0))
                
                data = {
                    "id": item['id'],
                    "제목": item['snippet']['title'],
                    "게시일": item['snippet']['publishedAt'][:10],
                    "영상 길이": format_duration(item['contentDetails']['duration']),
                    "조회수_raw": view_count,
                    "조회수": format_count(view_count),
                    "좋아요_raw": like_count,
                    "좋아요 수": format_count(like_count),
                    "댓글_raw": comment_count,
                    "댓글 수": format_count(comment_count),
                    "채널명": item['snippet']['channelTitle'],
                    "채널ID": item['snippet']['channelId'],
                    "구독자 수": "수집 중...",
                    "URL": f"https://www.youtube.com/watch?v={item['id']}"
                }
                results.append(data)
            
            # 3. 채널 구독자 수 수집
            if channel_ids:
                self.progress.emit("채널 구독자 수 수집 중...")
                channel_response = youtube.channels().list(
                    part="statistics",
                    id=",".join(channel_ids)
                ).execute()
                
                channel_stats = {}
                for item in channel_response.get('items', []):
                    sub_count = item['statistics'].get('subscriberCount')
                    if sub_count:
                        channel_stats[item['id']] = format_count(int(sub_count))
                    else:
                        channel_stats[item['id']] = "비공개"
                
                for item in results:
                    item['구독자 수'] = channel_stats.get(item['채널ID'], "비공개")
            
            self.progress.emit("데이터 수집 완료!")
            self.finished.emit(results)
            
        except HttpError as e:
            error_content = json.loads(e.content.decode('utf-8'))
            error_message = error_content.get('error', {}).get('message', str(e))
            
            if 'quotaExceeded' in str(e):
                self.error.emit("YouTube API 할당량이 초과되었습니다.\n내일 다시 시도해주세요.")
            elif 'keyInvalid' in str(e) or 'API key not valid' in str(e):
                self.error.emit("API 키가 유효하지 않습니다.\n설정에서 올바른 API 키를 입력해주세요.")
            else:
                self.error.emit(f"API 오류: {error_message}")
        
        except Exception as e:
            self.error.emit(f"오류 발생: {str(e)}")

# --- 4. PyQt GUI 클래스 ---

class YouTubeCollectorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube 데이터 수집 시스템 (Portable)")
        self.setGeometry(100, 100, 1400, 700)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        self.current_data = []
        self.checked_items = set()
        self.api_key = load_config()
        self.search_thread = None
        
        self._setup_ui()
        
        # 앱 시작 시 API 키 확인
        if not self.api_key:
            self.show_api_key_setup()
        
    def show_api_key_setup(self):
        """API 키 설정 다이얼로그"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("API 키 설정 필요")
        msg.setText("YouTube API 키를 설정해주세요.\n\n"
                   "API 키는 Google Cloud Console에서 발급받을 수 있습니다.\n"
                   "https://console.cloud.google.com/")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        
        result = msg.exec()
        if result == QMessageBox.StandardButton.Ok:
            self.open_settings()
        
    def _setup_ui(self):
        # 상단 정보 바
        info_bar = QHBoxLayout()
        app_dir = get_app_directory()
        location_label = QLabel(f"📁 프로그램 위치: {app_dir}")
        location_label.setStyleSheet("color: #666; padding: 5px; font-size: 11px;")
        
        self.settings_btn = QPushButton("⚙️ API 키 설정")
        self.settings_btn.clicked.connect(self.open_settings)
        self.settings_btn.setFixedSize(120, 25)
        
        info_bar.addWidget(location_label)
        info_bar.addStretch()
        info_bar.addWidget(self.settings_btn)
        
        self.main_layout.addLayout(info_bar)
        
        # 상태 표시 레이블
        self.status_label = QLabel("검색 키워드를 입력하세요")
        self.status_label.setStyleSheet("color: #666; padding: 5px; font-weight: bold;")
        self.main_layout.addWidget(self.status_label)
        
        # 1. 검색 영역
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("검색 키워드를 입력하세요...")
        self.search_input.setFixedHeight(35)
        self.search_input.returnPressed.connect(self.run_search)
        
        self.results_combo = QComboBox()
        self.results_combo.addItems(["20개", "50개", "100개"])
        self.results_combo.setFixedWidth(80)
        
        self.search_button = QPushButton("🔍 검색 및 데이터 수집")
        self.search_button.clicked.connect(self.run_search)
        self.search_button.setFixedHeight(35)
        
        search_layout.addWidget(QLabel("결과 수:"))
        search_layout.addWidget(self.results_combo)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        
        self.main_layout.addLayout(search_layout)
        
        # 2. 컨트롤 버튼들
        control_layout = QHBoxLayout()
        
        self.sort_date_btn = QPushButton("📅 게시일순")
        self.sort_date_btn.clicked.connect(lambda: self.sort_table_by_column("게시일"))
        
        self.sort_view_btn = QPushButton("👁️ 조회수순")
        self.sort_view_btn.clicked.connect(lambda: self.sort_table_by_column("조회수"))
        
        self.sort_like_btn = QPushButton("👍 좋아요순")
        self.sort_like_btn.clicked.connect(lambda: self.sort_table_by_column("좋아요 수"))
        
        self.select_all_btn = QPushButton("✅ 전체 선택")
        self.select_all_btn.clicked.connect(self.select_all)
        
        self.deselect_all_btn = QPushButton("❌ 전체 해제")
        self.deselect_all_btn.clicked.connect(self.deselect_all)
        
        self.export_json_btn = QPushButton("💾 JSON 저장")
        self.export_json_btn.clicked.connect(lambda: self.export_data('json'))
        
        self.export_csv_btn = QPushButton("📊 CSV 저장")
        self.export_csv_btn.clicked.connect(lambda: self.export_data('csv'))
        
        control_layout.addWidget(self.sort_date_btn)
        control_layout.addWidget(self.sort_view_btn)
        control_layout.addWidget(self.sort_like_btn)
        control_layout.addStretch()
        control_layout.addWidget(self.select_all_btn)
        control_layout.addWidget(self.deselect_all_btn)
        control_layout.addWidget(self.export_json_btn)
        control_layout.addWidget(self.export_csv_btn)
        
        self.main_layout.addLayout(control_layout)
        
        # 3. 결과 테이블
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(9)
        self.table_widget.setHorizontalHeaderLabels([
            "선택", "제목", "게시일", "영상 길이", 
            "조회수", "좋아요", "댓글", "채널명", "구독자"
        ])
        
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.doubleClicked.connect(self.open_video_url)
        
        self.main_layout.addWidget(self.table_widget)
        
        # 하단 정보
        tip_layout = QHBoxLayout()
        tip_label = QLabel("💡 팁: 행을 더블클릭하면 YouTube 영상을 엽니다")
        tip_label.setStyleSheet("color: #888; padding: 5px;")
        
        data_dir = get_data_directory()
        data_path_label = QLabel(f"📂 저장 폴더: {data_dir}")
        data_path_label.setStyleSheet("color: #888; padding: 5px; font-size: 11px;")
        
        tip_layout.addWidget(tip_label)
        tip_layout.addStretch()
        tip_layout.addWidget(data_path_label)
        
        self.main_layout.addLayout(tip_layout)

    def open_settings(self):
        """API 키 설정 다이얼로그"""
        current_key = self.api_key if self.api_key else ""
        
        api_key, ok = QInputDialog.getText(
            self,
            "API 키 설정",
            "YouTube Data API v3 키를 입력하세요:\n"
            "(발급: https://console.cloud.google.com/)",
            QLineEdit.EchoMode.Normal,
            current_key
        )
        
        if ok and api_key.strip():
            api_key = api_key.strip()
            if save_config(api_key):
                self.api_key = api_key
                QMessageBox.information(self, "설정 완료", "API 키가 저장되었습니다!")
                self.status_label.setText("✅ API 키 설정 완료 - 검색을 시작하세요")
            else:
                QMessageBox.warning(self, "오류", "API 키 저장에 실패했습니다.")

    def run_search(self):
        """검색 실행"""
        if not self.api_key:
            QMessageBox.warning(
                self, 
                "API 키 필요", 
                "먼저 API 키를 설정해주세요.\n'⚙️ API 키 설정' 버튼을 클릭하세요."
            )
            self.open_settings()
            return
        
        keyword = self.search_input.text().strip()
        if not keyword:
            self.search_input.setPlaceholderText("키워드를 입력해주세요!")
            return
        
        if self.search_thread and self.search_thread.isRunning():
            return
        
        max_results = int(self.results_combo.currentText().replace("개", ""))
        
        self.search_button.setEnabled(False)
        self.status_label.setText("검색 중...")
        
        self.search_thread = YouTubeSearchThread(keyword, self.api_key, max_results)
        self.search_thread.finished.connect(self.on_search_finished)
        self.search_thread.error.connect(self.on_search_error)
        self.search_thread.progress.connect(self.on_progress_update)
        self.search_thread.start()

    def on_progress_update(self, message):
        self.status_label.setText(message)

    def on_search_finished(self, results):
        self.current_data = results
        self.checked_items.clear()
        self.populate_table(results)
        
        self.search_button.setEnabled(True)
        self.status_label.setText(f"✅ {len(results)}개의 영상을 찾았습니다")

    def on_search_error(self, error_msg):
        self.search_button.setEnabled(True)
        self.status_label.setText("❌ 검색 실패")
        QMessageBox.critical(self, "오류", error_msg)

    def sort_table_by_column(self, column_name):
        if not self.current_data:
            return
        
        self.save_checked_state()
        
        sort_key_map = {
            "조회수": "조회수_raw",
            "좋아요 수": "좋아요_raw",
            "댓글 수": "댓글_raw",
            "게시일": "게시일"
        }
        sort_key = sort_key_map.get(column_name, column_name)
        
        if hasattr(self, '_sort_column') and self._sort_column == column_name:
            self._sort_order = not self._sort_order
        else:
            self._sort_order = True
            self._sort_column = column_name
        
        self.current_data.sort(
            key=lambda x: (
                datetime.fromisoformat(x[sort_key]) if sort_key == "게시일" 
                else x.get(sort_key, 0)
            ),
            reverse=self._sort_order
        )
        
        self.populate_table(self.current_data)
        self.restore_checked_state()
        
        order_text = "↓ 높은순" if self._sort_order else "↑ 낮은순"
        self.status_label.setText(f"{column_name} {order_text} 정렬됨")

    def populate_table(self, data):
        self.table_widget.setRowCount(len(data))
        
        for row_idx, video in enumerate(data):
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            checkbox_item.setCheckState(Qt.CheckState.Unchecked)
            self.table_widget.setItem(row_idx, 0, checkbox_item)
            
            columns = [
                video.get("제목", ""),
                video.get("게시일", ""),
                video.get("영상 길이", ""),
                video.get("조회수", "0"),
                video.get("좋아요 수", "0"),
                video.get("댓글 수", "0"),
                video.get("채널명", ""),
                video.get("구독자 수", "비공개")
            ]
            
            for col_idx, value in enumerate(columns, 1):
                self.table_widget.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def save_checked_state(self):
        self.checked_items.clear()
        for row in range(self.table_widget.rowCount()):
            if self.table_widget.item(row, 0).checkState() == Qt.CheckState.Checked:
                video_id = self.current_data[row]['id']
                self.checked_items.add(video_id)

    def restore_checked_state(self):
        for row in range(self.table_widget.rowCount()):
            video_id = self.current_data[row]['id']
            if video_id in self.checked_items:
                self.table_widget.item(row, 0).setCheckState(Qt.CheckState.Checked)

    def select_all(self):
        for row in range(self.table_widget.rowCount()):
            self.table_widget.item(row, 0).setCheckState(Qt.CheckState.Checked)
        self.status_label.setText(f"✅ {self.table_widget.rowCount()}개 항목 선택됨")

    def deselect_all(self):
        for row in range(self.table_widget.rowCount()):
            self.table_widget.item(row, 0).setCheckState(Qt.CheckState.Unchecked)
        self.status_label.setText("선택 해제됨")

    def get_selected_data(self):
        selected = []
        for row in range(self.table_widget.rowCount()):
            if self.table_widget.item(row, 0).checkState() == Qt.CheckState.Checked:
                selected.append(self.current_data[row])
        return selected

    def export_data(self, format_type):
        selected_data = self.get_selected_data()
        
        if not selected_data:
            QMessageBox.warning(self, "경고", "선택된 항목이 없습니다.\n먼저 내보낼 항목을 선택해주세요.")
            return
        
        # 기본 저장 경로를 data 폴더로 설정
        data_dir = get_data_directory()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format_type == 'json':
            default_path = data_dir / f"youtube_data_{timestamp}.json"
            file_path, _ = QFileDialog.getSaveFileName(
                self, "JSON 파일로 저장", 
                str(default_path),
                "JSON Files (*.json)"
            )
            if file_path:
                self._save_as_json(selected_data, file_path)
        
        elif format_type == 'csv':
            default_path = data_dir / f"youtube_data_{timestamp}.csv"
            file_path, _ = QFileDialog.getSaveFileName(
                self, "CSV 파일로 저장",
                str(default_path),
                "CSV Files (*.csv)"
            )
            if file_path:
                self._save_as_csv(selected_data, file_path)

    def _save_as_json(self, data, file_path):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(
                self, "저장 완료", 
                f"{len(data)}개 항목이 JSON 파일로 저장되었습니다.\n\n{file_path}"
            )
            self.status_label.setText(f"💾 {len(data)}개 항목 저장 완료")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"저장 실패: {str(e)}")

    def _save_as_csv(self, data, file_path):
        try:
            with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
                if not data:
                    return
                
                fieldnames = ['제목', '게시일', '영상 길이', '조회수', '좋아요 수', 
                             '댓글 수', '채널명', '구독자 수', 'URL']
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                
                writer.writeheader()
                writer.writerows(data)
            
            QMessageBox.information(
                self, "저장 완료",
                f"{len(data)}개 항목이 CSV 파일로 저장되었습니다.\n\n{file_path}"
            )
            self.status_label.setText(f"📊 {len(data)}개 항목 저장 완료")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"저장 실패: {str(e)}")

    def open_video_url(self, index):
        row = index.row()
        if 0 <= row < len(self.current_data):
            url = self.current_data[row].get('URL')
            if url:
                import webbrowser
                webbrowser.open(url)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = YouTubeCollectorApp()
    window.show()
    sys.exit(app.exec())