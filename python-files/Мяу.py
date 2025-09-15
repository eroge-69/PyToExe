import subprocess
import os
import serial
import serial.tools.list_ports
import time
import subprocess

HEX_FILE = "file1.hex"
BIN_FILE = "firmware.bin"
BAUDRATE = 115200
FONT_FILE = 'betaflight.mcm'
DUMP_FILE = 'file2.txt'

# MSP_API_VERSION = 1
# MSP_SET_ARMING_DISABLED = 209

TARGET_KEYWORDS = [
    "STM", "Silicon", "CP210", "CH340", "Virtual COM", "USB Serial", "Betaflight"
]


def convert_hex_to_bin(hex_file, bin_file):
    if not os.path.exists(hex_file):
        print(f"[!] Файл .hex не найден: {hex_file}")
        return False

    #print("[*] Конвертация .hex → .bin ...")
    try:
        subprocess.run([
            "arm-none-eabi-objcopy",
            "-I", "ihex",
            "-O", "binary",
            hex_file, bin_file
        ], check=True)
        #print("[✓] Успешно сконвертировано:", bin_file)
        return True
    except FileNotFoundError:
        print("[!] Команда 'arm-none-eabi-objcopy' не найдена. Установи ARM Toolchain и добавь её в PATH.")
    except subprocess.CalledProcessError as e:
        print("[!] Ошибка при конвертации:", e)
    return False

def check_dfu():
    try:
        output = subprocess.check_output(["dfu-util", "-l"], text=True)
        if "Found DFU" in output:
            print("[✓] Полётник в DFU-режиме обнаружен.")
            return True
        else:
            print("[!] DFU-устройство не найдено.")
            time.sleep(1)
            return False
    except FileNotFoundError:
        print("[!] dfu-util не установлен или не найден в PATH.")
        return False

def flash_firmware(bin_file):
    if not os.path.exists(bin_file):
        print(f"[!] Файл прошивки .bin не найден: {bin_file}")
        return False

    print("[*] Начинаю прошивку...")
    try:
        subprocess.run([
            "dfu-util",
            "-a", "0",
            "-s", "0x08000000:leave",
            "-D", bin_file
        ], check=True)
        print("[✓] Прошивка завершена успешно.")
        return True
    except subprocess.CalledProcessError as e:
        print("[!] Ошибка при прошивке:", e)
        return False

def find_fc_port(delay=1, max_attempts=1000):
    attempts = 0
    while attempts < max_attempts:
        if attempts > 0:
            print(f"❌ COM-порты не найдены. Повтор попытки через {delay} секунд...")
            time.sleep(delay)

        ports = list(serial.tools.list_ports.comports())
        candidates = []

        for p in ports:
            if p.pid is not None and p.pid != 0:
                desc = p.description.lower()
                if any(k.lower() in desc for k in TARGET_KEYWORDS):
                    print(f"✅ Найден подходящий порт: {p.device} ({p.description})")
                    return p.device
                candidates.append(p)

        if len(candidates) == 1:
            print(f"✅ Найден единственный кандидат: {candidates[0].device} ({candidates[0].description})")
            return candidates[0].device

        if candidates:
            print("⚠️ Автоопределение не сработало. Доступные порты с PID!=0:")
            for i, p in enumerate(candidates):
                print(f"{i+1}. {p.device}: {p.description}")

            try:
                selection = int(input("🔧 Введите номер нужного порта: ")) - 1
                if 0 <= selection < len(candidates):
                    return candidates[selection].device
                else:
                    print("❌ Неверный выбор.")
            except ValueError:
                print("❌ Неверный ввод.")
        else:
            attempts += 1

    print("[!] Не удалось найти подходящий COM-порт.")
    return None

def load_bin_file(path):
    with open(path, 'rb') as f:
        return f.read()

