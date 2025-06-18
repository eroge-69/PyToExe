def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Division by zero is not allowed.")
    return a / b

def main():
    print("=== Ethana Basic Calculator ===")
    while True:
        try:
            print("\nSelect operation:")
            print("1. Addition")
            print("2. Subtraction")
            print("3. Multiplication")
            print("4. Division")
            print("5. Exit")
            choice = input("Enter choice (1/2/3/4/5): ").strip()

            if choice == '5':
                print("Exiting Ethana Basic Calculator. Goodbye!")
                break

            if choice not in ('1', '2', '3', '4'):
                print("Invalid selection! Please choose a valid option.")
                continue

            num1 = float(input("Enter first number: ").strip())
            num2 = float(input("Enter second number: ").strip())

            if choice == '1':
                result = add(num1, num2)
            elif choice == '2':
                result = subtract(num1, num2)
            elif choice == '3':
                result = multiply(num1, num2)
            elif choice == '4':
                result = divide(num1, num2)

            print(f"Result: {result}")

        except ValueError as ve:
            print(f"Error: {ve}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
