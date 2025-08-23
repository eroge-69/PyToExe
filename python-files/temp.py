import argparse
import random
import re
import sys
import time

# Demo-only: replace with your real, server-side license verification.
PROVIDER_LICENSE = "ABC123-CRYPTO-2025"

SEARCH_MESSAGES = [
    "Scanning public blockchain data",
    "Analyzing mempool activity",
    "Indexing token transfer events",
    "Checking airdrop snapshot lists",
    "Aggregating smart contract logs",
    "Cross-referencing ENS records",
    "Crawling DeFi protocol metrics",
    "Inspecting exchange hot-wallet flows",
    "Exploring NFT marketplace events",
    "Reviewing L2 bridge deposits",
    "Evaluating staking withdrawals",
    "Parsing on-chain governance votes",
]

def validate_eth_address(addr: str) -> bool:
    """Basic Ethereum address validator (0x + 40 hex chars)."""
    return bool(re.fullmatch(r"0x[a-fA-F0-9]{40}", addr.strip()))

def search_simulation(duration_sec: int, msg_change_every: float = 8.0, tick: float = 0.2) -> bool:
    """
    Simulate a long-running 'search' with rotating messages and a spinner.
    Returns True on normal completion, False if interrupted.
    """
    spinner = "|/-\\"
    start = time.time()
    i = 0
    current_msg = random.choice(SEARCH_MESSAGES)
    next_change = start + msg_change_every

    try:
        while time.time() - start < duration_sec:
            now = time.time()
            if now >= next_change:
                current_msg = random.choice(SEARCH_MESSAGES)
                next_change = now + msg_change_every
                print()  # new line before switching message

            sys.stdout.write(f"\r{current_msg} {spinner[i % len(spinner)]}")
            sys.stdout.flush()
            time.sleep(tick)
            i += 1
    except KeyboardInterrupt:
        print("\n[Info] Search interrupted early by user.")
        return False
    finally:
        print()  # ensure newline at the end
    return True

def main():
    parser = argparse.ArgumentParser(description="Crypto Finder (Demo Simulation)")
    parser.add_argument(
        "--duration",
        type=int,
        default=4 * 60 * 60,  # 4 hours by default
        help="Search duration in seconds (use a small number for testing, e.g., 20).",
    )
    args = parser.parse_args()

    print("=== Crypto Finder (Demo) ===")
    license_input = input("Enter your license code: ").strip()

    if license_input != PROVIDER_LICENSE:
        print("License invalid. Exiting.")
        sys.exit(1)

    print("\n[Demo Notice] This is a simulation for testing. No real funds are found or sent.\n")
    hours = args.duration / 3600
    print(f"Starting 'searching' simulation for {args.duration} seconds (~{hours:.2f} hours). Press Ctrl+C to skip early.\n")

    search_simulation(args.duration)

    print("\nCongratulations! You (hypothetically) found 0.071 ETH.")

    # Ask for an ETH address (validated format); still demo-only.
    while True:
        addr = input("Enter your Ethereum address to (hypothetically) withdraw: ").strip()
        if validate_eth_address(addr):
            break
        print("Invalid Ethereum address format. It should look like: 0x followed by 40 hex characters.")

    print(f"\nThanks! In this demo, no actual transaction is made.")
    print(f"If this were live, 0.071 ETH would be queued to: {addr}")
    print("For real payouts, use testnets first, never hardcode private keys, and integrate via web3.py or a custodial API with clear user consent.")

if __name__ == "__main__":
    main()