import sys
import argparse
import struct
import json
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException
from pymodbus.pdu import ExceptionResponse
import serial.tools.list_ports

# Предварительная настройка мастера
COM_PORT = 'COM7'
SLAVE_ID = 1
BAUDRATE = 9600

# Инициализация modbus клиента
client = ModbusSerialClient(
    port=COM_PORT, 
    baudrate=BAUDRATE, 
    stopbits=2, 
    bytesize=8, 
    parity='N'
)

# Максимальное количество регистров за передачу
MAX_REG_QUANTITY = 32767 # 32767 согласно документации modbus

# Класс записи в словаре
class Record:
    """ Класс записи в словаре """

    # Конструктор класса
    def __init__(self, list):
        self.name = list[0]
        self.type = list[1]
        self.access = list[2]
        self.min = list[3]
        self.max = list[4]
        self.read_err = list[5]
        self.write_err = list[6]
        self.all = list

# Проверка подключения modbus-интерфейса
def check_port_exists(port_name):
    """Проверка подключения modbus-интерфейса"""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if port.device == port_name:
            return True
    return False

def convert_to_registers(value, addr, dict):
    """Конвертирует значение в список 16-битных регистров (big-endian)."""
    result_list = []
    dict_keys = list(dict.keys())
    reg_id = 0
    for key in dict_keys:
        if int(key) < int(addr): continue
        if reg_id >= len(value): break

        record = Record(dict[key])

        if record.access == "mb_read_only":
            print("❌ Ошибка: попытка записи в регистр только для чтения.")
            client.close()
            sys.exit()

        match record.type:
            case "ui16": result_list.append(int(value[reg_id]))[0]
            case "i16" : result_list.append(int(value[reg_id]) & 0xFFFF)[0]
            case "ui32":
                tmp = struct.unpack(">HH", struct.pack(">I",   int(value[reg_id])))
                result_list.extend(tmp)
            case "i32" :
                tmp = struct.unpack(">HH", struct.pack(">i",   int(value[reg_id])))
                result_list.extend(tmp)
            case "f32" :
                tmp = struct.unpack(">HH", struct.pack(">f", float(value[reg_id])))
                result_list.extend(tmp)
            case _ : raise ValueError("Неподдерживаемый тип данных")
        ++reg_id
    return result_list

#Читаем регистры
#TODO: Добавить проверки
def read_registers(client, addr, dict, quantity):
    """Считывает значение из Modbus-регистров в зависимости от типа данных."""
    result_list = []
    try:
        response = client.read_holding_registers(address=addr, count=quantity, slave=SLAVE_ID)

        if isinstance(response, ExceptionResponse):
            print(f"❌ Modbus-exeption: код {response.exception_code}")
        elif response.isError():
            print(f"❌ Ошибка Modbus: {response}")
        else:
            registers = response.registers
            dict_keys = list(dict.keys())
            reg_id = 0
            for key in dict_keys:
                if int(key) < int(addr): continue
                if reg_id >= quantity: break

                record = Record(dict[key])
                match record.type:
                    case "ui16": value = registers[reg_id]
                    case "i16" : value = struct.unpack(">h", struct.pack(">H", registers[reg_id]))[0]
                    case "ui32":
                        value = struct.unpack(">I", struct.pack(">HH", registers[reg_id], registers[reg_id+1]))[0]
                        ++reg_id
                    case "i32":
                        value = struct.unpack(">i", struct.pack(">HH", registers[reg_id], registers[reg_id+1]))[0]
                        ++reg_id
                    case "f32":
                        value = struct.unpack(">f", struct.pack(">HH", registers[reg_id], registers[reg_id+1]))[0]
                        ++reg_id
                    case _: raise ValueError("Неподдерживаемый тип данных")
                ++reg_id
                
                print(f"✅ {addr} : {value}")
                result_list.append(value)
    except ModbusException as e:
        raise
    return result_list

