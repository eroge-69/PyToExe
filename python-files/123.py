import argparse
import time
from encrypt import *
from art import text2art

def logo():
    logo = text2art("FUXSOCY","rand")
    print("\n"+logo+"\n")

def include_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", 
                        "--all", 
                        action="store_true", 
                        help="Encrypt every bit of data in the system")
    
    parser.add_argument("-f",
                        dest="folder",
                        metavar="FOLDERNAME",
                        help="Encrypts the mentioned folder")

    
    parser.add_argument("-l",
                        dest="logo",
                        action = "store_true",
                        help = "prints banner")

    
    return parser

def main():

    parser = include_parser()
    args = parser.parse_args()
        
    if args.logo:
        logo()
    
    if args.all:
        encrypt_system()
    elif args.folder:
        encrypt_folder(args.folder)
    else:
        parser.print_help()

main()
