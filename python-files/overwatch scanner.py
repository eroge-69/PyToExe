import re, os, sys, psutil, requests, ctypes, threading, time, subprocess, traceback, platform, datetime, yara, json, winreg, struct, csv, vdf, glob, win32evtlog, base64, pythoncom
from datetime import timedelta
from win32com.client import Dispatch

Detects = []
Warnings = []
Logs = []
PcaClient = []
Bam = []
Recording = []
Steam = []
USBLogs = []
LastAV = []
Recent = []

ctypes.windll.kernel32.SetConsoleTitleW("Overwatch Scanner")

Journal_List = ["%d.%m.%Y %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%d. %m. %Y %H:%M:%S"]
Username = os.path.basename(os.path.normpath(os.path.expanduser('~')))

if not ctypes.windll.shell32.IsUserAnAdmin():
    print("Run Console as Administrator!")
    time.sleep(6)
    pidos = os.getpid()
    psutil.Process(pidos).terminate()

Local_PIN = None
    
if "-" in sys.executable:
    parts = os.path.basename(sys.executable).split("-")
    if len(parts) > 1:
        Local_PIN = os.path.splitext(parts[1])[0]

if not Local_PIN:
    Local_PIN = input("PIN: ")

def Boot_Time():
    try:
        boot_time_timestamp = psutil.boot_time()
        boot_time = datetime.datetime.fromtimestamp(boot_time_timestamp)
        return boot_time
    except Exception as e:
        print(traceback.format_exc())

def Boot_Time_UPTIME():
    try:
        boot_time = Boot_Time()
        current_time = datetime.datetime.now()
        uptime = current_time - boot_time
        days, seconds = divmod(uptime.seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)

        uptime_string = ""
        if days > 0:
            uptime_string += f"{int(days)}d, "
        if hours > 0 or (days == 0 and minutes == 0):
            uptime_string += f"{int(hours)}h, "
        if minutes > 0 or (days == 0 and hours == 0):
            uptime_string += f"{int(minutes)}m, "
        if seconds > 0 or (days == 0 and hours == 0 and minutes == 0):
            uptime_string += f"{int(seconds)}s ago"

        return uptime_string
    except Exception as e:
        print(traceback.format_exc())

def ServicePID(service_name):
    services = psutil.win_service_iter()
    for service in services:
        if service.name().lower() == service_name.lower():
            try:
                return service.pid()
            except psutil.AccessDenied:
                pass
    return None

def Remove_Files(subs):
    if os.path.exists(subs):
        for item in os.listdir(subs):
            item_path = os.path.join(subs, item)
            if os.path.isdir(item_path):
                Remove_Files(item_path)
            else:
                os.remove(item_path)
        os.rmdir(subs)
    else:
        pass

def ProcessPID(process_name):
    try:
        for proc in psutil.process_iter(['pid', 'name', 'ppid']):
            proc_name = proc.info['name'].lower()
            if proc_name in process_name:
                try:
                    parent = psutil.Process(proc.info['ppid'])
                    parent_name = parent.name().lower()
                    if parent_name not in process_name:
                        return proc.info['pid']
                except psutil.NoSuchProcess:
                    return proc.info['pid']
    except psutil.NoSuchProcess:
        pass

    return None

def Process_UpTime(pid, warning_message):
    if pid is not None:
        process = psutil.Process(pid)
        create_time = process.create_time()
        current_time = datetime.datetime.now().timestamp()
        uptime_seconds = current_time - create_time
        days, seconds = divmod(uptime_seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)

        uptime_string = ""
        if days > 0:
            uptime_string += f"{int(days)}d, "
        if hours > 0:
            uptime_string += f"{int(hours)}h, "
        if minutes > 0:
            uptime_string += f"{int(minutes)}m, "
        if seconds > 0:
            uptime_string += f"{int(seconds)}s ago"

        return uptime_string
    else:
        if not 'FiveM' in warning_message:
            return "Not Running!"
        else:
            return "Not Running!"

def Discord_ID():
    try:
        with open(f'C:\\Users\\{Username}\\AppData\\Roaming\\discord\\sentry\\scope_v3.json', 'r', encoding='utf-8', errors='replace') as File:
            Content = File.read()

        Regex = re.search(r'"id"\s*:\s*"(\d+)"', Content)

        if Regex:
            return Regex.group(1)
        else:
            return None

    except Exception:
        pass

def BL_Hwid():
    try:
        combinations_link = "https://example.com/api/module/blacklist/"
        response_combinations = requests.get(combinations_link)
        combinations = response_combinations.text.split('\n')

        if not combinations:
            print("SSL [ ERROR ]")
            psutil.Process(os.getpid()).terminate()

        for comb in combinations:
            if HWID_System() in comb:
                print("This Person is Banned!")

                url = 'https://example.com/api/ban'
                headers1 = {
                    'Content-Type': 'application/json', 
                    'pin': Local_PIN
                }
                data = {
                    'ScreenShot': encoded_image,
                    'Start-Time': Boot_Time_UPTIME(),
                    'Discord': Discord_ID(),
                    'HWID': HWID_System(),
                }
                headers = {'PIN': Local_PIN}
                requests.post(url, headers=headers1, json=data)
                del headers
                psutil.Process(os.getpid()).terminate()

    except Exception as e:
        print(traceback.format_exc())

BL_Hwid()

Process_Lists = [
    #budget anti debug
    #example ("random process", "detection name")
]

Stop_Monitor = False

def Process_Monitor():
    global Stop_Monitor
    while not Stop_Monitor:
        running_processes = [p.name() for p in psutil.process_iter()]
        for proc_name, description in Process_Lists:
            if proc_name in running_processes:
                Stop_Monitor = True
                print("Scanner [ ERROR ]: Debugger Found")
                url = 'https://example.com/api/loader/debugger'
                data = {
                    'ScreenShot': encoded_image,
                    'Start-Time': Boot_Time_UPTIME(),
                    'Discord': Discord_ID(),
                    'HWID': HWID_System(),
                    'Process': proc_name,
                    'Description': description
                }
                headers = {'PIN': Local_PIN}
                requests.post(url, headers=headers, json=data)
                psutil.Process(os.getpid()).terminate()
        time.sleep(5)

Monitor = threading.Thread(target=Process_Monitor)
Monitor.start()

Files_2_Delete = ["xxStrings.exe", "Scanner-USBCheck.exe", "Scanner-USBCheck.csv", "Scanner-Journal.exe", "Scanner-Journal.txt", "Scanner-USBLogs.csv", "Scanner-Prefetch.csv", "Scanner-Prefetch.exe" ]

def Memory():
    try:
        a = "a"
        a1 = "l"
        a2 = "p"
        a3 = "B"
        a4 = "0"

        Hashed_Memory_Dump = a + a1 + a2 + a3 + a4

        return base64.b64encode(Hashed_Memory_Dump.encode('utf-8')).decode('utf-8')
    except Exception as e:
        print(traceback.format_exc())

MUICache_Path = r"Local Settings\Software\Microsoft\Windows\Shell\MuiCache"
Store_Path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Compatibility Assistant\Store"
APPSwitched_Path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\FeatureUsage\AppSwitched"
Bam_Path = r'SYSTEM\CurrentControlSet\Services\bam\State\UserSettings'
Shell_MuiCache = r'Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache'
Desktop_Path = os.path.expanduser("~\Desktop").replace("\\", "\\\\")
RecentFolder = os.path.expandvars(rf'C:\Users\{Username}\AppData\Roaming\Microsoft\Windows\Recent')
Task_Scheduler = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tasks"
PrefetchFolder = os.path.expandvars(r'C:\Windows\Prefetch')
System_Install = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
Hosts_Path = r'C:\Windows\System32\drivers\etc\hosts'
System_Install_Key = "InstallDate"
Module_Path = os.getcwd()
Disks = [d.device for d in psutil.disk_partitions()]

Regex_Compile_1 = re.compile(r'\Afile:///(.+)')
Regex_Compile_2 = re.compile(r'([CDEFGHIJKLMNOPQRSTUVWXYZ]:\\.+)') 
Regex_Compile_3 = re.compile(r'^[^\\/]*[a-zA-Z]+[0-9]+[^\\/]*\.(exe|rpf|meta)$')
Regex_Compile_4 = re.compile(r'x[CDEFGHIJKLMNOPQRSTUVWXYZ]:\\') 
PcaClient_Regex = re.compile('TRACE,0000,0000,PcaClient,')

def XoR(String):
    Cryption = "lolxor"
    
    return ''.join(chr(ord(c) ^ ord(k)) for c, k in zip(String, Cryption))

def C_Directory():
    global CDirectory
    CDirectory = "C:\\Windows\\Temp"

def Scan_Time(start_time):
    try:
        end_time = time.time()
        elapsed_time = end_time - start_time
        return elapsed_time
    except Exception as e:
        print(traceback.format_exc())

def RegistryScan():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\OpenSavePidlDeleted\dll"):
            Logs.append("Generic Regedit [ DLL ]")
    except FileNotFoundError:
        pass
    
def RecentChecker():
    try:
        def Original_Path_Path(Path):
            try:
                Shell = Dispatch("WScript.Shell")
                Shortcut = Shell.CreateShortcut(Path)
                return Shortcut.Targetpath
            except Exception as e:
                return None
            
        Recent_Files = glob.glob(os.path.join(RecentFolder, '*.lnk'))
        if not Recent_Files:
            return

        for Short_File in Recent_Files:
            Original_Path = Original_Path_Path(Short_File)
            if Original_Path:
                Original_Path_Full = Original_Path.replace("\\", "\\\\")
                Recent.append(f"{Original_Path_Full}")
            else:
                Short_Path_Full = Short_File.replace("\\", "\\\\")
                Recent.append(f"{Short_Path_Full}")

        if Recent is None:
            return
        
        Scanner_Agent = base64.b64decode(Memory().encode('utf-8')).decode('utf-8')
        
        headers = {
            'User-Agent': Scanner_Agent,
            'PIN': f"{Local_PIN}",
            'Security': "Success",
            'Game': "FiveM",
            'Authorization': Authorization()
        }

        del Scanner_Agent

        combinations_link = "https://example.com/api/module/fivem/.Recent"
        response_combinations = requests.get(combinations_link, headers=headers)

        del headers

        combinations = (lambda Text: XoR(Text.text))(response_combinations).splitlines()
                
        for comb in combinations:
            try:
                split_idx = comb.index(":::")
                cheatName = comb[:split_idx]
                cheatString = comb[split_idx + 3:]
                for dumpedString in Recent:
                    if cheatString.strip() in dumpedString:
                        detection = cheatName
                        Detects.append(f"Detected: {detection}")
                        break
            except ValueError as e:
                print(traceback.format_exc())
        del combinations
        if Recent:
            Recent.clear()
    except Exception as e:
        print(traceback.format_exc())

def FiveM_Location():
    try:
        fivem_locations = []
        start_time_fivem = time.time()

        for folder, subfolders, files in os.walk(os.path.expanduser("~")):
            if "FiveM.app" in subfolders:
                fivem_path = os.path.join(folder, "FiveM.app")
                fivem_locations.append(fivem_path)
                break
            
            if time.time() - start_time_fivem > 80:
                break
                
        return fivem_locations
    
    except Exception as e:
        print(traceback.format_exc())

