import os

def get_file_lines(path):
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return set(line.strip() for line in file if line.strip())
    except FileNotFoundError:
        print(f"Error: File not found - {path}")
        exit(1)
    except Exception as e:
        print(f"Error reading {path}: {e}")
        exit(1)

def save_unique_lines(unique_lines, output_path):
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            for line in unique_lines:
                file.write(line + '\n')
        print(f"\n✅ Unique lines saved to: {output_path}")
    except Exception as e:
        print(f"Error writing output file: {e}")

def main():
    file1_path = input("Enter the path of the FIRST text file: ").strip()
    file2_path = input("Enter the path of the SECOND text file: ").strip()

    file1_lines = get_file_lines(file1_path)
    file2_lines = get_file_lines(file2_path)

    unique_to_file2 = file2_lines - file1_lines

    # Output file name
    file2_name = os.path.basename(file2_path)
    file2_dir = os.path.dirname(file2_path)
    file2_base, file2_ext = os.path.splitext(file2_name)
    output_filename = f"{file2_base}_UNIQUE{file2_ext}"
    output_path = os.path.join(file2_dir, output_filename)

    # Save and report
    save_unique_lines(unique_to_file2, output_path)

    print("\n📊 Statistics:")
    print(f"  Total lines in FIRST file : {len(file1_lines)}")
    print(f"  Total lines in SECOND file: {len(file2_lines)}")
    print(f"  Unique lines in SECOND file: {len(unique_to_file2)}")

if __name__ == "__main__":
    main()