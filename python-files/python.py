import requests
from datetime import datetime
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

def create_session():
    session = requests.Session()
    
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    session.verify = True
    session.timeout = 30
    
    # Disable chunked encoding to avoid InvalidChunkLength errors
    session.headers.update({
        'Connection': 'close',
        'Content-Length': '0'
    })
    
    return session

def login_authorization(username, password, session_id=None):
    url = 'https://ts.cubesofttech.com/authorization'
    
    data = {
        'username': username,
        'password': password
    }
    
    # Calculate content length for the form data
    data_string = '&'.join([f'{k}={v}' for k, v in data.items()])
    content_length = len(data_string.encode('utf-8'))
    
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': str(content_length),
        'Origin': 'https://ts.cubesofttech.com',
        'Referer': 'https://ts.cubesofttech.com/logout',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'Connection': 'close'
    }
    
    if session_id:
        headers['Cookie'] = f'JSESSIONID={session_id}; cooksc=sc'
    
    session = create_session()
    
    try:
        print(f"Attempting login for user: {username}")
        
        # Use stream=False to avoid chunked encoding issues
        response = session.post(
            url, 
            headers=headers, 
            data=data, 
            timeout=30,
            stream=False,
            allow_redirects=False
        )
        
        print(f"Login response status: {response.status_code}")
        if response.status_code in [302, 301]:
            print("Login redirect detected (likely successful)")
        return response
        
    except requests.exceptions.Timeout:
        print("Error: Request timed out")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"Error: Connection error - {e}")
        return None
    except requests.exceptions.SSLError as e:
        print(f"Error: SSL error - {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error during login: {e}")
        return None
    finally:
        session.close()

def save_check_in_out(work_time, work_date, work_type, latitude, longitude, 
                      session_id, description=""):
    url = 'https://ts.cubesofttech.com/save-check'
    
    data = {
        'work_hours_time_work': work_time,
        'work_hours_date_work': work_date,
        'work_hours_type': str(work_type),
        'description': description,
        'savebtn': '',
        'latitude': str(latitude),
        'longitude': str(longitude)
    }
    
    # Calculate content length for the form data
    data_string = '&'.join([f'{k}={v}' for k, v in data.items()])
    content_length = len(data_string.encode('utf-8'))
    
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': str(content_length),
        'Origin': 'https://ts.cubesofttech.com',
        'Referer': 'https://ts.cubesofttech.com/check_in.action?userId=',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'Cookie': f'JSESSIONID={session_id}; cooksc=sc',
        'Connection': 'close'
    }
    
    session = create_session()
    
    try:
        print(f"Attempting to save check-{'in' if work_type == 1 else 'out'}")
        
        # Use stream=False to avoid chunked encoding issues
        response = session.post(
            url, 
            headers=headers, 
            data=data, 
            timeout=30,
            stream=False,
            allow_redirects=False
        )
        
        print(f"Save response status: {response.status_code}")
        return response
        
    except requests.exceptions.Timeout:
        print("Error: Request timed out")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"Error: Connection error - {e}")
        return None
    except requests.exceptions.SSLError as e:
        print(f"Error: SSL error - {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error during check-in/out: {e}")
        return None
    finally:
        session.close()

def test_connection():
    test_url = 'https://ts.cubesofttech.com'
    session = create_session()
    
    try:
        print("Testing connection to server...")
        response = session.get(test_url, timeout=10)
        print(f"Connection test status: {response.status_code}")
        return response.status_code == 200
    except requests.exceptions.Timeout:
        print("Error: Connection test timed out")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"Error: Cannot connect to server - {e}")
        return False
    except requests.exceptions.SSLError as e:
        print(f"Error: SSL connection failed - {e}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Error during connection test: {e}")
        return False
    finally:
        session.close()

def get_current_date():
    return datetime.now().strftime("%d-%m-%Y")

def read_credentials(file_path="credential.txt"):
    credentials = {}
    
    try:
        if not os.path.exists(file_path):
            print(f"Credential file '{file_path}' not found!")
            return None
        
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                
                if not line or line.startswith('#'):
                    continue
                
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if key in ['latitude', 'longitude']:
                        try:
                            credentials[key] = float(value)
                        except ValueError:
                            print(f"Warning: Invalid {key} value on line {line_num}: {value}")
                            continue
                    else:
                        credentials[key] = value
                else:
                    print(f"Warning: Invalid format on line {line_num}: {line}")
        
        required_fields = ['username', 'password', 'latitude', 'longitude', 'checkin_time', 'checkout_time']
        missing_fields = [field for field in required_fields if field not in credentials]
        
        if missing_fields:
            print(f"Error: Missing required fields in credential file: {', '.join(missing_fields)}")
            return None
        
        return credentials
        
    except Exception as e:
        print(f"Error reading credential file: {e}")
        return None

