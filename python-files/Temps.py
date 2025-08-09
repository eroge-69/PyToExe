import wmi

MaxTempImp = input("Max Temp Until Alert: ")

if MaxTempImp.isdigit():
    MaxTemp = int(MaxTempImp)
    w = wmi.WMI(namespace="root\\wmi")
    try:
        thermal_zones = w.MSAcpi_ThermalZoneTemperature()

        for zone in thermal_zones:
            temp_celsius = (zone.CurrentTemperature / 10.0) - 273.15
            print(f"CPU Temperature: {temp_celsius:.2f}°C")
            if temp_celsius >= MaxTemp:
                print(f"Warning: Temperature exceeds {MaxTemp}°C!")

    except wmi.WMIError as e:
        print(f"Error accessing thermal zone temperature: {e}")
        print("This method may not provide detailed or GPU temperature information.")
else:
    exitimp = input("Press Enter To Exit. Returned Value Was Not A Number.")
    if exitimp:
        exit()
