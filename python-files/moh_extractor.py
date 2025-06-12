import os
import re
import pandas as pd
import PyPDF2
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        logging.error(f"Error reading PDF {pdf_path}: {str(e)}")
        return None

def extract_patient_info(text, filename):
    """Extract patient information from the letter text"""
    patient_data = {
        'date_added': datetime.now().strftime('%d %b %Y'),
        'approval_number': None,
        'health_number': None,
        'patient_name': None,
        'approval_date': None,
        'expiry_date': None,
        'service': None
    }
    
    if not text:
        logging.warning(f"Could not extract text from {filename}")
        return patient_data
    
    try:
        # Extract letter date and format as DD MMM YYYY
        date_pattern = r'([A-Za-z]+ \d{1,2}, \d{4})'
        date_match = re.search(date_pattern, text)
        if date_match:
            date_str = date_match.group(1)
            try:
                # Parse the date and reformat
                parsed_date = datetime.strptime(date_str, '%B %d, %Y')
                patient_data['approval_date'] = parsed_date.strftime('%d %b %Y')
                
                # Calculate expiry date (6 months later)
                if parsed_date.month <= 6:
                    expiry_date = parsed_date.replace(month=parsed_date.month + 6)
                else:
                    expiry_date = parsed_date.replace(year=parsed_date.year + 1, month=parsed_date.month - 6)
                patient_data['expiry_date'] = expiry_date.strftime('%d %b %Y')
            except ValueError:
                logging.warning(f"Could not parse date '{date_str}' in {filename}")
        
        # Extract patient name from RE: line
        # Pattern: RE: [Name] (Health Number [...], Prior Approval Number [...])
        re_pattern = r'RE:\s*([^(]+)\s*\(Health Number\s+([^,]+),\s*Prior Approval Number\s+([^)]+)\)'
        re_match = re.search(re_pattern, text, re.IGNORECASE)
        
        if re_match:
            patient_data['patient_name'] = re_match.group(1).strip()
            patient_data['health_number'] = re_match.group(2).strip()
            patient_data['approval_number'] = re_match.group(3).strip()
        
        # Determine service type based on text content
        if 'liver and cardiac iron' in text.lower():
            patient_data['service'] = 'Both'
        elif 'liver iron' in text.lower():
            patient_data['service'] = 'FerriScan'
        else:
            # Look for other variations
            if 'cardiac' in text.lower() and 'liver' in text.lower():
                patient_data['service'] = 'Both'
            elif 'ferriscan' in text.lower():
                patient_data['service'] = 'FerriScan'
            
    except Exception as e:
        logging.error(f"Error extracting data from {filename}: {str(e)}")
    
    return patient_data

def process_moh_letters(folder_path, output_excel_path):
    """Process all PDF files in the folder and extract patient information"""
    
    if not os.path.exists(folder_path):
        logging.error(f"Folder path does not exist: {folder_path}")
        return
    
    # Get all PDF files in the folder
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        logging.warning(f"No PDF files found in {folder_path}")
        return
    
    logging.info(f"Found {len(pdf_files)} PDF files to process")
    
    all_patient_data = []
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(folder_path, pdf_file)
        logging.info(f"Processing: {pdf_file}")
        
        # Extract text from PDF
        text = extract_text_from_pdf(pdf_path)
        
        # Extract patient information
        patient_info = extract_patient_info(text, pdf_file)
        all_patient_data.append(patient_info)
    
    # Create DataFrame and save to Excel
    df = pd.DataFrame(all_patient_data)
    
    # Reorder columns as requested
    column_order = [
        'date_added', 'approval_number', 'health_number', 'patient_name',
        'approval_date', 'expiry_date', 'service'
    ]
    df = df[column_order]
    
    # Rename columns to match Excel headers
    df.columns = [
        'Date Added', 'Approval Number', 'Health Number', 'Patient Name',
        'Approval Date', 'Expiry Date', 'Service'
    ]
    
    # Save to Excel with formatting
    with pd.ExcelWriter(output_excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='MoH_Referrals', index=False)
        
        # Get the workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['MoH_Referrals']
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 30)  # Cap at 30 characters
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    logging.info(f"Data extracted and saved to: {output_excel_path}")
    logging.info(f"Processed {len(all_patient_data)} files")
    
    return df

def main():
    """Main function to run the extraction"""
    
    # Base path for MoH documents
    BASE_PATH = r"X:\Service Centre\Canadian MOH Approvals\Ontario MOH Approvals\MOH Approval Documents"
    
    print("MoH Letter Data Extraction Tool")
    print("=" * 40)
    
    # Get the folder name from user (expected format: yyyymmdd)
    folder_name = input("Enter the folder name (e.g., 20250611): ").strip()
    
    if not folder_name:
        print("Error: Folder name is required")
        return
    
    # Build the full folder path
    FOLDER_PATH = os.path.join(BASE_PATH, folder_name)
    
    # Set output Excel file path (same base directory)
    OUTPUT_EXCEL_PATH = os.path.join(BASE_PATH, f"moh_referrals_extracted_{folder_name}.xlsx")
    
    # Verify the folder exists
    if not os.path.exists(FOLDER_PATH):
        print(f"Error: Folder '{folder_name}' not found at {BASE_PATH}")
        print("Available folders:")
        try:
            folders = [f for f in os.listdir(BASE_PATH) if os.path.isdir(os.path.join(BASE_PATH, f))]
            for folder in sorted(folders):
                print(f"  - {folder}")
        except:
            print("  Could not list available folders")
        return
    
    print(f"Processing PDFs from: {FOLDER_PATH}")
    print(f"Output will be saved to: {OUTPUT_EXCEL_PATH}")
    print()
    
    # Process the files
    try:
        df = process_moh_letters(FOLDER_PATH, OUTPUT_EXCEL_PATH)
        
        if df is not None:
            print(f"\nExtraction completed successfully!")
            print(f"Results saved to: {OUTPUT_EXCEL_PATH}")
            print(f"\nExtracted data from {len(df)} files")
            print(f"Sample of extracted data:")
            print(df[['Patient Name', 'Health Number', 'Service']].head().to_string(index=False))
        
    except Exception as e:
        logging.error(f"An error occurred during processing: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()