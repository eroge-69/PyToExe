# # # # # # # # # # # # # # # # # # # # # # # #
# logo.txt  __.__              _________      #
#          |__|__| ____ ___  __\______  \     #
#          |  |  |/    \\  \/  /   /    /     #
#          |  |  |   |  \>    <   /    /      #
#      /\__|  |__|___|  /__/\_ \ /____/       #
#      \______|       \/      \/              #
#            CAETSPLOIT - JINX7               #
# # # # # # # # # # # # # # # # # # # # # # # #
# Credits.txt                                 #
# Caet, Ches, Cats, Prefer, Bug, Shown, Sang. #
# # # # # # # # # # # # # # # # # # # # # # # #
# Instructions.txt                            #
# Changing themes is easy. Click the Jinx or  #
# Google Drive icon and select the folder of  #
# the theme that you want. The picked theme   #
# will also be loaded every time you boot.    #
#                                             #
# To attach just join a game and then press   #
# the big A button. Enjoy!                    #
# # # # # # # # # # # # # # # # # # # # # # # #

# CAETSPLOIT JINX7. | Config
Click_Sound = r"Resources\Click.wav"
Wolfy_Sound = r"Resources\Howl.wav" # Wolfy_Sound = ".\Resources\Cleaver.wav" # 4 jayln LOL

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QFileDialog
from PyQt6.Qsci import *

import winsound, threading
import os
import glob

import pymem
import logging
import click
import ctypes

import threading
import pymem.ressources
import pymem.ressources.structure
import time
import subprocess

import socket

import re

import xml.etree.ElementTree as parseXml

from flask import Flask, request
from waitress import serve

import win32api
import windows.generated_def as generated_def
import windows.winproxy as winproxy

import json

mem = ctypes.WinDLL('api-ms-win-core-memory-l1-1-5', use_last_error=True)

if not os.path.exists("./Resources/Config.txt"): 
    with open("./Resources/Config.txt", 'w+') as File: 
        File.write("JINX7 Blue") 
    
with open("./Resources/Config.txt", 'r') as File:
    Current_Theme = File.read().strip()

try:
    open("./Resources/settings.json",'x')
except:
    None
settingsfile = open("./Resources/settings.json", 'r')
settings = {}
try:
    settings = json.loads(settingsfile.read())
except:
    None
settingsfile.close()
print(settings)
def GetOptionalSetting(name, fallback = None):
    if name in settings:
        return settings[name]
    return fallback

def GetThemeColor():
    with open('./Themes/' + Current_Theme + '/Config.txt') as File:
        data = File.read().split(":")[1].split(",")

    x,y,z = data[0], data[1], data[2].removeprefix(';')
    return int(x), int(y), int(z.removesuffix(";"))

def PlaySound(Path):
    threading.Thread(target=winsound.PlaySound, args=(None, winsound.SND_PURGE,), daemon=True).start()
    threading.Thread(target=winsound.PlaySound, args=(Path, winsound.SND_ASYNC,), daemon=True).start()

app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def secho(text, file=None, nl=None, err=None, color=None, **styles):
    pass

def echo(text, file=None, nl=None, err=None, color=None, **styles):
    pass

click.echo = echo
click.secho = secho

NameOffset = 0x80
ChildOffset = 0x60
ParentOffset = 0x50
LuaSourceContainerOffset = 0x150

Pattern = b"\x0c \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01"

global consoleoutput

global socketclient
socketclient = None
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 4444))
server.listen()
def getsocketclients():
    global socketclient
    while True:
        try:
            client,address = server.accept()
            socketclient = client
            #print("accepted client connection!")
            consoleoutput("jinx8 connected")
            """
            time.sleep(2)
            try:
                Inject()
            except:
                consoleoutput("jinx8 auto inject failed")
            """
        except:
            None
        time.sleep(1)

def getrecv():
    global socketclient
    while True:
        try:
            if socketclient:
                socketclient.recv()
        except:
            None
        time.sleep(1)

getclientsthr = threading.Thread(target=getsocketclients)
getclientsthr.daemon = True
getclientsthr.start()

# begin safe read funcs

def SafeVirtualUnlockEx(lpAddress, dwSize):
    result = mem.VirtualUnlockEx(Main.process_handle, ctypes.c_int64(lpAddress), dwSize)
    return result

def saferead_ulonglong(Address):
    returnvalue = Main.read_ulonglong(Address)
    SafeVirtualUnlockEx(Address,8)
    return returnvalue

def saferead_int(Address):
    returnvalue = Main.read_int(Address)
    SafeVirtualUnlockEx(Address,4)
    return returnvalue

def saferead_string(Address,length):
    returnvalue = Main.read_string(Address,length)
    SafeVirtualUnlockEx(Address,length)
    return returnvalue

def saferead_bytes(Address,length):
    returnvalue = Main.read_bytes(Address, length)
    SafeVirtualUnlockEx(Address,length)
    return returnvalue

def safewrite_bytes(Address,value,length):
    Main.write_bytes(Address, value, length)
    SafeVirtualUnlockEx(Address,length)

def safewrite_ulonglong(Address,value):
    Main.write_ulonglong(Address, value)
    SafeVirtualUnlockEx(Address,8)

def safewrite_int(Address,value):
    Main.write_int(Address, value)
    SafeVirtualUnlockEx(Address,4)

