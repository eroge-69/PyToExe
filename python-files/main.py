import sys
import os
from pathlib import Path

def parse_time(time_bytes):
    """Преобразует 2 байта времени в миллисекунды"""
    return (time_bytes[1] << 8) | time_bytes[0]

def parse_data_line(line):
    if line.startswith('#'):
        line = line[1:]
    parts = line.strip().split('#')
    
    if len(parts) < 11:
        return None
    
    try:
        pulse = int(parts[0], 16)
        oxygen = int(parts[4], 16)
        time_bytes = (int(parts[8], 16), int(parts[9], 16))
        time = parse_time(time_bytes)
        return pulse, oxygen, time
    except (ValueError, IndexError) as e:
        print(f"Ошибка в строке: {line.strip()}, ошибка: {str(e)}")
        return None

def convert_file(input_file):
    output_file = str(Path(input_file).parent / "PulseOUT.txt")
    
    with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
        f_out.write("Пульс\tКислород\tВремя(мс)\n")
        
        for line in f_in:
            line = line.strip()
            if not line:
                continue
            
            parsed = parse_data_line(line)
            if parsed:
                pulse, oxygen, time = parsed
                f_out.write(f"{pulse}\t{oxygen}\t{time}\n")

    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        input("Перетащите файл с данными на этот EXE-файл и нажмите Enter...")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        input(f"Файл {input_file} не найден! Нажмите Enter для выхода...")
        sys.exit(1)
    
    try:
        output_file = convert_file(input_file)
        print(f"Файл успешно обработан! Результат сохранён в:\n{output_file}")
        print("\nПервые 5 строк результата:")
        with open(output_file, 'r') as f:
            for i, line in enumerate(f):
                if i < 6:
                    print(line.strip())
        input("\nНажмите Enter для выхода...")
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        input("Нажмите Enter для выхода...")