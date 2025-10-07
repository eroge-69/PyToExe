#PAC Extractor
#coded by James

#import
import sys, os
from struct import *

#gets all the offsets from the header
def getFiles(str):
    num_files = unpack("<I", str[4:8])[0] #how many files
    offset = 8
    offsets = []
    
    #for how many files, get each pointer
    for i in range(num_files):
        file = unpack("<I", str[offset:offset+4])[0]
        if file != 0 and file not in offsets:
            offsets.append(file)
        offset += 4
    return offsets

#get the type of file, just add more to this for more file types
#double tested because I was having errors without it
def getType(str):
    try:
        if str[:4].encode("hex").upper() == "4D4F4420" or str[:3] == "MOD":
            suf = "mod"
        elif str[:4] == "TIM2":
            suf = "tm2"
        elif str[:4].encode("hex").upper() == "53485720" or str[:3] == "SHW":
            suf = "shw"
        elif str[:3] == "MOT" or str[:4].encode("hex").upper() == "50000000":
            suf = "mot"
        elif str[:3] == "PAC" or str[:3] == "PNS":
            suf = "pac"
        elif str[:4].encode("hex").upper() == "4F676753" or str[:3] == "Ogg":
            suf = "ogg"
        elif str[:4].encode("hex").upper() == "424D3600" or str[:3] == "BM6":
            suf = "bm6"
        elif str[:4].encode("hex").upper() == "000001BA":
            suf = "mpg"
        elif str[:4] == "LIG2":
            suf = "lig"
        elif str[:3] == "SEF":
            suf = "sef"
        elif str[:3] == "CAM":
            suf = "cam"
        elif str[:3] == "EVE":
            suf = "eve"
        elif str[:3] == "POS":
            suf = "pos"
        elif str[:4].encode("hex").upper() == "EFBBBF23":
            suf = "txt"
        elif str[:4].encode("hex").upper() == "00000000":
            suf = "bd"
        elif str[:4].encode("hex").upper() == "00000100":
            suf = "ico"
        elif str[:4].encode("hex").upper() == "64627354" or str[:4] == "dbsT":
            suf = "tsb"
        elif str[:2] == "# ":
            suf = "txt"
    #    elif str[:4] == "ff&A":
    #        suf = "ff"
        elif str[:1] == ";":
            suf = "txt"
        elif str[:2].encode("hex").upper() == "0600" and str[2:4] != "0000":
            suf = "so"
            
        #last chance, if the first three values are ASCII, use em.
        elif (unpack("B", str[:1]) >= 65 and unpack("B", str[:1]) <= 90 and  unpack("B", str[1:2]) >= 65 and unpack("B", str[1:2]) <= 90 and unpack("B", str[2:3]) >= 65 and unpack("B", str[2:3]) <= 90) or (unpack("B", str[:1]) >= 97 and unpack("B", str[:1]) <= 122 and unpack("B", str[1:2]) >= 97 and unpack("B", str[1:2]) <= 122 and unpack("B", str[2:3]) >= 97 and unpack("B", str[2:3]) <= 122):
            suf = str[:3]
        else: suf = "ukn"
    except:
        suf = "ukn"
    return suf

#PTX extractor
def PTX(str, ptx_name, pac_name):
    #print "PTX Archive: %s.ptx" % ptx_name
    num_files = unpack("<I", str[:4])[0] #number of files
    offsets = []
    last = 0
    
    #too lazy to properly write it, just searched
    for i in range(num_files):
        offsets.append(str.find("TIM2", last))
        last = str.find("TIM2", last)+4
    
    #make another sub directory
    try:
        os.mkdir("%s\\%s" % (pac_name, ptx_name))
    except WindowsError:
        ""
    index_file = open("%s\\%s\\%s.index" % (pac_name, ptx_name, ptx_name), "w")
    #for how many files, write each file
    for i in range(num_files):
        try:
            file_str = str[offsets[i]:offsets[i+1]]
        except IndexError:
            file_str = str[offsets[i]:]
        #index files, and writing contents
        index_file.write("%s_%.3d.tm2\n" % (ptx_name, i))
        print "\tWriting: %s_%.3d.tm2" % (ptx_name, i)
        try:
            file_open = open("%s\\%s\\%s_%.3d.tm2" % (pac_name, ptx_name, ptx_name, i), "wb")
            file_open.write(file_str)
            file_open.close()
        except:
            print "\tError Writing %s_%.3d.tm2" % (ptx_name, i)
    return 0

def main():
    #greetings
    print "\n=================================\nDevil May Cry 3 \nPac extractor\nv1.0\nCoded by James aka Jamesuminator\n=================================\n---------------------------------\n"
    #not enough args, usage
    if len(sys.argv) < 2:
        print "Usage: %s [file]\nExtracts Contents of a DMC3 PAC" % sys.argv[0]
        return -1
    else:
        pac_file = sys.argv[1]     #pac file
        pac_name = pac_file[:pac_file.find(".")]    #the name of the folder
        
    #if can't open, exit
    print "Opening: %s" % pac_file
    try:
        pac_open = open(pac_file, "rb")
    except:
        print "Error Opening %s" % pac_file
        return -1
    
    #if can't read, exit
    print "Reading: %s" % pac_file
    try:
        pac_str = pac_open.read()
    except:
        print "Error Reading %s" % pac_file
        return -1
    pac_open.close()
    
    #if the header is corrupt, exit
    try:
        offsets = getFiles(pac_str)
        print "\nNumber of Files: %d\n" % len(offsets)
    except:
        print "Error Getting Contents of %s" % pac_file
        return -1
    
    #make directory
    try:
        os.mkdir(pac_name)
    except:
        ""
    
    #write all the files
    index_file = open("%s\\%s.index" % (pac_name, pac_name), "w")
    for i in range(len(offsets)):
        try:
            file_str = pac_str[offsets[i]:offsets[i+1]]
        except IndexError:
            file_str = pac_str[offsets[i]:]
        
        if "TIM2" in file_str[4:] and "PAC" not in file_str and "PNST" not in file_str:
            print "%X" % offsets[i]
            PTX(file_str, "%s_%.3d" % (pac_name, i), pac_name)
            index_file.write("%s folder\n" % ("%s_%.3d"% (pac_name, i)))
        else:
            index_file.write("%s_%.3d.%s\n" % (pac_name, i,getType(file_str)))
            print "Writing: %s_%3d.%s" % (pac_name, i,getType(file_str))
            try:
                file_open = open("%s\\%s_%.3d.%s" % (pac_name,pac_name, i,getType(file_str)), "wb")
                file_open.write(file_str)
                file_open.close()
            except:
                print "Error Writing %s" % ("%s_%.3i.%s" % (pac_name, i,getType(file_str)))
    index_file.close()
    
    print "\nAll Done!"
    return 0

main()
    

    