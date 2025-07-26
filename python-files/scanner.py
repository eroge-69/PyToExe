import psutil
import os
import json
import time
from datetime import datetime
from collections import defaultdict
import sys

class KeyloggerDetector:
    def __init__(self):
        self.suspicious_processes = []
        self.suspicious_files = []
        self.suspicious_keywords = ['keylog', 'keystroke', 'key_capture', 'password_steal', 'hook_keyboard']
        self.whitelist = {'explorer.exe', 'dwm.exe', 'winlogon.exe', 'csrss.exe', 'svchost.exe'}
        
    def print_banner(self):
        print("\n" + "═" * 65)
        print("🔍 KEYLOGGER DETECTION TOOL")
        print("═" * 65)
        
    def print_progress(self, message, progress=None):
        if progress:
            bar = "█" * int(progress * 20) + "▒" * (20 - int(progress * 20))
            print(f"\r{message} [{bar}] {int(progress * 100)}%", end="", flush=True)
        else:
            print(f"🔎 {message}...")

    def scan_processes(self):
        self.print_progress("Scanning running processes")
        processes = list(psutil.process_iter(['pid', 'name', 'exe', 'cmdline']))
        
        for i, proc in enumerate(processes):
            try:
                info = proc.info
                if not info['name'] or info['name'].lower() in self.whitelist:
                    continue
                    
                score = 0
                reasons = []
                
                # Check process name
                name = info['name'].lower()
                for keyword in self.suspicious_keywords:
                    if keyword in name:
                        score += 3
                        reasons.append(f"Suspicious name: {keyword}")
                
                # Check command line
                if info['cmdline']:
                    cmdline = ' '.join(info['cmdline']).lower()
                    for keyword in self.suspicious_keywords:
                        if keyword in cmdline:
                            score += 2
                            reasons.append(f"Suspicious cmdline: {keyword}")
                
                # Check executable path
                if info['exe']:
                    exe_path = info['exe'].lower()
                    suspicious_paths = ['temp', 'downloads', 'appdata\\local\\temp']
                    for path in suspicious_paths:
                        if path in exe_path:
                            score += 2
                            reasons.append("Suspicious location")
                
                if score >= 3:
                    self.suspicious_processes.append({
                        'pid': info['pid'],
                        'name': info['name'],
                        'exe': info['exe'],
                        'score': score,
                        'reasons': reasons
                    })
                    
                # Progress bar
                progress = (i + 1) / len(processes)
                self.print_progress("Scanning processes", progress)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        print()  # New line after progress bar

    def scan_files(self):
        self.print_progress("Checking suspicious files")
        
        dirs = [
            os.path.expanduser("~\\AppData\\Local\\Temp"),
            os.path.expanduser("~\\AppData\\Roaming"),
            "C:\\Windows\\Temp"
        ]
        
        for directory in dirs:
            if not os.path.exists(directory):
                continue
                
            try:
                for root, _, files in os.walk(directory):
                    for file in files:
                        filepath = os.path.join(root, file)
                        try:
                            # Recent files only (last 24h)
                            if time.time() - os.path.getmtime(filepath) > 86400:
                                continue
                                
                            filename = file.lower()
                            # Check for suspicious patterns
                            if (any(kw in filename for kw in self.suspicious_keywords) or
                                (filename.endswith(('.log', '.txt', '.dat')) and os.path.getsize(filepath) > 1024)):
                                
                                self.suspicious_files.append({
                                    'path': filepath,
                                    'size': os.path.getsize(filepath),
                                    'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M')
                                })
                        except (OSError, PermissionError):
                            continue
            except (OSError, PermissionError):
                continue

    def save_report(self):
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'suspicious_processes': self.suspicious_processes,
            'suspicious_files': self.suspicious_files
        }
        
        filename = f"keylogger_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        return filename

    def display_results(self):
        print("\n" + "═" * 65)
        print("📊 SCAN RESULTS")
        print("═" * 65)
        
        # Processes
        if self.suspicious_processes:
            print(f"\n⚠️  SUSPICIOUS PROCESSES FOUND: {len(self.suspicious_processes)}")
            print("─" * 65)
            for proc in self.suspicious_processes:
                print(f"🔴 {proc['name']} (PID: {proc['pid']}) - Score: {proc['score']}/10")
                print(f"   Path: {proc['exe'] or 'Unknown'}")
                for reason in proc['reasons']:
                    print(f"   • {reason}")
                print()
        else:
            print("\n✅ No suspicious processes detected")
        
        # Files
        if self.suspicious_files:
            print(f"\n📁 SUSPICIOUS FILES FOUND: {len(self.suspicious_files)}")
            print("─" * 65)
            for file_info in self.suspicious_files[:10]:  # Show top 10
                print(f"📄 {os.path.basename(file_info['path'])}")
                print(f"   Size: {file_info['size']} bytes | Modified: {file_info['modified']}")
                print(f"   Path: {file_info['path'][:60]}...")
                print()
            
            if len(self.suspicious_files) > 10:
                print(f"   ... and {len(self.suspicious_files) - 10} more files")
        else:
            print("\n✅ No suspicious files detected")

    def run_scan(self):
        self.print_banner()
        
        try:
            # Run scans
            self.scan_processes()
            self.scan_files()
            
            # Display results
            self.display_results()
            
            # Save report
            report_file = self.save_report()
            
            print(f"\n💾 Full report saved: {report_file}")
            print("═" * 65)
            
            # Summary
            total_threats = len(self.suspicious_processes) + len(self.suspicious_files)
            if total_threats > 0:
                print(f"⚠️  ALERT: {total_threats} potential threats detected!")
                print("   Review the findings above and investigate suspicious items.")
            else:
                print("✅ System appears clean - no keyloggers detected.")
            
            print("═" * 65)
            
        except KeyboardInterrupt:
            print("\n\n❌ Scan interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Error during scan: {e}")
            sys.exit(1)

def main():
    if os.name != 'nt':
        print("❌ This tool is designed for Windows systems only.")
        return
    
    try:
        detector = KeyloggerDetector()
        detector.run_scan()
        
        input("\nPress Enter to exit...")
        
    except KeyboardInterrupt:
        print("\n\nGoodbye!")

if __name__ == "__main__":
    main()