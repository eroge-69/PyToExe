import win32clipboard
import time
import re
import os
from datetime import datetime

def matches_pattern(text):
    """Check if text starts with 'C' and ends with '.jpg'"""
    if not text:
        return False
    
    # Extract just the filename from full path
    filename = os.path.basename(text)
    
    # Check if it starts with 'C' and ends with '.jpg'
    pattern = r'^C.*\.jpg$'
    return re.match(pattern, filename, re.IGNORECASE) is not None

def get_clipboard_file_path():
    try:
        win32clipboard.OpenClipboard()
        # Check for CF_HDROP format, which indicates file drop
        if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_HDROP):
            file_paths = win32clipboard.GetClipboardData(win32clipboard.CF_HDROP)
            return file_paths[0] if file_paths else None # Return the first path if multiple
        return None
    except Exception as e:
        print(f"Error accessing clipboard: {e}")
        return None
    finally:
        win32clipboard.CloseClipboard()

def write_to_file(data, filename="clipboard_data.txt"):
    """Write data to text file with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"{data}\n")
    
    print(f"✓ Saved: {data}")

def monitor_clipboard():
    """Monitor clipboard for file changes and save matching data"""
    print("🔍 Monitoring clipboard for files starting with 'C' and ending with '.jpg'")
    print("📝 Data will be saved to 'clipboard_data.txt'")
    print("⏹️ Press Ctrl+C to stop monitoring\n")
    
    last_file_path = None
    
    try:
        while True:
            try:
                file_path = get_clipboard_file_path()
                
                # Check if file path has changed and matches our pattern
                if file_path and file_path != last_file_path:
                    print(f"📁 Detected file in clipboard: {file_path}")
                    
                    if matches_pattern(file_path):
                        filename = os.path.basename(file_path)
                        write_to_file(filename)
                    else:
                        filename = os.path.basename(file_path)
                        print(f"⏭️ Skipped (doesn't match pattern): {filename}")
                    
                    last_file_path = file_path
                
                # Small delay to avoid excessive CPU usage
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error monitoring clipboard: {e}")
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped.")

if __name__ == "__main__":
    try:
        # Test the function once
        file_name = get_clipboard_file_path()
        if file_name:
            print(f"Clipboard file path: {file_name}")
            if matches_pattern(file_name):
                print(f"✅ Matches pattern: {os.path.basename(file_name)}")
            else:
                print(f"❌ Doesn't match pattern: {os.path.basename(file_name)}")
        else:
            print("No file path found in clipboard.")
        
        print("\nStarting continuous monitoring...")
        monitor_clipboard()
        
    except ImportError:
        print("❌ Error: pywin32 library is not installed.")
        print("📦 Install it with: pip install pywin32")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you have clipboard access permissions.")
