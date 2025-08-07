# Program to add two numbers with error handling

def get_number(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Error: Please enter a valid number.")

# Request input for the first number
num1 = get_number("Enter the first number: ")

# Request input for the second number
num2 = get_number("Enter the second number: ")

# Add the numbers
result = num1 + num2

# Display the result
print(f"The result of addition is: {result}")