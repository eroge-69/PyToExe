import pandas
import re
from datetime import datetime
from dateutil.parser import parse

def process_shelf(file):
    new_file = file + ' ' + str(datetime.now()) + '.txt'
    with open(file + '.txt', 'r') as reader, open(new_file, 'w') as writer:
        lines = reader.readlines()
        area = ''
        writer.write('Date       Header     Dept Cat.  Mfg   Style Type    Retail  P.O.      Vendor Name     Style Description    Store Holding    Total Area    Pre Ticket\n')

        for line in lines:
            if(len(line) == 0):
                continue
            
            clean_line = re.sub("\s\s+" , " ", line).strip()
            split_line = clean_line.split()
            if 'GRAND TOTAL PAGE' in line:
                break
            if 'Area' in line:
                if split_line[1] == area:
                    continue
                else:
                    area = split_line[1]
                    continue
            elif len(split_line) > 0:
                if is_date(split_line[0]) and "TOTAL HEADERS" not in line:
                    last_char = split_line[len(split_line) - 1]
                    num_spaces = " "
                    if len(area) == 4:
                        num_spaces = "  "
                    if len(area) == 6:
                        num_spaces = ""
                    if last_char.isnumeric():
                        writer.write(line.rstrip() + " " + area + num_spaces)
                    else:
                        new_str = line.rstrip()[:-1].strip()
                        writer.write(" " + new_str + " " + area + num_spaces)
                    if "*" in line:
                        writer.write("       Y      \n")
                    else:
                        writer.write("       N      \n")
                    continue      
            else:
                continue

def process_purge(file):
    new_file = file + ' ' + str(datetime.now()) + '.txt'
    with open(file + ".txt", 'r') as reader, open (new_file, 'w') as writer:
        lines = reader.readlines()
        area = ''

        writer.write("Location      Date   Header    Dept Vendor Name                     Style Description        #Boxes #Pllts   Hdr Status\n")
        for line in lines:
            if len(line) == 0:
                continue

            clean_line = re.sub("\s\s+" , " ", line).strip()
            split_line = clean_line.split()

            if len(split_line) > 1:
                if is_date(split_line[1]):
                    writer.write(line.rstrip() + "\n")      

            continue

def is_date(string, fuzzy=False):
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False

process_shelf('PHIL SHELF')
process_shelf('PITT SHELF')
process_purge("PHIL PURGE")
process_purge("PITT PURGE")