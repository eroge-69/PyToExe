
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: drag and drop a text file onto this exe.")
        input("Press Enter to exit...")
        return

    file_path = sys.argv[1]
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        numbers = [int(x.strip()) for x in content.split(",") if x.strip().isdigit()]
        if numbers:
            print("Largest number in file:", max(numbers))
        else:
            print("No valid numbers found in the file.")

    except Exception as e:
        print("Error:", e)

    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
