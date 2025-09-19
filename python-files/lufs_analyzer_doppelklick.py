import soundfile as sf
import pyloudnorm as pyln
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import sys

class LUFSAnalyzer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LUFS Audio Analyzer")
        self.root.geometry("600x500")
        self.root.resizable(True, True)

        # Icon setzen (falls verfügbar)
        try:
            self.root.iconbitmap(default="audio.ico")
        except:
            pass

        self.setup_gui()

    def setup_gui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        header_frame.pack(fill="x", padx=5, pady=5)
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text="🎵 LUFS Audio Analyzer", 
                              font=("Arial", 16, "bold"), 
                              bg="#2c3e50", fg="white")
        title_label.pack(expand=True)

        # Button Frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        # Datei auswählen Button
        self.select_button = tk.Button(button_frame, 
                                      text="📁 Audio-Datei auswählen", 
                                      font=("Arial", 12),
                                      bg="#3498db", fg="white",
                                      padx=20, pady=10,
                                      command=self.select_and_analyze)
        self.select_button.pack(side="left", padx=5)

        # Beenden Button
        self.quit_button = tk.Button(button_frame, 
                                    text="❌ Beenden", 
                                    font=("Arial", 12),
                                    bg="#e74c3c", fg="white",
                                    padx=20, pady=10,
                                    command=self.root.quit)
        self.quit_button.pack(side="right", padx=5)

        # Ergebnis-Textfeld
        result_frame = tk.Frame(self.root)
        result_frame.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(result_frame, text="Analyseergebnisse:", font=("Arial", 12, "bold")).pack(anchor="w")

        self.result_text = scrolledtext.ScrolledText(result_frame, 
                                                    font=("Consolas", 10),
                                                    bg="#f8f9fa",
                                                    wrap=tk.WORD)
        self.result_text.pack(fill="both", expand=True)

        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Bereit - Wähle eine Audio-Datei aus")
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                             relief=tk.SUNKEN, anchor="w", bg="#ecf0f1")
        status_bar.pack(fill="x", side="bottom")

        # Willkommensnachricht
        welcome_text = """🎵 Willkommen beim LUFS Audio Analyzer!

Dieser Analyzer hilft dir dabei, deine Audio-Dateien für Streaming-Plattformen zu optimieren.

Unterstützte Formate:
• WAV (16-bit, 24-bit, 32-bit)
• FLAC
• AIFF

Was wird analysiert:
• LUFS Integrated Loudness (YouTube/Spotify Standard)
• True Peak Level (Clipping-Schutz)
• RMS Durchschnitt
• Dynamikbereich
• Frequenzspektrum (wird als PNG gespeichert)

Klicke auf "Audio-Datei auswählen" um zu starten!"""

        self.result_text.insert(tk.END, welcome_text)

    def select_and_analyze(self):
        # Datei-Dialog öffnen
        file_path = filedialog.askopenfilename(
            title="Audio-Datei für LUFS-Analyse auswählen",
            filetypes=[
                ("WAV-Dateien", "*.wav"),
                ("FLAC-Dateien", "*.flac"),
                ("AIFF-Dateien", "*.aiff *.aif"),
                ("Alle Audio-Dateien", "*.wav *.flac *.aiff *.aif"),
                ("Alle Dateien", "*.*")
            ],
            initialdir=os.getcwd()
        )

        if file_path:
            self.status_var.set(f"Analysiere: {os.path.basename(file_path)}...")
            self.root.update()

            # Textfeld leeren
            self.result_text.delete(1.0, tk.END)

            # Analyse starten
            self.analyze_audio(file_path)
        else:
            self.status_var.set("Keine Datei ausgewählt")

    def log(self, message):
        """Fügt eine Nachricht zum Ergebnis-Textfeld hinzu"""
        self.result_text.insert(tk.END, message + "\n")
        self.result_text.see(tk.END)
        self.root.update()

    def analyze_audio(self, filename):
        """Analysiert eine Audio-Datei"""
        try:
            self.log(f"🎵 Analysiere: {os.path.basename(filename)}")
            self.log("=" * 50)

            # Audio laden
            try:
                y, sr = sf.read(filename)
                self.log(f"✅ Datei geladen: {len(y)/sr:.1f} Sekunden, {sr} Hz")
            except Exception as e:
                self.log(f"❌ Fehler beim Laden: {e}")
                messagebox.showerror("Fehler", f"Datei konnte nicht geladen werden:\n{e}")
                return

            # Stereo -> Mono
            if len(y.shape) > 1:
                y_mono = y.mean(axis=1)
                self.log("📊 Stereo -> Mono konvertiert für LUFS-Messung")
            else:
                y_mono = y
                self.log("📊 Mono-Datei erkannt")

            # LUFS Meter
            meter = pyln.Meter(sr)

            # Werte berechnen
            lufs_integrated = meter.integrated_loudness(y_mono)

            # Loudness Range (falls verfügbar)
            try:
                loudness_range = meter.loudness_range(y_mono)
                lra_available = True
            except AttributeError:
                loudness_range = None
                lra_available = False

            # True Peak
            if len(y.shape) > 1:
                true_peak = max(np.max(np.abs(y[:, 0])), np.max(np.abs(y[:, 1])))
            else:
                true_peak = np.max(np.abs(y))

            true_peak_db = 20*np.log10(true_peak + 1e-12)

            # RMS
            rms = np.sqrt(np.mean(y_mono**2))
            rms_db = 20*np.log10(rms + 1e-12)

            # Dynamik-Schätzung
            if not lra_available:
                dynamic_range_estimate = true_peak_db - rms_db

            # Ergebnisse ausgeben
            self.log("\n📊 ERGEBNISSE")
            self.log("-" * 30)
            self.log(f"Integrated Loudness : {lufs_integrated:.2f} LUFS")

            if lra_available:
                self.log(f"Loudness Range (LRA): {loudness_range:.2f} LU")
            else:
                self.log(f"Dynamik-Schätzung   : {dynamic_range_estimate:.2f} dB (Peak-RMS)")

            self.log(f"True Peak           : {true_peak_db:.2f} dBFS")
            self.log(f"RMS Durchschnitt    : {rms_db:.2f} dBFS")

            # Streaming Bewertung
            self.log("\n🎯 STREAMING BEWERTUNG")
            self.log("-" * 30)

            if -15 <= lufs_integrated <= -13:
                self.log("✅ YouTube/Spotify: PERFEKT (-14 LUFS Ziel)")
            elif lufs_integrated > -13:
                self.log(f"⚠️  Zu laut ({lufs_integrated:.1f} LUFS) - wird runtergeregelt")
                self.log(f"   Empfehlung: Maximizer Gain um {lufs_integrated - (-14):.1f} dB senken")
            elif lufs_integrated < -16:
                self.log(f"⚠️  Zu leise ({lufs_integrated:.1f} LUFS) - könnte lauter sein")
                self.log(f"   Empfehlung: Maximizer Gain um +{(-14) - lufs_integrated:.1f} dB anheben")
            else:
                self.log(f"ℹ️  Akzeptabel ({lufs_integrated:.1f} LUFS)")

            if true_peak_db <= -1.0:
                self.log("✅ True Peak: SICHER (≤ -1 dBFS)")
            elif true_peak_db <= -0.1:
                self.log("⚠️  True Peak: GRENZWERTIG - besser -1 dBFS")
            else:
                self.log("❌ True Peak: RISIKO - kann clippen!")

            # Ozone 12 Empfehlungen
            self.log("\n🎛️  OZONE 12 EMPFEHLUNGEN")
            self.log("-" * 30)

            if lufs_integrated > -13:
                self.log(f"• Maximizer Gain: {lufs_integrated - (-14):.1f} dB RUNTER")
            elif lufs_integrated < -15:
                self.log(f"• Maximizer Gain: +{(-14) - lufs_integrated:.1f} dB HOCH")
            else:
                self.log("• Maximizer Gain: PERFEKT, so lassen")

            self.log("• Maximizer Ceiling: -1.0 dBFS (True Peak ON)")
            self.log("• EQ Low-Cut: ~30 Hz (High-Pass Filter)")

            # Spektrum erstellen
            self.log("\n📈 Erstelle Frequenzspektrum...")
            self.create_spectrum(y_mono, sr, filename)

            self.status_var.set("✅ Analyse abgeschlossen!")

            # Erfolgs-Popup
            messagebox.showinfo("Analyse abgeschlossen", 
                              f"Die Analyse von '{os.path.basename(filename)}' wurde erfolgreich abgeschlossen!\n\n"
                              f"LUFS: {lufs_integrated:.2f}\n"
                              f"True Peak: {true_peak_db:.2f} dBFS\n\n"
                              f"Spektrum wurde als PNG gespeichert.")

        except Exception as e:
            error_msg = f"❌ Fehler bei der Analyse: {e}"
            self.log(error_msg)
            messagebox.showerror("Analysefehler", error_msg)
            self.status_var.set("❌ Fehler bei der Analyse")

    def create_spectrum(self, y_mono, sr, filename):
        """Erstellt und speichert das Frequenzspektrum"""
        try:
            fft = np.fft.rfft(y_mono)
            freqs = np.fft.rfftfreq(len(y_mono), d=1/sr)
            fft_db = 20*np.log10(np.abs(fft) + 1e-12)

            plt.figure(figsize=(12, 6))
            plt.semilogx(freqs, fft_db, color="red", linewidth=1)
            plt.title(f"Frequenzspektrum - {os.path.basename(filename)}")
            plt.xlabel("Frequenz (Hz)")
            plt.ylabel("Amplitude (dB)")
            plt.xlim(20, 20000)
            plt.ylim(np.max(fft_db) - 80, np.max(fft_db) + 5)
            plt.grid(True, which="both", ls="--", alpha=0.3)

            # Frequenzbereiche markieren
            plt.axvline(x=100, color='gray', linestyle=':', alpha=0.5, label='Sub-Bass')
            plt.axvline(x=500, color='orange', linestyle=':', alpha=0.5, label='Low-Mid')
            plt.axvline(x=2000, color='green', linestyle=':', alpha=0.5, label='Mid')
            plt.axvline(x=8000, color='blue', linestyle=':', alpha=0.5, label='High')
            plt.legend()

            plt.tight_layout()

            # Spektrum speichern
            base_name = os.path.splitext(filename)[0]
            spectrum_filename = f"{base_name}_spectrum.png"
            plt.savefig(spectrum_filename, dpi=150, bbox_inches='tight')
            plt.close()  # Fenster schließen, damit es nicht hängen bleibt

            self.log(f"💾 Spektrum gespeichert: {os.path.basename(spectrum_filename)}")

        except Exception as e:
            self.log(f"⚠️  Spektrum konnte nicht erstellt werden: {e}")

    def run(self):
        """Startet die GUI"""
        self.root.mainloop()

# Hauptprogramm
if __name__ == "__main__":
    try:
        app = LUFSAnalyzer()
        app.run()
    except Exception as e:
        # Fallback für kritische Fehler
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Kritischer Fehler", 
                           f"Das Programm konnte nicht gestartet werden:\n{e}\n\n"
                           f"Stelle sicher, dass folgende Pakete installiert sind:\n"
                           f"pip install soundfile pyloudnorm matplotlib numpy")
        sys.exit(1)
