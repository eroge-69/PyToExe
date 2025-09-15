import random, time, sys
from colorama import init, Fore, Style
from mnemonic import Mnemonic

init(autoreset=True)


mnemo = Mnemonic("english")
WORDLIST = mnemo.wordlist  


PRINCIPALS = ["Bitcoin","Ethereum","Tether"]
PRICE_MAP = {"Bitcoin":110928,"Ethereum":4300,"Tether":1}
RANGE_MAP = {"Bitcoin":(0.001,0.05),"Ethereum":(0.01,0.5),"Tether":(10,500)}


HALLAZGO_MIN = 18000    
HALLAZGO_MAX = 43200   


def set_title(idx, balances_acumulado):
    total_usd = sum(balances_acumulado[c] * PRICE_MAP[c] for c in PRINCIPALS)
    title = f"PLOX SEEDMINER V1.0 | #{idx} | total USD ${total_usd:,.2f} | " + \
            " | ".join(f"{name}: {balances_acumulado[name]:.3f}" for name in PRINCIPALS)
    
    sys.stdout.write(f"\33]0;{title}\a")
    sys.stdout.flush()


def format_amount(amount):
    return f"{amount:,.3f}"

def format_usd(amount, crypto):
    return f"${amount*PRICE_MAP[crypto]:,.2f}"

def fake_mnemonic(words):
    return " ".join(random.choice(WORDLIST) for _ in range(words))

def fake_address():
    return "0x" + "".join(random.choice("0123456789abcdef") for _ in range(40))


def main():
    RATE = 69.6        
    WORDS = 12
    balances_acumulado = {name:0.0 for name in PRINCIPALS}  

    print(Fore.MAGENTA + Style.BRIGHT + "\n=== PLOX SEEDMINER V1.0 ===")
    print(Fore.YELLOW + "good luck ;)))).\n")

    try:
        while True:
            idx = 0
            start_time = time.time()
            hallazgo_time = start_time + random.uniform(HALLAZGO_MIN, HALLAZGO_MAX)

            while True:
                idx += 1
                mn = fake_mnemonic(WORDS)
                set_title(idx, balances_acumulado)  

                current_time = time.time()
                if current_time >= hallazgo_time:
                    crypto = random.choice(PRINCIPALS)
                    addr = fake_address()
                    low, high = RANGE_MAP[crypto]
                    bal = round(random.uniform(low, high),3)
                    balances_acumulado[crypto] += bal  

                    total_usd = sum(balances_acumulado[c]*PRICE_MAP[c] for c in PRINCIPALS)
                    per_crypto = " | ".join(f"{c}: {format_amount(balances_acumulado[c])} ({format_usd(balances_acumulado[c], c)})" for c in PRINCIPALS)

                    print(Fore.GREEN + f"#{idx} BALANCE FOUND!!!! , saved on wallets.txt")
                    print(Fore.GREEN + f"  Seed: {mn}")
                    print(Fore.GREEN + f"  Addr: {addr}")
                    print(Fore.GREEN + f"  | total USD = ${total_usd:,.2f} | {per_crypto}")
                    print(Style.DIM + "-"*100)

                    
                    with open("wallets.txt","a",encoding="utf-8") as f:
                        f.write(f"#{idx} | Seed: {mn} | Addr: {addr} | total USD: ${total_usd:,.2f} | {per_crypto}\n")

                    input(Fore.CYAN + "\nBalance Found! Press ENTER to start again...")
                    break  

                else:
                    
                    total_usd = sum(balances_acumulado[c]*PRICE_MAP[c] for c in PRINCIPALS)
                    per_crypto = " | ".join(f"{c}: {format_amount(balances_acumulado[c])}" for c in PRINCIPALS)
                    print(Fore.WHITE + f"#{idx} Seed: {mn} | total USD = ${total_usd:,.2f} | {per_crypto}")

                time.sleep(1.0 / RATE)

    except KeyboardInterrupt:
        print(Fore.RED + "\nMining stopped by user.")

if __name__=="__main__":
    main()
