from pathlib import Path
import zipfile

# AutoHotkey-Skript für das gewünschte Verhalten
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

