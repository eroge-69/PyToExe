"""
Build script for creating LinkedPad EXE using PyInstaller
Run this script to convert the Python application to a standalone EXE file
"""

import subprocess
import sys
import os

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("PyInstaller is already installed")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller installed successfully")

def build_exe():
    """Build the EXE file using PyInstaller"""
    
    # PyInstaller command with all necessary options
    cmd = [
        "pyinstaller",
        "--onefile",                    # Create a single executable file
        "--name=LinkedPad",             # Name the executable
        "--add-data=templates;templates",  # Include templates folder
        "--console",                    # Show console window (useful for debugging)
        "--icon=NONE",                  # No icon (you can add one later)
        "app.py"                        # Main Python file
    ]
    
    print("Building EXE file...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print("\n" + "="*50)
        print("BUILD SUCCESSFUL!")
        print("="*50)
        print("Your executable is ready:")
        print("- Location: dist/LinkedPad.exe")
        print("- Size: Check the dist folder")
        print("\nTo run your application:")
        print("1. Copy LinkedPad.exe to any computer")
        print("2. Double-click to run")
        print("3. Open http://localhost:5000 in browser")
        print("4. Use your phone to connect to the same IP")
        print("\nNote: Make sure the computer allows the application through firewall")
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        return False
    
    return True

def create_installer_script():
    """Create a batch file for easy building"""
    installer_content = '''@echo off
echo Building LinkedPad EXE...
python build_exe.py
pause
'''
    
    with open("build.bat", "w") as f:
        f.write(installer_content)
    
    print("Created build.bat - double-click this file to build the EXE")

if __name__ == "__main__":
    print("LinkedPad EXE Builder")
    print("="*30)
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("Error: app.py not found in current directory")
        print("Please run this script in the same folder as app.py")
        sys.exit(1)
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Build the EXE
    success = build_exe()
    
    # Create helper batch file
    create_installer_script()
    
    if success:
        print("\nBuild completed successfully!")
        print("Check the 'dist' folder for your LinkedPad.exe file")
    else:
        print("\nBuild failed. Please check the error messages above.")
    
    input("\nPress Enter to exit...")