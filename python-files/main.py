def calculator():
    print("🔢 КаЛьКуЛяТоР 🔢")
    print("=" * 17)
    
    while True:
        print("\nВыберите операцию:")
        print("1. ➕Сложение➕ (+)")
        print("2. ➖Вычитание➖ (-)")
        print("3. ✖️Умножение✖️ (*)")
        print("4. ➗Деление➗ (/)")
        print("5. 🔴Выход🔴")
        
        choice = input("\nВаш выбор (1-5): ").strip()
        
        if choice == '5':
            print("До свидания! 👋")
            break
            
        if choice not in ['1', '2', '3', '4']:
            print("❌ Неверный выбор! Попробуйте снова.")
            continue
            
        try:
            # Ввод чисел
            num1 = float(input("Введите первое число: "))
            num2 = float(input("Введите второе число: "))
            
            # Проверка на 52 в любом из чисел
            if num1 == 52 or num2 == 52:
                print("\n" + "=" * 60)
                print("🎉 ПЯТЬДЕСЯТ ДВА! Это Санкт-Питербург. И ЭТОТ ГОРОД НАШ 🎉")
                print("=" * 60)
                # Продолжаем вычисления несмотря на сюрприз
            
            # Выполнение операций
            if choice == '1':
                result = num1 + num2
                print(f"\nРезультат: {num1} + {num2} = {result}")
                
            elif choice == '2':
                result = num1 - num2
                print(f"\nРезультат: {num1} - {num2} = {result}")
                
            elif choice == '3':
                result = num1 * num2
                print(f"\nРезультат: {num1} * {num2} = {result}")
                
            elif choice == '4':
                if num2 == 0:
                    print("❌ Ошибка: Деление на ноль!")
                else:
                    result = num1 / num2
                    print(f"\nРезультат: {num1} / {num2} = {result}")
            
            # Дополнительная проверка результата на 52
            if 'result' in locals() and result == 52:
                print("🎉 ПЯТЬДЕСЯТ ДВА! Это Санкт-Питербург. И ЭТОТ ГОРОД НАШ 🎉")
                    
        except ValueError:
            print("❌ Ошибка: Введите корректные числа!")
        except Exception as e:
            print(f"❌ Произошла ошибка: {e}")

# Запуск калькулятора
if __name__ == "__main__":
    calculator()