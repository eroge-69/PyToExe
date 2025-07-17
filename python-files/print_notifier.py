import win32print
import time
from playsound import playsound

printer_name = win32print.GetDefaultPrinter()

def get_print_jobs():
    jobs = []
    hPrinter = win32print.OpenPrinter(printer_name)
    try:
        info = win32print.EnumJobs(hPrinter, 0, 999, 1)
        for job in info:
            jobs.append(job['JobId'])
    finally:
        win32print.ClosePrinter(hPrinter)
    return jobs

existing_jobs = get_print_jobs()
print("🖨️ Print monitor running...")

while True:
    time.sleep(1)
    new_jobs = get_print_jobs()

    if len(new_jobs) > len(existing_jobs):
        print("Printing started.")
        playsound("printing_started.wav")
        existing_jobs = new_jobs

    elif len(new_jobs) < len(existing_jobs):
        print("Printing complete.")
        playsound("printing_complete.wav")
        existing_jobs = new_jobs
