import base64

def encode_message(message: str) -> str:
    """Encode a message into base64 code."""
    message_bytes = message.encode("utf-8")
    base64_bytes = base64.b64encode(message_bytes)
    return base64_bytes.decode("utf-8")

def decode_message(code: str) -> str:
    """Decode a base64 code back into the original message."""
    base64_bytes = code.encode("utf-8")
    message_bytes = base64.b64decode(base64_bytes)
    return message_bytes.decode("utf-8")

def main():
    print("Do you want to CODE or DECODE a message?")
    choice = input("Type 'code' or 'decode': ").strip().lower()

    if choice == "code":
        message = input("Type your message: ")
        coded = encode_message(message)
        print("\n This is your code:\n")
        print(coded)

    elif choice == "decode":
        code = input("Type your code: ")
        try:
            decoded = decode_message(code)
            print("\n Your message is:\n")
            print(decoded)
        except Exception as e:
            print("❌ Error: Invalid code entered!")

    else:
        print("❌ Invalid choice. Please run again and choose 'code' or 'decode'.")

if __name__ == "__main__":
    main()
