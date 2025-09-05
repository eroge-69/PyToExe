import sys

# Define TSUMO_Game structure
class TSUMO_Game:
    def __init__(self, title, game_id):
        self.game_title = title
        self.game_id = game_id

# TSUMO Game definitions
TSUMO_Games = [
    TSUMO_Game('Air Raid', 0x6B28D609),
    TSUMO_Game('AirStrike', 0x51694A6E),
    TSUMO_Game('BeachHead 2000 SE', 0xD53BB2C7),
    TSUMO_Game('Crimson Skies', 0xBA49994D),
    TSUMO_Game('ExZeus', 0xBB053D9F),
    TSUMO_Game('Mechwarrior 4', 0x85BFA92E),
    TSUMO_Game('Starfighter', 0xE18F8DE1),
    TSUMO_Game('Motion Adventures', 0xAA83E155),
    # ReVolt is a dedicated machine, this cannot be installed on TSuMo multi 
    # game machine. Included here as the licensing mechanism is the same.
    TSUMO_Game('ReVolt', 0x6816AA99)
]

# Function to generate tsumo game key
def generate_tsumo_game_key(license_id, game_id):
    original_license = int(license_id, 16)
    game_identifier = game_id

    shifted_value = (original_license >> 28) & 0x0F
    result_value = (original_license >> (32 - shifted_value)) & 0xFFFF
    result_value |= (original_license << shifted_value)
    result_value ^= game_identifier

    return format(result_value & 0xFFFFFFFF, '08X')

if __name__ == "__main__":
    # Check for command line argument
    if len(sys.argv) != 2:
        print("TSuMo License Generator v1.1 (2024-03-04)")
        print("Usage: python tsumo_license_gen.py <license_id>")
        sys.exit(1)

    # Get license_id from command line argument and validate
    license_id = sys.argv[1]
    if len(license_id) != 8 or not all(c in '0123456789ABCDEFabcdef' for c in license_id):
        print("Error: Invalid license_id. It should be an 8-character hex value.")
        sys.exit(1)

    print(f"Machine License ID: {license_id}")
    print("-----------------------------")
    # Iterate through defined games and print results
    for entry in TSUMO_Games:
        result = generate_tsumo_game_key(license_id, entry.game_id)
        print(f"{entry.game_title}: {result}")
    print("-----------------------------")
