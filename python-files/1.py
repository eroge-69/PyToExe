#!/usr/bin/env python3
"""
Harris Radio Feature Upgrade Tool (Patent US5499295A)
with enhanced logging (with file fallback), full input validation,
and XOR‑based feature string encryption/decryption.

Structure of the unencrypted (plaintext) feature string:
  • Header (3 bytes, 6 hex digits):  
      - Byte 1: arbitrary  
      - Byte 2: seed (used for keystream generation)  
      - Byte 3: fixed constant (typically 10 or 0B; not modified)
  • Feature Bitfield (8 bytes, 16 hex digits): 62 features are represented in a 64‑bit field.
  • System Configuration (5 bytes, 10 hex digits):  
      - SYSGRP (2 bytes, 4 hex digits)  
      - TRKSYS (1 byte, 2 hex digits)  
      - CNVCHN (2 bytes, 4 hex digits)

The full encrypted feature string is 16 bytes (32 hex digits). The tool preserves the header,
decrypts the remaining 13 bytes, updates the feature bits and system config, then re‑encrypts.
"""

import logging
from datetime import datetime
import re
from typing import List, Tuple
import os
import sys
from dataclasses import dataclass

# --- Modified Logging Setup with Fallback ---
try:
    log_dir = os.path.expanduser('~')
    if not os.access(log_dir, os.W_OK):
        log_dir = os.getcwd()
    log_file = os.path.join(log_dir, f'feature_upgrade_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
except (OSError, PermissionError):
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format='%(levelname)s - %(message)s'
    )
    logging.warning("Could not create log file. Logging to console instead.")

# --- Constants ---
# For ESN: after removing spaces, it must be exactly 12 hex digits.
FEATURE_STRING_PATTERN = r'^[0-9A-F]+$'
FEATURE_BITS = 62  # Number of features
EXPECTED_TOTAL_LENGTH = 32  # Total hex digits in a valid feature string

# --- Validation Functions ---
def validate_esn(esn: str) -> bool:
    """Validate ESN: after removing spaces, must be 12 hex digits."""
    esn_clean = esn.replace(" ", "")
    return len(esn_clean) == 12 and bool(re.fullmatch(r'[0-9A-F]{12}', esn_clean))

def validate_feature_string(feature_string: str) -> bool:
    """
    Validate feature string format.
    It must consist solely of hexadecimal characters, have an even length,
    and (for this tool) be exactly 32 hex digits (when spaces are removed).
    """
    s = feature_string.replace(" ", "")
    return bool(re.fullmatch(FEATURE_STRING_PATTERN, s)) and (len(s) == EXPECTED_TOTAL_LENGTH)

def validate_feature_bits(bits: List[int]) -> bool:
    """Ensure each feature number is between 1 and 62."""
    return all(1 <= bit <= FEATURE_BITS for bit in bits)

# --- System Configuration Class ---
@dataclass
class SystemConfig:
    trksys: int
    sysgrp: int
    cnvchn: int

    def __post_init__(self):
        if not (1 <= self.trksys <= 255):
            raise ValueError("TRKSYS must be between 1 and 255")
        if not (1 <= self.sysgrp <= 65535):
            raise ValueError("SYSGRP must be between 1 and 65535")
        if not (1 <= self.cnvchn <= 65535):
            raise ValueError("CNVCHN must be between 1 and 65535")

    def to_hex(self) -> str:
        """Return system configuration as 10 hex digits: 4 for SYSGRP, 2 for TRKSYS, 4 for CNVCHN."""
        return f"{self.sysgrp:04X}{self.trksys:02X}{self.cnvchn:04X}"

# --- Keystream and XOR Functions ---
def generate_keystream(seed: int, length: int) -> List[int]:
    """Generate a keystream of the given length using: current = (current * 13 + 7) mod 256."""
    keystream = []
    current_value = seed
    for _ in range(length):
        keystream.append(current_value & 0xFF)
        current_value = (current_value * 13 + 7) % 256
    return keystream

def encrypt_feature_string(plaintext: str, seed: int) -> str:
    """XOR encrypt the plaintext (hex string) with the keystream generated from seed."""
    try:
        plaintext_bytes = bytes.fromhex(plaintext)
        keystream = generate_keystream(seed, len(plaintext_bytes))
        encrypted_bytes = bytes(b ^ k for b, k in zip(plaintext_bytes, keystream))
        return encrypted_bytes.hex().upper()
    except ValueError as e:
        raise Exception(f"Encryption error: {str(e)}")

def decrypt_feature_string(ciphertext: str, seed: int) -> str:
    """XOR decrypt the ciphertext (hex string) using the keystream generated from seed."""
    try:
        ciphertext_bytes = bytes.fromhex(ciphertext)
        keystream = generate_keystream(seed, len(ciphertext_bytes))
        decrypted_bytes = bytes(b ^ k for b, k in zip(ciphertext_bytes, keystream))
        return decrypted_bytes.hex().upper()
    except ValueError as e:
        raise Exception(f"Decryption error: {str(e)}")

