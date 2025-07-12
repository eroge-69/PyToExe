import os
from datetime import datetime

class MahalakshmiACCapsule:
    def __init__(self):
        self.booking_details = {}
        self.charge_3hours = 300
        self.charge_24hours = 400

    def book_capsule(self):
        print("Welcome to Mahalakshmi AC Capsule Booking!")
        num_persons = int(input("Enter the number of persons: "))
        
        # Get Aadhar card number as proof
        if num_persons == 1:
            proof = input("Enter Aadhar card number for proof: ")
        else:
            proof = input(f"Enter Aadhar card number for one person out of {num_persons}: ")
        
        # Ask for booking duration
        print("\nChoose your booking duration:")
        print("1. 3 Hours")
        print("2. 24 Hours")
        choice = int(input("Enter your choice (1/2): "))
        
        if choice == 1:
            charge = self.charge_3hours
            duration = "3 Hours"
        elif choice == 2:
            charge = self.charge_24hours
            duration = "24 Hours"
        else:
            print("Invalid choice. Booking cancelled.")
            return
        
        total_charge = charge * num_persons
        
        # Save booking details
        booking_id = datetime.now().strftime("%Y%m%d%H%M%S")
        self.booking_details[booking_id] = {
            "Number of Persons": num_persons,
            "Proof": proof,
            "Duration": duration,
            "Total Charge": total_charge
        }
        
        # Save to a new folder
        self.save_booking_details(booking_id)

    def save_booking_details(self, booking_id):
        folder_name = "Mahalakshmi_AC_Capsule_Bookings"
        folder_path = os.path.join(os.getcwd(), folder_name)
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        file_name = f"Booking_{booking_id}.txt"
        file_path = os.path.join(folder_path, file_name)
        
        with open(file_path, 'w') as file:
            file.write(f"Booking ID: {booking_id}\n")
            for key, value in self.booking_details[booking_id].items():
                file.write(f"{key}: {value}\n")
        
        print(f"\nBooking successful! Details saved to: {file_path}")

if __name__ == "__main__":
    capsule = MahalakshmiACCapsule()
    capsule.book_capsule()
