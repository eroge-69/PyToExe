import serial
import time

# =============================
# Configuration
# =============================
COM_PORT = "COM3"      # Change to your COM port
BAUD_RATE = 9600       # Check your scale’s manual
CSV_FILE = "weight.csv"
REFRESH_DELAY = 1      # seconds between reads
# =============================

def save_weight_to_csv(weight):
    """Overwrite CSV with only the latest weight in 'weight,<value>' format."""
    with open(CSV_FILE, "w") as f:
        f.write(f"weight,{weight}\n")

def main():
    try:
        ser = serial.Serial(
            port=COM_PORT,
            baudrate=BAUD_RATE,
            timeout=1
        )
        print(f"Connected to {COM_PORT} at {BAUD_RATE} baud.")
        print(f"Writing latest weight to {CSV_FILE}... (CTRL+C to stop)")

        while True:
            line = ser.readline().decode(errors="ignore").strip()
            if line:
                # Optionally add "kg" if your scale output is just a number
                if not any(c.isalpha() for c in line):
                    line += "kg"
                print("Weight:", line)
                save_weight_to_csv(line)
            time.sleep(REFRESH_DELAY)

    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except KeyboardInterrupt:
        print("\nStopped by user.")

if __name__ == "__main__":
    main()
