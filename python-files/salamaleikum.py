import os

def shutdown():
    print("Il computer si spegnerà ora...")
    os.system("shutdown /s /t 0")

if __name__ == "__main__":
    shutdown()
