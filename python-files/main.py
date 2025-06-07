 import sys
import threading
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QTextEdit
import vlc
import subprocess


class ChordifyLite(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chordify Lite")
        self.setGeometry(100, 100, 600, 400)

        self.text = QTextEdit(self)
        self.text.setGeometry(50, 50, 500, 250)

        self.button = QPushButton("Open Audio File", self)
        self.button.setGeometry(200, 320, 200, 40)
        self.button.clicked.connect(self.load_audio)

        self.chords = []
        self.player = None

    def load_audio(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "", "Audio Files (*.mp3 *.wav)")
        if file_path:
            self.chords = extract_chords(file_path)
            self.text.append("Chords loaded.")
            self.play_audio(file_path)

    def play_audio(self, path):
        self.player = vlc.MediaPlayer(path)
        self.player.play()
        self.start_timer()

    def start_timer(self):
        def update():
            shown = set()
            while self.player.is_playing():
                current_time = self.player.get_time() / 1000.0
                for t, chord in self.chords:
                    if abs(current_time - t) < 0.25 and t not in shown:
                        self.text.append(f"{round(t, 2)}s: {chord}")
                        shown.add(t)
                time.sleep(0.2)

        threading.Thread(target=update, daemon=True).start()

	def extract_chords(audio_path):
		"""Uses Chordino plugin via Sonic Annotator to extract chords."""
		vamp_command = [
			"sonic-annotator",
			"-d", "vamp:nnls-chroma:chordino:chordino",
			audio_path,
			"-w", "csv",
			"--csv-stdout"
		]
		result = subprocess.run(vamp_command, stdout=subprocess.PIPE, text=True)
		chords = []

		for line in result.stdout.strip().split("\n"):
			if line and not line.startswith("#"):
				parts = line.split(",")
				start_time = float(parts[0])
				chord = parts[2]
				chords.append((start_time, chord))

		return chords

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChordifyLite()
    window.show()
    sys.exit(app.exec_())
