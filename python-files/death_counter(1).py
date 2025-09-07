import asyncio
import platform

# Віртуальний файл у пам'яті (симуляція текстового файлу)
death_count = 0

def save_death_count():
    global death_count
    # У браузері (Pyodide) зберігаємо в локальному сховищі
    if platform.system() == "Emscripten":
        try:
            import js
            js.localStorage.setItem('death_count', str(death_count))
        except:
            pass  # Якщо не вдалося, просто ігноруємо
    else:
        with open('death_count.txt', 'w') as f:
            f.write(str(death_count))

def load_death_count():
    global death_count
    if platform.system() == "Emscripten":
        try:
            import js
            stored = js.localStorage.getItem('death_count')
            death_count = int(stored) if stored else 0
        except:
            death_count = 0
    else:
        try:
            with open('death_count.txt', 'r') as f:
                death_count = int(f.read())
        except FileNotFoundError:
            death_count = 0

def simulate_f6_press():
    global death_count
    death_count += 1
    save_death_count()
    print(f"Смерть! Лічильник: {death_count}")
    print("Щоб симулювати натискання F6, просто запустіть цю функцію ще раз.")

async def main():
    load_death_count()
    print(f"Початковий лічильник смертей: {death_count}")
    print("Програма запущена. Оскільки це браузерне середовище, натискання клавіш не працює.")
    print("Для збільшення лічильника викличте: simulate_f6_press()")
    print("Наприклад, у консолі: simulate_f6_press()")

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())