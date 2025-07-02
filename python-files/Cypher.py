import json

def apply_legend(text, legend, encode=True):
    """
    Applies or reverses the letter replacement based on the provided legend.

    Args:
        text (str): The input text to apply the legend to.
        legend (dict): The dictionary mapping original letters to replacement letters.
        encode (bool): If True, applies the legend (original -> replacement).
                       If False, reverses the legend (replacement -> original).

    Returns:
        str: The text after applying/reversing the legend.
    """
    result = []
    replacement_map = {}

    if encode:
        replacement_map = legend
    else:
        # Create a reverse map for decoding
        for original, replacement in legend.items():
            replacement_map[replacement] = original

    for char in text:
        upper_char = char.upper()
        if upper_char in replacement_map:
            # Preserve original casing if possible
            if char.isupper():
                result.append(replacement_map[upper_char])
            else:
                result.append(replacement_map[upper_char].lower())
        else:
            result.append(char)  # Keep character as is if not in legend
    return "".join(result)

def encode_word(word):
    """
    Encodes a single word based on its length and the defined rules.

    Args:
        word (str): The word to encode.

    Returns:
        str: The encoded word.
    """
    word_len = len(word)
    if word_len == 0:
        return ""

    if word_len % 2 == 0:
        # Even letter word: first half + reversed second half
        mid = word_len // 2
        first_half = word[:mid]
        second_half_reversed = word[mid:][::-1]
        return first_half + second_half_reversed
    else:
        # Odd letter word: second (longer) half + "'" + reversed first half
        first_half_length = word_len // 2
        first_half = word[:first_half_length]
        second_half = word[first_half_length:] # This is the longer half
        first_half_reversed = first_half[::-1]
        return second_half + "'" + first_half_reversed

def decode_word(encoded_word):
    """
    Decodes a single word based on its structure and the defined rules.

    Args:
        encoded_word (str): The encoded word to decode.

    Returns:
        str: The decoded word.
    """
    if not encoded_word:
        return ""

    apostrophe_index = encoded_word.find("'")
    if apostrophe_index != -1:
        # It's an odd-letter word transformation
        # Structure: secondHalf + "'" + firstHalfReversed
        second_half = encoded_word[:apostrophe_index]
        first_half_reversed = encoded_word[apostrophe_index + 1:]
        first_half = first_half_reversed[::-1]
        return first_half + second_half # Reconstruct original word
    else:
        # It's an even-letter word transformation (or an original word not following odd rule)
        # Structure: firstHalf + reversedSecondHalf
        original_length = len(encoded_word)
        mid = original_length // 2
        first_half = encoded_word[:mid]
        reversed_second_half = encoded_word[mid:]
        second_half = reversed_second_half[::-1]
        return first_half + second_half

def process_text(text, legend, mode):
    """
    Processes the entire text (encrypts or decrypts) based on the mode.

    Args:
        text (str): The input text to process.
        legend (dict): The letter replacement legend.
        mode (str): 'encrypt' or 'decrypt'.

    Returns:
        str: The processed text.
    """
    # Split text by spaces, keeping the spaces for rejoining
    words_and_spaces = []
    current_word = []
    for char in text:
        if char.isspace():
            if current_word:
                words_and_spaces.append("".join(current_word))
                current_word = []
            words_and_spaces.append(char)
        else:
            current_word.append(char)
    if current_word:
        words_and_spaces.append("".join(current_word))

    processed_parts = []
    for part in words_and_spaces:
        if part.strip() == '': # It's a space or punctuation block
            processed_parts.append(part)
        else:
            if mode == 'encrypt':
                # Apply word rule, then legend
                transformed_word = encode_word(part)
                processed_parts.append(apply_legend(transformed_word, legend, True))
            else: # mode == 'decrypt'
                # Reverse legend, then reverse word rule
                legend_decoded_word = apply_legend(part, legend, False)
                processed_parts.append(decode_word(legend_decoded_word))
    return "".join(processed_parts)

if __name__ == "__main__":
    # Default legend: Vowels replaced by other vowels, Consonants by other consonants
    default_legend = {
        'A': 'E', 'E': 'I', 'I': 'O', 'O': 'U', 'U': 'A',
        'B': 'D', 'C': 'F', 'D': 'B', 'F': 'C', 'G': 'J', 'H': 'K', 'J': 'G', 'K': 'H', 'L': 'N',
        'M': 'P', 'N': 'L', 'P': 'M', 'Q': 'S', 'R': 'T', 'S': 'Q', 'T': 'R', 'V': 'W', 'W': 'X',
        'X': 'Y', 'Y': 'Z', 'Z': 'V'
    }

    print("Welcome to the Custom Cypher Tool (Python Version)!")

    while True:
        print("\n--- Menu ---")
        print("1. Encrypt Text")
        print("2. Decrypt Text")
        print("3. View Current Legend")
        print("4. Set Custom Legend")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            input_text = input("Enter text to encrypt: ")
            output_text = process_text(input_text, default_legend, 'encrypt')
            print("\nEncrypted Text:")
            print(output_text)
        elif choice == '2':
            input_text = input("Enter text to decrypt: ")
            output_text = process_text(input_text, default_legend, 'decrypt')
            print("\nDecrypted Text:")
            print(output_text)
        elif choice == '3':
            print("\nCurrent Letter Replacement Legend:")
            print(json.dumps(default_legend, indent=4))
        elif choice == '4':
            print("\nEnter your custom legend as a JSON string (e.g., {'A': 'Z', 'B': 'Y'}):")
            print("Note: Ensure keys and values are single uppercase letters and valid JSON.")
            custom_legend_str = input("Custom Legend JSON: ")
            try:
                parsed_legend = json.loads(custom_legend_str)
                # Basic validation: ensure keys/values are single uppercase letters
                is_valid = True
                for k, v in parsed_legend.items():
                    if not (isinstance(k, str) and len(k) == 1 and k.isupper() and
                            isinstance(v, str) and len(v) == 1 and v.isupper()):
                        is_valid = False
                        break
                if is_valid:
                    default_legend = parsed_legend
                    print("Legend updated successfully!")
                else:
                    print("Error: Legend keys/values must be single uppercase letters.")
            except json.JSONDecodeError:
                print("Error: Invalid JSON format. Please try again.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
        elif choice == '5':
            print("Exiting Cypher Tool. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

