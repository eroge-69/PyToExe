#!/usr/bin/env python3
"""
Test script for the Python to EXE Converter application.
This script tests the basic functionality without launching the full UI.
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        print("✓ PyQt5.QtWidgets imported successfully")
    except ImportError as e:
        print(f"✗ PyQt5.QtWidgets import failed: {e}")
        return False
    
    try:
        from PyQt5.QtCore import QThread, pyqtSignal
        print("✓ PyQt5.QtCore imported successfully")
    except ImportError as e:
        print(f"✗ PyQt5.QtCore import failed: {e}")
        return False
    
    try:
        from PyQt5.QtGui import QIcon
        print("✓ PyQt5.QtGui imported successfully")
    except ImportError as e:
        print(f"✗ PyQt5.QtGui import failed: {e}")
        return False
    
    try:
        import psutil
        print("✓ psutil imported successfully")
    except ImportError as e:
        print(f"✗ psutil import failed: {e}")
        return False
    
    return True

def test_main_module():
    """Test if the main module can be imported."""
    print("\nTesting main module import...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        import main
        print("✓ Main module imported successfully")
        
        # Test if classes exist
        if hasattr(main, 'PythonToExeConverter'):
            print("✓ PythonToExeConverter class found")
        else:
            print("✗ PythonToExeConverter class not found")
            return False
            
        if hasattr(main, 'ConversionWorker'):
            print("✓ ConversionWorker class found")
        else:
            print("✗ ConversionWorker class not found")
            return False
            
        if hasattr(main, 'IconConverter'):
            print("✓ IconConverter class found")
        else:
            print("✗ IconConverter class not found")
            return False
            
        return True
        
    except ImportError as e:
        print(f"✗ Main module import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_requirements():
    """Test if requirements.txt exists and can be read."""
    print("\nTesting requirements file...")
    
    if os.path.exists("requirements.txt"):
        print("✓ requirements.txt found")
        try:
            with open("requirements.txt", "r") as f:
                content = f.read()
                if "PyQt5" in content and "cx_Freeze" in content:
                    print("✓ requirements.txt contains required packages")
                    return True
                else:
                    print("✗ requirements.txt missing required packages")
                    return False
        except Exception as e:
            print(f"✗ Error reading requirements.txt: {e}")
            return False
    else:
        print("✗ requirements.txt not found")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("Python to EXE Converter - Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # Test imports
    if test_imports():
        tests_passed += 1
    
    # Test main module
    if test_main_module():
        tests_passed += 1
    
    # Test requirements
    if test_requirements():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✓ All tests passed! The application is ready to run.")
        print("\nTo launch the application, run:")
        print("  python main.py")
        print("\nOr double-click run.bat")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        print("\nMake sure to install all dependencies:")
        print("  pip install -r requirements.txt")
    
    print("=" * 50)

if __name__ == "__main__":
    main()