def safewrite_long(Address,value):
    Main.write_long(Address, value)
    SafeVirtualUnlockEx(Address,4)

# end

def ReadString(Address):
    Length = saferead_int(Address + 0x10) #16 away because max c++ string size is 16 LOL
    
    if Length > 0:
        if Length < 16:
            return saferead_string(Address, Length)
        else:
            return saferead_string(saferead_ulonglong(Address), Length) #they store it somewhere else

def ReadName(instance):
    return ReadString(saferead_ulonglong(instance + NameOffset))
    
def GetParent(Address):
    return saferead_ulonglong(Address + ParentOffset)

def GetChildren(Address):
    try:
        CListPointer = saferead_ulonglong(Address + ChildOffset)
        ListStart = saferead_ulonglong(CListPointer)
        ListEnd = saferead_ulonglong(CListPointer + 8)
    except:
        return {}

    if (ListStart == 0 or ListEnd == 0) or (ListEnd == ListStart):
        return {}
    
    ChildList = {}

    for i in range(ListStart, ListEnd, 16):
        try:
            InstanceAddress = saferead_ulonglong(i)
            ChildInstance = InstanceAddress
            Name = ReadString(saferead_ulonglong(ChildInstance + NameOffset))
            ChildList[Name] = ChildInstance
        except:
            pass

    return ChildList

def LuaCompile(Code, Chunkname):
    with open("./Resources/Source.txt", "w+", encoding = "utf-8") as SourceFile:
        SourceFile.write(Code)

    with open("./Resources/Output.txt", "wb") as File:
        Proc = subprocess.Popen(["./luau.exe", "--compile=binary", "./Resources/Source.txt", "-O2"], stdout = File, stderr = File, creationflags=subprocess.CREATE_NO_WINDOW)
        Proc.wait()


def GetClassName(Address):
    classdesc = saferead_ulonglong(Address + 0x18)
    return ReadString(saferead_ulonglong(classdesc + 0x8)), classdesc

THREAD_ALL_ACCESS = 0x1F03FF
CONTEXT_FULL = 0x10007

TH32CS_SNAPTHREAD = 0x00000004
INVALID_HANDLE_VALUE = ctypes.wintypes.HANDLE(-1)
ERROR_NO_MORE_FILES = 0x12


class THREADENTRY32(ctypes.Structure):
    _fields_ = (
        ("dwSize", ctypes.wintypes.DWORD),
        ("cntUsage", ctypes.wintypes.DWORD),
        ("th32ThreadID", ctypes.wintypes.DWORD),
        ("th32OwnerProcessID", ctypes.wintypes.DWORD),
        ("tpBasePri", ctypes.wintypes.LONG),
        ("tpDeltaPri", ctypes.wintypes.LONG),
        ("dwFlags", ctypes.wintypes.DWORD)
    )

LPTHREADENTRY32 = ctypes.POINTER(THREADENTRY32)


kernel32 = ctypes.windll.kernel32

CreateToolhelp32Snapshot = kernel32.CreateToolhelp32Snapshot
CreateToolhelp32Snapshot.argtypes = (ctypes.wintypes.DWORD, ctypes.wintypes.DWORD)
CreateToolhelp32Snapshot.restype = ctypes.wintypes.HANDLE

Thread32First = kernel32.Thread32First
Thread32First.argtypes = (ctypes.wintypes.HANDLE, LPTHREADENTRY32)
Thread32First.restype = ctypes.wintypes.BOOL

Thread32Next = kernel32.Thread32Next
Thread32Next.argtypes = (ctypes.wintypes.HANDLE, LPTHREADENTRY32)
Thread32Next.restype = ctypes.wintypes.BOOL

CloseHandle = kernel32.CloseHandle
CloseHandle.argtypes = (ctypes.wintypes.HANDLE,)
CloseHandle.restype = ctypes.wintypes.BOOL

GetLastError = kernel32.GetLastError
GetLastError.argtypes = ()
GetLastError.restype = ctypes.wintypes.DWORD

def get_threads(pid):
    threads = []
    flags = TH32CS_SNAPTHREAD
    snap = CreateToolhelp32Snapshot(flags, 0)
    if snap == INVALID_HANDLE_VALUE:
        print(f"CreateToolhelp32Snapshot failed: {GetLastError()}")
        return -1
    entry = THREADENTRY32()
    size = ctypes.sizeof(THREADENTRY32)
    entry.dwSize = size
    res = Thread32First(snap, ctypes.byref(entry))
    idx = 0
    while res:
        if entry.th32OwnerProcessID == pid:
            threads.append(entry.th32ThreadID)
        idx += 1
        res = Thread32Next(snap, ctypes.byref(entry))
    gle = GetLastError()
    if gle != ERROR_NO_MORE_FILES:
        print(f"Error: {gle}")
    CloseHandle(snap)
    return threads

Main = None


