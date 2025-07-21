from bluelights import BJLEDInstance
import asyncio

ADDRESS = "be:30:6a:00:4b:64"
UUID = "0000ee01-0000-1000-8000-00805f9b34fb"

async def main():
    led = BJLEDInstance(address=ADDRESS, uuid=UUID)
    try:
        await led.turn_on()
    except:
        pass
    finally:
        await led._disconnect()

asyncio.run(main())
