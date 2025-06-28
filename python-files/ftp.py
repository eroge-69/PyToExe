import keyboard
import time
import os
import threading
from datetime import datetime
from PIL import ImageGrab
import ftplib
import tempfile
import sys

class BackgroundScreenshotCapture:
    def __init__(self):
        self.ftp_host = "192.168.1.16"
        self.ftp_port = 2221
        self.ftp_path = "/1/"
        self.running = True
        self.screenshot_counter = 0
        
    def get_next_screenshot_number(self):
        """Get the next available screenshot number by checking FTP server"""
        try:
            # Connect to FTP server to check existing files
            ftp = ftplib.FTP()
            ftp.connect(self.ftp_host, self.ftp_port)
            ftp.login()  # Anonymous login
            
            try:
                ftp.cwd(self.ftp_path)
                files = ftp.nlst()
                
                # Find the highest numbered screenshot
                max_number = 0
                for file in files:
                    if file.endswith('.png') and file[:-4].isdigit():
                        number = int(file[:-4])
                        max_number = max(max_number, number)
                
                self.screenshot_counter = max_number + 1
                
            except Exception as e:
                print(f"Could not read FTP directory, starting from 1: {e}")
                self.screenshot_counter = 1
                
            ftp.quit()
            
        except Exception as e:
            print(f"Error connecting to FTP for numbering, starting from 1: {e}")
            self.screenshot_counter = 1
    
    def take_screenshot(self):
        """Take a screenshot and return the image object"""
        try:
            screenshot = ImageGrab.grab()
            return screenshot
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return None
    
    def upload_to_ftp(self, image_path, filename):
        """Upload the screenshot to FTP server"""
        try:
            # Connect to FTP server
            ftp = ftplib.FTP()
            ftp.connect(self.ftp_host, self.ftp_port)
            ftp.login()  # Anonymous login (no username/password)
            
            # Change to the target directory
            try:
                ftp.cwd(self.ftp_path)
            except:
                print(f"Could not change to directory {self.ftp_path}")
                return False
            
            # Upload the file
            with open(image_path, 'rb') as file:
                ftp.storbinary(f'STOR {filename}', file)
            
            ftp.quit()
            print(f"Screenshot uploaded successfully: {filename}")
            return True
            
        except Exception as e:
            print(f"Error uploading to FTP: {e}")
            return False
    
    def on_hotkey_pressed(self):
        """Called when Ctrl+Shift+Q is pressed"""
        print("Hotkey detected! Taking screenshot...")
        
        # Take screenshot
        screenshot = self.take_screenshot()
        if not screenshot:
            return
        
        # Generate filename with sequential number
        filename = f"{self.screenshot_counter}.png"
        
        # Save to temporary file
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, filename)
        
        try:
            screenshot.save(temp_path, "PNG")
            print(f"Screenshot saved temporarily: {temp_path}")
            
            # Upload to FTP in a separate thread to avoid blocking
            upload_thread = threading.Thread(
                target=self.upload_and_cleanup, 
                args=(temp_path, filename)
            )
            upload_thread.daemon = True
            upload_thread.start()
            
            # Increment counter for next screenshot
            self.screenshot_counter += 1
            
        except Exception as e:
            print(f"Error saving screenshot: {e}")
    
    def upload_and_cleanup(self, temp_path, filename):
        """Upload file and clean up temporary file"""
        success = self.upload_to_ftp(temp_path, filename)
        
        # Clean up temporary file
        try:
            os.remove(temp_path)
            print(f"Temporary file cleaned up: {temp_path}")
        except Exception as e:
            print(f"Error cleaning up temporary file: {e}")
        
        if success:
            print("Screenshot capture and upload completed successfully!")
        else:
            print("Screenshot capture completed but upload failed.")
    
    def start_monitoring(self):
        """Start the background monitoring"""
        print("Initializing screenshot numbering...")
        self.get_next_screenshot_number()
        print(f"Next screenshot will be: {self.screenshot_counter}.png")
        
        print("Background screenshot capture started.")
        print("Press Ctrl+Shift+Q to take a screenshot.")
        print("Press Ctrl+C to exit the program.")
        
        # Register the hotkey
        keyboard.add_hotkey('ctrl+shift+q', self.on_hotkey_pressed)
        
        try:
            # Keep the program running
            while self.running:
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nExiting screenshot capture...")
            self.running = False
            keyboard.unhook_all()

def main():
    """Main function to start the screenshot capture service"""
    try:
        # Check if required modules are available
        required_modules = ['keyboard', 'PIL', 'ftplib']
        missing_modules = []
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)
        
        if missing_modules:
            print("Missing required modules. Please install:")
            for module in missing_modules:
                if module == 'PIL':
                    print("pip install Pillow")
                else:
                    print(f"pip install {module}")
            return
        
        # Create and start the screenshot capture service
        capture_service = BackgroundScreenshotCapture()
        capture_service.start_monitoring()
        
    except Exception as e:
        print(f"Error starting screenshot capture service: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
