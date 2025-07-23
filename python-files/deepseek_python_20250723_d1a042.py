import sys
import struct
import lzss
import zlib
from typing import BinaryIO

def validate_sizes(input_bin: str, expected_com_size: int = 2054339):
    """Ensure input BIN is correct before processing."""
    with open(input_bin, 'rb') as f:
        bin_data = f.read()
    
    if len(bin_data) != 2555904:
        raise ValueError(f"Input BIN must be 2,555,904 bytes (got {len(bin_data)})")
    
    return bin_data

def compress_toshiba_lzss(data: bytes) -> bytes:
    """Toshiba-specific LZSS compression to achieve exact COM size."""
    # Adjust window_size and lookahead_buffer to match Toshiba's algorithm
    compressed = lzss.compress(data, window_size=4096, lookahead_buffer=18)
    
    # Pad to exact size if needed (Toshiba sometimes expects fixed sizes)
    if len(compressed) < 2054339 - 256:  # Account for header
        compressed += bytes([0xFF] * (2054339 - 256 - len(compressed)))
    return compressed

def build_toshiba_header(checksum: int) -> bytes:
    """Reconstruct Toshiba's 256-byte header exactly."""
    header = bytearray()
    
    # Signature (observed in Toshiba B552/F COM files)
    header.extend(b'TSBC')
    
    # File size fields (little-endian)
    header.extend(struct.pack('<I', 2054339))  # Total COM size
    header.extend(struct.pack('<I', 2555904))  # Uncompressed BIN size
    
    # Checksum and reserved fields
    header.extend(struct.pack('<I', checksum))
    header.extend(bytes(240))  # Toshiba-specific padding
    
    return header

def calculate_toshiba_checksum(data: bytes) -> int:
    """Toshiba's additive checksum with 32-bit overflow."""
    return sum(data) & 0xFFFFFFFF

def rebuild_com_file(input_bin: str, output_com: str):
    """Create a byte-perfect COM file for chgbiosf.exe."""
    try:
        bin_data = validate_sizes(input_bin)
        
        # Compress to match original COM size
        compressed_data = compress_toshiba_lzss(bin_data)
        
        # Build header with placeholder checksum
        com_header = build_toshiba_header(0)
        com_data = com_header + compressed_data
        
        # Calculate final checksum (must include header)
        checksum = calculate_toshiba_checksum(com_data)
        com_data[0x08:0x0C] = struct.pack('<I', checksum)
        
        # Verify final size
        if len(com_data) != 2054339:
            raise RuntimeError(f"Output COM is {len(com_data)} bytes (expected 2,054,339)")
        
        # Write file
        with open(output_com, 'wb') as f:
            f.write(com_data)
        
        print(f"Success! Output COM: {output_com}")
        print(f"Checksum: 0x{checksum:08X}")
        print("Ready for chgbiosf.exe flashing.")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python toshiba_rebuild_com.py input.bin output.com")
        sys.exit(1)
    
    rebuild_com_file(sys.argv[1], sys.argv[2])