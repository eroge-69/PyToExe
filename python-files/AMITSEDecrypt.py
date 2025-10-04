#!/usr/bin/env python3

import sys, os, platform
from pathlib import Path

if (len(sys.argv) < 2):
    raise Exception("No input file was given.")

def decode(pw_hash):
    dec = pw_hash ^ 0x5B93B62611BA6C4DC7E022747D07D89A332E8EC1E95444E89F7BFA0E55A2B0350BC9665CC1EF1C83
    res = hex(dec)[2:]
    fin = ""

    i = 0
    for char in res:
        if i % 4 < 2:
            fin += char

        i += 1
    
    return bytes.fromhex(fin).decode(errors="ignore")

def extract(imagePath):
    basePath = Path(__file__).parent.resolve()

    if platform.system() == "Linux":
        toolPath = Path(basePath, "UEFIExtract")
        os.system(str(toolPath) + " " + str(imagePath) + " > /dev/null")
    elif platform.system() == "Windows":
        toolPath = Path(basePath, "UEFIExtract.exe")
        os.system(str(toolPath) + " " + str(imagePath) + " > nul")

    return Path(imagePath.parent, str(imagePath.name) + ".dump")

def search(dumpPath):
    return list(dumpPath.rglob("*AMITSESetup"))


imagePath = Path(sys.argv[1])

print("Extracting " + str(imagePath) + "\n")
dumpPath = extract(imagePath)

print("Searching " + str(dumpPath) + "\n")
results = search(dumpPath)

for result in results:
    filePath = Path(result, "body.bin")

    with open(filePath, mode='rb') as file:
        fileContent = file.read()

    t = 0
    while ((t+1)*40 <= len(fileContent)):
        pw_hash = int(fileContent[t*40:(t+1)*40].hex(), base=16)
        t = t+1

        if (pw_hash == 0):
            continue

        print("Found possible password hash in " + str(filePath) + " at offset " + hex((t-1)*40))

        password = decode(pw_hash)

        print("Decoded Password: " + password + "\n")