
import sys

def extract_pin(filename):
    with open(filename, "rb") as f:
        data = f.read()

    # أماكن شائعة قد يحتوي فيها الملف على كود PIN (EDC15C7)
    offsets = [0x1F0, 0x200, 0x2F0]

    for offset in offsets:
        chunk = data[offset:offset + 32].hex().upper()
        if "531488" in chunk:
            print("PIN Code Found: 1488")
            return

    print("PIN Code Not Found")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_pin.py <file.bin>")
    else:
        extract_pin(sys.argv[1])
