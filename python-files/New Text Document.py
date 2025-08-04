#!/usr/bin/env python

import sys
import json
import struct

# Helper function to read a message from stdin
def get_message():
    raw_length = sys.stdin.buffer.read(4)
    if not raw_length:
        return {}
    length = struct.unpack('@I', raw_length)[0]
    message = sys.stdin.buffer.read(length).decode('utf-8')
    return json.loads(message)

# Helper function to send a message to stdout
def send_message(message):
    encoded_message = json.dumps(message).encode('utf-8')
    sys.stdout.buffer.write(struct.pack('@I', len(encoded_message)))
    sys.stdout.buffer.write(encoded_message)
    sys.stdout.buffer.flush()

if __name__ == '__main__':
    while True:
        # Read the message from the extension
        message = get_message()
        if 'text' in message:
            # Process the message
            response_text = f"Hello from Python! You said: '{message['text']}'"
            response = {"response": response_text}
            # Send the response back to the extension
            send_message(response)
        else:
            # If the message is empty, stop the loop
            break