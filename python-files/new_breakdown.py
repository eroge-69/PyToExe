import re
import os

while True:

    def get_valid_commission_input():
       while True:
            try:
               commx_str = input("Add % from BO like 18.5: ")
               comm = float(commx_str)
               return comm
            except ValueError:
               print("Error: Please enter a valid number (e.g., 18.5, 20).")


    print("\nNew breakdown for b.com\n")
    print("Hi, lets start with the info we have\n")
    print("\n  ---  Manual Input Values   --- \n")

    total_amountx = input("Please add the total from BO:  ")
    total_amount = float(total_amountx)
    n_n = input("How many nights?:  ")
    number_nights = float(n_n)
    oc = input("Cleaning from PMS:  ") 
    original_cleaning = float(oc)
    ot = input("Towels from PMS (total for all guests):  ") 
    original_towels = float(ot)
    ol = input("Bed linen from PMS (total for all guests):  ") 
    original_linen = float(ol)
    oe = input("Electricity from PMS (total for all guests):  ") 
    original_electricity = float(oe)

    original_extra_fees = [original_cleaning, original_towels, original_linen, original_electricity]
    commission = get_valid_commission_input()
    commp = (100-commission)/100

    commissioned_extra_fees = []

    for fee in original_extra_fees:
            new_fee = fee / commp
            commissioned_extra_fees.append(new_fee)


    tourist_tax_var = input("How much for tourist tax (total for all guests):  ")
    tourist_tax = float(tourist_tax_var)

    elect_total = commissioned_extra_fees[3] * number_nights
    commissioned_extra_fees[3] = elect_total 

    vcc_validation = input ("Is it VCC? Y/N:  ")

    total_commissioned = commissioned_extra_fees[0] + commissioned_extra_fees[1] + commissioned_extra_fees[2] + commissioned_extra_fees[3]
    holiday_home = total_amount - total_commissioned
    nightly_rate = holiday_home / number_nights

    item_names = ["Cleaning fee:  ", "Towels fee:  ", "Bed linen fee:  ", "Electricity fee:  "]

    print("\n\n  ---  Output for the channel  ---\n")
    print(f"Nightly Rate:  {nightly_rate:.2f}")
    print(f"Holiday Home:  {holiday_home:.2f}")
    print("Extra fees including 10% VAT and commissions:  ")

    total_rental = 0.0

    for fee, label in zip(commissioned_extra_fees, item_names):
       if fee > 0:
            print(f"{label}{fee:.2f}")

    if vcc_validation in ["n", "N"]:
            total_rental = total_amount + tourist_tax
            print(f"Total amount (Inc. Tourist Tax): {total_rental:.2f}")
            print(f"FOR THE GUEST: Total amount : {total_amount:.2f}")
    else:
             total_rental = print(f"Total amount (without Tourist Tax): {total_amount:.2f}\n\n")

    user_choice = input("\nRun another calculation (y) or Exit (n)? ").lower()
    
    if user_choice == 'n':
        break
    elif user_choice != 'y':
        print("Invalid input. Please enter 'y' to run again or 'n' to exit.")

input("\nThank you for using the script! Press Enter to close this window...")