def FiveM_Location_M():
    global FiveM
    FiveM = FiveM_Location()

def Memory_Strings(pid):
    try:
        if pid is None:
            return []
        else:
            cmd = f"{CDirectory}\\xxStrings.exe" + f" -p {pid} -raw -l 5"
            strings = str(subprocess.check_output(cmd)).split("\\r\\n")
            return list(set(strings))
    except subprocess.CalledProcessError as e:
        print(traceback.format_exc())
    except Exception as e:
        print(traceback.format_exc())
    
def Valid_Journal(entry_str):
    for date_format in Journal_List:
        try:
            return datetime.datetime.strptime(entry_str, date_format)
        except ValueError:
            continue
    return None

def Signature_Checker(file_path):
    try:
        crypt32 = ctypes.windll.LoadLibrary("crypt32.dll")
        
        CERT_QUERY_OBJECT_FILE = 1
        CERT_QUERY_CONTENT_FLAG_ALL = 0xFFFF
        CERT_QUERY_FORMAT_FLAG_ALL = 0xFFFF

        sign_info = crypt32.CryptQueryObject(
            CERT_QUERY_OBJECT_FILE,
            file_path,
            CERT_QUERY_CONTENT_FLAG_ALL,
            CERT_QUERY_FORMAT_FLAG_ALL,
            0,
            None,
            None,
            None,
            None,
            None,
            None
        )
        
        if sign_info != 0:
            return True
    except Exception as e:
        print(traceback.format_exc())
    return False
    
def Modules():
    global Explorer_Strings

    Explorer_Strings = Memory_Strings(Explorer_PID())

def Modules_Existing():
    global DPS_Strings, DNSCache_Strings, FiveM_Strings, PcaSVC_Strings, EventLog_Strings, SIHost_Strings, CTFMon_Strings, DiagTrack_Strings, SysMain_Strings, Lsass_Strings, TCP_Strings, CryptSVC_Strings, SearchIndexer_Strings, TaskHost_Strings, Steam_Strings

    DPS_Strings = Memory_Strings(DPS_PID())
    EventLog_Strings = Memory_Strings(EventLOG_PID())
    DNSCache_Strings = Memory_Strings(DNSCache_PID())
    FiveM_Strings = Memory_Strings(FiveM_PID())
    PcaSVC_Strings = Memory_Strings(PcaSVC_PID())
    SIHost_Strings = Memory_Strings(SIHost_PID())
    CTFMon_Strings = Memory_Strings(CTFMon_PID())
    DiagTrack_Strings = Memory_Strings(DiagTrack_PID())
    SysMain_Strings = Memory_Strings(SysMain_PID())
    Lsass_Strings = Memory_Strings(Lsass_PID())
    TCP_Strings = Memory_Strings(TCP_PID())
    CryptSVC_Strings = Memory_Strings(CryptSVC_PID())
    SearchIndexer_Strings = Memory_Strings(SearchIndexer_PID())
    TaskHost_Strings = Memory_Strings(TaskHost_PID())
    Steam_Strings = Memory_Strings(Steam_PID())

FILE_ATTRIBUTE_HIDDEN = 0x02
FILE_ATTRIBUTE_SYSTEM = 0x04

SetFileAttributes = ctypes.windll.kernel32.SetFileAttributesW

def Download_File(url, output_file_path):
    try:
        Scanner_Agent = base64.b64decode(Memory().encode('utf-8')).decode('utf-8')
    
        headers = {
            'User-Agent': Scanner_Agent
        }

        response = requests.get("https://example.com/api/download/" + url, verify=True, headers=headers)
        
        del Scanner_Agent
        del headers

        with open(output_file_path, 'wb') as output_file:
            output_file.write(response.content)

    except PermissionError:
        pass
        
    except Exception as e:
        print(traceback.format_exc())

def Explorer_PID():
    PID = ProcessPID("explorer.exe")
    return PID

def Steam_PID():
    PID = ProcessPID("Steam.exe")
    return PID

def TaskHost_PID():
    PID = ProcessPID("taskhostw.exe")
    return PID

def WinLogon_PID():
    PID = ProcessPID("winlogon.exe")
    return PID

def SearchIndexer_PID():
    PID = ProcessPID("SearchIndexer.exe")
    return PID

def CTFMon_PID():
    PID = ProcessPID("ctfmon.exe")
    return PID

def SIHost_PID():
    PID = ProcessPID("sihost.exe")
    return PID

def Lsass_PID():
    PID = ProcessPID("lsass.exe")
    return PID

def DNSCache_PID():
    PID = ServicePID("dnscache")
    return PID

def CryptSVC_PID():
    PID = ServicePID("cryptsvc")
    return PID

def TCP_PID():
    PID = ServicePID("tcp")
    return PID

def DPS_PID():
    PID = ServicePID("dps")
    return PID

def DUSMSVC_PID():
    PID = ServicePID("dusmsvc")
    return PID

def PcaSVC_PID():
    PID = ServicePID("pcasvc")
    return PID

def EventLOG_PID():
    PID = ServicePID("eventlog")
    return PID

def DiagTrack_PID():
    PID = ServicePID("diagtrack")
    return PID
        
def SysMain_PID():
    PID = ServicePID("sysmain")
    return PID   

def APPInfo_PID():
    PID = ServicePID("appinfo")
    return PID

def FiveM_PID():
    #find process fivem.
    return None

def BAM_PID():
    try:
        Service = psutil.win_service_get('bam').as_dict()
        
        return Service

    except Exception as e:
        print(traceback.format_exc())

def FiveM_UPTime():
    return Process_UpTime(DNSCache_PID(), "FiveM Process Not Running!")

def DNSCache_UPTime():
    return Process_UpTime(DNSCache_PID(), "DNSCache Service Not Running!")

def DPS_UPTime():
    return Process_UpTime(DPS_PID(), "DPS Service Not Running!")

def PcaSVC_UPTime():
    return Process_UpTime(PcaSVC_PID(), "PcaSVC Service Not Running!")

def Explorer_UPTime():
    return Process_UpTime(Explorer_PID(), "Explorer.exe Process Not Running!")

def EventLog_UPTime():
    return Process_UpTime(EventLOG_PID(), "EventLog Service Not Running!")

def AppInfo_UPTime():
    return Process_UpTime(APPInfo_PID(), "AppInfo Service Not Running!")

def IP_Analyzis():
    try:
        return None
        #get ip then check vpn https://proxycheck.io/v2/{IP_Address}?vpn=1&asn=1
    except Exception as e:
        return None, None