def getdatamodel(in_game: bool):
    dmoffset = GetOptionalSetting("datamodeloffset1", 0xe8)
    threads = get_threads(Main.process_id)
    for thread_id in threads:
        thread_handle = winproxy.OpenThread(THREAD_ALL_ACCESS, False, thread_id)
        if not thread_handle:
            continue

        context = generated_def.CONTEXT()
        context.ContextFlags = CONTEXT_FULL

        if not winproxy.GetThreadContext(thread_handle, context):
            win32api.CloseHandle(thread_handle)
            continue

        contexts = [
            #context.Rbp,
            #context.Rcx,
            #context.Rax,
            #context.Rdx,
            #context.Rbx,
            #context.Rsp,
            #context.Rsi,
            #context.Rdi,
            #context.R8,
            #context.R9,
            #context.R10,
            context.R11,
            context.R12,
            context.R13,
            context.R14,
            context.R15,
            #context.Rip
        ]
        for ctx in contexts:
            try:
                #print(hex(ctx))
                #mcp = saferead_ulonglong(saferead_ulonglong(ctx + 0x48) + 0xB0)
                service = saferead_ulonglong(saferead_ulonglong(ctx + 0x0) + dmoffset) #0x108
                #classnam, _ = GetClassName(service)
                pname = ReadName(GetParent(service))
                if pname == "Ugc" and in_game:
                    return GetParent(service)
                if pname == "LuaApp" and not in_game:
                    return GetParent(service)
            except:
                None
            #dm = checkdatamodel(ctx)

        win32api.CloseHandle(thread_handle)
    return None

DataModel = None
NameList = ["Animate"]

ExecuteQueue = []

RobloxPath = ""

ct = pymem.ressources.ctypes

ntdll = ct.WinDLL("ntdll.dll")

def scan_pattern_page(handle, address, pattern, *, return_multiple=False):
    mbi = pymem.memory.virtual_query(handle, address)
    next_region = mbi.BaseAddress + mbi.RegionSize
    allowed_protections = [
        pymem.ressources.structure.MEMORY_PROTECTION.PAGE_EXECUTE,
        pymem.ressources.structure.MEMORY_PROTECTION.PAGE_EXECUTE_READ,
        pymem.ressources.structure.MEMORY_PROTECTION.PAGE_EXECUTE_READWRITE,
        pymem.ressources.structure.MEMORY_PROTECTION.PAGE_READWRITE,
        pymem.ressources.structure.MEMORY_PROTECTION.PAGE_READONLY,
    ]
    if mbi.state != pymem.ressources.structure.MEMORY_STATE.MEM_COMMIT or mbi.protect not in allowed_protections:
        return next_region, None

    page_bytes = pymem.memory.read_bytes(handle, address, mbi.RegionSize)
    SafeVirtualUnlockEx(address,mbi.RegionSize)

    if not return_multiple:
        found = None
        match = re.search(pattern, page_bytes, re.DOTALL)

        if match:
            found = address + match.span()[0]

    else:
        found = []

        for match in re.finditer(pattern, page_bytes, re.DOTALL):
            found_address = address + match.span()[0]
            found.append(found_address)

    return next_region, found

def pattern_scan_all(handle, pattern, *, return_multiple=False):
    next_region = 0

    found = []
    user_space_limit = 0x7FFFFFFF0000 if sys.maxsize > 2**32 else 0x7fff0000

    #ntdll.NtSuspendProcess(handle)
    StartTime = time.time()

    while next_region < user_space_limit:
        next_region, page_found = scan_pattern_page(
            handle,
            next_region,
            pattern,
            return_multiple=return_multiple
        )

        #what???
        '''
        if time.time() - StartTime >= 3:
            #ntdll.NtResumeProcess(handle)
            time.sleep(7)
            #ntdll.NtSuspendProcess(handle)
            StartTime = time.time()'''

        if not return_multiple and page_found:
            return page_found

        if page_found:
            found += page_found

    if not return_multiple:
        return None

    #ntdll.NtResumeProcess(handle)

    return found

def scan_script(handle, pattern, *, return_multiple=False):
    page_found = pattern_scan_all(
        handle,
        pattern,
        return_multiple=return_multiple
    )
    if not return_multiple and page_found:
        return page_found

    if page_found:
        for Address in page_found:
            try:
                NameAddress = saferead_ulonglong(Address - 0x20)
                Name = ReadString(NameAddress)

                if Name in NameList:
                    BaseScript = Address - 0x20 - NameOffset
                    return BaseScript

            except Exception as e:
                pass

    if not return_multiple:
        return None

    return None

