import serial
import time

def download_grbl_config(com_port, baud_rate, output_file):
    """
    Downloads GRBL configuration settings and saves them to a file.

    Args:
        com_port (str): The COM port of your GRBL controller (e.g., 'COM3').
        baud_rate (int): The baud rate for the serial connection (typically 115200 for GRBL).
        output_file (str): The path to the file where the configuration will be saved.
    """
    try:
        # Open serial port
        s = serial.Serial(com_port, baud_rate, timeout=1)  # timeout of 1 second for reads

        # Wake up GRBL (optional, but good practice)
        s.write(b'\r\n\r\n')
        time.sleep(2)  # Wait for GRBL to initialize
        s.flushInput()  # Flush startup text

        # Request GRBL settings
        s.write(b'$$\r\n')  # Send the $$ command to request settings

        # Read the response and save it to the output file
        with open(output_file, 'w') as f:
            while True:
                line = s.readline().decode('utf-8').strip()
                if not line:
                    break  # Exit loop when no more lines are received
                f.write(line + '\n')

        print(f"GRBL configuration saved to {output_file}")

    except serial.SerialException as e:
        print(f"Error communicating with GRBL controller: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 's' in locals() and s.isOpen():
            s.close()
            print("Serial port closed.")

if __name__ == "__main__":
    # --- Configuration ---
    GRBL_COM_PORT = 'COM5'  # Change this to your actual COM port
    GRBL_BAUD_RATE = 115200  # Default GRBL baud rate
    OUTPUT_CONFIG_FILE = 'grbl_config.txt'  # Name of the output file

    # --- Download and save ---
    download_grbl_config(GRBL_COM_PORT, GRBL_BAUD_RATE, OUTPUT_CONFIG_FILE)
