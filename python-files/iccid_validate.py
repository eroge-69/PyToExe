import re

def luhn_checksum(iccid):
    """Calculate Luhn checksum for ICCID and return True if valid."""
    digits = [int(d) for d in iccid if d.isdigit()]
    if not digits:
        return False
    # Double every second digit from right to left
    for i in range(len(digits) - 2, -1, -2):
        doubled = digits[i] * 2
        digits[i] = (doubled // 10) + (doubled % 10) if doubled > 9 else doubled
    # Sum all digits
    total = sum(digits)
    return total % 10 == 0

def validate_iccid(iccid):
    """Validate ICCID based on length, prefix, and Luhn checksum."""
    # Remove any whitespace or non-digit characters
    iccid = iccid.strip()
    # Check if ICCID is numeric and has 19 or 20 digits
    if not re.match(r'^\d{19,20}$', iccid):
        return False, "Invalid length or contains non-digits"
    # Check if it starts with '89'
    if not iccid.startswith('89'):
        return False, "Does not start with '89'"
    # Validate Luhn checksum
    if not luhn_checksum(iccid):
        return False, "Invalid Luhn checksum"
    return True, "Valid ICCID"

def process_iccid_file(input_file, output_file):
    """Read ICCIDs from input file, validate, and write results to output file."""
    results = []
    try:
        with open(input_file, 'r') as infile:
            iccids = infile.readlines()
        
        for iccid in iccids:
            iccid = iccid.strip()
            if iccid:  # Skip empty lines
                is_valid, message = validate_iccid(iccid)
                result = f"ICCID: {iccid} - {message}"
                results.append(result)
                print(result)
        
        # Write results to output file
        with open(output_file, 'w') as outfile:
            for result in results:
                outfile.write(result + '\n')
                
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
    except Exception as e:
        print(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    input_file = "iccids.txt"
    output_file = "iccid_validation_results.txt"
    process_iccid_file(input_file, output_file)