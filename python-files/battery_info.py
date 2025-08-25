import psutil
import platform
import datetime

def battery_info():
    print("==============================================")
    print("       Battery Information Software")
    print("   Developed by: Muhammad Mushtaq")
    print("   Contact: +92 321 7468559")
    print("==============================================\n")

    # سسٹم کی بنیادی معلومات
    print("System Information:")
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"Machine: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    print(f"Python Version: {platform.python_version()}")
    print("----------------------------------------------")

    battery = psutil.sensors_battery()
    if battery is None:
        print("⚠️  Battery information not available. (Maybe Desktop PC?)")
        return

    # بیٹری کی بنیادی معلومات
    print("Battery Status:")
    print(f"Percentage: {battery.percent}%")
    print(f"Power Plugged: {'Yes (Charging)' if battery.power_plugged else 'No (On Battery)'}")

    if battery.secsleft != psutil.POWER_TIME_UNLIMITED:
        if battery.secsleft == psutil.POWER_TIME_UNKNOWN:
            print("Time Left: Unknown")
        else:
            print("Time Left: " + str(datetime.timedelta(seconds=battery.secsleft)))

    print("----------------------------------------------")

    # ⚡ اضافی تفصیلات (WMI کے ذریعے)
    try:
        import wmi
        c = wmi.WMI()
        for b in c.Win32_Battery():
            print("Additional Battery Information:")
            print(f"Name: {b.Name}")
            print(f"Device ID: {b.DeviceID}")
            print(f"Chemistry: {b.Chemistry}")
            print(f"Design Voltage: {b.DesignVoltage} mV")
            print(f"Estimated Charge Remaining: {b.EstimatedChargeRemaining}%")
            print(f"Battery Status: {b.BatteryStatus}")
            print(f"Expected Life: {b.ExpectedLife}")
            print(f"Full Charge Capacity: {getattr(b, 'FullChargeCapacity', 'N/A')} mWh")
            print(f"Design Capacity: {getattr(b, 'DesignCapacity', 'N/A')} mWh")
            print(f"Cycle Count: {getattr(b, 'CycleCount', 'N/A')}")
            print("----------------------------------------------")
    except Exception as e:
        print("⚠️  Advanced battery details require 'wmi' package.")
        print("----------------------------------------------")

if __name__ == "__main__":
    battery_info()
    input("\nPress Enter to Exit...")