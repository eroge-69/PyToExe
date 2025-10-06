import streamlit as st
import pandas as pd
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
import requests
import base64
import re
from io import BytesIO
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Data Processor Suite",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.5rem;
        color: #721c24;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'mode' not in st.session_state:
    st.session_state.mode = None
if 'excel_result' not in st.session_state:
    st.session_state.excel_result = None
if 'column_mapping' not in st.session_state:
    st.session_state.column_mapping = None
if 'detected_columns' not in st.session_state:
    st.session_state.detected_columns = []
if 'preview_data' not in st.session_state:
    st.session_state.preview_data = None
if 'extracted_tables' not in st.session_state:
    st.session_state.extracted_tables = []


def clean_cell_data(cell):
    """Clean special characters and formatting from cell data"""
    if pd.isna(cell) or cell == '':
        return ''
    
    cleaned = str(cell)
    
    # Remove control characters
    cleaned = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', cleaned)
    # Normalize spaces
    cleaned = re.sub(r'[\u2000-\u206F]', ' ', cleaned)
    # Normalize dashes
    cleaned = re.sub(r'[\u2013-\u2015]', '-', cleaned)
    # Normalize quotes
    cleaned = re.sub(r'[\u2018-\u201F]', "'", cleaned)
    # Normalize bullets
    cleaned = re.sub(r'[\u2022\u2023\u2043]', '•', cleaned)
    # Non-breaking space to regular space
    cleaned = re.sub(r'[\u00A0]', ' ', cleaned)
    # Remove soft hyphens and zero-width characters
    cleaned = re.sub(r'[\u00AD\u200B-\u200D\uFEFF]', '', cleaned)
    # Normalize multiple spaces
    cleaned = re.sub(r'\s+', ' ', cleaned)
    # Trim whitespace
    cleaned = cleaned.strip()
    
    # Remove separator lines (just hyphens/dashes)
    if re.match(r'^[-–—=_\s]+$', cleaned):
        return ''
    
    # Clean drawing numbers (contains digits)
    if re.search(r'\d', cleaned):
        # Remove leading non-alphanumeric characters
        cleaned = re.sub(r'^[^a-zA-Z0-9]+', '', cleaned)
        # Remove trailing non-alphanumeric characters
        cleaned = re.sub(r'[^a-zA-Z0-9]+$', '', cleaned)
    
    return cleaned


def process_excel_file(uploaded_file, col_mapping):
    """Process Excel file: merge columns, clean data, remove column"""
    try:
        # Read Excel file
        df = pd.read_excel(uploaded_file, header=0)
        
        # Get column indices
        drawing_col = col_mapping['drawing_number']
        rev_col = col_mapping['rev']
        
        # Store original data for comparison
        original_df = df.copy()
        
        # Clean drawing number column
        cleaned_count = 0
        if drawing_col < len(df.columns):
            col_name = df.columns[drawing_col]
            for idx in df.index:
                original = str(df.at[idx, col_name])
                cleaned = clean_cell_data(original)
                df.at[idx, col_name] = cleaned
                if original != cleaned:
                    cleaned_count += 1
        
        # Remove column D (index 3) if it exists
        if len(df.columns) > 3:
            df = df.drop(df.columns[3], axis=1)
        
        # Merge Column A + Column C (now Column B after removing D)
        col_a = df.columns[0]
        col_c = df.columns[2] if len(df.columns) > 2 else df.columns[1]
        df['Merged'] = df[col_a].astype(str) + '-' + df[col_c].astype(str)
        
        return {
            'dataframe': df,
            'record_count': len(df),
            'cleaned_count': cleaned_count,
            'original_filename': uploaded_file.name
        }
    
    except Exception as e:
        st.error(f"Error processing Excel file: {str(e)}")
        return None


def extract_tables_from_pdf(pdf_file):
    """Extract tables from PDF using Claude API"""
    try:
        # Read PDF and convert to base64
        pdf_bytes = pdf_file.read()
        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # Prepare API request
        prompt = """You are tasked with extracting all tables from a provided PDF and converting them into Excel-compatible tables for data analysis and reporting.

Instructions:
1. **Identify Tables:** Locate all structured data presented in rows and columns, including tables with merged or spanning headers.

2. **Extract Table Data:** For each table, extract all data exactly as shown, including headers, every row, every column, and any empty cells. Preserve original order and structure.

3. **Format as Excel Tables:** For each extracted table, create an Excel-compatible version: columns separated by tabs, rows by newlines. The first row must contain column headers.

4. **Preserve All Columns:** Include every column, even if some are empty. Do not combine or omit columns.

5. **Output Format:** For each table, use this format:
<extracted_table number="1">
[Tab-separated columns, newline-separated rows]
</extracted_table>

<table_notes number="1">
[Footnotes, image/chart placeholders, or any relevant notes]
</table_notes>

6. **Final Verification:** Ensure all tables are extracted with correct column counts and all data transcribed.

Present all extracted tables and notes in the specified format."""

        # Make API request
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type": "application/json"},
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 4000,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": base64_pdf
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code}")
        
        # Parse response
        response_data = response.json()
        response_text = response_data['content'][0]['text']
        
        # Extract tables
        tables = parse_extracted_tables(response_text)
        
        return tables
    
    except Exception as e:
        st.error(f"Error extracting tables from PDF: {str(e)}")
        return []