def load_txt_dump(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def send_osd_font(ser, font_data):
    if len(font_data) != 13824:
        print("❌ Неверный размер шрифта: должно быть 256 символов по 54 байта.")
        return False

    def build_msp_packet(cmd, payload):
        packet = bytearray()
        packet.extend(b"$M<")
        packet.append(len(payload))
        packet.append(cmd)
        packet.extend(payload)
        checksum = len(payload) ^ cmd
        for b in payload:
            checksum ^= b
        packet.append(checksum)
        return packet

    print("📡 Отправка MSP_DISPLAYPORT (0x6C)...")
    ser.write(build_msp_packet(0x6C, b''))
    time.sleep(0.1)

    print("🔠 Загрузка 256 символов через 0x57...")
    for i in range(256):
        payload = bytes([i]) + font_data[i*54:(i+1)*54]
        packet = build_msp_packet(0x57, payload)
        ser.write(packet)
        time.sleep(0.03)
        print(f"  Загружено: {i+1}/256", end='\r')

    print("\n💾 Сохраняем в EEPROM (0x46)...")
    ser.write(build_msp_packet(0x46, b''))
    time.sleep(3)

    print("✅ Шрифт загружен.")
    return True

def print_progress(current, total, bar_len=40):
    filled_len = int(bar_len * current // total)
    bar = '█' * filled_len + '-' * (bar_len - filled_len)
    percent = int(current * 100 / total)
    print(f'\r[{bar}] {percent}% ({current}/{total})', end='', flush=True)

def msp_build(cmd, data=b''):
    size = len(data)
    checksum = size ^ cmd
    for b in data:
        checksum ^= b
    return b'$M<' + bytes([size, cmd]) + data + bytes([checksum])

def msp_send(ser, cmd, data=b''):
    packet = msp_build(cmd, data)
    ser.write(packet)

def msp_recv(ser):
    time.sleep(0.1)
    return ser.read_all()

def send_dump(ser, dump_text):
    try:
        print("⏫ Переход в CLI режим...")
        ser.write(b"#\n")
        ser.flush()
        time.sleep(1)
        output = ser.read_all().decode(errors='ignore')
        if output.strip():
            print("Ответ при входе в CLI:", output.strip())
        else:
            print("⚠️ Не удалось подтвердить вход в CLI. Пробуем 'cli\\n'")
            ser.write(b"cli\n")
            ser.flush()
            time.sleep(0.5)
            output = ser.read_all().decode(errors='ignore')
            if output.strip():
                print("Ответ при входе в CLI (cli):", output.strip())
            else:
                print("❌ CLI режим не активирован.")
                return False

        print("⏫ Отправка дампа настроек...")
        lines = dump_text.splitlines()
        for line in lines:
            ser.write((line + '\n').encode('utf-8'))
            ser.flush()
            time.sleep(0.02)
            response = ser.read_all().decode(errors='ignore')
            if response.strip():
                print(response.strip())

        print("⏫ Отправка команды save...")
        ser.write(b"save\n")
        ser.flush()

        print("⏳ Ждём 5 секунд после команды save, полётник может отключиться...")
        time.sleep(5)

        try:
            ser.close()
        except Exception:
            pass

        return True

    except Exception as e:
        print(f"❌ Ошибка при отправке дампа: {e}")
        try:
            ser.close()
        except Exception:
            pass
        return False

def osd_cli_stage():
    port = find_fc_port()
    if not port:
        print("[!] COM-порт не найден, этап OSD/CLI пропущен.")
        return None

    if not os.path.isfile(FONT_FILE):
        print(f"[!] Файл шрифта '{FONT_FILE}' не найден.")
        return None

    if not os.path.isfile(DUMP_FILE):
        print(f"[!] Файл дампа '{DUMP_FILE}' не найден.")
        return None

    font_data = load_bin_file(FONT_FILE)
    dump_text = load_txt_dump(DUMP_FILE)

    try:
        # Отправка шрифта и сохранение (с закрытием порта)
        with serial.Serial(port, BAUDRATE, timeout=2) as ser:
            print(f"📡 Подключение к {port} для отправки шрифта.")
            font_result = send_osd_font(ser, font_data)
            if not font_result:
                print("[!] Ошибка при отправке и сохранении OSD шрифта.")
                return None

        print("⏳ Ждём 5 секунд для перезагрузки контроллера...")
        time.sleep(5)

        # Повторное открытие порта для отправки дампа
        with serial.Serial(port, BAUDRATE, timeout=2) as ser:
            print(f"📡 Повторное подключение к {port} для отправки дампа CLI.")
            dump_result = send_dump(ser, dump_text)
            if dump_result:
                print("[✓] Этап OSD/CLI успешно завершён.")
                return port
            else:
                print("[!] Ошибка при отправке дампа CLI.")
                return None

    except serial.SerialException as e:
        print(f"[!] Ошибка открытия порта: {e}")
        return None

def msp_packet(cmd, payload=b''):
    header = b'$M<'
    length = len(payload)
    packet = header + bytes([length]) + bytes([cmd]) + payload
    checksum = 0
    for b in packet[3:]:
        checksum ^= b
    packet += bytes([checksum])
    return packet

def calibration_stage(port):
    if not port:
        print("[!] Нет порта для калибровки.")
        return False

    try:
        ser = serial.Serial(port, BAUDRATE, timeout=2)
        time.sleep(2)

        pkt = msp_packet(205)
        print("Отправляем MSP_CALIBRATE_ACCELEROMETER")
        ser.write(pkt)
        ser.flush()

        time.sleep(2)
        resp = ser.read_all()
        print("Ответ:", resp)

        pkt_save = msp_packet(244)
        print("Отправляем MSP_SAVE")
        ser.write(pkt_save)
        ser.flush()

        time.sleep(2)
        resp_save = ser.read_all()
        print("Ответ на сохранение:", resp_save)

        ser.close()
        print("[✓] Калибровка завершена.")
        return True
    except serial.SerialException as e:
        print(f"[!] Ошибка открытия порта для калибровки: {e}")
        return False

def main():
    success_count = 0
    while True:
        print("\n\033[94m[*] Запуск прошивки и настройки, developed by spektor...\033[0m\n")
        #print("\n[*] Запуск прошивки и настройки, developed by spektor...\n")

        if not convert_hex_to_bin(HEX_FILE, BIN_FILE):
            print("[!] Конвертация не удалась. Начинаем сначала.")
            time.sleep(1)
            #input("Нажмите Enter, чтобы повторить...")
            continue

        #input("Переведите полётник в DFU-режим и нажмите Enter...")

        if not check_dfu():
            #print("[!] Устройство не в DFU-режиме. Начинаем сначала.")
            os.system("cls")
            #input("Нажмите Enter, чтобы повторить...")
            continue

        if not flash_firmware(BIN_FILE):
            print("[!] Прошивка не удалась. Начинаем сначала.")
            time.sleep(1)
            #input("Нажмите Enter, чтобы повторить...")
            continue

       # print("\n[!] Отключите и снова подключите полётник для поиска COM-порта.")
        print("⏳ Ждем 5 секунд перед поиском COM-порта...")
        time.sleep(1)

        port = osd_cli_stage()
        if not port:
            print("[!] Этап OSD/CLI не завершён. Начинаем сначала.")
            time.sleep(1)
            #input("Нажмите Enter, чтобы повторить...")
            continue

        if not calibration_stage(port):
            print("[!] Калибровка не завершена. Начинаем сначала.")
            time.sleep(1)
            input("Нажмите Enter, чтобы повторить...")
            continue

        os.system("cls")
        print("\n[✓] ✅✅Все этапы прошли успешно! Перезапуск процесса.")
        success_count += 1
        print(f"📊 Успешных прошивок: {success_count}")
        time.sleep(2)
        os.startfile(r"C:\Users\user\Desktop\start.mcr")
       # input("Нажмите Enter для повторного запуска...\n")

if __name__ == '__main__':
    main()
