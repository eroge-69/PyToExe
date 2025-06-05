import sys
import os
import shutil
import subprocess
import threading

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QLabel,
    QLineEdit,
    QHBoxLayout,
    QVBoxLayout,
    QMessageBox
)

import mss


class ScreenRecorderHD(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enregistreur d'écran HD + Audio")
        self.setFixedSize(450, 160)

        # ----------------------------------------------------------------------------
        # 1) Dossier de sauvegarde fixe
        # ----------------------------------------------------------------------------
        # Remplacez ce chemin par celui que vous souhaitez :
        self.SAVE_DIR = r"C:\Users\flori\Downloads\New folder"

        # ----------------------------------------------------------------------------
        # Variables d’état
        # ----------------------------------------------------------------------------
        self.ffmpeg_process = None
        self.recording = False

        # ----------------------------------------------------------------------------
        # Widgets de l’interface
        # ----------------------------------------------------------------------------
        self.label_filename = QLabel("Nom de fichier :")
        # On affiche déjà l’exemple de chemin complet (avec le dossier) pour guider l’utilisateur :
        self.input_filename = QLineEdit("ma_capture.mp4")
        self.input_filename.setPlaceholderText("ex. ma_capture.mp4")

        self.btn_start = QPushButton("Démarrer l'enregistrement")
        self.btn_stop = QPushButton("Arrêter")
        self.btn_stop.setEnabled(False)

        # ----------------------------------------------------------------------------
        # Layouts
        # ----------------------------------------------------------------------------
        h_file = QHBoxLayout()
        h_file.addWidget(self.label_filename)
        h_file.addWidget(self.input_filename)

        h_buttons = QHBoxLayout()
        h_buttons.addWidget(self.btn_start)
        h_buttons.addWidget(self.btn_stop)

        v_main = QVBoxLayout()
        v_main.addLayout(h_file)
        v_main.addLayout(h_buttons)

        self.setLayout(v_main)

        # ----------------------------------------------------------------------------
        # Connexions signaux/slots
        # ----------------------------------------------------------------------------
        self.btn_start.clicked.connect(self.start_recording)
        self.btn_stop.clicked.connect(self.stop_recording)

    def start_recording(self):
        """Prépare et lance le processus FFmpeg en arrière-plan."""
        filename = self.input_filename.text().strip()
        if not filename:
            QMessageBox.warning(self, "Erreur", "Veuillez saisir un nom de fichier valide.")
            return
        if not (filename.lower().endswith(".mp4") or filename.lower().endswith(".avi")):
            QMessageBox.warning(self, "Erreur", "Le fichier doit se terminer par .mp4 ou .avi.")
            return

        # ----------------------------------------------------------------------------
        # Vérifier que le dossier de sauvegarde existe, sinon le créer
        # ----------------------------------------------------------------------------
        try:
            os.makedirs(self.SAVE_DIR, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur dossier",
                f"Impossible de créer/accéder au dossier de sauvegarde :\n{self.SAVE_DIR}\n\n{e}"
            )
            return

        # ----------------------------------------------------------------------------
        # Construction du chemin complet du fichier de sortie
        # ----------------------------------------------------------------------------
        full_path = os.path.join(self.SAVE_DIR, filename)

        # ----------------------------------------------------------------------------
        # Vérifier que FFmpeg est installé (commande 'ffmpeg' trouvable)
        # ----------------------------------------------------------------------------
        if shutil.which("ffmpeg") is None:
            QMessageBox.critical(
                self,
                "FFmpeg introuvable",
                "La commande 'ffmpeg' n'a pas été trouvée dans votre PATH.\n"
                "Installez FFmpeg et ajoutez-le à votre variable d'environnement PATH."
            )
            return

        # ----------------------------------------------------------------------------
        # Lire la résolution de l’écran principal (minimum HD 1280×720)
        # ----------------------------------------------------------------------------
        with mss.mss() as sct:
            mon = sct.monitors[1]  # moniteur principal
            screen_width = mon["width"]
            screen_height = mon["height"]

        if screen_width < 1280 or screen_height < 720:
            QMessageBox.warning(
                self,
                "Résolution trop faible",
                f"Votre écran actuel fait {screen_width}×{screen_height}.\n"
                "La résolution minimale requise est 1280×720."
            )
            return

        # ----------------------------------------------------------------------------
        # Construction de la commande FFmpeg pour capturer vidéo + audio système
        # ----------------------------------------------------------------------------
        #    - Capture vidéo : gdigrab (Windows), 60 fps, plein écran (desktop).
        #    - Capture audio : dshow + virtual-audio-capturer.
        #    - Encodage vidéo : libx264, yuv420p, preset ultrafast, 60 fps.
        #    - Encodage audio : AAC à 192 kbps.
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            # === Vidéo ===
            "-f", "gdigrab",
            "-framerate", "60",
            "-video_size", f"{screen_width}x{screen_height}",
            "-i", "desktop",
            # === Audio ===
            "-f", "dshow",
            "-i", "audio=virtual-audio-capturer",
            # === Codec vidéo ===
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "ultrafast",
            "-r", "60",
            # === Codec audio ===
            "-c:a", "aac",
            "-b:a", "192k",
            # === Fichier de sortie (chemin complet) ===
            full_path
        ]

        try:
            # Lancement du process en tâche de fond
            # On redirige stdout et stderr vers DEVNULL pour ne pas polluer la console
            self.ffmpeg_process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW  # pas de fenêtre console
            )
        except Exception as e:
            QMessageBox.critical(self, "Erreur FFmpeg", f"Impossible de lancer ffmpeg :\n{e}")
            return

        # ----------------------------------------------------------------------------
        # Mise à jour de l’UI
        # ----------------------------------------------------------------------------
        self.recording = True
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)

    def stop_recording(self):
        """Arrête proprement le processus FFmpeg et notifie l’utilisateur."""
        if not self.recording or self.ffmpeg_process is None:
            return

        # On envoie un terminate() à FFmpeg
        try:
            self.ffmpeg_process.terminate()
        except Exception:
            pass

        # Déréférencer pour éviter réutilisation
        proc = self.ffmpeg_process
        self.ffmpeg_process = None
        self.recording = False
        self.btn_stop.setEnabled(False)

        # On attend la fin du process dans un thread pour ne pas bloquer l’UI
        def wait_and_finalize():
            try:
                proc.wait(timeout=10)
            except Exception:
                pass
            # Une fois FFmpeg bien terminé, réactivation du bouton Start et message
            QtCore.QTimer.singleShot(0, lambda: self.btn_start.setEnabled(True))
            QtCore.QTimer.singleShot(
                0,
                lambda: QMessageBox.information(
                    self,
                    "Enregistrement terminé",
                    f"L'enregistrement a été sauvegardé dans :\n{os.path.join(self.SAVE_DIR, self.input_filename.text().strip())}"
                )
            )

        threading.Thread(target=wait_and_finalize, daemon=True).start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreenRecorderHD()
    window.show()
    sys.exit(app.exec_())
