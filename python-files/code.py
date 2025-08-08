import serial
import struct

# Конфигурация порта
port = "COM4"  # Замените на свой COM-порт
baudrate = 9600

# Функция для чтения данных из последовательного порта
def read_data(ser):
    """Читает данные из последовательного порта до достижения конца пакета."""
    data = bytearray()
    while True:
        byte = ser.read(1)
        if not byte:
            break  # Таймаут
        data += byte
        if len(data) >= 32:  # Пакет данных всегда 32 байта
            break
    return data

# Функция для проверки контрольной суммы
def check_checksum(data):
    """Проверяет контрольную сумму."""
    if len(data) != 32:
        return False, 0

    calculated_checksum = sum(data[:30])
    received_checksum = struct.unpack(">H", data[30:32])[0] # Unpack as big-endian unsigned short
    
    return calculated_checksum == received_checksum, calculated_checksum, received_checksum


# Функция для разбора данных
def parse_data(data):
    """Разбирает 32-байтовый пакет данных PMS5003."""
    if len(data) != 32:
        print("Некорректная длина данных.")
        return None

    # Проверяем стартовые байты
    if data[0] != 0x42 or data[1] != 0x4d:
        print("Неправильные стартовые байты.")
        return None
    
    # Проверка контрольной суммы
    checksum_ok, calculated_checksum, received_checksum = check_checksum(data)
    if not checksum_ok:
        print(f"Ошибка контрольной суммы. Вычислено: {calculated_checksum}, Получено: {received_checksum}")
        return None

    # Разбираем данные (используем struct.unpack для удобства)
    pm1_0_standard, pm2_5_standard, pm10_standard, \
    pm1_0_atmospheric, pm2_5_atmospheric, pm10_atmospheric, \
    particles_0_3um, particles_0_5um, particles_1_0um, \
    particles_2_5um, particles_5_0um, particles_10um, \
    reserved, checksum = struct.unpack(">HHHHHHHHHHHHHH", data[2:]) # Big Endian

    # Возвращаем данные в виде словаря
    return {
        "PM1.0_standard": pm1_0_standard,
        "PM2.5_standard": pm2_5_standard,
        "PM10_standard": pm10_standard,
        "PM1.0_atmospheric": pm1_0_atmospheric,
        "PM2.5_atmospheric": pm2_5_atmospheric,
        "PM10_atmospheric": pm10_atmospheric,
        "particles_0.3um": particles_0_3um,
        "particles_0.5um": particles_0_5um,
        "particles_1.0um": particles_1_0um,
        "particles_2.5um": particles_2_5um,
        "particles_5.0um": particles_5_0um,
        "particles_10um": particles_10um,
        "reserved": reserved,
        "checksum": checksum
    }

# Основной код
try:
    ser = serial.Serial(port, baudrate)
    print(f"Подключено к порту {port} на скорости {baudrate}")

    while True:
        data = read_data(ser)

        if data:
            parsed_data = parse_data(data)
            if parsed_data:
                print("Данные PMS5003:")
                for key, value in parsed_data.items():
                    print(f"  {key}: {value}")
                print("-" * 20)
        else:
            print("Нет данных.  Проверьте подключение и скорость передачи.")

except serial.SerialException as e:
    print(f"Ошибка подключения к порту: {e}")
except KeyboardInterrupt:
    print("Завершение программы.")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Последовательный порт закрыт.")