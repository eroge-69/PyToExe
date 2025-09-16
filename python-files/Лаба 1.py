# Задание 1
import math


def print_section_header(title):
    """Печатает заголовок раздела с форматированием"""
    print(f"\n{'-' * 60}")
    print(f"{title.upper()}")
    print(f"{'-' * 60}")


def print_probability_results(detected_prob, undetected_prob, precision_det=8, precision_undet=12):
    """Печатает результаты вероятностей в едином формате"""
    print(f"Вероятность обнаружения ошибки: {detected_prob:.{precision_det}f}")
    print(f"Вероятность необнаружения ошибки: {undetected_prob:.{precision_undet}f}")


def calculate_parity_control(p0):
    """Расчет контроля по паритету для 8-битовых блоков"""
    n_a = 9  # 7 бит данных + 1 бит паритета

    # Вероятность необнаружения ошибки (четное количество ошибок)
    P_und_a = (math.comb(8, 2) * (p0**2) * ((1 - p0)**6) +
               math.comb(8, 4) * (p0**4) * ((1 - p0)**4) +
               math.comb(8, 6) * (p0**6) * ((1 - p0)**2) +
               math.comb(8, 8) * (p0**8))

    P_det_a = 1 - P_und_a
    return P_det_a, P_und_a


def calculate_double_parity_control(p0):
    """Расчет контроля по вертикальному и горизонтальному паритету"""
    rows = 8
    columns = 8

    # Вероятность четного числа ошибок в одной строке
    P_all_rows = 0
    for k in range(0, 10, 2):  # четные числа ошибок
        P_all_rows += math.comb(9, k) * (p0**k) * ((1 - p0)**(9 - k))

    P_und_b = P_all_rows**8  # для всех 8 строк
    P_det_b = 1 - P_und_b

    return P_det_b, P_und_b


def calculate_crc_control(p0):
    """Расчет циклического избыточного контроля"""
    n_c_data = 1024  # бит данных
    n_c_crc = 16     # бит CRC

    P_und_c = 2**(-n_c_crc)  # приближенная оценка
    P_det_c = 1 - P_und_c

    return P_det_c, P_und_c


def main():
    print_section_header("Задание 1")

    # Исходные данные
    BIT_ERROR_PROBABILITY = 10**-3

    print(f"Вероятность ошибки одного бита p0 = {BIT_ERROR_PROBABILITY}")

    # a) Контроль по паритету для 8-битовых блоков
    print_section_header("а) Контроль по паритету для 8-битовых блоков")
    P_det_a, P_und_a = calculate_parity_control(BIT_ERROR_PROBABILITY)
    print_probability_results(P_det_a, P_und_a)

    # б) Контроль по вертикальному и горизонтальному паритету
    print_section_header("б) Контроль по вертикальному и горизонтальному паритету")
    P_det_b, P_und_b = calculate_double_parity_control(BIT_ERROR_PROBABILITY)
    print_probability_results(P_det_b, P_und_b, precision_det=12, precision_undet=16)

    # в) Циклический избыточный контроль
    print_section_header("в) Циклический избыточный контроль для 1024-битовых блоков")
    P_det_c, P_und_c = calculate_crc_control(BIT_ERROR_PROBABILITY)
    print_probability_results(P_det_c, P_und_c, precision_det=12, precision_undet=16)

    # Сравнительная таблица
    print_section_header("Сравнительная таблица")
    print(f"{'Метод контроля':<30} {'Вероятность обнаружения':<20}")
    print("-" * 50)
    print(f"{'Паритет (8 бит)':<30} {P_det_a:.10f}")
    print(f"{'Двойной паритет (64 бит)':<30} {P_det_b:.10f}")
    print(f"{'CRC-16 (1024 бит)':<30} {P_det_c:.10f}")

if __name__ == "__main__":
    main()


