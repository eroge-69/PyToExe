
import asyncio
from bleak import BleakScanner, BleakClient

BATTERY_UUID = "00002a19-0000-1000-8000-00805f9b34fb"
RONIN_NAME_PREFIX = "Ronin"

async def find_ronin(timeout=10):
    devices = await BleakScanner.discover(timeout=timeout)
    for d in devices:
        if d.name and d.name.startswith(RONIN_NAME_PREFIX):
            return d
    return None

async def read_battery(addr):
    async with BleakClient(addr) as client:
        if BATTERY_UUID in await client.get_services():
            data = await client.read_gatt_char(BATTERY_UUID)
            return int(data[0])
        else:
            raise RuntimeError("Battery service not found")

async def main():
    print("🔍 Scanning for EvoFox Ronin...")
    dev = await find_ronin()
    if not dev:
        print("❌ EvoFox Ronin not found. Make sure it's in Bluetooth mode and discoverable.")
        return
    print(f"✅ Found Ronin: {dev.name} [{dev.address}]")
    try:
        pct = await read_battery(dev.address)
        print(f"🔋 Battery level: {pct}%")
    except Exception as e:
        print("⚠️  Could not read battery service:", e)

if __name__ == "__main__":
    asyncio.run(main())
