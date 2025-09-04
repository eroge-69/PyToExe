# elrifenos.py

import sys, threading, random, numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui
import sounddevice as sd
from flask import Flask, request

# --- FLASK SERVER ---
app = Flask(__name__)
audio_buffer = []
connected = False

@app.route('/stream', methods=['POST'])
def stream():
    global audio_buffer, connected
    connected = True
    audio_buffer.append(np.frombuffer(request.data, dtype=np.int16))
    return "OK"

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False)

# --- AUDIO PLAYER ---
playing = False
volume_level = 0
def play_audio():
    global audio_buffer, playing, volume_level
    fs = 44100
    while True:
        if playing and audio_buffer:
            chunk = audio_buffer.pop(0)
            volume_level = np.abs(chunk).mean() / 500
            sd.play(chunk, samplerate=fs)
            sd.wait()
        else:
            volume_level = 0

# --- MATRIX EFFECT ---
class MatrixWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, columns=120):
        super().__init__(parent)
        self.chars = [chr(i) for i in range(33, 127)]
        self.columns = columns
        self.drops = [random.randint(0, 50) for _ in range(self.columns)]
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)
        self.setStyleSheet("background-color: black;")

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QColor(0, 255, 0))
        font = QtGui.QFont("Consolas", 12)
        painter.setFont(font)
        w = self.width() // self.columns
        for i in range(self.columns):
            text = random.choice(self.chars)
            painter.drawText(i*w, self.drops[i]*12, text)
            if self.drops[i]*12 > self.height() or random.random() > 0.95:
                self.drops[i] = 0
            self.drops[i] += 1

