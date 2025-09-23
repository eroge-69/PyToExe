import time
import sys

def main():
    try:
        while True:
            time.sleep(3600)  # Спит 1 час
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
