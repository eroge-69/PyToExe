#!/usr/bin/env python3
import csv
import json
import re
import os
from datetime import datetime, timedelta

def read_csv_file(file_path, skip_rows=0):
    """Read CSV file and return list of dictionaries"""
    rows = []
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        # Skip header rows if needed
        for _ in range(skip_rows):
            next(file)
        
        reader = csv.DictReader(file)
        for row in reader:
            # Skip empty rows
            if any(value.strip() for value in row.values() if value):
                rows.append(row)
    return rows

def parse_clinical_user(user_str):
    """Parse Clinical User format: LastName, FirstName (discipline)"""
    if not user_str:
        return '', ''
    
    # Remove discipline part in parentheses
    user_clean = re.sub(r'\s*\([^)]*\)\s*$', '', user_str.strip())
    
    # Split by comma
    parts = user_clean.split(',')
    if len(parts) >= 2:
        last_name = parts[0].strip()
        first_name = parts[1].strip()
        return first_name, last_name
    
    return '', ''

def parse_times(clinical_time_str, mcg_time_str):
    """Parse and compare times - Clinical is local (-6), MCG is UTC"""
    if not clinical_time_str or not mcg_time_str:
        return False
    
    try:
        # Parse Clinical time (ISO format with timezone)
        clinical_dt = datetime.fromisoformat(clinical_time_str.replace('Z', '+00:00'))
        # Convert to UTC by adding 6 hours (since it's -6 timezone)
        clinical_utc = clinical_dt.replace(tzinfo=None)
        if '-06:00' in clinical_time_str:
            clinical_utc = clinical_utc + timedelta(hours=6)
        
        # Parse MCG time (simple format, already UTC)
        mcg_dt = datetime.strptime(mcg_time_str, '%m/%d/%Y %H:%M')
        
        # Compare date, hour, and minute
        return (clinical_utc.date() == mcg_dt.date() and 
                clinical_utc.hour == mcg_dt.hour and 
                clinical_utc.minute == mcg_dt.minute)
    except:
        return False

def match_visits(clinical_file, mcg_file, output_file):
    """Match visits from two CSV files and create merged output"""
    
    clinical_data = read_csv_file(clinical_file, skip_rows=5)
    mcg_data = read_csv_file(mcg_file)
    
    print(f"Clinical: {len(clinical_data)} records, MCG: {len(mcg_data)} records")
    
    total_clinical = len(clinical_data)
    total_mcg = len(mcg_data)
    
    matched_records = []
    used_clinical_indices = set()
    used_mcg_indices = set()
    
    # Match records based on carerecord_client_id to MR# (1:1 matching)
    for j, mcg_row in enumerate(mcg_data):
        mcg_client_id = str(mcg_row.get('carerecord_client_id', '')).strip()
        
        if not mcg_client_id:
            continue
        
        for i, clinical_row in enumerate(clinical_data):
            if i in used_clinical_indices:
                continue
                
            clinical_mr = str(clinical_row.get('MR#', '')).strip()
            
            if mcg_client_id == clinical_mr and mcg_client_id != '':
                # Additional matching: Check personnel names
                clinical_first, clinical_last = parse_clinical_user(clinical_row.get('User', ''))
                mcg_first = str(mcg_row.get('personnel_first_name', '')).strip()
                mcg_last = str(mcg_row.get('personnel_last_name', '')).strip()
                
                # Additional matching: Check times
                clinical_clock_in = clinical_row.get('Clock In - Device Date/Time', '')
                mcg_actual_start = mcg_row.get('actual_start_time', '')
                
                # Match if patient ID, personnel names, and times all match
                if (clinical_first.lower() == mcg_first.lower() and 
                    clinical_last.lower() == mcg_last.lower() and
                    clinical_first != '' and clinical_last != '' and
                    parse_times(clinical_clock_in, mcg_actual_start)):
                    
                    # Create merged record with original columns
                    matched_record = {
                        'Matched_Patient': mcg_client_id,
                        'Matched_User': f"{clinical_first} {clinical_last}",
                        'Matched_DateTime': mcg_actual_start
                    }
                    
                    # Add all clinical columns
                    matched_record.update(clinical_row)
                    
                    # Add all MCG columns
                    matched_record.update(mcg_row)
                    
                    matched_records.append(matched_record)
                    used_clinical_indices.add(i)
                    used_mcg_indices.add(j)
                    break
    
    # Add unmatched Clinical records
    for i, clinical_row in enumerate(clinical_data):
        if i not in used_clinical_indices:
            unmatched_record = {
                'Matched_Patient': 'No Match',
                'Matched_User': 'No Match', 
                'Matched_DateTime': 'No Match'
            }
            unmatched_record.update(clinical_row)
            matched_records.append(unmatched_record)
    
    # Add unmatched MCG records
    for j, mcg_row in enumerate(mcg_data):
        if j not in used_mcg_indices:
            unmatched_record = {
                'Matched_Patient': 'No Match',
                'Matched_User': 'No Match',
                'Matched_DateTime': 'No Match'
            }
            unmatched_record.update(mcg_row)
            matched_records.append(unmatched_record)
    
    # Write to CSV output
    if matched_records:
        fieldnames = list(matched_records[0].keys())
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(matched_records)
        
        matched_count = len(used_clinical_indices)
        clinical_unmatched = total_clinical - matched_count
        mcg_unmatched = total_mcg - len(used_mcg_indices)
        
        print(f"Data saved to: {output_file}")
        print(f"Total matched: {matched_count}")
        print(f"Clinical visits not matched: {clinical_unmatched}")
        print(f"MCG visits not matched: {mcg_unmatched}")
    
    return matched_records

if __name__ == "__main__":
    print("CSV Visit Matcher")
    print("=" * 20)
    
    # Get file paths from user
    clinical_file = input("Enter path to Clinical Visits CSV file: ").strip()
    mcg_file = input("Enter path to MCG Visits CSV file: ").strip()
    
    # Validate files exist
    if not os.path.exists(clinical_file):
        print(f"Error: Clinical file not found: {clinical_file}")
        exit(1)
    if not os.path.exists(mcg_file):
        print(f"Error: MCG file not found: {mcg_file}")
        exit(1)
    
    # Generate output filename
    output_file = input("Enter output filename (or press Enter for 'Matched_Visits.csv'): ").strip()
    if not output_file:
        output_file = "Matched_Visits.csv"
    
    print(f"\nProcessing files...")
    
    # Run the matching
    result = match_visits(clinical_file, mcg_file, output_file)
    
    print("\nDone! Press Enter to exit...")
    input()