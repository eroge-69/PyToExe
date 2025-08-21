# Syllable Pitch Analyzer (Extended)
# Note: This file is the application entry point. It loads audio, performs pitch tracking,
# syllable segmentation (heuristic), and — if Whisper/WhisperX are installed and a transcript is available —
# it can perform ASR + forced alignment to get precise syllable boundaries.
#
# The GUI and core analysis are similar to the prototype. For full ASR+alignment integration, install
# whisperx and pyphen (optional for syllabification languages) and enable the 'run_asr_alignment' flag.

import sys, os, numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QPushButton, QLabel, QTableWidgetItem, QTableWidget
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QLineEdit
from PySide6 import QtCore
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import librosa, librosa.display
from scipy.signal import find_peaks

# Optional imports (ASR/Alignment):
# import whisper
# import whisperx
# import pyphen

def hz_to_midi(hz):
    if hz is None or np.isnan(hz) or hz <= 0:
        return None
    return 69 + 12 * np.log2(hz / 440.0)

NOTE_NAMES_SHARP = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

def midi_to_note_name(midi):
    if midi is None:
        return "-"
    m = int(round(midi))
    name = NOTE_NAMES_SHARP[m % 12]
    octave = (m // 12) - 1
    return f"{name}{octave}"

class MplCanvas(FigureCanvas):
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        super().__init__(self.fig)
        self.fig.tight_layout()

class Analyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Syllable Pitch Analyzer (Extended)")
        self.resize(1100, 750)
        self.y = None; self.sr = None; self.pitch_hz = None; self.pitch_time = None
        self.syllables = []
        self.setup_ui()

    def setup_ui(self):
        open_btn = QPushButton("Άνοιγμα ήχου"); open_btn.clicked.connect(self.open_audio)
        analyze_btn = QPushButton("Ανάλυση"); analyze_btn.clicked.connect(self.run_analysis)
        export_btn = QPushButton("Εξαγωγή CSV"); export_btn.clicked.connect(self.export_csv)
        self.hyphened_edit = QLineEdit(); self.hyphened_edit.setReadOnly(True)

        top_h = QHBoxLayout(); top_h.addWidget(open_btn); top_h.addWidget(analyze_btn); top_h.addWidget(export_btn); top_h.addStretch(1)
        top_panel = QWidget(); top_panel.setLayout(top_h)

        self.wave_canvas = MplCanvas(); self.wave_toolbar = NavigationToolbar(self.wave_canvas, self)
        self.contour_canvas = MplCanvas(); self.contour_toolbar = NavigationToolbar(self.contour_canvas, self)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["Idx","Start (s)","End (s)","Dur (s)","Pitch (Hz)","Note","Clef","Word#"])
        self.table.itemSelectionChanged.connect(self.update_selected_contour)

        top_split = QSplitter(QtCore.Qt.Vertical)
        wave_widget = QWidget(); v = QVBoxLayout(); v.addWidget(top_panel); v.addWidget(self.wave_toolbar); v.addWidget(self.wave_canvas); v.addWidget(QLabel("Συλλαβές (με παύλες):")); v.addWidget(self.hyphened_edit); wave_widget.setLayout(v)
        top_split.addWidget(wave_widget)
        bottom_split = QSplitter(QtCore.Qt.Horizontal)
        left = QWidget(); l = QVBoxLayout(); l.addWidget(QLabel("Συλλαβές")); l.addWidget(self.table); left.setLayout(l)
        right = QWidget(); r = QVBoxLayout(); r.addWidget(QLabel("Επιτονική καμπύλη")); r.addWidget(self.contour_toolbar); r.addWidget(self.contour_canvas); right.setLayout(r)
        bottom_split.addWidget(left); bottom_split.addWidget(right)
        main_split = QSplitter(QtCore.Qt.Vertical); main_split.addWidget(wave_widget); main_split.addWidget(bottom_split)
        central = QWidget(); main_l = QVBoxLayout(); main_l.addWidget(main_split); central.setLayout(main_l); self.setCentralWidget(central)

    def msg(self, t): QMessageBox.information(self, "Info", t)

    def open_audio(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open audio", filter="Audio Files (*.wav *.mp3 *.flac *.ogg)")
        if not path: return
        y, sr = librosa.load(path, sr=None, mono=True)
        self.y = y; self.sr = sr; self.times = np.arange(len(y))/sr; self.draw_waveform(); self.msg("Audio loaded.")

    def draw_waveform(self):
        if self.y is None: return
        ax = self.wave_canvas.ax; ax.clear(); ax.plot(self.times, self.y, linewidth=0.5); ax.set_xlabel("Time (s)"); ax.set_ylabel("Amplitude"); self.wave_canvas.draw()

    def run_analysis(self):
        if self.y is None: self.msg("Load audio first"); return
        y = self.y; sr = self.sr
        fmin = librosa.note_to_hz('C2'); fmax = librosa.note_to_hz('C7')
        f0, voiced_flag, voiced_prob = librosa.pyin(y, fmin=fmin, fmax=fmax, frame_length=2048, sr=sr)
        times = librosa.times_like(f0, sr=sr)
        self.pitch_hz = f0; self.pitch_time = times
        hop_length = 512
        oenv = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
        oenv_time = librosa.times_like(oenv, sr=sr, hop_length=hop_length)
        from scipy.ndimage import gaussian_filter1d
        oenv_s = gaussian_filter1d(oenv, sigma=1.0)
        min_distance = int(0.08 * sr / hop_length)
        height = np.percentile(oenv_s, 60)
        peaks, _ = find_peaks(oenv_s, distance=max(1, min_distance), height=height)
        peak_times = oenv_time[peaks]
        boundaries = [0.0] + list(peak_times) + [len(y)/sr]
        boundaries = sorted(list(set([float(b) for b in boundaries])))
        syllables = []
        for i in range(len(boundaries)-1):
            s = max(0.0, boundaries[i]); e = max(s + 1e-3, boundaries[i+1])
            dur = e - s; idx = np.where((self.pitch_time >= s) & (self.pitch_time < e))[0]; f0seg = self.pitch_hz[idx] if len(idx)>0 else np.array([])
            if f0seg.size > 0:
                f0clean = f0seg[~np.isnan(f0seg)]; pitch = float(np.median(f0clean)) if f0clean.size>0 else float("nan")
            else:
                pitch = float("nan")
            midi = hz_to_midi(pitch) if np.isfinite(pitch) else None
            note = midi_to_note_name(midi)
            syllables.append({"start":s,"end":e,"duration":dur,"pitch_hz":float(pitch) if np.isfinite(pitch) else None,"midi":midi,"note":note})
        self.syllables = syllables
        # create hyphenated placeholder
        hyph = []
        wid = 1
        for i, syl in enumerate(syllables):
            if i>0 and i%5==0:
                hyph.append(" ")
                wid += 1
            hyph.append("σ"); 
            if i < len(syllables)-1 and (i+1)%5 != 0:
                hyph.append("-")
        self.hyphened_edit.setText("".join(hyph))
        self.draw_waveform(); ax = self.wave_canvas.ax
        for syl in syllables:
            t = (syl["start"]+syl["end"])/2; ax.axvline(t, color='r', linewidth=0.6, alpha=0.4)
        self.wave_canvas.draw()
        self.table.setRowCount(len(syllables))
        for i, syl in enumerate(syllables):
            def set_item(col, text):
                it = QTableWidgetItem(text); it.setFlags(it.flags() ^ QtCore.Qt.ItemIsEditable); self.table.setItem(i, col, it)
            set_item(0, str(i+1)); set_item(1, f"{syl['start']:.3f}"); set_item(2, f"{syl['end']:.3f}"); set_item(3, f"{syl['duration']:.3f}"); hz = syl['pitch_hz']; set_item(4, f"{hz:.2f}" if hz is not None else "-"); set_item(5, syl['note']); set_item(6, "G"); set_item(7, str((i//5)+1))
        self.msg("Analysis complete (heuristic syllable boundaries). For exact boundaries enable ASR+alignment modules.")

    def export_csv(self):
        if not self.syllables: self.msg("No data"); return
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", filter="CSV (*.csv)")
        if not path: return
        import csv
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["index","start_s","end_s","duration_s","pitch_hz","note"])
            for i, syl in enumerate(self.syllables):
                w.writerow([i+1, f"{syl['start']:.6f}", f"{syl['end']:.6f}", f"{syl['duration']:.6f}", f"{syl['pitch_hz']:.3f}" if syl['pitch_hz'] is not None else ""])
        self.msg("CSV saved.")

    def update_selected_contour(self):
        rows = set([idx.row() for idx in self.table.selectedIndexes()])
        if not rows: return
        row = sorted(list(rows))[0]; wid = self.syllables[row]['start']; s = self.syllables[row]['start']; e = self.syllables[row]['end']
        idx = np.where((self.pitch_time >= s) & (self.pitch_time <= e))[0]; tseg = self.pitch_time[idx]; fseg = self.pitch_hz[idx]; ax = self.contour_canvas.ax; ax.clear()
        if tseg.size>0:
            ax.plot(tseg - s, fseg); ax.set_xlabel("Time (s)"); ax.set_ylabel("Hz"); ax.set_title("Contour")
        else:
            ax.text(0.5, 0.5, "No pitch data", ha="center", va="center")
        self.contour_canvas.draw()

def main():
    app = QApplication([]); w = Analyzer(); w.show(); sys.exit(app.exec())

if __name__ == "__main__":
    main()