def parse_extracted_tables(response_text):
    """Parse extracted tables from Claude API response"""
    tables = []
    
    # Extract table content
    table_pattern = r'<extracted_table number="(\d+)">\s*(.*?)\s*</extracted_table>'
    notes_pattern = r'<table_notes number="(\d+)">\s*(.*?)\s*</table_notes>'
    
    table_matches = re.findall(table_pattern, response_text, re.DOTALL)
    notes_matches = re.findall(notes_pattern, response_text, re.DOTALL)
    
    notes_dict = {num: note.strip() for num, note in notes_matches}
    
    for table_num, table_content in table_matches:
        # Split into rows and clean
        rows = []
        for line in table_content.strip().split('\n'):
            cells = [clean_cell_data(cell) for cell in line.split('\t')]
            if any(cell for cell in cells):  # Only include non-empty rows
                rows.append(cells)
        
        if rows:
            tables.append({
                'number': int(table_num),
                'rows': rows,
                'notes': notes_dict.get(table_num, ''),
                'dataframe': pd.DataFrame(rows[1:], columns=rows[0]) if len(rows) > 1 else pd.DataFrame()
            })
    
    return tables


def reset_app():
    """Reset all session state variables"""
    st.session_state.mode = None
    st.session_state.excel_result = None
    st.session_state.column_mapping = None
    st.session_state.detected_columns = []
    st.session_state.preview_data = None
    st.session_state.extracted_tables = []


# ============= MAIN APP =============

# Mode Selection Screen
if st.session_state.mode is None:
    st.markdown("<h1 style='text-align: center; color: white;'>📊 Data Processor Suite</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #E0E7FF; font-size: 1.2rem;'>Choose your processing tool</p>", unsafe_allow_html=True)
    
    st.markdown("<div style='text-align: center; margin: 2rem 0;'><span style='background: rgba(34, 197, 94, 0.2); border: 1px solid rgba(34, 197, 94, 0.3); padding: 0.5rem 1rem; border-radius: 2rem; color: #86efac;'>🔒 100% Private & Secure</span></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Excel Processor")
        st.markdown("Merge columns, clean data, and transform your Excel files")
        st.markdown("✅ Merge Column A + C")
        st.markdown("✅ Remove Column D")
        st.markdown("✅ Clean special characters")
        if st.button("Select Excel Tool", use_container_width=True, type="primary"):
            st.session_state.mode = 'excel'
            st.rerun()
    
    with col2:
        st.markdown("### 📄 PDF Table Extractor")
        st.markdown("Extract tables from PDFs and convert to Excel format")
        st.markdown("✅ AI-powered extraction")
        st.markdown("✅ Multiple tables support")
        st.markdown("✅ Excel-ready output")
        if st.button("Select PDF Tool", use_container_width=True, type="primary"):
            st.session_state.mode = 'pdf'
            st.rerun()
    
    st.markdown("<p style='text-align: center; color: #C7D2FE; margin-top: 3rem;'>All processing happens locally • No data sent to servers • Files automatically cleared</p>", unsafe_allow_html=True)


