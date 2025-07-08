import random
import time
import webbrowser

def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def mock_send_sms(phone_number, otp):
    """Simulate sending an SMS (in reality just prints to console)"""
    print(f"\n[DEBUG] SMS would be sent to {phone_number}")
    print(f"[DEBUG] Your OTP is: {otp}\n")
    return True

def verify_otp(entered_otp, actual_otp):
    """Verify if entered OTP matches"""
    return entered_otp == actual_otp

def open_rules_page():
    """Open the rules page in browser"""

    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Access Rules</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f5f7fa;
                margin: 0;
                padding: 20px;
                color: #333;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2c3e50;
                text-align: center;
                margin-bottom: 30px;
            }
            h2 {
                color: #3498db;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
                margin-top: 30px;
            }
            .rule-card {
                background: #f8f9fa;
                padding: 15px;
                border-left: 4px solid #3498db;
                margin-bottom: 15px;
                border-radius: 0 5px 5px 0;
            }
            .rule-card h3 {
                margin-top: 0;
                color: #2c3e50;
            }
            .success-message {
                text-align: center;
                padding: 20px;
                background: #d4edda;
                color: #155724;
                border-radius: 5px;
                margin-bottom: 30px;
            }
            .warning {
                color: #856404;
                background-color: #fff3cd;
                padding: 15px;
                border-radius: 5px;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="success-message">
                <h1>✓ Access Granted</h1>
                <p>You have successfully authenticated</p>
            </div>
            
            <h1>System Access Rules</h1>
            
            <h2>General Guidelines</h2>
            <div class="rule-card">
                <h3>Authentication</h3>
                <p>All users must authenticate using the OTP system. Never share your OTP with anyone.</p>
            </div>
            
            <div class="rule-card">
                <h3>Sessions</h3>
                <p>Your session will expire after 30 minutes of inactivity. Please save your work frequently.</p>
            </div>
            
            <h2>Security Policies</h2>
            <div class="rule-card">
                <h3>Password Protection</h3>
                <p>Change your password every 90 days. Use strong passwords with a mix of letters, numbers and symbols.</p>
            </div>
            
            <div class="rule-card">
                <h3>Data Handling</h3>
                <p>Classified information must be encrypted and stored only in approved locations.</p>
            </div>
            
            <div class="warning">
                <h3>Important Notice</h3>
                <p>Violation of these rules may result in immediate suspension of access privileges.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Save the HTML to a temporary file and open it
    with open('rules.html', 'w') as f:
        f.write(html_content)
    webbrowser.open('rules.html')

def main():
    print("OTP Authentication System")
    print("")
    
    phone_number = input("Enter your phone number: ")
    
    # Generate and "send" OTP
    otp = generate_otp()
    if mock_send_sms(phone_number, otp):
        print("OTP has been sent to your phone number.")
    
    # Give user 3 attempts to enter correct OTP
    attempts = 3
    while attempts > 0:
        user_otp = input(f"Enter OTP (you have {attempts} attempts remaining): ")
        
        if verify_otp(user_otp, otp):
            print("Authentication successful!")
            open_rules_page()
            return
        else:
            attempts -= 1
            print("Invalid OTP. Please try again.")
            
    print("Too many failed attempts. Please request a new OTP.")

if __name__ == "__main__":
    main()
