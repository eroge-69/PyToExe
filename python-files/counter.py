import tiktoken

def main():
    # Χρησιμοποιούμε το encoding cl100k_base (είναι αυτό των GPT-4/5)
    enc = tiktoken.get_encoding("cl100k_base")

    print("=== Token Counter (GPT encoding) ===")
    print("Δώσε το κείμενο που θέλεις να μετρήσεις (Ctrl+D για τέλος σε Linux/Mac ή Ctrl+Z σε Windows):")

    # Διαβάζουμε όλο το input κείμενο
    text = []
    try:
        while True:
            line = input()
            text.append(line)
    except EOFError:
        pass

    text = "\n".join(text)

    tokens = enc.encode(text)
    print("\nΑριθμός tokens:", len(tokens))

if __name__ == "__main__":
    main()
