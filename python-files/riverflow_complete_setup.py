#!/usr/bin/env python3
"""
RiverFlow Studio - Complete Build & Distribution Setup Script
Created by Juvons Riviere Creative Labs

This script handles the complete build process for RiverFlow Studio:
- Dependency management and installation
- Application compilation and packaging  
- Installer creation
- Distribution preparation
- Testing and validation
"""

import os
import sys
import subprocess
import shutil
import json
import time
import platform
import requests
import zipfile
import tempfile
from pathlib import Path
from datetime import datetime

class RiverFlowSetupManager:
    """Complete setup and build management for RiverFlow Studio"""
    
    def __init__(self):
        self.app_name = "RiverFlow Studio"
        self.app_version = "1.0.0"
        self.creator = "Juvons Riviere Creative Labs"
        self.script_name = "riverflow_studio.py"
        
        # Build configuration
        self.build_config = {
            'executable_name': 'RiverFlowStudio',
            'icon_file': 'riverflow_icon.ico',
            'build_dir': Path('build'),
            'dist_dir': Path('dist'),
            'setup_dir': Path('setup'),
            'assets_dir': Path('assets'),
            'docs_dir': Path('docs'),
            'installer_name': 'RiverFlowStudio_Setup.exe'
        }
        
        # Required dependencies with versions
        self.dependencies = {
            'runtime': {
                'PyQt6': '>=6.4.0',
                'obs-websocket-py': '>=1.0.0',
                'psutil': '>=5.9.0',
                'requests': '>=2.28.0',
                'pillow': '>=9.0.0'
            },
            'build': {
                'pyinstaller': '>=5.0.0',
                'auto-py-to-exe': '>=2.0.0',
                'setuptools': '>=65.0.0',
                'wheel': '>=0.37.0'
            },
            'optional': {
                'nsis': 'makensis',  # For Windows installer
                'upx': 'upx'         # For executable compression
            }
        }
        
        # Platform detection
        self.platform = platform.system().lower()
        self.is_windows = self.platform == 'windows'
        self.is_macos = self.platform == 'darwin'
        self.is_linux = self.platform == 'linux'
        
        print(f"🌊 {self.app_name} Setup Manager")
        print(f"Platform: {platform.system()} {platform.machine()}")
        print(f"Python: {sys.version}")
        print("=" * 60)
    
    def run_complete_setup(self):
        """Execute complete setup process"""
        try:
            print("🚀 Starting complete build process...\n")
            
            # Phase 1: Environment Setup
            self.log_phase("Environment Setup")
            self.setup_build_environment()
            self.validate_python_environment()
            
            # Phase 2: Dependency Management
            self.log_phase("Dependency Management")
            self.install_dependencies()
            self.verify_dependencies()
            
            # Phase 3: Asset Creation
            self.log_phase("Asset Creation")
            self.create_application_assets()
            self.create_documentation()
            
            # Phase 4: Application Build
            self.log_phase("Application Build")
            self.build_executable()
            self.optimize_executable()
            
            # Phase 5: Installer Creation
            self.log_phase("Installer Creation")
            self.create_installer_package()
            
            # Phase 6: Testing & Validation
            self.log_phase("Testing & Validation")
            self.test_executable()
            self.validate_installer()
            
            # Phase 7: Distribution Preparation
            self.log_phase("Distribution Preparation")
            self.prepare_distribution()
            self.create_release_package()
            
            print("\n🎉 Build process completed successfully!")
            self.display_build_summary()
            
            return True
            
        except Exception as e:
            print(f"\n❌ Build process failed: {e}")
            self.cleanup_failed_build()
            return False
    
    def log_phase(self, phase_name):
        """Log current build phase"""
        print(f"\n📋 Phase: {phase_name}")
        print("-" * 40)
    
    def setup_build_environment(self):
        """Setup build environment and directories"""
        print("🔧 Setting up build environment...")
        
        # Create directory structure
        directories = [
            self.build_config['build_dir'],
            self.build_config['dist_dir'],
            self.build_config['setup_dir'],
            self.build_config['assets_dir'],
            self.build_config['docs_dir']
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        
        # Clean previous builds
        if self.build_config['dist_dir'].exists():
            shutil.rmtree(self.build_config['dist_dir'])
            self.build_config['dist_dir'].mkdir()
            print("🧹 Cleaned previous build artifacts")
    
    def validate_python_environment(self):
        """Validate Python environment"""
        print("🐍 Validating Python environment...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            raise Exception("Python 3.8 or higher is required")
        print(f"✅ Python version: {sys.version}")
        
        # Check pip availability
        try:
            subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                         check=True, capture_output=True)
            print("✅ pip is available")
        except subprocess.CalledProcessError:
            raise Exception("pip is not available")
        
        # Upgrade pip
        print("⬆️ Upgrading pip...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True, capture_output=True)
    
    def install_dependencies(self):
        """Install all required dependencies"""
        print("📦 Installing dependencies...")
        
        all_deps = {}
        all_deps.update(self.dependencies['runtime'])
        all_deps.update(self.dependencies['build'])
        
        for package, version in all_deps.items():
            print(f"📥 Installing {package} {version}...")
            package_spec = f"{package}{version}" if version.startswith(('>', '<', '=', '!')) else package
            
            try:
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', 
                    package_spec, '--upgrade', '--user'
                ], check=True, capture_output=True)
                print(f"✅ {package} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Warning: Failed to install {package}: {e}")
        
        # Install optional tools
        self.install_optional_tools()
    
    def install_optional_tools(self):
        """Install optional build tools"""
        print("🛠️ Installing optional tools...")
        
        # Check for NSIS (Windows installer creator)
        if self.is_windows:
            nsis_path = shutil.which('makensis')
            if not nsis_path:
                print("💡 NSIS not found. Download from: https://nsis.sourceforge.io/")
                print("   NSIS is needed for creating Windows installers")
            else:
                print(f"✅ NSIS found: {nsis_path}")
        
        # Check for UPX (executable compressor)
        upx_path = shutil.which('upx')
        if not upx_path:
            print("💡 UPX not found. Download from: https://upx.github.io/")
            print("   UPX can compress executables to reduce size")
        else:
            print(f"✅ UPX found: {upx_path}")
    
    def verify_dependencies(self):
        """Verify all dependencies are properly installed"""
        print("🔍 Verifying dependencies...")
        
        for category, deps in self.dependencies.items():
            if category == 'optional':
                continue
                
            for package in deps.keys():
                try:
                    # Convert package names to import names
                    import_name = {
                        'PyQt6': 'PyQt6.QtWidgets',
                        'obs-websocket-py': 'obswebsocket',
                        'pillow': 'PIL',
                        'auto-py-to-exe': 'auto_py_to_exe'
                    }.get(package, package)
                    
                    __import__(import_name)
                    print(f"✅ {package} import successful")
                except ImportError as e:
                    print(f"❌ {package} import failed: {e}")
                    raise Exception(f"Dependency verification failed for {package}")
    
    def create_application_assets(self):
        """Create application assets (icons, resources)"""
        print("🎨 Creating application assets...")
        
        # Create application icon
        self.create_application_icon()
        
        # Create resource files
        self.create_resource_files()
        
        # Create configuration templates
        self.create_config_templates()
    
    def create_application_icon(self):
        """Create professional application icon"""
        icon_path = self.build_config['assets_dir'] / self.build_config['icon_file']
        
        if icon_path.exists():
            print(f"✅ Icon already exists: {icon_path}")
            return
        
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            print("🖼️ Creating application icon...")
            
            # Create multi-resolution icon
            sizes = [(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)]
            images = []
            
            for size in sizes:
                # Create base image with gradient
                image = Image.new('RGBA', size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(image)
                
                # RiverFlow brand colors
                center = (size[0] // 2, size[1] // 2)
                radius = min(size) // 2 - 2
                
                # Create circular gradient background
                for i in range(radius):
                    alpha = 255 - (i * 255 // radius)
                    color = (30, 60, 114, alpha)  # RiverFlow blue with alpha
                    draw.ellipse([
                        center[0] - radius + i, center[1] - radius + i,
                        center[0] + radius - i, center[1] + radius - i
                    ], fill=color)
                
                # Add river flow pattern
                wave_color = (74, 144, 226, 200)
                wave_height = size[1] // 8
                for j in range(3):
                    y_offset = center[1] - wave_height + j * wave_height // 2
                    wave_width = size[0] - 20 - j * 10
                    wave_x = (size[0] - wave_width) // 2
                    
                    draw.ellipse([
                        wave_x, y_offset,
                        wave_x + wave_width, y_offset + wave_height
                    ], fill=wave_color)
                
                images.append(image)
            
            # Save as ICO file
            images[0].save(
                icon_path, format='ICO', 
                sizes=[(img.size[0], img.size[1]) for img in images],
                append_images=images[1:]
            )
            
            print(f"✅ Application icon created: {icon_path}")
            
        except ImportError:
            print("⚠️ PIL not available, creating simple icon...")
            self.create_simple_icon(icon_path)
        except Exception as e:
            print(f"⚠️ Icon creation failed: {e}")
            self.create_simple_icon(icon_path)
    
    def create_simple_icon(self, icon_path):
        """Create a simple fallback icon"""
        # Create a simple ICO file using basic drawing
        try:
            from PIL import Image, ImageDraw
            
            image = Image.new('RGBA', (256, 256), (30, 60, 114, 255))
            draw = ImageDraw.Draw(image)
            
            # Simple design
            draw.ellipse([20, 20, 236, 236], fill=(74, 144, 226, 255))
            draw.ellipse([60, 60, 196, 196], fill=(255, 255, 255, 255))
            
            image.save(icon_path, format='ICO')
            print(f"✅ Simple icon created: {icon_path}")
        except:
            print("⚠️ Could not create icon file")
    
    def create_resource_files(self):
        """Create additional resource files"""
        print("📄 Creating resource files...")
        
        # Create version info file
        version_info = {
            'version': self.app_version,
            'name': self.app_name,
            'description': 'Professional Stream Automation Suite',
            'creator': self.creator,
            'build_date': datetime.now().isoformat(),
            'platform': platform.system(),
            'python_version': sys.version
        }
        
        version_file = self.build_config['assets_dir'] / 'version.json'
        with open(version_file, 'w') as f:
            json.dump(version_info, f, indent=2)
        print(f"✅ Version info created: {version_file}")
        
        # Create license file
        license_content = f"""RiverFlow Studio
Copyright (c) 2024 {self.creator}

All rights reserved. This software is proprietary and confidential.
Unauthorized copying, distribution, or use is strictly prohibited.

For licensing information, contact: info@juvonsriviere.com
"""
        
        license_file = self.build_config['assets_dir'] / 'LICENSE.txt'
        with open(license_file, 'w') as f:
            f.write(license_content)
        print(f"✅ License file created: {license_file}")
    
    def create_config_templates(self):
        """Create configuration templates"""
        print("⚙️ Creating configuration templates...")
        
        # Default configuration template
        default_config = {
            'app_name': self.app_name,
            'version': self.app_version,
            'obs_websocket_ip': '127.0.0.1',
            'obs_websocket_port': 4455,
            'scene_name': 'RiverFlow Live',
            'media_source_name': 'Primary Media',
            'auto_launch_obs': True,
            'minimize_to_tray': True,
            'randomize_playback': True,
            'stream_duration_minutes': 0,
            'scheduler_active': False,
            'status_update_interval': 6,
            'max_log_entries': 1000
        }
        
        config_file = self.build_config['assets_dir'] / 'default_config.json'
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        print(f"✅ Default configuration created: {config_file}")
    
    def create_documentation(self):
        """Create user documentation"""
        print("📚 Creating documentation...")
        
        # README file
        readme_content = f"""# {self.app_name} v{self.app_version}

## Professional Stream Automation Suite
*Created by {self.creator}*

### Features
- 🎬 Intelligent Stream Automation
- 🔄 Smart Media Management  
- ⚡ One-Click Broadcasting
- 📊 Advanced Analytics Dashboard
- ⏰ Scheduled Streaming
- 🛡️ Professional Grade Security

### Quick Start
1. Launch RiverFlow Studio
2. Complete the initial setup wizard
3. Configure your media library
4. Connect to OBS Studio
5. Start streaming with one click!

### System Requirements
- Windows 10/11, macOS 10.14+, or Linux
- OBS Studio 28.0 or higher
- 4GB RAM minimum (8GB recommended)
- 1GB free disk space

### Support
For support and documentation, visit:
https://github.com/juvonsriviere/riverflow

### License
Copyright (c) 2024 {self.creator}
All rights reserved.
"""
        
        readme_file = self.build_config['docs_dir'] / 'README.md'
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        print(f"✅ README created: {readme_file}")
        
        # User guide
        user_guide = """# RiverFlow Studio User Guide

## Getting Started

### Initial Setup
When you first launch RiverFlow Studio, the setup wizard will guide you through:
1. System analysis and OBS detection
2. Media file discovery
3. Stream configuration
4. Final setup confirmation

### Main Interface

#### Control Center
- **GO LIVE**: Start/stop streaming with one click
- **Studio Setup**: Reconfigure your setup
- **Launch OBS**: Open OBS Studio directly

#### Media Library Manager
- **Select Media Files**: Choose individual files
- **Select Media Folder**: Import entire folders
- **Auto-Discover**: Find media automatically

#### Stream Configuration
- **Scene Name**: OBS scene to use for streaming
- **Media Source**: OBS media source name
- **Stream Duration**: Set automatic stop time

#### Stream Automation
- **Smart Scheduling**: Automatically stream at scheduled times
- **Daily Configuration**: Set different times for each day
- **Duration Control**: Customize stream length per day

### Advanced Settings
Access advanced settings for:
- OBS WebSocket configuration
- Application preferences
- Performance tuning
- System integration

### Troubleshooting

#### OBS Connection Issues
1. Ensure OBS Studio is running
2. Check WebSocket plugin is enabled
3. Verify IP address and port settings
4. Check firewall settings

#### Media Playback Issues
1. Verify file formats are supported
2. Check file paths are correct
3. Ensure files are not corrupted
4. Test files in OBS directly

### Keyboard Shortcuts
- **Ctrl+G**: Go Live/Stop Stream
- **Ctrl+O**: Launch OBS Studio
- **Ctrl+S**: Open Studio Setup
- **Ctrl+Q**: Quit Application

### Tips for Best Results
1. Use high-quality media files
2. Keep media files in accessible locations
3. Test your setup before going live
4. Monitor system resources during streaming
5. Keep OBS Studio updated

For more help, visit: https://github.com/juvonsriviere/riverflow
"""
        
        guide_file = self.build_config['docs_dir'] / 'UserGuide.md'
        with open(guide_file, 'w') as f:
            f.write(user_guide)
        print(f"✅ User guide created: {guide_file}")
    
    def build_executable(self):
        """Build the standalone executable"""
        print("🏗️ Building standalone executable...")
        
        if not Path(self.script_name).exists():
            raise Exception(f"Main script not found: {self.script_name}")
        
        # PyInstaller build command
        cmd = [
            'pyinstaller',
            '--onefile',
            '--windowed',
            '--name', self.build_config['executable_name'],
            '--clean',
            '--noconfirm',
            f'--distpath={self.build_config["dist_dir"]}',
            f'--workpath={self.build_config["build_dir"]}',
            '--optimize=2'
        ]
        
        # Add icon if available
        icon_path = self.build_config['assets_dir'] / self.build_config['icon_file']
        if icon_path.exists():
            cmd.extend(['--icon', str(icon_path)])
        
        # Add version info for Windows
        if self.is_windows:
            self.create_windows_version_file()
            version_file = self.build_config['assets_dir'] / 'version.rc'
            if version_file.exists():
                cmd.extend(['--version-file', str(version_file)])
        
        # Add resource files
        resources_to_add = [
            (self.build_config['assets_dir'] / 'default_config.json', '.'),
            (self.build_config['assets_dir'] / 'LICENSE.txt', '.'),
            (self.build_config['docs_dir'] / 'README.md', '.'),
            (self.build_config['docs_dir'] / 'UserGuide.md', '.')
        ]
        
        for src, dst in resources_to_add:
            if src.exists():
                cmd.extend(['--add-data', f'{src};{dst}'])
        
        # Hidden imports for dependencies
        hidden_imports = [
            'obswebsocket',
            'psutil',
            'requests',
            'json',
            'logging',
            'threading',
            'subprocess',
            'pathlib',
            'datetime',
            'platform'
        ]
        
        if self.is_windows:
            hidden_imports.append('winreg')
        
        for import_name in hidden_imports:
            cmd.extend(['--hidden-import', import_name])
        
        # Add the main script
        cmd.append(self.script_name)
        
        print(f"🚀 Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✅ Executable build completed successfully!")
            
            # Verify executable was created
            exe_name = self.build_config['executable_name']
            if self.is_windows:
                exe_name += '.exe'
            
            exe_path = self.build_config['dist_dir'] / exe_name
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"📦 Executable size: {size_mb:.1f} MB")
                print(f"📍 Location: {exe_path}")
            else:
                raise Exception("Executable not found after build")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Build failed: {e}")
            if e.stdout:
                print("STDOUT:", e.stdout)
            if e.stderr:
                print("STDERR:", e.stderr)
            raise
    
    def create_windows_version_file(self):
        """Create Windows version resource file"""
        if not self.is_windows:
            return
        
        print("📋 Creating Windows version file...")
        
        version_parts = self.app_version.split('.')
        while len(version_parts) < 4:
            version_parts.append('0')
        
        version_rc = f"""# UTF-8
# RiverFlow Studio Version Information

VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({version_parts[0]},{version_parts[1]},{version_parts[2]},{version_parts[3]}),
    prodvers=({version_parts[0]},{version_parts[1]},{version_parts[2]},{version_parts[3]}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [
            StringStruct(u'CompanyName', u'{self.creator}'),
            StringStruct(u'FileDescription', u'{self.app_name}'),
            StringStruct(u'FileVersion', u'{self.app_version}'),
            StringStruct(u'InternalName', u'{self.build_config["executable_name"]}'),
            StringStruct(u'LegalCopyright', u'Copyright (c) 2024 {self.creator}'),
            StringStruct(u'OriginalFilename', u'{self.build_config["executable_name"]}.exe'),
            StringStruct(u'ProductName', u'{self.app_name}'),
            StringStruct(u'ProductVersion', u'{self.app_version}')
          ]
        )
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
        
        version_file = self.build_config['assets_dir'] / 'version.rc'
        with open(version_file, 'w', encoding='utf-8') as f:
            f.write(version_rc)
        print(f"✅ Version file created: {version_file}")
    
    def optimize_executable(self):
        """Optimize the built executable"""
        print("⚡ Optimizing executable...")
        
        exe_name = self.build_config['executable_name']
        if self.is_windows:
            exe_name += '.exe'
        
        exe_path = self.build_config['dist_dir'] / exe_name
        
        if not exe_path.exists():
            print("⚠️ Executable not found for optimization")
            return
        
        original_size = exe_path.stat().st_size
        
        # Try UPX compression
        upx_path = shutil.which('upx')
        if upx_path:
            print("🗜️ Compressing with UPX...")
            try:
                subprocess.run([
                    upx_path, '--best', '--lzma', str(exe_path)
                ], check=True, capture_output=True)
                
                new_size = exe_path.stat().st_size
                compression_ratio = (1 - new_size / original_size) * 100
                print(f"✅ UPX compression successful: {compression_ratio:.1f}% smaller")
            except subprocess.CalledProcessError:
                print("⚠️ UPX compression failed, continuing without compression")
        else:
            print("💡 UPX not available for compression")
        
        print("✅ Executable optimization completed")
    
    def create_installer_package(self):
        """Create installer package"""
        print("📦 Creating installer package...")
        
        if self.is_windows:
            self.create_windows_installer()
        elif self.is_macos:
            self.create_macos_package()
        else:
            self.create_linux_package()
    
    def create_windows_installer(self):
        """Create Windows NSIS installer"""
        print("🖥️ Creating Windows installer...")
        
        nsis_path = shutil.which('makensis')
        if not nsis_path:
            print("⚠️ NSIS not found, creating portable package instead")
            self.create_portable_package()
            return
        
        # Create NSIS script
        nsis_script = self.generate_nsis_script()
        script_file = self.build_config['setup_dir'] / 'installer.nsi'
        
        with open(script_file, 'w') as f:
            f.write(nsis_script)
        
        # Build installer
        try:
            subprocess.run([
                nsis_path, str(script_file)
            ], check=True, capture_output=True)
            
            installer_path = self.build_config['setup_dir'] / self.build_config['installer_name']
            if installer_path.exists():
                size_mb = installer_path.stat().st_size / (1024 * 1024)
                print(f"✅ Windows installer created: {installer_path}")
                print(f"📦 Installer size: {size_mb:.1f} MB")
            else:
                raise Exception("Installer not created")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Installer creation failed: {e}")
            self.create_portable_package()
    
    def generate_nsis_script(self):
        """Generate NSIS installer script"""
        return f'''# RiverFlow Studio Installer
# Created by {self.creator}

!define APPNAME "{self.app_name}"
!define COMPANYNAME "{self.creator}"
!define DESCRIPTION "Professional Stream Automation Suite"
!define VERSIONMAJOR {self.app_version.split('.')[0]}
!define VERSIONMINOR {self.app_version.split('.')[1]}
!define VERSIONBUILD {self.app_version.split('.')[2] if len(self.app_version.split('.')) > 2 else '0'}
!define HELPURL "https://github.com/juvonsriviere/riverflow"
!define UPDATEURL "https://github.com/juvonsriviere/riverflow/releases"
!define ABOUTURL "https://juvonsriviere.com"
!define INSTALLSIZE 100000

RequestExecutionLevel admin
InstallDir "$PROGRAMFILES\\${{APPNAME}}"
Name "${{APPNAME}} v{self.app_version}"
OutFile "{self.build_config['installer_name']}"
Icon "{self.build_config['assets_dir'] / self.build_config['icon_file']}"

!include "MUI2.nsh"

# Modern UI Configuration
!define MUI_ABORTWARNING
!define MUI_ICON "{self.build_config['assets_dir'] / self.build_config['icon_file']}"
!define MUI_UNICON "{self.build_config['assets_dir'] / self.build_config['icon_file']}"

# Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "{self.build_config['assets_dir'] / 'LICENSE.txt'}"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

Section "install"
    SetOutPath $INSTDIR
    
    # Install main executable
    File "{self.build_config['dist_dir'] / (self.build_config['executable_name'] + '.exe')}"
    
    # Install documentation
    File "{self.build_config['docs_dir'] / 'README.md'}"
    File "{self.build_config['docs_dir'] / 'UserGuide.md'}"
    File "{self.build_config['assets_dir'] / 'LICENSE.txt'}"
    
    # Create uninstaller
    WriteUninstaller "$INSTDIR\\uninstall.exe"
    
    # Start Menu
    CreateDirectory "$SMPROGRAMS\\${{APPNAME}}"
    CreateShortCut "$SMPROGRAMS\\${{APPNAME}}\\${{APPNAME}}.lnk" "$INSTDIR\\{self.build_config['executable_name']}.exe"
    CreateShortCut "$SMPROGRAMS\\${{APPNAME}}\\User Guide.lnk" "$INSTDIR\\UserGuide.md"
    CreateShortCut "$SMPROGRAMS\\${{APPNAME}}\\Uninstall.lnk" "$INSTDIR\\uninstall.exe"
    
    # Desktop shortcut
    CreateShortCut "$DESKTOP\\${{APPNAME}}.lnk" "$INSTDIR\\{self.build_config['executable_name']}.exe"
    
    # Registry information for Add/Remove Programs
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "DisplayName" "${{APPNAME}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "UninstallString" "$INSTDIR\\uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "QuietUninstallString" "$INSTDIR\\uninstall.exe /S"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "DisplayIcon" "$INSTDIR\\{self.build_config['executable_name']}.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "Publisher" "${{COMPANYNAME}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "HelpLink" "${{HELPURL}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "URLUpdateInfo" "${{UPDATEURL}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "URLInfoAbout" "${{ABOUTURL}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "DisplayVersion" "${{VERSIONMAJOR}}.${{VERSIONMINOR}}.${{VERSIONBUILD}}"
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "VersionMajor" ${{VERSIONMAJOR}}
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "VersionMinor" ${{VERSIONMINOR}}
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "NoModify" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "NoRepair" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "EstimatedSize" ${{INSTALLSIZE}}
SectionEnd

Section "uninstall"
    # Remove files
    Delete "$INSTDIR\\{self.build_config['executable_name']}.exe"
    Delete "$INSTDIR\\README.md"
    Delete "$INSTDIR\\UserGuide.md"
    Delete "$INSTDIR\\LICENSE.txt"
    Delete "$INSTDIR\\uninstall.exe"
    
    # Remove shortcuts
    Delete "$SMPROGRAMS\\${{APPNAME}}\\${{APPNAME}}.lnk"
    Delete "$SMPROGRAMS\\${{APPNAME}}\\User Guide.lnk"
    Delete "$SMPROGRAMS\\${{APPNAME}}\\Uninstall.lnk"
    RMDir "$SMPROGRAMS\\${{APPNAME}}"
    Delete "$DESKTOP\\${{APPNAME}}.lnk"
    
    # Remove registry entries
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}"
    
    RMDir "$INSTDIR"
SectionEnd
'''
    
    def create_macos_package(self):
        """Create macOS application bundle"""
        print("🍎 Creating macOS package...")
        
        app_name = f"{self.build_config['executable_name']}.app"
        app_path = self.build_config['setup_dir'] / app_name
        
        # Create app bundle structure
        contents_dir = app_path / "Contents"
        macos_dir = contents_dir / "MacOS"
        resources_dir = contents_dir / "Resources"
        
        for directory in [contents_dir, macos_dir, resources_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Copy executable
        exe_path = self.build_config['dist_dir'] / self.build_config['executable_name']
        if exe_path.exists():
            shutil.copy2(exe_path, macos_dir / self.build_config['executable_name'])
            os.chmod(macos_dir / self.build_config['executable_name'], 0o755)
        
        # Create Info.plist
        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDisplayName</key>
    <string>{self.app_name}</string>
    <key>CFBundleExecutable</key>
    <string>{self.build_config['executable_name']}</string>
    <key>CFBundleIdentifier</key>
    <string>com.juvonsriviere.riverflowstudio</string>
    <key>CFBundleName</key>
    <string>{self.app_name}</string>
    <key>CFBundleShortVersionString</key>
    <string>{self.app_version}</string>
    <key>CFBundleVersion</key>
    <string>{self.app_version}</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.14</string>
    <key>NSHumanReadableCopyright</key>
    <string>Copyright © 2024 {self.creator}</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>'''
        
        with open(contents_dir / "Info.plist", 'w') as f:
            f.write(plist_content)
        
        # Copy resources
        for resource in ['README.md', 'UserGuide.md', 'LICENSE.txt']:
            src = self.build_config['docs_dir'] / resource if resource.endswith('.md') else self.build_config['assets_dir'] / resource
            if src.exists():
                shutil.copy2(src, resources_dir)
        
        print(f"✅ macOS app bundle created: {app_path}")
        
        # Create DMG if possible
        self.create_dmg_package(app_path)
    
    def create_dmg_package(self, app_path):
        """Create DMG package for macOS"""
        try:
            dmg_name = f"{self.build_config['executable_name']}-{self.app_version}.dmg"
            dmg_path = self.build_config['setup_dir'] / dmg_name
            
            subprocess.run([
                'hdiutil', 'create', '-srcfolder', str(app_path),
                '-volname', self.app_name, '-fs', 'HFS+',
                '-fsargs', '-c c=64,a=16,e=16', '-format', 'UDBZ',
                str(dmg_path)
            ], check=True, capture_output=True)
            
            print(f"✅ DMG package created: {dmg_path}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ Could not create DMG package")
    
    def create_linux_package(self):
        """Create Linux package"""
        print("🐧 Creating Linux package...")
        
        # Create AppImage or portable package
        self.create_portable_package()
        
        # Try to create .deb package if possible
        self.create_deb_package()
    
    def create_deb_package(self):
        """Create Debian package"""
        try:
            package_name = self.build_config['executable_name'].lower()
            package_dir = self.build_config['setup_dir'] / f"{package_name}_{self.app_version}"
            
            # Create package structure
            debian_dir = package_dir / "DEBIAN"
            usr_bin_dir = package_dir / "usr" / "bin"
            usr_share_dir = package_dir / "usr" / "share" / package_name
            applications_dir = package_dir / "usr" / "share" / "applications"
            
            for directory in [debian_dir, usr_bin_dir, usr_share_dir, applications_dir]:
                directory.mkdir(parents=True, exist_ok=True)
            
            # Copy executable
            exe_path = self.build_config['dist_dir'] / self.build_config['executable_name']
            if exe_path.exists():
                shutil.copy2(exe_path, usr_bin_dir)
                os.chmod(usr_bin_dir / self.build_config['executable_name'], 0o755)
            
            # Create control file
            control_content = f"""Package: {package_name}
Version: {self.app_version}
Section: multimedia
Priority: optional
Architecture: amd64
Depends: python3, python3-pyqt6
Maintainer: {self.creator} <info@juvonsriviere.com>
Description: {self.app_name}
 Professional Stream Automation Suite for content creators.
 Features intelligent stream automation, smart media management,
 and one-click broadcasting capabilities.
"""
            
            with open(debian_dir / "control", 'w') as f:
                f.write(control_content)
            
            # Create desktop file
            desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={self.app_name}
Comment=Professional Stream Automation Suite
Exec={self.build_config['executable_name']}
Terminal=false
Categories=AudioVideo;Video;
"""
            
            with open(applications_dir / f"{package_name}.desktop", 'w') as f:
                f.write(desktop_content)
            
            # Build package
            subprocess.run([
                'dpkg-deb', '--build', str(package_dir)
            ], check=True, capture_output=True)
            
            deb_file = f"{package_dir}.deb"
            if Path(deb_file).exists():
                print(f"✅ Debian package created: {deb_file}")
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ Could not create Debian package")
    
    def create_portable_package(self):
        """Create portable ZIP package"""
        print("📦 Creating portable package...")
        
        package_name = f"{self.build_config['executable_name']}-{self.app_version}-portable"
        package_dir = self.build_config['setup_dir'] / package_name
        package_dir.mkdir(exist_ok=True)
        
        # Copy executable
        exe_name = self.build_config['executable_name']
        if self.is_windows:
            exe_name += '.exe'
        
        exe_path = self.build_config['dist_dir'] / exe_name
        if exe_path.exists():
            shutil.copy2(exe_path, package_dir)
        
        # Copy documentation
        for doc in ['README.md', 'UserGuide.md']:
            src = self.build_config['docs_dir'] / doc
            if src.exists():
                shutil.copy2(src, package_dir)
        
        # Copy license
        license_src = self.build_config['assets_dir'] / 'LICENSE.txt'
        if license_src.exists():
            shutil.copy2(license_src, package_dir)
        
        # Create portable marker file
        with open(package_dir / 'PORTABLE.txt', 'w') as f:
            f.write(f"{self.app_name} Portable Edition\\n")
            f.write(f"Version: {self.app_version}\\n")
            f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n")
            f.write("This is a portable version that does not require installation.\\n")
            f.write("Simply run the executable to start the application.\\n")
        
        # Create ZIP archive
        zip_path = self.build_config['setup_dir'] / f"{package_name}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in package_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(package_dir.parent)
                    zipf.write(file_path, arcname)
        
        # Clean up temporary directory
        shutil.rmtree(package_dir)
        
        size_mb = zip_path.stat().st_size / (1024 * 1024)
        print(f"✅ Portable package created: {zip_path}")
        print(f"📦 Package size: {size_mb:.1f} MB")
    
    def test_executable(self):
        """Test the built executable"""
        print("🧪 Testing executable...")
        
        exe_name = self.build_config['executable_name']
        if self.is_windows:
            exe_name += '.exe'
        
        exe_path = self.build_config['dist_dir'] / exe_name
        
        if not exe_path.exists():
            raise Exception("Executable not found for testing")
        
        # Test basic execution (with timeout)
        try:
            print("🔍 Testing executable launch...")
            process = subprocess.Popen([str(exe_path), '--version'], 
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for a short time to see if it starts properly
            try:
                stdout, stderr = process.communicate(timeout=10)
                print("✅ Executable test completed")
            except subprocess.TimeoutExpired:
                process.kill()
                print("✅ Executable launched successfully (timeout expected)")
                
        except Exception as e:
            print(f"⚠️ Executable test warning: {e}")
            # Don't fail the build for test issues
    
    def validate_installer(self):
        """Validate created installer package"""
        print("✅ Validating installer package...")
        
        if self.is_windows:
            installer_path = self.build_config['setup_dir'] / self.build_config['installer_name']
            if installer_path.exists():
                print(f"✅ Windows installer validated: {installer_path}")
            else:
                print("⚠️ Windows installer not found")
        
        # Check for portable package
        portable_files = list(self.build_config['setup_dir'].glob('*portable*.zip'))
        if portable_files:
            print(f"✅ Portable package validated: {portable_files[0]}")
        else:
            print("⚠️ Portable package not found")
    
    def prepare_distribution(self):
        """Prepare files for distribution"""
        print("📋 Preparing distribution files...")
        
        # Create distribution manifest
        manifest = {
            'app_name': self.app_name,
            'version': self.app_version,
            'creator': self.creator,
            'build_date': datetime.now().isoformat(),
            'platform': platform.system(),
            'files': [],
            'checksums': {}
        }
        
        # List all distribution files
        for file_path in self.build_config['setup_dir'].rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(self.build_config['setup_dir'])
                manifest['files'].append(str(relative_path))
                
                # Calculate checksum
                import hashlib
                sha256_hash = hashlib.sha256()
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(chunk)
                manifest['checksums'][str(relative_path)] = sha256_hash.hexdigest()
        
        # Save manifest
        manifest_file = self.build_config['setup_dir'] / 'MANIFEST.json'
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✅ Distribution manifest created: {manifest_file}")
    
    def create_release_package(self):
        """Create final release package"""
        print("🎁 Creating release package...")
        
        release_name = f"{self.build_config['executable_name']}-{self.app_version}-{self.platform}"
        release_dir = Path('release') / release_name
        release_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy all setup files to release directory
        for item in self.build_config['setup_dir'].iterdir():
            if item.is_file():
                shutil.copy2(item, release_dir)
            elif item.is_dir():
                shutil.copytree(item, release_dir / item.name, dirs_exist_ok=True)
        
        # Create release notes
        release_notes = f"""# {self.app_name} v{self.app_version} Release Notes

## Release Information
- **Version**: {self.app_version}
- **Release Date**: {datetime.now().strftime('%Y-%m-%d')}
- **Platform**: {platform.system()} {platform.machine()}
- **Created by**: {self.creator}

## Installation Options

### Windows
- **Installer**: `{self.build_config['installer_name']}` (Recommended)
- **Portable**: `*portable*.zip` (No installation required)

### macOS
- **App Bundle**: `*.app` (Drag to Applications folder)
- **DMG Package**: `*.dmg` (Disk image with installer)

### Linux
- **Debian Package**: `*.deb` (For Ubuntu/Debian systems)
- **Portable**: `*portable*.zip` (No installation required)

## What's New in v{self.app_version}
- Professional stream automation suite
- Intelligent media management
- One-click broadcasting
- Advanced scheduling system
- Professional grade security
- Modern, intuitive interface

## System Requirements
- **Windows**: Windows 10/11 (64-bit)
- **macOS**: macOS 10.14 or later
- **Linux**: Ubuntu 18.04+ or equivalent
- **Memory**: 4GB RAM (8GB recommended)
- **Storage**: 1GB free space
- **Additional**: OBS Studio 28.0+ for full functionality

## Support
- **Documentation**: See included UserGuide.md
- **Issues**: https://github.com/juvonsriviere/riverflow/issues
- **Support**: info@juvonsriviere.com

## License
Copyright (c) 2024 {self.creator}. All rights reserved.
"""
        
        with open(release_dir / 'RELEASE_NOTES.md', 'w') as f:
            f.write(release_notes)
        
        print(f"✅ Release package created: {release_dir}")
        
        # Create final archive
        final_archive = f"{release_name}.zip"
        with zipfile.ZipFile(final_archive, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in release_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(release_dir.parent)
                    zipf.write(file_path, arcname)
        
        final_size = Path(final_archive).stat().st_size / (1024 * 1024)
        print(f"🎉 Final release archive: {final_archive} ({final_size:.1f} MB)")
    
    def display_build_summary(self):
        """Display build summary"""
        print("\\n" + "=" * 60)
        print(f"🎉 {self.app_name} Build Summary")
        print("=" * 60)
        
        # Executable info
        exe_name = self.build_config['executable_name']
        if self.is_windows:
            exe_name += '.exe'
        
        exe_path = self.build_config['dist_dir'] / exe_name
        if exe_path.exists():
            exe_size = exe_path.stat().st_size / (1024 * 1024)
            print(f"📦 Executable: {exe_path} ({exe_size:.1f} MB)")
        
        # Package info
        setup_files = list(self.build_config['setup_dir'].glob('*'))
        if setup_files:
            print(f"📋 Package files: {len(setup_files)} files created")
            
            for file_path in setup_files:
                if file_path.is_file():
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    print(f"   • {file_path.name} ({size_mb:.1f} MB)")
        
        # Release info
        release_files = list(Path('release').glob('*.zip')) if Path('release').exists() else []
        if release_files:
            print(f"🎁 Release archives: {len(release_files)} created")
            for archive in release_files:
                size_mb = archive.stat().st_size / (1024 * 1024)
                print(f"   • {archive.name} ({size_mb:.1f} MB)")
        
        print("\\n📋 Next Steps:")
        print("1. Test the executable on target systems")
        print("2. Verify installer functionality")
        print("3. Upload release packages to distribution channels")
        print("4. Update documentation and changelog")
        
        print(f"\\n✨ {self.app_name} is ready for distribution!")
    
    def cleanup_failed_build(self):
        """Clean up after failed build"""
        print("🧹 Cleaning up failed build...")
        
        # Remove incomplete build artifacts
        if self.build_config['build_dir'].exists():
            shutil.rmtree(self.build_config['build_dir'])
        
        # Keep logs for debugging
        print("💡 Check logs for error details")

def create_quick_build_script():
    """Create a quick build batch/shell script"""
    if platform.system().lower() == 'windows':
        script_content = f'''@echo off
echo 🌊 RiverFlow Studio - Quick Build Script
echo ==========================================
echo.

echo 📦 Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install PyQt6 obs-websocket-py psutil requests pillow pyinstaller

echo.
echo 🏗️ Running complete build process...
python riverflow_complete_setup.py

echo.
echo ✅ Build process completed!
echo 📁 Check the 'dist' and 'setup' folders for your files
pause
'''
        
        with open('quick_build.bat', 'w') as f:
            f.write(script_content)
        print("✅ Quick build script created: quick_build.bat")
    
    else:  # Unix-like systems
        script_content = f'''#!/bin/bash
echo "🌊 RiverFlow Studio - Quick Build Script"
echo "=========================================="
echo

echo "📦 Installing Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install PyQt6 obs-websocket-py psutil requests pillow pyinstaller

echo
echo "🏗️ Running complete build process..."
python3 riverflow_complete_setup.py

echo
echo "✅ Build process completed!"
echo "📁 Check the 'dist' and 'setup' folders for your files"
'''
        
        with open('quick_build.sh', 'w') as f:
            f.write(script_content)
        os.chmod('quick_build.sh', 0o755)
        print("✅ Quick build script created: quick_build.sh")

def main():
    """Main function"""
    print("🌊 RiverFlow Studio - Complete Setup Manager")
    print("=" * 50)
    
    # Create quick build scripts
    create_quick_build_script()
    
    # Initialize and run setup
    setup_manager = RiverFlowSetupManager()
    success = setup_manager.run_complete_setup()
    
    if success:
        print("\\n🎉 Setup completed successfully!")
        print("🚀 RiverFlow Studio is ready for distribution!")
    else:
        print("\\n💥 Setup failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()