def Inject(): 
    global Main
    global DataModel
    start = time.time()
    try:
        Main = pymem.Pymem("RobloxPlayerBeta.exe")
    except:
        QtWidgets.QMessageBox.critical(
            JINX7, 
            "Roblox was not found", 
            "what are you doing"
        )

        raise Exception("lol")
    
    ExecuteQueue.clear()

    DataModel = None
    while not DataModel:
        try:
            DataModel = getdatamodel(True)
            time.sleep(.001)
        except:
            None
    print("got datamodel")
    def GetDescendantOfClass(inst,name):
        tosearch = [inst]
        while len(tosearch) > 0:
            for searchinst in tosearch:
                tosearch.remove(searchinst)
                try:
                    children = GetChildren(searchinst)
                    for child in children:
                        classnam, classdesc = GetClassName(children[child])
                        if classnam == name:
                            print(classnam)
                            return children[child], classdesc
                        else:
                            tosearch.append(children[child])
                except:
                    None, None

    def GetFromPath(inst, path):
        descendants = path.split(".")
        lastdescendant = inst
        for i in descendants:
            lastdescendantchildren = GetChildren(lastdescendant)
            if i in lastdescendantchildren:
                lastdescendant = lastdescendantchildren[i]
            else:
                return None
        return lastdescendant

    global TargetScript
    TargetScript = None
    #TargetScript = GetFromPath(DataModel, "CorePackages.Packages._Index.UIBlox.UIBlox.App.Grid.GridView")
    while not TargetScript:
        TargetScript = GetFromPath(DataModel, "CorePackages.Workspace.Packages._Workspace.ScreenTime.ScreenTime.Constants")

    safewrite_ulonglong(TargetScript + 0x1B0, 1)
    print(hex(TargetScript))
    """
    try:
        CorePackages = GetChildren(GetParent(DataModel))["CorePackages"]
    except:
        CorePackages = GetChildren(DataModel)["CorePackages"]
    AppTempCommon = GetChildren(CorePackages)["AppTempCommon"]
    LuaApp = GetChildren(AppTempCommon)["LuaApp"]
    Actions = GetChildren(LuaApp)["Actions"]
    global TargetScript
    TargetScript = GetChildren(Actions)["SetDeviceOrientation"]
    print(hex(TargetScript))"""

    """
    try:
        CoreGui = GetChildren(GetParent(DataModel))["CoreGui"]
    except:
        CoreGui = GetChildren(DataModel)["CoreGui"]
    RobloxGui = GetChildren(CoreGui)["RobloxGui"]
    Modules = GetChildren(RobloxGui)["Modules"]
    Settings = GetChildren(Modules)["Settings"]
    Pages = GetChildren(Settings)["Pages"]
    ShareGame = GetChildren(Pages)["ShareGame"]
    Reducers = GetChildren(ShareGame)["Reducers"]
    global TargetScript
    TargetScript = GetChildren(Reducers)["DeviceInfo"]
    """

    #CoreGui = GetChildren(DataModel)["CoreGui"]
    #RobloxGui = GetChildren(CoreGui)["RobloxGui"]
    #Modules = GetChildren(RobloxGui)["Modules"]
    #PlayerList = GetChildren(Modules)["PlayerList"]
    #DummyScript = GetChildren(PlayerList)["PlayerListManager"]
    #DumpTargetScript = GetChildren(Modules)["Feedback"]
    #ScriptContext = GetChildren(Game)["Script Context"]
    #GuiChildren = GetChildren(RobloxGui)

    #Settings = GuiChildren["SettingsClippingShield"]
    #Frame = GuiChildren["ToastsFrame"]
    #TargetScript = GetChildren(Modules)["Feedback"]

    #safewrite_ulonglong(DummyScript + 0x8, TargetScript)
    #temp write so it fucks with the toastframe instead of settings
    #ReadBuffer = Main.read_bytes(Settings, 0x200)
    #ReadFrame = Main.read_bytes(Frame, 0x200)

    #Main.write_bytes(Settings, ReadFrame, len(ReadFrame))

    BytecodeFile = open("./Resources/precompiled.txt", "rb")
    Bytecode = BytecodeFile.read()
    BytecodeFile.close()
    AllocatedBase = Main.allocate(len(Bytecode))
    safewrite_bytes(AllocatedBase, Bytecode, len(Bytecode))
    LuaSourceContainer = saferead_ulonglong(TargetScript + LuaSourceContainerOffset)
    
    safewrite_ulonglong(
        LuaSourceContainer + 16,
        AllocatedBase
    )
    safewrite_int(
        LuaSourceContainer + 16 + 16,
        len(Bytecode)
    )

    safewrite_bytes(LuaSourceContainer, b'\xe0\xfb\xd7\x88\xaa7\x99-K\xfb|\xc6\x12B"&', 16)

    consoleoutput(f"Injected in {round(time.time()-start, 2)} seconds")
    try:
        def SetScriptable(ClassDescriptor,Props):
            top = saferead_ulonglong(ClassDescriptor + 0x9c0)
            end = saferead_ulonglong(ClassDescriptor + 0x9c0 + 0x8)
            for address in range(top, end, 0x8):
                Descriptor = saferead_ulonglong(address)
                Name = ReadString(saferead_ulonglong(Descriptor + 0x8))
                print(Name)
                if Name in Props:
                    consoleoutput(f"Set {Name} scriptable")
                    safewrite_ulonglong(Descriptor + 0x50, 63)

        Workspace = GetChildren(DataModel)['Workspace']
        Hat, HatClassDesc = GetDescendantOfClass(Workspace, "Accessory")
        Part, PartClassDesc = GetDescendantOfClass(Workspace, "Part")
        SetScriptable(HatClassDesc,["BackendAccoutrementState"])
        print("Hi")
        SetScriptable(PartClassDesc,["NetworkIsSleeping"])
        print("Hi")
        Part, PartClassDesc = GetDescendantOfClass(Workspace, "Motor6D")
        SetScriptable(PartClassDesc,["ReplicateCurrentAngle6D", "ReplicateCurrentOffset6D"])
    except:
        None

    Main.close_process()

ExecutionLimit = 1

@app.route("/", methods = ["GET"])
def ReturnBytecode():
    BytecodeString = b""

    for i in range(ExecutionLimit):
        if len(ExecuteQueue) <= 0:
            break

        Bytecode = ExecuteQueue.pop(0)
        Length = len(Bytecode).to_bytes(4, "little")

        BytecodeString += Length + Bytecode

    return BytecodeString

