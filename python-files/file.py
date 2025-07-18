import os
from datetime import datetime
import LpHelper as lp
import getpass
import sys
import re
import socket
import time
import serial
import subprocess
from tailer import follow
import ifaddr
import telnetlib
import paramiko
import json

############################################ Init LP Log ###########################################
timestamp   = datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')[:-3]
logFileName = 'PyLog_' + timestamp + '.txt'

#lp.LogInit(logFileName)

####################################################################################################
class DeviceInfo():
    def __init__(self, handler, connectionType, hostNamePort, timeOutMs):
        self.conn_handle       = handler
        self.conn_type         = connectionType
        self.conn_hostNamePort = hostNamePort
        self.conn_timeOutMs    = timeOutMs

    def PrintDeviceInfo(self):
        print("conn_handle       = ", self.conn_handle)
        print("conn_type         = ", self.conn_type)
        print("conn_hostNamePort = ", self.conn_hostNamePort)
        print("conn_timeOutMs    = ", self.conn_timeOutMs)


####################################################################################################
def InsertDevice(iSessionID, strConnectionType, strHostNamePort, iTimeOutMs, optionString):

    errorCode = 0

    global g_ip_address
    g_ip_address = strHostNamePort
    print('Insert DUT ....\n')
    #lp.LogInfo('strHostNamePort: ' + str(g_ip_address))
    #lp.LogInfo('iTimeOutMs: ' + str(iTimeOutMs))

    return errorCode

####################################################################################################
def InitializeDut(optionString):

    errorCode = 0
    print('Connect to DUT via SSH ...\n')
    global g_client
    g_client = paramiko.SSHClient()
    g_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    g_client.connect(g_ip_address, username='root', password='eAqnKUDca@ZN@$K+ZwTqF6EygyW&#CL8')
    time.sleep(1)

    #stdin, stdout, stderr = g_client.exec_command('ls -al')
    #lp.LogInfo('Connected to UE via SSH!')

    # Read the output of the command
    #output = stdout.read().decode()

    # Print the output
    #print(output)
    return errorCode

####################################################################################################
def RemoveDut(optionString):
    errorCode = 0

    g_client.close()

    return errorCode
####################################################################################################

def imei(client, optionString):
    time.sleep(1)
    stdin, stdout, stderr = client.exec_command('/usr/sbin/sc_atcmd ati\n')
    output = stdout.read().decode('ascii')
    time.sleep(1)
    for line in output.splitlines():
        if "IMEI:" in line:
            imei_value = line.split("IMEI:")[1].strip()
            print('IMEI :',imei_value)
            return imei_value
    print("IMEI not found")
    return None
####################################################################################################

def file(optionString):
    global g_client
    imei_value = imei(g_client, optionString)

    if imei_value is None:
        print("❌ 無法取得 IMEI，檔案不會被重新命名。")
        return None

    folder_path = r'C:\LitePoint\IQfact_plus\IQfact-s_3.7.2_Lock\bin\Log'
    original_filename = os.path.join(folder_path, 'logOutput.txt')
    new_filename = os.path.join(folder_path, f'{imei_value}_logOutput.txt')

    if os.path.exists(original_filename):
        try:
            os.rename(original_filename, new_filename)
            print(f"✅ 檔案已重新命名為：{new_filename}")
        except Exception as e:
            print(f"❌ 檔案重新命名失敗：{e}")
            return None
    else:
        print(f"❌ 找不到檔案：{original_filename}")
        return None

    print(f"📦 取得的 IMEI 為：{imei_value}")
    time.sleep(5)
    return imei_value
####################################################################################################
def main():
    # example

    InsertDevice(iSessionID = 1, strConnectionType = 'SSH', strHostNamePort = '192.168.12.1', iTimeOutMs = 100, optionString = 'optionString_1')

    InitializeDut('')

    file('dummy')
    RemoveDut('')

####################################################################################################
if __name__ == "__main__":
    main()

