import os, subprocess, sys, json

def read_message():
    raw_length = sys.stdin.buffer.read(4)
    if len(raw_length) == 0:
        sys.exit(0)
    message_length = int.from_bytes(raw_length, byteorder="little")
    message = sys.stdin.buffer.read(message_length).decode("utf-8")
    return message

def send_message(message):
    encoded = json.dumps(message).encode("utf-8")
    sys.stdout.buffer.write(len(encoded).to_bytes(4, byteorder="little"))
    sys.stdout.buffer.write(encoded)
    sys.stdout.flush()

if __name__ == "__main__":
    while True:
        msg = read_message()
        if msg == "run":
            subprocess.Popen([r"C:\Users\mustakim\Desktop\Downloader\Now\test.bat"], shell=True)
            send_message({"status": "bat started"})
