# ===============================================
# 🚀 PDF Splitter - Auto-Detect Files Version
# ===============================================

import pandas as pd
import os
import zipfile
import pdfplumber
from PyPDF2 import PdfWriter, PdfReader
import glob
from datetime import datetime

def find_files():
    """Automatically find Excel and PDF files in current directory"""
    current_dir = os.getcwd()
    
    # Find Excel files
    excel_patterns = ['*.xlsx', '*.xls']
    excel_files = []
    for pattern in excel_patterns:
        excel_files.extend(glob.glob(pattern))
    
    # Find PDF files
    pdf_files = glob.glob('*.pdf')
    
    return excel_files, pdf_files

def main():
    print("🚀 PDF SPLITTER - Auto-Detect Version")
    print("=" * 50)
    print("📁 Looking for files in current folder...")
    
    try:
        # Step 1: Auto-find files
        excel_files, pdf_files = find_files()
        
        # Check Excel files
        if not excel_files:
            print("❌ No Excel files found!")
            print("📋 Please put your Excel file (.xlsx or .xls) in this folder")
            input("Press Enter to exit...")
            return
        elif len(excel_files) > 1:
            print("📊 Multiple Excel files found:")
            for i, file in enumerate(excel_files, 1):
                print(f"   {i}. {file}")
            excel_file = excel_files[0]  # Use first one
            print(f"✅ Using: {excel_file}")
        else:
            excel_file = excel_files[0]
            print(f"✅ Found Excel: {excel_file}")
        
        # Check PDF files
        if not pdf_files:
            print("❌ No PDF files found!")
            print("📄 Please put your PDF file in this folder")
            input("Press Enter to exit...")
            return
        elif len(pdf_files) > 1:
            print("📄 Multiple PDF files found:")
            for i, file in enumerate(pdf_files, 1):
                print(f"   {i}. {file}")
            pdf_file = pdf_files[0]  # Use first one
            print(f"✅ Using: {pdf_file}")
        else:
            pdf_file = pdf_files[0]
            print(f"✅ Found PDF: {pdf_file}")
        
        # Step 2: Load broker routes
        print("\n🔄 Loading broker routes...")
        df = pd.read_excel(excel_file, header=None)
        broker_routes = {}
        
        for _, row in df.iterrows():
            if pd.notnull(row[0]):
                broker = str(row[0]).strip()
                routes = [str(item).strip() for item in row[1:] if pd.notnull(item)]
                routes = [r for r in routes if not r.replace('.', '').isdigit()]
                if routes:
                    broker_routes[broker] = routes
        
        print(f"✅ Loaded {len(broker_routes)} brokers with routes")
        
        # Step 3: Process PDF
        print("\n⚡ Processing PDF... Please wait...")
        
        # Create timestamped output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f'split_pdfs_{timestamp}'
        os.makedirs(output_dir, exist_ok=True)
        
        total_created = 0
        
        with pdfplumber.open(pdf_file) as pdf_reader, open(pdf_file, 'rb') as f:
            pdf_writer_source = PdfReader(f)
            total_pages = len(pdf_writer_source.pages)
            print(f"📖 Total pages in PDF: {total_pages}")
            
            for broker_num, (broker, routes) in enumerate(broker_routes.items(), 1):
                print(f"🔄 Processing broker {broker_num}/{len(broker_routes)}: {broker}")
                
                # Clean broker name for folder
                safe_broker = "".join(c for c in broker if c.isalnum() or c in (' ', '_', '-')).strip()
                broker_folder = os.path.join(output_dir, safe_broker)
                os.makedirs(broker_folder, exist_ok=True)
                
                for route in routes:
                    writer = PdfWriter()
                    found_pages = 0
                    
                    # Scan pages for route matches
                    for page_num, page in enumerate(pdf_reader.pages):
                        text = page.extract_text() or ""
                        if route in text:
                            writer.add_page(pdf_writer_source.pages[page_num])
                            found_pages += 1
                    
                    # Save if pages found
                    if found_pages > 0:
                        safe_route = "".join(c for c in route if c.isalnum() or c in (' ', '_', '-')).strip()
                        output_path = os.path.join(broker_folder, f"{safe_route}.pdf")
                        
                        with open(output_path, 'wb') as output_file:
                            writer.write(output_file)
                        
                        print(f"  ✅ {route}: {found_pages} pages")
                        total_created += 1
                    else:
                        print(f"  ⚠️ {route}: No pages found")
        
        # Step 4: Create ZIP file
        print(f"\n📦 Creating ZIP file... ({total_created} PDFs created)")
        
        zip_name = f'Broker_PDFs_{timestamp}.zip'
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files_list in os.walk(output_dir):
                for file in files_list:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, output_dir)
                    zipf.write(file_path, arcname)
        
        print(f"\n🎯 SUCCESS!")
        print(f"✅ Created: {zip_name}")
        print(f"📁 Individual PDFs in: {output_dir}")
        print(f"📊 Total files created: {total_created}")
        print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        print(error_msg)
    
    print("\n" + "=" * 50)
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()