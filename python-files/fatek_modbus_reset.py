
from pymodbus.client import ModbusSerialClient as ModbusClient

def main():
    # === USER SETTINGS ===
    COM_PORT = 'COM1'        # Change this to your COM port, like COM3, COM4, etc.
    BAUD_RATE = 9600         # Fatek default
    SLAVE_ID = 1             # Default Modbus slave ID
    REGISTER = 4050          # R4050 - triggers factory reset
    VALUE = 1                # Write value to reset

    # Initialize Modbus RTU client
    client = ModbusClient(
        method='rtu',
        port=COM_PORT,
        baudrate=BAUD_RATE,
        stopbits=1,
        bytesize=8,
        parity='N',
        timeout=2
    )

    if client.connect():
        print(f"Connected to {COM_PORT}. Sending reset command to R4050...")
        result = client.write_register(address=REGISTER - 1, value=VALUE, unit=SLAVE_ID)
        if not result.isError():
            print("✅ Reset command sent successfully! Now power cycle your PLC.")
        else:
            print("❌ Failed to send command:", result)
        client.close()
    else:
        print(f"❌ Could not connect to {COM_PORT}. Check cable and port settings.")

if __name__ == "__main__":
    main()
