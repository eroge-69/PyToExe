import keyboard
import asyncio
import platform

# Віртуальний файл у пам'яті
death_count = 0

def save_death_count():
    global death_count
    with open('death_count.txt', 'w') as f:
        f.write(str(death_count))

def load_death_count():
    global death_count
    try:
        with open('death_count.txt', 'r') as f:
            death_count = int(f.read())
    except FileNotFoundError:
        death_count = 0

def on_f6_press():
    global death_count
    death_count += 1
    save_death_count()
    print(f"Death count: {death_count}")

async def main():
    load_death_count()
    print(f"Initial death count: {death_count}")
    keyboard.on_press_key("f6", lambda _: on_f6_press())
    while True:
        await asyncio.sleep(1)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())