def File_Scanner_Global():
    try:
        ExecutedFiles = set()
        ExecutedFiles2 = set()
        ExecutedFiles4 = set()
        ExecutedFiles5 = set()
        ExecutedFiles6 = set()
        ExecutedFiles7 = set()

        Files = set()

        Scanner_Agent = base64.b64decode(Memory().encode('utf-8')).decode('utf-8')
    
        headers = {
            'User-Agent': Scanner_Agent,
            'PIN':  f"{Local_PIN}",
            'Security': "Success",
            'Game': "Game",
            'Authorization': Authorization()
        }
        
        del Scanner_Agent

        combinations_link = "https://example.com/api/module/fivem/.yara"
        response_combinations = requests.get(combinations_link, headers=headers)

        del headers

        Decrypted = (lambda Text: XoR(Text.text))(response_combinations)


        rule_text = f'''
        {Decrypted}
        '''

        del Decrypted

        rules = yara.compile(source=rule_text)

        del rule_text

        Account = os.getlogin()

        def FileScan(file_path):
            try:
                file_size = os.path.getsize(file_path)

                if file_size < 200 * 1024 * 1024:
                    with open(file_path, 'rb') as f:
                        data = f.read()
                        matches = rules.match(data=data)
                        if matches:
                            separators = ['\\', '/', '//']
                            last_separator_index = -1
                            for sep in separators:
                                index = file_path.rfind(sep)
                                if index > last_separator_index:
                                    last_separator_index = index

                            if last_separator_index != -1:
                                file_name = file_path[last_separator_index + 1:]
                            else:
                                file_name = os.path.basename(file_path)

                            if '"' in file_name:
                                file_name = file_name.replace('"', '')

                            for match in matches:
                                rule_name = match.meta.get('rule_name', 'Generic Detection')

                                if not file_name:
                                    file_name = ""

                                if (rule_name, file_name) not in Files:
                                    Detects.append(f"Detected: {rule_name}, Path: {file_name}")
                                    Files.add((rule_name, file_name))
                            del match
                        del matches
            except Exception:
                pass

        def Method1():
            try:

                for root, dirs, files in os.walk(Desktop_Path):
                    for filename in files:
                        file_path = os.path.join(root, filename)
                        if os.path.getsize(file_path) > 4 * 1024 * 1024:
                            ExecutedFiles.add(file_path)

                for file_path in ExecutedFiles:
                    if Account in file_path:
                        file_path.replace(Account, Username)
                        
                    corrected_file_path = file_path.replace('\\', '\\\\')
                    FileScan(corrected_file_path)

            except FileNotFoundError:
                pass

            except Exception as e:
                print(traceback.format_exc())

        def Method2():
            try:
                usb_drives = [partition.mountpoint for partition in psutil.disk_partitions() if partition.fstype == 'fat32']

                if usb_drives:
                    Detects.append("FAT32 Plugged!")
                else:
                    pass

                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, Shell_MuiCache)

                    index = 0
                    while True:
                        try:
                            name, _, _ = winreg.EnumValue(key, index)
                            nome = name.replace(".ApplicationCompany", "").replace(".FriendlyAppName", "").replace("\\", "\\\\")
                            ExecutedFiles2.add(nome)
                            index += 1
                        except OSError as e:
                            break

                    winreg.CloseKey(key)

                except FileNotFoundError:
                    pass
                except Exception as e:
                    print(traceback.format_exc())
                
                if thread15.is_alive:
                    thread15.join()

                for File in LastAV:
                    path = File['Path']
                    ExecutedFiles2.add(path)

                for file_path in ExecutedFiles2:
                    if Account in file_path:
                        file_path.replace(Account, Username)

                    corrected_file_path = file_path.replace('\\', '\\\\')
                    FileScan(corrected_file_path)
            except FileNotFoundError:
                pass

            except Exception as e:
                print(traceback.format_exc())

        def Method3():
            try:
                pass
            except Exception as e:
                print(traceback.format_exc())

        def Method4():
            try:
                if Explorer_Strings:
                    Matches = [entry for entry in Explorer_Strings if PcaClient_Regex.search(entry)]

                    for Match in Matches:
                        Parts = Match.split(',')
                        if len(Parts) >= 6:
                            path = Parts[5].strip().replace('"', '').replace('\\\\', '\\')
                            if path.endswith(('.exe', '.dll', '.rpf', '.meta', '.mp4', '.mp3', '.mp3')):
                                ExecutedFiles4.add(path)

                try:
                    if os.path.exists(r'C:\$Recycle.Bin'):
                        for dirpath, dirnames, filenames in os.walk(r'C:\$Recycle.Bin'):
                            for filename in filenames:
                                file_path = os.path.join(dirpath, filename)
                                file_size = os.path.getsize(file_path)

                                file_size_mb = (file_size) / 1024 * 1024

                                if 0.1 < file_size_mb < 300:
                                    ExecutedFiles4.add(file_path)
                    else:
                        pass

                except Exception as e:
                    print(traceback.format_exc())

                for file_path in ExecutedFiles4:
                    if Account in file_path:
                        file_path.replace(Account, Username)

                    corrected_file_path = file_path.replace('\\', '\\\\')
                    FileScan(corrected_file_path)

            except Exception as e:
                print(traceback.format_exc())
                
        def Method5():
            try:
                for line in DPS_Strings:
                    if DPS_Strings:
                        if ':\\' in line:
                            ExecutedFiles5.add(line)

                for line in CTFMon_Strings:
                    if CTFMon_Strings:
                        if ':\\' in line:
                            ExecutedFiles5.add(line)

                for line in SysMain_Strings:
                    if SysMain_Strings:
                        if ':\\' in line:
                            ExecutedFiles5.add(line)
                if SysMain_Strings:
                    SysMain_Strings.clear()
                    
                for line in PcaSVC_Strings:
                    if PcaSVC_Strings:
                        if ':\\' in line:
                            ExecutedFiles5.add(line)

                for line in DiagTrack_Strings:
                    if DiagTrack_Strings:
                        if ':\\' in line:
                            ExecutedFiles5.add(line)

                for Path_MUI in [MUICache_Path]:
                    try:
                        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, Path_MUI) as key:
                            i = 0
                            while True:
                                try:
                                    value_name, value_type, _ = winreg.EnumValue(key, i)
                                    if value_type == winreg.REG_BINARY:
                                        ExecutedFiles5.add(value_name)
                                    i += 1
                                except OSError as e:
                                    break
                    except FileNotFoundError:
                        pass

                for key_path in [Store_Path, APPSwitched_Path]:
                    try:
                        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                            i = 0
                            while True:
                                try:
                                    value_name, value_type, _ = winreg.EnumValue(key, i)
                                    if value_type == winreg.REG_BINARY:
                                        ExecutedFiles5.add(value_name)
                                    i += 1
                                except OSError as e:
                                    break
                    except FileNotFoundError:
                        pass
                    
                for file_path in ExecutedFiles5:
                    if Account in file_path:
                        file_path.replace(Account, Username)

                    corrected_file_path = file_path.replace('\\', '\\\\')
                    FileScan(corrected_file_path)

            except Exception as e:
                print(traceback.format_exc())
        
        def Method6():
            try:
                for FM in FiveM:
                    log_location = os.path.join(FM, "mods")
                    for filename in os.listdir(log_location):
                        file_path = os.path.join(log_location, filename)
                        if os.path.isfile(file_path):
                            ExecutedFiles6.add(file_path)

                    CitizenFX_Path = os.path.join(FM, "CitizenFX.ini")
                    if os.path.exists(CitizenFX_Path):
                        with open(CitizenFX_Path, encoding="utf-8", errors='replace', mode='r') as File:
                            for line in File:
                                if 'IVPath=' in line:
                                    GTAV_Path = line.strip().split('IVPath=')[1].strip().replace('\\', '\\\\')
                                    imgui_ini_path = os.path.join(GTAV_Path, "x64a.rpf")
                                    if os.path.exists(imgui_ini_path):
                                        ExecutedFiles6.add(imgui_ini_path)
                                    else:
                                        pass
                    else:
                        pass

                for file_path in ExecutedFiles6:
                    if Account in file_path:
                        file_path.replace(Account, Username)

                    corrected_file_path = file_path.replace('\\', '\\\\')
                    FileScan(corrected_file_path)

            except FileNotFoundError:
                pass
            except Exception as e:
                print(traceback.format_exc())

        def Method7():
            try:
                if Explorer_Strings is None:
                    return

                for linea in Explorer_Strings:
                    Regex_1 = Regex_Compile_1.search(linea)
                    Regex_2 = Regex_Compile_2.search(linea)
                    Regex_3 = Regex_Compile_3.search(linea)
                    Regex_4 = Regex_Compile_4.search(linea)

                    if Regex_1 is not None:
                        file_path = Regex_1.group(1)
                        ExecutedFiles7.add(file_path)

                    if Regex_2 is not None:
                        file_path = Regex_2.group(1)
                        ExecutedFiles7.add(file_path)   

                    if Regex_3 is not None or Regex_4 is not None:
                        if Regex_3 is not None and Regex_3.group() in linea:
                            ExecutedFiles7.add(linea.strip())

                        if Regex_4 is not None and Regex_4.group() in linea:
                            ExecutedFiles7.add(linea.strip())  

                for file_path in ExecutedFiles7:
                    if Account in file_path:
                        file_path.replace(Account, Username)
                        
                    corrected_file_path = file_path.replace('\\', '\\\\')
                    FileScan(corrected_file_path)
            except FileNotFoundError:
                pass
            except Exception as e:
                print(traceback.format_exc())

        Method1T = threading.Thread(target=Method1)
        Method2T = threading.Thread(target=Method2)
        Method3T = threading.Thread(target=Method3)
        Method4T = threading.Thread(target=Method4)
        Method5T = threading.Thread(target=Method5)
        Method6T = threading.Thread(target=Method6)
        Method7T = threading.Thread(target=Method7)

        Method1T.start()
        Method2T.start()
        Method3T.start()
        Method4T.start()
        Method5T.start()
        Method6T.start()
        Method7T.start()

        if Method1T.is_alive:
            Method1T.join()

        if Method2T.is_alive:
            Method2T.join()

        if Method3T.is_alive:
            Method3T.join()

        if Method4T.is_alive:
            Method4T.join()

        if Method5T.is_alive:
            Method5T.join()

        if Method6T.is_alive:
            Method6T.join()

        if Method7T.is_alive:
            Method7T.join()
    except Exception as e:
        print(traceback.format_exc())

def AMCacheChecker():
    try:
        Download_File("AMCacher.exe", f"{CDirectory}\\Cacher.exe")
        os.system(f'{CDirectory}\\Cacher.exe --csv .')
        if os.path.exists(f"{CDirectory}\\Scanner-Cache.csv"):
            with open(f"{CDirectory}\\Scanner-Cache.csv", 'r', encoding='utf-8', errors='replace') as file:
                amcache = file.read()

                if amcache is None:
                    return
                
                Scanner_Agent = base64.b64decode(Memory().encode('utf-8')).decode('utf-8')
                
                headers = {
                    'User-Agent': Scanner_Agent,
                    'PIN': f"{Local_PIN}",
                    'Security': "Success",
                    'Game': "FiveM",
                    'Authorization': Authorization()
                }

                del Scanner_Agent

                combinations_link = "https://example.com/api/module/fivem/.AMCache"
                response_combinations = requests.get(combinations_link, headers=headers)

                combinations_link1 = "https://example.com/api/module/fivem/.DPS"
                response_combinations1 = requests.get(combinations_link1, headers=headers)

                del headers

                combinations = (lambda Text: XoR(Text.text))(response_combinations).splitlines()
                        
                for comb in combinations:
                    try:
                        split_idx = comb.index(":::")
                        cheatName = comb[:split_idx]
                        cheatString = comb[split_idx + 3:]
                        if cheatString.strip() in amcache:
                            Detects.append(f"Detected: {cheatName}")
                            break
                    except ValueError as e:
                        continue
                del combinations
                combinations1 = (lambda Text: XoR(Text.text))(response_combinations1).splitlines()
                for comb in combinations1:
                    try:
                        split_idx = comb.index(":::")
                        cheatName = comb[:split_idx]
                        cheatString = comb[split_idx + 3:]
                        cheat_string = cheatString[1:-1].replace(':', ' ', 1)
                        if cheat_string.strip() in amcache:
                            Detects.append(f"Detected: {cheatName}")
                            break
                    except ValueError as e:
                        continue
                del combinations1
    except Exception as e:
        print(traceback.format_exc())
        
def USBChecker():
    try:
        def convert_csv_to_json(csv_file_path):
            header = ["Device Name", "Description", "Device Type", "Connected", "Safe To Unplug", "Disabled",
                    "USB Hub", "Drive Letter", "Serial Number", "Registry Time 1", "Registry Time 2",
                    "VendorID", "ProductID", "Firmware Revision", "WCID", "USB Class", "USB SubClass", "USB Protocol", "Hub / Port", "Computer Name", "Vendor Name", "Product Name", "ParentId Prefix", "Service Name", "Service Description", "Driver Filename", "Device Class", "Device Mfg", "Friendly Name", "Power", "USB Version", "Driver Description", "Driver Version", "Driver InfSection", "Driver InfPath", "Instance ID", "Capabilites", "Install Time", "First Install Time", "Connect Time", "Disconnect Time"]

            with open(csv_file_path, 'r', encoding='utf-8', errors='replace') as csv_file:
                csv_reader = csv.DictReader(csv_file, fieldnames=header)

                for row in csv_reader:
                    USBLogs.append({
                        "Description": row["Driver Description"],
                        "Connected": row["Connected"],
                        "Connect": row["Connect Time"],
                        "Disconnect": row["Disconnect Time"]
                    })

        Download_File("Nirsoft-USB.exe", f"{CDirectory}\\Scanner-Nirsoft-USB.exe")
        os.system(f"{CDirectory}\\Scanner-Nirsoft-USB.exe /scomma {CDirectory}\\Scanner-USBLogs.csv")
        csv_path = f'{CDirectory}\\Scanner-USBLogs.csv'
        convert_csv_to_json(csv_path)
    except Exception as e:
        print(traceback.format_exc())

def CrashDumpChecker():
    try:
        if not os.path.exists(os.path.expanduser('~\\AppData\\Local\\CrashDumps')):
            return

        now = datetime.datetime.now()
        before = now - timedelta(hours=24)

        File = os.path.join(os.path.expanduser('~\\AppData\\Local\\CrashDumps'), '*')
        Files = glob.glob(File)

        for File in Files:
            modified_files = datetime.datetime.fromtimestamp(os.path.getmtime(File))
            if before < modified_files < now:
                Logs.append("Generic [ A - Crashdump ]")
                return
    except Exception as e:
        print(traceback.format_exc())

def PcaClientChecker():
    try:
        if Explorer_Strings:

            matches = [entry for entry in Explorer_Strings if PcaClient_Regex.search(entry)]

            for match in matches:
                parts = match.split(',')
                if len(parts) >= 6:
                    path = parts[5].strip().replace('"', '').replace('\\\\', '\\')
                    if path.endswith(('.exe', '.dll', '.rpf', '.meta', '.mp4', '.png', '.jpg', '.mp3')):
                        PcaClient.append(path)
                        try:
                            if not Signature_Checker(parts[5].strip()):
                                Detects.append('Unsigned File: {}'.format(path.split('\\')[-1]))
                            else:
                                pass
                        except Exception as e:
                            print(traceback.format_exc())

    except Exception as e:
        print(traceback.format_exc())

