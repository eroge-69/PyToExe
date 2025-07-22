input_file=input("where is the file?")
output_file=input("where do you want the file placed")

input_file = input_file
output_file = output_file

with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
    for line in infile:
        # Remove trailing commas and any whitespace
        cleaned_line = line.rstrip(', \t\n') + '\n'
        outfile.write(cleaned_line)