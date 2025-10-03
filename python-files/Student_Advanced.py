
strGroupName = input("Please enter the names of those in your group: ")

def secs_to_hms(seconds: float) -> str:
    seconds = int(round(seconds))
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h}h {m}m {s}s"

def brute_force_with_timing(max_guess=9999999, report_every=1000):
    # Read secret once (faster than opening the file every attempt)
    try:
        with open("secret_pin.txt", "r", encoding="utf-8") as f:
            secret = f.read().strip()
    except FileNotFoundError:
        print("Error: secret_pin.txt not found.")
        return None, 0, 0.0

    # Decide how we will compare:
    numeric_secret = secret.isdigit()   # True if secret is all digits (e.g., "0427" or "427")
    # zfill width: use the secret length if you want guesses to print with same leading zeros
    zfill_width = len(secret)

    start = time.perf_counter()
    guess = 0
    attempts = 0

    while guess <= max_guess:
        attempts += 1
        pin_str = str(guess).zfill(zfill_width)

        # Comparison logic:
        if numeric_secret:
            # numeric compare ignores leading zeros (so "0427" == "427")
            try:
                if int(pin_str) == int(secret):
                    elapsed = time.perf_counter() - start
                    aps = attempts / elapsed if elapsed > 0 else float('inf')
                    print(f"Found PIN: {pin_str} (attempts #{attempts}) — {elapsed:.4f} s ({secs_to_hms(elapsed)})")
                    print(f"Rate: {aps:.1f} attempts/sec")
                    return pin_str, attempts, elapsed
            except ValueError:
                # defensive: if conversion to int somehow fails, fall back to string compare
                if pin_str == secret:
                    elapsed = time.perf_counter() - start
                    aps = attempts / elapsed if elapsed > 0 else float('inf')
                    print(f"Found PIN: {pin_str} (attempts #{attempts}) — {elapsed:.4f} s ({secs_to_hms(elapsed)})")
                    print(f"Rate: {aps:.1f} attempts/sec")
                    return pin_str, attempts, elapsed
        else:
            # non-numeric secret: compare exact strings (preserves leading zeros)
            if pin_str == secret:
                elapsed = time.perf_counter() - start
                aps = attempts / elapsed if elapsed > 0 else float('inf')
                print(f"Found PIN: {pin_str} (attempts #{attempts}) — {elapsed:.4f} s ({secs_to_hms(elapsed)})")
                print(f"Rate: {aps:.1f} attempts/sec")
                return pin_str, attempts, elapsed

        # periodic report (reduces printing overhead)
        if attempts % report_every == 0:
            elapsed = time.perf_counter() - start
            aps = attempts / elapsed if elapsed > 0 else float('inf')
            remaining = (max_guess + 1) - (guess + 1)
            eta_seconds = remaining / aps if aps > 0 else float('inf')
            print(f"[{attempts}/{max_guess+1}] trying {pin_str}  rate={aps:.1f} a/s  ETA={secs_to_hms(eta_seconds)}")

        guess += 1

    elapsed = time.perf_counter() - start
    print(f"PIN not found after {attempts} attempts in {elapsed:.4f} seconds")
    return None, attempts, elapsed

def open_document():
    try:
        # Print existing document contents (if any)
        with open("locked_document.txt", "r", encoding="utf-8") as doc:
            print("-----DOCUMENT CONTENTS-----")
            print(doc.read())
            print("---------------------------")
    except FileNotFoundError:
        print("locked_document.txt not found. (It will be created when we append.)")

    # Append team + timestamp (done outside the read block to avoid nested open issues)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("locked_document.txt", "a", encoding="utf-8") as f:
        f.write(f"Team: {strGroupName}  Unlocked at: {now}\n")

if __name__ == "__main__":
    pin, attempts, elapsed = brute_force_with_timing(max_guess=999999999, report_every=2000)
    if pin:
        open_document()
    else:
        print(f"PIN not found after {attempts} attempts in {elapsed:.4f} seconds")