def DPSChecker():
    try:
        PID = DPS_PID()

        if PID is None or DPS_Strings is None:
            return
        
        Scanner_Agent = base64.b64decode(Memory().encode('utf-8')).decode('utf-8')
        
        headers = {
            'User-Agent': Scanner_Agent,
            'PIN': f"{Local_PIN}",
            'Security': "Success",
            'Game': "FiveM",
            'Authorization': Authorization()
        }

        del Scanner_Agent

        combinations_link = "https://example.com/api/module/fivem/.DPS"
        response_combinations = requests.get(combinations_link, headers=headers)

        del headers

        combinations = (lambda Text: XoR(Text.text))(response_combinations).splitlines()
                
        for comb in combinations:
            try:
                split_idx = comb.index(":::")
                cheatName = comb[:split_idx]
                cheatString = comb[split_idx + 3:]
                for dumpedString in DPS_Strings:
                    if cheatString.strip() in dumpedString:
                        detection = cheatName
                        Detects.append(f"Detected: {cheatName}")
                        break
            except ValueError as e:
                continue
        del combinations
    except Exception as e:
        print(traceback.format_exc())

def DiagTrackChecker():
    try:
        PID = DiagTrack_PID()
        if PID is None:
            return

        Scanner_Agent = base64.b64decode(Memory().encode('utf-8')).decode('utf-8')
        
        headers = {
            'User-Agent': Scanner_Agent,
            'PIN': f"{Local_PIN}",
            'Security': "Success",
            'Game': "FiveM",
            'Authorization': Authorization()
        }

        del Scanner_Agent

        combinations_link = "https://example.com/api/module/fivem/.DPS"
        response_combinations = requests.get(combinations_link, headers=headers)

        del headers

        combinations = (lambda Text: XoR(Text.text))(response_combinations).splitlines()
        
        for comb in combinations:
            try:
                split_idx = comb.index(":::")
                cheatName = comb[:split_idx]
                cheatString = comb[split_idx + 3:]
                for dumpedString in DiagTrack_Strings:
                    if cheatString.strip() in dumpedString:
                        detection = cheatName
                        Detects.append(f"Detected: {cheatName}")
                        break
            except ValueError as e:
                continue
        del combinations

        Scanner_Agent = base64.b64decode(Memory().encode('utf-8')).decode('utf-8')
        
        headers = {
            'User-Agent': Scanner_Agent,
            'PIN': f"{Local_PIN}",
            'Security': "Success",
            'Game': "FiveM",
            'Authorization': Authorization()
        }

        del Scanner_Agent

        combinations_link = "https://example.com/api/module/fivem/.DiagTrack"
        response_combinations = requests.get(combinations_link, headers=headers)

        del headers

        combinations = (lambda Text: XoR(Text.text))(response_combinations).splitlines()
        
        for comb in combinations:
            try:
                split_idx = comb.index(":::")
                cheatName = comb[:split_idx]
                cheatString = comb[split_idx + 3:]
                for dumpedString in DiagTrack_Strings:
                    if cheatString.strip() in dumpedString:
                        detection = cheatName
                        Detects.append(f"Detected: {cheatName}")
                        break
            except ValueError as e:
                continue
        del combinations
    except Exception as e:
        print(traceback.format_exc())

def SearchIndexerChecker():
    try:
        PID = SearchIndexer_PID()
        if PID is None:
            return

        Scanner_Agent = base64.b64decode(Memory().encode('utf-8')).decode('utf-8')
        
        headers = {
            'User-Agent': Scanner_Agent,
            'PIN': f"{Local_PIN}",
            'Security': "Success",
            'Game': "FiveM",
            'Authorization': Authorization()
        }

        del Scanner_Agent

        combinations_link = "https://example.com/api/module/fivem/.Search_Indexer"
        response_combinations = requests.get(combinations_link, headers=headers)

        del headers

        combinations = (lambda Text: XoR(Text.text))(response_combinations).splitlines()
        
        for comb in combinations:
            try:
                split_idx = comb.index(":::")
                cheatName = comb[:split_idx]
                cheatString = comb[split_idx + 3:]
                for dumpedString in SearchIndexer_Strings:
                    if cheatString.strip() in dumpedString:
                        detection = cheatName
                        Detects.append(f"Detected: {cheatName}")
                        break
            except ValueError as e:
                continue
        del combinations
        if SearchIndexer_Strings:
            SearchIndexer_Strings.clear()
    
    except Exception as e:
        print(traceback.format_exc())

def FiveMChecker():
    try:
        if FiveM_Strings is None:
            return

        Scanner_Agent = base64.b64decode(Memory().encode('utf-8')).decode('utf-8')
        
        headers = {
            'User-Agent': Scanner_Agent,
            'PIN': f"{Local_PIN}",
            'Security': "Success",
            'Game': "FiveM",
            'Authorization': Authorization()
        }

        del Scanner_Agent

        combinations_link = "https://example.com/api/module/fivem/.FiveM"
        response_combinations = requests.get(combinations_link, headers=headers)

        del headers

        combinations = (lambda Text: XoR(Text.text))(response_combinations).splitlines()

        for comb in combinations:
            split_idx = comb.index(":::")
            cheatName = comb[:split_idx]
            cheatString = comb[split_idx + 3:]
            for dumpedString in FiveM_Strings:
                if cheatString.strip() in dumpedString:
                    detection = cheatName
                    Detects.append(f"Detected: {cheatName}")
                    break
        del combinations
        if FiveM_Strings:
            FiveM_Strings.clear()

    except Exception as e:
        print(traceback.format_exc())

def TCPChecker():
    try:
        PID = TCP_PID()

        if PID is None:
            return

        Scanner_Agent = base64.b64decode(Memory().encode('utf-8')).decode('utf-8')
        
        headers = {
            'User-Agent': Scanner_Agent,
            'PIN': f"{Local_PIN}",
            'Security': "Success",
            'Game': "FiveM",
            'Authorization': Authorization()
        }

        del Scanner_Agent

        combinations_link = "https://example.com/api/module/fivem/.TCP"
        response_combinations = requests.get(combinations_link, headers=headers)

        del headers

        combinations = (lambda Text: XoR(Text.text))(response_combinations).splitlines()

        for comb in combinations:
            split_idx = comb.index(":::")
            cheatName = comb[:split_idx]
            cheatString = comb[split_idx + 3:]
            for dumpedString in TCP_Strings:
                if cheatString.strip() in dumpedString:
                    detection = cheatName
                    Detects.append(f"Detected: {cheatName}")
                    break
        del combinations
        if TCP_Strings:
            TCP_Strings.clear()

    except Exception as e:
        print(traceback.format_exc())

def CryptSVCChecker():
    try:
        PID = CryptSVC_PID()

        if PID is None:
            return

        Scanner_Agent = base64.b64decode(Memory().encode('utf-8')).decode('utf-8')
        
        headers = {
            'User-Agent': Scanner_Agent,
            'PIN': f"{Local_PIN}",
            'Security': "Success",
            'Game': "FiveM",
            'Authorization': Authorization()
        }

        del Scanner_Agent

        combinations_link = "https://example.com/api/module/fivem/.TCP"
        response_combinations = requests.get(combinations_link, headers=headers)

        del headers

        combinations = (lambda Text: XoR(Text.text))(response_combinations).splitlines()

        for comb in combinations:
            split_idx = comb.index(":::")
            cheatName = comb[:split_idx]
            cheatString = comb[split_idx + 3:]
            for dumpedString in CryptSVC_Strings:
                if cheatString.strip() in dumpedString:
                    detection = cheatName
                    Detects.append(f"Detected: {cheatName}")
                    break
        del combinations
        if CryptSVC_Strings:
            CryptSVC_Strings.clear()

    except Exception as e:
        print(traceback.format_exc())

def PcaSVChecker():
    try:

        PID = PcaSVC_PID()

        if PID is None:
            return

        Scanner_Agent = base64.b64decode(Memory().encode('utf-8')).decode('utf-8')
        
        headers = {
            'User-Agent': Scanner_Agent,
            'PIN': f"{Local_PIN}",
            'Security': "Success",
            'Game': "FiveM",
            'Authorization': Authorization()
        }

        del Scanner_Agent

        combinations_link = "https://example.com/api/module/fivem/.PcaSVC"
        response_combinations = requests.get(combinations_link, headers=headers)

        del headers

        combinations = (lambda Text: XoR(Text.text))(response_combinations).splitlines()

        for comb in combinations:
            try:
                split_idx = comb.index(":::")
                cheatName = comb[:split_idx]
                cheatString = comb[split_idx + 3:]
                for dumpedString in PcaSVC_Strings:
                    if cheatString.strip() in dumpedString:
                        detection = cheatName
                        Detects.append(f"Detected: {cheatName}")
                        break
            except ValueError as e:
                continue
        del combinations

    except Exception as e:
        print(traceback.format_exc())

def DNSCacheChecker():
    try:
        PID = DNSCache_PID()

        if PID is None:
            return

        Scanner_Agent = base64.b64decode(Memory().encode('utf-8')).decode('utf-8')
        
        headers = {
            'User-Agent': Scanner_Agent,
            'PIN': f"{Local_PIN}",
            'Security': "Success",
            'Game': "FiveM",
            'Authorization': Authorization()
        }

        del Scanner_Agent

        combinations_link = "https://example.com/api/module/fivem/.DNSCache"
        response_combinations = requests.get(combinations_link, headers=headers)

        del headers

        combinations = (lambda Text: XoR(Text.text))(response_combinations).splitlines()

        for comb in combinations:
            try:
                split_idx = comb.index(":::")
                cheatName = comb[:split_idx]
                cheatString = comb[split_idx + 3:]
                for dumpedString in DNSCache_Strings:
                    if cheatString.strip() in dumpedString:
                        detection = cheatName
                        Detects.append(f"Detected: {cheatName}")
                        break
            except ValueError as e:
                
                continue
        del combinations
        if DNSCache_Strings:
            DNSCache_Strings.clear()

    except Exception as e:
        print(traceback.format_exc())

def LsassChecker():
    try:
        PID = Lsass_PID()

        if PID is None:
            return
        
        Scanner_Agent = base64.b64decode(Memory().encode('utf-8')).decode('utf-8')
        
        headers = {
            'User-Agent': Scanner_Agent,
            'PIN': f"{Local_PIN}",
            'Security': "Success",
            'Game': "FiveM",
            'Authorization': Authorization()
        }

        del Scanner_Agent

        combinations_link = "https://example.com/api/module/fivem/.Lsass"
        response_combinations = requests.get(combinations_link, headers=headers)

        del headers

        combinations = (lambda Text: XoR(Text.text))(response_combinations).splitlines()

        for comb in combinations:
            split_idx = comb.index(":::")
            cheatName = comb[:split_idx]
            cheatString = comb[split_idx + 3:]
            for dumpedString in Lsass_Strings:
                if cheatString.strip() in dumpedString:
                    detection = cheatName
                    Detects.append(f"Detected: {cheatName}")
                    break
        del combinations

    except Exception as e:
        print(traceback.format_exc())

