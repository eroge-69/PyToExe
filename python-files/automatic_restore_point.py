import subprocess
import datetime
import sys
import os
import ctypes
import time

def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def create_automatic_restore_point():
    """
    Automatically create a restore point using Windows' native system
    without requiring manual input from the user.
    """
    try:
        print("🔄 Creating automatic restore point...")
        print("Please wait, this may take a few moments...")
        
        # Generate automatic description with timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d at %I:%M %p")
        auto_description = f"Automatic Restore Point - {timestamp}"
        
        print(f"📝 Description: {auto_description}")
        
        # Use PowerShell to create restore point automatically
        # This uses Windows' native restore point creation system
        powershell_command = f'''
        $ErrorActionPreference = "Stop"
        try {{
            # Enable computer restore if not already enabled
            Enable-ComputerRestore -Drive "C:\\" -ErrorAction SilentlyContinue
            
            # Create the restore point
            Checkpoint-Computer -Description "{auto_description}" -RestorePointType "APPLICATION_INSTALL"
            
            Write-Host "SUCCESS: Restore point created successfully"
            exit 0
        }}
        catch {{
            Write-Host "ERROR: $($_.Exception.Message)"
            exit 1
        }}
        '''
        
        # Execute PowerShell command
        result = subprocess.run([
            'powershell.exe',
            '-WindowStyle', 'Minimized',
            '-ExecutionPolicy', 'Bypass',
            '-Command', powershell_command
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ SUCCESS: Restore point created automatically!")
            print(f"📍 Restore point name: {auto_description}")
            
            # Show confirmation
            print("\n" + "="*60)
            print("🎉 RESTORE POINT CREATED SUCCESSFULLY!")
            print("="*60)
            print(f"📅 Created on: {datetime.datetime.now().strftime('%A, %B %d, %Y at %I:%M:%S %p')}")
            print(f"💾 Description: {auto_description}")
            print("🔧 Type: Application Install")
            print("="*60)
            
            return True
        else:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            print(f"❌ ERROR: Failed to create restore point")
            print(f"Details: {error_msg}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ ERROR: Operation timed out (5 minutes)")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def check_system_requirements():
    """Check if system meets requirements for restore point creation."""
    print("🔍 Checking system requirements...")
    
    # Check Windows OS
    if os.name != 'nt':
        print("❌ This script requires Windows OS")
        return False
    
    # Check admin privileges
    if not is_admin():
        print("❌ Administrator privileges required")
        print("\n💡 To fix this:")
        print("1. Right-click on Command Prompt or PowerShell")
        print("2. Select 'Run as administrator'")
        print("3. Navigate to this script and run it again")
        return False
    
    print("✅ System requirements met")
    return True

def show_restore_points():
    """Display existing restore points."""
    try:
        print("\n📋 Checking existing restore points...")
        
        powershell_cmd = '''
        Get-ComputerRestorePoint | Sort-Object CreationTime -Descending | 
        Select-Object -First 5 SequenceNumber, CreationTime, Description, RestorePointType |
        Format-Table -AutoSize
        '''
        
        result = subprocess.run([
            'powershell.exe',
            '-Command', powershell_cmd
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout.strip():
            print("📊 Recent restore points:")
            print("-" * 50)
            print(result.stdout.strip())
        else:
            print("ℹ️  No existing restore points found or System Restore not configured")
            
    except Exception as e:
        print(f"⚠️  Could not retrieve restore points: {e}")

def main():
    """Main function to create automatic restore point."""
    
    print("\n" + "="*60)
    print("🔧 AUTOMATIC WINDOWS RESTORE POINT CREATOR")
    print("="*60)
    print("This will automatically create a new System Restore point")
    print("using Windows' native restore point system.\n")
    
    # Check system requirements
    if not check_system_requirements():
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Show existing restore points
    show_restore_points()
    
    print("\n" + "="*60)
    print("🚀 CREATING NEW RESTORE POINT")
    print("="*60)
    
    # Create restore point automatically
    success = create_automatic_restore_point()
    
    if success:
        print("\n🎯 OPERATION COMPLETED SUCCESSFULLY!")
        print("Your system now has a new restore point that you can use")
        print("to restore your computer if needed.")
        
        # Option to view all restore points
        print("\n" + "-"*40)
        view_points = input("Would you like to see all restore points? (y/n): ").lower().strip()
        if view_points in ['y', 'yes']:
            show_restore_points()
            
        # Option to open System Restore
        print("\n" + "-"*40)
        open_restore = input("Would you like to open System Restore wizard? (y/n): ").lower().strip()
        if open_restore in ['y', 'yes']:
            try:
                subprocess.Popen(['rstrui.exe'])
                print("✅ System Restore wizard opened!")
            except:
                print("❌ Could not open System Restore wizard")
    else:
        print("\n❌ OPERATION FAILED")
        print("The restore point could not be created.")
        print("Please check the error messages above.")
    
    print("\n" + "="*60)
    input("Press Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Operation cancelled by user.")
        sys.exit(0)