import random
import time
import os

chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890@#$%^&*()"
num_lines = 10
positions = [random.randint(0, 70) for _ in range(num_lines)]

start_time = time.time()
duration = 10  # тривалість роботи у секундах

try:
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')

        for i in range(num_lines):
            line = [" "] * 80
            line[positions[i]] = random.choice(chars)
            print("".join(line))

        positions = [(pos + random.choice([-1, 0, 1])) % 80 for pos in positions]

        time.sleep(0.1)

        # Перевірка часу для завершення
        if time.time() - start_time > duration:
            break

except KeyboardInterrupt:
    print("\nЕфект завершено")

print("Програма завершила роботу після 10 секунд.")
