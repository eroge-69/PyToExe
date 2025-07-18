import phonenumbers
from phonenumbers import PhoneNumberFormat, NumberParseException

DEFAULT_REGIONS = ['GB', 'US', 'FR', 'DE', 'IN', 'AU', 'CA', 'ZA']

def get_common_formats(parsed_number, original_input):
    cc = parsed_number.country_code
    nn = str(parsed_number.national_number)
    formatted = set()

    # Include original input
    formatted.add(original_input)

    # Standard phonenumbers formats
    formatted.add(phonenumbers.format_number(parsed_number, PhoneNumberFormat.E164))
    formatted.add(phonenumbers.format_number(parsed_number, PhoneNumberFormat.INTERNATIONAL))
    formatted.add(phonenumbers.format_number(parsed_number, PhoneNumberFormat.NATIONAL))

    # Manual realistic formats
    local = '0' + nn if not nn.startswith('0') else nn

    formatted.update([
        f"+{cc} {nn[:4]} {nn[4:]}",
        f"+{cc}-{nn[:4]}-{nn[4:]}",
        f"(+{cc}) {nn[:4]} {nn[4:]}",
        f"(+{cc}){nn}",                    # e.g. (+44)1795229077
        f"00{cc} {nn[:4]} {nn[4:]}",
        f"00{cc}{nn}",                     # 00441795229077
        f"{local[:5]} {local[5:]}",
        f"{local[:5]}-{local[5:]}",
        f"({local[:5]}) {local[5:]}"
    ])

    return sorted(formatted)


def process_input_file(input_file, output_file):
    with open(input_file, 'r') as f:
        numbers = [line.strip() for line in f if line.strip()]

    with open(output_file, 'w', encoding='utf-8') as f:
        for number in numbers:
            parsed = None
            cleaned = ''.join(filter(lambda x: x.isdigit() or x == '+', number))

            for region in DEFAULT_REGIONS:
                try:
                    parsed = phonenumbers.parse(cleaned, region)
                    if phonenumbers.is_valid_number(parsed):
                        break
                except NumberParseException:
                    continue

            if parsed:
                variations = get_common_formats(parsed, number)
            else:
                variations = [number]  # fallback: just the input number

            for var in sorted(variations):
                f.write(var + '\n')

            f.write('\n')  # Add a blank line between each group


# === MAIN USAGE ===
if __name__ == "__main__":
    process_input_file("input_numbers.txt", "output_variations.txt")
