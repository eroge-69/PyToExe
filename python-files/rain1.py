import csv
import os
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MIN_RAIN_RATE = 0.01  # мм/ч

def parse_float(value):
    try:
        return float(value.replace(',', '.'))
    except:
        return 0.0

def process_data(input_file, output_file, start_date=None, end_date=None, alpha=0.1):
    if not os.path.exists(input_file):
        print(f"Файл не найден: {input_file}")
        return

    timestamps = []
    rates = []
    smoothed_rate = 0.0
    last_time = None
    last_value = None

    try:
        with open(input_file, 'r', encoding='utf-8-sig') as f_in, \
             open(output_file, 'w', newline='', encoding='utf-8') as f_out:

            reader = csv.reader(f_in, delimiter=';')
            writer = csv.writer(f_out, delimiter=';')

            try:
                headers = next(reader)
                if headers[0].strip().upper() != 'STAMP' or headers[1].strip().upper() != 'VALUE':
                    print("Неверные заголовки! Должно быть: STAMP;VALUE")
                    return
            except StopIteration:
                print("Файл пуст.")
                return

            writer.writerow(['STAMP', 'RATE'])

            for row in reader:
                if len(row) < 2:
                    continue

                stamp_str = row[0].strip()
                value_str = row[1].strip()

                try:
                    stamp = datetime.strptime(stamp_str, '%d.%m.%Y %H:%M:%S')
                except ValueError:
                    continue

                # Пропускаем если дата вне диапазона
                if (start_date and stamp < start_date) or (end_date and stamp > end_date):
                    continue

                value = parse_float(value_str)

                if last_time is not None and last_value is not None:
                    dt_h = (stamp - last_time).total_seconds() / 3600.0
                    if dt_h > 0:
                        delta = value if value < last_value else value - last_value
                        current_rate = delta / dt_h
                        smoothed_rate = alpha * current_rate + (1 - alpha) * smoothed_rate
                        if smoothed_rate >= MIN_RAIN_RATE:
                            writer.writerow([stamp_str, f"{smoothed_rate:.6f}".replace('.', ',')])
                            timestamps.append(stamp)
                            rates.append(smoothed_rate)

                last_time = stamp
                last_value = value

        if timestamps:
            plt.figure(figsize=(10, 5))
            plt.plot(timestamps, rates, 'b-', label='Интенсивность дождя (мм/ч)')
            plt.xlabel('Время')
            plt.ylabel('Интенсивность (мм/ч)')
            plt.title('Интенсивность дождя по времени')
            plt.grid(True)
            plt.legend()

            ax = plt.gca()
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m %H:%M'))
            plt.gcf().autofmt_xdate()
            plt.tight_layout()

            plt.savefig('output.png')
            plt.show()
        else:
            print("Нет данных о дожде в указанном диапазоне.")
    except Exception as e:
        print(f"Ошибка выполнения: {e}")

def input_date(prompt):
    date_str = input(prompt).strip()
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%d.%m.%Y %H:%M:%S')
    except ValueError:
        print("Неверный формат даты. Используйте формат: ДД.ММ.ГГГГ ЧЧ:ММ:СС")
        return input_date(prompt)

if __name__ == "__main__":
    print("=== Анализ интенсивности осадков ===")
    input_file = input("Введите имя входного CSV-файла (например: rain.csv): ").strip()
    output_file = input("Введите имя выходного CSV-файла (например: rain_out.csv): ").strip()

    print("Введите начальную дату и время (формат: ДД.ММ.ГГГГ ЧЧ:ММ:СС). Оставьте пустым для пропуска.")
    start_date = input_date("Начальная дата: ")

    print("Введите конечную дату и время (формат: ДД.ММ.ГГГГ ЧЧ:ММ:СС). Оставьте пустым для пропуска.")
    end_date = input_date("Конечная дата: ")

    alpha_str = input("Введите коэффициент сглаживания (по умолчанию 0.1): ").strip()

    try:
        alpha = float(alpha_str) if alpha_str else 0.1
    except ValueError:
        print("Некорректный коэффициент сглаживания, используется значение по умолчанию (0.1).")
        alpha = 0.1

    process_data(input_file, output_file, start_date, end_date, alpha)
