import ntplib
import time
from datetime import datetime, timezone
import sys
import platform

if platform.system() == 'Windows':
    import win32api

def get_ntp_time(ntp_server='pool.ntp.org'):
    client = ntplib.NTPClient()
    response = client.request(ntp_server, version=3)
    return datetime.fromtimestamp(response.tx_time, timezone.utc)

def get_local_time():
    return datetime.now(timezone.utc)

def set_system_time(dt):
    if platform.system() == 'Windows':
        d = dt
        win32api.SetSystemTime(
            d.year, d.month, d.isoweekday(), d.day, d.hour,
            d.minute, d.second, int(d.microsecond / 1000)
        )
    else:
        import subprocess
        timestr = dt.strftime('%m%d%H%M%Y.%S')
        subprocess.call(['sudo', 'date', timestr])

def main():
    threshold_sec = 2
    while True:
        try:
            ntp_time = get_ntp_time()
            local_time = get_local_time()
        except Exception as e:
            print("Error fetching NTP or local time:", e)
            sys.exit(1)

        diff = abs((ntp_time - local_time).total_seconds())
        print(f"NTP time:    {ntp_time.isoformat()}")
        print(f"Local time:  {local_time.isoformat()}")
        print(f"Difference:  {diff:.3f} seconds")

        if diff > threshold_sec:
            print("Adjusting system time...")
            set_system_time(ntp_time)
            print("System time adjusted.")
        else:
            print("System time is already synchronized.")
        print("Waiting 10 minutes before next check...\n")
        time.sleep(600)  # 600 seconds = 10 minutes

if __name__ == "__main__":
    main()