def Generic_Detection():
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, Task_Scheduler) as key:
            for i in range(winreg.QueryInfoKey(key)[0]):
                sid = winreg.EnumKey(key, i)
                with winreg.OpenKey(key, sid) as sid_key:
                    author_value = None
                    date_string = None
                    for j in range(winreg.QueryInfoKey(sid_key)[1]):
                        name, value, data_type = winreg.EnumValue(sid_key, j)
                        if name == 'SequenceNumber' or name == 'Version':
                            continue
                        if data_type == winreg.REG_SZ and name == 'Author':
                            author_value = value
                        if data_type == winreg.REG_SZ and name == 'Date':
                            date_string = value
                    if author_value and date_string and Username in author_value:
                        try:
                            date_part, time_part = date_string.split('T')
                            if 'Z' in time_part:
                                time_part = time_part.replace('Z', '')
                            formatted_date = datetime.datetime.strptime(date_part, "%Y-%m-%d")
                            formatted_time = datetime.datetime.strptime(time_part.split('.')[0], "%H:%M:%S")
                            combined_datetime = formatted_date.replace(hour=formatted_time.hour, minute=formatted_time.minute, second=formatted_time.second)
                            time_difference = datetime.datetime.now() - combined_datetime
                            if time_difference < datetime.timedelta(hours=24):
                                Detects.append(f"Task Scheduler: {combined_datetime.strftime('%H:%M:%S, %d.%m.%Y')}")
                        except ValueError:
                            pass
                        except Exception as e:
                            print(traceback.format_exc())
    except Exception as e:
        print(traceback.format_exc())
    try:
        if Explorer_Strings:
            if "Cercare = ) (0x" in Explorer_Strings:
                Detects.append("Generic Clear Method")

        if "curl.exe" in Explorer_Strings:
            curl_index = Explorer_Strings.index("curl.exe")
            if "url" in Explorer_Strings[curl_index:]:
                Detects.append("Generic Bypass Download")

        if "fsutil usn deletejournal /d" in DiagTrack_Strings or "fsutil usn createjournal m=1000 a=100" in SysMain_Strings:
            Detects.append("Generic Journal Clear")

        if "Reg Delete" in DiagTrack_Strings:
            Detects.append("Generic Regedit Delete")
            
    except Exception as e:
        print(traceback.format_exc())

def BypassAtCDirectoryt():
    DPS_Service = psutil.Process(DPS_PID())
    EventLOG_Service = psutil.Process(EventLOG_PID())
    DiagTrack_Service = psutil.Process(DiagTrack_PID())
    SysMain_Service = psutil.Process(SysMain_PID())
    DNSCache_Service = psutil.Process(DNSCache_PID())
    Explorer_Process = psutil.Process(Explorer_PID())
    WinLogon_Process = psutil.Process(WinLogon_PID())

    DPS_Create = DPS_Service.create_time()
    EventLog_Create = EventLOG_Service.create_time()
    DiagTrack_Create = DiagTrack_Service.create_time()
    SysMain_Create = SysMain_Service.create_time()
    DNSCache_Create = DNSCache_Service.create_time()
    Explorer_Create = Explorer_Process.create_time()
    WinLogon = WinLogon_Process.create_time()

    Formatted_Time1 = datetime.datetime.fromtimestamp(DPS_Create)
    Formatted_Time2 = datetime.datetime.fromtimestamp(EventLog_Create)
    Formatted_Time3 = datetime.datetime.fromtimestamp(DiagTrack_Create)
    Formatted_Time4 = datetime.datetime.fromtimestamp(SysMain_Create)
    Formatted_Time5 = datetime.datetime.fromtimestamp(DNSCache_Create)
    Formatted_Time6 = datetime.datetime.fromtimestamp(Explorer_Create)
    Formatted_Time7 = datetime.datetime.fromtimestamp(WinLogon)

    BT_TS = psutil.boot_time()
    BT = datetime.datetime.fromtimestamp(BT_TS)

    try:
        EventLOG_Connection = win32evtlog.OpenEventLog(None, "Application")

        Flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        Total_Entries = win32evtlog.GetNumberOfEventLogRecords(EventLOG_Connection)

        if Total_Entries <= 10:
            Detects.append("EventLog Manipulated!")
            pass

        events = 1
        while events:
            events = win32evtlog.ReadEventLog(EventLOG_Connection, Flags, 0)
            for event in events:
                Event_ID = event.EventID & 0xFFFF
                Event_Time = event.TimeGenerated
                Formatted_Event_Time = Event_Time.strftime("%H:%M:%S, %d.%m.%Y")
                Event_Message = event.StringInserts if hasattr(event, "StringInserts") else ""
                if Event_ID == 3079:
                    Warnings.append(f"Journal Deleted at {Formatted_Event_Time}")

    except Exception as e:
        print(traceback.format_exc())
    
    finally:
        win32evtlog.CloseEventLog(EventLOG_Connection)

    try:
        drives = [chr(i) for i in range(ord('A'), ord('Z') + 1) if os.path.exists(f"{chr(i)}:\\")]
        last_boot_time = Boot_Time()
        for drive_letter in drives:
            if drive_letter == 'C':
                continue
            
            root_path = f"{drive_letter}:\\"
            system_info_path = os.path.join(root_path, "System Volume Information")

            if os.path.exists(system_info_path):
                last_modification = os.path.getmtime(system_info_path)
                last_modification_datetime = datetime.datetime.fromtimestamp(last_modification)

                if last_modification_datetime > last_boot_time:
                    Detects.append(f"Generic USB")
    except Exception as e:
        print(traceback.format_exc())

    if 'OSFMount' in DiagTrack_Strings:
        Detects.append("Generic Virtual USB")

    try:
        if not (Formatted_Time1 - BT < datetime.timedelta(minutes=5)) and DPS_PID() is not None:
            Detects.append("DPS Service Restarted")
        
        if not (Formatted_Time2 - BT < datetime.timedelta(minutes=5)) and EventLOG_PID() is not None:
            Detects.append("EventLOG Service Restarted")

        if not (Formatted_Time3 - BT < datetime.timedelta(minutes=5)) and DiagTrack_PID() is not None:
            Detects.append("DiagTrack Service Restarted")

        if not (Formatted_Time4 - BT < datetime.timedelta(minutes=5)) and SysMain_PID() is not None:
            Detects.append("SysMain Service Restarted")

        if not (Formatted_Time5 - BT < datetime.timedelta(minutes=5)) and DNSCache_PID() is not None:
            Detects.append("DNSCache Service Restarted")

        if not (Formatted_Time6 - BT < datetime.timedelta(minutes=5)) and Explorer_PID() is not None:
            if (Formatted_Time6 - BT) > datetime.timedelta(seconds=300):
                Difference = abs(Formatted_Time6 - Formatted_Time7)
                MD = timedelta(minutes=2)
                if not Difference <= MD:
                    Detects.append("Explorer.exe Process Restarted")

    except Exception as e:
        print(traceback.format_exc())

    PID_EVT = EventLOG_PID()
    if PID_EVT is not None:
        Powershell_Strings = ["Invoke-RestMethod","Invoke-Expression","import base64","base64_decode","base32_decode","base64_encode","base32_encode","Convert.FromBase32String","Convert.FromBase64String","Base64.getDecoder()","Base32.getDecoder()","js-base64","js-base32","base64-js","base32-js","base64.b64decode","base32.b32decode","base64.b64encode","base32.b32encode","Base64.decode64","Base32.decode32","Base64.encode64","Base32.encode32","encoding/base64","encoding/base32","decoding/base32","decoding/base64","decode_base64","decode_base32","encode_base64","encode_base32","base64::decode","base32::decode","base64::encode","base64::encode","Base64.decode","Base64.encode","Base32.decode","Base32.encode","NSString base64Decode","NSString base32Decode","NSString base32Encode","NSString base64Encode","com.google.common.io.BaseEncoding.base64.decode","com.google.common.io.BaseEncoding.base32.decode","com.google.common.io.BaseEncoding.base32.encode","com.google.common.io.BaseEncoding.base64.encode","Codec.Binary.Base64.String.decode","Codec.Binary.Base32.String.decode","Codec.Binary.Base64.String.encode","Codec.Binary.Base32.String.encode",":base64.decode_to_string",":base32.decode_to_string",":base32.encode_to_string",":base64.encode_to_string","Base64.base64decode","Base64.base64encode","Base32.base32encode","Base32.base32decode","btoa()","atob()","Convert.ToBase64String()","Convert.ToBase32String()","Convert.FromBase64String()","Convert.FromBase32String()","ConvertTo-Base64String","ConvertTo-Base32String","ConvertFrom-Base32String","ConvertFrom-Base64String","base64decode","base64encode","base32decode","base32encode","org.apache.commons.codec.binary.Base64.decodeBase64","org.apache.commons.codec.binary.Base32.decodeBase32","org.apache.commons.codec.binary.Base32.encodeBase32","org.apache.commons.codec.binary.Base64.encodeBase64","base64Url.decode","base64Url.encode","base32Url.decode","base32Url.encode","System.Text.Encoding.Default.GetString(System.Convert.FromBase64String","System.Text.Encoding.Default.GetString(System.Convert.ToBase64String","System.Text.Encoding.Default.GetString(System.Convert.FromBase32String","System.Text.Encoding.Default.GetString(System.Convert.ToBase32String","base64url:decode/1","base32url:decode/1","base32url:encode/1","base64url:encode/1","base64dec/2","base32dec/2","jsonlite::base64_decode","jsonlite::base32_decode","jsonlite::base64_encode","jsonlite::base32_encode","Base64.decode_bytes","Base32.decode_bytes","Base32.encode_bytes","Base32.decode_bytes","Ada.Strings.Base64.Decoder.Decode","Ada.Strings.Base64.Encoder.Encode","Ada.Strings.Base32.Decoder.Decode","Ada.Strings.Base32.Encoder.Encode","decode64_char","encode64_char","decode32_char","encode32_char","Base64.decode_string","Base32.decode_string","Base32.encode_string","Base64.encode_string","base64/decode","base64/encode","base32/decode","base32/encode","import base64","base64.b32encode","base64.b32decode","vssadmin delete shadows"]

        for B_String in Powershell_Strings:
            for String in EventLog_Strings:
                if B_String.lower() in String.lower():
                    Detects.append("ImportCode bypass [ invoke ]")
                    break

        if "/flushdns" in EventLog_Strings:
            Detects.append("Generic DNS Clear")
    else:
        pass

    PID_DGT = DiagTrack_PID()
    if PID_DGT is not None:
        Powershell_Strings = ["Invoke-RestMethod","Invoke-Expression","import base64","base64_decode","base32_decode","base64_encode","base32_encode","Convert.FromBase32String","Convert.FromBase64String","Base64.getDecoder()","Base32.getDecoder()","js-base64","js-base32","base64-js","base32-js","base64.b64decode","base32.b32decode","base64.b64encode","base32.b32encode","Base64.decode64","Base32.decode32","Base64.encode64","Base32.encode32","encoding/base64","encoding/base32","decoding/base32","decoding/base64","decode_base64","decode_base32","encode_base64","encode_base32","base64::decode","base32::decode","base64::encode","base64::encode","Base64.decode","Base64.encode","Base32.decode","Base32.encode","NSString base64Decode","NSString base32Decode","NSString base32Encode","NSString base64Encode","com.google.common.io.BaseEncoding.base64.decode","com.google.common.io.BaseEncoding.base32.decode","com.google.common.io.BaseEncoding.base32.encode","com.google.common.io.BaseEncoding.base64.encode","Codec.Binary.Base64.String.decode","Codec.Binary.Base32.String.decode","Codec.Binary.Base64.String.encode","Codec.Binary.Base32.String.encode",":base64.decode_to_string",":base32.decode_to_string",":base32.encode_to_string",":base64.encode_to_string","Base64.base64decode","Base64.base64encode","Base32.base32encode","Base32.base32decode","btoa()","atob()","Convert.ToBase64String()","Convert.ToBase32String()","Convert.FromBase64String()","Convert.FromBase32String()","ConvertTo-Base64String","ConvertTo-Base32String","ConvertFrom-Base32String","ConvertFrom-Base64String","base64decode","base64encode","base32decode","base32encode","org.apache.commons.codec.binary.Base64.decodeBase64","org.apache.commons.codec.binary.Base32.decodeBase32","org.apache.commons.codec.binary.Base32.encodeBase32","org.apache.commons.codec.binary.Base64.encodeBase64","base64Url.decode","base64Url.encode","base32Url.decode","base32Url.encode","System.Text.Encoding.Default.GetString(System.Convert.FromBase64String","System.Text.Encoding.Default.GetString(System.Convert.ToBase64String","System.Text.Encoding.Default.GetString(System.Convert.FromBase32String","System.Text.Encoding.Default.GetString(System.Convert.ToBase32String","base64url:decode/1","base32url:decode/1","base32url:encode/1","base64url:encode/1","base64dec/2","base32dec/2","jsonlite::base64_decode","jsonlite::base32_decode","jsonlite::base64_encode","jsonlite::base32_encode","Base64.decode_bytes","Base32.decode_bytes","Base32.encode_bytes","Base32.decode_bytes","Ada.Strings.Base64.Decoder.Decode","Ada.Strings.Base64.Encoder.Encode","Ada.Strings.Base32.Decoder.Decode","Ada.Strings.Base32.Encoder.Encode","decode64_char","encode64_char","decode32_char","encode32_char","Base64.decode_string","Base32.decode_string","Base32.encode_string","Base64.encode_string","base64/decode","base64/encode","base32/decode","base32/encode","import base64","base64.b32encode","base64.b32decode","vssadmin delete shadows"]

        for B_String in Powershell_Strings:
            for String in DiagTrack_Strings:
                if B_String.lower() in String.lower():
                    Detects.append("Generic Importcode Byprint(traceback.format_exc())")
                    break

        if "/flushdns" in DiagTrack_Strings:
            Detects.append("DNSCache Cleared")
    else:
        pass

