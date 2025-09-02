#!/usr/bin/env python3
"""
Remove Zero Sectors Script

This Python script removes all sectors containing only zeros (00000000) from a hex file.
Usage: 
    python remove_zero_sectors.py input.hex output.hex [sector_size]

Parameters:
    input.hex: Path to the input hex file
    output.hex: Path to save the output hex file
    sector_size: Size of each sector in bytes (default: 512)
"""

import sys
import os

def is_zero_sector(data):
    """
    Check if a sector contains only zeros
    """
    return all(byte == 0 for byte in data)

def main():
    # Check command line arguments
    if len(sys.argv) < 3:
        print("Usage: python remove_zero_sectors.py input.hex output.hex [sector_size]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Default sector size is 512 bytes
    sector_size = 512
    if len(sys.argv) > 3:
        try:
            sector_size = int(sys.argv[3])
        except ValueError:
            print(f"Error: Invalid sector size '{sys.argv[3]}'. Using default (512).")
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)
    
    # Statistics
    total_sectors = 0
    zero_sectors = 0
    non_zero_sectors = 0
    
    try:
        # Open input file for reading in binary mode
        with open(input_file, 'rb') as in_file:
            # Create output file for writing in binary mode
            with open(output_file, 'wb') as out_file:
                print(f"Processing file {input_file}...")
                
                while True:
                    # Read a sector
                    sector_data = in_file.read(sector_size)
                    
                    # Check if we've reached the end of the file
                    if not sector_data:
                        break
                    
                    total_sectors += 1
                    
                    # Check if the sector contains only zeros
                    if not is_zero_sector(sector_data):
                        # Write non-zero sector to output file
                        out_file.write(sector_data)
                        non_zero_sectors += 1
                    else:
                        zero_sectors += 1
                    
                    # Show progress every 1000 sectors
                    if total_sectors % 1000 == 0:
                        print(f"Processed {total_sectors} sectors, removed {zero_sectors} zero sectors...")
        
        # Display final statistics
        print("Processing complete!")
        print(f"Total sectors processed: {total_sectors}")
        print(f"Zero sectors removed: {zero_sectors}")
        print(f"Non-zero sectors kept: {non_zero_sectors}")
        print(f"Output file saved to: {output_file}")
        
        # Calculate size reduction
        input_size = os.path.getsize(input_file)
        output_size = os.path.getsize(output_file)
        reduction = input_size - output_size
        reduction_percent = (reduction / input_size) * 100 if input_size > 0 else 0
        
        print(f"Original size: {input_size:,} bytes")
        print(f"New size: {output_size:,} bytes")
        print(f"Size reduction: {reduction:,} bytes ({reduction_percent:.2f}%)")
        
    except IOError as e:
        print(f"Error processing file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()