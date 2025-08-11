import requests
import curses
import time
from datetime import datetime

CHECK_URL = "https://www.google.com"
CHECK_INTERVAL = 2 
def check_internet():
    try:
        requests.get(CHECK_URL, timeout=3)
        return True
    except requests.RequestException:
        return False

def main(stdscr):
    curses.curs_set(0) 
    stdscr.nodelay(True) 
    total_requests = 0
    failed_requests = 0
    downtime_log = []
    while True:
        total_requests += 1
        online = check_internet()

        if not online:
            failed_requests += 1
            downtime_log.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        stdscr.clear()

        stdscr.addstr(0, 0, f"Internet Status Monitor".center(80), curses.A_BOLD)
        stdscr.addstr(2, 0, f"Total Requests: {total_requests}")
        stdscr.addstr(3, 0, f"Failed Requests: {failed_requests}")
        stdscr.addstr(4, 0, f"Last Checked: {datetime.now().strftime('%H:%M:%S')}")
        stdscr.addstr(5, 0, f"Current Status: {'ONLINE' if online else 'OFFLINE'}", 
                        curses.color_pair(2) if online else curses.color_pair(1))
        stdscr.addstr(7, 0, "Downtime Log:")
        for idx, timestamp in enumerate(downtime_log[-10:], start=8):  
            stdscr.addstr(idx, 2, timestamp)
        stdscr.refresh()
        time.sleep(CHECK_INTERVAL)
        try:
            key = stdscr.getch()
            if key == ord('q'):
                break
        except:
            pass

if __name__ == "__main__":
    curses.wrapper(main)