def RecordingChecker():
    try:
        Scanner_Agent = base64.b64decode(Memory().encode('utf-8')).decode('utf-8')
        
        headers = {
            'User-Agent': Scanner_Agent,
            'PIN': f"{Local_PIN}",
            'Security': "Success",
            'Game': "Game",
            'Authorization': Authorization()
        }

        del Scanner_Agent

        combinations_link = "https://example.com/api/module/fivem/.Recording"
        response_combinations = requests.get(combinations_link, headers=headers)

        del headers

        combinations = (lambda Text: XoR(Text.text))(response_combinations).splitlines()
    
        for comb in combinations:
            try:
                split_idx = comb.index(":::")
                String = comb[:split_idx].strip()
                Software = comb[split_idx + 3:].strip()
                if String.lower() in [proc.info["name"] for proc in psutil.process_iter(['name'])]:
                    Recording.append(Software)
            except ValueError as e:
                continue
        del combinations

    except Exception as e:
        print(traceback.format_exc())

def ExplorerChecker():
    try:
        PID = Explorer_PID()

        if PID is None:
            return
        
        if Explorer_Strings is None:
            return

        Scanner_Agent = base64.b64decode(Memory().encode('utf-8')).decode('utf-8')
        
        headers = {
            'User-Agent': Scanner_Agent,
            'PIN': f"{Local_PIN}",
            'Security': "Success",
            'Game': "FiveM",
            'Authorization': Authorization()
        }

        del Scanner_Agent

        combinations_link = "https://example.com/api/module/fivem/.Explorer"
        response_combinations = requests.get(combinations_link, headers=headers)

        del headers

        combinations = (lambda Text: XoR(Text.text))(response_combinations).splitlines()
        
        for comb in combinations:
            split_idx = comb.index(":::")
            cheatName = comb[:split_idx]
            cheatString = comb[split_idx + 3:]
            for dumpedString in Explorer_Strings:
                if cheatString.strip() in dumpedString:
                    detection = cheatName
                    Detects.append(f"Detected: {detection}")
                    break
        del combinations
    except Exception as e:
        print(traceback.format_exc())

def SIHostChecker():
    try:
        PID = SIHost_PID()

        if PID is None:
            return
        
        if SIHost_Strings is None:
            return

        Scanner_Agent = base64.b64decode(Memory().encode('utf-8')).decode('utf-8')
        
        headers = {
            'User-Agent': Scanner_Agent,
            'PIN': f"{Local_PIN}",
            'Security': "Success",
            'Game': "FiveM",
            'Authorization': Authorization()
        }

        del Scanner_Agent

        combinations_link = "https://example.com/api/module/fivem/.SIHost"
        response_combinations = requests.get(combinations_link, headers=headers)

        del headers

        combinations = (lambda Text: XoR(Text.text))(response_combinations).splitlines()
        
        for comb in combinations:
            split_idx = comb.index(":::")
            cheatName = comb[:split_idx]
            cheatString = comb[split_idx + 3:]
            for dumpedString in SIHost_Strings:
                if cheatString.strip() in dumpedString:
                    detection = cheatName
                    Warnings.append(f"Visited: {detection} [ SIHOST ]")
                    break
        del combinations
        if SIHost_Strings:
            SIHost_Strings.clear()
    except Exception as e:
        print(traceback.format_exc())

def TaskHostChecker():
    try:
        PID = TaskHost_PID()

        if PID is None:
            return
        
        if TaskHost_Strings is None:
            return

        Scanner_Agent = base64.b64decode(Memory().encode('utf-8')).decode('utf-8')
        
        headers = {
            'User-Agent': Scanner_Agent,
            'PIN': f"{Local_PIN}",
            'Security': "Success",
            'Game': "FiveM",
            'Authorization': Authorization()
        }

        del Scanner_Agent

        combinations_link = "https://example.com/api/module/fivem/.TaskHostW"
        response_combinations = requests.get(combinations_link, headers=headers)

        del headers

        combinations = (lambda Text: XoR(Text.text))(response_combinations).splitlines()
        
        for comb in combinations:
            split_idx = comb.index(":::")
            cheatName = comb[:split_idx]
            cheatString = comb[split_idx + 3:]
            for dumpedString in TaskHost_Strings:
                if cheatString.strip() in dumpedString:
                    detection = cheatName
                    Detects.append(f"Detected: {detection} [ TaskHost ]")
                    break
        del combinations
        if TaskHost_Strings:
            TaskHost_Strings.clear()
    except Exception as e:
        print(traceback.format_exc())

def LastActivityView():
    try:
        def LA_BAM():
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, Bam_Path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        sid = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, sid) as sid_key:
                            for j in range(winreg.QueryInfoKey(sid_key)[1]):
                                name, value, data_type = winreg.EnumValue(sid_key, j)
                                if name == 'SequenceNumber' or name == 'Version':
                                    continue
                                date = struct.unpack("<Q", value[0:8])[0]
                                entry_date = datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=date/10)
                                formatted_date = entry_date.strftime("%d.%m.%Y, %H:%M:%S")
                                formatted_record = {'Path': name, 'Time': formatted_date}
                                LastAV.append(formatted_record)
            except PermissionError:
                pass

        def Original_Path_Path(Path):
            try:
                Shell = Dispatch("WScript.Shell")
                Shortcut = Shell.CreateShortcut(Path)
                return Shortcut.Targetpath
            except Exception as e:
                return None
            
        def Creation_Date(Path):
            try:
                timestamp = os.path.getctime(Path)
                return datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y, %H:%M:%S')
            except Exception as e:
                return "25.02.2008, 19:15:00"

        def LA_Recent():
            try:
                pythoncom.CoInitialize()
                try:
                    Recent_Files = glob.glob(os.path.join(RecentFolder, '*.lnk'))
                    if not Recent_Files:
                        return

                    for Short_File in Recent_Files:
                        Original_Path = Original_Path_Path(Short_File)
                        if Original_Path:
                            Original_Path_Full = Original_Path.replace("\\", "\\\\")
                            creation_date = Creation_Date(Short_File)
                            formatted_record = {'Path': Original_Path_Full, 'Time': creation_date}
                            LastAV.append(formatted_record)
                        else:
                            creation_date = Creation_Date(Short_File)
                            Short_Path_Full = Short_File.replace("\\", "\\\\")
                            formatted_record = {'Path': Short_Path_Full, 'Time': creation_date}
                            LastAV.append(formatted_record)
                except Exception as e:
                    print(e)
                finally:
                    pythoncom.CoUninitialize()

            except Exception as e:
                print(e)

        def LA_Prefetch():
            try:
                PrefetchFolder = os.path.expandvars('C:\\Windows\\Prefetch')
                for filename in os.listdir(PrefetchFolder):
                    if filename.endswith(".pf"):
                        filename_without_info = filename.rsplit('-', 1)[0]
                        
                        file_path = os.path.join(PrefetchFolder, filename)
                        entry_date = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                        formatted_date = entry_date.strftime("%d.%m.%Y, %H:%M:%S")
                        formatted_record = {'Path': filename_without_info, 'Time': formatted_date}
                        LastAV.append(formatted_record)
            except PermissionError:
                pass

        def Prefetch_Parser():
            try:
                PrefetchFolder = os.path.expandvars(r'C:\Windows\Prefetch')

                for filename in os.listdir(PrefetchFolder):
                    if filename.endswith(".pf"):
                        full_path = os.path.join(PrefetchFolder, filename)
                        modification_time = os.path.getmtime(full_path)
                        entry_date = datetime.datetime.fromtimestamp(modification_time)
                        formatted_date = entry_date.strftime("%d.%m.%Y, %H:%M:%S")
                        
                        filename_without_info = filename.rsplit('-', 1)[0]
                        for file in Explorer_Strings:
                            if filename_without_info in file:
                                if "\\" in file and ".pf" not in file:
                                    formatted_record = {'Path': file, 'Time': formatted_date}
                                    LastAV.append(formatted_record)
            except PermissionError:
                pass
            except Exception as e:
                print("An error occurred:", traceback.format_exc())

        def LA_Scheduler():
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, Task_Scheduler) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        sid = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, sid) as sid_key:
                            author_value = None
                            date_string = None
                            file_path = None
                            for j in range(winreg.QueryInfoKey(sid_key)[1]):
                                name, value, data_type = winreg.EnumValue(sid_key, j)
                                if name == 'SequenceNumber' or name == 'Version':
                                    continue
                                if data_type == winreg.REG_SZ and name == 'Author':
                                    author_value = value
                                if data_type == winreg.REG_SZ and name == 'Date':
                                    date_string = value
                                if data_type == winreg.REG_SZ and name == 'Path':
                                    file_path = value
                            if author_value and date_string and file_path:
                                try:
                                    if 'T' in date_string and date_string.endswith('Z'):
                                        formatted_datetime = datetime.datetime.fromisoformat(date_string[:-1])
                                    else:
                                        date_part, time_part = date_string.split('T')
                                        if '-' in time_part or '+' in time_part:
                                            time_part = time_part.split('-')[0].split('+')[0]
                                        try:
                                            formatted_date = datetime.datetime.strptime(date_part, "%Y-%m-%d")
                                            formatted_time = datetime.datetime.strptime(time_part.split('.')[0], "%H:%M:%S")
                                        except ValueError:
                                            formatted_date = datetime.datetime.strptime(date_part, "%Y-%m-%d")
                                            formatted_time = datetime.datetime.strptime(time_part.split('.')[0], "%d.%m.%Y, %H:%M:%S")
                                        combined_datetime = formatted_date.replace(hour=formatted_time.hour, minute=formatted_time.minute, second=formatted_time.second)
                                        if time_part.endswith('Z'):
                                            combined_datetime = combined_datetime.astimezone(datetime.timezone.utc).astimezone()
                                        formatted_datetime = combined_datetime
                                    
                                    formatted_record = {'Path': file_path, 'Time': formatted_datetime.strftime('%d.%m.%Y, %H:%M:%S')}
                                    LastAV.append(formatted_record)
                                except ValueError as e:
                                    print(e)
                                except Exception as e:
                                    print(e)
            except PermissionError:
                pass
            except FileNotFoundError:
                pass
            except Exception as e:
                print(e)

        LA_BAM()
        LA_Recent()
        LA_Prefetch()
        LA_Scheduler()
        Prefetch_Parser()

        LastAV.sort(key=lambda x: datetime.datetime.strptime(x['Time'], "%d.%m.%Y, %H:%M:%S"), reverse=True)
    except Exception as e:
        print(traceback.format_exc())

