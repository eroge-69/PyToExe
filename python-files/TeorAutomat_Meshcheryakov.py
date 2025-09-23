def GetBit(prompt: str) -> int:
    while True:
        bit = input(prompt)
        if bit in ('0', '1'):
            return int(bit)
        print("Некорректный ввод: введите 0 или 1.")


def GetFullState() -> str:
    while True:
        state = input("\nВведите 3-битное состояние (например, 101): ")
        if len(state) == 3 and all(c in '01' for c in state):
            return state
        print("Некорректный ввод. Введите строку из трёх символов 0 или 1.")


def CheckInputState():
    print("\nНачало алгоритма")
    while True:
        print("Выполняется Y0.")
        
        print("Вход в условную вершину X0.")
        state_x0 = GetBit("Введите значение X0 ('0' или '1'): ")
        
        if state_x0 == 0:
            print("Выполняется Y2.")
        else:
            print("Выполняется Y1.")

        print("Вход в условную вершину X1.")
        state_x1 = GetBit("Введите значение X1 ('0' или '1'): ")
        
        if state_x1 == 0:
            print("Выполняется Y3.")
        else:
            print("Продолжение к X2.")

        print("Вход в условную вершину X2.")
        state_x2 = GetBit("Введите значение X2 ('0' или '1'): ")
        
        if state_x2 == 1:
            print("Цикл: возврат к Y0.")
            continue  
        else:
            print("Конец алгоритма")
            break

def CheckFullState(state: str):
    print(f"\nПроверка состояния {state}:")
    print("Начало алгоритма")
    
    x0, x1, x2 = state[0], state[1], state[2]
    
    # Y0
    print("Выполняется Y0.")
    
    # X0
    print("Вход в условную вершину X0.")
    if x0 == '0':
        print("Выполняется Y2.")
    else:
        print("Выполняется Y1.")
    
    # X1
    print("Вход в условную вершину X1.")
    if x1 == '0':
        print("Выполняется Y3.")
    else:
        print("Продолжение к X2.")
    
    # X2 — ВСЕГДА выполняется после X1
    print("Вход в условную вершину X2.")
    if x2 == '1':
        print("Цикл: возврат к Y0.")
        return  # Цикл — завершаем проверку состояния
    else:
        print("Конец алгоритма")


def CheckAllStates():
    for i in "01":
        for j in "01":
            for k in "01":
                state = i + j + k
                print(f"\nПроверка состояния {state}:")
                CheckFullState(state)


def main():
    while True:
        print("\nНачало работы с алгоритмом: Yн → Y0 → X0 → (Y2/Y1) → X1 → (Y3/→X2) → X2 → (Yк/→Y0)")
        print("Выберите режим:")
        print("  1 - Пошаговый ввод")
        print("  2 - Ввод полного состояния")
        print("  3 - Проверка всех состояний")

        mode = input("Режим: ")

        if mode == "1":
            CheckInputState()
        elif mode == "2":
            state = GetFullState()
            CheckFullState(state)
        elif mode == "3":
            CheckAllStates()
        else:
            print("Некорректный режим. Попробуйте снова.")
            continue

        print("\nПрограмма завершена")
        input("Нажмите Enter для выхода...")
        return


#if name == "main":
main()
