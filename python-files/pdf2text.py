#!/usr/bin/python3
# title           : pdf2text.py
# description     : Convert a PDF into text file.
# author          : Martin Hohlneicher/ BKG 
# version         : 1.0 (07/2025) 
#==================================================================================================

from pypdf import PdfReader
import sys
import os
import glob
sys.stdout.reconfigure(encoding='utf-8')

def convert2txt(pdf_in):
    '''
    Make a list of all files with a given extension in a chosen directory.

    Parameters
    ----------
        - pdf_in

    Returns
    -------
        - none    
    '''
    print('Converting ' + pdf_in + ' into textfile.')
    reader = PdfReader(pdf_in)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

    # Write textfile:
    text_file = pdf_in.replace('pdf', 'txt')    
    with open(text_file, "w", encoding="utf-8") as f:
        print(text, file=f, end='')    

def get_file_list(directory, file_extension):
    '''
    Make a list of all files with a given extension in a chosen directory.

    Parameters
    ----------
        - file_extension

    Returns
    -------
        - filelist    
    '''
    # Go to directory:
    os.chdir(directory)        
    # Get sorted list of files:    
    filelist = sorted(glob.glob('*' + file_extension)) 
    return filelist 

def main(arg):
    '''
    Make a list of all files with a given extension in a chosen directory.

    Parameters
    ----------
        - arg

    Returns
    -------
        - filelist 
    '''   
    directory_input = './'
    directory_output = './'
    # Check if input-file (pdf) is provided as program argument:
    if len(arg) > 1:
        filelist_pdf = [arg[1]]
    # if not, take all pdfs in input folder:    
    else: 
        filelist_pdf = get_file_list(directory_input, file_extension='pdf')
    # Get file list of all existing text files in folder:    
    filelist_txt = get_file_list(directory_input, file_extension='txt')   

    # Convert pdfs into txt, if not already done:
    for pdf in filelist_pdf:
        if pdf.replace('pdf', 'txt') not in filelist_txt:
            convert2txt(pdf)           

# ======================================================================================= M A I N:
if __name__ == "__main__":
    main(sys.argv)

# ======================================================================================= N O T E S:    
# python3.12 -m pip install --user pypdf    
    