# --- Conversion Functions ---
def string_to_binary(hex_string: str) -> str:
    """Convert a hex string to a binary string, padded to (number_of_bytes * 8) bits."""
    try:
        num_bytes = len(hex_string) // 2
        return bin(int(hex_string, 16))[2:].zfill(num_bytes * 8)
    except ValueError as e:
        raise Exception(f"Binary conversion error: {str(e)}")

def binary_to_string(binary: str) -> str:
    """Convert a binary string back to a hex string, padded to (len(binary)//4) hex digits."""
    try:
        num_hex_digits = len(binary) // 4
        return format(int(binary, 2), 'X').zfill(num_hex_digits)
    except ValueError as e:
        raise Exception(f"Hex conversion error: {str(e)}")

# --- Feature Bit Modification ---
def modify_feature_bits(binary: str, selected_features: List[int]) -> str:
    """
    Given a binary string representing the feature bitfield,
    set (to '1') the bits corresponding to the selected features (1-indexed).
    """
    if len(binary) < FEATURE_BITS:
        raise Exception("Binary string too short for feature bits")
    binary_list = list(binary)
    for bit in selected_features:
        binary_list[bit - 1] = '1'
    return ''.join(binary_list)

# --- Feature Bit Mapping ---
revised_feature_bit_mapping = {
    1: "Conventional Priority Scan",
    2: "EDACS 3 Site System Scan",
    3: "Public Address",
    4: "EDACS Group Scan",
    5: "EDACS Priority System Scan",
    6: "EDACS/P25 ProScan (ProSound / Wide Area Scan)",
    7: "EDACS/P25 Dynamic Regroup",
    8: "EDACS/P25 Emergency",
    9: "Type 99 Encode and Decode",
    10: "Conventional Emergency",
    11: "RX Preamp",
    12: "Digital Voice (P25 CAI)",
    13: "VGE Encryption",
    14: "DES Encryption",
    15: "VGS Encryption - User-defined speech encryption",
    16: "EDACS/P25 Mobile Data",
    17: "EDACS/P25 Status/Message",
    18: "EDACS/P25 Test Unit",
    19: "M-RK I Second Bank",
    20: "OpenSky AES Encryption (128-Bit)",
    21: "EDACS Security Key (ESK) / Personality Lock",
    22: "ProFile (Over-the-Air Programming - OTAP)",
    23: "Narrow Band",
    24: "Auto Power Control",
    25: "OpenSky Voice",
    26: "OpenSky Data",
    27: "OpenSky OTAR",
    28: "OpenSky AES Encryption (256-Bit)",
    29: "ProVoice (EDACS Digital Voice)",
    30: "Limited Feature Expansion (LPE-50/P5100/P5200/M5300)",
    31: "Smart Battery",
    32: "FIPS 140-2 Encryption Compliance",
    33: "P25 Common Air Interface (CAI) – P25 Conventional",
    34: "Direct Frequency Entry",
    35: "P25 Over-The-Air ReKeying (P25 OTAR)",
    36: "Personality Cloning",
    37: "EDACS/P25 AES Encryption (256-Bit)",
    38: "Radio TextLink",
    39: "P25 Trunking",
    40: "700Mhz Only",
    41: "VHF-Low (35-50 MHz)",
    42: "VHF-High (136-174 MHz)",
    43: "UHF (380-520 MHz)",
    44: "700/800 MHz (Dual Band)",
    45: "DES-CFB Encryption",
    46: "Vote Scan",
    47: "Phase II TDMA (P25 Phase 2 Trunking)",
    48: "GPS",
    49: "Bluetooth",
    50: "OMAP Wideband Disable",
    51: "MDC1200 Signaling",
    52: "C-TICK Certified Operation",
    53: "Single Key DES",
    54: "Control and Status Services",
    55: "Link Layer Authentication",
    56: "Motorola Multi-Group",
    57: "TSBK on an Analog Channel",
    58: "Unity Wideband Disable",
    59: "eData (Enhanced Data Capabilities)",
    60: "InBand GPS",
    61: "Encryption Lite (ARC4)",
    62: "Single Key AES"
}

