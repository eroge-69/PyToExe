import ctypes

def main():
    ctypes.windll.user32.MessageBoxW(0, "Hello World!", "Test", 1)

if __name__ == "__main__":
    main()
