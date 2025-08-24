import time

def countdown(minutes, label):
    total_seconds = minutes * 60
    while total_seconds:
        mins, secs = divmod(total_seconds, 60)
        timer = f"{mins:02d}:{secs:02d}"
        print(f"{label} {timer}", end="\r")
        time.sleep(1)
        total_seconds -= 1
    print(f"{label} finished.            ")

def pomodoro():
    work_minutes = 25
    short_break = 5
    long_break = 15
    cycles = 4

    for cycle in range(1, cycles + 1):
        print(f"\nPomodoro {cycle}: Work for {work_minutes} minutes")
        countdown(work_minutes, "Work")

        if cycle < cycles:
            print("Short break")
            countdown(short_break, "Break")
        else:
            print("Long break")
            countdown(long_break, "Long Break")

if __name__ == "__main__":
    pomodoro()
