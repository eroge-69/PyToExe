import os

def main():
    print("---------------------- DATA TRANSFER INFORMATION ----------------------\n\n" + \
          "Enter the full path to the directory containing the transfer contents")
    
    root_dir = ""
    while (True):
        root_dir = input("Path: ")
        if os.path.exists(root_dir):
            break
        else:
            print("ERROR - Could not find the specified directory. Try again.")

    default_class = input("Default classification for files: ")
        
    os.chdir(root_dir)

    fout = "transfer_contents.html"

    table_content = ""
    print("Reading directory contents...")
    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            if fout in file:
                continue

            rel_dir = os.path.relpath(subdir, root_dir)
            rel_path = os.path.join(rel_dir, file)
            classification = get_file_classification(file)
            if classification == None:
                classification = default_class
            file_size = get_file_size(rel_path)
            
            table_content = add_row(table_content, rel_path, file_size, classification)

    out_content = get_html()
    out_content = out_content.replace("$REPLACE$", table_content)
    
    fob = open(fout, "w")
    fob.write(out_content)
    fob.close()

    print("Contents written to " + os.path.join(root_dir, fout))

def get_file_size(file_path):
    file_size_bytes = os.path.getsize(file_path)
    file_size_kb = file_size_bytes / 1024
    return round(file_size_kb) 

def get_file_classification(file_name):
    map_to_class = {"S":"SECRET", 
                    "U":"UNCLASSIFIED",
                    "CUI": "CONTROLLED UNCLASSIFIED INFORMATION"}

    f = file_name.strip()
    if f[0] == "(":
        f = f[1:]
        acronymn = f.split(")")[0]
        acronymn = str.upper(acronymn)
        if acronymn in map_to_class.keys():
            return map_to_class[acronymn]
        else:
            return None
    else:
        return None

def add_row(table_content, name, size, classification):
    table_content += '  <tr>\n'
    table_content += '    <th style="font-weight:normal" contenteditable="true">' + str(name) + '</th>\n'
    table_content += '    <th style="font-weight:normal" contenteditable="true">' + str(size) + '</th>\n'
    table_content += '    <th style="font-weight:normal" contenteditable="true">' + str(classification) + '</th>\n'
    table_content += '  </tr>\n'
    return table_content

def get_html():
    return ('<!DOCTYPE html>\n' 
            '<html>\n'
            '<style>\n'
            'table {\n'
            'table-layout: fixed;\n'
            'margin: 0 auto;\n'
            'border-collapse: collapse;\n'          
            '}\n'
            'th, td {\n'
            '  border:1px solid black;\n'
            '  padding: 0.2em;\n'
            '  text-align:left;\n'
            '}\n'
            '</style>\n'
            '<body>\n'
            '<h2 style="text-align: center;">Transfer contents</h2>\n'
            '<table style="width:auto">\n'
            '  <tr>\n'
            '    <th>Classification, Filename, Extension</th>\n'
            '    <th>Size (KB) </th>\n'
            '    <th>File Classification</th>'
            '  </tr>\n'
            '$REPLACE$'
            '</table>\n'
            '</body>\n'
            '</html>\n') 
       
if __name__ == "__main__":
    main()