from pypresence import Presence
import time


client_id = "1381923578156417146"  
RPC = Presence(client_id)
RPC.connect()

RPC.update(
    # state= "hehe",
    # details="hehe",
    large_image="anime_icon",  
    small_image="episode_icon",  
)


while True:
    time.sleep(15)  