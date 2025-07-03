import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import sv_ttk
from PIL import Image, ImageTk
import subprocess
import os
import threading
import json
import io
import requests
import time
import re
import os
import sys
import shutil
import subprocess
import zipfile
import requests
import darkdetect
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import winreg

# queueItems - stores queue items
queueItems = []
queueVisible = True

def browseFolder():
    folder = filedialog.askdirectory()
    if folder:
        pathVar.set(folder)

def getVideoInfo(url):
    try:
        result = subprocess.run(
            ["yt-dlp", "-J", url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return json.loads(result.stdout)
    except:
        return None

class DependencyChecker:
    def __init__(self):
        self.requiredPackages = [
            'tkinter',
            'PIL',
            'sv_ttk',
            'requests',
            'pathlib'
        ]
        
        self.pipPackages = [
            'Pillow',
            'sv-ttk',
            'requests'
        ]
        
        self.missingPackages = []
        self.failedImports = []
        
    def checkPython(self):
        """Check if Python version is compatible"""
        pythonVersion = sys.version_info
        if pythonVersion.major < 3 or (pythonVersion.major == 3 and pythonVersion.minor < 7):
            print(f"❌ Python {pythonVersion.major}.{pythonVersion.minor} detected. Python 3.7+ required.")
            return False
        print(f"✅ Python {pythonVersion.major}.{pythonVersion.minor}.{pythonVersion.micro} detected.")
        return True
    
    def checkPackage(self, packageName):
        """Check if a package can be imported"""
        try:
            importlib.import_module(packageName)
            print(f"✅ {packageName} is available")
            return True
        except ImportError:
            print(f"❌ {packageName} is missing")
            self.failedImports.append(packageName)
            return False
    
    def checkSystemDependencies(self):
        """Check for system-level dependencies"""
        print("🔍 Checking system dependencies...")
        
        # Check for Windows registry access (for winreg)
        try:
            import winreg
            print("Windows registry access available")
        except ImportError:
            print("Windows registry access not available (non-Windows system)")
        
        return True
    
    def installMissingPackages(self):
        """Install missing packages via pip"""
        if not self.failedImports:
            return True
            
        print("\n📦 Installing missing packages...")
        
        packageMap = {
            'PIL': 'Pillow',
            'sv_ttk': 'sv-ttk'
        }
        
        for package in self.failedImports:
            if package in ['tkinter', 'pathlib']:
                print(f"⚠️  {package} is a built-in module - check Python installation")
                continue
                
            pipPackage = packageMap.get(package, package)
            
            try:
                print(f"Installing {pipPackage}...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', pipPackage])
                print(f"✅ {pipPackage} installed successfully")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {pipPackage}")
                self.missingPackages.append(pipPackage)
        
        return len(self.missingPackages) == 0
    
    def verifyInstallation(self):
        """Verify all packages can be imported after installation"""
        print("\n🔍 Verifying installation...")
        allGood = True
        
        for package in self.requiredPackages:
            if not self.checkPackage(package):
                allGood = False
        
        return allGood
    
    def showErrorDialog(self):
        """Show error dialog for missing dependencies"""
        try:
            root = tk.Tk()
            root.withdraw()
            
            errorMsg = "Missing dependencies detected:\n\n"
            errorMsg += "\n".join([f"• {pkg}" for pkg in self.missingPackages])
            errorMsg += "\n\nPlease install them manually using:\n"
            errorMsg += f"pip install {' '.join(self.missingPackages)}"
            
            messagebox.showerror("Dependency Error", errorMsg)
            root.destroy()
        except:
            print("Could not show GUI error dialog")
    
    def runCheck(self):
        """Run complete dependency check"""
        print("🚀 Starting dependency check...\n")
        
        if not self.checkPython():
            return False
        
        print("\n🔍 Checking required packages...")
        for package in self.requiredPackages:
            self.checkPackage(package)
        
        self.checkSystemDependencies()
        
        if self.failedImports:
            print(f"\n⚠️  Found {len(self.failedImports)} missing packages")
            
            userInput = input("Install missing packages automatically? (y/n): ").lower()
            if userInput == 'y':
                if self.installMissingPackages():
                    if self.verifyInstallation():
                        print("\n✅ All dependencies satisfied!")
                        return True
                    else:
                        print("\n❌ Some packages still missing after installation")
                        self.showErrorDialog()
                        return False
                else:
                    print("\n❌ Failed to install some packages")
                    self.showErrorDialog()
                    return False
            else:
                print("\n❌ Cannot proceed without required dependencies")
                self.showErrorDialog()
                return False
        else:
            print("\n✅ All dependencies satisfied!")
            return True

def getAvailableFormats(url):
    """Get available formats for a video"""
    try:
        result = subprocess.run(
            ["yt-dlp", "-F", url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return result.stdout
    except:
        return None

def isPlaylist(url):
    """Check if URL is a playlist"""
    try:
        result = subprocess.run(
            ["yt-dlp", "--flat-playlist", "-J", url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        data = json.loads(result.stdout)
        return data.get('_type') == 'playlist'
    except:
        return False

def parseVideoFormats(formatOutput):
    """Parse video formats from yt-dlp output"""
    formats = []
    lines = formatOutput.split('\n')
    
    for line in lines:
        if any(ext in line for ext in ['mp4', 'webm', 'mkv']) and 'video' in line.lower():
            parts = line.split()
            if len(parts) >= 3:
                formatId = parts[0]
                # Look for resolution pattern
                resMatch = re.search(r'(\d+)x(\d+)', line)
                if resMatch:
                    width, height = resMatch.groups()
                    quality = f"{height}p"
                    formats.append((formatId, quality, line.strip()))
                else:
                    # Try to find height pattern like "720p"
                    heightMatch = re.search(r'(\d+)p', line)
                    if heightMatch:
                        height = heightMatch.group(1)
                        quality = f"{height}p"
                        formats.append((formatId, quality, line.strip()))
    
    # Remove duplicates and sort by quality
    uniqueFormats = []
    seenQualities = set()
    for formatId, quality, line in formats:
        if quality not in seenQualities:
            uniqueFormats.append((formatId, quality, line))
            seenQualities.add(quality)
    
    # Sort by quality (highest first)
    uniqueFormats.sort(key=lambda x: int(x[1][:-1]) if x[1][:-1].isdigit() else 0, reverse=True)
    return uniqueFormats

def updateQualityOptions():
    """Update quality options based on URL"""
    # url - video URL
    url = urlVar.get().strip()
    if not url:
        messagebox.showwarning("Warning", "Please enter a URL first")
        return
    
    # Clear current selection
    qualityVar.set("")
    
    # Show loading message
    qualityVar.set("Loading...")
    root.update()
    
    def fetchFormats():
        try:
            if isPlaylist(url):
                # plsQualities - playlist quality options
                plsQualities = ["best", "1080p", "720p", "480p", "360p", "worst"]
                root.after(0, lambda: updateQualityDropdown(plsQualities))
                root.after(0, lambda: qualityVar.set("1080p"))
            else:
                # formatOutput - raw format output from yt-dlp
                formatOutput = getAvailableFormats(url)
                if formatOutput:
                    formats = parseVideoFormats(formatOutput)
                    if formats:
                        qualities = ["best"] + [quality for formatId, quality, _ in formats] + ["worst"]
                        # Remove duplicates while preserving order
                        uniqueQualities = []
                        for q in qualities:
                            if q not in uniqueQualities:
                                uniqueQualities.append(q)
                        
                        root.after(0, lambda: updateQualityDropdown(uniqueQualities))
                        # Set default quality
                        if "1080p" in uniqueQualities:
                            root.after(0, lambda: qualityVar.set("1080p"))
                        elif "720p" in uniqueQualities:
                            root.after(0, lambda: qualityVar.set("720p"))
                        else:
                            root.after(0, lambda: qualityVar.set("best"))
                    else:
                        # No formats found, use defaults
                        defaultQualities = ["best", "1080p", "720p", "480p", "360p", "worst"]
                        root.after(0, lambda: updateQualityDropdown(defaultQualities))
                        root.after(0, lambda: qualityVar.set("1080p"))
                else:
                    # Failed to get formats
                    defaultQualities = ["best", "1080p", "720p", "480p", "360p", "worst"]
                    root.after(0, lambda: updateQualityDropdown(defaultQualities))
                    root.after(0, lambda: qualityVar.set("1080p"))
        except Exception as e:
            print(f"Error fetching formats: {e}")
            defaultQualities = ["best", "1080p", "720p", "480p", "360p", "worst"]
            root.after(0, lambda: updateQualityDropdown(defaultQualities))
            root.after(0, lambda: qualityVar.set("1080p"))
    
    threading.Thread(target=fetchFormats, daemon=True).start()

def updateQualityDropdown(qualities):
    """Update the quality dropdown with new options"""
    qualityDropdown['menu'].delete(0, 'end')
    for quality in qualities:
        qualityDropdown['menu'].add_command(
            label=quality, 
            command=tk._setit(qualityVar, quality)
        )

def updateFormatOptions():
    if modeVar.get() == "Video":
        formatVar.set("mp4")
        formatDropdown['menu'].delete(0, 'end')
        for f in ["mp4", "webm", "best"]:
            formatDropdown['menu'].add_command(label=f, command=tk._setit(formatVar, f))
    else:
        formatVar.set("mp3")
        formatDropdown['menu'].delete(0, 'end')
        for f in ["mp3", "wav", "ogg", "best"]:
            formatDropdown['menu'].add_command(label=f, command=tk._setit(formatVar, f))

def toggleTerminal():
    if terminalFrame.winfo_ismapped():
        terminalFrame.pack_forget()
        terminalBtn.config(text="Show Terminal")
    else:
        terminalFrame.pack(fill=tk.BOTH, expand=True, padx=0, pady=(10, 0))
        terminalBtn.config(text="Hide Terminal")

def clearQueue():
    global queueItems
    queueItems = []
    for widget in queueScrollFrame.winfo_children():
        widget.destroy()

def estimateDownloadTime(filesize):
    # bandwidth - estimated download speed
    bandwidth = 2 * 1024 * 1024  # 2 MB/s estimate
    return f"{int(filesize / bandwidth)}s"

def addToQueue(info, estimatedTime):
    global queueItems
    queueItems.append(info)
    
    # itemFrame - container for queue item
    itemFrame = ttk.Frame(queueScrollFrame)
    itemFrame.pack(fill=tk.X, padx=8, pady=4)

    try:
        response = requests.get(info['thumbnail'], timeout=5)
        imgData = response.content
        img = Image.open(io.BytesIO(imgData)).resize((60, 45))
        # thumb - thumbnail image
        thumb = ImageTk.PhotoImage(img)
        
        # thumbLabel - thumbnail display
        thumbLabel = ttk.Label(itemFrame, image=thumb)
        thumbLabel.pack(side=tk.LEFT, padx=8, pady=8)
        thumbLabel.image = thumb
    except:
        pass

    # infoFrame - container for text info
    infoFrame = ttk.Frame(itemFrame)
    infoFrame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)
    
    # titleLabel - video title display
    titleLabel = ttk.Label(infoFrame, text=info['title'][:40] + "..." if len(info['title']) > 40 else info['title'], 
                          font=("Segoe UI", 10, "bold"))
    titleLabel.pack(fill=tk.X)
    
    # lengthText - formatted duration
    lengthText = time.strftime('%M:%S', time.gmtime(info['duration'])) if info.get('duration') else 'Unknown'
    # lengthLabel - duration display
    lengthLabel = ttk.Label(infoFrame, text=f"Length: {lengthText}", 
                           font=("Segoe UI", 8))
    lengthLabel.pack(fill=tk.X)
    
    # timeLabel - estimated time display
    timeLabel = ttk.Label(infoFrame, text=f"Estimated Time: {estimatedTime}", 
                         font=("Segoe UI", 8))
    timeLabel.pack(fill=tk.X)

    # removeBtn - remove item button
    removeBtn = ttk.Button(itemFrame, text="×", width=3,
                          command=lambda: itemFrame.destroy())
    removeBtn.pack(side=tk.RIGHT, padx=8)

def startDownload():
    # url - video URL
    url = urlVar.get().strip()
    # folder - download folder path
    folder = pathVar.get()
    # mode - download mode (Video/Audio)
    mode = modeVar.get()
    # fmt - file format
    fmt = formatVar.get()
    # quality - video quality
    quality = qualityVar.get()

    if not url or not folder:
        messagebox.showerror("Error", "Please provide both a URL and a folder.")
        return

    # info - video metadata
    info = getVideoInfo(url)
    if not info:
        messagebox.showerror("Error", "Failed to retrieve video information.")
        return

    # estTime - estimated download time
    filesize = info.get('filesize_approx')
    if not isinstance(filesize, int) or filesize == 0:
        filesize = 10 * 1024 * 1024  # fallback to 10 MB if missing or None
    estTime = estimateDownloadTime(filesize)
    addToQueue(info, estTime)

    # outtmpl - output template for filename
    outtmpl = os.path.join(folder, "%(title)s.%(ext)s")
    # command - yt-dlp command list
    command = ["yt-dlp", url, "-o", outtmpl]

    if mode == "Audio":
        command += ["-x"]
        if fmt != "best":
            command += ["--audio-format", fmt]
    else:
        # Video mode - handle quality selection
        if quality and quality not in ["best", "worst", "Loading..."]:
            if quality.replace('p', '').isdigit():
                # qualityHeight - extracted height value
                qualityHeight = quality.replace('p', '')
                # Use format selection that ensures we get video+audio
                command += ["-f", f"best[height<={qualityHeight}]/best"]
            else:
                command += ["-f", quality]
        elif quality == "worst":
            command += ["-f", "worst"]
        else:
            command += ["-f", "best"]
        
        # Add format preference if specified
        if fmt != "best":
            command += ["--merge-output-format", fmt]

    def run():
        try:
            # process - subprocess for yt-dlp
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Display command in terminal
            terminalOutput.insert(tk.END, f"Running: {' '.join(command)}\n")
            terminalOutput.insert(tk.END, "-" * 50 + "\n")
            terminalOutput.see(tk.END)
            
            for line in process.stdout:
                terminalOutput.insert(tk.END, line)
                terminalOutput.see(tk.END)
                root.update_idletasks()
                
            process.wait()
            
            if process.returncode == 0:
                messagebox.showinfo("Success", "Download completed successfully!")
            else:
                messagebox.showerror("Error", f"Download failed with return code: {process.returncode}")
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    threading.Thread(target=run, daemon=True).start()

# Set theme BEFORE creating widgets

# root - main window
root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("820x530")

# urlVar - URL input variable
urlVar = tk.StringVar()
# pathVar - path input variable
pathVar = tk.StringVar()
# modeVar - mode selection variable
modeVar = tk.StringVar(value="Video")
# formatVar - format selection variable
formatVar = tk.StringVar(value="mp4")
# qualityVar - quality selection variable
qualityVar = tk.StringVar(value="1080p")

# container - main container frame
container = ttk.Frame(root)
container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

# queueSidebar - queue sidebar frame
queueSidebar = ttk.Frame(container, width=280)
queueSidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
queueSidebar.pack_propagate(False)

# queueHeader - queue header frame
queueHeader = ttk.Frame(queueSidebar)
queueHeader.pack(fill=tk.X, pady=10)

ttk.Label(queueHeader, text="Queue", font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT, padx=15)

# clearBtn - clear queue button
clearBtn = ttk.Button(queueHeader, text="Clear Queue", command=clearQueue)
clearBtn.pack(side=tk.RIGHT, padx=15)

# queueCanvas - scrollable canvas for queue
queueCanvas = tk.Canvas(queueSidebar, highlightthickness=0)
# queueScrollbar - scrollbar for queue
queueScrollbar = ttk.Scrollbar(queueSidebar, orient="vertical", command=queueCanvas.yview)
# queueScrollFrame - frame inside canvas for queue items
queueScrollFrame = ttk.Frame(queueCanvas)

queueScrollFrame.bind(
    "<Configure>",
    lambda e: queueCanvas.configure(scrollregion=queueCanvas.bbox("all"))
)

queueCanvas.create_window((0, 0), window=queueScrollFrame, anchor="nw")
queueCanvas.configure(yscrollcommand=queueScrollbar.set)

queueCanvas.pack(side="left", fill="both", expand=True)
queueScrollbar.pack(side="right", fill="y")

# mainFrame - main content frame
mainFrame = ttk.Frame(container)
mainFrame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# urlFrame - URL input frame
urlFrame = ttk.Frame(mainFrame)
urlFrame.pack(fill=tk.X, pady=(0, 20))

ttk.Label(urlFrame, text="YouTube URL", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 5))

# urlEntry - URL input field
urlEntry = ttk.Entry(urlFrame, textvariable=urlVar, font=("Segoe UI", 11))
urlEntry.pack(fill=tk.X, pady=(0, 5))

# pathFrame - path input frame
pathFrame = ttk.Frame(mainFrame)
pathFrame.pack(fill=tk.X, pady=(0, 20))

ttk.Label(pathFrame, text="Download Location", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 5))

# pathInputFrame - path input container
pathInputFrame = ttk.Frame(pathFrame)
pathInputFrame.pack(fill=tk.X)

# pathEntry - path input field
pathEntry = ttk.Entry(pathInputFrame, textvariable=pathVar, font=("Segoe UI", 11))
pathEntry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

# browseBtn - browse folder button
browseBtn = ttk.Button(pathInputFrame, text="Browse", command=browseFolder)
browseBtn.pack(side=tk.RIGHT)

# optionsFrame - download options frame
optionsFrame = ttk.Frame(mainFrame)
optionsFrame.pack(fill=tk.X, pady=(0, 20))

ttk.Label(optionsFrame, text="Download Options:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 10))

# typeFrame - type selection frame
typeFrame = ttk.Frame(optionsFrame)
typeFrame.pack(fill=tk.X, pady=(0, 15))

ttk.Label(typeFrame, text="Type:", font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=(0, 20))

# videoRadio - video mode radio button
videoRadio = ttk.Radiobutton(typeFrame, text="Video", variable=modeVar, value="Video", command=updateFormatOptions)
videoRadio.pack(side=tk.LEFT, padx=(0, 20))

# audioRadio - audio mode radio button
audioRadio = ttk.Radiobutton(typeFrame, text="Audio", variable=modeVar, value="Audio", command=updateFormatOptions)
audioRadio.pack(side=tk.LEFT)

# formatQualityFrame - format and quality container
formatQualityFrame = ttk.Frame(optionsFrame)
formatQualityFrame.pack(fill=tk.X, pady=(0, 15))

# formatFrame - format selection frame
formatFrame = ttk.Frame(formatQualityFrame)
formatFrame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 20))

ttk.Label(formatFrame, text="Format", font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 5))
# formatDropdown - format selection dropdown
formatDropdown = ttk.OptionMenu(formatFrame, formatVar, "mp4")
formatDropdown.pack(fill=tk.X)

# qualityFrame - quality selection frame
qualityFrame = ttk.Frame(formatQualityFrame)
qualityFrame.pack(side=tk.LEFT, fill=tk.X, expand=True)

ttk.Label(qualityFrame, text="Quality", font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 5))
# qualityDropdown - quality selection dropdown
qualityDropdown = ttk.OptionMenu(qualityFrame, qualityVar, "1080p")
qualityDropdown.pack(fill=tk.X)

# getQualitiesBtn - get qualities button
getQualitiesBtn = ttk.Button(optionsFrame, text="Get Qualities", command=updateQualityOptions)
getQualitiesBtn.pack(pady=(0, 10))

# actionFrame - action buttons frame
actionFrame = ttk.Frame(mainFrame)
actionFrame.pack(fill=tk.X, pady=(0, 20))

# downloadBtn - download button
downloadBtn = ttk.Button(actionFrame, text="Download", command=startDownload)
downloadBtn.pack(side=tk.LEFT, padx=(0, 15))

# terminalBtn - terminal toggle button
terminalBtn = ttk.Button(actionFrame, text="Show Terminal", command=toggleTerminal)
terminalBtn.pack(side=tk.RIGHT)

# terminalFrame - terminal output frame
terminalFrame = ttk.Frame(mainFrame)
# terminalOutput - terminal text widget
terminalOutput = scrolledtext.ScrolledText(terminalFrame, height=10, wrap=tk.WORD, font=("Consolas", 9))
terminalOutput.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

updateFormatOptions()

sv_ttk.set_theme(darkdetect.theme())



class DependencyInstaller:
    def __init__(self):
        self.ytDlpUrl = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_win.zip"
        self.ffmpegUrl = "https://www.gyan.dev/ffmpeg/builds/packages/ffmpeg-7.1.1-essentials_build.zip"
        self.ytDlpPath = r"C:\Program Files (x86)\yt-dlp"
        self.ffmpegPath = r"C:\Program Files (x86)\ffmpeg"
        self.ffmpegBinPath = r"C:\Program Files (x86)\ffmpeg\bin"
        
    def checkDependencies(self):
        """Check if yt-dlp and ffmpeg are installed"""
        ytDlpInstalled = shutil.which('yt-dlp') is not None
        ffmpegInstalled = shutil.which('ffmpeg') is not None
        return ytDlpInstalled, ffmpegInstalled
    
    def addToPath(self, directory):
        """Add directory to system PATH"""
        try:
            # Open the registry key for system environment variables
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                               0, winreg.KEY_ALL_ACCESS)
            
            # Get current PATH
            currentPath, _ = winreg.QueryValueEx(key, "Path")
            
            # Check if directory is already in PATH
            if directory.lower() not in currentPath.lower():
                newPath = currentPath + ";" + directory
                winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, newPath)
                
                # Broadcast WM_SETTINGCHANGE to notify applications
                import ctypes
                ctypes.windll.user32.SendMessageW(0xFFFF, 0x001A, 0, "Environment")
            
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Error adding to PATH: {e}")
            return False
    
    def downloadFile(self, url, destination, progressCallback=None):
        """Download file with progress tracking"""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            totalSize = int(response.headers.get('content-length', 0))
            downloadedSize = 0
            
            with open(destination, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloadedSize += len(chunk)
                        if progressCallback and totalSize > 0:
                            progress = (downloadedSize / totalSize) * 100
                            progressCallback(progress)
            
            return True
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            return False
    
    def extractZip(self, zipPath, extractPath):
        """Extract zip file"""
        try:
            with zipfile.ZipFile(zipPath, 'r') as zipRef:
                zipRef.extractall(extractPath)
            return True
        except Exception as e:
            print(f"Error extracting {zipPath}: {e}")
            return False
    
    def installYtDlp(self, progressCallback=None):
        """Download and install yt-dlp"""
        try:
            # Create directory
            os.makedirs(self.ytDlpPath, exist_ok=True)
            
            # Download
            zipPath = os.path.join(self.ytDlpPath, "yt-dlp_win.zip")
            if not self.downloadFile(self.ytDlpUrl, zipPath, progressCallback):
                return False
            
            # Extract
            if not self.extractZip(zipPath, self.ytDlpPath):
                return False
            
            # Clean up zip file
            os.remove(zipPath)
            
            # Add to PATH
            self.addToPath(self.ytDlpPath)
            
            return True
        except Exception as e:
            print(f"Error installing yt-dlp: {e}")
            return False
    
    def installFfmpeg(self, progressCallback=None):
        """Download and install ffmpeg"""
        try:
            # Create directory
            os.makedirs(self.ffmpegPath, exist_ok=True)
            
            # Download
            zipPath = os.path.join(self.ffmpegPath, "ffmpeg.zip")
            if not self.downloadFile(self.ffmpegUrl, zipPath, progressCallback):
                return False
            
            # Extract
            if not self.extractZip(zipPath, self.ffmpegPath):
                return False
            
            # Clean up zip file
            os.remove(zipPath)
            
            # Move files from extracted folder to ffmpeg directory
            extractedFolders = [f for f in os.listdir(self.ffmpegPath) 
                              if os.path.isdir(os.path.join(self.ffmpegPath, f))]
            
            if extractedFolders:
                extractedPath = os.path.join(self.ffmpegPath, extractedFolders[0])
                
                # Move contents
                for item in os.listdir(extractedPath):
                    src = os.path.join(extractedPath, item)
                    dst = os.path.join(self.ffmpegPath, item)
                    if os.path.isdir(src):
                        shutil.move(src, dst)
                    else:
                        shutil.move(src, dst)
                
                # Remove empty extracted folder
                os.rmdir(extractedPath)
            
            # Add bin directory to PATH
            self.addToPath(self.ffmpegBinPath)
            
            return True
        except Exception as e:
            print(f"Error installing ffmpeg: {e}")
            return False

class InstallProgressWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Installing Dependencies")
        self.window.geometry("400x150")
        self.window.resizable(False, False)
        self.window.grab_set()  # Make window modal
        
        # Center window
        self.window.transient(parent)
        self.window.protocol("WM_DELETE_WINDOW", self.onClose)
        
        # Status label
        self.statusLabel = tk.Label(self.window, text="Checking dependencies...")
        self.statusLabel.pack(pady=10)
        
        # Progress bar
        self.progressBar = ttk.Progressbar(self.window, length=300, mode='determinate')
        self.progressBar.pack(pady=10)
        
        # Cancel button
        self.cancelButton = tk.Button(self.window, text="Cancel", command=self.onClose)
        self.cancelButton.pack(pady=5)
        
        self.cancelled = False
        
    def updateStatus(self, text):
        self.statusLabel.config(text=text)
        self.window.update()
    
    def updateProgress(self, value):
        self.progressBar['value'] = value
        self.window.update()
    
    def onClose(self):
        self.cancelled = True
        self.window.destroy()

def checkAndInstallDependencies(parent=None):
    """Main function to check and install dependencies"""
    installer = DependencyInstaller()
    ytDlpInstalled, ffmpegInstalled = installer.checkDependencies()
    
    if ytDlpInstalled and ffmpegInstalled:
        return True  # All dependencies are already installed
    
    # Show install dialog
    if parent is None:
        root = tk.Tk()
        root.withdraw()  # Hide main window
        parent = root
    
    missing = []
    if not ytDlpInstalled:
        missing.append("yt-dlp")
    if not ffmpegInstalled:
        missing.append("ffmpeg")
    
    missingText = ", ".join(missing)
    response = messagebox.askyesno(
        "Missing Dependencies",
        f"The following dependencies are missing: {missingText}\n\n"
        "Would you like to install them automatically?\n"
        "(This requires administrator privileges)"
    )
    
    if not response:
        return False
    
    # Show progress window
    progressWindow = InstallProgressWindow(parent)
    
    def installWorker():
        try:
            if not ytDlpInstalled:
                progressWindow.updateStatus("Installing yt-dlp...")
                progressWindow.updateProgress(0)
                
                success = installer.installYtDlp(
                    lambda p: progressWindow.updateProgress(p * 0.5)
                )
                
                if not success or progressWindow.cancelled:
                    progressWindow.window.destroy()
                    messagebox.showerror("Error", "Failed to install yt-dlp")
                    return
            
            if not ffmpegInstalled:
                progressWindow.updateStatus("Installing ffmpeg...")
                startProgress = 50 if not ytDlpInstalled else 0
                
                success = installer.installFfmpeg(
                    lambda p: progressWindow.updateProgress(startProgress + (p * 0.5))
                )
                
                if not success or progressWindow.cancelled:
                    progressWindow.window.destroy()
                    messagebox.showerror("Error", "Failed to install ffmpeg")
                    return
            
            progressWindow.updateStatus("Installation complete!")
            progressWindow.updateProgress(100)
            
            # Close progress window
            progressWindow.window.destroy()
            
            messagebox.showinfo(
                "Success",
                "Dependencies installed successfully!\n"
                "Please restart your application for changes to take effect."
            )
            
        except Exception as e:
            progressWindow.window.destroy()
            messagebox.showerror("Error", f"Installation failed: {str(e)}")
    
    # Start installation in separate thread
    installThread = threading.Thread(target=installWorker)
    installThread.daemon = True
    installThread.start()
    
    return True


if checkAndInstallDependencies(root):
    
    root.mainloop()
else:
    # User cancelled installation
    root.destroy()
    sys.exit(1)