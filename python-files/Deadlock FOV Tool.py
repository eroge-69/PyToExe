import os
import sys
import re
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QFileDialog, QMessageBox, QFrame
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class DeadlockTool(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Deadlock FOV Tool")
        self.setStyleSheet("background-color: #2b2b2b; color: #f0f0f0;")
        self.resize(650, 260)

        layout = QVBoxLayout()
        layout.setSpacing(10)

        # ===== Status Banner (oben) =====
        self.status_banner = QLabel("valid file missing")
        self.status_banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_banner.setStyleSheet(
            "background-color:#5a1f1f; color:#ffffff; padding:8px; border-radius:8px; font-weight:700;"
        )
        self.status_banner.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(self.status_banner)

        # ===== Install Path =====
        path_label = QLabel("Install Path (folder that contains gameinfo.gi)")
        path_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(path_label)

        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText(r"e.g. C:\...\SteamLibrary\steamapps\common\Deadlock\game\citadel")
        self.path_input.setStyleSheet("background-color: #3c3c3c; padding: 6px; border-radius: 6px;")

        btn_layout = QHBoxLayout()
        self.auto_btn = QPushButton("Auto Select")
        self.manual_btn = QPushButton("Manual Select")
        for btn in (self.auto_btn, self.manual_btn):
            btn.setStyleSheet("background-color: #444; padding: 8px; border-radius: 6px;")
        btn_layout.addWidget(self.path_input, 1)
        btn_layout.addWidget(self.auto_btn)
        btn_layout.addWidget(self.manual_btn)
        layout.addLayout(btn_layout)

        # thin divider
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet("color:#444;")
        layout.addWidget(div)

        # ===== FOV =====
        fov_label = QLabel("FOV")
        fov_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(fov_label)

        self.fov_input = QLineEdit()
        self.fov_input.setPlaceholderText("e.g. 2.7")
        self.fov_input.setStyleSheet("background-color: #3c3c3c; padding: 6px; border-radius: 6px;")
        layout.addWidget(self.fov_input)

        # ===== Update Button =====
        self.update_btn = QPushButton("Update FOV")
        self.update_btn.setStyleSheet("background-color: #555; padding: 10px; border-radius: 8px;")
        layout.addWidget(self.update_btn)

        # ===== Edit-Status unter Button =====
        self.edit_status = QLabel("Unedited GI")
        self.edit_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.edit_status.setStyleSheet(
            "color:#dddddd; padding:4px; font-style:italic;"
        )
        layout.addWidget(self.edit_status)

        self.setLayout(layout)

        # Signals
        self.auto_btn.clicked.connect(self.auto_select)
        self.manual_btn.clicked.connect(self.manual_select)
        self.update_btn.clicked.connect(self.update_fov)
        self.path_input.textChanged.connect(self.on_path_changed)

        # Try auto select on start
        self.auto_select()

    # ---------- Helpers ----------
    def set_banner(self, ok: bool):
        if ok:
            self.status_banner.setText("valid file found")
            self.status_banner.setStyleSheet(
                "background-color:#1f5a2b; color:#ffffff; padding:8px; border-radius:8px; font-weight:700;"
            )
        else:
            self.status_banner.setText("valid file missing")
            self.status_banner.setStyleSheet(
                "background-color:#5a1f1f; color:#ffffff; padding:8px; border-radius:8px; font-weight:700;"
            )

    def gameinfo_path(self):
        """
        Returns the path to gameinfo.gi based on current path_input.
        The path_input is expected to be the folder that directly contains gameinfo.gi.
        """
        base_path = self.path_input.text().strip()
        return os.path.join(base_path, "gameinfo.gi")

    def ensure_citadel_path(self, folder: str) -> str | None:
        """
        Ensures we return the FOLDER that directly contains gameinfo.gi.
        Accepts either:
         - the exact citadel folder (…\game\citadel), or
         - the Deadlock root (…\Deadlock) -> then append \game\citadel if valid, or
         - any Steam library root -> try resolving.
        Returns the normalized citadel folder or None.
        """
        f = os.path.normpath(folder)

        # Case 1: selected folder already contains gameinfo.gi
        gi_here = os.path.join(f, "gameinfo.gi")
        if os.path.isfile(gi_here):
            return f

        # Case 2: user picked Deadlock root -> append \game\citadel
        candidate = os.path.join(f, "game", "citadel")
        gi_cand = os.path.join(candidate, "gameinfo.gi")
        if os.path.isfile(gi_cand):
            return os.path.normpath(candidate)

        # Case 3: user picked steam library root -> try to resolve
        candidate = os.path.join(f, "steamapps", "common", "Deadlock", "game", "citadel")
        gi_cand = os.path.join(candidate, "gameinfo.gi")
        if os.path.isfile(gi_cand):
            return os.path.normpath(candidate)

        return None

    def on_path_changed(self):
        """Whenever the path field changes, refresh status + FOV + edited flag."""
        self.read_current_fov()

    # ---------- Core ----------
    def auto_select(self):
        steam_root = os.path.expandvars(r"C:\Program Files (x86)\Steam")
        library_file = os.path.join(steam_root, "steamapps", "libraryfolders.vdf")

        steam_libraries = []

        # libraryfolders.vdf parsen
        if os.path.exists(library_file):
            try:
                with open(library_file, "r", encoding="utf-8") as f:
                    content = f.read()
                matches = re.findall(r'"path"\s+"([^"]+)"', content)
                steam_libraries = [os.path.normpath(m) for m in matches]
            except Exception:
                pass

        # Standard-Steam-Pfad hinzufügen
        steam_libraries.append(steam_root)

        # Nach Deadlock suchen
        for lib in steam_libraries:
            candidate = os.path.join(lib, "steamapps", "common", "Deadlock", "game", "citadel")
            gi_path = os.path.join(candidate, "gameinfo.gi")
            if os.path.exists(gi_path):
                # WICHTIG: exakten citadel-Ordner in das Feld schreiben
                self.path_input.setText(candidate)
                self.read_current_fov()
                return

        # nichts gefunden
        self.set_banner(False)
        QMessageBox.warning(self, "Not Found", "Deadlock installation not found. Please select manually.")

    def manual_select(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Deadlock Folder (Deadlock OR ...\\game\\citadel)")
        if folder:
            fixed = self.ensure_citadel_path(folder)
            if fixed:
                self.path_input.setText(fixed)
                self.read_current_fov()
            else:
                self.set_banner(False)
                QMessageBox.critical(
                    self, "Invalid Folder",
                    "Could not locate gameinfo.gi. Please select the Deadlock folder or the '...\\game\\citadel' folder."
                )

    def read_current_fov(self):
        gi_path = self.gameinfo_path()
        exists = os.path.exists(gi_path)
        self.set_banner(exists)

        if not exists:
            self.fov_input.clear()
            self.edit_status.setText("Unedited GI")
            return

        try:
            with open(gi_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not read gameinfo.gi:\n{e}")
            return

        # FOV und Edit-Status ermitteln
        match = re.search(r'^\s*"r_aspectratio"\s+"([0-9]+(?:\.[0-9]+)?)"\s*$', content, re.MULTILINE)
        if match:
            self.fov_input.setText(match.group(1))
            self.edit_status.setText("Edited GI")
        else:
            # leer lassen, aber Status anzeigen
            self.edit_status.setText("Unedited GI")

    def update_fov(self):
        fov_val = self.fov_input.text().strip()
        if not re.match(r'^[0-9]+(\.[0-9]+)?$', fov_val):
            QMessageBox.critical(self, "Invalid Input", "FOV must be a float number like 2.7")
            return

        gi_path = self.gameinfo_path()
        if not os.path.exists(gi_path):
            QMessageBox.critical(self, "Error", "gameinfo.gi not found!")
            self.set_banner(False)
            return

        try:
            with open(gi_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not read gameinfo.gi:\n{e}")
            return

        new_lines = []
        found_aspect = False
        inside_convars = False

        # Wir wollen "r_aspectratio" direkt ÜBER "rate" platzieren, falls es noch nicht existiert.
        for i, line in enumerate(lines):
            stripped = line.strip()

            # Eintritt in ConVars-Block
            if stripped == "ConVars":
                inside_convars = True
                new_lines.append(line)
                continue

            # Bereits vorhandenes r_aspectratio -> ersetzen
            if inside_convars and stripped.startswith('"r_aspectratio"'):
                indent = line[:len(line) - len(line.lstrip())]  # Einrückung beibehalten
                new_lines.append(f'{indent}"r_aspectratio" "{fov_val}"\n')
                found_aspect = True
                continue

            # Wenn noch nicht gefunden: direkt über "rate" einfügen
            if inside_convars and (stripped.startswith('"rate"') or stripped == '"rate"'):
                if not found_aspect:
                    indent = line[:len(line) - len(line.lstrip())]
                    new_lines.append(f'{indent}"r_aspectratio" "{fov_val}"\n')
                    found_aspect = True
                new_lines.append(line)
                continue

            # Ende des ConVars-Blocks
            if inside_convars and stripped == "}":
                if not found_aspect:
                    # Fallback: vor schließender Klammer einfügen
                    indent = " " * 8  # Standard-Indent passend zum Beispiel
                    new_lines.append(f'{indent}"r_aspectratio" "{fov_val}"\n')
                    found_aspect = True
                inside_convars = False
                new_lines.append(line)
                continue

            new_lines.append(line)

        # Backup anlegen (einmalig)
        try:
            if not os.path.exists(gi_path + ".bak"):
                os.rename(gi_path, gi_path + ".bak")
        except Exception as e:
            QMessageBox.warning(self, "Backup Warning", f"Could not create backup (.bak):\n{e}")

        # Schreiben
        try:
            with open(gi_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not write gameinfo.gi:\n{e}")
            return

        # UI aktualisieren
        self.set_banner(True)
        self.edit_status.setText("Edited GI")
        QMessageBox.information(self, "Success", f"FOV updated to {fov_val}!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = DeadlockTool()
    win.show()
    sys.exit(app.exec())
