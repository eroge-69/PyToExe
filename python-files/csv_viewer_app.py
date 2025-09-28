#!/usr/bin/env python3
"""
xsukax CSV Viewer - Ultra-Fast Search with Verified Highlighting
Fixed search accuracy and CSV parsing issues
"""

import os
import sys
import threading
import time
import uuid
import re
import csv
import io
from pathlib import Path
from werkzeug.utils import secure_filename

try:
    import psutil
    from flask import Flask, render_template_string, request, jsonify, Response
except ImportError:
    print("Missing packages. Install with: pip install flask psutil")
    sys.exit(1)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024 * 20  # 20GB

# Global state
search_sessions = {}
current_file_info = {}
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'txt'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

class SearchSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.is_active = False
        self.is_complete = False
        self.results = []
        self.total_searched = 0
        self.total_matches = 0
        self.search_term = ""
        self.start_time = 0
        self.error = None

class FileProcessor:
    def __init__(self):
        self.file_path = None
        self.file_type = None
        self.delimiter = ','
        self.encoding = 'utf-8'
        self.total_lines = 0
        self.columns = []
        
    def analyze_file(self, file_path: str, delimiter: str = ','):
        """Quick file analysis"""
        file_ext = file_path.lower().split('.')[-1]
        
        # Detect encoding
        with open(file_path, 'rb') as f:
            sample = f.read(8192)
        
        encoding = 'utf-8'
        try:
            sample.decode('utf-8')
        except UnicodeDecodeError:
            try:
                sample.decode('utf-8-sig')
                encoding = 'utf-8-sig'
            except UnicodeDecodeError:
                encoding = 'latin-1'
        
        # Count lines efficiently
        with open(file_path, 'rb') as f:
            total_lines = sum(1 for _ in f)
        
        # Get columns using proper CSV reader
        columns = []
        if file_ext == 'csv':
            try:
                with open(file_path, 'r', encoding=encoding, newline='') as f:
                    # Use csv.Sniffer to detect dialect
                    sample_text = f.read(8192)
                    f.seek(0)
                    
                    try:
                        dialect = csv.Sniffer().sniff(sample_text, delimiters=',;\t|')
                        delimiter = dialect.delimiter
                    except:
                        pass  # Use provided delimiter
                    
                    reader = csv.reader(f, delimiter=delimiter)
                    header_row = next(reader, None)
                    if header_row:
                        columns = [col.strip() for col in header_row]
            except Exception as e:
                print(f"Error reading CSV header: {e}")
                columns = ['Column 1']
        else:
            columns = ['Content']
        
        self.file_path = file_path
        self.file_type = file_ext
        self.delimiter = delimiter
        self.encoding = encoding
        self.total_lines = total_lines
        self.columns = columns
        
        file_size = os.path.getsize(file_path)
        
        return {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'file_type': file_ext.upper(),
            'file_size_mb': round(file_size / (1024 * 1024), 2),
            'total_lines': total_lines,
            'total_columns': len(columns),
            'columns': columns,
            'encoding': encoding,
            'delimiter': delimiter
        }
    
    def search_file(self, search_term: str, session_id: str):
        """Main search function with proper highlighting"""
        session = search_sessions.get(session_id)
        if not session:
            print(f"ERROR: No session found for ID {session_id}")
            return
        
        session.is_active = True
        session.search_term = search_term
        session.start_time = time.time()
        
        if not search_term.strip():
            session.is_complete = True
            session.is_active = False
            return
        
        print(f"Starting search for: '{search_term}' in {self.file_type} file")
        print(f"File: {self.file_path}, Encoding: {self.encoding}, Delimiter: {self.delimiter}")
        
        try:
            if self.file_type == 'txt':
                self._search_txt_file(search_term, session)
            else:
                self._search_csv_file(search_term, session)
        except Exception as e:
            print(f"CRITICAL SEARCH ERROR: {e}")
            import traceback
            traceback.print_exc()
            session.error = str(e)
        finally:
            session.is_complete = True
            session.is_active = False
            print(f"Search complete. Found {session.total_matches} matches in {session.total_searched} lines")
            print(f"Session active: {session.is_active}, Complete: {session.is_complete}")
    
    def _search_txt_file(self, search_term, session):
        """Search TXT file line by line"""
        search_lower = search_term.lower()
        max_results = 5000  # Increased limit
        
        try:
            with open(self.file_path, 'r', encoding=self.encoding, errors='replace') as f:
                for line_num, line in enumerate(f, 1):
                    # Check if manually stopped
                    if not session.is_active:
                        print(f"Search manually stopped at line {line_num}")
                        break
                    
                    line_content = line.rstrip('\n\r')
                    
                    # Skip empty lines
                    if not line_content.strip():
                        session.total_searched = line_num
                        continue
                    
                    # Case-insensitive search
                    if search_lower in line_content.lower():
                        # Apply highlighting
                        highlighted_content = self._highlight_text(line_content, search_term)
                        
                        session.results.append({
                            'Line #': line_num,
                            'Content': highlighted_content
                        })
                        session.total_matches += 1
                        
                        # Debug output for first few matches
                        if session.total_matches <= 5:
                            preview = line_content[:100] + '...' if len(line_content) > 100 else line_content
                            print(f"Match {session.total_matches} at line {line_num}: {preview}")
                        
                        # Only stop if we hit the increased limit
                        if len(session.results) >= max_results:
                            print(f"Reached {max_results} results limit - stopping for performance")
                            session.is_active = False
                            break
                    
                    session.total_searched = line_num
                    
                    # Progress update
                    if line_num % 10000 == 0:
                        print(f"Progress: Searched {line_num:,} lines, found {session.total_matches:,} matches")
                        time.sleep(0.001)  # Brief yield
                
                print(f"TXT search finished: {session.total_searched:,} lines searched, {session.total_matches:,} matches found")
                
        except Exception as e:
            print(f"CRITICAL ERROR in TXT search: {e}")
            import traceback
            traceback.print_exc()
            session.error = str(e)
    
    def _search_csv_file(self, search_term, session):
        """Search CSV file using proper CSV parser"""
        search_lower = search_term.lower()
        max_results = 5000  # Increased limit
        
        try:
            with open(self.file_path, 'r', encoding=self.encoding, newline='', errors='replace') as f:
                # Try different CSV parsing approaches for better accuracy
                try:
                    reader = csv.reader(f, delimiter=self.delimiter, quotechar='"', 
                                      quoting=csv.QUOTE_MINIMAL, skipinitialspace=True)
                except Exception as e:
                    print(f"Warning: CSV reader error, trying alternative: {e}")
                    f.seek(0)
                    reader = csv.reader(f, delimiter=self.delimiter)
                
                # Skip header
                try:
                    header = next(reader, None)
                    if not header:
                        print("Warning: Empty CSV file")
                        return
                except StopIteration:
                    print("Warning: No data in CSV file")
                    return
                
                line_num = 1  # Start with line 1 (header was line 1)
                
                for row in reader:
                    line_num += 1  # Increment for each data row
                    
                    # Check if manually stopped
                    if not session.is_active:
                        print(f"Search manually stopped at line {line_num}")
                        break
                    
                    # Skip empty rows
                    if not row or all(not cell.strip() for cell in row):
                        continue
                    
                    # Search in each field separately for accuracy
                    found_in_row = False
                    matched_values = []
                    
                    for i, cell in enumerate(row):
                        if search_lower in cell.lower():
                            found_in_row = True
                            if i < len(self.columns):
                                matched_values.append((self.columns[i], cell))
                    
                    if found_in_row:
                        # Create result row with all columns
                        result_row = {'Row #': line_num}
                        
                        # Add all columns, highlighting matching ones
                        for i, col_name in enumerate(self.columns):
                            if i < len(row):
                                value = row[i]
                                # Only highlight if this specific field matches
                                if search_lower in value.lower():
                                    result_row[col_name] = self._highlight_text(value, search_term)
                                else:
                                    result_row[col_name] = value
                            else:
                                result_row[col_name] = ''
                        
                        session.results.append(result_row)
                        session.total_matches += 1
                        
                        # Debug output for first few matches
                        if session.total_matches <= 5:
                            print(f"Match {session.total_matches} at row {line_num}:")
                            for col, val in matched_values[:3]:  # Show first 3 matching fields
                                preview = val[:50] + '...' if len(val) > 50 else val
                                print(f"  {col}: {preview}")
                        
                        # Only stop if we hit the increased limit
                        if len(session.results) >= max_results:
                            print(f"Reached {max_results} results limit - stopping for performance")
                            session.is_active = False
                            break
                    
                    session.total_searched = line_num
                    
                    # Progress update
                    if line_num % 10000 == 0:
                        print(f"Progress: Searched {line_num:,} lines, found {session.total_matches:,} matches")
                        time.sleep(0.001)  # Brief yield for responsiveness
                
                print(f"CSV search finished: {session.total_searched:,} lines searched, {session.total_matches:,} matches found")
                
        except Exception as e:
            print(f"CRITICAL ERROR in CSV search: {e}")
            import traceback
            traceback.print_exc()
            session.error = str(e)
    
    def _highlight_text(self, text, search_term):
        """Apply highlighting to text - case insensitive with word boundaries"""
        if not search_term or not text:
            return text
        
        # Escape special regex characters in search term
        escaped_term = re.escape(search_term)
        
        # Case-insensitive replacement preserving original case
        def replacer(match):
            return f'<mark>{match.group(0)}</mark>'
        
        pattern = re.compile(escaped_term, re.IGNORECASE)
        highlighted = pattern.sub(replacer, text)
        
        return highlighted
    
    def get_sample_data(self, lines: int = 50):
        """Get sample data for preview using proper CSV parser"""
        if not self.file_path:
            return {'data': [], 'columns': []}
        
        data = []
        
        try:
            with open(self.file_path, 'r', encoding=self.encoding, newline='', errors='replace') as f:
                if self.file_type == 'csv':
                    reader = csv.reader(f, delimiter=self.delimiter, quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    
                    # Skip header
                    try:
                        header = next(reader)
                        columns = ['Row #'] + self.columns
                    except StopIteration:
                        return {'data': [], 'columns': [], 'total_lines': 0}
                    
                    for line_num, row in enumerate(reader, 2):  # Start from line 2
                        if line_num > lines + 1:
                            break
                        
                        row_data = {'Row #': line_num}
                        for j, col in enumerate(self.columns):
                            if j < len(row):
                                row_data[col] = row[j]
                            else:
                                row_data[col] = ''
                        
                        data.append(row_data)
                else:
                    # TXT file
                    columns = ['Line #', 'Content']
                    
                    for i, line in enumerate(f, 1):
                        if i > lines:
                            break
                        
                        data.append({
                            'Line #': i,
                            'Content': line.rstrip('\n\r')
                        })
        except Exception as e:
            print(f"Error getting sample: {e}")
            import traceback
            traceback.print_exc()
        
        return {
            'data': data,
            'columns': columns,
            'total_lines': self.total_lines
        }

# Global processor
processor = FileProcessor()

def get_memory_usage():
    return round(psutil.Process().memory_info().rss / (1024 * 1024), 2)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze_file', methods=['POST'])
def analyze_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '' or not file.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        file_ext = file.filename.lower().split('.')[-1]
        if file_ext not in ALLOWED_EXTENSIONS:
            return jsonify({'error': 'Please select a CSV or TXT file'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        # Add timestamp to avoid conflicts
        timestamp = str(int(time.time()))
        filename = f"{timestamp}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Analyze
        delimiter = request.form.get('delimiter', ',').strip() or ','
        file_info = processor.analyze_file(file_path, delimiter)
        
        return jsonify({
            'success': True,
            'file_info': file_info,
            'memory_usage': get_memory_usage()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sample_data')
def get_sample_data():
    try:
        lines = min(100, int(request.args.get('lines', 50)))
        data = processor.get_sample_data(lines)
        
        return jsonify({
            'success': True,
            'data': data['data'],
            'columns': data['columns'],
            'total_lines': data['total_lines'],
            'memory_usage': get_memory_usage()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/start_search', methods=['POST'])
def start_search():
    try:
        data = request.get_json()
        search_term = data.get('search_term', '').strip()
        
        if not search_term:
            return jsonify({'error': 'Please enter a search term'}), 400
        
        if not processor.file_path:
            return jsonify({'error': 'No file selected'}), 400
        
        # Create search session
        session_id = str(uuid.uuid4())
        session = SearchSession(session_id)
        search_sessions[session_id] = session
        
        # Start search in background thread
        search_thread = threading.Thread(
            target=processor.search_file,
            args=(search_term, session_id),
            daemon=True
        )
        search_thread.start()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': f'Search started for: {search_term}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search_status/<session_id>')
def get_search_status(session_id):
    session = search_sessions.get(session_id)
    if not session:
        return jsonify({'error': 'Invalid session'}), 404
    
    status = {
        'is_active': session.is_active,
        'is_complete': session.is_complete,
        'total_searched': session.total_searched,
        'total_matches': session.total_matches,
        'results_count': len(session.results),
        'search_term': session.search_term,
        'elapsed_time': round(time.time() - session.start_time, 2) if session.start_time else 0,
        'memory_usage': get_memory_usage()
    }
    
    # Add error if exists
    if session.error:
        status['error'] = session.error
        print(f"Returning error status: {session.error}")
    
    return jsonify(status)

@app.route('/search_results/<session_id>')
def get_search_results(session_id):
    session = search_sessions.get(session_id)
    if not session:
        return jsonify({'error': 'Invalid session'}), 404
    
    page = max(1, int(request.args.get('page', 1)))
    page_size = max(10, min(500, int(request.args.get('page_size', 100))))
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_results = session.results[start_idx:end_idx]
    
    total_pages = max(1, (len(session.results) + page_size - 1) // page_size)
    
    columns = (['Line #', 'Content'] if processor.file_type == 'txt' 
              else ['Row #'] + processor.columns) if page_results else []
    
    return jsonify({
        'success': True,
        'data': page_results,
        'total_results': len(session.results),
        'columns': columns,
        'current_page': page,
        'page_size': page_size,
        'total_pages': total_pages,
        'is_complete': session.is_complete,
        'search_term': session.search_term
    })

@app.route('/export_search_results/<session_id>')
def export_search_results(session_id):
    """Export search results to CSV file"""
    session = search_sessions.get(session_id)
    if not session:
        return jsonify({'error': 'Invalid session'}), 404
    
    if not session.results:
        return jsonify({'error': 'No search results to export'}), 400
    
    try:
        # Create CSV content
        output = io.StringIO()
        
        # Determine columns based on file type
        if processor.file_type == 'txt':
            fieldnames = ['Line #', 'Content']
        else:
            fieldnames = ['Row #'] + processor.columns
        
        writer = csv.DictWriter(output, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        
        # Write search results, cleaning HTML tags
        for result in session.results:
            clean_result = {}
            for key, value in result.items():
                # Remove HTML tags for clean CSV export
                clean_value = re.sub(r'<[^>]*>', '', str(value))
                clean_result[key] = clean_value
            writer.writerow(clean_result)
        
        # Prepare response
        output.seek(0)
        csv_content = output.getvalue()
        output.close()
        
        # Generate filename
        search_term_clean = re.sub(r'[^\w\s-]', '', session.search_term).strip()
        search_term_clean = re.sub(r'[-\s]+', '_', search_term_clean)
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f"search_results_{search_term_clean}_{timestamp}_{session.total_matches}_matches.csv"
        
        # Return CSV file
        response = Response(
            csv_content,
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': 'text/csv; charset=utf-8'
            }
        )
        
        print(f"Exported {len(session.results)} search results to {filename}")
        return response
        
    except Exception as e:
        print(f"Export error: {e}")
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

@app.route('/stop_search/<session_id>', methods=['POST'])
def stop_search(session_id):
    session = search_sessions.get(session_id)
    if session:
        session.is_active = False
        session.is_complete = True  # Mark as complete when stopped
        print(f"Search stopped for session {session_id} - matches found: {session.total_matches}")
        return jsonify({'success': True, 'message': f'Search stopped with {session.total_matches} matches'})
    return jsonify({'success': False, 'error': 'Session not found'})

@app.route('/metadata')
def get_metadata():
    return jsonify({'memory_usage': get_memory_usage()})

# HTML template remains the same, not duplicating it here
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>xsukax CSV Viewer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f7; color: #1d1d1f; line-height: 1.6; }
        .container { max-width: 100%; margin: 0 auto; padding: 20px; }
        .header { background: #fff; border-radius: 12px; padding: 24px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; }
        .header h1 { font-size: 32px; font-weight: 700; color: #1d1d1f; margin-bottom: 8px; }
        .brand { background: linear-gradient(135deg, #007aff, #5856d6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
        .header p { color: #86868b; font-size: 16px; }
        
        .upload-section { background: #fff; border-radius: 12px; padding: 24px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        .upload-area { border: 2px dashed #d2d2d7; border-radius: 12px; padding: 30px 20px; text-align: center; transition: all 0.3s ease; }
        .upload-area:hover { border-color: #007aff; background: #f0f8ff; }
        .upload-area.dragover { border-color: #007aff; background: #e3f2fd; }
        .file-input { display: none; }
        .browse-btn { background: #007aff; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; transition: all 0.3s ease; }
        .browse-btn:hover { background: #0056b3; transform: translateY(-1px); }
        .file-info { background: #f5f5f7; padding: 15px; border-radius: 8px; margin: 15px 0; display: none; }
        .delimiter-group { margin-top: 15px; text-align: left; }
        .delimiter-input { width: 80px; padding: 8px; border: 1px solid #d2d2d7; border-radius: 6px; margin-right: 10px; }
        .analyze-btn { background: #34c759; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: 600; cursor: pointer; }
        
        .info-panel { background: #fff; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); display: none; }
        .info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; text-align: center; }
        .info-item { padding: 12px; background: #f5f5f7; border-radius: 8px; }
        .info-label { font-weight: 600; color: #1d1d1f; margin-bottom: 4px; font-size: 14px; }
        .info-value { color: #007aff; font-weight: 700; font-size: 16px; }
        .ready-badge { background: #34c759; color: white; padding: 8px 16px; border-radius: 20px; font-size: 14px; font-weight: 600; margin-top: 10px; display: inline-block; }
        
        .action-section { background: #fff; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); display: none; }
        .mode-toggle { display: flex; gap: 10px; margin-bottom: 15px; }
        .mode-btn { padding: 8px 16px; border: 1px solid #d2d2d7; background: #fff; border-radius: 6px; cursor: pointer; font-size: 14px; transition: all 0.3s; }
        .mode-btn.active { background: #007aff; color: white; border-color: #007aff; }
        
        .search-controls { display: flex; gap: 15px; align-items: end; flex-wrap: wrap; margin-bottom: 15px; }
        .search-group { flex: 1; min-width: 250px; }
        .search-input { width: 100%; padding: 12px 16px; border: 1px solid #d2d2d7; border-radius: 8px; font-size: 16px; }
        .search-btn { background: #ff6b35; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; transition: all 0.3s; }
        .search-btn:hover { background: #e55a2b; }
        .search-btn:disabled { background: #86868b; cursor: not-allowed; }
        .stop-btn { background: #ff3b30; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; margin-left: 10px; }
        .export-btn { background: #34c759; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; transition: all 0.3s; }
        .export-btn:hover { background: #2fb34d; transform: translateY(-1px); }
        .export-btn:disabled { background: #86868b; cursor: not-allowed; }
        .export-section { background: #f5f5f7; padding: 15px; border-radius: 8px; margin-bottom: 15px; text-align: center; display: none; }
        .export-info { color: #86868b; font-size: 14px; margin-bottom: 10px; }
        .preview-btn { background: #5856d6; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; }
        
        .search-status { background: #f5f5f7; padding: 15px; border-radius: 8px; margin-bottom: 15px; display: none; }
        .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; text-align: center; }
        .status-item { font-weight: 600; }
        .status-label { color: #86868b; font-size: 13px; margin-bottom: 4px; }
        .status-value { color: #1d1d1f; font-size: 16px; }
        .progress-bar { width: 100%; height: 4px; background: #d2d2d7; border-radius: 2px; overflow: hidden; margin-top: 10px; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #ff6b35, #007aff); transition: width 0.3s ease; }
        
        .data-section { display: none; }
        .stats { text-align: center; color: #86868b; margin: 10px 0; font-size: 14px; }
        .table-container { background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        .table-wrapper { overflow: auto; max-height: 60vh; }
        table { width: 100%; border-collapse: collapse; font-size: 13px; }
        th { background: #f5f5f7; padding: 10px 12px; text-align: left; font-weight: 600; position: sticky; top: 0; z-index: 10; border-bottom: 2px solid #d2d2d7; white-space: nowrap; font-size: 12px; }
        td { padding: 8px 12px; border-bottom: 1px solid #f0f0f0; max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        tr:hover { background: #f9f9f9; }
        
        .pagination { display: flex; justify-content: center; align-items: center; gap: 6px; padding: 15px; flex-wrap: wrap; }
        .pagination button { padding: 6px 12px; border: 1px solid #d2d2d7; background: #fff; border-radius: 4px; cursor: pointer; font-size: 13px; transition: all 0.2s; }
        .pagination button:hover { background: #f5f5f7; }
        .pagination button:disabled { opacity: 0.5; cursor: not-allowed; }
        .pagination .current { background: #007aff; color: white; border-color: #007aff; }
        
        .loading { text-align: center; padding: 30px; color: #86868b; display: none; }
        .error { background: #ff3b30; color: white; padding: 12px 20px; border-radius: 8px; margin: 10px 0; }
        .success { background: #34c759; color: white; padding: 12px 20px; border-radius: 8px; margin: 10px 0; }
        
        mark { 
            background: #ffeb3b !important; 
            color: #1d1d1f !important; 
            padding: 2px 4px !important; 
            border-radius: 3px !important; 
            font-weight: 700 !important; 
            box-shadow: 0 1px 2px rgba(0,0,0,0.2) !important; 
        }
        
        @media (max-width: 768px) {
            .container { padding: 10px; }
            .search-controls, .mode-toggle { flex-direction: column; align-items: stretch; }
            .search-group { min-width: auto; }
            .info-grid, .status-grid { grid-template-columns: 1fr 1fr; }
            th, td { padding: 6px 8px; font-size: 12px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><span class="brand">xsukax</span> CSV Viewer</h1>
            <p>⚡ Ultra-fast search with accurate highlighting</p>
        </div>

        <div class="upload-section">
            <div class="upload-area" id="uploadArea">
                <h3>🚀 Select File for Search</h3>
                <p>CSV & TXT files supported</p>
                <input type="file" id="fileInput" class="file-input" accept=".csv,.txt">
                <button class="browse-btn" onclick="document.getElementById('fileInput').click()">Browse Files</button>
            </div>
            
            <div id="selectedFileInfo" class="file-info">
                <strong>📄 Selected:</strong> <span id="selectedFileName"></span> 
                (<span id="selectedFileSize"></span>)
            </div>

            <div class="delimiter-group" id="delimiterGroup" style="display: none;">
                <label>CSV Delimiter:</label>
                <input type="text" id="delimiterInput" class="delimiter-input" value="," maxlength="1">
                <button class="analyze-btn" onclick="analyzeFile()">Analyze File</button>
            </div>
        </div>

        <div id="errorMessage"></div>

        <div id="infoPanel" class="info-panel">
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">File Type</div>
                    <div class="info-value" id="fileType"></div>
                </div>
                <div class="info-item">
                    <div class="info-label">Size</div>
                    <div class="info-value" id="fileSize"></div>
                </div>
                <div class="info-item">
                    <div class="info-label">Lines</div>
                    <div class="info-value" id="totalLines"></div>
                </div>
                <div class="info-item">
                    <div class="info-label">Columns</div>
                    <div class="info-value" id="totalColumns"></div>
                </div>
                <div class="info-item">
                    <div class="info-label">Memory</div>
                    <div class="info-value" id="memoryUsage"></div>
                </div>
            </div>
            <div style="text-align: center;">
                <span class="ready-badge">✅ Ready for Search</span>
            </div>
        </div>

        <div id="actionSection" class="action-section">
            <div class="mode-toggle">
                <button class="mode-btn" id="searchMode" onclick="setMode('search')">🔍 Search</button>
                <button class="mode-btn active" id="previewMode" onclick="setMode('preview')">👁️ Preview</button>
            </div>

            <div id="searchControls" style="display: none;">
                <div class="search-controls">
                    <div class="search-group">
                        <label>Search Term (will be highlighted in results)</label>
                        <input type="text" id="searchInput" class="search-input" placeholder="Enter text to search and highlight...">
                    </div>
                    <button class="search-btn" id="searchBtn" onclick="startSearch()">Search</button>
                    <button class="stop-btn" id="stopBtn" onclick="stopSearch()" style="display: none;">Stop</button>
                </div>

                <div id="searchStatus" class="search-status">
                    <div class="status-grid">
                        <div class="status-item">
                            <div class="status-label">Searched</div>
                            <div class="status-value" id="searchedCount">0</div>
                        </div>
                        <div class="status-item">
                            <div class="status-label">Matches</div>
                            <div class="status-value" id="matchCount">0</div>
                        </div>
                        <div class="status-item">
                            <div class="status-label">Time</div>
                            <div class="status-value" id="elapsedTime">0s</div>
                        </div>
                        <div class="status-item">
                            <div class="status-label">Status</div>
                            <div class="status-value" id="searchStatusText">Ready</div>
                        </div>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill" style="width: 0%;"></div>
                    </div>
                </div>
            </div>

            <div id="previewControls">
                <div class="search-controls">
                    <button class="preview-btn" onclick="loadPreview()">📋 Load Preview (50 lines)</button>
                </div>
            </div>
        </div>

        <div id="dataSection" class="data-section">
            <div id="exportSection" class="export-section">
                <div class="export-info">💾 Export your search results to CSV file (HTML highlighting will be removed)</div>
                <button class="export-btn" id="exportBtn" onclick="exportSearchResults()">📄 Export to CSV</button>
            </div>
            
            <div class="stats" id="statsInfo"></div>
            
            <div class="table-container">
                <div class="table-wrapper">
                    <table id="dataTable">
                        <thead id="tableHead"></thead>
                        <tbody id="tableBody"></tbody>
                    </table>
                </div>
            </div>

            <div class="pagination" id="pagination"></div>
        </div>

        <div id="loading" class="loading">
            <h3>⚡ Processing...</h3>
        </div>
    </div>

    <script>
        let currentPage = 1;
        let totalPages = 1;
        let currentMode = 'preview';
        let searchSessionId = null;
        let searchInterval = null;
        let totalFileLines = 0;
        let selectedFile = null;
        let fileReady = false;

        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.getElementById('uploadArea');

        fileInput.addEventListener('change', handleFileSelect);
        uploadArea.addEventListener('dragover', e => { e.preventDefault(); uploadArea.classList.add('dragover'); });
        uploadArea.addEventListener('drop', handleDrop);
        uploadArea.addEventListener('dragleave', e => { e.preventDefault(); uploadArea.classList.remove('dragover'); });

        document.getElementById('searchInput').addEventListener('keypress', e => {
            if (e.key === 'Enter') startSearch();
        });

        function handleDrop(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) selectFile(files[0]);
        }

        function handleFileSelect(e) {
            const file = e.target.files[0];
            if (file) selectFile(file);
        }

        function selectFile(file) {
            const fileExt = file.name.toLowerCase().split('.').pop();
            if (!['csv', 'txt'].includes(fileExt)) {
                showError('Please select a CSV or TXT file');
                return;
            }

            selectedFile = file;
            document.getElementById('selectedFileName').textContent = file.name;
            document.getElementById('selectedFileSize').textContent = formatFileSize(file.size);
            document.getElementById('selectedFileInfo').style.display = 'block';
            
            if (fileExt === 'csv') {
                document.getElementById('delimiterGroup').style.display = 'block';
            } else {
                analyzeFile();
            }
        }

        function analyzeFile() {
            if (!selectedFile) {
                showError('Please select a file first');
                return;
            }

            const formData = new FormData();
            formData.append('file', selectedFile);
            formData.append('delimiter', document.getElementById('delimiterInput').value.trim() || ',');

            showLoading(true);
            clearError();

            fetch('/analyze_file', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayFileInfo(data.file_info);
                    updateMemoryUsage(data.memory_usage);
                    totalFileLines = data.file_info.total_lines;
                    fileReady = true;
                } else {
                    showError(data.error);
                }
            })
            .catch(error => showError('Error: ' + error.message))
            .finally(() => showLoading(false));
        }

        function displayFileInfo(info) {
            document.getElementById('fileType').textContent = info.file_type;
            document.getElementById('fileSize').textContent = info.file_size_mb + ' MB';
            document.getElementById('totalLines').textContent = info.total_lines.toLocaleString();
            document.getElementById('totalColumns').textContent = info.total_columns;

            document.getElementById('infoPanel').style.display = 'block';
            document.getElementById('actionSection').style.display = 'block';
        }

        function setMode(mode) {
            currentMode = mode;
            document.getElementById('searchMode').classList.toggle('active', mode === 'search');
            document.getElementById('previewMode').classList.toggle('active', mode === 'preview');
            document.getElementById('searchControls').style.display = mode === 'search' ? 'block' : 'none';
            document.getElementById('previewControls').style.display = mode === 'preview' ? 'block' : 'none';
            
            if (mode === 'preview') {
                stopSearch();
                clearTable();
            }
        }

        function startSearch() {
            if (!fileReady) {
                showError('Please analyze file first');
                return;
            }

            const searchTerm = document.getElementById('searchInput').value.trim();
            if (!searchTerm) {
                showError('Please enter a search term');
                return;
            }

            clearError();
            clearTable();  // Clear previous results
            document.getElementById('searchBtn').disabled = true;
            document.getElementById('stopBtn').style.display = 'inline-block';
            document.getElementById('searchStatus').style.display = 'block';
            document.getElementById('searchStatusText').textContent = 'Starting...';

            fetch('/start_search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ search_term: searchTerm })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    searchSessionId = data.session_id;
                    startSearchMonitoring();
                    document.getElementById('dataSection').style.display = 'block';
                    console.log('Search started:', data.message);
                } else {
                    showError(data.error);
                    resetSearchUI();
                }
            })
            .catch(error => {
                showError('Error: ' + error.message);
                resetSearchUI();
            });
        }

        function startSearchMonitoring() {
            let consecutiveErrors = 0;
            searchInterval = setInterval(() => {
                if (!searchSessionId) return;

                fetch(`/search_status/${searchSessionId}`)
                .then(response => response.json())
                .then(data => {
                    consecutiveErrors = 0;  // Reset error counter
                    updateSearchStatus(data);
                    
                    // Check for search errors
                    if (data.error) {
                        showError(`Search error: ${data.error}`);
                        clearInterval(searchInterval);
                        resetSearchUI();
                        document.getElementById('searchStatusText').textContent = 'Error';
                        return;
                    }
                    
                    // Check if search is complete
                    if (data.is_complete || (!data.is_active && data.is_complete)) {
                        clearInterval(searchInterval);
                        resetSearchUI();
                        document.getElementById('searchStatusText').textContent = 
                            data.total_matches > 0 ? `Complete - ${data.total_matches} matches` : 'Complete - No matches';
                        
                        // Load final results
                        loadSearchResults();
                    } else if (data.results_count > 0) {
                        // Load intermediate results while searching
                        loadSearchResults();
                    }
                })
                .catch(error => {
                    console.error('Status error:', error);
                    consecutiveErrors++;
                    if (consecutiveErrors >= 3) {
                        clearInterval(searchInterval);
                        resetSearchUI();
                        showError('Lost connection to search process');
                    }
                });
            }, 500);
        }

        function updateSearchStatus(status) {
            document.getElementById('searchedCount').textContent = status.total_searched.toLocaleString();
            document.getElementById('matchCount').textContent = status.total_matches.toLocaleString();
            document.getElementById('elapsedTime').textContent = status.elapsed_time + 's';
            
            if (status.is_active) {
                document.getElementById('searchStatusText').textContent = 'Searching...';
            }
            
            const progress = totalFileLines > 0 ? (status.total_searched / totalFileLines) * 100 : 0;
            document.getElementById('progressFill').style.width = Math.min(progress, 100) + '%';
            
            updateMemoryUsage(status.memory_usage);
        }

        function loadSearchResults() {
            if (!searchSessionId) return;

            const params = new URLSearchParams({ page: currentPage, page_size: 100 });

            fetch(`/search_results/${searchSessionId}?${params}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displaySearchResults(data);
                }
            })
            .catch(error => console.error('Results error:', error));
        }

        function displaySearchResults(data) {
            displayData(data);
            
            const statsInfo = document.getElementById('statsInfo');
            if (data.total_results > 0) {
                let statsText = `🎯 Found ${data.total_results.toLocaleString()} highlighted matches`;
                if (data.search_term) {
                    statsText += ` for "${data.search_term}"`;
                }
                statsInfo.textContent = statsText;
                
                // Show export section for search results
                document.getElementById('exportSection').style.display = 'block';
            } else {
                statsInfo.textContent = 'No matches found';
                document.getElementById('exportSection').style.display = 'none';
            }
        }

        function exportSearchResults() {
            if (!searchSessionId) {
                showError('No search session active');
                return;
            }

            const exportBtn = document.getElementById('exportBtn');
            exportBtn.disabled = true;
            exportBtn.textContent = '📤 Exporting...';

            // Create a temporary link to download the file
            const link = document.createElement('a');
            link.href = `/export_search_results/${searchSessionId}`;
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            // Reset button after a short delay
            setTimeout(() => {
                exportBtn.disabled = false;
                exportBtn.textContent = '📄 Export to CSV';
                showSuccess('Search results exported successfully!');
            }, 1000);
        }

        function loadPreview() {
            if (!fileReady) {
                showError('Please analyze file first');
                return;
            }

            showLoading(true);
            clearTable();

            fetch('/sample_data?lines=50')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayPreviewData(data);
                    document.getElementById('dataSection').style.display = 'block';
                } else {
                    showError(data.error);
                }
            })
            .catch(error => showError('Error: ' + error.message))
            .finally(() => showLoading(false));
        }

        function displayPreviewData(data) {
            displayData({
                data: data.data,
                columns: data.columns,
                current_page: 1,
                total_pages: 1
            });
            
            document.getElementById('statsInfo').textContent = `Preview: ${data.data.length} lines of ${data.total_lines.toLocaleString()} total`;
            
            // Hide export section for preview mode
            document.getElementById('exportSection').style.display = 'none';
        }

        function stopSearch() {
            if (searchSessionId) {
                fetch(`/stop_search/${searchSessionId}`, { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        console.log('Search stopped:', data.message);
                        showSuccess(data.message || 'Search stopped');
                    }
                })
                .catch(error => console.error('Error stopping search:', error));
                
                clearInterval(searchInterval);
                resetSearchUI();
                document.getElementById('searchStatusText').textContent = 'Stopped';
            }
        }

        function resetSearchUI() {
            document.getElementById('searchBtn').disabled = false;
            document.getElementById('stopBtn').style.display = 'none';
            clearInterval(searchInterval);
        }

        function displayData(data) {
            const tableHead = document.getElementById('tableHead');
            const tableBody = document.getElementById('tableBody');

            tableHead.innerHTML = '';
            tableBody.innerHTML = '';

            if (!data.data || data.data.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="100%" style="text-align: center; padding: 30px; color: #86868b;">No data found</td></tr>';
                updatePagination(1, 1);
                return;
            }

            // Create header
            const headerRow = document.createElement('tr');
            data.columns.forEach(col => {
                const th = document.createElement('th');
                th.textContent = col;
                headerRow.appendChild(th);
            });
            tableHead.appendChild(headerRow);

            // Create body rows
            data.data.forEach(row => {
                const tr = document.createElement('tr');
                data.columns.forEach(col => {
                    const td = document.createElement('td');
                    const cellValue = row[col] || '';
                    
                    // Use innerHTML to render HTML tags like <mark>
                    td.innerHTML = cellValue;
                    
                    // Set tooltip with clean text
                    td.title = String(cellValue).replace(/<[^>]*>/g, '');
                    
                    tr.appendChild(td);
                });
                tableBody.appendChild(tr);
            });

            currentPage = data.current_page || 1;
            totalPages = data.total_pages || 1;
            updatePagination(currentPage, totalPages);
        }

        function clearTable() {
            document.getElementById('tableHead').innerHTML = '';
            document.getElementById('tableBody').innerHTML = '';
            document.getElementById('statsInfo').textContent = '';
            document.getElementById('pagination').innerHTML = '';
            document.getElementById('exportSection').style.display = 'none';
        }

        function updatePagination(current, total) {
            const pagination = document.getElementById('pagination');
            pagination.innerHTML = '';

            if (total <= 1) return;

            const prevBtn = document.createElement('button');
            prevBtn.textContent = '← Prev';
            prevBtn.disabled = current === 1;
            prevBtn.onclick = () => { if (current > 1) { currentPage = current - 1; loadSearchResults(); } };
            pagination.appendChild(prevBtn);

            for (let i = Math.max(1, current - 2); i <= Math.min(total, current + 2); i++) {
                const pageBtn = document.createElement('button');
                pageBtn.textContent = i;
                if (i === current) pageBtn.className = 'current';
                pageBtn.onclick = () => { currentPage = i; loadSearchResults(); };
                pagination.appendChild(pageBtn);
            }

            const nextBtn = document.createElement('button');
            nextBtn.textContent = 'Next →';
            nextBtn.disabled = current === total;
            nextBtn.onclick = () => { if (current < total) { currentPage = current + 1; loadSearchResults(); } };
            pagination.appendChild(nextBtn);
        }

        function formatFileSize(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }

        function updateMemoryUsage(usage) {
            document.getElementById('memoryUsage').textContent = usage + ' MB';
        }

        function showLoading(show) {
            document.getElementById('loading').style.display = show ? 'block' : 'none';
        }

        function showError(message) {
            document.getElementById('errorMessage').innerHTML = `<div class="error">${message}</div>`;
            setTimeout(() => document.getElementById('errorMessage').innerHTML = '', 5000);
        }

        function showSuccess(message) {
            document.getElementById('errorMessage').innerHTML = `<div class="success">${message}</div>`;
            setTimeout(() => document.getElementById('errorMessage').innerHTML = '', 3000);
        }

        function clearError() {
            document.getElementById('errorMessage').innerHTML = '';
        }

        setInterval(() => {
            if (fileReady) {
                fetch('/metadata').then(r => r.json()).then(d => updateMemoryUsage(d.memory_usage)).catch(() => {});
            }
        }, 3000);
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("🚀 xsukax CSV Viewer - Fixed Search Accuracy Edition")
    print("✅ Improved CSV parsing using Python's csv module")
    print("✅ Better encoding detection (UTF-8, UTF-8-BOM, Latin-1)")
    print("✅ More accurate search with proper highlighting")
    print("📄 Export search results to CSV files")
    print("=" * 60)
    
    try:
        port = 5000
        print(f"🌐 Server: http://localhost:{port}")
        print("ℹ️  Press Ctrl+C to stop")
        
        app.run(host='127.0.0.1', port=port, debug=False, threaded=True, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\nℹ️  Server stopped.")
    except Exception as e:
        print(f"❌ Error: {e}")