import random

def generate_ipv4():
    # IPv4 with prefix 5 and three random sections
    return f"5.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"

def generate_ipv6():
    # IPv6 with prefix 6b0e:afcb:cc17:d4:: and additional random sections, totaling 17 characters without colons
    base = "6b0e:afcb:cc17:d4"
    random_parts = []
    total_chars = 17 - len(base.replace(":", ""))
    
    while sum(len(part) for part in random_parts) < total_chars:
        part = f"{random.randint(0, 65535):x}"
        if sum(len(part) for part in random_parts) + len(part) <= total_chars:
            random_parts.append(part)

    return f"{base}::{':'.join(random_parts)}"

def main():
    print("IPv4:", generate_ipv4())
    print("IPv4: 10.202.10.10")
    print("IPv6:", generate_ipv6())
    print("IPv6:", generate_ipv6())


if __name__ == "__main__":
    main()
