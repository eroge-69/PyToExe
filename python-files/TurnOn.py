import asyncio
from bleak import BleakScanner, BleakClient

DEVICE_NAME = "GBK_H6125_246E"

strip_device = None
strip_client = None

CHARACTERISTIC_UUID = "00010203-0405-0607-0809-0a0b0c0d2b11"

# TurnOn
CMD_TURN_ON = bytes.fromhex("3301010000000000000000000000000000000033")



async def Scan_and_Connect():
    global strip_device, strip_client

    devices = await BleakScanner.discover(5.0, return_adv=True)
    for d in devices:
        if (devices[d][1].local_name == DEVICE_NAME):
            print("Found it")
            strip_device = d

    print(f"Verbinde zu {strip_device}...")
    strip_client = BleakClient(strip_device)
    await strip_client.connect()

async def TurnOn():
    global strip_device, strip_client

    print("Sende TurnOn-Befehl...")
    await strip_client.write_gatt_char(CHARACTERISTIC_UUID, CMD_TURN_ON)


asyncio.run(Scan_and_Connect())
asyncio.run(TurnOn())