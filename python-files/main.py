import random
import math
import time
import secrets
import hashlib

def init_rng():
    entropy_sources = [
        str(time.perf_counter_ns()),
        str(secrets.randbits(256)),
        str(hashlib.sha256(str(id(object)).encode()).hexdigest())
    ]
    combined = "|".join(entropy_sources).encode()
    seed = int(hashlib.sha256(combined).hexdigest(), 16) & 0xFFFFFFFFFFFF
    rng = random.Random()
    rng.seed(seed)
    return rng

def get_float_input(prompt, default=None):
    while True:
        try:
            value = input(prompt)
            if not value and default is not None:
                return default
            return float(value)
        except ValueError:
            print("Ошибка: введите число!")

def run_simulation():
    print("\n=== Параметры симуляции ===")
    initial_value = get_float_input("Начальное значение суммы x (по умолчанию 10): ", 10)
    target_multiplier = get_float_input("Во сколько раз нужно увеличить сумму x (по умолчанию 10): ", 10)
    prob_increase = get_float_input("Вероятность успешной сделки (от 0 до 1, по умолчанию 0.55): ", 0.55)
    increase_percent = get_float_input("Процент увеличения (по умолчанию 1.5): ", 1.5)
    decrease_percent = get_float_input("Процент уменьшения (по умолчанию 1.0): ", 1.0)
    num_simulations = int(get_float_input("Количество прогонов экспериментов (по умолчанию 10000): ", 10000))

    # Расчет коэффициентов
    increase_factor = 1 + (increase_percent / 100 * decrease_percent)
    decrease_factor = 1 - decrease_percent / 100
    target_value = initial_value * target_multiplier
    

    # Инициализация ГСЧ
    rng = init_rng()

    # Статистика
    steps_list = []
    
    print(f"\nСтарт симуляции: {num_simulations} экспериментов...")
    print("=" * 50)

    # Запуск симуляций
    for sim in range(num_simulations):
        x = initial_value
        steps = 0
        
        while x < target_value:
            if steps % 100 == 0:
                rng.seed(rng.getrandbits(64) ^ secrets.randbits(64))
                
            if rng.random() < prob_increase:
                x *= increase_factor
            else:
                x *= decrease_factor
                
            steps += 1
            
        steps_list.append(steps)
        
        if (sim + 1) % 1000 == 0:
            print(f"Завершено: {sim + 1}/{num_simulations} экспериментов")

    # Расчет статистики
    total_steps = sum(steps_list)
    mean_steps = total_steps / num_simulations
    sorted_steps = sorted(steps_list)
    median_steps = sorted_steps[num_simulations // 2]
    min_steps = min(steps_list)
    max_steps = max(steps_list)
    squared_diffs = sum((x - mean_steps) ** 2 for x in steps_list)
    std_steps = math.sqrt(squared_diffs / num_simulations)

    print("=" * 50)
    print("РЕЗУЛЬТАТЫ:")
    print(f"Начальное значение x: {initial_value}")
    print(f"Целевое значение: {target_value:.2f} (увеличение в {target_multiplier} раз)")
    print(f"Вероятность увеличения: {prob_increase*100}%")
    print(f"Процент увеличения: {increase_percent*decrease_percent}%")
    print(f"Процент уменьшения: {decrease_percent}%")
    print(f"\nСреднее количество итераций: {mean_steps:.1f}")
    print(f"Медианное количество итераций: {median_steps}")
    print(f"Минимальное количество итераций: {min_steps}")
    print(f"Максимальное количество итераций: {max_steps}")
    print(f"Стандартное отклонение: {std_steps:.1f}")

    # Теоретическая оценка
    log_inc = math.log(increase_factor)
    log_dec = math.log(decrease_factor)
    expected_growth = prob_increase * log_inc + (1 - prob_increase) * log_dec
    required_growth = math.log(target_multiplier)
    theoretical_steps = required_growth / expected_growth

    print("\nТЕОРЕТИЧЕСКАЯ ОЦЕНКА:")
    print(f"Ожидаемый прирост логарифма за шаг: {expected_growth:.6f}")
    print(f"Требуемое изменение логарифма: {required_growth:.6f}")
    print(f"Теоретическая оценка шагов: {theoretical_steps:.1f}")

    # Гистограмма
    print("\nГИСТОГРАММА РАСПРЕДЕЛЕНИЯ:")
    min_val = min_steps // 100 * 100
    max_val = (max_steps // 100 + 1) * 100
    bins = 10
    bin_width = max(1, (max_val - min_val) // bins)

    freq = [0] * bins
    for steps in steps_list:
        if bin_width > 0:
            index = min((steps - min_val) // bin_width, bins - 1)
            freq[index] += 1

    max_freq = max(freq) or 1
    for i in range(bins):
        start = min_val + i * bin_width
        end = start + bin_width - 1
        count = freq[i]
        bar_length = int(count * 50 / max_freq)
        bar = '█' * bar_length
        print(f"{start:5}-{end:5}: {bar} {count} ({count/num_simulations*100:.1f}%)")

# Основной цикл программы
def main():
    print("=== Имитационное моделирование сделок ===")
    print("Параметры можно вводить с клавиатуры или нажимать Enter для значений по умолчанию")
    print("Для выхода введите 'ок' в любой момент\n")
    
    while True:
        run_simulation()
        
        command = input("\nВведите 'ок' для выхода или нажмите Enter для нового расчета: ").strip().lower()
        if command == 'ок':
            print("Завершение работы программы...")
            break

if __name__ == "__main__":
    main()