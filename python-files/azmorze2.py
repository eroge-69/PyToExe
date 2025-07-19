import pyaudio
import numpy as np
from scipy.fft import fft, fftfreq
import time
import collections

# --- Параметры аудиопотока ---
CHUNK = 1024        # Размер буфера (количество семплов за один раз)
SAMPLE_RATE = 44100 # Частота дискретизации аудио (семплов в секунду)
MORSE_FREQ = 1000    # Ожидаемая частота тона Морзе в Гц (наиболее распространенная 500-1000 Гц)
AUDIO_THRESHOLD = 0.05 # Порог громкости для распознавания тона (от 0 до 1, экспериментально!)

# --- Параметры для определения точек, тире и пауз ---
# Эти параметры должны быть согласованы с тем, как вы будете "отбивать" Морзе.
# Если вы используете медленные нажатия, увеличьте unit_time_ms.
unit_time_ms = 100 # Базовая единица времени в миллисекундах (как в правилах Морзе)

# Пороговые значения для определения точек и тире
dot_duration_threshold_ms = unit_time_ms * 1.5   # Нажатие, короче этого, считается точкой
dash_duration_threshold_ms = unit_time_ms * 2.5# Нажатие, длиннее этого, считается тире

# Пороговые значения для определения пауз
inter_element_pause_threshold_ms = unit_time_ms * 1 # Пауза между точкой и тире внутри одной буквы
inter_letter_pause_threshold_ms = unit_time_ms * 3 # Пауза между буквами (от 3 базовых единиц)
inter_word_pause_threshold_ms = unit_time_ms * 7   # Пауза между словами (от 7 базовых единиц и более)

# --- Словарь Морзе (английский + русский алфавит) ---
morse_codes = {
    # Русский алфавит (стандартная русская морзянка)
    'а': 'dot dash',         'б': 'dash dot dot dot',   'в': 'dot dash dash',
    'г': 'dash dash dot',    'д': 'dash dot dot',       'е': 'dot',
    'ж': 'dot dot dot dash', 'з': 'dash dash dot dot', 'и': 'dot dot',
    'й': 'dot dash dash dash', 'к': 'dash dot dash',    'л': 'dot dash dot dot',
    'м': 'dash dash',        'н': 'dash dot',           'о': 'dash dash dash',
    'п': 'dot dash dash dot', 'р': 'dot dash dot',      'с': 'dot dot dot',
    'т': 'dash',             'у': 'dot dot dash',       'ф': 'dot dot dash dot',
    'х': 'dot dot dot dot', 'ц': 'dash dot dash dot', 'ч': 'dash dash dash dot',
    'ш': 'dash dash dash dash', 'щ': 'dash dash dot dash', 'ъ': 'dash dash dot dash dash',
    'ы': 'dash dot dash dash', 'ь': 'dash dot dot dash', 'э': 'dot dot dash dot dot',
    'ю': 'dot dot dash dash', 'я': 'dot dash dot dash',

}

# --- Инвертируем словарь для дешифрования ---
inverted_morse_codes = {v: k for k, v in morse_codes.items()}

# --- Переменные состояния дешифратора ---
current_morse_char_elements = [] # Список для хранения 'dot' или 'dash' для текущей буквы
decoded_text = ""                 # Общий дешифрованный текст

is_tone_active = False            # Флаг, указывающий, активен ли тон Морзе
tone_start_time = 0               # Время начала текущего тона (мс)
last_event_time = time.time() * 1000 # Время последнего события (начало тона или конец тона) в мс

# --- PyAudio Setup ---
p = pyaudio.PyAudio()

# Выбор устройства ввода (микрофона)
# Вы можете раскомментировать и использовать эту часть, чтобы выбрать конкретный микрофон
# info = p.get_host_api_info_by_index(0)
# num_devices = info.get('deviceCount')
# print("Доступные аудиоустройства:")
# for i in range(0, num_devices):
#     if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
#         print("ID:", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
# device_index = int(input("Введите ID микрофона для использования (по умолчанию 0): ") or 0)

stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=SAMPLE_RATE,
                input=True,
                frames_per_buffer=CHUNK,
                # input_device_index=device_index # Раскомментировать, если выбрали устройство
                )

