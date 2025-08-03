
import random

def get_user_input():
    # Λήψη σταθερών αριθμών
    fixed_numbers = input("Δώσε τους σταθερούς αριθμούς (π.χ. 5,12): ")
    fixed_numbers = [int(x.strip()) for x in fixed_numbers.split(",") if x.strip().isdigit()]

    # Λήψη εύρους αριθμών
    min_num = int(input("Ελάχιστος αριθμός (π.χ. 1): "))
    max_num = int(input("Μέγιστος αριθμός (π.χ. 45): "))

    # Πόσες στήλες;
    num_columns = int(input("Πόσες στήλες θέλεις να δημιουργηθούν; "))

    # Εύρος για Τζόκερ
    joker_min = int(input("Ελάχιστος αριθμός Τζόκερ (π.χ. 1): "))
    joker_max = int(input("Μέγιστος αριθμός Τζόκερ (π.χ. 20): "))

    return fixed_numbers, min_num, max_num, num_columns, joker_min, joker_max

def generate_columns(fixed, min_n, max_n, count, joker_min, joker_max):
    all_numbers = list(range(min_n, max_n + 1))
    columns = []

    for _ in range(count):
        available = [n for n in all_numbers if n not in fixed]
        needed = 5 - len(fixed)
        if needed < 0:
            print("Έδωσες περισσότερους από 5 σταθερούς αριθμούς.")
            return []
        chosen = random.sample(available, needed)
        full = sorted(fixed + chosen)
        joker = random.randint(joker_min, joker_max)
        columns.append((full, joker))

    return columns

def save_to_file(columns):
    with open("tzoker_result.txt", "w", encoding="utf-8") as f:
        for i, (nums, joker) in enumerate(columns, start=1):
            line = f"Στήλη {i}: {nums} - Τζόκερ: {joker}"
            print(line)
            f.write(line + "\n")
        f.write(f"\nΣύνολο στηλών: {len(columns)}\n")
    print("\nΤα αποτελέσματα αποθηκεύτηκαν στο αρχείο: tzoker_result.txt")

def main():
    print("== Προγραμμα Δημιουργίας Στηλών Τζόκερ ==")
    fixed, min_n, max_n, count, joker_min, joker_max = get_user_input()
    columns = generate_columns(fixed, min_n, max_n, count, joker_min, joker_max)
    if columns:
        save_to_file(columns)

if __name__ == "__main__":
    main()
