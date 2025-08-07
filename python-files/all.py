# ��������� ��� �������� ���� ����� � ���������� ������

def get_number(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("������: ������� ���������� �����.")

# ������ ����� ������� �����
num1 = get_number("������� ������ �����: ")

# ������ ����� ������� �����
num2 = get_number("������� ������ �����: ")

# �������� �����
result = num1 + num2

# ����� ����������
print(f"��������� ��������: {result}")