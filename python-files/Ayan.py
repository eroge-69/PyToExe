text = "Welcome to Calculator 2.0"
print(text.capitalize())
Number1 = float(input("Enter your Number...."))
operator = input("Enter Operator....+ - * /")
Number2 = float(input("Enter second number....."))
if operator == "+":
    result = Number1 + Number2
elif operator == "-":
    result = Number1 - Number2
elif operator == "*":
    result = Number1 * Number2
elif operator == "/":
    if Number2 != 0:
        result = Number1 / Number2
    else:
        print("0 in invalid for division")
else:
    result = "Invalid Operation"
print(f"result: {result}")
input("Press any button to close....")