print(f"--- Морзе Дешифратор (Аудио) ---")
print(f"Ожидаемый тон Морзе: {MORSE_FREQ} Гц")
print(f"Порог аудио: {AUDIO_THRESHOLD} (может потребоваться корректировка)")
print(f"Единица времени: {unit_time_ms} мс (настройте под свою скорость)")
print("Начните воспроизводить звуки Морзе через микрофон.")
print("Для выхода нажмите Ctrl+C.")
print("---------------------------------")
print("Декодировано: ", end="")

# --- Вспомогательная функция для обработки текущей буквы ---
def process_current_char():
    global current_morse_char_elements, decoded_text
    if current_morse_char_elements: # Если есть элементы для дешифрования
        morse_sequence_str = " ".join(current_morse_char_elements)
        decoded_char = inverted_morse_codes.get(morse_sequence_str, '[?]') # Если не найдено, ставим '[?]'
        decoded_text += decoded_char
        print(f"\rДекодировано: {decoded_text}", end="", flush=True)
        current_morse_char_elements = [] # Сбрасываем для следующей буквы

# --- Основной цикл дешифрования ---
try:
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False) # Читаем данные из микрофона
        audio_data = np.frombuffer(data, dtype=np.int16) # Преобразуем в массив numpy

        # Нормализуем данные для FFT (приводим к диапазону -1.0 до 1.0)
        normalized_audio = audio_data / 32768.0

        # Выполняем FFT
        N = len(normalized_audio)
        yf = fft(normalized_audio)
        xf = fftfreq(N, 1 / SAMPLE_RATE)

        # Находим индекс частоты, соответствующей MORSE_FREQ
        # abs(xf - MORSE_FREQ) находит расстояние до MORSE_FREQ
        # argmin() находит индекс минимального расстояния
        freq_idx = np.argmin(np.abs(xf - MORSE_FREQ))

        # Получаем амплитуду на нужной частоте (берем абсолютное значение, так как FFT возвращает комплексные числа)
        amplitude = np.abs(yf[freq_idx]) / N # Нормализуем по количеству семплов

        current_time_ms = time.time() * 1000

        # --- Логика определения тона и пауз ---
        if amplitude > AUDIO_THRESHOLD: # Тон обнаружен
            if not is_tone_active: # Если тон только что начался
                is_tone_active = True
                tone_start_time = current_time_ms

                # Проверяем паузу перед этим тоном
                pause_duration = current_time_ms - last_event_time
                if pause_duration >= inter_word_pause_threshold_ms:
                    process_current_char()
                    decoded_text += " " # Добавляем пробел для нового слова
                    print(f"\rДекодировано: {decoded_text}", end="", flush=True)
                elif pause_duration >= inter_letter_pause_threshold_ms:
                    process_current_char() # Завершаем предыдущую букву

        else: # Тон не активен (тишина)
            if is_tone_active: # Если тон только что закончился
                is_tone_active = False
                tone_duration = current_time_ms - tone_start_time

                # Определяем, была ли это точка или тире
                if tone_duration < dot_duration_threshold_ms:
                    current_morse_char_elements.append('dot')
                    print(".", end="", flush=True)
                elif tone_duration >= dash_duration_threshold_ms:
                    current_morse_char_elements.append('dash')
                    print("-", end="", flush=True)
                else:
                    # Длительность тона неоднозначна
                    current_morse_char_elements.append('?')
                    print("?", end="", flush=True)

                last_event_time = current_time_ms

            # Если тон не активен и есть длительная пауза, но еще не конец слова/буквы
            else:
                # Автоматическое завершение буквы/слова, если долго нет сигнала
                current_pause_duration = current_time_ms - last_event_time
                if current_pause_duration >= inter_word_pause_threshold_ms and decoded_text and decoded_text[-1] != ' ':
                    process_current_char()
                    decoded_text += " "
                    print(f"\rДекодировано: {decoded_text}", end="", flush=True)
                    last_event_time = current_time_ms # Обновляем время, чтобы не добавлять много пробелов
                elif current_pause_duration >= inter_letter_pause_threshold_ms and current_morse_char_elements:
                    process_current_char()
                    last_event_time = current_time_ms # Обновляем время

        # Небольшая задержка, чтобы не нагружать процессор слишком сильно, если CHUNK очень маленький
        # time.sleep(CHUNK / SAMPLE_RATE / 2) # Можно поэкспериментировать

except KeyboardInterrupt:
    print("\nДешифратор остановлен.")
except Exception as e:
    print(f"\nПроизошла ошибка: {e}")
finally:
    # Очистка PyAudio ресурсов
    stream.stop_stream()
    stream.close()
    p.terminate()
