import hashlib
import random
import time
from multiprocessing import Pool, cpu_count
from tqdm import tqdm

def md5_cp1251(string):
    """Вычисляет MD5 в кодировке Windows-1251 (CP1251)."""
    try:
        s_bytes = string.encode('cp1251')
        return hashlib.md5(s_bytes).hexdigest().lower()
    except UnicodeEncodeError:
        return None

def verify_hash(roulette_num, number, target_hash):
    """Верифицирует хеш для дробного или целого числа."""
    if '.' in str(number):
        integer_part, frac_part = str(number).split('.')
        test_string = f"{roulette_num}.{integer_part}.{frac_part}"
    else:
        test_string = f"{roulette_num}.{number}"
    
    computed_hash = md5_cp1251(test_string)
    if computed_hash == target_hash.lower():
        return f"✅ Совпадение! Число: {number}, Строка: '{test_string}', Хеш: {computed_hash}"
    else:
        return f"❌ Не совпадает. Вычисленный хеш: {computed_hash}"

def check_integer(args):
    """Проверяет целое число (для многопоточного brute)."""
    roulette_num, num, target_hash = args
    test_string = f"{roulette_num}.{num}"
    if md5_cp1251(test_string) == target_hash.lower():
        return num
    return None

def brute_integers(roulette_num, target_hash, min_num=1, max_num=100):
    """Многопоточный brute-force целых чисел."""
    print(f"🚀 Brute-force целых чисел {min_num}–{max_num} на {cpu_count()} ядрах...")
    start_time = time.time()
    with Pool(cpu_count()) as pool:
        results = list(tqdm(pool.imap(check_integer, [(roulette_num, num, target_hash) for num in range(min_num, max_num + 1)]), total=max_num-min_num+1))
    pool.close()
    pool.join()
    
    found = [r for r in results if r is not None]
    elapsed = time.time() - start_time
    if found:
        return f"✅ Найдено целое число: {found[0]}, Строка: '{roulette_num}.{found[0]}', Время: {elapsed:.2f} сек."
    return f"❌ Нет совпадения среди целых {min_num}–{max_num}. Время: {elapsed:.2f} сек."

def check_fractional(args):
    """Проверяет дробное число (для многопоточного brute)."""
    roulette_num, integer_part, frac_part, target_hash = args
    test_string = f"{roulette_num}.{integer_part}.{frac_part}"
    if md5_cp1251(test_string) == target_hash.lower():
        return f"{integer_part}.{frac_part}"
    return None

def brute_fractional(roulette_num, target_hash, integer_parts=(1, 100), frac_length=5, max_attempts=1000000):
    """Многопоточный brute-force дробных чисел (ограниченный)."""
    print(f"⚠️ Brute-force дробных чисел (целая часть {integer_parts[0]}–{integer_parts[1]}, длина дробной: {frac_length}, попыток: {max_attempts})...")
    start_time = time.time()
    attempts = []
    for _ in range(max_attempts):
        integer_part = random.randint(integer_parts[0], integer_parts[1])
        frac_part = ''.join(random.choices('0123456789', k=frac_length))
        attempts.append((roulette_num, integer_part, frac_part, target_hash))
    
    with Pool(cpu_count()) as pool:
        results = list(tqdm(pool.imap(check_fractional, attempts), total=max_attempts))
    pool.close()
    pool.join()
    
    found = [r for r in results if r is not None]
    elapsed = time.time() - start_time
    if found:
        return f"✅ Найдено! Число: {found[0]}, Строка: '{roulette_num}.{found[0].replace('.', '.')}', Время: {elapsed:.2f} сек."
    return f"❌ Не найдено за {max_attempts} попыток (время: {elapsed:.2f} сек.). Увеличь попытки или уменьши длину дробной части."

if __name__ == "__main__":
    print("=== Расшифровщик MD5 для рулетки (CP1251) ===")
    roulette_num = input("Введи номер рулетки: ").strip()
    target_hash = input("Введи MD5-хеш: ").strip()
    
    choice = input("Выбери действие (1 - верифицировать число, 2 - brute целые 1-100, 3 - brute дробных): ")
    
    if choice == "1":
        number = input("Введи число (целое или дробное, напр. 90.9193358955592513): ").strip()
        print(verify_hash(roulette_num, number, target_hash))
    
    elif choice == "2":
        min_num = int(input("Мин. целая часть (по умол. 1): ") or 1)
        max_num = int(input("Макс. целая часть (по умол. 100): ") or 100)
        print(brute_integers(roulette_num, target_hash, min_num, max_num))
    
    elif choice == "3":
        integer_min = int(input("Мин. целая часть (по умол. 1): ") or 1)
        integer_max = int(input("Макс. целая часть (по умол. 100): ") or 100)
        frac_length = int(input("Длина дробной части (по умол. 5, макс 8 для демо): ") or 5)
        max_attempts = int(input("Макс. попыток (по умол. 1000000): ") or 1000000)
        print(brute_fractional(roulette_num, target_hash, (integer_min, integer_max), frac_length, max_attempts))
    
    # Тест на примере
    print("\n--- Тест на примере №1779953163 ---")
    print(verify_hash("1779953163", "90.9193358955592513", "0cf563a517729f5c64c88d01e1f1628c"))