def RecycleBin_Information(recycle_bin_path):
    try:
        if not os.path.exists(recycle_bin_path):
            raise OSError("Failed to find Recycle Bin folder")

        latest_deletion_time = None
        for filename in os.listdir(recycle_bin_path):
            filepath = os.path.join(recycle_bin_path, filename)
            deletion_time = os.path.getmtime(filepath)

            if latest_deletion_time is None or deletion_time > latest_deletion_time:
                latest_deletion_time = deletion_time

        return latest_deletion_time
    except Exception as e:
        print(traceback.format_exc())

def RecycleBin():
    try:
        recycle_bin_path = r'C:\$Recycle.Bin'
        latest_deletion_time = RecycleBin_Information(recycle_bin_path)

        if latest_deletion_time is not None:
            dt = datetime.datetime.fromtimestamp(latest_deletion_time)
            current_time = datetime.datetime.now().timestamp()
            uptime_seconds = current_time - dt.timestamp()
            days, seconds = divmod(uptime_seconds, 86400)
            hours, seconds = divmod(seconds, 3600)
            minutes, seconds = divmod(seconds, 60)

            uptime_string = ""
            if days > 0:
                uptime_string += f"{int(days)}d, "
            if hours > 0:
                uptime_string += f"{int(hours)}h, "
            if minutes > 0:
                uptime_string += f"{int(minutes)}m, "
            if seconds > 0:
                uptime_string += f"{int(seconds)}s ago"

            if minutes < 30:
                Logs.append(f"Recycle-Bin Modified: {uptime_string}")

            return uptime_string
        else:
            return "N/A"
    except Exception as e:
        print(traceback.format_exc())

def System_Information():
    try:

        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, System_Install) as key:
            try:
                Install_Date_R, _ = winreg.QueryValueEx(key, System_Install_Key)
                Install_Date = datetime.datetime.fromtimestamp(Install_Date_R)
                Install_Date_H = Install_Date - datetime.timedelta(hours=1)
                Result = Install_Date_H.strftime("%d.%m.%Y, %H:%M:%S")

                return Result if Result else 'N/A'
            except FileNotFoundError:
                return 'N/A'
    except Exception as e:
        return 'N/A'

def VMCheck():
    try:
        VMCheck.vm = 'False'
        system = platform.uname()
        if 'Microsoft' in system.release:
            VMCheck.vm = 'True'
        elif 'Hypervisor' in system.release:
            VMCheck.vm = 'True'
    except Exception as e:
        print(traceback.format_exc())

def JournalChecker():
    try:
        Download_File(f"Journal.exe", f"{CDirectory}\\Journal.exe")
        os.system(f'"{CDirectory}\\Journal.exe" > {CDirectory}\\Journal.txt')

        file_directory = f'{CDirectory}'
        file_name = 'Journal.txt'

        file_path = os.path.join(file_directory, file_name)

        Scanner_Agent = base64.b64decode(Memory().encode('utf-8')).decode('utf-8')

        headers = {
            'User-Agent': Scanner_Agent,
            'PIN': f"{Local_PIN}",
            'Security': "Success",
            'Game': "FiveM",
            'Authorization': Authorization()
        }

        del Scanner_Agent

        combinations_link = "https://example.com/api/module/fivem/.Journal"
        response_combinations = requests.get(combinations_link, headers=headers)

        del headers

        combinations = (lambda Text: XoR(Text.text))(response_combinations).splitlines()

        with open(file_path, mode="r", encoding='utf-8', errors='replace') as file:
            Content = file.read()
            if Content.strip() == "":
                return

            try:
                data = json.loads(Content)
            except json.JSONDecodeError:
                return

            for comb in combinations:
                split_idx = comb.index(":::")
                cheatName = comb[:split_idx]
                Cheat_String = comb[split_idx + 3:]
                for line in Content.lower().split('\n'):
                    if Cheat_String.strip() in line:
                        Detects.append(cheatName)
                        break
            del combinations

            if "OldestEntry" in data:
                oldest_entry_str = data["OldestEntry"]

                current_time = datetime.datetime.now()
                new_time = current_time - datetime.timedelta(hours=24)

                oldest_entry_datetime = Valid_Journal(oldest_entry_str)

                if oldest_entry_datetime and oldest_entry_datetime > new_time:
                    Warnings.append("Journal Manipulated")

            if thread15.is_alive:
                thread15.join()
           
            if "Infos" not in data or len(data["Infos"]) < 100:
                Detects.append("Generic Journal Delete")

    except Exception as e:
        print(traceback.format_exc())

def Eulen_Detection():
    try:
        Machine_List = os.listdir(r'C:\ProgramData\Microsoft\Crypto\RSA\MachineKeys')
        Certificates_List = os.listdir(f"C:\\Users\\{Username}\\AppData\\Roaming\\Microsoft\\SystemCertificates\\My\\Certificates")
        Current_Time = time.time()
        Day = Current_Time - (24 * 60 * 60)

        Recent_Machine = [file for file in Machine_List if os.path.isfile(os.path.join(r'C:\ProgramData\Microsoft\Crypto\RSA\MachineKeys', file)) and os.path.getmtime(os.path.join(r'C:\ProgramData\Microsoft\Crypto\RSA\MachineKeys', file)) > Day]
        Recent_Certificates = [file for file in Certificates_List if os.path.isfile(os.path.join(f"C:\\Users\\{Username}\\AppData\\Roaming\\Microsoft\\SystemCertificates\\My\\Certificates", file)) and os.path.getmtime(os.path.join(f"C:\\Users\\{Username}\\AppData\\Roaming\\Microsoft\\SystemCertificates\\My\\Certificates", file)) > Day]

        combined_recent_files = Recent_Machine + Recent_Certificates

        if len(combined_recent_files) > 8:
            Detects.append("Generic Eulen")
    except Exception as e:
        print(traceback.format_exc())

def Skript_Detection():
    #outdated lsass checking.
    return None

def SteamChecker():
    try:
        steam_paths = []

        if os.name == 'nt':
            default_steam_path = os.path.join(os.environ.get('ProgramFiles(x86)', ''), 'Steam')
            if os.path.exists(default_steam_path):
                steam_paths.append(default_steam_path)

        for drive in ['C:', 'D:', 'E:', 'F:']:
            custom_steam_path = os.path.join(drive, 'Steam')
            if os.path.exists(custom_steam_path) and custom_steam_path not in steam_paths:
                steam_paths.append(custom_steam_path)

        for steam_path in steam_paths:
            loginusers_path = os.path.join(steam_path, 'config', 'loginusers.vdf')
            if os.path.exists(loginusers_path):
                with open(loginusers_path, 'r', encoding='utf-8', errors='replace') as file:
                    data = vdf.load(file)
                    users_data = data.get("users")
                    if users_data:
                        for user_id, user_info in users_data.items():
                            account_name = user_info.get("AccountName")
                            if account_name:
                                Steam.append(f"{account_name} - {user_id}")
        return steam_paths
    except Exception as e:
        print(traceback.format_exc())

