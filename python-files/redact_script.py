
import os
import re
import logging
from docx import Document

# Define folder paths
input_folder = 'input_docs'
output_folder = 'redacted_docs'
log_file = 'redaction_log.txt'

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Set up logging
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')

# Define regex patterns for personal data
patterns = {
    'Account Number': r'\b\d{8,16}\b',
    'Email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'Phone Number': r'\b(?:\+?\d{1,3})?[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{4}\b',
    'Surname': r'\b[A-Z][a-z]+(?:-[A-Z][a-z]+)?\b'
}

# Function to redact text
def redact_text(text, file_name):
    for label, pattern in patterns.items():
        matches = re.findall(pattern, text)
        for match in matches:
            text = text.replace(match, '[REDACTED]')
            logging.info(f"{file_name}: Redacted {label} - {match}")
    return text

# Process each .docx file in the input folder
for file_name in os.listdir(input_folder):
    if file_name.endswith('.docx'):
        file_path = os.path.join(input_folder, file_name)
        doc = Document(file_path)

        # Redact text in each paragraph
        for para in doc.paragraphs:
            para.text = redact_text(para.text, file_name)

        # Save the redacted document
        output_path = os.path.join(output_folder, file_name)
        doc.save(output_path)

print(f"Redaction complete. Cleaned documents saved in '{output_folder}' and log saved in '{log_file}'.")