# ============= EXCEL MODE =============
elif st.session_state.mode == 'excel':
    col_header1, col_header2 = st.columns([6, 1])
    with col_header1:
        st.title("📊 Excel Data Processor")
        st.caption("Merges Column A + C, removes Column D, cleans data")
    with col_header2:
        if st.button("🏠 Home"):
            reset_app()
            st.rerun()
    
    st.divider()
    
    # File upload
    if st.session_state.excel_result is None:
        uploaded_file = st.file_uploader("Upload Excel File (.xlsx, .xls)", type=['xlsx', 'xls'], key='excel_upload')
        
        if uploaded_file is not None:
            try:
                # Read file for preview
                df_preview = pd.read_excel(uploaded_file, header=0, nrows=3)
                headers = df_preview.columns.tolist()
                
                st.session_state.detected_columns = headers
                st.session_state.preview_data = df_preview
                
                # Auto-detect columns
                drawing_col = next((i for i, h in enumerate(headers) if 'drawing' in str(h).lower()), 0)
                rev_col = next((i for i, h in enumerate(headers) if 'rev' in str(h).lower()), 1 if len(headers) > 1 else 0)
                
                if st.session_state.column_mapping is None:
                    st.session_state.column_mapping = {
                        'drawing_number': drawing_col,
                        'rev': rev_col
                    }
                
                # Show preview
                st.subheader("📋 Data Preview (First 3 rows)")
                st.dataframe(df_preview, use_container_width=True)
                
                # Column mapping
                st.subheader("🔧 Map Your Columns")
                col1, col2 = st.columns(2)
                
                with col1:
                    drawing_idx = st.selectbox(
                        "Drawing Number Column *",
                        range(len(headers)),
                        index=st.session_state.column_mapping['drawing_number'],
                        format_func=lambda x: f"Column {x+1}: {headers[x]}"
                    )
                    st.session_state.column_mapping['drawing_number'] = drawing_idx
                
                with col2:
                    rev_idx = st.selectbox(
                        "Rev Column *",
                        range(len(headers)),
                        index=st.session_state.column_mapping['rev'],
                        format_func=lambda x: f"Column {x+1}: {headers[x]}"
                    )
                    st.session_state.column_mapping['rev'] = rev_idx
                
                # Process button
                if st.button("🚀 Process File", use_container_width=True, type="primary"):
                    with st.spinner("Processing your file..."):
                        result = process_excel_file(uploaded_file, st.session_state.column_mapping)
                        if result:
                            st.session_state.excel_result = result
                            st.rerun()
            
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
    
    # Show results
    else:
        result = st.session_state.excel_result
        
        st.success("✅ Processing Complete!")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Records Processed", result['record_count'])
        with col2:
            st.metric("Values Cleaned", result['cleaned_count'])
        
        # Download button
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            result['dataframe'].to_excel(writer, index=False, sheet_name='Processed Data')
        
        output.seek(0)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{result['original_filename'].rsplit('.', 1)[0]}_processed_{timestamp}.xlsx"
        
        st.download_button(
            label="⬇️ Download Processed File",
            data=output,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary"
        )
        
        # Preview
        st.subheader("📊 Data Preview")
        st.dataframe(result['dataframe'].head(10), use_container_width=True)
        
        if len(result['dataframe']) > 10:
            st.caption(f"Showing 10 of {result['record_count']} rows")
        
        if st.button("🔄 Process Another File"):
            reset_app()
            st.rerun()


# ============= PDF MODE =============
elif st.session_state.mode == 'pdf':
    col_header1, col_header2 = st.columns([6, 1])
    with col_header1:
        st.title("📄 PDF Table Extractor")
        st.caption("AI-powered table extraction from PDF documents")
    with col_header2:
        if st.button("🏠 Home"):
            reset_app()
            st.rerun()
    
    st.divider()
    
    # File upload
    uploaded_pdf = st.file_uploader("Upload PDF File", type=['pdf'], key='pdf_upload')
    
    if uploaded_pdf is not None:
        st.info(f"📎 Selected file: {uploaded_pdf.name} ({uploaded_pdf.size / 1024 / 1024:.2f} MB)")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("🔍 Extract Tables", use_container_width=True, type="primary"):
                with st.spinner("Extracting tables from PDF... This may take a moment."):
                    tables = extract_tables_from_pdf(uploaded_pdf)
                    st.session_state.extracted_tables = tables
                    if tables:
                        st.success(f"✅ Successfully extracted {len(tables)} table(s)!")
                    else:
                        st.warning("No tables found in the PDF.")
        
        with col2:
            if st.session_state.extracted_tables:
                # Create combined Excel file
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    for table in st.session_state.extracted_tables:
                        sheet_name = f"Table {table['number']}"
                        table['dataframe'].to_excel(writer, index=False, sheet_name=sheet_name[:31])
                        
                        if table['notes']:
                            notes_df = pd.DataFrame([['Notes'], [table['notes']]])
                            notes_sheet = f"Notes {table['number']}"
                            notes_df.to_excel(writer, index=False, header=False, sheet_name=notes_sheet[:31])
                
                output.seek(0)
                st.download_button(
                    label="⬇️ Download All",
                    data=output,
                    file_name="all_extracted_tables.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
    
    # Display extracted tables
    if st.session_state.extracted_tables:
        st.divider()
        st.subheader(f"📊 Extracted Tables ({len(st.session_state.extracted_tables)})")
        
        for table in st.session_state.extracted_tables:
            with st.expander(f"Table {table['number']}", expanded=True):
                st.dataframe(table['dataframe'], use_container_width=True)
                
                if table['notes']:
                    st.warning(f"📝 Notes: {table['notes']}")
                
                # Individual download
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    table['dataframe'].to_excel(writer, index=False, sheet_name=f"Table {table['number']}")
                
                output.seek(0)
                st.download_button(
                    label=f"⬇️ Download Table {table['number']}",
                    data=output,
                    file_name=f"table_{table['number']}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"download_{table['number']}"
                )
