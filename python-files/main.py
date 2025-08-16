#!/usr/bin/env python3
"""
Bitcoin Puzzle Random Scanner
Searches for private keys within a specified range using random search method.
This is for the public Bitcoin puzzle challenge.
"""

import random
import hashlib
import base58
import ecdsa
from ecdsa import SigningKey, SECP256k1
import sys
import time
from datetime import datetime

def private_key_to_wif(private_key_hex):
    """Convert private key to WIF format"""
    # Add version byte (0x80 for mainnet)
    extended_key = '80' + private_key_hex
    
    # Create checksum
    first_hash = hashlib.sha256(bytes.fromhex(extended_key)).digest()
    second_hash = hashlib.sha256(first_hash).digest()
    checksum = second_hash[:4].hex()
    
    # Add checksum to extended key
    final_key = extended_key + checksum
    
    # Convert to base58
    wif = base58.b58encode(bytes.fromhex(final_key)).decode()
    return wif

def private_key_to_address(private_key_hex):
    """Convert private key to Bitcoin address"""
    try:
        # Convert hex to integer
        private_key_int = int(private_key_hex, 16)
        
        # Create signing key
        signing_key = SigningKey.from_secret_exponent(private_key_int, curve=SECP256k1)
        verifying_key = signing_key.verifying_key
        
        # Get uncompressed public key
        public_key = b'\04' + verifying_key.to_string()
        
        # SHA256 hash
        sha256_hash = hashlib.sha256(public_key).digest()
        
        # RIPEMD160 hash
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256_hash)
        public_key_hash = ripemd160.digest()
        
        # Add version byte (0x00 for P2PKH)
        versioned_payload = b'\x00' + public_key_hash
        
        # Double SHA256 for checksum
        checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
        
        # Final address
        address_bytes = versioned_payload + checksum
        address = base58.b58encode(address_bytes).decode()
        
        return address
    except Exception as e:
        return None

def hex_to_decimal(hex_string):
    """Convert hex string to decimal"""
    return int(hex_string.replace('0x', ''), 16)

def decimal_to_hex(decimal_num):
    """Convert decimal to hex string (64 characters, padded with zeros)"""
    return format(decimal_num, '064x')

def validate_hex_range(hex_string):
    """Validate hex string format"""
    try:
        hex_string = hex_string.replace('0x', '').replace(' ', '')
        int(hex_string, 16)
        return hex_string.upper()
    except ValueError:
        return None

def main():
    print("=" * 60)
    print("    BITCOIN PUZZLE RANDOM SCANNER")
    print("    Public Bitcoin Puzzle Challenge")
    print("=" * 60)
    print()
    
    # Get target wallet address
    while True:
        target_address = input("Enter target wallet address: ").strip()
        if len(target_address) >= 26 and len(target_address) <= 35:
            break
        print("Invalid address format. Please enter a valid Bitcoin address.")
    
    # Get start range
    while True:
        start_input = input("Enter start range (hex, e.g., 20000000000000000): ").strip()
        start_hex = validate_hex_range(start_input)
        if start_hex:
            start_decimal = hex_to_decimal(start_hex)
            break
        print("Invalid hex format. Please enter a valid hexadecimal number.")
    
    # Get end range
    while True:
        end_input = input("Enter end range (hex, e.g., 3ffffffffffffffff): ").strip()
        end_hex = validate_hex_range(end_input)
        if end_hex:
            end_decimal = hex_to_decimal(end_hex)
            break
        print("Invalid hex format. Please enter a valid hexadecimal number.")
    
    if start_decimal >= end_decimal:
        print("Error: Start range must be smaller than end range.")
        return
    
    print(f"\nTarget Address: {target_address}")
    print(f"Start Range: {start_hex} ({start_decimal})")
    print(f"End Range: {end_hex} ({end_decimal})")
    print(f"Search Space: {end_decimal - start_decimal:,} keys")
    print("\nStarting random search...")
    print("Press Ctrl+C to stop")
    print("-" * 60)
    
    keys_checked = 0
    start_time = time.time()
    
    try:
        while True:
            # Generate random private key in range
            random_decimal = random.randint(start_decimal, end_decimal)
            private_key_hex = decimal_to_hex(random_decimal)
            
            # Generate address from private key
            generated_address = private_key_to_address(private_key_hex)
            keys_checked += 1
            
            # Check if we found the target
            if generated_address == target_address:
                print("\n" + "=" * 60)
                print("🎉 PRIVATE KEY FOUND! 🎉")
                print("=" * 60)
                print(f"Private Key (Hex): {private_key_hex}")
                print(f"Private Key (Decimal): {random_decimal}")
                print(f"Private Key (WIF): {private_key_to_wif(private_key_hex)}")
                print(f"Address: {generated_address}")
                print(f"Keys Checked: {keys_checked:,}")
                print("=" * 60)
                
                # Save to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"btc_puzzle_solution_{timestamp}.txt"
                with open(filename, 'w') as f:
                    f.write(f"Bitcoin Puzzle Solution Found\n")
                    f.write(f"Timestamp: {datetime.now()}\n")
                    f.write(f"Target Address: {target_address}\n")
                    f.write(f"Private Key (Hex): {private_key_hex}\n")
                    f.write(f"Private Key (Decimal): {random_decimal}\n")
                    f.write(f"Private Key (WIF): {private_key_to_wif(private_key_hex)}\n")
                    f.write(f"Keys Checked: {keys_checked:,}\n")
                
                print(f"Solution saved to: {filename}")
                input("\nPress Enter to exit...")
                return
            
            # Progress update every 10000 keys
            if keys_checked % 10000 == 0:
                elapsed_time = time.time() - start_time
                rate = keys_checked / elapsed_time
                print(f"Keys checked: {keys_checked:,} | Rate: {rate:.0f} keys/sec | Last key: {private_key_hex[:16]}...")
    
    except KeyboardInterrupt:
        print(f"\n\nScan stopped by user.")
        print(f"Keys checked: {keys_checked:,}")
        elapsed_time = time.time() - start_time
        if elapsed_time > 0:
            rate = keys_checked / elapsed_time
            print(f"Average rate: {rate:.2f} keys/second")
        print("No solution found in scanned range.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")