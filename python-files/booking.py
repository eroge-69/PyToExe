def get_booking_details():
    print("Welcome to Mahalakshmi AC Capsule Booking\n")
    
    # Get number of persons
    while True:
        try:
            persons = int(input("Enter number of persons: "))
            if persons <= 0:
                print("Please enter a valid number of persons (at least 1).")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    # Show pricing
    print("\nSelect duration:")
    print("1. 3 hours - ₹300 per person")
    print("2. 24 hours - ₹400 per person")
    
    # Get duration and price
    while True:
        duration_choice = input("Enter 1 or 2: ")
        if duration_choice == '1':
            price_per_person = 300
            duration = "3 hours"
            break
        elif duration_choice == '2':
            price_per_person = 400
            duration = "24 hours"
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")
    
    # Aadhaar input
    if persons == 1:
        aadhaar = input("Enter Aadhaar card number (single person): ")
    else:
        aadhaar = input("Enter Aadhaar card number of one member in the group: ")
    
    # Validate Aadhaar length (optional)
    if len(aadhaar) != 12 or not aadhaar.isdigit():
        print("⚠️  Warning: Aadhaar number should be 12 digits. Proceeding anyway.")

    # Calculate total
    total_amount = persons * price_per_person

    # Summary
    print("\n--- Booking Summary ---")
    print(f"Number of persons : {persons}")
    print(f"Duration          : {duration}")
    print(f"Price per person  : ₹{price_per_person}")
    print(f"Total amount      : ₹{total_amount}")
    print(f"Aadhaar (proof)   : {aadhaar}")
    print("\n✅ Booking Confirmed. Thank you!")

# Run the booking system
get_booking_details()
