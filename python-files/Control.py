import speech_recognition as sr
import keyboard
import time
import sys
import os

def is_admin():
    """Проверяем, запущен ли скрипт от имени администратора"""
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()

def setup_microphone():
    """Настройка микрофона с обработкой ошибок"""
    try:
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        print("Настройка микрофона...")
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Микрофон настроен!")
        return recognizer, microphone
    except Exception as e:
        print(f"Ошибка настройки микрофона: {e}")
        print("Проверьте, подключен ли микрофон и доступен ли он для программы")
        return None, None

def listen_for_command(recognizer, microphone):
    """Слушает микрофон и возвращает распознанный текст"""
    try:
        with microphone as source:
            print("🎤 Слушаю...")
            audio = recognizer.listen(source, phrase_time_limit=4, timeout=5)
        
        text = recognizer.recognize_google(audio, language="ru-RU")
        print(f"📝 Распознано: {text}")
        return text.lower()
    
    except sr.WaitTimeoutError:
        return ""
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print(f"❌ Ошибка сервиса распознавания: {e}")
        return ""
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return ""

def next_track():
    """Переключает на следующий трек"""
    try:
        keyboard.send("next track")
        print("✅ Следующий трек!")
        return True
    except Exception as e:
        print(f"❌ Ошибка переключения трека: {e}")
        return False

def previous_track():
    """Возвращает к предыдущему треку"""
    try:
        keyboard.send("previous track")
        print("✅ Предыдущий трек!")
        return True
    except Exception as e:
        print(f"❌ Ошибка возврата трека: {e}")
        return False

def play_pause():
    """Ставит на паузу или возобновляет воспроизведение"""
    try:
        keyboard.send("play/pause")
        print("✅ Пауза/Воспроизведение!")
        return True
    except Exception as e:
        print(f"❌ Ошибка паузы: {e}")
        return False

def process_command(command):
    """Обрабатывает голосовые команды"""
    command = command.lower().strip()
    
    # Команда переключения трека вперед
    if any(phrase in command for phrase in ["переключи трек", "следующий трек"]):
        next_track()
    
    # Команда возврата к предыдущему треку
    elif any(phrase in command for phrase in ["верни трек", "предыдущий трек"]):
        previous_track()
    
    # Команда паузы/воспроизведения
    elif any(phrase in command for phrase in ["пауза", "останови"]):
        play_pause()
    
    # Помощь по командам
    elif any(phrase in command for phrase in ["помощь", "команды", "help"]):
        print_help()
    
    else:
        print("❌ Команда не распознана. Скажите 'помощь' для списка команд.")

def print_help():
    """Выводит список доступных команд"""
    print("\n📋 Доступные команды:")
    print("  • 'переключи трек' - следующий трек")
    print("  • 'верни трек' - предыдущий трек")
    print("  • 'пауза' - пауза/воспроизведение")
    print("  • 'помощь' - этот список команд\n")

def main():
    print("🎵 Голосовое управление Яндекс.Музыкой")
    print("=" * 40)
    
    # Проверка прав администратора
    if not is_admin():
        print("⚠️  Совет: Если медиа-клавиши не работают, попробуйте запустить VS Code от имени администратора")
    
    # Настройка микрофона
    recognizer, microphone = setup_microphone()
    if recognizer is None:
        print("❌ Не удалось настроить микрофон. Скрипт завершает работу.")
        return
    
    print("✅ Скрипт готов к работе!")
    print_help()
    print("🗣️  Произнесите одну из команд")
    print("⏹️  Для выхода нажмите Ctrl+C\n")
    
    try:
        while True:
            command = listen_for_command(recognizer, microphone)
            
            if command:
                process_command(command)
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n👋 Скрипт завершен пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    main()