import os
import json

class AC_Capsule:
    def __init__(self, name, charge_per_3_hours, charge_per_24_hours):
        self.name = name
        self.charge_per_3_hours = charge_per_3_hours
        self.charge_per_24_hours = charge_per_24_hours

    def calculate_charge(self, hours):
        if hours <= 3:
            return self.charge_per_3_hours
        else:
            return self.charge_per_24_hours

    def save_booking(self, customer_info):
        folder_path = os.path.join(os.getcwd(), 'AC_Capsule_Bookings')
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, f"{customer_info['name']}_booking.json")
        
        with open(file_path, 'w') as file:
            json.dump(customer_info, file)

def main():
    capsule = AC_Capsule("Mahalakshmi AC Capsule", 300, 400)
    
    name = input("Enter your name: ")
    aadhar_card = input("Enter your Aadhar card number: ")
    num_parties = int(input("Enter number of parties (1, 2, or 3): "))
    
    if num_parties > 1:
        proof_name = input("Enter the name of the person providing proof: ")
        proof_aadhar = input("Enter the Aadhar card number of the proof provider: ")
        customer_info = {
            "name": name,
            "aadhar_card": proof_aadhar,
            "num_parties": num_parties
        }
    else:
        customer_info = {
            "name": name,
            "aadhar_card": aadhar_card,
            "num_parties": num_parties
        }
    
    hours = int(input("Enter number of hours for booking: "))
    charge = capsule.calculate_charge(hours)
    customer_info["charge"] = charge
    
    capsule.save_booking(customer_info)
    print(f"Booking saved! Total charge: {charge}")

if __name__ == "__main__":
    main()
