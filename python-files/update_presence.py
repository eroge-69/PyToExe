from pypresence import Presence
import time

DISCORD_CLIENT_ID = "1396933197882982490"
RPC = Presence(DISCORD_CLIENT_ID)
RPC.connect()

def get_status():
    try:
        with open("status.txt", "r") as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1].strip()
                return last_line
    except Exception:
        return "No status"
    return "No status"

while True:
    status = get_status()
    RPC.update(
        details="Black Ops III - zm_ww2",
        state=status,
        large_image="bo3",
        start=time.time()
    )
    time.sleep(10)