@app.route("/autoexec", methods = ["GET"])
def RunAutoExec():
    print('received')
    AutoExecFiles = glob.glob("./AutoExecute/*.lua") + ["./Resources/uncfunc.txt"]

    for Path in AutoExecFiles:
        with open(Path, "r", encoding='utf-8') as File:
            Code = File.read()

            try:
                LuaCompile(Code, "Caetlery")
            except:
                LuaCompile('warn("Compile failed!")', "Caetlery")

            with open("./Resources/Output.txt", "rb") as File:
                Bytecode = File.read()

            ExecuteQueue.append(Bytecode)
    return "ran autoexec"

@app.route("/funccall", methods = ["POST"])
def FunctionHandler():
    Data = request.get_json()

    if not Data["name"] in CustomFunctions:
        return ""

    Function = CustomFunctions[Data["name"]]
    Arguments = Data["args"]

    try:
        Return = Function(Arguments)
        return Return
    except:
        return ""

def loadstring(args):
    code = args[0]
    chunkname = args[1] if len(args) > 1 else "Caetlery"
    
    try:
        LuaCompile(code, chunkname)
    except:
        LuaCompile('warn("Compile failed!")', chunkname)

    with open("./Resources/output.txt", "rb") as file:
        bytecode = file.read()
        return bytecode
    
def readfile(args):
    path = args[0]
    with open(f"./Workspace/{path}", "r+") as file:
        return file.read()

def writefile(args):
    path = args[0]
    data = args[1]

    with open(f"./Workspace/{path}", "w+") as file:
        file.write(data)
        return ""
    
def appendfile(args):
    path = args[0]
    data = args[1]

    with open(f"./Workspace/{path}", "a+") as file:
        file.write(data)
        return ""
    
def isfile(args):
    path = args[0]

    return "1" if os.path.isfile(f"./Workspace/{path}") else "0"

def isfolder(args):
    path = args[0]

    return "1" if os.path.isdir(f"./Workspace/{path}") else "0"

def listfiles(args):
    path = args[0]
    paths = [os.path.basename(i) for i in glob.glob(f"./Workspace/{path}/*")]

    return paths

def makefolder(args):
    path = args[0]
    os.mkdir(f"./Workspace/{path}")
    return ""

def getcustomasset(args):
    path = args[0]
    return "IM TOO LAZY TO MAKE GETCUSTOMASSET RN" #goodness gracious someone save me vro

def replicatesignal(args):
    global socketclient
    payload = args[0]
    if socketclient != None:
        try:
            socketclient.send(payload.encode())
            return "1"
        except:
            print("failed to send payload :(")
            return "0"
    else:
        print("couldnt find socket client :(")
        return "0"
    
def desync(args):
    global socketclient
    if socketclient != None:
        try:
            socketclient.send(b'desync')
            return "1"
        except:
            print("failed to send desync :(")
            return "0"
    else:
        print("couldnt find socket client :(")
        return "0"
    
def jinx8init(args):
    if socketclient != None:
        try:
            socketclient.send(("0").encode())
            consoleoutput("sent in game jinx8 init")
        except:
            print("failed to send jinx8 init")
    else:
        print("couldnt find socket client for jinx 8 init :(")

    global Main
    Main = pymem.Pymem("RobloxPlayerBeta.exe")
    data_model = getdatamodel(True)
    
    Wrote = False
    while not Wrote:
        scriptcontext = GetChildren(data_model)["Script Context"]

        capabilitiesmap = saferead_ulonglong(scriptcontext + GetOptionalSetting("identityoffset", 0x838)) #0x840)
        corescriptcapabilitiescap = saferead_ulonglong(capabilitiesmap) + 0x18
        safewrite_ulonglong(corescriptcapabilitiescap, 0xFFFFFFFFFFFFFFFF)

        coreguilist = saferead_ulonglong(scriptcontext + GetOptionalSetting("identityoffset2", 0x478))#+ 0x480)
        coreguimodules = saferead_ulonglong(coreguilist + 0x8)
        moduleinstances = saferead_ulonglong(coreguimodules + 0x78)

        LuaState = saferead_ulonglong(moduleinstances + 0x10)
        for i in range(5000):
            try:
                module = saferead_ulonglong(LuaState + 0x50)
                modulename = ReadName(module)
                parentname = ReadName(GetParent(module))
                if modulename == "Constants" and parentname == "ScreenTime":
                    print("found screen time constants")
                    Wrote = True
                    safewrite_int(LuaState + 0x30, 8)
                    #print(hex(saferead_ulonglong(LuaState + 0x48)))
                    safewrite_ulonglong(LuaState + 0x48, 0xFFFFFFFFFFFFFFFF) #0x200000000000003F | 0xfffffff00)
                LuaState = saferead_ulonglong(LuaState + 0x10)
            except:
                break
        time.sleep(.1)
    Main.close_process()
    return "1"


CustomFunctions = {
    "loadstring" : loadstring,
    "readfile" : readfile,
    "writefile" : writefile,
    "appendfile" : appendfile,
    "listfiles" : listfiles,
    "isfile" : isfile,
    "isfolder" : isfolder,
    "makefolder" : makefolder,
    "getcustomasset" : getcustomasset,
    "replicatesignal" : replicatesignal, #whoop whoop
    "desync" : desync,
    "jinx8init" : jinx8init,
}

