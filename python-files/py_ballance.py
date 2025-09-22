import serial
import serial.tools.list_ports
import time

def select_com_port():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("COM порты не найдены")
        return None
    print("Доступные COM порты:")
    for i, port in enumerate(ports):
        print(f"{i}: {port.device} - {port.description}")
    idx = input("Выберите номер порта: ")
    try:
        idx = int(idx)
        if 0 <= idx < len(ports):
            return ports[idx].device
        else:
            print("Неверный номер порта")
            return None
    except ValueError:
        print("Введите число")
        return None

port_name = select_com_port()
if port_name:
    ser = serial.Serial(
        port=port_name,
        baudrate=9600,
        bytesize=8,
        parity='N',
        stopbits=1,
        timeout=2
    )

    with open("ballance.txt", "a", encoding="utf-8") as file:  # Открываем файл для добавления данных
        while True:
            data = ser.readline()
            try:
                decoded_data = data.decode("ascii").strip()
                print(decoded_data)
                file.write(decoded_data + "\n")  # Записываем данные в файл с новой строки
                file.flush()  # Принудительно сбрасываем буфер записи в файл
            except Exception:
                pass
            time.sleep(60)  # Задержка 1 минута перед следующим чтением
else:
    print("Порт не выбран")
