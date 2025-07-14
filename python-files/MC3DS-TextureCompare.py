import os, sys

def compare_files(base_file, first_file, second_file, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    first_file_output = os.path.join(output_dir, os.path.basename(first_file))
    with open(first_file, 'rb') as f1, open(first_file_output, 'wb') as f1_out:
        f1_out.write(f1.read())
    
    with open(base_file, 'rb') as base_f, open(second_file, 'rb') as second_f, open(first_file_output, 'rb+') as output_f:
        base_data = base_f.read()
        second_data = second_f.read()
        for i in range(len(base_data)):
            if base_data[i] != second_data[i]:
                output_f.seek(i)
                output_f.write(second_data[i:i+1])

try:
    base_file_path = sys.argv[1]
except IndexError:
    print("\nThis Application is a CLI Tool. And can only be ran from Windows Powershell or Command Prompt.")
    print("Usage: 'python MC3DS-TextureCompare.py [YourUnmodifiedFilePATH] [YourModifiedFilePATH] [TheOtherModifiedFileToMergePATH]'\n")
    print("Please Note: Do NOT include the [] or the Quotation Marks in the Usage Example.\n")
    os.system('pause')
    exit(1)
try:
    first_file_path = sys.argv[2]
except IndexError:
    print("Primary File Input is Missing.\n")
    os.system('pause')
    exit(1)
try:
    second_file_path = sys.argv[3]
except IndexError:
    print("Secondary File Input is Missing.\n")
    os.system('pause')
    exit(1)

second_file_path = second_file_path.replace('"','');second_file_path = second_file_path.replace('\\','/')
base_file_path = base_file_path.replace('"','');base_file_path = base_file_path.replace('\\','/')
first_file_path = first_file_path.replace('"','');first_file_path = first_file_path.replace('\\','/')
output_directory = '.\\mc3dstc_out'
if os.path.exists(base_file_path) and '.3dst' in base_file_path:
    pass
else:
    print(f"PATH Provided for The BASE File isn't Correct or has the Wrong File Extension.\n")
    exit(1)
if os.path.exists(first_file_path) and '.3dst' in first_file_path:
    pass
else:
    print(f"PATH Provided for The Primary File isn't Correct or has the Wrong File Extension.\n")
    exit(1)
if os.path.exists(second_file_path) and '.3dst' in second_file_path:
    pass
else:
    print(f"PATH Provided for The Secondary File isn't Correct or has the Wrong File Extension.\n")
    exit(1)

compare_files(base_file_path, first_file_path, second_file_path, output_directory)