def Scanner():
    try:
        global Stop_Monitor

        def get_time_ago(file_path):
            try:
                creation_time = os.path.getctime(file_path)
                time_ago = datetime.datetime.now() - datetime.datetime.fromtimestamp(creation_time)
                return time_ago
            except Exception as e:
                print(traceback.format_exc())

        def format_time_ago(time_delta):
            try:
                seconds = time_delta.total_seconds()
                if seconds < 60:
                    return f"{int(seconds)} seconds ago"
                elif seconds < 3600:
                    return f"{int(seconds / 60)} minutes ago"
                elif seconds < 86400:
                    return f"{int(seconds / 3600)} hours ago"
                else:
                    return f"{int(seconds / 86400)} days ago"
            except Exception as e:
                print(traceback.format_exc())
        try:

            for fivem_location in FiveM:
                log_location = os.path.join(fivem_location, "logs")
                if os.path.exists(log_location) and os.path.isdir(log_location):
                    log_files = [file for file in os.listdir(log_location) if file.endswith('.log')]
                    if log_files:
                        latest_log_files = sorted(log_files, key=lambda x: os.path.getmtime(os.path.join(log_location, x)), reverse=True)[:5]
                        for log_file in latest_log_files:
                            log_path = os.path.join(log_location, log_file)
                            with open(log_path, 'r', encoding='utf-8', errors='replace') as file_log:
                                for line in file_log:
                                    if "Loaded graphics mod:" in line:
                                        logname = line.split("Loaded graphics mod: ")[1].strip()
                                        log_name = os.path.basename(os.path.normpath(logname))
                                        time_ago = get_time_ago(log_path)
                                        formatted_time_ago = format_time_ago(time_ago)
                                        Logs.append(f"FiveM [ Internal - Plugins ]: {log_name}")
                    else:
                        pass
                else:
                    pass

            if not FiveM:
                pass
        except Exception as e:
            print(traceback.format_exc())

        try:
            for FM in FiveM:
                CitizenFX_Path = os.path.join(FM, "CitizenFX.ini")
                if os.path.exists(CitizenFX_Path):
                    with open(CitizenFX_Path, encoding="utf-8", errors='replace', mode='r') as File:
                        for line in File:
                            if 'IVPath=' in line:
                                GTAV_Path = line.strip().split('IVPath=')[1].strip().replace('\\', '\\\\')
                                imgui_ini_path = os.path.join(GTAV_Path, "imgui.ini")
                                d3d10 = os.path.join(GTAV_Path, "d3d10.dll")
                                if os.path.exists(imgui_ini_path):
                                    Detects.append("Generic [ GTA Folder ]")
                                    with open(imgui_ini_path, encoding='utf-8', errors='replace', mode='r') as IMGUI_FILE:
                                        for line in IMGUI_FILE:
                                            if "redengine" in line.lower():
                                                Detects.append("RedEngine")
                                if os.path.exists(d3d10):
                                    Detects.append("Generic Cheat")
        except Exception as e:
            print(traceback.format_exc())
                            
        try:
            service = BAM_PID()
            if not service is None:
                if not service is None or "AccessDenied" in service:
                    if service and service['status'] == 'stopped':
                        Logs.append("Service Bam Stopped")

                    def convert_filetime_to_datetime(filetime):
                        return datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=filetime/10)

                    try:
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, Bam_Path) as key:
                            for i in range(winreg.QueryInfoKey(key)[0]):
                                sid = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, sid) as sid_key:
                                    for j in range(winreg.QueryInfoKey(sid_key)[1]):
                                        name, value, data_type = winreg.EnumValue(sid_key, j)
                                        if name == 'SequenceNumber' or name == 'Version':
                                            continue
                                        date = struct.unpack("<Q", value[0:8])[0]
                                        entry_date = convert_filetime_to_datetime(date)
                                        formatted_date = entry_date.strftime("%d.%m.%Y, %H:%M:%S")
                                        Bam.append(f"{name} - {formatted_date}")
                    except PermissionError:
                        pass
            else:            
                Detects.append("Bam Disabled")
        except Exception as e:
            print(traceback.format_exc())
        try:
            system = System_Information()
        except Exception as e:
            print(traceback.format_exc())
        try:
            fivem = FiveM_UPTime()
        except Exception as e:
            print(traceback.format_exc())
        try:
            explorer = Explorer_UPTime()
        except Exception as e:
            print(traceback.format_exc())
        try:
            eventlog = EventLog_UPTime()
        except Exception as e:
            print(traceback.format_exc())
        try:
            appinfos = AppInfo_UPTime()
        except Exception as e:
            print(traceback.format_exc())

        try:
            if os.path.exists("C:\\Windows\\System32\\sru\\SRUDB.dat"):
                Scanner_Agent = base64.b64decode(Memory().encode('utf-8')).decode('utf-8')
        
                headers = {
                    'User-Agent': Scanner_Agent,
                    'PIN': f"{Local_PIN}",
                    'Security': "Success",
                    'Game': "FiveM",
                    'Authorization': Authorization()
                }

                del Scanner_Agent

                combinations_link = "https://example.com/api/module/fivem/.DPS"
                response_combinations = requests.get(combinations_link, headers=headers)

                del headers

                combinations = (lambda Text: XoR(Text.text))(response_combinations).splitlines()
                with open("C:\\Windows\\System32\\sru\\SRUDB.dat", mode="rb") as file:
                    Content = file.read().lower()
                    for comb in combinations:
                        if ":::" in comb:
                            split_idx = comb.index(":::")
                            cheatName = comb[:split_idx]
                            Cheat_String_Before = comb[split_idx + 3:].strip().lower()
                            Cheat_String_After = b'    '.join(Cheat_String_Before.encode('utf-8').split()) + b'    '
                            if Cheat_String_After in Content:
                                Detects.append(f"Generic {cheatName}")
                    del combinations
        except PermissionError:
            pass
        except Exception as e:
            print(traceback.format_exc())

        threads = {
            "thread8": thread8,
            "thread1": thread1,
            "thread8": thread8,
            "thread5": thread5,
            "thread10": thread10,
            "thread15": thread15,
            "thread20": thread20,
            "thread22": thread22,
            "thread23": thread23,
            "thread7": thread7,
            "thread9": thread9,
            "thread11": thread11,
            "thread13": thread13,
            "thread16": thread16,
            "thread17": thread17,
            "thread18": thread18,
            "thread21": thread21,
            "thread24": thread24,
            "thread26": thread26,
            "thread27": thread27,
            "thread28": thread28,
            "thread29": thread29,
            "thread31": thread31,
            "thread32": thread32,
            "thread33": thread33,
            "thread34": thread34,
            "thread35": thread35
        }

        for thread_name, thread in threads.items():
            try:
                if thread.is_alive():
                    thread.join()
            except Exception as e:
                print(traceback.format_exc())
        
        with open("Results.txt", "w") as file:
            file.write(f"VPN: {vpn}\n\n")
            file.write(f"System Install: {system}\n\n")
            file.write(f"Service Runtimes:\n")
            file.write(f"- Explorer: {explorer}\n")
            file.write(f"- DNSCache: {DNSCache_UPTime()}\n")
            file.write(f"- DPS: {DPS_UPTime()}\n")
            file.write(f"- Eventlog: {eventlog}\n")
            file.write(f"- FiveM: {fivem}\n")
            file.write(f"- Appinfo: {appinfos}\n\n")
            file.write(f"Detects:\n")
            for detect in Detects:
                file.write(str(detect) + "\n")
            
            file.write("\nWarnings:\n")
            for warning in Warnings:
                file.write(str(warning) + "\n")
            
            file.write("\nLogs:\n")
            for log in Logs:
                file.write(str(log) + "\n")

            file.write("\nPcaClient:\n")
            for pca in PcaClient:
                file.write(str(pca) + "\n")

            file.write("\nBam:\n")
            for bam in Bam:
                file.write(str(bam) + "\n")

            file.write("\nRecording:\n")
            for rec in Recording:
                file.write(str(rec) + "\n")

            file.write("\nSteam:\n")
            for steam in Steam:
                file.write(str(steam) + "\n")

            file.write("\nUSBLogs:\n")
            for usb in USBLogs:
                file.write(str(usb) + "\n")

            file.write("\nLastAV:\n")
            for av in LastAV:
                file.write(f"{av['Path']} - {av['Time']}\n")

            file.write("\nRecent:\n")
            for recent in Recent:
                file.write(recent + "\n")

        os.system('cls')
        print("Check 'Results.txt'")
        
        Remove_Files(CDirectory)
            
        Stop_Monitor = True

    except Exception as e:
        print(traceback.format_exc())

def Scanner_Auth():
    global Start_Time

    if not Local_PIN:
        print("Usage: [PIN]")
        time.sleep(5)
        psutil.Process(os.getpid()).terminate() 

    check_pin = 'https://example.com/api/validation/'
    Scanner_Agent = base64.b64decode(Memory().encode('utf-8')).decode('utf-8')
        
    headers = {
        'User-Agent': Scanner_Agent,
        'PIN': Local_PIN,
        'Security': "Success",
        'Game': "FiveM",
        'Authorization': Authorization()
    }
    r = requests.get(check_pin, headers=headers)
    del headers
    del check_pin
    del Scanner_Agent
    res = r.json()
    Status = res["Used"]
    Game = res["Game"]
    if Status == 0 and Game == "FiveM":
        try:
            global Stop_Monitor, thread1, thread3, thread5, thread8, thread7, thread9, thread10, thread11, thread13, thread15, thread16, thread17, thread18, thread20, thread21, thread22, thread23, thread24, thread26, thread27, thread28, thread29, thread31, thread32, thread33, thread34, thread35
            
            os.system("cls")

            Scanner_Agent = base64.b64decode(Memory().encode('utf-8')).decode('utf-8')

            headers2 = {
                'User-Agent': Scanner_Agent,
                "PIN": f"{Local_PIN}",
                "HWID1": f"{Token_}",
                "HWID2": f"{Token__}",
                "DCID": f"{Discord_ID()}"
            }

            Link = f"https://example.com/api/module/check"
            
            requests.post(Link, headers=headers2)
            
            del headers2
            del Link
            del Scanner_Agent

            Start_Time = time.time()
            C_Directory()

            arch = platform.architecture()[0]

            if arch == '32bit':
                Download_File("xxStrings-32.exe", f"{CDirectory}\\xxStrings.exe")
            elif arch == '64bit':
                Download_File("xxStrings-64.exe", f"{CDirectory}\\xxStrings.exe")
            else:
                pass

            Modules()
            Modules_Existing()

            thread1 = threading.Thread(target=Skript_Detection)
            thread2 = threading.Thread(target=USBChecker)
            thread3 = threading.Thread(target=JournalChecker)
            thread5 = threading.Thread(target=Generic_Detection)
            thread7 = threading.Thread(target=LsassChecker)
            thread8 = threading.Thread(target=File_Scanner_Global)
            thread9 = threading.Thread(target=VMCheck)
            thread10 = threading.Thread(target=DNSCacheChecker)
            thread11 = threading.Thread(target=PcaClientChecker)
            thread13 = threading.Thread(target=RegistryScan)
            thread15 = threading.Thread(target=LastActivityView)
            thread16 = threading.Thread(target=RecordingChecker)
            thread17 = threading.Thread(target=SteamChecker)
            thread18 = threading.Thread(target=FiveMChecker)
            thread20 = threading.Thread(target=ExplorerChecker)
            thread21 = threading.Thread(target=CrashDumpChecker)
            thread22 = threading.Thread(target=PcaSVChecker)
            thread23 = threading.Thread(target=DPSChecker)
            thread24 = threading.Thread(target=BypassAtCDirectoryt)
            thread26 = threading.Thread(target=CryptSVCChecker)
            thread27 = threading.Thread(target=TCPChecker)
            thread28 = threading.Thread(target=Eulen_Detection)
            thread29 = threading.Thread(target=DiagTrackChecker)
            thread31 = threading.Thread(target=SearchIndexerChecker)
            thread32 = threading.Thread(target=RecentChecker)
            thread33 = threading.Thread(target=TaskHostChecker)
            thread34 = threading.Thread(target=SIHostChecker)
            thread35 = threading.Thread(target=AMCacheChecker)

            thread1.start()
            thread2.start()
            thread3.start()
            thread5.start()
            thread7.start()
            thread15.start()
            thread16.start()

            FiveM_Location_M()
            
            
            thread8.start()
            thread9.start()
            thread10.start()
            thread11.start()
            thread13.start()
            thread17.start()
            thread18.start()
            thread20.start()
            thread21.start()
            thread22.start()
            thread23.start()
            thread24.start()
            thread26.start()
            thread27.start()
            thread28.start()
            thread29.start()
            thread31.start()
            thread32.start()
            thread33.start()
            thread34.start()
            thread35.start()

            Scanner()

            Stop_Monitor = True

            try:
                for root, dirs, files in os.walk(CDirectory):
                    for file in files:
                        if file in Files_2_Delete:
                            file_path = os.path.join(root, file)
                            os.remove(file_path)
            except Exception as e:
                print(traceback.format_exc())

        except Exception as e:
            print(traceback.format_exc())
    else:
        print('PIN Not Found!')
        Stop_Monitor = True

if not Stop_Monitor:
    Scanner_Auth()
    #cracked