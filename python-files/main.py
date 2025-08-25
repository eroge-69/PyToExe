import pymem
import pymem.process
import psutil
import os
import logging
import re
import struct
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_resource_path(relative_path):
    """Получает абсолютный путь к файлу, работает для .py и .exe."""
    exe_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
    local_path = os.path.join(exe_dir, relative_path)
    if os.path.exists(local_path):
        logger.info(f"Файл найден рядом с .exe: {local_path}")
        return local_path
    
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = exe_dir
    embedded_path = os.path.join(base_path, relative_path)
    logger.info(f"Файл ищется во временной папке: {embedded_path}")
    return embedded_path

def load_skin_ids(file_path):
    """Читает ID скинов из файла формата 'Имя_Скина = Числовой_ID'."""
    file_path = get_resource_path(file_path)
    try:
        if not os.path.exists(file_path):
            logger.error(f"Файл {file_path} не найден!")
            return []
        skin_ids = []
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line or '=' not in line:
                    continue
                match = re.match(r'(\w+)\s*=\s*(\d+);?', line)
                if match:
                    skin_name, skin_id = match.groups()
                    skin_ids.append((skin_name, int(skin_id)))
        logger.info(f"Загружено {len(skin_ids)} ID скинов из {file_path}")
        return skin_ids
    except Exception as e:
        logger.error(f"Ошибка при чтении файла {file_path}: {e}")
        return []

def find_process():
    """Находит процесс эмулятора (HD-Player, LdVBoxHeadless, Ld9BoxHeadless)."""
    process_names = ["HD-Player.exe", "LdVBoxHeadless.exe", "Ld9BoxHeadless.exe"]
    try:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() in [name.lower() for name in process_names]:
                emulator = "LDPlayer" if "Ld" in proc.info['name'] else "BlueStacks"
                logger.info(f"Найден процесс {proc.info['name']} (PID: {proc.pid}, Эмулятор: {emulator})")
                return proc.pid, proc.info['name'], emulator
        logger.error("Процесс эмулятора не найден!")
        return None, None, None
    except Exception as e:
        logger.error(f"Ошибка при поиске процесса: {e}")
        return None, None, None

def check_signature(pm, address):
    """Проверяет, соответствует ли память после адреса сигнатуре '01 00 00 00 ?? 00 00 ??'."""
    try:
        bytes_read = pm.read_bytes(address + 4, 8)
        expected = [0x01, 0x00, 0x00, 0x00, None, 0x00, 0x00, None]
        for i, (b, e) in enumerate(zip(bytes_read, expected)):
            if e is not None and b != e:
                return False
        return True
    except Exception as e:
        logger.warning(f"Ошибка при проверке сигнатуры на адресе {hex(address)}: {e}")
        return False

def search_skins(pm, skin_ids, memory_start=0x59682f00, memory_end=0xee6b2800):
    """Ищет скины в памяти процесса по ID и проверяет сигнатуру."""
    found_skins = []
    try:
        for skin_name, skin_id in skin_ids:
            logger.info(f"Поиск скина: {skin_name} (ID: {skin_id})")
            try:
                pattern = struct.pack('<I', skin_id)
                addresses = pm.pattern_scan_all(pattern, return_multiple=True)
                for addr in addresses:
                    if memory_start <= addr <= memory_end:
                        if check_signature(pm, addr):
                            found_skins.append((skin_name, skin_id, addr))
                            logger.info(f"Найден скин: {skin_name} (ID: {skin_id}), Адрес: {hex(addr)}")
                
                if not any(memory_start <= addr <= memory_end for addr, _, _ in found_skins):
                    logger.info(f"Скин {skin_name} не найден в диапазоне, пробуем полный поиск...")
                    addresses = pm.pattern_scan_all(pattern, return_multiple=True)
                    for addr in addresses:
                        if check_signature(pm, addr):
                            found_skins.append((skin_name, skin_id, addr))
                            logger.info(f"Найден скин (полный поиск): {skin_name} (ID: {skin_id}), Адрес: {hex(addr)}")
            except Exception as e:
                logger.warning(f"Ошибка при поиске скина {skin_name} (ID: {skin_id}): {e}")
        if not found_skins:
            logger.info("Скины не найдены в памяти процесса.")
    except Exception as e:
        logger.error(f"Общая ошибка при поиске скинов: {e}")
    return found_skins

def replace_skin(pm, address, new_id):
    """Заменяет скин по указанному адресу на новый ID (32-битное целое)."""
    try:
        if not isinstance(new_id, int) or new_id < 0:
            raise ValueError("Новый ID должен быть положительным целым числом")
        pm.write_int(address, new_id)
        logger.info(f"Скин по адресу {hex(address)} успешно заменён на ID {new_id}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при замене скина по адресу {hex(address)}: {e}")
        print(f"Ошибка при замене: {e}")
        return False

