__author__ = 'LionelB1'
#!/usr/bin/python

from socket import *
import re
import sys
import os


# print(sys.argv)
argv_key_list = ['-ip', '-cl', '-cr', '-cv', '-cp', '-ci']
NLPORT = 5142

FULLPATH_KEY = "-cl"
BASENAME_KEY = "filename"
FILE_SIZE_KEY = "size"
MASK_KEY = "mask"
USER_KEY = "user"
GROUP_KEY = "group"
TYPE_KEY = "type"

NLC_DOWNLOAD = "DLD:"
NLC_RESET = "RST:"
NLC_GET_VERSION = "VER:"
NLC_GET_TERM_INFO = "WHO:"
NLC_GET_INSTALLED_PACKAGE = "WHO2:"

NLT_FS = '\x1C'
NLT_GS = '\x1D'
NLT_NULL = '\x00'

# dictionary to hold all param
all_parameters = dict()
#all_parameters[MASK_KEY] = "644"
all_parameters[MASK_KEY] = "750"
all_parameters[USER_KEY] = "os"
all_parameters[GROUP_KEY] = "system"
all_parameters[TYPE_KEY] = "F"


def printUsage():
    print("-ip: specify the IP address of the device (mandatory)")
    print("-cl: <filename> load the specified file ")
    print("-cr: force a reset")
    print("-cv: get NetLoader version")
    print("-cp: get list of installed packages and bundles")
    print("-ci: get terminal info")
    print("Commands can be chained: netloader.py -cv -cp -cl myApp.tar -cr")

# use full path from all_parameters (-f) and update it with file basename and size


def _getFileInfo():
    # extract basename from full path
    full_path = all_parameters["-cl"]
    basename = os.path.basename(full_path)
    all_parameters[BASENAME_KEY] = basename

    # check if file exist and get the size
    if os.path.isfile(full_path):
        size = os.path.getsize(full_path)
        all_parameters[FILE_SIZE_KEY] = size
    else:
        all_parameters[FILE_SIZE_KEY] = -1


def _check_all_parameters():
    if (all_parameters[FILE_SIZE_KEY] == -1):
        print("error: can't find ", all_parameters['-f'])
        exit()

    if (all_parameters[FILE_SIZE_KEY] == 0):
        print("error: 0 file size for ", all_parameters['-f'])
        exit()


def _bytes_from_file(filename, chunksize=4096):
    with open(filename, "rb") as f:
        while True:
            chunk = f.read(chunksize)
            if chunk:
                yield chunk
            else:
                break


class NetLoader:
    def __init__(self, ARGS, port=NLPORT):
        self._ip = ARGS["-ip"]
        self._port = port
        self._sock = None

    def _connect_to_device(self):
        print(self._ip)
        print(self._port)
        self._sock = socket(AF_INET, SOCK_STREAM)  # create a TCP socket
        self._sock.connect((self._ip, self._port))  # connect to server on the port
        print("Uspesne nadviazane Spojenie")

    def _close_connection(self):
        self._sock.close()

    def load_file(self, param):
        filename = param[BASENAME_KEY]
        size = param[FILE_SIZE_KEY]
        # build download file command
        cmd = NLC_DOWNLOAD + param[BASENAME_KEY] + NLT_NULL
        cmd += str(param[FILE_SIZE_KEY]) + NLT_NULL
        cmd += str(param[MASK_KEY]) + NLT_NULL
        cmd += str(param[USER_KEY]) + NLT_NULL
        cmd += str(param[GROUP_KEY]) + NLT_NULL
        cmd += str(param[TYPE_KEY]) + NLT_NULL
        self._connect_to_device()
        print("cmd:", cmd)
        self._sock.send(cmd.encode())
        rsp = self._sock.recv(16).decode()  # receive device resp
        print("resp", rsp)
        if rsp != "OK\x00":
            print("error: download can't be initialized")
            exit()

        print("download of", filename, "initialized")
        all_bytes = _bytes_from_file(param["-cl"])
        for b in all_bytes:
            self._sock.send(b)
            print("."),
        print("[Done]")

    def getversion(self):
        cmd = NLC_GET_VERSION + NLT_NULL
        self._connect_to_device()
        print("cmd:", cmd)
        print("cmd.encode:", cmd.encode())
        self._sock.send(cmd.encode())
        rsp = self._sock.recv(16).decode()  # receive device resp
        print("resp", rsp)
        self._close_connection()

    def showMessage(self, msg):
        cmd = "MSG:" + msg + NLT_NULL
        self._connect_to_device()
        print("cmd:", cmd)
        print("cmd.encode:", cmd.encode())
        self._sock.send(cmd.encode())
        rsp = self._sock.recv(16).decode()  # receive device resp
        print("resp", rsp)
        self._close_connection()

    def getListOfBundleAndPackages(self):
        cmd = NLC_GET_INSTALLED_PACKAGE + NLT_NULL
        self._connect_to_device()
        print("cmd:", cmd)
        print("cmd.encode:", cmd.encode())
        self._sock.send(cmd.encode())
        rsp = self._sock.recv(1024).decode()
        print("rsp:", rsp)
        self._close_connection()
        # analyse rsp
        ll = rsp.split("\x1c")
        for l in ll:
            print("=====================")
            ls = l.split("\x1d")
            for s in ls:
                print(s)

        return rsp


def is_valid_ipv4(ip):
    """Validates IPv4 addresses.
    """
    pattern = re.compile(r"""
        ^
        (?:
          # Dotted variants:
          (?:
            # Decimal 1-255 (no leading 0's)
            [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
          |
            0x0*[0-9a-f]{1,2}  # Hexadecimal 0x0 - 0xFF (possible leading 0's)
          |
            0+[1-3]?[0-7]{0,2} # Octal 0 - 0377 (possible leading 0's)
          )
          (?:                  # Repeat 0-3 times, separated by a dot
            \.
            (?:
              [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
            |
              0x0*[0-9a-f]{1,2}
            |
              0+[1-3]?[0-7]{0,2}
            )
          ){0,3}
        |
          0x0*[0-9a-f]{1,8}    # Hexadecimal notation, 0x0 - 0xffffffff
        |
          0+[0-3]?[0-7]{0,10}  # Octal notation, 0 - 037777777777
        |
          # Decimal notation, 1-4294967295:
          429496729[0-5]|42949672[0-8]\d|4294967[01]\d\d|429496[0-6]\d{3}|
          42949[0-5]\d{4}|4294[0-8]\d{5}|429[0-3]\d{6}|42[0-8]\d{7}|
          4[01]\d{8}|[1-3]\d{0,9}|[4-9]\d{0,8}
        )
        $
    """, re.VERBOSE | re.IGNORECASE)
    return pattern.match(ip) is not None

# main loop


if __name__ == '__main__':

    # first get the IP
    if ("-ip") not in sys.argv:
        print("error: device's IP is missing")
        exit()

    index = sys.argv.index("-ip")
    all_parameters["-ip"] = sys.argv[index + 1]

    NL = NetLoader(all_parameters, NLPORT)

    # then loop over all commands and process one by one
    for arg in sys.argv[1:]:  # skip the program name argv[0]
        if arg not in argv_key_list:
            continue

        if arg == "-ip":
            continue

        # process download
        if (arg == "-cl"):
            index = sys.argv.index(arg)
            all_parameters[arg] = sys.argv[index + 1]
            _getFileInfo()
            NL.load_file(all_parameters)
            continue

        if (arg == "-cp"):
            NL.getListOfBundleAndPackages()
            continue

        if (arg == "-cv"):
            NL.getversion()
            continue
