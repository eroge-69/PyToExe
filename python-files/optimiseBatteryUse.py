import psutil
import subprocess
import ctypes,sys
from win10toast import ToastNotifier
import os

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
        
    except:
        return False

if is_admin():
    battery = psutil.sensors_battery()
    if battery :
        plugged = battery.power_plugged
        if plugged:
            with open("./counter.txt","w") as file:
                file.write("0")
            ps_script = """
            $device = Get-WmiObject Win32_PnPEntity | Where-Object { $_.Caption -like "*Microsoft Surface ACPI-Compliant Control Method Battery*" }
            if ($device.status -eq "OK"){
                $device.Disable()
            }

        """
            subprocess.run(["powershell", "-Command", ps_script], check=True)

        else:
             battery_percent =  battery.percent
             if battery_percent < 20:
                   toast = ToastNotifier()
                   toast.show_toast(
                                 f"درصد باتری: %{battery_percent}",  
                             "شارژر را وصل کنید",  
                                  duration=10 
                                     )
                  
    else:
        if os.path.exists("./counter.txt"):
            with open ("./counter.txt","r+") as file:
                counter = int(file.readline().strip())
                if counter < 10 :
                    counter+=1
                    file.seek(0)
                    file.truncate(0)
                    file.write(str(counter))
                else:  
                    file.close()
                    os.remove("./counter.txt")
                    toast = ToastNotifier()
                    toast.show_toast(f"{"10"} دقیقه شارژ انجام شد",  duration=10 )



        else:
            ps_script = """
                $device = Get-WmiObject Win32_PnPEntity | Where-Object { $_.Caption -like "*Microsoft Surface ACPI-Compliant Control Method Battery*" }
                $device.Enable()

        """
            subprocess.run(["powershell", "-Command", ps_script], check=True)
            if psutil.sensors_battery().power_plugged and psutil.sensors_battery().percent >=90:
               ps_script = """
                  $device = Get-WmiObject Win32_PnPEntity | Where-Object { $_.Caption -like "*Microsoft Surface ACPI-Compliant Control Method Battery*" }
                  $device.Disable()
        """
               subprocess.run(["powershell", "-Command", ps_script], check=True)
               with open("./counter.txt","w") as file:
                 file.write("0")
            else:
                toast = ToastNotifier()
                toast.show_toast(f"درصد باتری {psutil.sensors_battery.percent}",  duration=10 )


else:
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, sys.argv[0], None, 1)
    


