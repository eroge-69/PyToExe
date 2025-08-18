#!/usr/bin/env python3
import re, sys, base64, os

TOKEN_REGEXES = [
    re.compile(r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}'),   # classic
    re.compile(r'mfa\.[\w-]{84}')                    # MFA
]

def decode_user_id(segment: str):
    pad = '=' * (-len(segment) % 4)
    try:
        raw = base64.urlsafe_b64decode(segment + pad)
        s = raw.decode('utf-8', errors='ignore')
        return int(s) if s.isdigit() else None
    except Exception:
        return None

def scan_file(path):
    hits = set()
    try:
        with open(path, 'rb') as f:
            data = f.read().decode('utf-8', errors='ignore')
        for rx in TOKEN_REGEXES:
            hits.update(rx.findall(data))
    except Exception:
        pass
    return hits

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <folder> <output_file>")
        sys.exit(1)

    root = sys.argv[1]
    output_file = sys.argv[2]

    tokens = set()
    for dp, _, files in os.walk(root):
        for fn in files:
            tokens.update(scan_file(os.path.join(dp, fn)))

    if not tokens:
        print("No tokens found.")
        return

    with open(output_file, "w") as out:
        for t in sorted(tokens):
            info = ""
            if not t.startswith("mfa."):
                seg = t.split('.')[0]
                uid = decode_user_id(seg)
                if uid:
                    info = f"[user_id ≈ {uid}]"
            out.write(f"{t} {info}\n")

    print(f"Saved {len(tokens)} potential tokens to {output_file}")

if __name__ == "__main__":
    main()
