import os
import sys
import signal
import time
import base64
import hashlib
import json
import copy # Module copy installed via pip
try:
  from playsound import playsound # Module playsound installed via pip
except Exception:
  pass
from urllib import request
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes # Module cryptography installed via pip
from cryptography.hazmat.backends import default_backend

statusDebug = False
allStreets = False

streets_list = [
    "ADRA WAY",
    "AEGINA WAY",
    "AEOLIA WAY",
    "AGORA WAY",
    "ALICANTE WAY",
    "ANDROS WAY",
    "ARCADIA WAY",
    "ATHOS WAY",
    "BARCELONA WAY",
    "CAESENA WAY",
    "COLLINOS WAY",
    "CORDOBA WAY",
    "CORINTHIA WAY",
    "CYRUS WAY",
    "DASSIA WAY",
    "DELOS WAY",
    "DEMETER WAY",
    "DENIA WAY",
    "GALICIA WAY",
    "ICARIA WAY",
    "KALAMIS WAY",
    "KEOS WAY",
    "LAMIA WAY",
    "LEISURE VILLAGE DRIVE",
    "LEISURE VILLAGE WAY",
    "LEMNOS WAY",
    "LERKAS WAY",
    "LINDOS WAY",
    "LORCA WAY",
    "MAJORCA WAY",
    "MALEA WAY",
    "MARATHON WAY",
    "MILETUS WAY",
    "MILOS WAY",
    "MYCENAE WAY",
    "OCEAN HILLS DRIVE",
    "PATMOS WAY",
    "PINDAR WAY",
    "PIROS WAY",
    "POSEIDON WAY",
    "PYLOS WAY",
    "RHODES WAY",
    "SANTORINI WAY",
    "SIROS WAY",
    "THEBES WAY",
    "TILOS WAY",
    "ZAMORA WAY",
    "ZENOS WAY"
]


agencies = {
    "37170": "VISTA FIRE", 
    "37115": "OCEANSIDE FIRE", 
    "37145": "SAN MARCOS FIRE", 
    "37025": "CARLSBAD FIRE",
    "37047": "SAN DIEGO COUNTY FIRE"
}

def ppPullAgency(agency_id):
  ## BEGIN IMPORTED CODE
  data = json.loads(request.urlopen("https://web.pulsepoint.org/DB/giba.php?agency_id=" + agency_id).read().decode())
  
  ct = base64.b64decode(data.get("ct"))
  iv = bytes.fromhex(data.get("iv"))
  salt = bytes.fromhex(data.get("s"))
  
  # Build the password tombrady5rings
  t = ""
  e = "CommonIncidents"
  t += e[13] + e[1] + e[2] + "brady" + "5" + "r" + e.lower()[6] + e[5] + "gs"
  
  # Calculate a key from the password
  hasher = hashlib.md5()
  key = b''
  block = None
  while len(key) < 32:
    if block:
        hasher.update(block)
      
    hasher.update(t.encode())
    hasher.update(salt)
    block = hasher.digest()
  
    hasher = hashlib.md5()
    key += block
  
  # Create a cipher and decrypt the data
  backend = default_backend()
  cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
  decryptor = cipher.decryptor()
  out = decryptor.update(ct) + decryptor.finalize()
  
  # Clean up output data
  out = out[1:out.rindex(b'"')].decode()              # Strip off extra bytes and wrapper quotes
  out = out.replace(r'\"', r'"')                      # Un-escape
  ## END IMPORTED CODE
  
  aout = json.loads(out).get("incidents", {}).get("active", {})
  active = {}
  if aout:
    for a in aout:
      active[a["ID"]] = a
  
  return active

def isRelevantStreet(streetName,streetList):
  for street in streetList:
    if street.upper() in streetName.upper():
      return True
  return False

def trimStreetName(streetName):
  return streetName[0:streetName.index(",")]

def clearScreen(lines):
  if statusDebug:
    return not statusDebug
  if os.name.upper() == "NT":
    os.system("cls")
  else:
    os.system("clear")
  for i in range(lines):
    print("")
  return not statusDebug

