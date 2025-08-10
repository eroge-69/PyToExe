import os
import sys

import whisper
from datetime import timedelta

from PySide6.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QTextEdit, QLabel, QHBoxLayout)
from PySide6.QtGui import QFont, Qt, QPixmap, QIcon

class JustInCaseCore:
    def __init__(self):
        self.model = whisper.load_model("small")

    def format_timestampt(self, seconds):
        td = timedelta(seconds=seconds)
        total_seconds = int(td.total_seconds())
        milliseconds = int((td.total_seconds() - total_seconds) * 1000)
        return str(td).split(".")[0].zfill(8) + f",{milliseconds:03d}"

    def listern_and_generate_srt(self, audio_path):
        result = self.model.transcribe(audio_path)

        base, _ = os.path.splitext(audio_path)
        srt_output_path = f"{base}_subtitles.srt"

        with open(srt_output_path, "w", encoding="utf-8") as srt_file:
            for i, segment in enumerate(result["segments"], start=1):
                start = self.format_timestampt(segment["start"])
                end = self.format_timestampt(segment["end"])
                text = segment["text"].strip()

                srt_file.write(f"{i}\n")
                srt_file.write(f"{start} --> {end}\n")
                srt_file.write(f"{text}\n\n")


        # print(f"SRT file saved: {srt_output_path}")
        # print(Fore.LIGHTYELLOW_EX + "Note: Review the subtitles. Some words may be inaccurate or misheard ")
        return srt_output_path


class JustInCaseGUI(QWidget):
    def __init__(self):
        super().__init__() # this is used to call the constructor of the parent class of the current class, Here it inherited from QWidget
        # QWidget is basically like blank canvas. u can add buttons, labels, set layouts, etc.

        self.setWindowTitle("JustInCase V2 – Subtitle Generator By Mr. BILRED")
        self.setGeometry(100, 100, 600, 500)  # (x, y, width, height)

        self.setWindowIcon(QIcon("JUSTINCASELOGO.icns"))

        self.audio_path = None
        self.core = JustInCaseCore()  # this allows GUI to use functions from JustInCaseCore (cli backend)

        layout = QVBoxLayout()  # this creates vertical layout.
        button_layout = QHBoxLayout()  # this creates horizontal layout
        # No need to modify this layout later, so no need to use self.


        title_label = QLabel("JustInCase V2")
        title_font = QFont("Arial", 24, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: white;")
        layout.addWidget(title_label)


        subtitle_label = QLabel("Subtitle Generator By Mr. BILRED \nJust In Case You Need Them")
        subtitle_font = QFont("Arial", 16)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: white;")
        layout.addWidget(subtitle_label)


        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/asset1.png")
        logo_label.setPixmap(logo_pixmap.scaledToHeight(40, Qt.SmoothTransformation))


        header_layout = QHBoxLayout()
        header_layout.addWidget(title_label, alignment=Qt.AlignLeft)
        header_layout.addWidget(subtitle_label, alignment=Qt.AlignLeft)



        header_layout.addStretch()
        header_layout.addWidget(logo_label, alignment=Qt.AlignRight)
        layout.addLayout(header_layout)


        # Buttons
        self.browse_button = QPushButton("Browse Audio File")
        self.generate_button = QPushButton("Generate SRT")
        self.generate_button.setEnabled(False)  # this means unless a file is selected, generate_button is unclickable

        # When Buttons are Clicked

        self.browse_button.clicked.connect(self.browse_audio_file)  # this function should be defined below
        self.generate_button.clicked.connect(self.generate_srt)
        # self.generate_button.clicked.connect(self.generate_srt)


        self.log_output = QTextEdit()  # this creates a text area in gui where logs, messages, errors, etc can be shown
        self.log_output.setReadOnly(True) # this makes QTextEdit read only

        button_layout.addWidget(self.browse_button)  # just see, i used button_layout, which is horizontal!
        button_layout.addWidget(self.generate_button)

        layout.addLayout(button_layout)
        layout.addWidget(QLabel("Log Output:")) # this creates a label right above the text area
        layout.addWidget(self.log_output) # this adds the actual text area for logs under the label

        self.setLayout(layout)

    def log(self, message):
        self.log_output.append(message)

    def browse_audio_file(self):
            file_path, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "", "All Files (*)")
            if file_path:
                self.audio_path = file_path
                self.generate_button.setEnabled(True)
                self.log(f"File Selected: {file_path}")
                self.log("\nWhen You Press Generate SRT Button, Wait For A While...")



    def generate_srt(self):
        if not self.audio_path:
            self.log("NO FILE SELECTED")
            return

        try:
            # self.log("\nAttempting to generate SRT...")
            srt_output_path = self.core.listern_and_generate_srt(self.audio_path)
            self.log(f"\nSRT File Saved: {srt_output_path}")
            self.log("NOTE: Review the subtitles. Some words may be inaccurate or misheard")

        except Exception as e:
            self.log(f"ERROR: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JustInCaseGUI()
    window.show()
    sys.exit(app.exec())  # this ensures when the app closes, Python exits cleanly.



# Mr. BILRED

