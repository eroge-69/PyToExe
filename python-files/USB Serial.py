import subprocess

def get_usb_serial_numbers():
    try:
        # Get all disk drives with their interface type and serial number
        result = subprocess.run(
            ['wmic', 'diskdrive', 'get', 'Caption,InterfaceType,SerialNumber'],
            capture_output=True,
            text=True
        )
        lines = result.stdout.strip().split('\n')
        headers = lines[0].split()
        usb_serials = []

        for line in lines[1:]:
            if 'USB' in line:
                parts = line.split()
                # Serial number is usually the last item
                serial = parts[-1]
                usb_serials.append(serial)

        return usb_serials if usb_serials else ["No USB drives detected."]
    except Exception as e:
        return [f"Error: {e}"]

# Example usage
if __name__ == "__main__":
    serial_numbers = get_usb_serial_numbers()
    print("USB Drive Serial Numbers:")
    for sn in serial_numbers:
        print(f" - {sn}")