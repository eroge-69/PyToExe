# Sample data
list1 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'R', 'S', 'T', 'V', 'W', 'X', 'Y', '1', '2', '3', '4', '5', '6', '7', '8', '9']  # List of 30 strings
list2 = [i * 1 for i in range(1980, 2009)]      # List of 30 integers: 1980...2009

# Display list1 for reference
print("Available items in list1:")
print(list1)

# Get user input
user_input = input("\nEnter an item from list1: ").upper()

# Check if input exists in list1
if user_input in list1:
    index = list1.index(user_input)
    corresponding_number = list2[index]
    
    print(f"\nFirst dtae is: {corresponding_number}")
    print(f"Second Date: {corresponding_number + 30}")
else:
    print("\nItem not found in list1. Please try again with a valid item.")
