# A simple script to split a large .obj file into smaller files,
# one for each object ('o' tag) found in the file.

def split_obj_file(input_path):
    """
    Reads a .obj file line by line and splits it into multiple .obj files
    based on the object 'o' tags.
    """
    output_file = None
    file_counter = 0
    
    # Open the huge input file for reading
    with open(input_path, 'r') as infile:
        for line in infile:
            # Check if the line defines a new object
            if line.startswith('o '):
                # If we were already writing to a file, close it
                if output_file:
                    output_file.close()
                
                # Get the object name to use as the filename
                object_name = line.strip().split()[1]
                file_name = f"{object_name}.obj"
                
                print(f"Creating new file: {file_name}")
                output_file = open(file_name, 'w')
                file_counter += 1

            # If we have an open output file, write the current line to it
            if output_file:
                output_file.write(line)

    # Close the last opened file
    if output_file:
        output_file.close()

    print(f"\nFinished! Split the file into {file_counter} smaller files.")

# --- HOW TO USE ---
# 1. Save this code as a Python file (e.g., split_obj.py).
# 2. Place it in the same folder as your huge .obj file.
# 3. Change 'your_huge_file.obj' to the actual name of your file.
# 4. Run the script from your terminal: python split_obj.py

if __name__ == '__main__':
    # Replace this with the name of your file
    input_file_name = 'your_huge_file.obj' 
    split_obj_file(input_file_name)