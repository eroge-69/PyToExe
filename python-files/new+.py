import asyncio
import pydivert

TCP_WINDOW_SIZE = 65535
TARGET_PORT = 25565
NEW_DEFAULT_TTL = 32

def packet_handler(packet):
    try:
        packet.tcp.window_size = TCP_WINDOW_SIZE
        print(f"[+] Modified TCP Window: {TCP_WINDOW_SIZE}")

        if hasattr(packet, 'ip'):
            packet.ip.ttl = NEW_DEFAULT_TTL
            packet.ip.df = True
            print(f"[+] Modified TTL: {NEW_DEFAULT_TTL}")

    except pydivert.PyDivertError as e:
        print(f"[!] Error in packet_handler: {e}")

async def process_packets(w, batch_size=3):
    try:
        while True:
            packets = [await asyncio.to_thread(w.recv) for _ in range(batch_size)]
            for packet in packets:
                packet_handler(packet)
            for packet in packets:
                await asyncio.to_thread(w.send, packet)
            await asyncio.sleep(0.001)  # Небольшая задержка

    except pydivert.PyDivertError as e:
        print(f"[!] Error in process_packets: {e}")

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        with pydivert.WinDivert(f"tcp and tcp.DstPort == {TARGET_PORT}") as w:
            print(f"[*] Listening for TCP packets on port {TARGET_PORT}...")
            loop.run_until_complete(process_packets(w))
            
    except KeyboardInterrupt:
        print("\n[!] Exiting...")
    finally:
        loop.close()

if __name__ == "__main__":
    main()
