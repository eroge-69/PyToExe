def generate_mobile_number_omr():
    print("Mobile Number:\n")
    for column in range(1, 11):
        line = f"Column {column}: "
        for digit in range(10):
            line += f" {digit} ⃝"
        print(line)

def scan_mobile_number(filled_bubbles):
    """
    filled_bubbles: List of 10 integers, each representing the selected digit (0-9) for each column.
    """
    if len(filled_bubbles) != 10:
        print("Error: Mobile number must have exactly 10 digits.")
        return None

    if not all(isinstance(d, int) and 0 <= d <= 9 for d in filled_bubbles):
        print("Error: Invalid digits detected. Each digit must be between 0 and 9.")
        return None

    mobile_number = ''.join(str(d) for d in filled_bubbles)
    print(f"Scanned Mobile Number: {mobile_number}")
    return mobile_number

# Generate the OMR layout
generate_mobile_number_omr()

# Simulate filled bubbles (as if scanned from OMR sheet)
# For example: the user filled 9 8 7 6 5 4 3 2 1 0
filled_bubbles_example = [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]

# Scan and extract the mobile number
scan_mobile_number(filled_bubbles_example)
