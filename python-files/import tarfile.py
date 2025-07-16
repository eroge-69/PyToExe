import tarfile
import os
import re

# Patterns to flag for cybersecurity risks
CYBER_PATTERNS = [
    (r'\bgets\s*\(', "Use of 'gets' (unsafe function)"),
    (r'\bstrcpy\s*\(', "Use of 'strcpy' (potential buffer overflow)"),
    (r'\bsprintf\s*\(', "Use of 'sprintf' (potential buffer overflow)"),
    (r'\bscanf\s*\(', "Use of 'scanf' (potential format string vulnerability)"),
    (r'password\s*=', "Hardcoded password assignment"),
    (r'passwd\s*=', "Hardcoded password assignment"),
    (r'key\s*=', "Hardcoded key assignment"),
    (r'\bmemcpy\s*\(', "Use of 'memcpy' (potential buffer overflow)"),
    (r'\bsystem\s*\(', "Use of 'system' (command injection risk)"),
    (r'\bfopen\s*\(', "Use of 'fopen' (file access risk)"),
    (r'\bstrcat\s*\(', "Use of 'strcat' (potential buffer overflow)"),
    (r'//\s*TODO', "TODO comment (potential unfinished security work)"),
    (r'//\s*FIXME', "FIXME comment (potential known issue)"),
    (r'//\s*HACK', "HACK comment (potential workaround)"),
]

def extract_tarball(tarball_path, extract_path):
    with tarfile.open(tarball_path, "r:gz") as tar:
        tar.extractall(path=extract_path)

def scan_c_files(extract_path):
    findings = []
    for root, dirs, files in os.walk(extract_path):
        for file in files:
            if file.endswith('.c'):
                file_path = os.path.join(root, file)
                with open(file_path, encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for pattern, description in CYBER_PATTERNS:
                        for match in re.finditer(pattern, content):
                            line_num = content[:match.start()].count('\n') + 1
                            findings.append({
                                'file': file_path,
                                'line': line_num,
                                'description': description,
                                'snippet': content[match.start():match.end()+40].split('\n')[0]
                            })
    return findings

if __name__ == "__main__":
    tarball_path = input("Enter path to the .tar.gz file: ").strip()
    extract_path = "extracted_tarball"
    print("Extracting tarball...")
    extract_tarball(tarball_path, extract_path)
    print("Scanning C files for cybersecurity risks...")
    findings = scan_c_files(extract_path)
    if findings:
        print(f"\nCybersecurity Findings ({len(findings)} issues found):")
        for f in findings:
            print(f"File: {f['file']}, Line: {f['line']}, Issue: {f['description']}")
            print(f"  Code: {f['snippet']}\n")
    else:
        print("No cybersecurity issues detected in C files.")