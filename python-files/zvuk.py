import argparse
import os
import sys
import time
import subprocess

def set_system_volume_max():
    """
    Устанавливает системную громкость на 100% (Windows Core Audio).
    Требует pycaw и comtypes.
    """
    try:
        from ctypes import POINTER, cast
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        try:
            volume.SetMute(10, None)
        except Exception:
            pass
        volume.SetMasterVolumeLevelScalar(1.0, None)
        print("[info] System volume set to 100%.")
    except ImportError:
        print("[warn] pycaw/comtypes не установлены. Пропускаю установку системной громкости.")
    except Exception as e:
        print(f"[warn] Не удалось установить громкость: {e}")
def ps_escape_single_quotes(s: str) -> str:
# Для PowerShell: экранируем одиночные кавычки
    return s.replace("'", "''")

def play_wav_once_in_new_process(wav_path: str):
    """
    Запускает скрытый PowerShell-процесс, который синхронно проигрывает WAV и завершается.
    Каждый вызов — отдельный процесс => можно накладывать воспроизведения.
    """
    escaped = ps_escape_single_quotes(wav_path)
    ps_script = (
    "[void][System.Reflection.Assembly]::LoadWithPartialName('System');"
    f"$sp = New-Object System.Media.SoundPlayer -ArgumentList '{escaped}';"
    "$sp.PlaySync();"
    )

    # Скрываем окно дочернего процесса
    creationflags = 0
    startupinfo = None
    if os.name == "nt":
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    # Запуск без ожидания (вернёт Popen сразу)
    return subprocess.Popen(
        ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps_script],
        startupinfo=startupinfo,
        creationflags=creationflags,
)

def main():
    parser = argparse.ArgumentParser(description="Windows WAV alarm loop with overlap")
    parser.add_argument("--period", type=float, default=0.1, help="Interval between starts, seconds (default: 1.0)") # <--- Изменено значение по умолчанию
    parser.add_argument("--setmax", action="store_true", help="Set system volume to 100% on start")
    args = parser.parse_args()

    # Файл sound.wav в той же директории, что и скрипт
    wav_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sound.wav")

    # Проверяем существует ли файл
    if not os.path.isfile(wav_path):
        print(f"[error] Файл не найден: {wav_path}")
        sys.exit(1)

    if not wav_path.lower().endswith(".wav"):
        print("[warn] Рекомендуется WAV-файл. System.Media.SoundPlayer поддерживает WAV.")
        # Можно продолжить, но проигрывание, вероятно, не сработает для других форматов.

    if args.setmax:
        set_system_volume_max()
    else:
        print("[info] System volume will not be set to 100%. Use --setmax to enable.")

    procs = []
    print("Старт. Каждую период секунду будет запускаться новое проигрывание. Нажмите Ctrl+C для остановки.")
    try:
        while True:
            p = play_wav_once_in_new_process(wav_path)
            procs.append(p)
            # Чистим завершившиеся процессы
            procs = [pp for pp in procs if pp.poll() is None]
            time.sleep(max(0.0, args.period))
    except KeyboardInterrupt:
        print("Остановка...")
    finally:
    # Процессы сами завершаются после доигрывания; тут просто ждём, если нужно
        pass

if __name__ == "__main__":
    # Предупреждение о громкости
    if sys.stdout.isatty():
        print("ВНИМАНИЕ: будет возможна максимальная системная громкость и наложение звуков.")
        main()
