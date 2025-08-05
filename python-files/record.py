import sys
import os
import cv2
import numpy
import time
import queue # 用于线程安全的数据传输

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QFont

# --- 依赖库 ---
# pip install sounddevice scipy moviepy Pillow soundfile
import sounddevice as sd
import soundfile as sf
import moviepy.editor as mp
from PIL import ImageGrab 
# --------------------

# 用于捕获视频帧的线程
class ScreenCaptureThread(QThread):
    def __init__(self, frame_queue, parent=None):
        super().__init__(parent)
        self.frame_queue = frame_queue
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            pil_img = ImageGrab.grab()
            rgb_frame = numpy.array(pil_img)
            self.frame_queue.put(rgb_frame)
            self.msleep(35) # ~28 FPS

    def stop(self):
        self.running = False
        print("Screen capture thread stopped.")

# 用于将视频帧写入文件的线程
class VideoWriterThread(QThread):
    def __init__(self, frame_queue, filename, fps, width, height, parent=None):
        super().__init__(parent)
        self.frame_queue = frame_queue
        self.filename = filename
        self.fps = fps
        self.width = width
        self.height = height
        self.running = False

    def run(self):
        self.running = True
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        video_writer = cv2.VideoWriter(self.filename, fourcc, self.fps, (self.width, self.height))

        while self.running:
            try:
                frame = self.frame_queue.get(timeout=1)
                # OpenCV 使用 BGR 格式，因此需要从 RGB 转换为 BGR
                bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                video_writer.write(bgr_frame)
            except queue.Empty:
                # 如果队列中没有数据，则继续等待
                continue
        
        video_writer.release()
        print("Video writer thread finished and file released.")

    def stop(self):
        self.running = False

# 用于将音频直接录制到文件的线程
class AudioRecorderThread(QThread):
    def __init__(self, filename, samplerate=44100, channels=2, parent=None):
        super().__init__(parent)
        self.filename = filename
        self.samplerate = samplerate
        self.channels = channels
        self.running = False

    def run(self):
        self.running = True
        try:
            with sf.SoundFile(self.filename, mode='w', samplerate=self.samplerate, channels=self.channels) as file:
                with sd.InputStream(samplerate=self.samplerate, channels=self.channels) as stream:
                    while self.running:
                        audio_chunk, overflowed = stream.read(self.samplerate) # 1 second chunks
                        if self.running:
                            file.write(audio_chunk)
                        else:
                            break
        except Exception as e:
            print(f"Audio recording error: {e}")
    
    def stop(self):
        self.running = False
        print("Audio recorder thread stopped.")

