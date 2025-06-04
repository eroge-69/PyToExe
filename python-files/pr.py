def process_credit_card_numbers():
    input_file = "biner.txt"
    output_file = "processed_numbers.txt"

    try:
        with open(input_file, "r") as file:
            lines = file.readlines()

        # Extract first 13 digits from each line
        processed_numbers = [line.strip().split('|')[0][:13] for line in lines]

        # Display the results in the console
        print("\nProcessed Credit Card Numbers:")
        for number in processed_numbers:
            print(number)

        # Ask user if they want to save the results
        save_choice = input("\nDo you want to save the processed numbers to a file? (yes/no): ").strip().lower()
        if save_choice == "yes":
            with open(output_file, "w") as file:
                file.write("\n".join(processed_numbers))
            print(f"\nProcessed numbers have been saved to '{output_file}'.")
        else:
            print("\nNo file was created.")

    except FileNotFoundError:
        print(f"\nError: The file '{input_file}' was not found.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    process_credit_card_numbers()
