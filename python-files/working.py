import streamlit as st
import json
import math
import struct
import hashlib

def reverse_pairwise(subtracted, original_len, mod, anchors):
    """Reverse pairwise subtraction to reconstruct the original list using anchors."""
    reconstructed = []
    is_odd = original_len % 2 != 0
    subtracted_copy = subtracted[:]
    anchor_idx = 0
    if is_odd:
        last_value = subtracted_copy.pop()
    num_pairs = original_len // 2
    for _ in range(num_pairs):
        a = anchors[anchor_idx]
        c = subtracted_copy.pop(0)
        b = (a + c) % mod
        reconstructed.append(a)
        reconstructed.append(b)
        anchor_idx += 1
    if is_odd:
        reconstructed.append(last_value)
    return reconstructed

def main():
    st.title("Binary File Processor with Compact Binary Output and Accurate Restoration")
    
    st.markdown("""
    This application processes a file into decimal and binary outputs with subtractions,
    or restores the original file from a second subtracted decimal binary file.
    The second subtracted output is a compact binary file with minimal metadata for reduced size.
    """)
    
    # Modulo for 100 bits
    mod = 2 ** 100
    all_ones = '1' * 100
    ones_int = int(all_ones, 2)
    
    # Section for processing input file
    st.header("Process File")
    uploaded_file = st.file_uploader("Upload any file to process", type=None, key="process_uploader")
    
    if uploaded_file is not None:
        # Read the file as binary bytes
        file_bytes = uploaded_file.read()
        
        # Compute SHA-256 checksum
        sha256_hash = hashlib.sha256(file_bytes).hexdigest()
        
        # Provide downloadable binary file
        st.download_button(
            label="Download as Binary File",
            data=file_bytes,
            file_name="input.bin",
            mime="application/octet-stream"
        )
        
        if st.button("Process File"):
            with st.spinner("Processing..."):
                # Convert bytes to binary string
                binary_str = ''.join(format(byte, '08b') for byte in file_bytes)
                
                # Split into chunks of 100 bits, pad last chunk with 0s if needed
                chunks = []
                for i in range(0, len(binary_str), 100):
                    chunk = binary_str[i:i+100]
                    if len(chunk) < 100:
                        chunk += '0' * (100 - len(chunk))
                    chunks.append(chunk)
                
                # Process each chunk: subtract from 111...1 (modular)
                processed_decimals = []
                for chunk in chunks:
                    chunk_int = int(chunk, 2)
                    result_int = (ones_int - chunk_int) % mod
                    processed_decimals.append(result_int)
                
                # Anchors for first level
                anchors_first = processed_decimals[0::2]
                
                # First pairwise subtraction (modular)
                first_subtracted_decimals = []
                for i in range(0, len(processed_decimals)-1, 2):
                    result = (processed_decimals[i+1] - processed_decimals[i]) % mod
                    first_subtracted_decimals.append(result)
                if len(processed_decimals) % 2 != 0:
                    first_subtracted_decimals.append(processed_decimals[-1])
                
                # Anchors for second level
                anchors_second = first_subtracted_decimals[0::2]
                
                # Second pairwise subtraction (modular)
                second_subtracted_decimals = []
                for i in range(0, len(first_subtracted_decimals)-1, 2):
                    result = (first_subtracted_decimals[i+1] - first_subtracted_decimals[i]) % mod
                    second_subtracted_decimals.append(result)
                if len(first_subtracted_decimals) % 2 != 0:
                    second_subtracted_decimals.append(first_subtracted_decimals[-1])
                
                # Compute total of second subtraction results
                total_second_subtraction = sum(second_subtracted_decimals) % mod
                
                # Create text outputs
                decimal_output_str = ','.join(str(x) for x in processed_decimals)
                first_subtracted_output_str = ','.join(str(x) for x in first_subtracted_decimals)
                
                # Create binary output for second subtracted decimals
                metadata = {
                    'name': uploaded_file.name,
                    'extension': uploaded_file.name.split('.')[-1] if '.' in uploaded_file.name else '',
                    'mime': uploaded_file.type if uploaded_file.type else 'application/octet-stream',
                    'size': len(file_bytes),
                    'original_bit_length': len(binary_str),
                    'num_anchors_first': len(anchors_first),
                    'num_anchors_second': len(anchors_second),
                    'sha256': sha256_hash
                }
                metadata_str = json.dumps(metadata)
                metadata_bytes = metadata_str.encode('utf-8')
                metadata_len = len(metadata_bytes)
                
                # Pack binary output: metadata length (4 bytes), metadata, anchors, numbers
                output_binary = bytearray()
                output_binary.extend(struct.pack('>I', metadata_len))  # Metadata length
                output_binary.extend(metadata_bytes)
                for anchor in anchors_first:
                    output_binary.extend(anchor.to_bytes(13, byteorder='big'))
                for anchor in anchors_second:
                    output_binary.extend(anchor.to_bytes(13, byteorder='big'))
                for num in second_subtracted_decimals:
                    output_binary.extend(num.to_bytes(13, byteorder='big'))
                output_binary.extend(total_second_subtraction.to_bytes(13, byteorder='big'))
                
                # Convert bytearray to bytes
                output_binary_bytes = bytes(output_binary)
                
                # Display some info
                st.success(f"Processing complete! Original binary length: {len(binary_str)} bits")
                st.info(f"Number of chunks: {len(chunks)} (each 100 bits)")
                st.info(f"First subtraction results: {len(first_subtracted_decimals)}")
                st.info(f"Second subtraction results: {len(second_subtracted_decimals)} + 1 total")
                st.info(f"Second subtracted output size: {len(output_binary_bytes)} bytes")
                
                # Download buttons
                st.download_button(
                    label="Download Decimal Output TXT",
                    data=decimal_output_str,
                    file_name="output_decimal.txt",
                    mime="text/plain"
                )
                st.download_button(
                    label="Download First Subtracted Decimal Output TXT",
                    data=first_subtracted_output_str,
                    file_name="output_first_subtracted_decimal.txt",
                    mime="text/plain"
                )
                st.download_button(
                    label="Download Second Subtracted Decimal Binary",
                    data=output_binary_bytes,
                    file_name="output_second_subtracted_decimal.bin",
                    mime="application/octet-stream"
                )
    
    # Section for restoration
    st.header("Restore File")
    restore_file = st.file_uploader("Upload Second Subtracted Decimal Binary to Restore", type=['bin'], key="restore_uploader")
    
    if restore_file is not None:
        if st.button("Restore File"):
            with st.spinner("Restoring..."):
                # Read the binary file
                content = restore_file.read()
                if len(content) < 4:
                    st.error("Invalid binary file format. Too small.")
                    return
                
                # Unpack metadata length and metadata
                metadata_len = struct.unpack('>I', content[:4])[0]
                try:
                    metadata_str = content[4:4+metadata_len].decode('utf-8')
                    metadata = json.loads(metadata_str)
                except (UnicodeDecodeError, json.JSONDecodeError):
                    st.error("Invalid metadata in binary file.")
                    return
                
                # Extract metadata
                size_bytes = metadata.get('size', 0)
                original_bit_len = metadata.get('original_bit_length', size_bytes * 8)
                file_name = metadata.get('name', 'restored_file')
                file_mime = metadata.get('mime', 'application/octet-stream')
                num_anchors_first = metadata.get('num_anchors_first', 0)
                num_anchors_second = metadata.get('num_anchors_second', 0)
                original_sha256 = metadata.get('sha256', '')
                
                # Calculate expected number of chunks
                num_chunks = math.ceil(original_bit_len / 100)
                len_processed = num_chunks
                len_first = (len_processed + 1) // 2
                len_second = (len_first + 1) // 2
                
                # Parse anchors and numbers
                offset = 4 + metadata_len
                anchors_first = []
                for i in range(num_anchors_first):
                    anchor_bytes = content[offset:offset+13]
                    anchors_first.append(int.from_bytes(anchor_bytes, byteorder='big'))
                    offset += 13
                anchors_second = []
                for i in range(num_anchors_second):
                    anchor_bytes = content[offset:offset+13]
                    anchors_second.append(int.from_bytes(anchor_bytes, byteorder='big'))
                    offset += 13
                second_subtracted = []
                for i in range(len_second):
                    num_bytes = content[offset:offset+13]
                    second_subtracted.append(int.from_bytes(num_bytes, byteorder='big'))
                    offset += 13
                total = int.from_bytes(content[offset:offset+13], byteorder='big')
                
                # Validate total
                computed_total = sum(second_subtracted) % mod
                if computed_total != total:
                    st.warning("Total mismatch, but proceeding with restoration.")
                
                if len(second_subtracted) != len_second:
                    st.error(f"Invalid number of subtracted values. Expected {len_second}, got {len(second_subtracted)}.")
                    return
                
                # Reverse to first subtracted decimals
                first_subtracted = reverse_pairwise(second_subtracted, len_first, mod, anchors_second)
                
                # Reverse to processed decimals
                processed_decimals = reverse_pairwise(first_subtracted, len_processed, mod, anchors_first)
                
                # Reverse to original binary chunks
                original_chunks_bin = []
                for pd in processed_decimals:
                    orig_int = (ones_int - pd) % mod
                    orig_bin = format(orig_int, '0100b')
                    original_chunks_bin.append(orig_bin)
                
                # Combine chunks and trim to original bit length
                full_bin = ''.join(original_chunks_bin)
                original_bin = full_bin[:original_bit_len]
                
                # Convert binary string to bytes
                try:
                    original_int = int(original_bin, 2)
                    original_bytes = original_int.to_bytes(size_bytes, byteorder='big')
                except ValueError as e:
                    st.error(f"Error converting binary to bytes: {e}")
                    return
                
                # Verify checksum
                restored_sha256 = hashlib.sha256(original_bytes).hexdigest()
                if original_sha256 and restored_sha256 != original_sha256:
                    st.warning(f"Checksum mismatch! Restored file may be corrupted. Original SHA-256: {original_sha256}, Restored: {restored_sha256}")
                
                # Provide restored file
                st.success("Restoration complete!")
                st.download_button(
                    label="Download Restored File",
                    data=original_bytes,
                    file_name=file_name,
                    mime=file_mime
                )

if __name__ == "__main__":
    main()