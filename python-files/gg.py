import hid
import time
import re

# VID/PID UT61B+
VID = 0x1a86
PID = 0xe429

# Пакеты — 64 байта полезной нагрузки
KEEP_ALIVE_DATA = [
    0x06, 0xab, 0xcd, 0x03, 0x5e, 0x01, 0xd9
] + [0x00] * 57  # Всего 64 байта

ACTIVATE_S_DATA = [0xA0, 0x00, 0x20] + [0x00] * 5  # 64 байта

# Функция отправки: [Report ID] + данные → всего 65 байт
def send_report(device, data, report_id=0):
    packet = [report_id] + list(data)
    if len(packet) < 65:
        packet += [0] * (65 - len(packet))
    device.write(packet)


def parse_data(data):
    try:
        raw = bytes(data)

        # Ищем сигнатуру b'0  ' — это начало числа
        start_marker = b'\x30\x20\x20'  # "0  "
        start_idx = raw.find(start_marker)
        if start_idx == -1:
            return None

        # Число начинается сразу после "0  "
        value_start = start_idx + 3
        # Берём 7 байт: например, "3.71600"
        candidate = raw[value_start:value_start + 7]

        # Извлекаем только "X.XXX" — первые 5 символов
        number_str = candidate[:5].decode('ascii', errors='ignore')

        # Проверяем формат: цифра, точка, три цифры
        if re.match(r'\d\.\d{3}', number_str):
            # Единицы измерения — ищем по контексту
            unit = '?'
            if b'V=' in raw or b'V~' in raw:
                unit = 'V'
            elif b'A=' in raw or b'A~' in raw:
                unit = 'A'
            elif b'OHM' in raw or b'\xa9' in raw:  # \xa9 = Ω в CP866
                unit = 'Ω'
            elif b'F' in raw:
                unit = 'F'

            return f"📊 {number_str} {unit}"

        # Проверка на OL (перегрузка)
        if b'OL' in raw:
            unit = 'V' if b'V' in raw else 'A' if b'A' in raw else 'Ω' if b'\xa9' in raw else '?'
            return f"⚠️ OL {unit}"

        return None

    except Exception as e:
        print(f"\n❌ Ошибка парсинга: {e}")
        return None


def main():
    print("🔍 Подключение к UT61B+...")
    try:
        h = hid.device()
        h.open(VID, PID)
        h.set_nonblocking(True)
        print("✅ Устройство открыто.")

        print("🔄 Отправка инициализации...")

        # Отправляем keep-alive и активацию с Report ID = 0
        send_report(h, KEEP_ALIVE_DATA)
        time.sleep(0.1)

        send_report(h, KEEP_ALIVE_DATA)
        time.sleep(0.1)

        send_report(h, ACTIVATE_S_DATA)
        time.sleep(0.5)

        send_report(h, KEEP_ALIVE_DATA)
        time.sleep(0.1)

        print("📡 Ожидание данных... (должен гореть 'S')")
        print("-" * 60)

        # Основной цикл — поддерживаем сессию и читаем данные
        for _ in range(500):  # ~1 минута
            send_report(h, KEEP_ALIVE_DATA)  # Keep-alive каждые 110 мс
            data = h.read(64, timeout_ms=300)  # Читаем 64 байта
            if data:
                result = parse_data(data)
                if result and "📡" not in result:
                    print(result)
                elif result:
                    print(".", end="", flush=True)  # Визуальный прогресс
            time.sleep(0.11)  # Общий интервал ~110 мс

    except Exception as ex:
        print(f"\n❌ Ошибка: {ex}")
    finally:
        if 'h' in locals():
            h.close()
            print("\n🔌 Устройство закрыто.")

if __name__ == "__main__":
    main()
