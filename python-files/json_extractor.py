
import json
import sys

def extract_values(data, key):
    """Recursively extract values from JSON based on key."""
    arr = []
    if isinstance(data, dict):
        for k, v in data.items():
            if k == key:
                arr.append(v)
            arr.extend(extract_values(v, key))
    elif isinstance(data, list):
        for item in data:
            arr.extend(extract_values(item, key))
    return arr

def main():
    if len(sys.argv) < 2:
        print("Usage: python json_extractor.py <json_file_path> [key]")
        print("If key is not provided, you will be prompted to enter it.")
        sys.exit(1)

    json_file_path = sys.argv[1]
    key_to_extract = None

    if len(sys.argv) > 2:
        key_to_extract = sys.argv[2]

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {json_file_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {json_file_path}")
        sys.exit(1)

    if key_to_extract is None:
        key_to_extract = input("Enter the key to extract (e.g., user_id): ")

    extracted_values = extract_values(json_data, key_to_extract)

    if not extracted_values:
        print(f"No values found for key '{key_to_extract}'.")
        sys.exit(0)

    while True:
        print("\nHow would you like to structure the output?")
        print("1. Comma-separated")
        print("2. Each value on a new line")
        choice = input("Enter your choice (1 or 2): ")

        if choice == '1':
            print(", ".join(map(str, extracted_values)))
            break
        elif choice == '2':
            for value in extracted_values:
                print(value)
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()


