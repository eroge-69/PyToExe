import itertools
import string
import time
import os

def generate_combinations(characters, length):
    """���������� ��� ��������� ���������� �������� �������� �����."""
    for combination in itertools.product(characters, repeat=length):
        yield ''.join(combination)

def estimate_time(total_combinations, combinations_per_second):
    """��������� ���������� ����� �������� � ��������."""
    if combinations_per_second == 0:
        return float('inf')  # �������������, ���� �������� ����� 0
    return total_combinations / combinations_per_second

def main():
    """�������� ������� �������."""

    # ����� ���� �������� ��� ��������
    print("�������� ��� �������� ��� ��������:")
    print("1) ��������� �����")
    print("2) ������� �����")
    print("3) �����")
    print("4) ������� � ��������� �����")
    print("5) ������� � ��������� ����� � �����")

    choice = input("������� ����� ���������� ��������: ")

    if choice == '1':
        characters = string.ascii_lowercase
    elif choice == '2':
        characters = string.ascii_uppercase
    elif choice == '3':
        characters = string.digits
    elif choice == '4':
        characters = string.ascii_letters
    elif choice == '5':
        characters = string.ascii_letters + string.digits
    else:
        print("������������ ����. ����� �� ���������.")
        return

    # ���� ����� ��������
    try:
        length = int(input("������� ����� ��������: "))
        if length <= 0:
            print("����� ������ ���� ������������� ����� ������. ����� �� ���������.")
            return
    except ValueError:
        print("������������ ����. ������� ����� �����. ����� �� ���������.")
        return

    # ��� ����� ��� ������ �����������
    filename = "combinations.txt"

    # ������� ������ ���������� ����������
    total_combinations = len(characters) ** length

    print(f"����� ���������� ��� ��������: {total_combinations}")
    print(f"���������� ����� �������� � ����: {filename}")

    start_time = time.time()
    combinations_generated = 0

    with open(filename, "w") as file:
        for combination in generate_combinations(characters, length):
            file.write(combination + "\n")
            combinations_generated += 1

            # ������ ����������� ������� (������ 1000 ����������)
            if combinations_generated % 1000 == 0:
                elapsed_time = time.time() - start_time
                combinations_per_second = combinations_generated / elapsed_time
                estimated_remaining_time = estimate_time(total_combinations - combinations_generated, combinations_per_second)

                print(f"�������������: {combinations_generated}/{total_combinations}, "
                      f"��������: {combinations_per_second:.2f} ����/���, "
                      f"�������� �������: {estimated_remaining_time:.2f} ���")

    end_time = time.time()
    total_time = end_time - start_time

    print(f"������� ��������. ����� ��������� �������: {total_time:.2f} ���")
    print(f"���������� �������� � ����: {filename}")

if __name__ == "__main__":
    main()
