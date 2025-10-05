def main():
    while True:
        print("\n" + "="*50)
        print("=== ПРОГРАММА ШИФРОВАНИЯ ===")
        print("="*50)
        print("Доступные алгоритмы:")
        print("1. Гронсфельд (строковый ключ)")
        print("2. Гронсфельд (числовой ключ)")
        print("3. Трисемуса")
        print("4. Плейфера")
        print("5. Аффинный Цезарь")
        print("6. Цезарь")
        print("0. Выход")
        
        choice = input("\nВыберите алгоритм (0-6): ").strip()
        
        if choice == '0':
            print("Выход из программы...")
            break
        
        if choice not in ['1', '2', '3', '4', '5', '6']:
            print("Неверный выбор! Попробуйте снова.")
            continue
        
        operation = input("Шифрование (E) или расшифрование (D): ").upper().strip()
        if operation not in ['E', 'D']:
            print("Неверная операция! Используйте E или D.")
            continue
        
        text = input("Введите текст: ").strip()
        if not text:
            print("Текст не может быть пустым!")
            continue
        
        try:
            if choice == '1':
                key = input("Введите строковый ключ (до 10 символов): ").strip()
                if not key:
                    print("Ключ не может быть пустым!")
                    continue
                if operation == 'E':
                    result = gronsfeld_encrypt_text(text, key)
                else:
                    result = gronsfeld_decrypt_text(text, key)
            
            elif choice == '2':
                key_input = input("Введите числовой ключ (через пробел): ").strip()
                if not key_input:
                    print("Ключ не может быть пустым!")
                    continue
                key = [int(x) for x in key_input.split()]
                if operation == 'E':
                    result = gronsfeld_encrypt_text(text, key)
                else:
                    result = gronsfeld_decrypt_text(text, key)
            
            elif choice == '3':
                key = input("Введите ключ для Трисемуса: ").strip()
                if not key:
                    print("Ключ не может быть пустым!")
                    continue
                if operation == 'E':
                    result = trisemus_encrypt(text, key)
                else:
                    result = trisemus_decrypt(text, key)
            
            elif choice == '4':
                key = input("Введите ключ для Плейфера: ").strip()
                if not key:
                    print("Ключ не может быть пустым!")
                    continue
                if operation == 'E':
                    result = playfair_encrypt(text, key)
                else:
                    result = playfair_decrypt(text, key)
            
            elif choice == '5':
                try:
                    a = int(input("Введите коэффициент a (взаимно простой с 26): "))
                    b = int(input("Введите коэффициент b: "))
                    if operation == 'E':
                        result = affine_encrypt(text, a, b)
                    else:
                        result = affine_decrypt(text, a, b)
                except ValueError as e:
                    print(f"Ошибка: {e}")
                    continue
            
            elif choice == '6':
                try:
                    shift = int(input("Введите сдвиг: "))
                    if operation == 'E':
                        result = caesar_encrypt(text, shift)
                    else:
                        result = caesar_decrypt(text, shift)
                except ValueError:
                    print("Сдвиг должен быть числом!")
                    continue
            
            print(f"\nРезультат: {result}")
            
            # Предложение продолжить
            continue_choice = input("\nПродолжить работу? (Y/N): ").upper().strip()
            if continue_choice != 'Y':
                print("Выход из программы...")
                break
                
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            print("Попробуйте снова.")

if __name__ == "__main__":
    main()