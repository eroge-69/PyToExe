import usb.core
import usb.util
import time
import sys

# FL256LAIF01 Commands
CMD_READ = 0x03
CMD_WRITE_ENABLE = 0x06
CMD_WRITE_DISABLE = 0x04
CMD_PAGE_PROGRAM = 0x02
CMD_SECTOR_ERASE = 0xD8
CMD_CHIP_ERASE = 0xC7
CMD_READ_STATUS = 0x05
CMD_WRITE_STATUS = 0x01
CMD_READ_ID = 0x9F

# Teensy Vendor ID and Product ID
TEENSY_VID = 0x16C0
TEENSY_PID = 0x0486


class FL256LAIF01_Programmer:
    def __init__(self):
        self.dev = None
        self.interface = 0
        self.timeout = 5000

    def connect(self):
        """Connect to Teensy 2.0++"""
        self.dev = usb.core.find(idVendor=TEENSY_VID, idProduct=TEENSY_PID)

        if self.dev is None:
            raise ValueError("Teensy 2.0++ not found")

        # Detach kernel driver if active
        if self.dev.is_kernel_driver_active(self.interface):
            self.dev.detach_kernel_driver(self.interface)

        # Set configuration
        self.dev.set_configuration()

    def disconnect(self):
        """Disconnect from Teensy"""
        usb.util.dispose_resources(self.dev)

    def send_spi_command(self, command, address=None, data=None, read_length=0):
        """
        Send SPI command to Teensy and receive response
        """
        # Create command packet
        packet = bytearray()
        packet.append(command)

        if address is not None:
            packet.extend(address.to_bytes(3, 'big'))

        if data is not None:
            packet.extend(data)

        # Send command
        self.dev.write(0x01, packet, self.timeout)

        # Read response if needed
        if read_length > 0:
            return self.dev.read(0x81, read_length, self.timeout)
        return None

    def read_id(self):
        """Read JEDEC ID"""
        return self.send_spi_command(CMD_READ_ID, read_length=3)

    def read_status(self):
        """Read status register"""
        return self.send_spi_command(CMD_READ_STATUS, read_length=1)[0]

    def wait_ready(self, timeout=1000):
        """Wait until device is ready"""
        start = time.time()
        while (time.time() - start) < timeout:
            status = self.read_status()
            if not (status & 0x01):  # Check BUSY bit
                return True
            time.sleep(0.01)
        return False

    def write_enable(self):
        """Enable writes to flash"""
        self.send_spi_command(CMD_WRITE_ENABLE)

    def write_disable(self):
        """Disable writes to flash"""
        self.send_spi_command(CMD_WRITE_DISABLE)

    def read_data(self, address, length):
        """Read data from flash"""
        if not self.wait_ready():
            raise Exception("Device busy")

        return self.send_spi_command(CMD_READ, address=address, read_length=length)

    def write_page(self, address, data):
        """Write a page (256 bytes) to flash"""
        if len(data) > 256:
            raise ValueError("Page size exceeds 256 bytes")

        if not self.wait_ready():
            raise Exception("Device busy")

        self.write_enable()
        self.send_spi_command(CMD_PAGE_PROGRAM, address=address, data=data)

    def erase_sector(self, address):
        """Erase a 4KB sector"""
        if not self.wait_ready():
            raise Exception("Device busy")

        self.write_enable()
        self.send_spi_command(CMD_SECTOR_ERASE, address=address)

    def erase_chip(self):
        """Perform full chip erase"""
        if not self.wait_ready():
            raise Exception("Device busy")

        self.write_enable()
        self.send_spi_command(CMD_CHIP_ERASE)

    def dump_flash(self, filename, size=0x2000000):
        """Dump entire flash to file"""
        with open(filename, 'wb') as f:
            for addr in range(0, size, 256):
                data = self.read_data(addr, 256)
                f.write(data)
                print(f"\rReading: {addr / size * 100:.1f}%", end='')
                sys.stdout.flush()
        print("\nDump complete")

    def program_flash(self, filename, verify=True):
        """Program flash from file"""
        with open(filename, 'rb') as f:
            data = f.read()

        # Erase necessary sectors first
        sector_size = 4096
        for sector_start in range(0, len(data), sector_size):
            sector_end = min(sector_start + sector_size, len(data))
            sector_data = data[sector_start:sector_end]

            if any(byte != 0xFF for byte in sector_data):
                print(f"Erasing sector at 0x{sector_start:06X}")
                self.erase_sector(sector_start)

        # Program pages
        page_size = 256
        for addr in range(0, len(data), page_size):
            page_data = data[addr:addr + page_size]
            if len(page_data) < page_size:
                page_data += b'\xFF' * (page_size - len(page_data))

            print(f"\rProgramming: {addr / len(data) * 100:.1f}%", end='')
            sys.stdout.flush()

            self.write_page(addr, page_data)

            if verify:
                # Verify written data
                read_data = self.read_data(addr, len(page_data))
                if read_data != page_data:
                    print(f"\nVerify failed at address 0x{addr:06X}")
                    return False

        print("\nProgramming complete")
        return True


def main():
    print("FL256LAIF01 Programmer using Teensy 2.0++")

    try:
        prog = FL256LAIF01_Programmer()
        prog.connect()

        # Read ID to verify connection
        id_data = prog.read_id()
        print(f"JEDEC ID: {id_data.hex()}")

        # Menu
        while True:
            print("\nOptions:")
            print("1. Dump flash to file")
            print("2. Program flash from file")
            print("3. Erase chip")
            print("4. Exit")

            choice = input("Select option: ")

            if choice == '1':
                filename = input("Enter output filename: ")
                prog.dump_flash(filename)
            elif choice == '2':
                filename = input("Enter input filename: ")
                if prog.program_flash(filename):
                    print("Programming successful")
                else:
                    print("Programming failed")
            elif choice == '3':
                confirm = input("Are you sure you want to erase the entire chip? (y/n): ")
                if confirm.lower() == 'y':
                    print("Erasing chip...")
                    prog.erase_chip()
                    print("Erase complete")
            elif choice == '4':
                break
            else:
                print("Invalid option")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        prog.disconnect()
        print("Disconnected")


if __name__ == "__main__":
    main()