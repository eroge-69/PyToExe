import time

import pynput

from pynput import mouse

def on_click(x, y, button, pressed):
    if button == mouse.Button.left:

        import time
        start = time.time()
        finish = start + 8
        while time.time() < finish:
            pass


        from winotify import Notification, audio

        toast = Notification(app_id="by Markus Zißler",
                             title="BMW AOS",
                             msg="Es sind neue Dateien für AOS installiert worden!",
                             duration="long",
                             icon=r"C:\Users\Teile\Downloads\_ISTAOSS\python_logo\BMW_ISTA_Next.png")

        toast.set_audio(audio.LoopingCall8, loop=True)

        toast.show()

        print('{} at {}'.format('Pressed Left Click' if pressed else 'Released Left Click', (x, y)))
        return False # Returning False if you need to stop the program when Left clicked.
    else:
        print('{} at {}'.format('Pressed Right Click' if pressed else 'Released Right Click', (x, y)))

listener = mouse.Listener(on_click=on_click)
listener.start()
listener.join()





