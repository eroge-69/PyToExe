"""
Author: Tomas Alexandre
Date: 2025-04-02
Description: This script generates formatted output based on country and postcode inputs. 
Copyright (c) 2025 Tomas Alexandre. All rights reserved.
Unauthorized copying, distribution, or modification of this code is strictly prohibited.
"""

import pyperclip 
import base64

# Hidden Digital Watermark - Do not remove
__author__ = "Tomas Alexandre"
__copyright__ = "Copyright (c) 2025 Your Name. All rights reserved."
__unique_id__ = "WM_Tomas_Alexandre_2025_Escavamos"  # Hidden watermark 

# Encode the watermark
encoded_watermark = base64.b64encode(__unique_id__.encode()).decode()



def get_input(prompt):
    return input(prompt)

def parse_postcode_range(postcode_range):
    """Parses a postcode range (e.g., '50 - 54') and returns a list of all postcodes in that range."""
    postcodes = []
    try:
        start, end = postcode_range.split('-')
        start = int(start.strip())  
        end = int(end.strip())  
        postcodes = [str(i) for i in range(start, end + 1)]  
    except ValueError:
        print("Invalid range format. Please use 'start - end'.")
    return postcodes

def main():
    origin_country = get_input("Enter the 2-digit origin country: ").upper()
    delivery_country = get_input("Enter the 2-digit delivery country: ").upper()

    # Ask for number of origin zones
    origin_zone_input = []
    origin_zone_count = int(get_input(f"How many origin zones for {origin_country}? "))
    for i in range(origin_zone_count):
        origin_zone_name = f"{origin_country}{i+1:02d}"  # Format: XX01, XX02, etc.
        origin_postcodes_input = get_input(f"Enter postcodes for {origin_zone_name} (comma separated, ranges allowed): ")
        origin_postcodes = []
        for postcode in origin_postcodes_input.split(','):
            postcode = postcode.strip()
            if ' - ' in postcode:  
                origin_postcodes.extend(parse_postcode_range(postcode))
            else:
                origin_postcodes.append(postcode)
        origin_zone_input.append((origin_zone_name, origin_postcodes))

    # Ask for number of delivery zones
    delivery_zone_input = []
    delivery_zone_count = int(get_input(f"How many delivery zones for {delivery_country}? "))
    for i in range(delivery_zone_count):
        delivery_zone_name = f"{delivery_country}{i+1:02d}"  # Format: XX01, XX02, etc.
        delivery_postcodes_input = get_input(f"Enter postcodes for {delivery_zone_name} (comma separated, ranges allowed): ")
        delivery_postcodes = []
        for postcode in delivery_postcodes_input.split(','):
            postcode = postcode.strip()
            if ' - ' in postcode:  
                delivery_postcodes.extend(parse_postcode_range(postcode))
            else:
                delivery_postcodes.append(postcode)
        delivery_zone_input.append((delivery_zone_name, delivery_postcodes))

    # Ask for repeat count
    repeat_count = int(get_input("How many times do you want to repeat each value? "))

    # Generate output data
    output_data = []
    for origin_zone_name, origin_postcodes in origin_zone_input:
        for origin_postcode in origin_postcodes:
            for delivery_zone_name, delivery_postcodes in delivery_zone_input:
                for delivery_postcode in delivery_postcodes:
                    result = f"{origin_country}_{origin_postcode}_{delivery_country}_{delivery_postcode} \t {delivery_zone_name}"
                    for _ in range(repeat_count):  
                        output_data.append(result)
    # Save to file
    output_file = "output.txt"
    with open(output_file, "w") as f:
        f.write("\n".join(output_data))
        f.write(f"\n# Watermark (Encoded): {encoded_watermark}")
    # Copy to clipboard
    pyperclip.copy("\n".join(output_data))
    print(f"✅ Output saved to {output_file} and copied to clipboard! Just paste it (Ctrl+V).")

if __name__ == "__main__":
    main()

