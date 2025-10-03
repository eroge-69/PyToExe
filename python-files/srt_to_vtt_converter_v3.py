# This will read the content from input_file.txt, replace the commas in the timestamps
#with dots, and save the modified content to a new file named output_input_file.txt
#check if the input file extension is .srt and if so, add the word WEBVTT followed by a new empty line at the beginning of the output file and change output file extension to .vtt

import re
import sys
import os

def replace_timestamps(text):
    # Regular expression pattern to match timestamps with commas
    pattern = r'(\d{2}:\d{2}:\d{2}),(\d{3})'
    # Replace commas with dots in the matched timestamps
    replaced_text = re.sub(pattern, r'\1.\2', text)
    return replaced_text

def main(input_file):
    # Check if the input file has .srt extension
    is_srt = input_file.lower().endswith('.srt')
    
    # Read from the input file
    with open(input_file, 'r') as file:
        text = file.read()

    # Replace the timestamps
    new_text = replace_timestamps(text)

    # Determine the output file name and extension
    if is_srt:
        output_file = os.path.splitext(input_file)[0] + '.vtt'
        new_text = "WEBVTT\n\n" + new_text
    else:
        output_file = 'output_' + input_file

    # Write the modified content to the output file
    with open(output_file, 'w') as file:
        file.write(new_text)

    print(f"Timestamps have been replaced and saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python replace_timestamps.py input-file-name")
        sys.exit(1)

    input_file = sys.argv[1]
    main(input_file)