def main_menu():
    search_file = "search.txt"
    replace_file = "skins.txt"
    custom_id = None
    memory_start = 0x59682f00
    memory_end = 0xee6b2800
    
    while True:
        print("""
████████╗ ██████╗     ██╗     ██╗████████╗███████╗██╗    ██╗ █████╗ ██████╗ ███████╗
╚══██╔══╝██╔════╝     ██║     ██║╚══██╔══╝██╔════╝██║    ██║██╔══██╗██╔══██╗██╔════╝
   ██║   ██║  ███╗    ██║     ██║   ██║   █████╗  ██║ █╗ ██║███████║██████╔╝█████╗  
   ██║   ██║   ██║    ██║     ██║   ██║   ██╔══╝  ██║███╗██║██╔══██║██╔══██╗██╔══╝  
   ██║   ╚██████╔╝    ███████╗██║   ██║   ███████╗╚███╔███╔╝██║  ██║██║  ██║███████╗
   ╚═╝    ╚═════╝     ╚══════╝╚═╝   ╚═╝   ╚══════╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝
""")
        print("[1] ПОИСК СКИНОВ")
        print("[2] ЗАМЕНИТЬ СКИН")
        print("[3] Выход")
        
        choice = input("Выберите действие (1-3): ")
        
        if choice == "1":
            skin_ids = load_skin_ids(search_file)
            if not skin_ids:
                print("Ошибка: файл search.txt пуст или не найден.")
                continue
            
            pid, proc_name, emulator = find_process()
            if not pid:
                print("Ошибка: процесс эмулятора не найден. Запустите Standoff 2.")
                continue
            
            try:
                pm = pymem.Pymem(proc_name)
                print(f"\nПодключено к {emulator} ({proc_name})")
                found_skins = search_skins(pm, skin_ids, memory_start, memory_end)
                if not found_skins:
                    print("Скины не найдены в памяти процесса. Попробуйте перезапустить эмулятор.")
                else:
                    print(f"\nНайдено скинов: {len(found_skins)}")
                    for i, (skin_name, skin_id, addr) in enumerate(found_skins, 1):
                        print(f"{i}. {skin_name} (ID: {skin_id}), Адрес: {hex(addr)}")
            except Exception as e:
                logger.error(f"Ошибка при поиске скинов: {e}")
                print(f"Произошла ошибка: {e}")
        
        elif choice == "2":
            skin_ids = load_skin_ids(search_file)
            if not skin_ids:
                print("Ошибка: файл search.txt пуст или не найден.")
                continue
            
            replace_ids = load_skin_ids(replace_file)
            if not replace_ids and not custom_id:
                print("Ошибка: файл skins.txt пуст, и кастомный ID не установлен. Используйте пункт 3.")
                continue
            
            pid, proc_name, emulator = find_process()
            if not pid:
                print("Ошибка: процесс эмулятора не найден. Запустите Standoff 2.")
                continue
            
            try:
                pm = pymem.Pymem(proc_name)
                print(f"\nПодключено к {emulator} ({proc_name})")
                found_skins = search_skins(pm, skin_ids, memory_start, memory_end)
                if not found_skins:
                    print("Скины не найдены в памяти процесса. Попробуйте перезапустить эмулятор.")
                    continue
                
                print("\nНайденные скины:")
                for i, (skin_name, skin_id, addr) in enumerate(found_skins, 1):
                    print(f"{i}. {skin_name} (ID: {skin_id}), Адрес: {hex(addr)}")
                
                try:
                    skin_index = int(input(f"\nВыберите номер скина для замены (1-{len(found_skins)}): ")) - 1
                    if 0 <= skin_index < len(found_skins):
                        skin_name, skin_id, addr = found_skins[skin_index]
                        print(f"\nВы выбрали: {skin_name} (ID: {skin_id})")
                        
                        if replace_ids:
                            print("\nСкины для замены (из skins.txt):")
                            for i, (replace_name, replace_id) in enumerate(replace_ids, 1):
                                print(f"{i}. {replace_name} (ID: {replace_id})")
                            if custom_id:
                                print(f"{len(replace_ids) + 1}. Кастомный ID: {custom_id}")
                            max_choice = len(replace_ids) + 1 if custom_id else len(replace_ids)
                            replace_choice = input(f"Выберите номер скина для замены (1-{max_choice}): ")
                            try:
                                replace_index = int(replace_choice) - 1
                                if 0 <= replace_index < len(replace_ids):
                                    new_name, new_id = replace_ids[replace_index]
                                    if replace_skin(pm, addr, new_id):
                                        print(f"\nУспех: {skin_name} заменён на {new_name} (ID: {new_id})")
                                    else:
                                        print("\nНе удалось заменить скин. Перезапустите эмулятор.")
                                elif custom_id and replace_index == len(replace_ids):
                                    if replace_skin(pm, addr, int(custom_id)):
                                        print(f"\nУспех: {skin_name} заменён на кастомный ID {custom_id}")
                                    else:
                                        print("\nНе удалось заменить скин. Перезапустите эмулятор.")
                                else:
                                    print("Неверный выбор!")
                            except ValueError:
                                print("Ошибка: введите число!")
                        elif custom_id:
                            if replace_skin(pm, addr, int(custom_id)):
                                print(f"\nУспех: {skin_name} заменён на кастомный ID {custom_id}")
                            else:
                                print("\nНе удалось заменить скин. Перезапустите эмулятор.")
                        else:
                            print("Ошибка: кастомный ID не установлен, и skins.txt пуст.")
                    else:
                        print(f"Ошибка: выберите номер от 1 до {len(found_skins)}!")
                except ValueError:
                    print("Ошибка: введите число!")
            except Exception as e:
                logger.error(f"Ошибка при замене скина: {e}")
                print(f"Произошла ошибка: {e}")
        
        elif choice == "3":
            custom_id = input("Введите кастомный ID скина (число): ").strip()
            try:
                custom_id = int(custom_id)
                if custom_id < 0:
                    raise ValueError("ID должен быть положительным!")
                logger.info(f"Кастомный ID установлен: {custom_id}")
                print(f"Кастомный ID установлен: {custom_id}")
            except ValueError:
                print("Ошибка: ID должен быть положительным числом!")
                custom_id = None
        
        elif choice == "4":
            print("Выход из программы...")
            logger.info("Программа завершена.")
            break
        else:
            print("Ошибка: выберите действие от 1 до 4!")

if __name__ == "__main__":
    main_menu()