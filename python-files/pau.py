import re
from datetime import datetime, timedelta

log_file = "logs/latest.log"  # Path to your server log file
time_limit = datetime.now() - timedelta(hours=24)

player_name = input("Enter player name: ").strip()

with open(log_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

pattern = re.compile(r"\[(\d{2}:\d{2}:\d{2})\].*?: (.*?) issued server command: (.*)")

print(f"\nCommands used by {player_name} in the last 24 hours:\n")

for line in lines:
    match = pattern.search(line)
    if match:
        time_str, player, command = match.groups()
        if player.lower() == player_name.lower():
            # Build datetime for today
            log_time = datetime.strptime(time_str, "%H:%M:%S")
            log_time = log_time.replace(year=datetime.now().year,
                                        month=datetime.now().month,
                                        day=datetime.now().day)
            if log_time >= time_limit:
                print(f"[{log_time}] {player} → {command}")