def create_sample_credential_file(file_path="credential.txt"):
    sample_content = """# Time Tracking System Credentials
# Format: key=value (no spaces around =)

# Login credentials
username=your_username_here
password=your_password_here

# GPS coordinates for check-in/out location
latitude=13.624941382060221
longitude=100.50107354434105

# Desired check-in and check-out times (24-hour format)
checkin_time=09:00
checkout_time=17:30

# Optional: You can add comments using # at the beginning of a line
"""
    
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(sample_content)
        print(f"Sample credential file created: {file_path}")
        print("Please edit the file with your actual credentials!")
    except Exception as e:
        print(f"Error creating credential file: {e}")

def scheduled_check_in(credential_file="credential.txt"):
    creds = read_credentials(credential_file)
    if not creds:
        return False
    
    return check_in(
        username=creds['username'],
        password=creds['password'],
        latitude=creds['latitude'],
        longitude=creds['longitude']
    )

def scheduled_check_out(credential_file="credential.txt"):
    creds = read_credentials(credential_file)
    if not creds:
        return False
    
    return check_out(
        username=creds['username'],
        password=creds['password'],
        latitude=creds['latitude'],
        longitude=creds['longitude']
    )

def check_in(username, password, latitude, longitude, session_id=None):
    if not test_connection():
        print("Cannot establish connection to server")
        return False
        
    if not session_id:
        login_response = login_authorization(username, password)
        if not login_response:
            print("Login failed - no response")
            return False
            
        # Accept both 200 (success) and 302 (redirect) as successful login
        if login_response.status_code not in [200, 302, 301]:
            print(f"Login failed - status code: {login_response.status_code}")
            return False
        
        session_id = login_response.cookies.get('JSESSIONID')
        if not session_id:
            print("Failed to get session ID")
            return False
        print(f"Session ID obtained: {session_id[:10]}...")
    
    current_time = datetime.now().strftime("%H:%M")
    current_date = get_current_date()
    
    check_response = save_check_in_out(
        work_time=f"0:{current_time.split(':')[1]}",
        work_date=current_date,
        work_type=1,
        latitude=latitude,
        longitude=longitude,
        session_id=session_id
    )
    
    if check_response and check_response.status_code in [200, 302, 301]:
        print("Check-in successful")
        return True
    else:
        print("Check-in failed")
        return False

def check_out(username, password, latitude, longitude, session_id=None):
    if not test_connection():
        print("Cannot establish connection to server")
        return False
        
    if not session_id:
        login_response = login_authorization(username, password)
        if not login_response:
            print("Login failed - no response")
            return False
            
        # Accept both 200 (success) and 302 (redirect) as successful login
        if login_response.status_code not in [200, 302, 301]:
            print(f"Login failed - status code: {login_response.status_code}")
            return False
        
        session_id = login_response.cookies.get('JSESSIONID')
        if not session_id:
            print("Failed to get session ID")
            return False
        print(f"Session ID obtained: {session_id[:10]}...")
    
    current_time = datetime.now().strftime("%H:%M")
    current_date = get_current_date()
    
    check_response = save_check_in_out(
        work_time=f"0:{current_time.split(':')[1]}",
        work_date=current_date,
        work_type=2,
        latitude=latitude,
        longitude=longitude,
        session_id=session_id
    )
    
    if check_response and check_response.status_code in [200, 302, 301]:
        print("Check-out successful")
        return True
    else:
        print("Check-out failed")
        return False

if __name__ == "__main__":
    if not os.path.exists("credential.txt"):
        print("Credential file not found. Creating sample file...")
        create_sample_credential_file()
        print("Please edit credential.txt with your actual information before running again.")
    else:
        print("Using credentials from credential.txt")
        creds = read_credentials()
        if creds:
            print(f"Username: {creds['username']}")
            print(f"Check-in time: {creds['checkin_time']}")
            print(f"Check-out time: {creds['checkout_time']}")
            print(f"Location: {creds['latitude']}, {creds['longitude']}")
        while True:
            current_time = datetime.now().strftime("%H:%M")
            if current_time == creds['checkin_time']:
                print("Time to check in!")
                scheduled_check_in()
                time.sleep(120)
            elif current_time == creds['checkout_time']:
                print("Time to check out!")
                scheduled_check_out()
                time.sleep(120)