def printDebug(debugString):
  if statusDebug:
    print("     --- " + str(debugString))
    return statusDebug
  else:
    return statusDebug

def mainLoop(delayTime):
  cachedIncidents = {}
  while True:
    printDebug("Top of mainLoop.")
    try:
      active = {}
      for agency_id in agencies.keys():
        try:
          printDebug("Trying to pull data for " + agencies[agency_id] + ".")
          newactive = ppPullAgency(agency_id)
          for na in newactive.keys():
            try:
              active[na] = newactive[na]
            
            except Exception:
              printDebug("No incidents for " + agencies[agency_id] + ".")
              break
        
        except Exception:
          printDebug("Failed to pull any.")
          continue
      
      factive = {}
      for a in active.keys():
        printDebug("Checking to see if " + a + " is a relevant address.")
        if isRelevantStreet(active[a]["FullDisplayAddress"],streets_list):
          printDebug("" + a + " is relevant.")
          factive[a] = active[a]
                
      if len(factive.keys()) > 0:
        clearScreen(100)
      
      if len(factive.keys()) > 0:
        print(" ** REFERENCE DATE & TIME: [" + \
              str(time.gmtime().tm_year) + "-" + \
              str(time.gmtime().tm_mon).zfill(2) + "-" + \
              str(time.gmtime().tm_mday).zfill(2) + "T" + \
              str(time.gmtime().tm_hour).zfill(2) + ":" + \
              str(time.gmtime().tm_min).zfill(2) + ":" + \
              str(time.gmtime().tm_sec).zfill(2) + "Z] ** \n" \
              )

      alertSoundPlayed = False
      for fa in factive.keys():
        factive[fa]["TrimmedAddress"] = trimStreetName(factive[fa]["FullDisplayAddress"])
        factive[fa]["AgencyName"] = agencies[factive[fa]["AgencyID"]]
        printDebug("Has incident " + fa + " already been cached?")
        if fa not in cachedIncidents.keys():
          printDebug("No, adding to cache and playing alert sound.")
          cachedIncidents[fa] = factive[fa]
          if not alertSoundPlayed:
            alertSoundPlayed = True
            try:
              if statusDebug:
                printDebug("Pretending to play alert sound.")
              else:
                playsound("alarm0.mp3", False)
            
            except Exception:
              print(" !! WARNING: Could not play the alert sound. !!")

      printDebug("Copying cache.")
      cachedIncidentsCopy = copy.deepcopy(cachedIncidents)
      for ci in cachedIncidents.keys():
        printDebug("Checking to see if " + ci + " from the cache is still in the relevant active list.")
        if ci in factive.keys():
          print(" => [" + \
                str(factive[ci]["CallReceivedDateTime"]) + "] " + \
                str(factive[ci]["PulsePointIncidentCallType"]) + ": " + \
                str(factive[ci]["TrimmedAddress"]) + " (" + \
                str(factive[ci]["AgencyName"]) + ")" \
                )
          
        else:
          printDebug("" + ci + " isn't active anymore, removing it from copied cache.")
          cachedIncidentsCopy.__delitem__(ci)

      printDebug("Copying back cache.")
      cachedIncidents = copy.deepcopy(cachedIncidentsCopy)
      
      if len(factive)>0:
        print(" !! NON-EMERGENCY LINE: +1 (858) 756-3006 !! \n")
      else:
        clearScreen(100)
    
    except Exception:
      printDebug("mainLoop 'while True' loop exception, sleeping" + str(delayTime) + " seconds.")
      time.sleep(delayTime)
      continue

    printDebug("Sleeping" + str(delayTime) + " seconds.")
    time.sleep(delayTime)

try:
  print(" ** PulsePoint-OHCC Monitor © 2020-02-19 Daniel D. Duffield.\n    This is Free Software, under the least restrictive two-clause BSD license.")
  printDebug("statusDebug is set to " + str(statusDebug))
  if allStreets:
    streets_list.append("a")
    streets_list.append("e")
    streets_list.append("i")
    streets_list.append("o")
    streets_list.append("u")
  
  time.sleep(5)
  clearScreen(100)
  mainLoop(30)

except KeyboardInterrupt:
  sys.exit(0)
