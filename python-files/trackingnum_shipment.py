

# shipment_tracker.py

CHARSET = "34789BCDFGHJKLMNPQRSTVWXYZ"  # length == 26

def encode_number(num: int, length: int = 6) -> str:
    """Encode integer num into a fixed-length base-26 string using CHARSET."""
    encoded_chars = []
    for power in reversed(range(length)):
        div = 26 ** power
        index = (num // div) % 26
        encoded_chars.append(CHARSET[index])
    return "".join(encoded_chars)


def get_shipment_number(tracking_number: str) -> str:
    """
    Convert an 18-char tracking number to a shipment number.
    """
    if len(tracking_number) != 18:
        raise ValueError("Tracking number must be exactly 18 characters.")

    # Prefix: characters 3..8 (1-based) -> indices 2..7
    prefix = tracking_number[2:8]

    # Numeric substring: characters 11..17 (1-based) -> indices 10..16
    num_str = tracking_number[10:17]
    num = int(num_str)

    suffix = encode_number(num, length=6)
    return prefix + suffix


def main():
    print("=== Shipment Number Generator ===")
    tracking_number = input("Enter 18-character tracking number: ").strip()

    try:
        shipment = get_shipment_number(tracking_number)
        print(f"Shipment number: {shipment}")
    except ValueError as e:
        print(f"Input error: {e}")


if __name__ == "__main__":
    main()
