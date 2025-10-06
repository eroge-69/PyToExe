import math

def add(a, b): return a + b
def subtract(a, b): return a - b
def multiply(a, b): return a * b
def divide(a, b): return "Cannot divide by zero" if b == 0 else a / b
def modulus(a, b): return a % b
def exponent(a, b): return a ** b
def floor_divide(a, b): return a // b
def absolute(a): return abs(a)
def negate(a): return -a
def square(a): return a ** 2
def cube(a): return a ** 3
def square_root(a): return math.sqrt(a)
def cube_root(a): return round(a ** (1/3), 5)
def sign(a):
    if a > 0: return "Positive"
    elif a < 0: return "Negative"
    else: return "Zero"
def sin(a): return math.sin(math.radians(a))
def cos(a): return math.cos(math.radians(a))
def tan(a): return math.tan(math.radians(a))
def log(a): return "Undefined for non-positive values" if a <= 0 else math.log10(a)
def antilog(a): return 10 ** a

print("Complex Calculator")
print("Select operation:")
print("1. Add")
print("2. Subtract")
print("3. Multiply")
print("4. Divide")
print("5. Modulus")
print("6. Exponent")
print("7. Floor Divide")
print("8. Absolute")
print("9. Negate")
print("10. Square")
print("11. Cube")
print("12. Square Root")
print("13. Cube Root")
print("14. Sign")
print("15. Sine")
print("16. Cosine")
print("17. Tangent")
print("18. Logarithm")
print("19. Antilogarithm")
print("20. Exit")

while True:
    choice = input("Enter choice (1-20): ")
    if choice == '20':
        print("Exiting calculator.")
        break

    try:
        if choice in ['1','2','3','4','5','6','7']:
            num1 = float(input("Enter first number: "))
            num2 = float(input("Enter second number: "))
        elif choice in ['8','9','10','11','12','13','14','15','16','17','18','19']:
            num1 = float(input("Enter number: "))
    except ValueError:
        print("Invalid input. Please enter numeric values.")
        continue

    if choice == '1':
        print("Result:", add(num1, num2))
    elif choice == '2':
        print("Result:", subtract(num1, num2))
    elif choice == '3':
        print("Result:", multiply(num1, num2))
    elif choice == '4':
        print("Result:", divide(num1, num2))
    elif choice == '5':
        print("Result:", modulus(num1, num2))
    elif choice == '6':
        print("Result:", exponent(num1, num2))
    elif choice == '7':
        print("Result:", floor_divide(num1, num2))
    elif choice == '8':
        print("Result:", absolute(num1))
    elif choice == '9':
        print("Result:", negate(num1))
    elif choice == '10':
        print("Result:", square(num1))
    elif choice == '11':
        print("Result:", cube(num1))
    elif choice == '12':
        print("Result:", square_root(num1))
    elif choice == '13':
        print("Result:", cube_root(num1))
    elif choice == '14':
        print("Result:", sign(num1))
    elif choice == '15':
        print("Result:", sin(num1))
    elif choice == '16':
        print("Result:", cos(num1))
    elif choice == '17':
        print("Result:", tan(num1))
    elif choice == '18':
        print("Result:", log(num1))
    elif choice == '19':
        print("Result:", antilog(num1))
    else:
        print("Invalid choice.")