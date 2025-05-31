#!/usr/bin/env python3
import sys
import os
import subprocess
import json
import tempfile
import webbrowser
from datetime import datetime
import numpy as np
import librosa
import cv2
from PIL import Image
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QFileDialog, QTextEdit, QProgressBar,
                             QTabWidget, QListWidget, QMessageBox, QGroupBox, QCheckBox,
                             QSplitter, QSizePolicy, QComboBox, QDoubleSpinBox,
                             QAction, QMenu, QStatusBar, QFrame, QToolButton)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer, QSize, QUrl
from PyQt5.QtGui import (QPixmap, QIcon, QColor, QFont, QPalette, QLinearGradient,
                         QBrush, QPainter, QDesktopServices)

# Set environment variable for XDG_RUNTIME_DIR if not set
if not os.environ.get("XDG_RUNTIME_DIR"):
    os.environ["XDG_RUNTIME_DIR"] = f"/tmp/runtime-{os.getuid()}"
    os.makedirs(os.environ["XDG_RUNTIME_DIR"], exist_ok=True)

def check_ffmpeg():
    """Check if FFmpeg is installed and available in PATH"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        subprocess.run(['ffprobe', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

class AnalysisThread(QThread):
    update_progress = pyqtSignal(int, str)
    analysis_complete = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    preview_generated = pyqtSignal(QPixmap)  # Changed to emit QPixmap
    metadata_extracted = pyqtSignal(dict)

    def __init__(self, video_path, settings):
        super().__init__()
        self.video_path = video_path
        self.settings = settings
        self.temp_dir = tempfile.mkdtemp(prefix="ghost_scanner_")
        self.video_details = {}

    def run(self):
        try:
            report = {
                'filename': os.path.basename(self.video_path),
                'timestamp': datetime.now().isoformat(),
                'audio_matches': [],
                'visual_matches': [],
                'metadata_issues': [],
                'quality_issues': [],
                'overall_risk': 'low',
                'video_details': {}
            }

            # Step 1: Extract metadata
            self.update_progress.emit(5, "Extracting metadata...")
            metadata = self.extract_metadata()
            self.metadata_extracted.emit(metadata)
            report['video_details'] = metadata
            self.video_details = metadata
            
            # Add metadata issues
            if metadata.get('duration', 0) > 600:  # 10 minutes
                report['metadata_issues'].append('Long video (>10 min) increases copyright risk')
            if metadata.get('video_codec', '') != 'h264':
                report['metadata_issues'].append(f"Codec {metadata.get('video_codec')} may have compatibility issues")
            if metadata.get('width', 0) < 1280 or metadata.get('height', 0) < 720:
                report['quality_issues'].append('Resolution below 720p may impact quality')
            
            # Step 2: Generate preview thumbnail
            self.update_progress.emit(10, "Generating preview...")
            preview_path = os.path.join(self.temp_dir, "preview.jpg")
            self.generate_preview(preview_path)
            
            # Load the preview as QPixmap
            pixmap = QPixmap(preview_path)
            if not pixmap.isNull():
                self.preview_generated.emit(pixmap)
            
            # Step 3: Analyze audio
            self.update_progress.emit(20, "Analyzing audio content...")
            audio_issues = self.analyze_audio()
            report['audio_matches'].extend(audio_issues)
            
            # Step 4: Analyze video
            self.update_progress.emit(60, "Analyzing visual content...")
            visual_issues = self.analyze_video()
            report['visual_matches'].extend(visual_issues)
            
            # Step 5: Determine risk level
            self.update_progress.emit(90, "Assessing risk level...")
            total_issues = len(report['audio_matches']) + len(report['visual_matches']) + len(report['metadata_issues'])
            if total_issues > 5:
                report['overall_risk'] = 'high'
            elif total_issues > 2:
                report['overall_risk'] = 'medium'
            else:
                report['overall_risk'] = 'low'
            
            # Add a summary of findings
            report['summary'] = (
                f"Found {len(report['audio_matches'])} audio issues, "
                f"{len(report['visual_matches'])} visual issues, "
                f"{len(report['metadata_issues'])} metadata issues, and "
                f"{len(report['quality_issues'])} quality issues."
            )
            
            self.update_progress.emit(100, "Analysis complete")
            self.analysis_complete.emit(report)
            
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            # Clean up temporary files when thread finishes
            QTimer.singleShot(30000, lambda: self.cleanup_temp_dir())
            
    def cleanup_temp_dir(self):
        """Clean up temporary directory after a delay"""
        try:
            for filename in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            os.rmdir(self.temp_dir)
        except Exception as e:
            print(f"Error cleaning temp dir: {e}")

    def extract_metadata(self):
        """Extract video metadata using FFprobe"""
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', self.video_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            # Extract relevant metadata
            metadata = {
                'format': data['format']['format_name'],
                'duration': float(data['format']['duration']),
                'size': int(data['format']['size']),
                'bitrate': int(data['format']['bit_rate']) if 'bit_rate' in data['format'] else 0
            }
            
            # Extract video stream info
            for stream in data['streams']:
                if stream['codec_type'] == 'video':
                    metadata.update({
                        'width': stream.get('width', 0),
                        'height': stream.get('height', 0),
                        'video_codec': stream.get('codec_name', ''),
                        'frame_rate': eval(stream.get('r_frame_rate', '0/0')) if '/' in stream.get('r_frame_rate', '0/0') else 0,
                        'pixel_format': stream.get('pix_fmt', '')
                    })
                elif stream['codec_type'] == 'audio':
                    metadata.update({
                        'audio_codec': stream.get('codec_name', ''),
                        'sample_rate': stream.get('sample_rate', '0'),
                        'channels': stream.get('channels', 0)
                    })
            
            return metadata
        except Exception as e:
            self.error_occurred.emit(f"Metadata extraction failed: {str(e)}")
            return {}

    def generate_preview(self, output_path):
        """Generate a preview thumbnail from the video"""
        # Extract frame at 25% of the video duration
        duration = self.video_details.get('duration', 10)
        cmd = [
            'ffmpeg', '-i', self.video_path, '-ss', 
            str(duration * 0.25),
            '-vframes', '1', '-q:v', '2', output_path
        ]
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            
            # Create a smaller version for UI display
            preview_img = Image.open(output_path)
            preview_img.thumbnail((400, 400))
            preview_img.save(output_path, "JPEG")
        except Exception as e:
            print(f"Preview generation failed: {e}")
            # Create a blank image as fallback
            img = Image.new('RGB', (400, 300), color=(50, 50, 50))
            img.save(output_path, "JPEG")

    def analyze_audio(self):
        """Analyze audio content for potential copyright issues"""
        issues = []
        
        # Extract audio to WAV
        audio_path = os.path.join(self.temp_dir, "audio.wav")
        cmd = [
            'ffmpeg', '-i', self.video_path, '-vn', '-acodec', 'pcm_s16le',
            '-ar', '44100', '-ac', '1', audio_path
        ]
        try:
            subprocess.run(cmd, capture_output=True, check=True)
        except Exception as e:
            return [{
                'type': 'extraction',
                'description': f'Audio extraction failed: {str(e)}',
                'severity': 'high'
            }]
        
        # Analyze audio using librosa
        try:
            y, sr = librosa.load(audio_path)
            
            # Detect silent portions
            non_silent = librosa.effects.split(y, top_db=30)
            silent_duration = (len(y) - sum(end-start for start, end in non_silent)) / sr
            if silent_duration > 10:  # More than 10 seconds of silence
                issues.append({
                    'type': 'silence',
                    'description': f'Long periods of silence detected ({silent_duration:.1f}s)',
                    'severity': 'medium'
                })
            
            # Detect loudness issues
            rms = librosa.feature.rms(y=y)
            avg_rms = np.mean(rms)
            if avg_rms > 0.3:
                issues.append({
                    'type': 'loudness',
                    'description': f'High audio levels detected (RMS: {avg_rms:.2f})',
                    'severity': 'low'
                })
            elif avg_rms < 0.05:
                issues.append({
                    'type': 'loudness',
                    'description': f'Low audio levels detected (RMS: {avg_rms:.2f})',
                    'severity': 'medium'
                })
            
            # Detect potential music (simplified)
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            chroma_mean = np.mean(chroma)
            if chroma_mean > 0.3:
                issues.append({
                    'type': 'music',
                    'description': 'Potential background music detected',
                    'severity': 'high',
                    'note': 'Check for copyrighted music'
                })
                
        except Exception as e:
            issues.append({
                'type': 'analysis',
                'description': f'Audio analysis error: {str(e)}',
                'severity': 'high'
            })
        
        return issues

    def analyze_video(self):
        """Analyze video content for potential copyright issues"""
        issues = []
        
        # Open the video file
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            return [{
                'type': 'access',
                'description': 'Could not open video file',
                'severity': 'high'
            }]
            
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = frame_count / fps
        
        # Analyze every nth frame (based on analysis depth)
        frame_skip = max(1, int(frame_count / (50 * self.settings['analysis_depth'])))
        
        # Variables for analysis
        black_frames = 0
        aspect_ratio_issues = 0
        watermark_detected = False
        previous_frame = None
        
        for i in range(0, frame_count, frame_skip):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if not ret:
                break
                
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect black frames
            if np.mean(gray) < 10:
                black_frames += 1
            
            # Detect aspect ratio issues
            h, w = frame.shape[:2]
            ar = w / h
            if ar < 1.7 or ar > 1.9:  # Check if not ~16:9
                aspect_ratio_issues += 1
            
            # Simple watermark detection (check corners)
            if self.settings.get('watermark_detection', True):
                corners = [
                    gray[10:60, 10:60],      # Top-left
                    gray[10:60, w-60:w-10],  # Top-right
                    gray[h-60:h-10, 10:60],  # Bottom-left
                    gray[h-60:h-10, w-60:w-10]  # Bottom-right
                ]
                
                for corner in corners:
                    if np.mean(corner) < 50 and np.std(corner) < 15:
                        watermark_detected = True
                        break
            
            # Detect static elements (comparing to previous frame)
            if previous_frame is not None:
                diff = cv2.absdiff(gray, previous_frame)
                if np.mean(diff) < 5:  # Very small difference
                    issues.append({
                        'type': 'static',
                        'description': 'Static content detected',
                        'severity': 'medium',
                        'timestamp': f"{i/fps:.1f}s"
                    })
            previous_frame = gray.copy()
        
        # Close video capture
        cap.release()
        
        # Compile results
        if black_frames > 5:
            issues.append({
                'type': 'black',
                'description': f'Multiple black frames detected ({black_frames})',
                'severity': 'low'
            })
            
        if aspect_ratio_issues > 10:
            issues.append({
                'type': 'aspect',
                'description': 'Non-standard aspect ratio detected',
                'severity': 'low'
            })
            
        if watermark_detected:
            issues.append({
                'type': 'watermark',
                'description': 'Potential watermark detected',
                'severity': 'high',
                'note': 'May indicate copyrighted content'
            })
        
        return issues

class AnimatedHeader(QLabel):
    """An animated header widget with gradient effect"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("Arial", 18, QFont.Bold))
        self.setMinimumHeight(80)
        self.animation_value = 0
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(50)  # Update every 50ms
        
    def update_animation(self):
        self.animation_value = (self.animation_value + 2) % 360
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create animated gradient
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, QColor(40, 40, 60))  # Dark blue
        gradient.setColorAt(0.5, QColor(70, 30, 100))  # Purple
        gradient.setColorAt(1, QColor(40, 40, 60))  # Dark blue
        
        # Draw background
        painter.fillRect(self.rect(), QBrush(gradient))
        
        # Draw text
        painter.setPen(QColor(220, 220, 255))  # Light purple text
        painter.setFont(self.font())
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())
        
        # Draw animated highlights
        highlight_pos = self.animation_value / 360.0
        highlight = QLinearGradient(0, 0, self.width(), 0)
        highlight.setColorAt(max(0, highlight_pos - 0.1), QColor(255, 255, 255, 0))
        highlight.setColorAt(highlight_pos, QColor(180, 180, 255, 120))  # Light purple highlight
        highlight.setColorAt(min(1, highlight_pos + 0.1), QColor(255, 255, 255, 0))
        painter.fillRect(self.rect(), QBrush(highlight))

