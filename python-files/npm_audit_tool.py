"""
npm & React Audit GUI (single-file)

Features:
- Select a project folder (where package.json lives)
- Run `npm audit --json` even without package-lock.json
- Show vulnerabilities in a table (package, severity, title, version, path, recommendation)
- Progress bar and log area
- Export results to CSV, TXT and PDF
- Automatic detection of npm path
- Works with or without package-lock.json
- Improved version detection
- Complete PDF reports with wrapped text

Dependencies:
- Python 3.8+
- PyQt5 (pip install PyQt5)
- reportlab (optional, for PDF export) (pip install reportlab)
"""

import sys
import os
import subprocess
import json
import csv
import datetime
import platform
import winreg  # Only for Windows
import re
import traceback
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QLabel, QProgressBar, QTextEdit, QTableWidget,
    QTableWidgetItem, QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# Try to import reportlab for PDF export
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, 
        PageBreak, KeepTogether
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class AuditWorker(QThread):
    started_run = pyqtSignal()
    finished_run = pyqtSignal(dict)
    log = pyqtSignal(str)
    progress_update = pyqtSignal(int)

    def __init__(self, project_path: str, npm_path: str):
        super().__init__()
        self.project_path = project_path
        self.npm_path = npm_path
        self.abort = False

    def run_npm_command(self, command, args, cwd=None):
        """Run npm command with proper environment setup"""
        cmd = [self.npm_path] + command + args
        self.log.emit(f"Running: {' '.join(cmd)} in {cwd or self.project_path}")
        
        creation_flags = 0
        if platform.system() == "Windows":
            creation_flags = subprocess.CREATE_NO_WINDOW
        
        try:
            proc = subprocess.run(
                cmd,
                cwd=cwd or self.project_path,
                capture_output=True,
                text=True,
                timeout=300,
                encoding='utf-8',
                creationflags=creation_flags
            )
            return proc
        except Exception as e:
            self.log.emit(f"Error running npm command: {str(e)}")
            return None

    def run(self):
        self.started_run.emit()
        self.progress_update.emit(10)
        
        # Check if we should abort
        if self.abort:
            self.log.emit("Audit aborted by user")
            self.finished_run.emit({"error": "aborted"})
            return

        # 1. Run npm audit directly without requiring package-lock.json
        self.log.emit("Running npm audit...")
        self.progress_update.emit(50)
        
        audit_proc = self.run_npm_command(['audit'], ['--json'])
        if audit_proc is None:
            self.finished_run.emit({"error": "npm_audit_failed"})
            return
        
        # npm audit may return 1 if vulnerabilities are found, which is acceptable
        if audit_proc.returncode not in (0, 1):
            self.log.emit(f"npm audit returned code {audit_proc.returncode}. stderr:\n{audit_proc.stderr}\n")
        
        # Check if we have valid output
        if not audit_proc.stdout.strip():
            # Try to run audit with --production flag if first attempt fails
            self.log.emit("No output from npm audit. Trying with --production flag...")
            audit_proc = self.run_npm_command(['audit'], ['--json', '--production'])
            
            if not audit_proc.stdout.strip():
                self.log.emit("Still no output from npm audit.\n")
                self.finished_run.emit({"error": "no_output", "stderr": audit_proc.stderr})
                return

        try:
            data = json.loads(audit_proc.stdout)
        except json.JSONDecodeError as e:
            self.log.emit(f"Failed to parse npm audit JSON: {e}\nstdout:\n{audit_proc.stdout}\n")
            self.finished_run.emit({
                "error": "json_error", 
                "stderr": audit_proc.stderr, 
                "stdout": audit_proc.stdout
            })
            return
        
        self.log.emit("npm audit JSON parsed successfully.\n")
        self.progress_update.emit(90)
        self.finished_run.emit({"data": data})


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NPM / React Audit GUI")
        self.resize(1200, 800)

        self.project_path = None
        self.audit_data = None
        self.vulnerabilities = []
        self.npm_path = self.find_npm_path()
        self.worker = None

        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout()
        root.setLayout(layout)

        # Top controls
        top_row = QHBoxLayout()
        layout.addLayout(top_row)

        self.path_label = QLabel("Project: (not selected)")
        top_row.addWidget(self.path_label)

        btn_browse = QPushButton("Select Project")
        btn_browse.clicked.connect(self.select_project)
        top_row.addWidget(btn_browse)

        btn_run = QPushButton("Run npm audit")
        btn_run.clicked.connect(self.run_audit)
        top_row.addWidget(btn_run)
        
        btn_abort = QPushButton("Abort")
        btn_abort.clicked.connect(self.abort_audit)
        top_row.addWidget(btn_abort)

        # Export buttons
        export_layout = QHBoxLayout()
        top_row.addLayout(export_layout)
        
        btn_export_csv = QPushButton("Export CSV")
        btn_export_csv.clicked.connect(self.export_csv)
        export_layout.addWidget(btn_export_csv)

        btn_export_txt = QPushButton("Export TXT")
        btn_export_txt.clicked.connect(self.export_txt)
        export_layout.addWidget(btn_export_txt)

        btn_export_pdf = QPushButton("Export PDF")
        btn_export_pdf.clicked.connect(self.export_pdf)
        export_layout.addWidget(btn_export_pdf)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        # Results table
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "Package", "Severity", "Title", "Installed", "Path", "Recommendation"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table, 1)

        # Bottom area
        bottom = QHBoxLayout()
        layout.addLayout(bottom)

        # Log area
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(150)
        bottom.addWidget(self.log, 2)

        # Help panel
        help_col = QVBoxLayout()
        bottom.addLayout(help_col, 1)
        
        help_label = QLabel(
            "<b>Important Notes:</b>"
            "<ul>"
            "<li>This tool requires Node.js and npm installed</li>"
            "<li>Works with or without package-lock.json</li>"
            "<li>NPM Path: " + (self.npm_path if self.npm_path else "Not found!") + "</li>"
            "</ul>"
            "<b>How to use:</b>"
            "<ol>"
            "<li>Select project folder containing package.json</li>"
            "<li>Click 'Run npm audit'</li>"
            "<li>Review vulnerabilities in table</li>"
            "<li>Export results to CSV/TXT/PDF if needed</li>"
            "</ol>"
        )
        help_label.setWordWrap(True)
        help_label.setTextFormat(Qt.RichText)
        help_col.addWidget(help_label)

    def find_npm_path(self):
        """Find npm path using multiple methods"""
        # Try common locations first
        common_paths = [
            # Windows
            os.path.join(os.environ.get('ProgramFiles', ''), 'nodejs', 'npm.cmd'),
            os.path.join(os.environ.get('ProgramFiles(x86)', ''), 'nodejs', 'npm.cmd'),
            # Unix/Mac
            '/usr/local/bin/npm',
            '/usr/bin/npm',
            os.path.expanduser('~/.nvm/versions/node/*/bin/npm'),
            # Global npm
            os.path.join(os.environ.get('APPDATA', ''), 'npm', 'npm.cmd'),
        ]
        
        for path in common_paths:
            if '*' in path:
                # Handle glob patterns
                import glob
                matches = glob.glob(path)
                if matches and os.path.isfile(matches[0]):
                    return matches[0]
            elif os.path.isfile(path):
                return path
        
        # Try environment PATH
        for path_dir in os.environ['PATH'].split(os.pathsep):
            candidate = os.path.join(path_dir, 'npm')
            if os.path.isfile(candidate):
                return candidate
            # Windows specific
            if platform.system() == "Windows":
                candidate_cmd = candidate + '.cmd'
                if os.path.isfile(candidate_cmd):
                    return candidate_cmd
        
        # Try shell command
        try:
            if platform.system() == "Windows":
                cmd = "where npm"
            else:
                cmd = "which npm"
                
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                path = result.stdout.splitlines()[0].strip()
                if os.path.isfile(path):
                    return path
        except Exception:
            pass
        
        return None

    def select_project(self):
        path = QFileDialog.getExistingDirectory(
            self, 
            "Select project folder",
            os.path.expanduser("~")  # Start at user home directory
        )
        if path:
            p = Path(path)
            if not (p / 'package.json').exists():
                res = QMessageBox.question(
                    self,
                    "No package.json found",
                    "Selected folder has no package.json. Continue anyway?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if res == QMessageBox.No:
                    return
            self.project_path = str(p)
            self.path_label.setText(f"Project: {self.project_path}")
            self.log.append(f"Selected project: {self.project_path}")

    def run_audit(self):
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "Audit in progress", "An audit is already running. Please wait or abort first.")
            return
            
        if not self.project_path:
            QMessageBox.warning(self, "No project", "Please select a project folder first.")
            return
        
        if not Path(self.project_path).exists():
            QMessageBox.critical(self, "Invalid path", "The selected project path does not exist.")
            return
        
        # Check npm path
        if not self.npm_path or not os.path.isfile(self.npm_path):
            QMessageBox.critical(
                self,
                "npm not found",
                "npm executable could not be found. Please ensure Node.js is installed and in your PATH."
            )
            return
            
        self.progress.setValue(5)
        self.table.setRowCount(0)
        self.log.append("Starting npm audit process...\n")
        self.log.append(f"Using npm at: {self.npm_path}\n")
        
        self.worker = AuditWorker(self.project_path, self.npm_path)
        self.worker.started_run.connect(lambda: self.progress.setValue(10))
        self.worker.log.connect(lambda s: self.log.append(s))
        self.worker.progress_update.connect(self.progress.setValue)
        self.worker.finished_run.connect(self.on_audit_finished)
        self.worker.start()
        
    def abort_audit(self):
        if self.worker and self.worker.isRunning():
            self.worker.abort = True
            self.log.append("Requested audit abort...")
            self.worker.terminate()  # Force stop if needed
            self.progress.setValue(0)
            self.log.append("Audit aborted by user")
        else:
            QMessageBox.information(self, "No active audit", "There is no audit running to abort.")

    def on_audit_finished(self, result: dict):
        if 'error' in result:
            err = result.get('error')
            if err == 'npm_not_found':
                QMessageBox.critical(
                    self,
                    "npm not found",
                    "npm not found in PATH. Install Node.js/npm or make sure it's available."
                )
            elif err == 'timeout':
                QMessageBox.warning(
                    self,
                    "Audit timed out",
                    "npm audit took too long to complete (5 minutes)."
                )
            elif err == 'no_output':
                QMessageBox.warning(
                    self,
                    "No audit output",
                    "npm audit did not produce any output. This may happen if:\n"
                    "- There are no dependencies in the project\n"
                    "- The project has no vulnerabilities\n"
                    "- npm audit is not working properly in your environment\n\n"
                    "Try running 'npm audit --json' manually in the project directory."
                )
            elif err == 'aborted':
                self.log.append("Audit was aborted by user")
            else:
                QMessageBox.critical(
                    self,
                    "Audit error",
                    f"Error occurred during audit: {err}\nSee log for details."
                )
            self.progress.setValue(0)
            return

        data = result.get('data')
        if data is None:
            QMessageBox.critical(self, "No data", "No audit data returned.")
            self.progress.setValue(0)
            return

        self.audit_data = data
        self.vulnerabilities = self.parse_vulnerabilities(data)
        self.populate_table(self.vulnerabilities)
        self.progress.setValue(100)
        
        if self.vulnerabilities:
            self.log.append(f"Audit finished. Found {len(self.vulnerabilities)} vulnerabilities.\n")
        else:
            self.log.append("Audit finished. No vulnerabilities found.\n")

    def parse_vulnerabilities(self, data: dict):
        vulns = []
        total_vulns = 0

        # npm v6 format
        if 'advisories' in data and isinstance(data['advisories'], dict):
            for aid, adv in data['advisories'].items():
                pkg = adv.get('module_name', '') or adv.get('package_name', '')
                sev = adv.get('severity', 'unknown').capitalize()
                title = adv.get('title', '') or adv.get('overview', 'No title')
                
                # Extract installed version - improved method
                installed = 'unknown'
                
                # Method 1: From findings
                if 'findings' in adv and adv['findings']:
                    for finding in adv['findings']:
                        if 'version' in finding:
                            installed = finding['version']
                            break
                
                # Method 2: From installed_version
                if installed == 'unknown' and 'installed_version' in adv:
                    installed = adv['installed_version']
                
                # Method 3: From paths
                paths = set()
                for finding in adv.get('findings', []):
                    if 'paths' in finding:
                        paths.update(finding['paths'])
                
                # Extract version from path if not found
                if installed == 'unknown' and paths:
                    for path_str in paths:
                        # Improved regex to capture versions with various formats
                        match = re.search(r'@([\w.+-]+)(?=[\\/]|$)', path_str)
                        if match:
                            installed = match.group(1)
                            break
                
                # Extract recommendation
                recommendation = adv.get('recommendation', '')
                if not recommendation and 'patched_versions' in adv:
                    recommendation = f"Upgrade to {adv['patched_versions']}"
                elif not recommendation and 'url' in adv:
                    recommendation = f"See: {adv['url']}"
                
                vulns.append({
                    'package': pkg,
                    'severity': sev,
                    'title': title,
                    'installed': installed,
                    'path': '\n'.join(sorted(paths)) if paths else 'Not specified',
                    'recommendation': recommendation or "No recommendation"
                })
                total_vulns += 1

        # npm v7+ format
        elif 'vulnerabilities' in data and isinstance(data['vulnerabilities'], dict):
            for pkg_name, vuln_info in data['vulnerabilities'].items():
                via = vuln_info.get('via', [])
                severity = vuln_info.get('severity', 'unknown').capitalize()
                
                # Extract installed version - improved method
                installed = vuln_info.get('version', 'unknown')
                
                # Handle multiple vulnerability paths
                paths = set()
                for node in vuln_info.get('nodes', []):
                    if isinstance(node, dict) and 'name' in node:
                        paths.add(node['name'])
                    elif isinstance(node, str):
                        paths.add(node)
                
                # Extract version from path if not found
                if installed == 'unknown' and paths:
                    for path_str in paths:
                        # Improved regex to capture versions with various formats
                        match = re.search(r'@([\w.+-]+)(?=[\\/]|$)', path_str)
                        if match:
                            installed = match.group(1)
                            break
                
                # Collect recommendations
                recommendations = set()
                for item in via:
                    if isinstance(item, dict):
                        if item.get('recommendation'):
                            recommendations.add(item['recommendation'])
                        elif item.get('url'):
                            recommendations.add(f"See: {item['url']}")
                
                title = f"Vulnerability in {pkg_name}"
                if via:
                    if isinstance(via[0], dict):
                        title = via[0].get('title', title)
                    elif isinstance(via[0], str):
                        title = via[0]
                
                vulns.append({
                    'package': pkg_name,
                    'severity': severity,
                    'title': title,
                    'installed': installed,
                    'path': '\n'.join(sorted(paths)) if paths else 'Not specified',
                    'recommendation': '\n'.join(recommendations) if recommendations else "No recommendation"
                })
                total_vulns += 1

        # Fallback for other formats
        elif 'actions' in data:
            for action in data.get('actions', []):
                for resolve in action.get('resolves', []):
                    pkg = resolve.get('id', 'Unknown')
                    severity = resolve.get('severity', 'unknown').capitalize()
                    title = resolve.get('title', 'No title')
                    installed = resolve.get('version', 'unknown')
                    path = resolve.get('path', 'Not specified')
                    recommendation = resolve.get('recommendation', 'No recommendation')
                    
                    # Extract version from path if not found
                    if installed == 'unknown' and path:
                        match = re.search(r'@([\w.+-]+)(?=[\\/]|$)', path)
                        if match:
                            installed = match.group(1)
                    
                    vulns.append({
                        'package': pkg,
                        'severity': severity,
                        'title': title,
                        'installed': installed,
                        'path': path,
                        'recommendation': recommendation
                    })
                    total_vulns += 1

        if total_vulns == 0:
            self.log.append("No vulnerabilities found.\n")
            return []

        # Sort by severity (critical first)
        severity_order = {'Critical': 0, 'High': 1, 'Moderate': 2, 'Low': 3, 'Unknown': 4}
        vulns.sort(key=lambda x: severity_order.get(x['severity'], 5))
        
        return vulns

    def populate_table(self, vulns):
        self.table.setRowCount(len(vulns))
        for i, vuln in enumerate(vulns):
            self.table.setItem(i, 0, QTableWidgetItem(vuln['package']))
            
            # Color code severity
            severity_item = QTableWidgetItem(vuln['severity'])
            if vuln['severity'] == 'Critical':
                severity_item.setBackground(Qt.red)
                severity_item.setForeground(Qt.white)
            elif vuln['severity'] == 'High':
                severity_item.setBackground(Qt.darkRed)
                severity_item.setForeground(Qt.white)
            elif vuln['severity'] == 'Moderate':
                severity_item.setBackground(Qt.yellow)
            elif vuln['severity'] == 'Low':
                severity_item.setBackground(Qt.green)
            self.table.setItem(i, 1, severity_item)
            
            self.table.setItem(i, 2, QTableWidgetItem(vuln['title']))
            self.table.setItem(i, 3, QTableWidgetItem(vuln['installed']))
            self.table.setItem(i, 4, QTableWidgetItem(vuln['path']))
            self.table.setItem(i, 5, QTableWidgetItem(vuln['recommendation']))
        
        # Auto resize columns
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

    def export_csv(self):
        if not self.vulnerabilities:
            QMessageBox.warning(self, "No data", "No vulnerabilities to export. Run an audit first.")
            return
            
        default_name = f"npm_audit_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save CSV Report",
            os.path.join(os.path.expanduser("~"), default_name),
            "CSV Files (*.csv)"
        )
        
        if not path:
            return
            
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Package", "Severity", "Title", 
                    "Installed Version", "Path", "Recommendation"
                ])
                
                for vuln in self.vulnerabilities:
                    writer.writerow([
                        vuln['package'],
                        vuln['severity'],
                        vuln['title'],
                        vuln['installed'],
                        vuln['path'].replace('\n', '; '),
                        vuln['recommendation']
                    ])
                    
            QMessageBox.information(
                self,
                "Export Successful",
                f"CSV report saved to:\n{path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Error saving CSV file:\n{str(e)}"
            )

    def export_txt(self):
        """Export vulnerabilities to a text file"""
        if not self.vulnerabilities:
            QMessageBox.warning(self, "No data", "No vulnerabilities to export. Run an audit first.")
            return
            
        default_name = f"npm_audit_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save TXT Report",
            os.path.join(os.path.expanduser("~"), default_name),
            "Text Files (*.txt)"
        )
        
        if not path:
            return
            
        try:
            with open(path, 'w', encoding='utf-8') as f:
                # Write header
                f.write("=" * 80 + "\n")
                f.write(f"NPM AUDIT REPORT\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Project: {self.project_path or 'Not specified'}\n")
                f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total vulnerabilities: {len(self.vulnerabilities)}\n")
                f.write(f"NPM Path: {self.npm_path or 'Not found'}\n\n")
                
                # Write vulnerabilities
                for i, vuln in enumerate(self.vulnerabilities):
                    f.write("-" * 80 + "\n")
                    f.write(f"Vulnerability #{i+1}\n")
                    f.write("-" * 80 + "\n")
                    f.write(f"Package: {vuln['package']}\n")
                    f.write(f"Severity: {vuln['severity']}\n")
                    f.write(f"Title: {vuln['title']}\n")
                    f.write(f"Installed Version: {vuln['installed']}\n")
                    f.write(f"Path:\n{vuln['path']}\n")
                    f.write(f"Recommendation:\n{vuln['recommendation']}\n\n")
                
                f.write("=" * 80 + "\n")
                f.write(f"Report generated by NPM Audit GUI Tool\n")
                f.write("=" * 80 + "\n")
                    
            QMessageBox.information(
                self,
                "Export Successful",
                f"TXT report saved to:\n{path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Error saving TXT file:\n{str(e)}"
            )

    def export_pdf(self):
        if not self.vulnerabilities:
            QMessageBox.warning(self, "No data", "No vulnerabilities to export. Run an audit first.")
            return
            
        if not REPORTLAB_AVAILABLE:
            res = QMessageBox.question(
                self,
                "PDF Export Unavailable",
                "ReportLab is not installed. Install it with 'pip install reportlab' for PDF export.\n\n"
                "Would you like to export as TXT instead?",
                QMessageBox.Yes | QMessageBox.No
            )
            if res == QMessageBox.Yes:
                self.export_txt()
            return
            
        default_name = f"npm_audit_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF Report",
            os.path.join(os.path.expanduser("~"), default_name),
            "PDF Files (*.pdf)"
        )
        
        if not path:
            return
            
        try:
            # Register DejaVu font for better Unicode support
            try:
                from reportlab.pdfbase.ttfonts import TTFont
                from reportlab.pdfbase import pdfmetrics
                pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
                pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
                default_font = 'DejaVuSans'
            except:
                default_font = 'Helvetica'
            
            # Create PDF document with proper margins
            doc = SimpleDocTemplate(
                path,
                pagesize=letter,
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=40
            )
            
            elements = []
            styles = getSampleStyleSheet()
            
            # Add custom styles
            styles.add(ParagraphStyle(
                name='VulnerabilityTitle',
                parent=styles['Heading3'],
                fontName='Helvetica-Bold',
                fontSize=12,
                spaceAfter=6
            ))
            
            styles.add(ParagraphStyle(
                name='VulnerabilityDetail',
                parent=styles['Normal'],
                fontName=default_font,
                fontSize=10,
                leading=12,
                spaceAfter=3
            ))
            
            styles.add(ParagraphStyle(
                name='Metadata',
                parent=styles['Normal'],
                fontName=default_font,
                fontSize=10,
                leading=14
            ))
            
            # Title
            title = Paragraph(f"<b>NPM Audit Report</b>", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 0.2 * inch))
            
            # Metadata
            metadata_table = [
                ["Project:", self.project_path or 'Not specified'],
                ["Date:", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                ["Total vulnerabilities:", str(len(self.vulnerabilities))],
                ["NPM Path:", self.npm_path or 'Not found']
            ]
            
            # Create metadata table
            meta_data = []
            for row in metadata_table:
                meta_data.append([
                    Paragraph(f"<b>{row[0]}</b>", styles['Metadata']),
                    Paragraph(row[1], styles['Metadata'])
                ])
            
            meta_table = Table(meta_data, colWidths=[100, None])
            meta_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
                ('FONT', (1, 0), (1, -1), default_font, 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            
            elements.append(meta_table)
            elements.append(Spacer(1, 0.3 * inch))
            
            # Vulnerability summary
            elements.append(Paragraph(f"<b>Vulnerabilities Found ({len(self.vulnerabilities)}):</b>", styles['Heading2']))
            elements.append(Spacer(1, 0.1 * inch))
            
            # Detailed vulnerability list
            for i, vuln in enumerate(self.vulnerabilities):
                # Create vulnerability block
                vuln_elements = [
                    Paragraph(f"{i+1}. <b>{vuln['package']}</b> (<font color='{self.get_severity_color(vuln['severity'])}'>{vuln['severity']}</font>)", 
                              styles['VulnerabilityTitle']),
                    Paragraph(f"<b>Title:</b> {vuln['title']}", styles['VulnerabilityDetail']),
                    Paragraph(f"<b>Installed Version:</b> {vuln['installed']}", styles['VulnerabilityDetail']),
                    Paragraph(f"<b>Path:</b> {vuln['path']}", styles['VulnerabilityDetail']),
                    Paragraph(f"<b>Recommendation:</b> {vuln['recommendation']}", styles['VulnerabilityDetail']),
                    Spacer(1, 0.1 * inch)
                ]
                
                # Keep vulnerability details together on one page
                elements.append(KeepTogether(vuln_elements))
            
            # Footer note
            elements.append(Spacer(1, 0.2 * inch))
            footer = Paragraph(
                "<i>Generated by NPM Audit GUI Tool</i>",
                styles['Italic']
            )
            elements.append(footer)
            
            # Build PDF
            doc.build(elements)
            
            QMessageBox.information(
                self,
                "Export Successful",
                f"PDF report saved to:\n{path}"
            )
        except Exception as e:
            error_msg = f"Error saving PDF file:\n{str(e)}\n\n{traceback.format_exc()}"
            QMessageBox.critical(
                self,
                "Export Failed",
                error_msg
            )

    def get_severity_color(self, severity):
        """Get color for severity level"""
        colors = {
            'Critical': 'red',
            'High': 'darkred',
            'Moderate': 'orange',
            'Low': 'green',
            'Unknown': 'gray'
        }
        return colors.get(severity, 'black')


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application font
    font = app.font()
    font.setPointSize(10)
    app.setFont(font)
    
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()