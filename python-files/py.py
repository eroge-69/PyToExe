from pathlib import Path
import zipfile

# AutoHotkey-Skript f�r das gew�nschte Verhalten
ahk_script = r"""
#NoTrayIcon
MsgBox, 64, Hinweis, Du bist geliefert!
StartTime := A_TickCount

SetTimer, Chaos, 100
return

Chaos:
if (A_TickCount - StartTime > 30000) ; 30 Sekunden
    ExitApp

Random, moveX, -100, 100
Random, moveY, -100, 100
MouseMove, moveX, moveY, 0, R

Random, key, 65, 90
Send, % Chr(key)

Random, freq, 500, 1500
Random, dur, 100, 300
SoundBeep, %freq%, %dur%
return

Esc::ExitApp
"""

# Speicherort
script_path = Path("/mnt/data/chaos_script.ahk")
exe_path = Path("/mnt/data/chaos_script.exe")
zip_path = Path("/mnt/data/chaos_script.zip")

# Skript speichern
script_path.write_text(ahk_script, encoding="utf-8")

# ZIP-Datei mit dem Skript erzeugen (statt .exe, da Kompilierung extern erfolgen m�sste)
with zipfile.ZipFile(zip_path, "w") as zipf:
    zipf.write(script_path, arcname="chaos_script.ahk")

zip_path.name  # R�ckgabe des Dateinamens zur Anzeige

