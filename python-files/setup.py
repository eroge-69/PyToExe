#!/usr/bin/env python3
"""
Real Estate Message Parser - Setup Script
Automated installation and configuration script
"""

import os
import sys
import subprocess
import platform
import urllib.request
import zipfile
import shutil
from pathlib import Path

def print_header():
    print("=" * 60)
    print("🏠 Real Estate Message Parser - Setup")
    print("=" * 60)
    print()

def print_step(step, description):
    print(f"📋 Step {step}: {description}")
    print("-" * 40)

def run_command(command, description=""):
    """Run a shell command and handle errors"""
    try:
        if description:
            print(f"   {description}...")
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"   ✅ Success")
            return True
        else:
            print(f"   ❌ Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("❌ Python 3.11 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_node_version():
    """Check if Node.js is available (optional for development)"""
    try:
        result = subprocess.run("node --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js version: {result.stdout.strip()}")
            return True
        else:
            print("⚠️  Node.js not found (optional for frontend development)")
            return False
    except:
        print("⚠️  Node.js not found (optional for frontend development)")
        return False

def create_virtual_environment():
    """Create Python virtual environment"""
    if os.path.exists("venv"):
        print("   Virtual environment already exists")
        return True
    
    return run_command("python -m venv venv", "Creating virtual environment")

def activate_virtual_environment():
    """Get activation command for virtual environment"""
    if platform.system() == "Windows":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"

def install_python_dependencies():
    """Install Python dependencies"""
    activate_cmd = activate_virtual_environment()
    
    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    
    commands = [
        f"{pip_cmd} install --upgrade pip",
        f"{pip_cmd} install -r requirements.txt"
    ]
    
    for cmd in commands:
        if not run_command(cmd, f"Running: {cmd}"):
            return False
    
    return True

def download_spacy_model():
    """Download spaCy English language model"""
    if platform.system() == "Windows":
        python_cmd = "venv\\Scripts\\python"
    else:
        python_cmd = "venv/bin/python"
    
    return run_command(f"{python_cmd} -m spacy download en_core_web_sm", 
                      "Downloading spaCy English model")

def create_database():
    """Initialize the database"""
    if platform.system() == "Windows":
        python_cmd = "venv\\Scripts\\python"
    else:
        python_cmd = "venv/bin/python"
    
    # Create database directory if it doesn't exist
    os.makedirs("src/database", exist_ok=True)
    
    # Run a simple database initialization
    init_script = """
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import db
from src.main import app

with app.app_context():
    db.create_all()
    print("Database initialized successfully")
"""
    
    with open("init_db.py", "w") as f:
        f.write(init_script)
    
    result = run_command(f"{python_cmd} init_db.py", "Initializing database")
    
    # Clean up
    if os.path.exists("init_db.py"):
        os.remove("init_db.py")
    
    return result

def create_sample_data():
    """Create sample data for testing"""
    sample_messages = [
        {
            "message": "🏠 2BHK apartment for sale in Mumbai Andheri. Price: ₹85 Lakhs. Area: 950 sqft. Contact: Rahul 9876543210",
            "source": "Sample Data"
        },
        {
            "message": "3BHK villa for rent in Gurgaon Sector 45. Monthly rent: ₹45,000. Furnished with parking. Call Priya 9123456789",
            "source": "Sample Data"
        },
        {
            "message": "Looking to buy 1BHK flat in Pune under 30 lakhs. Preferred areas: Kothrud, Karve Nagar. Contact buyer.pune@email.com",
            "source": "Sample Data"
        }
    ]
    
    if platform.system() == "Windows":
        python_cmd = "venv\\Scripts\\python"
    else:
        python_cmd = "venv/bin/python"
    
    sample_script = f"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.services.text_extractor import RealEstateTextExtractor
from src.models.real_estate import RealEstateEntry, db

sample_messages = {sample_messages}

with app.app_context():
    extractor = RealEstateTextExtractor()
    
    for msg_data in sample_messages:
        try:
            extracted_data = extractor.extract_real_estate_data(msg_data['message'])
            
            entry = RealEstateEntry(
                original_message=msg_data['message'],
                source=msg_data['source'],
                **extracted_data
            )
            
            db.session.add(entry)
            db.session.commit()
            print(f"Added sample entry: {{extracted_data.get('property_type', 'Unknown')}}")
            
        except Exception as e:
            print(f"Error adding sample data: {{str(e)}}")
    
    print("Sample data created successfully")
"""
    
    with open("create_samples.py", "w") as f:
        f.write(sample_script)
    
    result = run_command(f"{python_cmd} create_samples.py", "Creating sample data")
    
    # Clean up
    if os.path.exists("create_samples.py"):
        os.remove("create_samples.py")
    
    return result

def create_startup_script():
    """Create a startup script for easy launching"""
    if platform.system() == "Windows":
        script_content = """@echo off
echo Starting Real Estate Message Parser...
cd /d "%~dp0"
call venv\\Scripts\\activate
python src\\main.py
pause
"""
        with open("start.bat", "w") as f:
            f.write(script_content)
        print("   ✅ Created start.bat for Windows")
    
    else:
        script_content = """#!/bin/bash
echo "Starting Real Estate Message Parser..."
cd "$(dirname "$0")"
source venv/bin/activate
python src/main.py
"""
        with open("start.sh", "w") as f:
            f.write(script_content)
        os.chmod("start.sh", 0o755)
        print("   ✅ Created start.sh for Unix/Linux/Mac")

def print_completion_message():
    """Print setup completion message"""
    print()
    print("=" * 60)
    print("🎉 Setup Complete!")
    print("=" * 60)
    print()
    print("📋 Next Steps:")
    print("1. Start the application:")
    
    if platform.system() == "Windows":
        print("   • Double-click start.bat")
        print("   • Or run: python src\\main.py")
    else:
        print("   • Run: ./start.sh")
        print("   • Or run: python src/main.py")
    
    print()
    print("2. Open your browser to: http://localhost:5000")
    print()
    print("3. Try processing a sample message:")
    print("   '2BHK for sale in Mumbai 50 lakhs contact 9876543210'")
    print()
    print("📚 Documentation:")
    print("   • README.md - Technical documentation")
    print("   • USER_GUIDE.md - Practical usage guide")
    print()
    print("🆘 Need Help?")
    print("   • Check the troubleshooting section in README.md")
    print("   • Verify all dependencies are installed")
    print("   • Test with sample data first")
    print()
    print("Happy Lead Management! 🏠📊")

def main():
    """Main setup function"""
    print_header()
    
    # Step 1: Check prerequisites
    print_step(1, "Checking Prerequisites")
    if not check_python_version():
        sys.exit(1)
    check_node_version()
    print()
    
    # Step 2: Create virtual environment
    print_step(2, "Setting Up Python Environment")
    if not create_virtual_environment():
        print("❌ Failed to create virtual environment")
        sys.exit(1)
    print()
    
    # Step 3: Install dependencies
    print_step(3, "Installing Dependencies")
    if not install_python_dependencies():
        print("❌ Failed to install Python dependencies")
        sys.exit(1)
    print()
    
    # Step 4: Download spaCy model
    print_step(4, "Setting Up NLP Model")
    if not download_spacy_model():
        print("❌ Failed to download spaCy model")
        sys.exit(1)
    print()
    
    # Step 5: Initialize database
    print_step(5, "Initializing Database")
    if not create_database():
        print("❌ Failed to initialize database")
        sys.exit(1)
    print()
    
    # Step 6: Create sample data
    print_step(6, "Creating Sample Data")
    if not create_sample_data():
        print("⚠️  Failed to create sample data (optional)")
    print()
    
    # Step 7: Create startup scripts
    print_step(7, "Creating Startup Scripts")
    create_startup_script()
    print()
    
    # Completion message
    print_completion_message()

if __name__ == "__main__":
    main()

