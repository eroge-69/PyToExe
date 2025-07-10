import psutil
from pypresence import Presence
import time

client_id = '1330114632534200351'  # Fake ID, put your real one here
RPC = Presence(client_id,pipe=0)  # Initialize the client class
RPC.connect() # Start the handshake loop


while True:  # The presence will stay on as long as the program is running
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    pagefile = psutil.swap_memory()
    RPC.update(
        details=f"Подкачка: {str(round(pagefile.used / 1024**2))} МБ | {str(round(pagefile.total / 1024**2))} МБ",
        state=f"RAM: {str(round(mem.used / 1024 ** 2))} МБ | {str(round(mem.total / 1024 ** 2))} МБ"
    )  # Set the presence
    time.sleep(15) # Can only update rich presence every 15 seconds