# Задание 2
    def get_input_text():
        """Получает текст от пользователя"""
        return input("Введите русский текст: ")


    def convert_to_binary_blocks(text):
        """Преобразует текст в двоичные блоки"""
        binary_blocks = [
            format(byte, '08b')
            for char in text
            for byte in char.encode('utf-8')
        ]
        return binary_blocks


    def calculate_parity_bits(binary_blocks):
        """Вычисляет контрольные биты четности для каждого блока"""
        parity_bits = []
        for block in binary_blocks:
            ones_count = block.count('1')
            parity_bit = '1' if ones_count % 2 != 0 else '0'
            parity_bits.append(parity_bit)
        return parity_bits


    def check_parity_errors(binary_blocks, parity_bits):
        """Проверяет блоки на ошибки с помощью контрольных битов"""
        errors_detected = []

        for i, block in enumerate(binary_blocks):
            ones_count = block.count('1')
            calculated_parity = '1' if ones_count % 2 != 0 else '0'

            if calculated_parity != parity_bits[i]:
                errors_detected.append(i + 1)

        return errors_detected


    def print_parity_results(binary_blocks, parity_bits, errors_detected):
        """Выводит результаты контроля по паритету"""
        print(f"Двоичный код: {' '.join(binary_blocks)}")
        print(f"Количество блоков: {len(binary_blocks)}")
        print("\nПункт А)")
        print("\nКОНТРОЛЬ ПО ПАРИТЕТУ")
        print(f"Контрольные биты: {' '.join(parity_bits)}")

        # Блок проверки на ошибки
        print("\n" + "=" * 40)
        print("ПРОВЕРКА КОРРЕКТНОСТИ ПЕРЕДАЧИ")
        print("=" * 40)

        if not errors_detected:
            print("✓ Сообщение передано без ошибок")
            print("Все контрольные биты совпадают с расчетными значениями")
        else:
            print("✗ ОБНАРУЖЕНЫ ОШИБКИ ПЕРЕДАЧИ!")
            print(f"Ошибки в блоках: {', '.join(map(str, errors_detected))}")
            print(f"Количество ошибок: {len(errors_detected)}")

            print("\nДетальная информация об ошибках:")
            for error_block in errors_detected:
                block_index = error_block - 1
                print(f"Блок {error_block}: {binary_blocks[block_index]} "
                      f"(ожидаемый контрольный бит: {parity_bits[block_index]})")


    def process_double_parity(text):
        """Обрабатывает контроль по горизонтальному и вертикальному паритету"""
        print("\nПункт Б)")
        print("\nКОНТРОЛЬ ПО ГОРИЗОНТАЛЬНОМУ И ВЕРТИКАЛЬНОМУ ПАРИТЕТУ")

        # Получаем все биты
        all_bits = ''.join(
            format(byte, '08b')
            for char in text
            for byte in char.encode('utf-8')
        )

        # Разбиваем на блоки по 64 бита
        BLOCK_SIZE = 64
        blocks = []
        for i in range(0, len(all_bits), BLOCK_SIZE):
            block = all_bits[i:i + BLOCK_SIZE].ljust(BLOCK_SIZE, '0')
            blocks.append(block)

        print(f"Блоков по 64 бита: {len(blocks)}")

        # Горизонтальный паритет
        horizontal_parity = []
        print("\nГоризонтальный паритет:")
        for i, block in enumerate(blocks):
            parity = '1' if block.count('1') % 2 != 0 else '0'
            horizontal_parity.append(parity)
            print(f"Блок {i + 1}: {parity}")

        # Вертикальный паритет
        vertical_parity = []
        for column_index in range(BLOCK_SIZE):
            column_bits = ''.join(block[column_index] for block in blocks)
            parity = '1' if column_bits.count('1') % 2 != 0 else '0'
            vertical_parity.append(parity)

        print(f"\nВертикальный паритет: {''.join(vertical_parity)}")

        # Проверка на ошибки
        print("\nПРОВЕРКА:")
        errors_found = False

        for i, block in enumerate(blocks):
            calculated_parity = '1' if block.count('1') % 2 != 0 else '0'
            if calculated_parity != horizontal_parity[i]:
                print(f"Ошибка в блоке {i + 1}!")
                errors_found = True

        if not errors_found:
            print("Ошибок не обнаружено")
        else:
            print("Обнаружены ошибки передачи")


    def main():
        """Основная функция программы"""
        text = get_input_text()
        binary_blocks = convert_to_binary_blocks(text)
        parity_bits = calculate_parity_bits(binary_blocks)
        errors_detected = check_parity_errors(binary_blocks, parity_bits)

        print_parity_results(binary_blocks, parity_bits, errors_detected)
        process_double_parity(text)


    if __name__ == "__main__":
        main()
