def text_to_binary(text_string):
    """
    Converts a text string to its binary representation.

    Args:
        text_string (str): The text to convert.

    Returns:
        str: The binary representation as a single string of '0's and '1's,
             with each 8-bit character separated by a space for readability.
    """
    binary_chunks = []
    # Convert each character to its 8-bit binary representation
    for char in text_string:
        # Get the ASCII value, then format as an 8-bit binary string
        binary_chunks.append(format(ord(char), '08b'))
    
    # Join the binary chunks with a space for readability
    return " ".join(binary_chunks)

def binary_to_text(binary_string):
    """
    Converts a binary string to its text representation.

    Args:
        binary_string (str): The binary data as a single string of '0's and '1's.
                             Can be separated by spaces or not.

    Returns:
        str: The decoded text string.

    Raises:
        ValueError: If the binary string contains non-binary characters
                    or has an invalid length.
    """
    # Remove any spaces to handle inputs with or without spaces
    clean_binary_string = binary_string.replace(" ", "")

    if any(c not in '01' for c in clean_binary_string):
        raise ValueError("Invalid character found in binary string. Please use only '0's and '1's.")

    if len(clean_binary_string) % 8 != 0:
        raise ValueError("Input binary string length must be a multiple of 8.")

    # Split the binary string into 8-bit chunks (bytes)
    binary_chunks = [clean_binary_string[i:i+8] for i in range(0, len(clean_binary_string), 8)]

    # Convert each binary chunk to its corresponding character
    text_characters = [chr(int(chunk, 2)) for chunk in binary_chunks]

    # Join the characters to form the final text string
    return "".join(text_characters)

def main_converter():
    """
    Provides a command-line interface for the user to select and perform a conversion.
    """
    while True:
        print("\n--- Text and Binary Converter ---")
        print("Select an option:")
        print("1. Convert text to binary")
        print("2. Convert binary to text")
        print("3. Exit")

        choice = input("Enter your choice (1, 2, or 3): ")

        if choice == '1':
            user_input = input("Enter the text to convert to binary: ")
            print(f"Result: {text_to_binary(user_input)}")
        
        elif choice == '2':
            user_input = input("Enter the binary string to convert to text: ")
            try:
                print(f"Result: {binary_to_text(user_input)}")
            except ValueError as e:
                print(f"Error: {e}")
        
        elif choice == '3':
            print("Exiting...")
            break
        
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main_converter()