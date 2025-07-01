import csv
from datetime import datetime
from collections import defaultdict

input_file = 'for upload.txt'
output_file = 'cleaned_output.txt'

seen_entries = defaultdict(set)
output_lines = []

with open(input_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        emp_id = row['Personnel ID'].strip()
        timestamp_str = row['Time'].strip()
        state = row['In/out State'].strip()

        if not emp_id or not timestamp_str or not state:
            continue  # skip incomplete rows

        # Parse datetime
        dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        date_key = dt.strftime('%m/%d/%Y')
        time_key = dt.strftime('%H:%M')
        flag = 'I' if state == '0' else 'O'

        # Avoid second+ duplicates: only keep the first entry per ID/date/flag
        key = (emp_id, date_key, flag)
        if key in seen_entries[emp_id]:
            continue  # duplicate
        seen_entries[emp_id].add(key)

        formatted_line = f"{emp_id.zfill(4)}   ;{date_key};{time_key};{flag};"
        output_lines.append(formatted_line)

# Save to output text file
with open(output_file, 'w', encoding='utf-8') as out:
    out.write('\n'.join(output_lines))

print(f"Cleaned data saved to {output_file}")
