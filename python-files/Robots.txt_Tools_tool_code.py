import random
import string

LICENSE_KEY = "GVWT-V223-NZ0V-RTT-6295"

def generate_license_number():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def generate_code(length=128):
    sections = []
    for _ in range(8):
        segment = ''.join(random.choices(string.ascii_letters + string.digits + '!@#$%^&*()-_=+', k=length // 8))
        sections.append(segment)
    return '-'.join(sections)

def generate_multiple_codes(num_codes=10, length=128):
    codes = []
    for _ in range(num_codes):
        license_number = generate_license_number()
        code = generate_code(length)
        codes.append(f"License: {license_number} | Code: {code}")
    return codes

def save_codes_to_file(codes, filename):
    with open(filename, "w") as file:
        file.write(f"Product: Robots.txt Tools\n")
        file.write(f"License Key: {LICENSE_KEY}\n\n")
        for code in codes:
            file.write(code + "\n")

if __name__ == "__main__":
    product_name = "Robots.txt Tools"
    filename = product_name.replace(" ", "_") + "_codes.txt"
    codes = generate_multiple_codes(10, 128)
    save_codes_to_file(codes, filename)
