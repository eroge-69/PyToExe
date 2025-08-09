import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import QTimer, QTime, QDateTime, Qt

class StopwatchApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stopwatch & Clock")
        self.setGeometry(100, 100, 500, 250)

        # Main layout
        main_layout = QVBoxLayout()

        # Stopwatch label
        self.stopwatch_label = QLabel("00:00:00.000")
        self.stopwatch_label.setAlignment(Qt.AlignCenter)
        self.stopwatch_label.setStyleSheet("font-size: 30pt; color: #333;")
        
        # Labels for start, stop, and current time
        self.current_time_label = QLabel()
        self.current_time_label.setAlignment(Qt.AlignCenter)
        self.current_time_label.setStyleSheet("font-size: 14pt; color: #555; margin-top: 10px;")

        self.start_time_display_label = QLabel("Waktu Mulai: -")
        self.start_time_display_label.setStyleSheet("font-size: 10pt; margin-top: 5px;")

        self.stop_time_display_label = QLabel("Waktu Berhenti: -")
        self.stop_time_display_label.setStyleSheet("font-size: 10pt; margin-top: 5px;")
        
        # Button layout
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.start_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 14pt; padding: 10px;")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setStyleSheet("background-color: #F44336; color: white; font-size: 14pt; padding: 10px;")
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)

        # Add widgets to main layout
        main_layout.addWidget(self.stopwatch_label)
        main_layout.addWidget(self.current_time_label)
        main_layout.addWidget(self.start_time_display_label)
        main_layout.addWidget(self.stop_time_display_label)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)

        # Timer for stopwatch
        self.stopwatch_timer = QTimer(self)
        self.stopwatch_timer.timeout.connect(self.update_stopwatch)
        
        # Timer for current time
        self.current_time_timer = QTimer(self)
        self.current_time_timer.timeout.connect(self.update_current_time)
        self.current_time_timer.start(1000) # Update every second

        # Stopwatch variables
        self.is_running = False
        self.paused_time = 0
        self.start_time_counter = QTime()
        self.start_datetime = None
        self.stop_datetime = None

        # Connect button signals
        self.start_button.clicked.connect(self.start_pause_stopwatch)
        self.stop_button.clicked.connect(self.stop_stopwatch)
        
        self.update_current_time()

    def update_stopwatch(self):
        elapsed_time = self.paused_time + self.start_time_counter.elapsed()
        milliseconds = elapsed_time % 1000
        seconds = int(elapsed_time / 1000)
        minutes = int(seconds / 60)
        hours = int(minutes / 60)
        
        # Format the time
        display_time = f"{hours:02}:{minutes % 60:02}:{seconds % 60:02}.{milliseconds:03}"
        self.stopwatch_label.setText(display_time)
        
    def start_pause_stopwatch(self):
        if not self.is_running:
            if self.stopwatch_label.text() == "00:00:00.000":
                # Only record start time on the first start
                self.start_datetime = QDateTime.currentDateTime()
                formatted_start_time = self.start_datetime.toString("dd-MM-yyyy HH:mm:ss")
                self.start_time_display_label.setText(f"Waktu Mulai: {formatted_start_time}")
                self.stop_time_display_label.setText("Waktu Berhenti: -") # Clear stop time

            self.start_time_counter.restart()
            self.stopwatch_timer.start(1)
            self.is_running = True
            self.start_button.setText("Pause")
            self.start_button.setStyleSheet("background-color: #FFC107; color: black; font-size: 14pt; padding: 10px;")
        else:
            self.stopwatch_timer.stop()
            self.paused_time += self.start_time_counter.elapsed()
            self.is_running = False
            self.start_button.setText("Resume")
            self.start_button.setStyleSheet("background-color: #2196F3; color: white; font-size: 14pt; padding: 10px;")
            
    def stop_stopwatch(self):
        if self.is_running:
            self.stopwatch_timer.stop()
            self.stop_datetime = QDateTime.currentDateTime()
            formatted_stop_time = self.stop_datetime.toString("dd-MM-yyyy HH:mm:ss")
            self.stop_time_display_label.setText(f"Waktu Berhenti: {formatted_stop_time}")
            
            self.is_running = False
            self.paused_time += self.start_time_counter.elapsed()
            self.start_button.setText("Start")
            self.start_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 14pt; padding: 10px;")
            
        else: # Handle case when stop is pressed without starting
            self.start_button.setText("Start")
            self.start_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 14pt; padding: 10px;")
            self.paused_time = 0
            self.stopwatch_label.setText("00:00:00.000")
            self.start_time_display_label.setText("Waktu Mulai: -")
            self.stop_time_display_label.setText("Waktu Berhenti: -")
            
    def update_current_time(self):
        current_datetime = QDateTime.currentDateTime()
        formatted_datetime = current_datetime.toString("dddd, d MMMM yyyy, hh:mm:ss")
        self.current_time_label.setText(f"Waktu Saat Ini: {formatted_datetime}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StopwatchApp()
    window.show()
    sys.exit(app.exec_())