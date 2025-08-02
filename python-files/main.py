def process_large_hex_string(input_file_path, output_file_path):
    with open(input_file_path, 'r') as f:
        hex_string = f.read()

    # Remove any non-hex characters if necessary
    hex_string = ''.join(filter(str.isalnum, hex_string))
    
    # Check if length is multiple of 6
    length = len(hex_string)
    if length % 6 != 0:
        print(f"Warning: String length {length} is not a multiple of 6.")
        # Optionally, truncate or pad
        hex_string = hex_string[:length - (length % 6)]
    
    # Break into chunks of 6
    colors = [hex_string[i:i+6] for i in range(0, len(hex_string), 6)]
    
    # Prepend '#' to each
    color_codes = ['#' + color for color in colors]
    
    # Save to output file
    with open(output_file_path, 'w') as f:
        for code in color_codes:
            f.write(code + '\n')
    
    print(f"Processed {len(color_codes)} color codes and saved to {output_file_path}")

# Usage:
# Save your large hex string in a file, e.g., 'input_hex.txt'
# process_large_hex_string('input_hex.txt', 'output_colors.txt')