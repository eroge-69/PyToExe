# Define the data tables using dictionaries
metal_data = {
    '00': 'No metal', '01': 'Pancha Dhatu', '02': 'Silver',
    '03': '925 silver', '04': 'Gold', '05': 'Gold plate'
}

colour_data = {
    '00': 'Clear', '01': 'White', '02': 'Yellow', '03': 'Orange',
    '04': 'Red', '05': 'Pink', '06': 'Purple', '07': 'Blue',
    '08': 'Green', '09': 'Brown', '10': 'Grey', '11': 'Black'
}

stone_data = {
    '00': 'No Stone', '01': 'Spinel', '02': 'Tanzanite', '03': 'Sapphire',
    '04': 'Ruby', '05': 'Black opal', '06': 'Blue Topaz', '07': 'Sunstone',
    '08': 'Kunzite', '09': 'Labadorite', '10': 'Sugilite', '11': 'Pearl',
    '12': 'Malachite', '13': 'Larvikite', '14': 'Diaspore', '15': 'Rhodolite',
    '16': 'Prehnite', '17': 'Onyx', '18': 'Bark Rubite', '19': 'Ruby Zoisite',
    '20': 'Amethyst', '21': 'Coral', '22': 'Azurite', '23': 'Citrine',
    '24': 'Zircon', '25': 'Morganite', '26': 'T-Savorite', '27': 'Tourmaline',
    '28': 'Aquamarine', '29': 'Chaulite', '30': 'Smoky Quartz', '31': 'Bumble Bee',
    '32': 'Ametrine', '33': 'Flowrite', '34': 'Zeosite', '35': 'Topaz',
    '36': 'Rubellite', '37': 'Hessonite', '38': 'Emerald', '39': 'Moonstone',
    '40': 'Maldavite', '41': 'Rhodonite', '42': 'Lemon Quartz', '43': 'Amber',
    '44': 'Gold Rutile', '45': 'Apatite', '46': 'Tiger eye', '47': 'Unakite',
    '48': 'Lolita', '49': 'Rose Quartz', '50': 'Carnelian', '51': 'Honey Quartz',
    '52': 'Chrome', '53': 'Diamond', '54': 'Opal', '55': 'Lapis',
    '56': 'Proustite', '57': 'Peridot', '58': 'Turquoise', '59': 'Agate',
    '60': 'Howlite', '61': 'Sodalite', '62': 'Sphene', '63': 'Indigo Gabbro'
}

clarity_data = {
    '00': 'Eye Clean', '01': 'Slight inclusion', '02': 'Moderate inclusion',
    '03': 'Heavy inclusion', '04': 'Opaque'
}

cut_data = {
    '01': 'Pear', '02': 'Oval', '03': 'Cushion', '04': 'Asscher',
    '05': 'Marquise', '06': 'Radiant', '07': 'Emerald', '08': 'Round'
}

# New dictionary for the price lookup
price_codes = {
    'G': 1, 'H': 2, 'I': 3, 'J': 4, 'K': 5,
    'L': 6, 'M': 7, 'N': 8, 'O': 9, 'P': 0
}

def decode_jewelry_code(code):
    """
    Decodes a 17-character jewelry code string into item details.
    
    The assumed code structure is:
    Price (4 char) + Metal (2 char) + Colour (2 char) + Stone (2 char) + Clarity (2 char) + Carat (3 char) + Cut (2 char)
    Total = 17 characters
    """
    # Check for the correct length of the code
    if len(code) != 17:
        print("Error: The code must be exactly 17 characters long.")
        return

    # Split the code into its component parts based on the new structure
    price_code = code[0:4]
    metal_code = code[4:6]
    colour_code = code[6:8]
    stone_code = code[8:10]
    clarity_code = code[10:12]
    carat_code = code[12:15]
    cut_code = code[15:17]

    # Handle Price calculation
    price = "Unknown Price"
    try:
        thousands = price_codes.get(price_code[0], None)
        hundreds = price_codes.get(price_code[1], None)
        tens = price_codes.get(price_code[2], None)
        ones = price_codes.get(price_code[3], None)
        
        if all(val is not None for val in [thousands, hundreds, tens, ones]):
            price_val = (thousands * 1000) + (hundreds * 100) + (tens * 10) + ones
            price = str(price_val)
    except (IndexError, TypeError):
        pass # Keep 'Unknown Price' if there's an issue with the code format

    # Look up other descriptions using the dictionaries
    metal = metal_data.get(metal_code, "Unknown Metal")
    colour = colour_data.get(colour_code, "Unknown Colour")
    stone = stone_data.get(stone_code, "Unknown Stone")
    clarity = clarity_data.get(clarity_code, "Unknown Clarity")
    
    # Handle Carat calculation
    carat = "Unknown Carat"
    try:
        carat_val = int(carat_code)
        carat = str(carat_val) + " carats"
    except ValueError:
        pass

    cut = cut_data.get(cut_code, "Unknown Cut")

    # Print the decoded results
    print("\n--- Decoded Jewelry Details ---")
    print("Price: " + price)
    print("Metal: " + metal)
    print("Colour: " + colour)
    print("Stone: " + stone)
    print("Clarity: " + clarity)
    print("Carat: " + carat)
    print("Cut: " + cut)
    print("-------------------------------")

# Main program loop
while True:
    print("\nWelcome to the Jewelry Code Decoder!")
    print("Enter a 17-character code or 'quit' to exit.")
    print("Example: GHKL0407530006008")
    
    user_input = input("Enter the code: ").strip()

    if user_input.lower() == 'quit':
        print("Exiting the program.")
        break
    else:
        decode_jewelry_code(user_input)