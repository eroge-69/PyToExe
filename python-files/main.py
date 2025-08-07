import random

# Function to generate a random time between 8:00 AM and 8:15 AM
def generate_random_time():
    hour = 8
    minute = random.randint(0, 15)  # Random minute between 0 and 15
    return f"{hour:02}:{minute:02}:00"  # Format as HH:MM:SS

# Function to insert new records with random times between existing records
def insert_new_records(source_data, custom_id):
    new_data = []
    
    for record in source_data:
        new_data.append(record)  # Add the existing record
        
        # Extract the date from the current record
        date_str = record.split("\t")[1].split(" ")[0]  # Extract date part
        random_time = generate_random_time()
        
        # Create the new record with the generated random time
        new_record = f"{custom_id}\t{date_str} {random_time}\t1\t0\t1\t0"
        
        # Preserve the original spacing and tab structure
        new_data.append(new_record)

    return new_data

# Main execution
input_file_path = 'path/to/your/input_file.txt'  # Replace with your input file path
output_file_path = 'path/to/your/output_file.txt'  # Replace with your desired output file path

# Accept custom ID input from the user
custom_id = input("Please enter the custom ID: ")

# Read existing records from the input file
with open(input_file_path, 'r') as file:
    source_data = file.readlines()

# Process the records and generate new records
new_records = insert_new_records(source_data, custom_id)

# Save the updated records to the output file
with open(output_file_path, 'w') as file:
    file.writelines(new_records)

print(f"New records have been saved to {output_file_path}.")
