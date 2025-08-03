import keyboard as k
import time as t

a = ['0','1','2','3','4','5','6','7','8','9']
b = lambda: [k.press_and_release('w') or t.sleep(0.1) for _ in range(3)]

for c in a:
    k.on_press_key(c, lambda e: b())

print("Macro ativa. Pressione ESC para sair.")
k.wait('esc')