#Запись в регистр
#TODO: Переделать для записи нескольких регистров
def write_registers(client, addr, value, dict):
    """Выбирает функцию Modbus в зависимости от типа данных и записывает значение."""
    registers = convert_to_registers(value, addr, dict)
    try:
        if len(registers) == 1:
            response = client.write_register(address=addr, value=registers[0])
        else:
            response = client.write_registers(address=addr, values=registers)

        if isinstance(response, ExceptionResponse):
            print(f"❌ Ошибка Modbus от устройства: Код {response.exception_code}")
        elif response.isError():
            print(f"❌ Ошибка Modbus: {response}")
        else:
            print(f"✅")
    except ModbusException as e:
        raise

#Читаем файл JSON и определяем полученное как словарь
def dict_read(filename='mb_dict.json'):
    with open(filename, 'r') as f:
        obj = json.load(f)
    return dict(obj)

#Это нужно, чтобы ограничить значение аргумента без использования choices
def mb_range(string):
    value = int(string)
    if value < 1 or value > MAX_REG_QUANTITY:
        raise argparse.ArgumentTypeError(f"Значение должно быть в пределах 1-{MAX_REG_QUANTITY}")
    return value

#TODO: исправить баг с аварией в аварии из-за закрытия несуществующего клиента
#TODO: и вообще лучше переделать принцип работы перехвата аварий, я его сломал при переработке скрипта
if __name__ == "__main__":
    try:
        # Получение аргументов из строки терминала
        parser = argparse.ArgumentParser(description="Скрипт для общения с погружным трактором по modbus rtu. " \
        "Для работы требуется файл mb_dict.json в той же директории что и скрипт.")
        parser.add_argument("cmd", type=str, choices=["read", "write"], help="Тип команды (read/write)")
        parser.add_argument("addr", type=lambda x: int(x, 0), help="Адрес регистра (десятичный или hex, например 0x7D2)")
        parser.add_argument("-v", "--value", nargs='*', type=str, help="Значение для записи (только для write)")
        #parser.add_argument("-d", "--datatype", type=str, choices=["ui16", "i16", "ui32", "i32", "f32"], 
        #help="Тип данных. При указании этого аргумента JSON словарь не используется")
        parser.add_argument("-q", "--quantity", type=mb_range, default=1, help="Кол-во регистров для чтения/записи", 
                            metavar=f"1-{MAX_REG_QUANTITY}")
        args = parser.parse_args()

        if args.cmd == "write" and args.value is None:
            print("❌ Ошибка: для команды write необходимо указать значение")
            sys.exit()

        print("TEST!")
        sys.exit()

        mb_dictionary = dict_read()

        if not check_port_exists(COM_PORT):
            print(f"❌ Ошибка: Порт '{COM_PORT}' не найден. Пожалуйста, убедитесь, что порт существует и доступен.")
            sys.exit(1)

        if str(int(args.addr)) not in mb_dictionary:
            print("❌ Ошибка: Несуществующий адрес.")
            sys.exit()
        sys.exit()

        client.connect()

        match args.cmd:
            case "write":
                write_registers(client, args.addr, args.value, mb_dictionary)
            case "read":
                if args.value is not None: print("! Предупреждение: значение -v/--value проигнорировано, т.к. выбрана комманда чтения.")
                print(read_registers(client, args.addr, mb_dictionary, args.quantity))
            case _:
                raise Exception

        client.close()

    except ValueError as e:
        print(f"❌ Ошибка типа данных: {e}")
        client.close()
        sys.exit(1)

    except ModbusException as e:
        print(f"❌ Ошибка Modbus: {e}")
        client.close()
        sys.exit(1)

    except FileNotFoundError as e:
        print("❌: Файл не найден.")
        client.close()
        sys.exit()

    except Exception as e:
        print(f"❌ Неопознаная ошибка, обратитесь к разработчику: {e}")
        client.close()
        sys.exit(1)