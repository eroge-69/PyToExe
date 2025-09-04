from pypresence import Presence
import time

CLIENT_ID = "1412867850846208111"
rpc = Presence(CLIENT_ID)
rpc.connect()

start_time = int(time.time())  # timestamp inizio

rpc.update(
    state="Idling...",
    details="Welcome To Vice City!",
    start=start_time,            # solo start, niente end
    large_image="gta_vi_logo",
    large_text="Grand Theft Auto VI",
    small_image="rogue",
    small_text="Rogue - Level 100",
)

print("Rich Presence aggiornato!")

while True:
    time.sleep(15)

