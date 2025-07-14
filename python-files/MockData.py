import os

def adb_run(adb_cmd):
    try:
        os.system(adb_cmd)
    except Exception as e:
        print(f"Error executing command: {e}")

def send_signal_value(signal_name, signal_value):
    if not signal_name or not signal_value:
        print("Signal name and value cannot be empty.")
        return
    adb_cmd = f"adb shell am broadcast -a com.daimlertruck.source.MockDataSource --es Signal {signal_name} --ei Value {signal_value}"
    adb_run(adb_cmd)

if __name__ == "__main__":
    while True:
        signal_name = input("\nEnter the signal name (or type 'exit' to quit): ").strip()
        if signal_name.lower() == "exit":
            print("Exiting...")
            break
        signal_value = input("Enter signal value: ").strip()
        send_signal_value(signal_name, signal_value)