# 主应用程序窗口
class ScreenRecorder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("专业屏幕录像机")
        self.setGeometry(100, 100, 450, 250)
        # 注意：将字体更改为支持中文的字体，例如 "Microsoft YaHei" 或 "SimHei"
        self.setFont(QFont("Microsoft YaHei", 10))

        # --- UI 设置 ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.status_label = QLabel("准备就绪 (Ready)", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #333; font-size: 16px; font-weight: bold;")
        self.layout.addWidget(self.status_label)
        
        self.time_label = QLabel("00:00:00", self)
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("color: #e74c3c; font-size: 20px; font-weight: bold;")
        self.layout.addWidget(self.time_label)

        self.start_button = QPushButton("开始录制 (Start)", self)
        self.start_button.clicked.connect(self.start_recording)
        self.start_button.setStyleSheet("background-color: #2ecc71; color: white; padding: 12px; border-radius: 8px; font-size: 14px; border: none;")
        self.layout.addWidget(self.start_button)

        self.stop_button = QPushButton("停止录制 (Stop)", self)
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("background-color: #e74c3c; color: white; padding: 12px; border-radius: 8px; font-size: 14px; border: none; QPushButton:disabled { background-color: #95a5a6; }")
        self.layout.addWidget(self.stop_button)

        # --- 录制状态 ---
        self.capture_thread = None
        self.writer_thread = None
        self.audio_thread = None
        self.frame_queue = None
        self.temp_video_file = "temp_video.avi"
        self.temp_audio_file = "temp_audio.wav"
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.record_time_seconds = 0
        self.recording_start_time = 0

    def start_recording(self):
        self.frame_queue = queue.Queue()
        
        # 屏幕尺寸
        screen_size = ImageGrab.grab().size
        width, height = screen_size

        # 线程
        self.capture_thread = ScreenCaptureThread(self.frame_queue)
        self.writer_thread = VideoWriterThread(self.frame_queue, self.temp_video_file, 25.0, width, height)
        self.audio_thread = AudioRecorderThread(self.temp_audio_file)

        self.capture_thread.start()
        self.writer_thread.start()
        self.audio_thread.start()

        self.status_label.setText("正在录制音视频 (Recording...)")
        self.status_label.setStyleSheet("color: #e74c3c; font-size: 16px; font-weight: bold;")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        self.record_time_seconds = 0
        self.time_label.setText("00:00:00")
        self.timer.start(1000)
        self.recording_start_time = time.time()

    def stop_recording(self):
        recording_duration = time.time() - self.recording_start_time

        # 停止所有线程
        if self.capture_thread: self.capture_thread.stop()
        if self.writer_thread: self.writer_thread.stop()
        if self.audio_thread: self.audio_thread.stop()

        # 等待它们完成
        if self.capture_thread: self.capture_thread.wait()
        if self.writer_thread: self.writer_thread.wait()
        if self.audio_thread: self.audio_thread.wait()
        
        self.timer.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        if recording_duration < 1:
            self.status_label.setText("录制时间太短。")
            self.status_label.setStyleSheet("color: #f39c12; font-size: 16px; font-weight: bold;")
            return

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(self, "请选择视频保存位置", "", "MP4 视频 (*.mp4)", options=options)

        if filename:
            if not filename.lower().endswith('.mp4'):
                filename += '.mp4'
            self.merge_files(filename)
        else:
            self.status_label.setText("保存已取消。")
            self.status_label.setStyleSheet("color: #e74c3c; font-size: 16px; font-weight: bold;")
            self.cleanup_temp_files()

    def merge_files(self, final_filename):
        """合并临时的音频和视频文件。"""
        try:
            self.status_label.setText("正在合并视频和音频文件...")
            QApplication.processEvents()

            video_clip = mp.VideoFileClip(self.temp_video_file)
            audio_clip = mp.AudioFileClip(self.temp_audio_file)
            
            amplified_audio_clip = audio_clip.volumex(4.0)
            
            # 根据音频文件的时长调整视频剪辑
            final_clip = video_clip.set_duration(audio_clip.duration).set_audio(amplified_audio_clip)
            
            final_clip.write_videofile(final_filename, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True)
            print("Merging complete.")

            self.status_label.setText(f"视频已保存至 '{final_filename.split('/')[-1]}'")
            self.status_label.setStyleSheet("color: #27ae60; font-size: 14px; font-weight: bold;")

        except Exception as e:
            print(f"An error occurred during merging: {e}")
            self.status_label.setText("错误：合并视频时发生错误。")
            self.status_label.setStyleSheet("color: #e74c3c; font-size: 16px; font-weight: bold;")
        finally:
            # 关闭剪辑并清理
            if 'video_clip' in locals(): video_clip.close()
            if 'audio_clip' in locals(): audio_clip.close()
            self.cleanup_temp_files()

    def cleanup_temp_files(self):
        if os.path.exists(self.temp_video_file):
            os.remove(self.temp_video_file)
            print(f"Removed {self.temp_video_file}")
        if os.path.exists(self.temp_audio_file):
            os.remove(self.temp_audio_file)
            print(f"Removed {self.temp_audio_file}")

    def update_timer(self):
        self.record_time_seconds += 1
        h = self.record_time_seconds // 3600
        m = (self.record_time_seconds % 3600) // 60
        s = self.record_time_seconds % 60
        self.time_label.setText(f"{h:02d}:{m:02d}:{s:02d}")

    def closeEvent(self, event):
        print("Closing application...")
        if self.start_button.isEnabled() is False:
            self.stop_recording()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    recorder = ScreenRecorder()
    recorder.show()
    sys.exit(app.exec_())