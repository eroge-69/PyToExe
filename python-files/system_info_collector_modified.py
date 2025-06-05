
import platform
import psutil
import socket
import subprocess
from datetime import datetime
import os

def get_cpu_name():
    try:
        output = subprocess.check_output("wmic cpu get Name", shell=True)
        return output.decode().split("\n")[1].strip()
    except:
        return platform.processor()

def get_ram_info():
    try:
        output = subprocess.check_output("wmic memorychip get capacity, memorytype", shell=True)
        lines = output.decode().split("\n")[1:]
        ram_type_map = {
            "0": "Неизвестно", "20": "DDR", "21": "DDR2", "24": "DDR3", "26": "DDR4", "25": "DDR5"
        }

        total_gb = 0
        ram_types = set()

        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 2:
                cap, typ = parts
                total_gb += int(cap) / (1024 ** 3)
                ram_types.add(ram_type_map.get(typ, f"Код {typ}"))

        return round(total_gb, 2), ", ".join(ram_types)
    except:
        return round(psutil.virtual_memory().total / (1024**3), 2), "Неизвестно"

def get_disk_info():
    try:
        output = subprocess.check_output(
            'wmic diskdrive get Caption,Size,InterfaceType /format:csv',
            shell=True
        ).decode("utf-8").splitlines()

        disks = []
        for line in output:
            if line.strip() and not line.startswith("Node"):
                parts = line.split(",")
                if len(parts) >= 4:
                    _, name, interface, size = parts
                    try:
                        size_gb = round(int(size) / (1024 ** 3), 2)
                    except ValueError:
                        continue
                    disks.append({
                        "Название": name.strip(),
                        "Объем (ГБ)": size_gb,
                        "Интерфейс": interface.strip()
                    })
        return disks
    except Exception as e:
        return [{"Ошибка": str(e)}]

def get_system_info():
    info = {}
    info["Дата и время"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    info["Имя компьютера"] = socket.gethostname()
    info["ОС"] = platform.system()
    info["Версия ОС"] = platform.version()
    info["Процессор"] = get_cpu_name()
    ram_size, ram_type = get_ram_info()
    info["ОЗУ (ГБ)"] = ram_size
    info["Тип ОЗУ"] = ram_type
    info["Архитектура"] = platform.machine()
    info["Диски"] = get_disk_info()
    return info

def save_info_to_txt(info):
    directory = "G:\data"
    os.makedirs(directory, exist_ok=True)
    filename = os.path.join(directory, f"{info['Имя компьютера']}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        for key, value in info.items():
            if isinstance(value, list):
                f.write(f"{key}:")
                for item in value:
                    f.write("  - " + ", ".join(f"{k}: {v}" for k, v in item.items()) + "\n")
            else:
                f.write(f"{key}: {value}\n")

if __name__ == "__main__":
    data = get_system_info()
    save_info_to_txt(data)
    print(f"Информация сохранена в файл: E:\\input_data\data{data['Имя компьютера']}.txt")
