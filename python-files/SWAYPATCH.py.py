import struct

# Offset from the start of player index to the byte we want to change
BYTE_OFFSET = 37  # Adjust if needed for skin/tattoo byte

def change_skin_byte_by_id(input_file, output_file, player_id, new_value):
    # Convert decimal player ID to 4-byte little-endian bytes
    player_bytes_le = struct.pack("<I", player_id)
    player_bytes_be = struct.pack(">I", player_id)

    with open(input_file, "rb") as f:
        data = bytearray(f.read())

    # Find player index in the file
    pos = data.find(player_bytes_le)
    if pos == -1:
        pos = data.find(player_bytes_be)
    if pos == -1:
        print(f"Player {player_id} not found!")
        return

    old_value = data[pos + BYTE_OFFSET]
    data[pos + BYTE_OFFSET] = new_value
    print(f"Player {player_id}: byte at offset {pos + BYTE_OFFSET} changed from {hex(old_value)} to {hex(new_value)}")

    # Save changes to a new file
    with open(output_file, "wb") as f:
        f.write(data)
    print(f"Changes saved to {output_file}")

if __name__ == "__main__":
    input_file = "PlayerAppearance.bin"
    output_file = "PlayerAppearance_changed.bin"

    # Example: change player 40352 skin/tattoo byte to 0x01
    change_skin_byte_by_id(input_file, output_file, 40352, 0x01)
