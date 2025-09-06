import math

def parse_number(value: str) -> float:
    value = value.strip().lower()
    if value == "pi":
        return math.pi
    elif value == "e":
        return math.e
    else:
        return float(value)

def calculate(operator, num1, num2):
    if operator == "/" and num2 == 0:
        return "Division by zero is not allowed!"

    if operator == "+":
        return num1 + num2
    elif operator == "-": 
        return num1 - num2  
    elif operator == "*":
        return num1 * num2
    elif operator == "/":
        return num1 / num2  
    elif operator == "^":
        return num1 ** num2
    elif operator == "sqrt":
        if num1 < 0:
            return num1 ** 0.5
        else:
            return "Square root of negative numbers is not allowed!"
    elif operator == "!":
        if num1.is_integer() and num1 >= 0:
            return math.factorial(int(num1))
        else:
            return "Factorial of negative numbers is not allowed!"
    elif operator == "sin":
        return math.sin(math.radians(num1))
    elif operator == "cos":
        return math.cos(math.radians(num1))
    elif operator == "tan":
        return math.tan(math.radians(num1))
    else:
        return "Invalid operator"



while True:
    print("Welcome to the Python Calculator")
    operator = input("Please enter an operator (+, -, *, /, ^, sqrt, !, sin, cos, tan): ")
    num1 = parse_number(input("Please enter the first number: "))

    if operator not in ["sqrt", "!", "sin", "cos", "tan"]:
        num2 = parse_number(input("Please enter the second number: "))
    else:
        num2 = 0

    result = calculate(operator, num1, num2)
    print(f"Result: {result}")