class GhostYouTubeScanner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ghost YouTube Scanner")
        self.setGeometry(100, 100, 1200, 800)
        self.current_theme = "dark"  # Default theme
        self.apply_stylesheet()
        
        # Initialize settings
        self.settings = {
            'analysis_depth': 2,  # 1=Quick, 2=Standard, 3=Thorough
            'audio_sensitivity': 0.7,
            'visual_sensitivity': 0.7,
            'watermark_detection': True
        }
        
        # Check for FFmpeg
        self.ffmpeg_available = check_ffmpeg()
        if not self.ffmpeg_available:
            QMessageBox.warning(None, "FFmpeg Missing", 
                               "FFmpeg is not installed or not in PATH. Some features may not work properly.\n"
                               "Please install FFmpeg for full functionality.")
        
        # Initialize UI
        self.init_ui()
        
        # Analysis thread
        self.analysis_thread = None
        self.file_path = None
        self.temp_files = []
        
        # Set app icon
        self.setWindowIcon(self.create_app_icon())
        
    def create_app_icon(self):
        """Create a ghost-themed app icon"""
        # Create a simple ghost icon programmatically
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = Image.new('RGBA', (64, 64))
        
        # Draw ghost body (semi-circle with wavy bottom)
        for i in range(64):
            for j in range(64):
                # Ghost body (semi-circle)
                dist = ((i-32)**2 + (j-16)**2)**0.5
                if dist < 15 and j > 16:
                    draw.putpixel((i, j), (200, 200, 255, 255))
                
                # Wavy bottom
                wave = abs(int(5 * np.sin(i/5)) - 2)
                if 15 < dist < 18 and j > 30 - wave:
                    draw.putpixel((i, j), (200, 200, 255, 255))
        
        # Draw eyes
        for x, y in [(25, 20), (39, 20)]:
            for i in range(x-3, x+4):
                for j in range(y-3, y+4):
                    if ((i-x)**2 + (j-y)**2) < 9:
                        draw.putpixel((i, j), (30, 30, 60, 255))
        
        img = Image.alpha_composite(img, draw)
        img.save("ghost_icon.png")
        return QIcon("ghost_icon.png")
    
    def apply_stylesheet(self):
        """Apply stylesheet based on current theme"""
        if self.current_theme == "dark":
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1a1a2e;
                }
                QWidget {
                    background-color: #1a1a2e;
                    color: #e0e0e0;
                }
                QGroupBox {
                    border: 1px solid #4a4a6e;
                    border-radius: 6px;
                    margin-top: 15px;
                    padding-top: 20px;
                    font-weight: bold;
                    color: #f0f0f0;
                    background-color: #2a2a4e;
                }
                QPushButton {
                    background-color: #4a4a6e;
                    color: white;
                    border: 1px solid #5a5a8e;
                    border-radius: 4px;
                    padding: 8px 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5a5a8e;
                }
                QPushButton:pressed {
                    background-color: #3a3a5e;
                }
                #analyzeButton {
                    background-color: #6a0dad;
                }
                #analyzeButton:hover {
                    background-color: #7b1fa2;
                }
                #analyzeButton:pressed {
                    background-color: #5a0c9d;
                }
                #exportButton {
                    background-color: #27ae60;
                }
                #exportButton:hover {
                    background-color: #2ecc71;
                }
                QProgressBar {
                    border: 1px solid #4a4a6e;
                    border-radius: 4px;
                    background-color: #2a2a4e;
                    text-align: center;
                    color: #e0e0e0;
                }
                QProgressBar::chunk {
                    background-color: #7b1fa2;
                }
                QTextEdit, QListWidget {
                    background-color: #2a2a4e;
                    border: 1px solid #4a4a6e;
                    border-radius: 4px;
                    padding: 8px;
                    color: #e0e0e0;
                }
                QTabWidget::pane {
                    border: 1px solid #4a4a6e;
                    border-radius: 0 6px 6px 6px;
                    background-color: #2a2a4e;
                }
                QTabBar::tab {
                    padding: 8px 15px;
                    border: 1px solid #4a4a6e;
                    border-bottom: none;
                    border-radius: 6px 6px 0 0;
                    background: #4a4a6e;
                    color: #e0e0e0;
                }
                QTabBar::tab:selected {
                    background: #2a2a4e;
                    border-bottom: 1px solid #2a2a4e;
                    margin-bottom: -1px;
                }
                QTabBar::tab:hover {
                    background: #5a5a8e;
                }
                QLabel#previewLabel {
                    border: 2px solid #5a5a8e;
                    border-radius: 4px;
                    background-color: #22223a;
                }
                QLabel#riskLabel {
                    font-weight: bold;
                    font-size: 16px;
                    border-radius: 8px;
                    padding: 10px;
                }
                QMenu {
                    background-color: #2a2a4e;
                    border: 1px solid #4a4a6e;
                    color: #e0e0e0;
                }
                QMenu::item:selected {
                    background-color: #5a5a8e;
                }
                QFrame#footer {
                    background-color: #2a2a4e;
                    border-top: 1px solid #4a4a6e;
                }
                QToolButton {
                    background-color: transparent;
                    color: #a0a0ff;
                    border: none;
                    padding: 5px;
                }
                QToolButton:hover {
                    color: #ffffff;
                    text-decoration: underline;
                }
            """)
        else:  # Light theme
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f0f0f5;
                }
                QWidget {
                    background-color: #f0f0f5;
                    color: #333;
                }
                QGroupBox {
                    border: 1px solid #d0d0e0;
                    border-radius: 6px;
                    margin-top: 15px;
                    padding-top: 20px;
                    font-weight: bold;
                    color: #333;
                    background-color: #f8f8ff;
                }
                QPushButton {
                    background-color: #e0e0ff;
                    color: #333;
                    border: 1px solid #d0d0e0;
                    border-radius: 4px;
                    padding: 8px 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #d0d0f0;
                }
                QPushButton:pressed {
                    background-color: #c0c0e0;
                }
                #analyzeButton {
                    background-color: #6a0dad;
                    color: white;
                }
                #analyzeButton:hover {
                    background-color: #7b1fa2;
                }
                #analyzeButton:pressed {
                    background-color: #5a0c9d;
                }
                #exportButton {
                    background-color: #27ae60;
                    color: white;
                }
                #exportButton:hover {
                    background-color: #2ecc71;
                }
                QProgressBar {
                    border: 1px solid #d0d0e0;
                    border-radius: 4px;
                    background-color: #f8f8ff;
                    text-align: center;
                    color: #333;
                }
                QProgressBar::chunk {
                    background-color: #7b1fa2;
                }
                QTextEdit, QListWidget {
                    background-color: white;
                    border: 1px solid #d0d0e0;
                    border-radius: 4px;
                    padding: 8px;
                    color: #333;
                }
                QTabWidget::pane {
                    border: 1px solid #d0d0e0;
                    border-radius: 0 6px 6px 6px;
                    background-color: white;
                }
                QTabBar::tab {
                    padding: 8px 15px;
                    border: 1px solid #d0d0e0;
                    border-bottom: none;
                    border-radius: 6px 6px 0 0;
                    background: #e0e0ff;
                    color: #333;
                }
                QTabBar::tab:selected {
                    background: white;
                    border-bottom: 1px solid white;
                    margin-bottom: -1px;
                }
                QTabBar::tab:hover {
                    background: #d0d0f0;
                }
                QLabel#previewLabel {
                    border: 2px solid #d0d0e0;
                    border-radius: 4px;
                    background-color: #f8f8ff;
                }
                QLabel#riskLabel {
                    font-weight: bold;
                    font-size: 16px;
                    border-radius: 8px;
                    padding: 10px;
                }
                QFrame#footer {
                    background-color: #e0e0ff;
                    border-top: 1px solid #d0d0e0;
                }
                QToolButton {
                    background-color: transparent;
                    color: #4a4a8e;
                    border: none;
                    padding: 5px;
                }
                QToolButton:hover {
                    color: #0000ff;
                    text-decoration: underline;
                }
            """)
        
    def init_ui(self):
        # Create menu bar
        self.create_menu()
        
        # Main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)
        
        # Animated header
        self.header = AnimatedHeader("Ghost YouTube Scanner")
        self.layout.addWidget(self.header)
        
        # Create splitter for main content
        splitter = QSplitter(Qt.Horizontal)
        self.layout.addWidget(splitter, 1)
        
        # Left panel (preview and controls)
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        # Preview group
        preview_group = QGroupBox("Video Preview")
        preview_layout = QVBoxLayout()
        
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setObjectName("previewLabel")
        self.preview_label.setMinimumSize(400, 300)
        self.preview_label.setText("No video selected")
        self.preview_label.setFont(QFont("Arial", 12))
        preview_layout.addWidget(self.preview_label)
        
        # Video info
        self.video_info = QTextEdit()
        self.video_info.setReadOnly(True)
        self.video_info.setMaximumHeight(100)
        preview_layout.addWidget(self.video_info)
        
        preview_group.setLayout(preview_layout)
        left_layout.addWidget(preview_group)
        
        # Settings group
        settings_group = QGroupBox("Analysis Settings")
        settings_layout = QVBoxLayout()
        
        # Analysis depth
        depth_layout = QHBoxLayout()
        depth_layout.addWidget(QLabel("Analysis Depth:"))
        self.depth_combo = QComboBox()
        self.depth_combo.addItems(["Quick", "Standard", "Thorough"])
        self.depth_combo.setCurrentIndex(1)
        self.depth_combo.currentIndexChanged.connect(
            lambda idx: self.settings.update({'analysis_depth': idx+1})
        )
        depth_layout.addWidget(self.depth_combo)
        settings_layout.addLayout(depth_layout)
        
        # Sensitivity settings
        audio_layout = QHBoxLayout()
        audio_layout.addWidget(QLabel("Audio Sensitivity:"))
        self.audio_slider = QDoubleSpinBox()
        self.audio_slider.setRange(0.1, 1.0)
        self.audio_slider.setSingleStep(0.1)
        self.audio_slider.setValue(0.7)
        self.audio_slider.valueChanged.connect(
            lambda val: self.settings.update({'audio_sensitivity': val})
        )
        audio_layout.addWidget(self.audio_slider)
        settings_layout.addLayout(audio_layout)
        
        visual_layout = QHBoxLayout()
        visual_layout.addWidget(QLabel("Visual Sensitivity:"))
        self.visual_slider = QDoubleSpinBox()
        self.visual_slider.setRange(0.1, 1.0)
        self.visual_slider.setSingleStep(0.1)
        self.visual_slider.setValue(0.7)
        self.visual_slider.valueChanged.connect(
            lambda val: self.settings.update({'visual_sensitivity': val})
        )
        visual_layout.addWidget(self.visual_slider)
        settings_layout.addLayout(visual_layout)
        
        # Watermark detection
        self.watermark_check = QCheckBox("Enhanced Watermark Detection")
        self.watermark_check.setChecked(True)
        self.watermark_check.stateChanged.connect(
            lambda state: self.settings.update({'watermark_detection': state == Qt.Checked})
        )
        settings_layout.addWidget(self.watermark_check)
        
        settings_group.setLayout(settings_layout)
        left_layout.addWidget(settings_group)
        
        # Control group
        control_group = QWidget()
        control_layout = QHBoxLayout()
        
        self.browse_btn = QPushButton("Browse Video...")
        self.browse_btn.clicked.connect(self.browse_file)
        
        self.analyze_btn = QPushButton("Analyze Video")
        self.analyze_btn.setObjectName("analyzeButton")
        self.analyze_btn.clicked.connect(self.start_analysis)
        self.analyze_btn.setEnabled(False)
        
        self.export_btn = QPushButton("Export Report")
        self.export_btn.setObjectName("exportButton")
        self.export_btn.clicked.connect(self.export_report)
        self.export_btn.setEnabled(False)
        
        control_layout.addWidget(self.browse_btn)
        control_layout.addWidget(self.analyze_btn)
        control_layout.addWidget(self.export_btn)
        control_group.setLayout(control_layout)
        left_layout.addWidget(control_group)
        
        # Add left panel to splitter
        splitter.addWidget(left_panel)
        
        # Right panel (results)
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Ready")
        self.progress_bar.setMinimumHeight(30)
        right_layout.addWidget(self.progress_bar)
        
        # Risk indicator
        self.risk_label = QLabel("Overall Risk: Not Analyzed")
        self.risk_label.setAlignment(Qt.AlignCenter)
        self.risk_label.setObjectName("riskLabel")
        right_layout.addWidget(self.risk_label)
        
        # Results tabs
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        
        # Summary tab
        self.summary_tab = QWidget()
        self.summary_layout = QVBoxLayout()
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_layout.addWidget(self.summary_text)
        self.summary_tab.setLayout(self.summary_layout)
        
        # Audio issues tab
        self.audio_tab = QWidget()
        self.audio_layout = QVBoxLayout()
        self.audio_list = QListWidget()
        self.audio_layout.addWidget(self.audio_list)
        self.audio_tab.setLayout(self.audio_layout)
        
        # Visual issues tab
        self.visual_tab = QWidget()
        self.visual_layout = QVBoxLayout()
        self.visual_list = QListWidget()
        self.visual_layout.addWidget(self.visual_list)
        self.visual_tab.setLayout(self.visual_layout)
        
        # Metadata tab
        self.metadata_tab = QWidget()
        self.metadata_layout = QVBoxLayout()
        self.metadata_list = QListWidget()
        self.metadata_layout.addWidget(self.metadata_list)
        self.metadata_tab.setLayout(self.metadata_layout)
        
        # Quality tab
        self.quality_tab = QWidget()
        self.quality_layout = QVBoxLayout()
        self.quality_list = QListWidget()
        self.quality_layout.addWidget(self.quality_list)
        self.quality_tab.setLayout(self.quality_layout)
        
        # Add tabs
        self.tabs.addTab(self.summary_tab, "Summary")
        self.tabs.addTab(self.audio_tab, "Audio Issues")
        self.tabs.addTab(self.visual_tab, "Visual Issues")
        self.tabs.addTab(self.metadata_tab, "Metadata")
        self.tabs.addTab(self.quality_tab, "Quality")
        
        right_layout.addWidget(self.tabs, 1)
        
        # Add right panel to splitter
        splitter.addWidget(right_panel)
        
        # Set initial splitter sizes
        splitter.setSizes([400, 800])
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Create footer with channel links
        footer = QFrame()
        footer.setObjectName("footer")
        footer.setFrameShape(QFrame.StyledPanel)
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(10, 5, 10, 5)
        
        # Add channel links
        channels = [
            ("YouTube", "https://www.youtube.com/@sigma_ghost_hacking"),
            ("Telegram", "https://web.telegram.org/k/#@Sigma_Ghost"),
            ("GitHub", "https://github.com/sigma-cyber-ghost")
        ]
        
        for name, url in channels:
            btn = QToolButton()
            btn.setText(name)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, u=url: QDesktopServices.openUrl(QUrl(u)))
            footer_layout.addWidget(btn)
        
        footer_layout.addStretch()
        
        # Add a ghost icon
        ghost_icon = QLabel()
        pixmap = QPixmap("ghost_icon.png").scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        ghost_icon.setPixmap(pixmap)
        footer_layout.addWidget(ghost_icon)
        
        footer.setLayout(footer_layout)
        self.layout.addWidget(footer)
    
    def create_menu(self):
        """Create the menu bar"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        open_action = QAction("&Open Video", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.browse_file)
        file_menu.addAction(open_action)
        
        export_action = QAction("&Export Report", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_report)
        file_menu.addAction(export_action)
        
        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menu_bar.addMenu("&View")
        
        theme_menu = view_menu.addMenu("&Theme")
        dark_action = QAction("&Dark", self)
        dark_action.triggered.connect(lambda: self.set_theme("dark"))
        theme_menu.addAction(dark_action)
        
        light_action = QAction("&Light", self)
        light_action.triggered.connect(lambda: self.set_theme("light"))
        theme_menu.addAction(light_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def set_theme(self, theme):
        """Set the application theme"""
        self.current_theme = theme
        self.apply_stylesheet()
        
        # Update UI elements that need manual restyling
        if theme == "dark":
            self.risk_label.setStyleSheet("""
                background-color: #555;
                color: #e0e0e0;
            """)
        else:
            self.risk_label.setStyleSheet("""
                background-color: #e0e0e0;
                color: #333;
            """)
    
    def browse_file(self):
        """Browse for a video file"""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Video File", "", 
            "Video Files (*.mp4 *.mov *.avi *.mkv *.flv *.webm);;All Files (*)", 
            options=options
        )
        
        if file_path:
            self.file_path = file_path
            self.status_bar.showMessage(f"Selected: {os.path.basename(file_path)}")
            self.analyze_btn.setEnabled(True)
            
            # Show a loading indicator
            self.preview_label.setText("Loading preview...")
            
            # Start a thread to get a preview
            self.start_preview_generation(file_path)
    
    def start_preview_generation(self, file_path):
        """Start a thread to generate preview and metadata"""
        # Create a thread for preview generation
        self.preview_thread = QThread()
        self.preview_worker = PreviewWorker(file_path)
        self.preview_worker.moveToThread(self.preview_thread)
        
        # Connect signals
        self.preview_thread.started.connect(self.preview_worker.generate_preview)
        self.preview_worker.preview_generated.connect(self.show_preview)
        self.preview_worker.metadata_extracted.connect(self.show_metadata)
        self.preview_worker.finished.connect(self.preview_thread.quit)
        self.preview_worker.finished.connect(self.preview_worker.deleteLater)
        self.preview_thread.finished.connect(self.preview_thread.deleteLater)
        
        # Start the thread
        self.preview_thread.start()
    
    def show_preview(self, pixmap):
        """Show the preview image"""
        if pixmap and not pixmap.isNull():
            self.preview_label.setPixmap(pixmap.scaled(
                self.preview_label.width(), 
                self.preview_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
        else:
            self.preview_label.setText("Preview not available")
    
    def show_metadata(self, metadata):
        """Display video metadata"""
        if not metadata:
            self.video_info.setText("Metadata not available")
            return
            
        info_text = (
            f"<b>File:</b> {os.path.basename(self.file_path)}<br>"
            f"<b>Duration:</b> {metadata.get('duration', 0):.2f} seconds<br>"
            f"<b>Resolution:</b> {metadata.get('width', 0)}x{metadata.get('height', 0)}<br>"
            f"<b>Video Codec:</b> {metadata.get('video_codec', 'N/A')}<br>"
            f"<b>Audio Codec:</b> {metadata.get('audio_codec', 'N/A')}"
        )
        self.video_info.setText(info_text)
    
    def start_analysis(self):
        """Start the video analysis"""
        if not self.file_path:
            QMessageBox.warning(self, "No File Selected", "Please select a video file first.")
            return
            
        # Clear previous results
        self.summary_text.clear()
        self.audio_list.clear()
        self.visual_list.clear()
        self.metadata_list.clear()
        self.quality_list.clear()
        self.risk_label.setText("Analyzing...")
        self.export_btn.setEnabled(False)
        
        # Disable analyze button during analysis
        self.analyze_btn.setEnabled(False)
        
        # Start analysis thread
        self.analysis_thread = AnalysisThread(self.file_path, self.settings)
        self.analysis_thread.update_progress.connect(self.update_progress)
        self.analysis_thread.analysis_complete.connect(self.display_results)
        self.analysis_thread.error_occurred.connect(self.handle_error)
        self.analysis_thread.preview_generated.connect(self.show_preview)
        self.analysis_thread.metadata_extracted.connect(self.show_metadata)
        self.analysis_thread.finished.connect(self.analysis_finished)
        self.analysis_thread.start()
        
    def update_progress(self, value, message):
        self.progress_bar.setValue(value)
        self.progress_bar.setFormat(message)
        self.status_bar.showMessage(message)
        
    def display_results(self, report):
        """Display the analysis results"""
        # Update risk indicator
        risk_text = f"Overall Risk: {report['overall_risk'].upper()}"
        if report['overall_risk'] == 'high':
            risk_color = "#e74c3c"
        elif report['overall_risk'] == 'medium':
            risk_color = "#f39c12"
        else:
            risk_color = "#2ecc71"
            
        self.risk_label.setText(risk_text)
        self.risk_label.setStyleSheet(f"""
            background-color: {risk_color};
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 10px;
        """)
        
        # Update summary
        summary_html = f"""
        <h2>Copyright Analysis Report</h2>
        <p><b>File:</b> {report['filename']}</p>
        <p><b>Analysis date:</b> {report['timestamp']}</p>
        <p><b>Overall risk:</b> <span style="color: {risk_color}; font-weight: bold;">{report['overall_risk'].upper()}</span></p>
        <p>{report.get('summary', '')}</p>
        <hr>
        """
        
        if report['audio_matches']:
            summary_html += "<h3>Audio Issues:</h3><ul>"
            for issue in report['audio_matches']:
                severity = issue.get('severity', 'medium')
                severity_color = "#e74c3c" if severity == 'high' else "#f39c12" if severity == 'medium' else "#2ecc71"
                summary_html += f"<li><span style='color: {severity_color};'>{severity.upper()}</span>: {issue['description']}"
                if 'note' in issue:
                    summary_html += f" - {issue['note']}"
                summary_html += "</li>"
            summary_html += "</ul>"
            
        if report['visual_matches']:
            summary_html += "<h3>Visual Issues:</h3><ul>"
            for issue in report['visual_matches']:
                severity = issue.get('severity', 'medium')
                severity_color = "#e74c3c" if severity == 'high' else "#f39c12" if severity == 'medium' else "#2ecc71"
                summary_html += f"<li><span style='color: {severity_color};'>{severity.upper()}</span>: {issue['description']}"
                if 'note' in issue:
                    summary_html += f" - {issue['note']}"
                if 'timestamp' in issue:
                    summary_html += f" at {issue['timestamp']}"
                summary_html += "</li>"
            summary_html += "</ul>"
            
        if report['metadata_issues']:
            summary_html += "<h3>Metadata Issues:</h3><ul>"
            for issue in report['metadata_issues']:
                summary_html += f"<li>{issue}</li>"
            summary_html += "</ul>"
            
        if report['quality_issues']:
            summary_html += "<h3>Quality Issues:</h3><ul>"
            for issue in report['quality_issues']:
                summary_html += f"<li>{issue}</li>"
            summary_html += "</ul>"
            
        self.summary_text.setHtml(summary_html)
        
        # Add detailed issues to tabs
        for issue in report['audio_matches']:
            severity = issue.get('severity', 'medium')
            item_text = f"[{severity.upper()}] {issue['description']}"
            if 'note' in issue:
                item_text += f" - {issue['note']}"
            self.audio_list.addItem(item_text)
            
        for issue in report['visual_matches']:
            severity = issue.get('severity', 'medium')
            item_text = f"[{severity.upper()}] {issue['description']}"
            if 'note' in issue:
                item_text += f" - {issue['note']}"
            if 'timestamp' in issue:
                item_text += f" at {issue['timestamp']}"
            self.visual_list.addItem(item_text)
            
        for issue in report['metadata_issues']:
            self.metadata_list.addItem(issue)
            
        for issue in report['quality_issues']:
            self.quality_list.addItem(issue)
            
        # Enable export button
        self.export_btn.setEnabled(True)
        
    def handle_error(self, error_msg):
        QMessageBox.critical(self, "Analysis Error", f"An error occurred during analysis:\n\n{error_msg}")
        self.analysis_finished()
        self.risk_label.setText("Analysis Failed")
        self.risk_label.setStyleSheet("""
            background-color: #7f8c8d;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 10px;
        """)
        
    def analysis_finished(self):
        self.analyze_btn.setEnabled(True)
        self.progress_bar.setFormat("Analysis complete")
        self.status_bar.showMessage("Analysis complete")
    
    def export_report(self):
        """Export the analysis report to a file"""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Report", "", 
            "Text Files (*.txt);;HTML Files (*.html);;All Files (*)", 
            options=options
        )
        
        if file_path:
            try:
                # Get the current report text from the summary tab
                report_text = self.summary_text.toHtml() if file_path.endswith('.html') else self.summary_text.toPlainText()
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report_text)
                    
                QMessageBox.information(self, "Export Successful", f"Report saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to save report:\n{str(e)}")
    
    def show_about(self):
        """Show the about dialog"""
        about_text = (
            "<h2>Ghost YouTube Scanner</h2>"
            "<p><b>Version:</b> 2.0</p>"
            "<p><b>Description:</b> Professional tool for detecting potential copyright issues in videos before uploading to YouTube.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Audio analysis for music and loudness issues</li>"
            "<li>Visual analysis for watermarks and quality issues</li>"
            "<li>Metadata inspection</li>"
            "<li>Risk assessment report</li>"
            "<li>Exportable results</li>"
            "</ul>"
            "<p><b>Note:</b> This tool provides pre-upload guidance only and does not guarantee copyright clearance.</p>"
            "<hr>"
            "<h3>Sigma Ghost Channels</h3>"
            "<p>"
            "<a href='https://www.youtube.com/@sigma_ghost_hacking'>YouTube</a> | "
            "<a href='https://web.telegram.org/k/#@Sigma_Ghost'>Telegram</a> | "
            "<a href='https://github.com/sigma-cyber-ghost'>GitHub</a>"
            "</p>"
        )
        
        msg = QMessageBox()
        msg.setWindowTitle("About Ghost YouTube Scanner")
        msg.setTextFormat(Qt.RichText)
        msg.setText(about_text)
        msg.exec_()
        
    def closeEvent(self, event):
        if self.analysis_thread and self.analysis_thread.isRunning():
            reply = QMessageBox.question(
                self, 'Analysis in Progress',
                "An analysis is currently running. Are you sure you want to quit?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.analysis_thread.terminate()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

class PreviewWorker(QThread):
    preview_generated = pyqtSignal(QPixmap)
    metadata_extracted = pyqtSignal(dict)
    finished = pyqtSignal()
    
    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        
    def generate_preview(self):
        """Generate a preview and metadata for the video"""
        try:
            # Extract metadata
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', self.video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            # Extract relevant metadata
            metadata = {
                'format': data['format']['format_name'],
                'duration': float(data['format']['duration']),
                'size': int(data['format']['size']),
                'bitrate': int(data['format']['bit_rate']) if 'bit_rate' in data['format'] else 0
            }
            
            # Extract video stream info
            for stream in data['streams']:
                if stream['codec_type'] == 'video':
                    metadata.update({
                        'width': stream.get('width', 0),
                        'height': stream.get('height', 0),
                        'video_codec': stream.get('codec_name', ''),
                        'frame_rate': eval(stream.get('r_frame_rate', '0/0')) if '/' in stream.get('r_frame_rate', '0/0') else 0,
                        'pixel_format': stream.get('pix_fmt', '')
                    })
                elif stream['codec_type'] == 'audio':
                    metadata.update({
                        'audio_codec': stream.get('codec_name', ''),
                        'sample_rate': stream.get('sample_rate', '0'),
                        'channels': stream.get('channels', 0)
                    })
            
            self.metadata_extracted.emit(metadata)
            
            # Generate preview thumbnail
            temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            temp_file.close()
            
            # Extract frame at 25% of the video duration
            cmd = [
                'ffmpeg', '-i', self.video_path, '-ss', 
                str(metadata['duration'] * 0.25),
                '-vframes', '1', '-q:v', '2', temp_file.name
            ]
            subprocess.run(cmd, capture_output=True, check=True)
            
            # Load the preview as QPixmap
            pixmap = QPixmap(temp_file.name)
            
            # Clean up temporary file
            os.unlink(temp_file.name)
            
            if not pixmap.isNull():
                self.preview_generated.emit(pixmap)
            
        except Exception as e:
            print(f"Preview generation error: {e}")
            self.preview_generated.emit(QPixmap())
            self.metadata_extracted.emit({})
        finally:
            self.finished.emit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style and font
    app.setStyle('Fusion')
    font = QFont()
    font.setFamily("Arial")
    font.setPointSize(10)
    app.setFont(font)
    
    window = GhostYouTubeScanner()
    window.show()
    sys.exit(app.exec_())