class Ui_JINX7(object):
    def ClearFunc(self):
        self.Code.clear()

    def ExecuteGeneral(self, Code):
        try:
            LuaCompile(Code, "Caetlery")
        except Exception as e:
            print(e)
            LuaCompile('warn("Compile failed!")', "Caetlery")

        with open("./Resources/Output.txt", "rb") as File:
            Bytecode = File.read()

        ExecuteQueue.append(Bytecode)

    def ExecuteFunc(self):
        Code = self.Code.text()
        try:
            self.ExecuteGeneral(Code)
        except:
            pass
        # CAET > Execute

    def OpenFunc(self):
        Dialog = QFileDialog()
        Dialog.setDirectory(f"{os.getcwd()}/Scripts")
        Dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        Dialog.setNameFilter("Any files (*.*);;Lua files (*.lua);;Text files (*.txt)")
        if Dialog.exec():
            Paths = Dialog.selectedFiles()
            if Paths:
                Path = Paths[0]
                try:
                    with open(Path, 'r', encoding='utf-8') as File:
                        self.Code.setText(File.read())
                except UnicodeDecodeError:
                    with open(Path, 'r', encoding='latin-1') as File:
                        self.Code.setText(File.read())

    def SaveFunc(self):
        PlaySound(Click_Sound)
        Dialog = QFileDialog()
        Dialog.setDirectory("./Scripts")
        Dialog.setWindowTitle("Save")
        Dialog.setDefaultSuffix("lua")
        Dialog.setNameFilter("Lua files (*.lua)")
        Path, _ = Dialog.getSaveFileName(filter="Lua files (*.lua)")
        if Path:
            if not Path.endswith(".lua"):
                Path += ".lua"
            with open(Path, 'w', encoding='utf-8') as File:
                File.write(self.Code.text().replace('\r\n', '\n'))
        
    def WordWrapFunc(self):
        PlaySound(Click_Sound)
        if self.Code.wrapMode() == QsciScintilla.WrapMode.WrapNone:
            self.Code.setWrapMode(QsciScintilla.WrapMode.WrapWord)
        else:
            self.Code.setWrapMode(QsciScintilla.WrapMode.WrapNone)
        
    def AttachFunc(self):
        #global EnvironmentBlock

        PlaySound(Click_Sound)
        try:
            Inject()
            #EnvironmentBlock = ct.c_buffer(0x7FFFFFF)
        except Exception as e:
            #print(e)
            consoleoutput("Jinx7 failed to inject ...")
            try:
                ProcHandle = Main.process_handle
                #ntdll.RtlDestroyEnvironment(EnvironmentBlock)
                #ntdll.NtResumeProcess(ProcHandle)
                #EnvironmentBlock = ct.c_buffer(0x7FFFFFF)
                Main.close_process()
            except:
                pass
        # CAET > Attach
        
    def GoogleDriveFunc(self):
        PlaySound(Click_Sound)
        Dialog = QFileDialog.getExistingDirectory(self, 'Select Folder', './Themes')

        if Dialog:
            Current_Theme = Dialog.split('/')[-1]
        else:
            return
        
        def GetNewThemeColor():
            with open('Themes/' + Current_Theme + '/Config.txt') as file:
                t = file.read()

            data = t.split(":")[1].split(",")
            x,y,z = data[0], data[1], data[2].removeprefix(';')
            return int(x), int(y), int(z.removesuffix(";"))
        self.Window.setStyleSheet("background-image: url(Themes/" + Current_Theme +"/MainUi.bmp);")
        def ChangeSButtons(Button):
            Button.setStyleSheet("""
                QPushButton {
                    background-image: url(Themes/""" + Current_Theme + """/S_Button_Idle.bmp);
                    border: none;
                    color: rgb""" + str(GetNewThemeColor()) + """;
                }
                QPushButton:hover {
                    background-image: url(Themes/""" + Current_Theme + """/S_Button_Hover.bmp);
                }
                QPushButton:pressed {
                    background-image: url(Themes/""" + Current_Theme + """/S_Button_Clicked.bmp);
                }
            """)
        ChangeSButtons(self.Clear)
        ChangeSButtons(self.Execute)
        ChangeSButtons(self.Open)
        def ChangeInButton(Button, Tag):
            Button.setStyleSheet("""
                QPushButton {
                    background-image: url(transparent);
                    border: none;
                }
                QPushButton:pressed {
                    background-image: url(Themes/""" + Current_Theme + """/""" + Tag + """.bmp);
                }
        """)
        ChangeInButton(self.Save, "Save_In")
        ChangeInButton(self.Word_Wrap, "WordWrap_In")
        ChangeInButton(self.Attach, "Auto_In")
        ChangeInButton(self.Google_Drive, "Google_Drive_In")
        ChangeInButton(self.Krystal, "Krystal_In")
        ChangeInButton(self.Wolfy, "Wofly_In")
        if not os.path.exists("Resources/Config.txt"): 
            with open("Resources/Config.txt", 'w+') as file: 
                file.write(Current_Theme) 
        else: 
            with open("Resources/Config.txt", 'w') as file: 
                file.write(Current_Theme) 
        
    def KrystalFunc(self):
        PlaySound(Click_Sound)

        with open("./Resources/Infinite-Yield.lua", "r") as File:
            Code = File.read()
            try:
                self.ExecuteGeneral(Code)
            except:
                pass
        # CAET > Execute IY (./Resources/Infinite-Yield.lua)
        
    def WolfyFunc(self):
        PlaySound(Wolfy_Sound)

        with open("./Resources/Dex-V2.lua", "r") as File:
            Code = File.read()
            try:
                self.ExecuteGeneral(Code)
            except:
                pass

        # CAET > Execute Dex (./Resources/Dex-V2.lua)

    def setupUi(self, JINX7):
        JINX7.setObjectName("JINX7")
        JINX7.resize(339, 327)
        JINX7.setMinimumSize(QtCore.QSize(339, 327))
        JINX7.setMaximumSize(QtCore.QSize(339, 327))
        icon = QtGui.QIcon()
        #icon.addPixmap(QtGui.QPixmap(".\\Resources/ICO/JINX7-ICO.ico"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        icon.addPixmap(QtGui.QPixmap(".\\Resources/ARTWORK/JINX7-LOGO.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        JINX7.setWindowIcon(icon)
        font = QtGui.QFont('MS Shell Dlg 2', 10)
        font.setBold(True)

        self.Window = QtWidgets.QWidget(parent=JINX7)
        self.Window.setEnabled(True)
        self.Window.setStyleSheet("background-image: url(Themes/" + Current_Theme +"/MainUi.bmp);")
        self.Window.setObjectName("Window")

        self.Code = QsciScintilla(parent = self.Window) #QtWidgets.QTextEdit(parent=self.Window)
        self.Code.setIndentationsUseTabs(True)

        Lexer = QsciLexerLua()
        for i in range(21):
            QsciLexerLua.setFont(Lexer, QtGui.QFont("Courier New", 10), i)

        #Loading in npp themes
        Tree = parseXml.parse("./Resources/Theme.xml")
        Root = Tree.getroot()

        for LexerType in Root[0]:
            Name = LexerType.get("name")
            if Name != "lua":
                continue

            for WordStyle in LexerType:
                Style = int(WordStyle.get("styleID"))
                FGColor = QtGui.QColor("#" + WordStyle.get("fgColor"))
                BGColor = QtGui.QColor("#" + WordStyle.get("bgColor"))

                QsciLexerLua.setColor(Lexer, FGColor, Style)
                QsciLexerLua.setPaper(Lexer, BGColor, Style)

        self.Code.setLexer(Lexer)
        QsciScintilla.setMarginLineNumbers(self.Code, 0, True)
        QsciScintilla.setAutoIndent(self.Code, True)
        QsciScintilla.setMarginWidth(self.Code, 0, "000")
        QsciScintilla.setMarginWidth(self.Code, 1, 5)
        QsciScintilla.setCaretLineVisible(self.Code, False)
        QsciScintilla.setIndentationGuides(self.Code, True)
        QsciScintilla.setIndentationsUseTabs(self.Code, True)
        QsciScintilla.setTabIndents(self.Code, True)
        QsciScintilla.setTabWidth(self.Code, 4)
        QsciScintilla.setMarginsFont(self.Code, QtGui.QFont("Courier New", 9))

        self.Code.setGeometry(QtCore.QRect(11, 11, 287, 233))
        self.Code.setStyleSheet("background-image: url(none); border: none;")
        self.Code.setObjectName("Code")
        self.Clear = QtWidgets.QPushButton(parent=self.Window)
        self.Clear.setGeometry(QtCore.QRect(11, 245, 95, 25))
        self.Clear.setFont(font)


        self.Clear.setStyleSheet("""
            QPushButton {
                background-image: url(Themes/""" + Current_Theme + """/S_Button_Idle.bmp);
                border: none;
                color: rgb""" + str(GetThemeColor()) + """;
            }
            QPushButton:hover {
                background-image: url(Themes/""" + Current_Theme + """/S_Button_Hover.bmp);
            }
            QPushButton:pressed {
                background-image: url(Themes/""" + Current_Theme + """/S_Button_Clicked.bmp);
            }
        """)
        self.Clear.setObjectName("Clear")
        self.Clear.clicked.connect(self.ClearFunc)

        self.Execute = QtWidgets.QPushButton(parent=self.Window)
        self.Execute.setGeometry(QtCore.QRect(107, 245, 95, 25))
        self.Execute.setFont(font)
        self.Execute.setStyleSheet("""
            QPushButton {
                background-image: url(Themes/""" + Current_Theme + """/S_Button_Idle.bmp);
                border: none;
                color: rgb""" + str(GetThemeColor()) + """;
            }
            QPushButton:hover {
                background-image: url(Themes/""" + Current_Theme + """/S_Button_Hover.bmp);
            }
            QPushButton:pressed {
                background-image: url(Themes/""" + Current_Theme + """/S_Button_Clicked.bmp);
            }
        """)
        self.Execute.setObjectName("Execute")
        self.Execute.clicked.connect(self.ExecuteFunc)

        self.Open = QtWidgets.QPushButton(parent=self.Window)
        self.Open.setGeometry(QtCore.QRect(203, 245, 95, 25))
        self.Open.setFont(font)
        self.Open.setStyleSheet("""
            QPushButton {
                background-image: url(Themes/""" + Current_Theme + """/S_Button_Idle.bmp);
                border: none;
                color: rgb""" + str(GetThemeColor()) + """;
            }
            QPushButton:hover {
                background-image: url(Themes/""" + Current_Theme + """/S_Button_Hover.bmp);
            }
            QPushButton:pressed {
                background-image: url(Themes/""" + Current_Theme + """/S_Button_Clicked.bmp);
            }
        """)
        self.Open.setObjectName("Open")
        self.Open.clicked.connect(self.OpenFunc)

        self.Console = QtWidgets.QScrollArea(parent=self.Window)
        self.Console.setGeometry(QtCore.QRect(11, 271, 287, 53))
        self.Console.setStyleSheet("background-image: url(Resources/Scroll2.png); border: none;")
        #self.Console.setWidgetResizable(True)
        self.Console.setObjectName("Console")
        self.Contents = QtWidgets.QTextEdit()
        self.Contents.setGeometry(QtCore.QRect(0, 0, 285, 51))
        self.Contents.setReadOnly(True)
        global consoleoutput
        def consoleoutput(text):
            self.Contents.append(text)
        self.Contents.setObjectName("Contents")
        self.Console.setWidget(self.Contents)


        self.Save = QtWidgets.QPushButton(parent=self.Window)
        self.Save.setGeometry(QtCore.QRect(304, 108, 30, 30))
        self.Save.setStyleSheet("""
            QPushButton {
                background-image: url(transparent);
                border: none;
            }
            QPushButton:pressed {
                background-image: url(Themes/""" + Current_Theme + """/Save_In.bmp);
            }
        """)
        self.Save.setText("")
        self.Save.setObjectName("Save")
        self.Save.clicked.connect(self.SaveFunc)

        self.Word_Wrap = QtWidgets.QPushButton(parent=self.Window)
        self.Word_Wrap.setGeometry(QtCore.QRect(304, 145, 30, 30))
        self.Word_Wrap.setStyleSheet("""
            QPushButton {
                background-image: url(transparent);
                border: none;
            }
            QPushButton:pressed {
                background-image: url(Themes/""" + Current_Theme + """/WordWrap_In.bmp);
            }
        """)
        self.Word_Wrap.setText("")
        self.Word_Wrap.setObjectName("Word_Wrap")
        self.Word_Wrap.clicked.connect(self.WordWrapFunc)

        self.Attach = QtWidgets.QPushButton(parent=self.Window)
        self.Attach.setGeometry(QtCore.QRect(304, 182, 30, 30))
        self.Attach.setAutoFillBackground(False)
        self.Attach.setStyleSheet("""
            QPushButton {
                background-image: url(transparent);
                border: none;
            }
            QPushButton:pressed {
                background-image: url(Themes/""" + Current_Theme + """/Auto_In.bmp);
            }
        """)
        self.Attach.setText("")
        self.Attach.setObjectName("Attach")
        self.Attach.clicked.connect(self.AttachFunc)

        self.Google_Drive = QtWidgets.QPushButton(parent=self.Window)
        self.Google_Drive.setGeometry(QtCore.QRect(304, 219, 30, 30))
        self.Google_Drive.setStyleSheet("""
            QPushButton {
                background-image: url(transparent);
                border: none;
            }
            QPushButton:pressed {
                background-image: url(Themes/""" + Current_Theme + """/Google_Drive_In.bmp);
            }
        """)

        
        self.Google_Drive.setText("")
        self.Google_Drive.setObjectName("Google_Drive")
        self.Google_Drive.clicked.connect(self.GoogleDriveFunc)

        self.Krystal = QtWidgets.QPushButton(parent=self.Window)
        self.Krystal.setGeometry(QtCore.QRect(304, 256, 30, 30))
        self.Krystal.setStyleSheet("""
            QPushButton {
                background-image: url(transparent);
                border: none;
            }
            QPushButton:pressed {
                background-image: url(Themes/""" + Current_Theme + """/Krystal_In.bmp);
            }
        """)
        self.Krystal.setText("")
        self.Krystal.setObjectName("Krystal")
        self.Krystal.clicked.connect(self.KrystalFunc)

        self.Wolfy = QtWidgets.QPushButton(parent=self.Window)
        self.Wolfy.setGeometry(QtCore.QRect(304, 293, 30, 30))
        self.Wolfy.setStyleSheet("""
            QPushButton {
                background-image: url(transparent);
                border: none;
            }
            QPushButton:pressed {
                background-image: url(Themes/""" + Current_Theme + """/Wofly_In.bmp);
            }
        """)
        self.Wolfy.setText("")
        self.Wolfy.setObjectName("Wolfy")
        self.Wolfy.clicked.connect(self.WolfyFunc)

        JINX7.setCentralWidget(self.Window)
        self.retranslateUi(JINX7)
        QtCore.QMetaObject.connectSlotsByName(JINX7)

    def retranslateUi(self, JINX7):
        _translate = QtCore.QCoreApplication.translate
        JINX7.setWindowTitle(_translate("JINX7", "JINX7"))
        self.Clear.setText(_translate("JINX7", "Clear"))
        self.Execute.setText(_translate("JINX7", "Execute"))
        self.Open.setText(_translate("JINX7", "Open"))

class Window(QtWidgets.QMainWindow, Ui_JINX7):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint) 

def run():
    serve(app, host = "127.0.0.1", port = 8000)
    #app.run(host = "127.0.0.1", port = 8000, threaded = True, debug = False, use_reloader = False)

if __name__ == "__main__":
    import sys
    qtapp = QtWidgets.QApplication(sys.argv)
    QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create("windowsvista"))
    JINX7 = Window()
    JINX7.show()
    thread = threading.Thread(target=run)
    thread.daemon = True
    thread.start()
    sys.exit(qtapp.exec())