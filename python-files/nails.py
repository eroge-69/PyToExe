#!/usr/bin/python3
"""NXT-Python tutorial: find the brick."""
import time

import nxt.locator
import nxt.motor
import nxt.sensor
import nxt.sensor.generic

# Find a brick.
with nxt.locator.find() as b:
    # Once found, print its name.
    print("Found brick:", b.get_device_info()[0])
    # And play a recognizable note.
    b.play_tone(440, 250)

    mybutton = b.get_sensor(nxt.sensor.Port.S1, nxt.sensor.generic.Touch)
    mymotor = b.get_motor(nxt.motor.Port.A)

    response = mybutton.get_sample()

    while not response:
        mymotor.run(100)
        response = mybutton.get_sample()
        print(response)
        time.sleep(0.5)

    mymotor.idle()
