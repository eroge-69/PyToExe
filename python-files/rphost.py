import time
import os
import sys

def main():
    # Бесконечный цикл с минимальной нагрузкой
    try:
        while True:
            time.sleep(3600)  # Спит 1 час
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()