# --- Process Feature Upgrade ---
def process_feature_upgrade(esn: str, feature_string: str, selected_features: List[int],
                            sys_config: SystemConfig) -> Tuple[str, List[str]]:
    """
    Process the feature upgrade.
    
    The full encrypted feature string (with spaces removed) must be exactly 32 hex digits.
    The structure is:
      • Header (first 6 hex digits, 3 bytes) – preserved.
      • Encrypted data (remaining 26 hex digits, 13 bytes):
            - Feature bitfield: first 16 hex digits (8 bytes)
            - System config: last 10 hex digits (5 bytes)
    
    Steps:
      1. Extract header and encrypted data.
      2. Use the second byte (positions 3–4 of header) as the seed.
      3. Decrypt the encrypted data.
      4. Split the decrypted data into the feature bitfield and system config.
      5. Modify the feature bitfield by setting the bits for selected features.
      6. Replace the system config with new values from sys_config.
      7. Re-concatenate and encrypt the modified data.
      8. Prepend the unchanged header.
    
    Returns:
      A tuple of (new encrypted feature string, list of enabled feature names).
    """
    try:
        esn = esn.strip().upper()
        feature_string = feature_string.strip().upper().replace(" ", "")
        if not validate_esn(esn):
            raise Exception("Invalid ESN format")
        if not validate_feature_string(feature_string):
            raise Exception("Invalid feature string format")
        if not validate_feature_bits(selected_features):
            raise Exception("Invalid feature bit numbers")
        if len(feature_string) != EXPECTED_TOTAL_LENGTH:
            raise Exception("Feature string must be exactly 32 hex digits")

        # Split the string
        header = feature_string[:6]            # first 3 bytes (6 hex digits)
        encrypted_data = feature_string[6:]      # remaining 26 hex digits
        # Seed is extracted from the second byte (positions 3–4) of the header
        seed = int(header[2:4], 16)
        logging.info(f"Processing upgrade for ESN: {esn}")

        # Decrypt the encrypted data (26 hex digits)
        decrypted_data = decrypt_feature_string(encrypted_data, seed)
        # Split decrypted data into feature bitfield and system config
        # Feature bitfield: first 16 hex digits; system config: last 10 hex digits.
        feature_bits_plain = decrypted_data[:16]
        # sys_config_plain = decrypted_data[16:]  (ignored; we use new sys_config)
        # Modify feature bitfield:
        binary_feature_bits = string_to_binary(feature_bits_plain)  # should be 16*4 = 64 bits
        modified_binary = modify_feature_bits(binary_feature_bits, selected_features)
        modified_feature_bits = binary_to_string(modified_binary).zfill(16)
        new_sys_config_hex = sys_config.to_hex()  # 10 hex digits
        # Final plaintext for encryption:
        final_plaintext = modified_feature_bits + new_sys_config_hex  # 16+10 = 26 hex digits
        new_encrypted_data = encrypt_feature_string(final_plaintext, seed)
        new_feature_string = header + new_encrypted_data

        enabled_features = [revised_feature_bit_mapping[bit] for bit in selected_features]
        logging.info(f"Successfully upgraded features for ESN: {esn}")
        logging.info(f"Enabled features: {', '.join(enabled_features)}")
        return new_feature_string, enabled_features

    except Exception as e:
        logging.error(f"Error processing upgrade for ESN {esn}: {str(e)}")
        raise

# --- Main CLI Interface ---
def main():
    """Interactive CLI for feature upgrade with full validation."""
    try:
        print("\nHarris Radio Feature Upgrade Tool (Patent US5499295A)\n")
        
        # Get ESN
        while True:
            esn = input("Enter ESN (format: XX XX XX XX XX XX): ").strip().upper()
            if validate_esn(esn):
                break
            print("Invalid ESN format. Please enter 12 hexadecimal characters with spaces (e.g., A4 02 01 01 10 61)")
        
        # Get current encrypted feature string
        while True:
            feature_string = input("Enter Current Encrypted Feature String (32 hex digits): ").strip().upper()
            if validate_feature_string(feature_string.replace(" ", "")):
                if len(feature_string.replace(" ", "")) == EXPECTED_TOTAL_LENGTH:
                    break
                else:
                    print(f"Feature string must be exactly {EXPECTED_TOTAL_LENGTH} hex digits (without spaces).")
            else:
                print("Invalid feature string format. Please enter an even-length hexadecimal string.")
        
        # Get new system configuration values
        sysgrp_str = input("Enter SYSGRP (1-65535) [default 65535]: ").strip() or "65535"
        trksys_str = input("Enter TRKSYS (1-255) [default 255]: ").strip() or "255"
        convch_str = input("Enter CNVCHN (1-65535) [default 65535]: ").strip() or "65535"
        try:
            sysgrp = int(sysgrp_str)
            trksys = int(trksys_str)
            convch = int(convch_str)
            new_sys_config = SystemConfig(trksys=trksys, sysgrp=sysgrp, cnvchn=convch)
        except ValueError:
            raise Exception("Invalid system configuration values.")
        
        # Display available features
        print("\nAvailable Features:")
        for bit, feature in revised_feature_bit_mapping.items():
            print(f"{bit:2d}. {feature}")
        
        # Get feature selection
        while True:
            try:
                selected_features_input = input("\nEnter feature numbers to enable (comma-separated): ").strip()
                selected_features = [int(x) for x in selected_features_input.split(",") if x.strip()]
                if validate_feature_bits(selected_features):
                    break
                print("Invalid feature numbers. Please enter numbers between 1 and 62.")
            except ValueError:
                print("Invalid input. Please enter comma-separated numbers.")
        
        # Process the upgrade
        new_encrypted, enabled_features = process_feature_upgrade(esn, feature_string, selected_features, new_sys_config)
        
        # Format output (insert spaces every 2 hex digits)
        spaced_string = " ".join(new_encrypted[i:i+2] for i in range(0, len(new_encrypted), 2))
        print("\nUpgrade Successful!")
        print("\nNew Encrypted Feature String:")
        print(spaced_string)
        print("\nEnabled Features:")
        for feature in enabled_features:
            print(f"- {feature}")
    
    except Exception as e:
        print(f"\nError: {str(e)}")
        logging.error(str(e))

if __name__ == "__main__":
    main()
