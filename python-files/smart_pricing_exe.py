#!/usr/bin/env python3
"""
Smart Pricing Mechanism Executable

This script provides a simplified interface for the smart pricing mechanism.
"""

import sys
import os
import random
import numpy as np
from smart_pricing import SmartPricingMechanism

def generate_random_bids(n_customers, base_price):
    """
    Generate random bids for testing.
    
    Args:
        n_customers: Number of customers
        base_price: Base price
        
    Returns:
        List of bids
    """
    # Define bid range
    min_bid = base_price * 0.51  # P-49%
    max_bid = base_price * 1.50  # P+50%
    
    # Generate random bids
    bids = [random.uniform(min_bid, max_bid) for _ in range(n_customers)]
    return bids

def print_table(headers, rows):
    """
    Print a formatted table.
    
    Args:
        headers: List of column headers
        rows: List of rows, where each row is a list of values
    """
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))
    
    # Print header
    header_row = " | ".join(f"{h:{w}s}" for h, w in zip(headers, col_widths))
    print(header_row)
    print("-" * len(header_row))
    
    # Print rows
    for row in rows:
        row_str = " | ".join(f"{str(val):{w}s}" for val, w in zip(row, col_widths))
        print(row_str)

def run_example():
    """
    Run an example with predefined parameters.
    """
    # Example parameters
    n_items = 10
    base_price = 100
    n_customers = 10
    bids = [75.5, 80.2, 90.0, 100.0, 110.5, 120.0, 130.5, 140.0, 145.5, 150.0]
    
    print(f"\nRunning Smart Pricing Mechanism with {n_customers} customers and {n_items} items")
    print(f"Base price: {base_price}")
    print("-" * 80)
    
    # Run the mechanism
    mechanism = SmartPricingMechanism(n_items, base_price, n_customers, bids)
    results = mechanism.run_mechanism()
    
    # Print results
    print("\nResults:")
    print(f"Fulfilled customer ratio (T/C): {results['fulfilled_ratio']:.4f}")
    print(f"Sold items ratio (T/N): {results['sold_ratio']:.4f}")
    print(f"Vendor revenue: {results['vendor_revenue']:.2f}")
    print(f"Remaining balance: {results['remaining_balance']:.2f}")
    
    # Print customer data in a table
    print("\nCustomer Data:")
    headers = ["Customer ID", "Bid", "Final Price"]
    rows = []
    for i in range(n_customers):
        rows.append([
            i+1,
            f"{bids[i]:.2f}",
            results['customer_prices'][i] if results['customer_prices'][i] != "Incomplete" else "Incomplete"
        ])
    print_table(headers, rows)
    
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    run_example()
