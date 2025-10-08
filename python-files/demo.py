# Step 1: Read two files and zip their lines
def zip_files(file1, file2, output_file):
    try:
        with open(file1, 'r') as f1, open(file2, 'r') as f2:
            lines1 = [line.strip() for line in f1]
            lines2 = [line.strip() for line in f2]

        zipped = list(zip(lines1, lines2))

        with open(output_file, 'w') as out:
            for item1, item2 in zipped:
                out.write(f"{item1},{item2}\n")

        print(f"\n✅ Zipped data written to '{output_file}'")
        return zipped

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return []

# Step 2: Read zipped file and unzip it
def unzip_file(zipped_file):
    try:
        with open(zipped_file, 'r') as f:
            lines = f.readlines()

        zipped = [line.strip().split(',') for line in lines if ',' in line]

        if zipped:
            col1, col2 = zip(*zipped)
            print("\n📤 Unzipped Content:")
            print("First Column :", list(col1))
            print("Second Column:", list(col2))
        else:
            print("⚠️ No zipped data to unzip.")

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")

# Main program execution
if __name__ == "__main__":
    print("📁 Enter the file names to zip:")
    file1 = input("Enter first input file path (e.g., numbers.txt): ").strip()
    file2 = input("Enter second input file path (e.g., letters.txt): ").strip()
    output_file = input("Enter output file name (e.g., zipped_output.txt): ").strip()

    zipped_data = zip_files(file1, file2, output_file)

    if zipped_data:
        unzip_file(output_file)
