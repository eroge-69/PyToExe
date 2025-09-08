"""
Generates random IMEI numbers in AT command format and saves them to imei.txt.
Uses a predefined list of TAC numbers with identifiers.
"""

import sys
import random
import os
from datetime import datetime
from pathlib import Path


# Predefined list of TAC numbers with identifiers
PREDEFINED_TACS = [
    ("86600507", "U60 PRO,MU5250"),
    ("35461444", "iPhone 16 Pro Max"),
    ("35500828", "16 Pro Max Unlocked"),
    ("35204553", "Apple iPad Pro 13 m4 2024"),
    ("35890743", "Nighthawk M7 Pro MR7400"),
    ("86278507", "FiberHome 5G CPE Pro"),
    ("86073604", "mikrotik"),
    ("86167907", "ZTE G5 ULTRA"),
    ("35573167", "Galaxy S24 Ultra"),
    ("35554513", "S24 Ultra"),
    ("35886618", "Asus ROG Phone 9 Pro"),
    ("35948965", "Google Pixel 10 Pro XL"),
    ("01602600", "M6 NETGEAR MR6150"),
    ("01634700", "M6 Pro NETGEAR MR6400 MR6450 MR6550"),
    ("86316707", "FiberHome 5G Outdoor LG6121D"),
    ("35190977", "ZYXEL NR5103EV2"),
    ("86717306", "H158-381"),
    ("86968607", "Pro 5 E6888-982"),
    # Add more TACs here as needed
    # Format: ("TAC_NUMBER", "Device Name"),
]


# Src: https://github.com/arthurdejong/python-stdnum/blob/master/stdnum/luhn.py
def checksum(number, alphabet='0123456789'):
    """
    Calculate the Luhn checksum over the provided number.

    The checksum is returned as an int.
    Valid numbers should have a checksum of 0.
    """
    n = len(alphabet)
    number = tuple(alphabet.index(i)
                   for i in reversed(str(number)))
    return (sum(number[::2]) +
            sum(sum(divmod(i * 2, n))
                for i in number[1::2])) % n


def calc_check_digit(number, alphabet='0123456789'):
    """Calculate the extra digit."""
    check_digit = checksum(number + alphabet[0])
    return alphabet[-check_digit]


def generate_imeis(tac_base, count):
    """Generate IMEI numbers based on the provided TAC base."""
    imeis = []
    for _ in range(count):
        imei = tac_base
        
        # Randomly compute the remaining serial number digits
        while len(imei) < 14:
            imei += str(random.randint(0, 9))

        # Calculate the check digit with the Luhn algorithm
        imei += calc_check_digit(imei)
        imeis.append(imei)
    
    return imeis


def main():
    """Generate IMEIs for all predefined TACs in AT command format."""
    # Check if we have any predefined TACs
    if not PREDEFINED_TACS:
        return
    
    # Set the number of IMEIs to generate per TAC
    count_per_tac = 3
    
    # Generate IMEIs for each TAC
    all_imeis = []
    for tac, identifier in PREDEFINED_TACS:
        imeis = generate_imeis(tac, count_per_tac)
        # Store with identifier
        all_imeis.append({
            'tac': tac,
            'identifier': identifier,
            'imeis': imeis
        })
    
    # Get the script directory for saving files
    script_dir = Path(__file__).parent.absolute()
    
    # Save to file with AT command format
    try:
        filename = script_dir / 'imei_commands.txt'
        # Add timestamp to filename if it already exists to avoid overwriting
        if os.path.exists(filename):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = script_dir / f"imei_commands_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            # Write header information
            f.write(f"# Generated IMEI AT commands\n")
            f.write(f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# IMEIs per TAC: {count_per_tac}\n")
            f.write("#" * 60 + "\n\n")
            
            for group in all_imeis:
                f.write(f"# {group['identifier']} (TAC: {group['tac']}):\n")
                
                for imei in group['imeis']:
                    f.write(f'interface lte at-chat lte1 input="AT+EGMR=1,7,\\"{imei}\\"\n')
                
                f.write("/system reboot\n\n")
                
        print(f"File saved to: {filename}")
                
    except IOError as e:
        print(f"Error saving file: {e}")
    
    # Display only the AT commands in console
    for group in all_imeis:
        print(f"# {group['identifier']} (TAC: {group['tac']}):")
        for imei in group['imeis']:
            print(f'interface lte at-chat lte1 input="AT+EGMR=1,7,\\"{imei}\\"')
        print("/system reboot\n")
    
    # Add a pause to prevent the window from closing immediately
    try:
        input("Press Enter to exit...")
    except:
        pass


if __name__ == '__main__':
    main()