$# --- GUI ---$
class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RiFi-Hack - Connexion")
        self.setGeometry(100, 100, 800, 600)  # Résolution adaptable
        self.setStyleSheet("background-color: black; color: #00FF00; font-family: Consolas;")

        # Fond animé
        self.matrix = MatrixWidget(self, columns=100)
        self.matrix.setGeometry(0, 0, 800, 600)

        # Labels et inputs
        self.label_title = QtWidgets.QLabel("RiFi-Hack", self)
        self.label_title.setGeometry(250, 50, 300, 80)
        self.label_title.setStyleSheet("font-size: 48px; font-weight: bold; color: #00FF00; background: transparent;")

        self.label_id = QtWidgets.QLabel("Id RiFi:", self)
        self.label_id.setGeometry(200, 200, 150, 40)
        self.label_id.setStyleSheet("background: transparent; font-size: 20px;")
        self.label_mdp = QtWidgets.QLabel("MDP:", self)
        self.label_mdp.setGeometry(200, 270, 150, 40)
        self.label_mdp.setStyleSheet("background: transparent; font-size: 20px;")

        self.input_id = QtWidgets.QLineEdit(self)
        self.input_id.setGeometry(350, 200, 350, 40)
        self.input_id.setStyleSheet("background-color: #111; color: #00FF00; border: 2px solid #00FF00; font-size: 20px; padding-left: 5px;")
        self.input_mdp = QtWidgets.QLineEdit(self)
        self.input_mdp.setGeometry(350, 270, 350, 40)
        self.input_mdp.setEchoMode(QtWidgets.QLineEdit.Password)
        self.input_mdp.setStyleSheet("background-color: #111; color: #00FF00; border: 2px solid #00FF00; font-size: 20px; padding-left: 5px;")

        # Bouton connexion
        self.btn_login = QtWidgets.QPushButton("Connexion", self)
        self.btn_login.setGeometry(350, 350, 200, 50)
        self.btn_login.setStyleSheet("""
            QPushButton {
                background-color: #111;
                color: #00FF00;
                border: 2px solid #00FF00;
                font-weight: bold;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #00FF00;
                color: #0D0D0D;
            }
        """)
        self.btn_login.clicked.connect(self.check_login)

    def check_login(self):
        if self.input_id.text() == "RiFi" and self.input_mdp.text() == "Dalil2010.":
            self.main_window = MainWindow()
            self.main_window.show()
            self.close()
        else:
            QtWidgets.QMessageBox.warning(self, "Erreur", "Id ou MDP incorrect.")

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mise à l'écoute téléphone de Mokhtar")
        self.setGeometry(50, 50, 1200, 800)  # Résolution adaptable
        self.setStyleSheet("background-color: black; color: #00FF00; font-family: Consolas;")

        # Fond matrix
        self.matrix = MatrixWidget(self, columns=150)
        self.matrix.setGeometry(0, 0, 1200, 800)

        # Titre
        self.label_title = QtWidgets.QLabel("Mise à l'écoute téléphone de Mokhtar", self)
        self.label_title.setGeometry(250, 20, 700, 60)
        self.label_title.setStyleSheet("font-size: 36px; font-weight: bold; color: #00FF00; background: transparent;")

        # Boutons Start/Stop
        self.btn_start = QtWidgets.QPushButton("Start", self)
        self.btn_start.setGeometry(300, 100, 200, 60)
        self.btn_start.setStyleSheet("""
            QPushButton {background-color: #111; color: #00FF00; border: 2px solid #00FF00; font-weight: bold; font-size: 22px;}
            QPushButton:hover {background-color: #00FF00; color: #0D0D0D;}
        """)
        self.btn_start.clicked.connect(self.start_stream)

        self.btn_stop = QtWidgets.QPushButton("Stop", self)
        self.btn_stop.setGeometry(700, 100, 200, 60)
        self.btn_stop.setStyleSheet("""
            QPushButton {background-color: #111; color: #FF0000; border: 2px solid #FF0000; font-weight: bold; font-size: 22px;}
            QPushButton:hover {background-color: #FF0000; color: #0D0D0D;}
        """)
        self.btn_stop.clicked.connect(self.stop_stream)

        # Statut connexion
        self.label_status = QtWidgets.QLabel("Statut : Hors ligne", self)
        self.label_status.setGeometry(500, 200, 300, 40)
        self.label_status.setStyleSheet("font-size: 24px; color: #FF0000; background: transparent;")

        # Footer
        self.label_footer = QtWidgets.QLabel("Logiciel créé par RiFi", self)
        self.label_footer.setGeometry(500, 730, 300, 30)
        self.label_footer.setStyleSheet("font-size: 18px; color: grey; font-style: italic; background: transparent;")

        # Barre graphique du son
        self.audio_bar = QtWidgets.QProgressBar(self)
        self.audio_bar.setGeometry(300, 300, 600, 40)
        self.audio_bar.setMaximum(100)
        self.audio_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #00FF00;
                text-align: center;
                color: #00FF00;
                background-color: #111;
            }
            QProgressBar::chunk {
                background-color: #00FF00;
            }
        """)

        # Timer pour mise à jour interface
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(50)

    def start_stream(self):
        global playing
        playing = True

    def stop_stream(self):
        global playing
        playing = False

    def update_ui(self):
        global connected, volume_level
        # Statut connexion
        if connected:
            self.label_status.setText("Statut : En ligne")
            self.label_status.setStyleSheet("font-size: 24px; color: #00FF00; background: transparent;")
        else:
            self.label_status.setText("Statut : Hors ligne")
            self.label_status.setStyleSheet("font-size: 24px; color: #FF0000; background: transparent;")
        # Barre audio
        level = min(int(volume_level * 100), 100)
        self.audio_bar.setValue(level)

$# --- MAIN ---$
if __name__ == "__main__":
    print("Démarrage du serveur Flask...")
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    print("Démarrage du lecteur audio...")
    audio_thread = threading.Thread(target=play_audio)
    audio_thread.daemon = True
    audio_thread.start()

    print("Démarrage de l'interface graphique Qt...")
    app_qt = QtWidgets.QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app_qt.exec_())