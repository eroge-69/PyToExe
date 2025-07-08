import win32com.client
import time
import sys
import os

class IELauncher:
    def __init__(self, constant_url="https://www.microsoft.com"):
        """
        Initialize the IE Launcher with a constant URL
        
        Args:
            constant_url (str): The URL to always open in Internet Explorer
        """
        self.constant_url = constant_url
        self.ie_app = None
    
    def launch_ie(self):
        """
        Launch Internet Explorer with the constant URL
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print(f"Launching Internet Explorer with URL: {self.constant_url}")
            
            # Create Internet Explorer Application object
            self.ie_app = win32com.client.Dispatch("InternetExplorer.Application")
            
            # Configure IE settings
            self.ie_app.Visible = True
            self.ie_app.Navigate(self.constant_url)
            
            # Optional: Set window properties
            self.ie_app.Left = 100
            self.ie_app.Top = 100
            self.ie_app.Width = 1024
            self.ie_app.Height = 768
            
            # Wait for the page to load
            while self.ie_app.Busy:
                time.sleep(0.1)
            
            print("Internet Explorer launched successfully!")
            return True
            
        except Exception as e:
            print(f"Error launching Internet Explorer: {e}")
            print("Make sure Internet Explorer is installed and COM is available.")
            return False
    
    def launch_multiple_instances(self, count=3):
        """
        Launch multiple IE instances with the same constant URL
        
        Args:
            count (int): Number of instances to launch
        """
        instances = []
        
        for i in range(count):
            try:
                print(f"Launching IE instance {i+1}/{count}")
                
                ie = win32com.client.Dispatch("InternetExplorer.Application")
                ie.Visible = True
                ie.Navigate(self.constant_url)
                
                # Cascade windows
                ie.Left = 100 + (i * 50)
                ie.Top = 100 + (i * 50)
                ie.Width = 800
                ie.Height = 600
                
                instances.append(ie)
                time.sleep(1)  # Small delay between launches
                
            except Exception as e:
                print(f"Error launching instance {i+1}: {e}")
        
        print(f"Successfully launched {len(instances)} IE instances")
        return instances
    
    def launch_with_shell(self):
        """
        Alternative method using shell command
        """
        try:
            import subprocess
            command = f'start iexplore.exe "{self.constant_url}"'
            subprocess.run(command, shell=True)
            print("Internet Explorer launched via shell command")
            return True
        except Exception as e:
            print(f"Error launching via shell: {e}")
            return False
    
    def close_ie(self):
        """
        Close the IE instance if it exists
        """
        if self.ie_app:
            try:
                self.ie_app.Quit()
                print("Internet Explorer closed")
            except Exception as e:
                print(f"Error closing IE: {e}")

def main():
    # Constant URL configuration
    CONSTANT_URL = "https://www.microsoft.com"
    
    print("=" * 50)
    print("Internet Explorer Launcher")
    print("=" * 50)
    print(f"Constant URL: {CONSTANT_URL}")
    print()
    
    # Create launcher instance
    launcher = IELauncher(CONSTANT_URL)
    
    while True:
        print("\nOptions:")
        print("1. Launch Internet Explorer")
        print("2. Launch Multiple IE Instances")
        print("3. Launch via Shell Command")
        print("4. Change URL (temporarily)")
        print("5. Close IE")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            launcher.launch_ie()
        
        elif choice == "2":
            try:
                count = int(input("Enter number of instances to launch (default 3): ") or "3")
                launcher.launch_multiple_instances(count)
            except ValueError:
                print("Invalid number entered. Using default (3)")
                launcher.launch_multiple_instances(3)
        
        elif choice == "3":
            launcher.launch_with_shell()
        
        elif choice == "4":
            new_url = input(f"Enter new URL (current: {launcher.constant_url}): ").strip()
            if new_url:
                launcher.constant_url = new_url
                print(f"URL changed to: {new_url}")
            else:
                print("URL unchanged")
        
        elif choice == "5":
            launcher.close_ie()
        
        elif choice == "6":
            print("Exiting...")
            launcher.close_ie()
            break
        
        else:
            print("Invalid choice. Please try again.")

# Advanced configuration class
class IEConfig:
    """
    Configuration class for advanced IE settings
    """
    def __init__(self):
        self.default_url = "https://www.microsoft.com"
        self.window_width = 1024
        self.window_height = 768
        self.window_left = 100
        self.window_top = 100
        self.fullscreen = False
        self.toolbar_visible = True
        self.menubar_visible = True
        self.statusbar_visible = True
    
    def apply_to_ie(self, ie_app):
        """
        Apply configuration to IE application
        
        Args:
            ie_app: Internet Explorer Application object
        """
        try:
            ie_app.Width = self.window_width
            ie_app.Height = self.window_height
            ie_app.Left = self.window_left
            ie_app.Top = self.window_top
            ie_app.ToolBar = self.toolbar_visible
            ie_app.MenuBar = self.menubar_visible
            ie_app.StatusBar = self.statusbar_visible
            
            if self.fullscreen:
                ie_app.FullScreen = True
                
        except Exception as e:
            print(f"Error applying configuration: {e}")

def advanced_launch():
    """
    Advanced launcher with custom configuration
    """
    config = IEConfig()
    config.default_url = "https://www.google.com"
    config.window_width = 1200
    config.window_height = 800
    config.fullscreen = False
    
    try:
        ie = win32com.client.Dispatch("InternetExplorer.Application")
        ie.Visible = True
        ie.Navigate(config.default_url)
        
        # Wait for IE to initialize
        time.sleep(2)
        
        # Apply configuration
        config.apply_to_ie(ie)
        
        print("Advanced IE launcher completed successfully!")
        return ie
        
    except Exception as e:
        print(f"Advanced launcher error: {e}")
        return None

if __name__ == "__main__":
    # Check if required module is available
    try:
        import win32com.client
        main()
    except ImportError:
        print("Error: pywin32 module not found!")
        print("Install it using: pip install pywin32")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        sys.exit(0)