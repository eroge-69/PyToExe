import os
import json
import shutil
from PIL import Image

##Created by TBB Mods https://patreon.com/TBBMods

## For multiple chars at once add the names of the characters whose icons you want to make in this array.
## Change Resize to true if you want the icons to automatically be blown up to a bigger resolution. You'll need to install py_dds for that 

characters_to_mod = [""]
resize = True


### DON'T CHANGE ANYTHING BELOW THIS LINE OR THE SCRIPT WILL NOT WORK ****************************
cwd = os.getcwd()
filesPath = cwd + "/ScriptFiles/"
batch_path = cwd + "/CreatedMods/"
version = "5.5"

def create_folder(folder_path):
    """Creates a folder if it doesn't exist.

    Args:
        folder_path: The path of the folder to create.
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Batch Folder '{folder_path}' created successfully.")
    else:
        print(f"Batch Folder '{folder_path}' already exists.")


def copy_and_rename(source_path, destination_path, new_name):
    """Copies a file and renames it.

    Args:
        source_path: The path to the source file.
        destination_path: The destination directory for the copied file.
        new_name: The desired new name for the copied file.
    """
    
    # Create the full path to the new file
    new_file_path = os.path.join(destination_path, new_name)
    
    
    # Copy the file
    shutil.copy(source_path, new_file_path)
    # Rename the copied file
    os.rename(new_file_path, os.path.join(destination_path, new_name))

def resize_rename_dds(input_path, output_path):
    new_width = 1028
    new_height = 1028
    try:
        image = Image.open(input_path)
        new_image = image.resize((new_width, new_height))
        new_image.save(output_path)
    except Exception as e:
        print(f"Error: {e}")

def copyAndRenameCharacterIcons():
    try:
        with open(f"{filesPath}/character_icon_hashes_array.json", 'r', encoding='utf-8') as file:
            data = json.load(file)

        for item in data:
            print(f"Name: {item['name']}, frontIcon: {item['frontIcon']}")


            try:
                copy_and_rename(f"{filesPath}/IconFiles/{item['frontIcon']}-BC7_UNORM.dds", f"{filesPath}/IconFilesByName/", f"{item['name']}-FRONTICON-{item['frontIcon']}.dds",)
            except Exception as e:
                print(f"{item['name']} front icon error: {e}")


            try:
                copy_and_rename(f"{filesPath}/IconFiles/{item['sideIcon']}-BC7_UNORM.dds", f"{filesPath}/IconFilesByName/", f"{item['name']}-SIDEICON-{item['sideIcon']}.dds",)
            except Exception as e:
                print(f"{item['name']} side icon error: {e}")

    except FileNotFoundError:
        print("Error: Hash File not found.")
    except json.JSONDecodeError:
        print("Error: Hash Invalid JSON format.")
    except UnicodeDecodeError:
        print("Error: Unable to decode the hash file. Please check the file's encoding.")
    except Exception as e:
        print(f"An unexpected error occurred while opening the hash file: {e}")


def createCharModFolder(name, icon_hashes):
    print(f"---- Creating {name} Icon Mod Folder ----")  
    mod_folder = f"{batch_path}/{name}IconMod"
    new_ini_name = f"{name}Icon.ini"
    ini_file = f"{mod_folder}/{new_ini_name}"
    create_folder(mod_folder)
    print(f"* Creating .ini File")  
    copy_and_rename(f"{filesPath}/TEMPLATEIcon.ini", mod_folder, new_ini_name)
    print(f"** Copying Icon Files")  


    try: 
        copy_and_rename(f"{filesPath}/IconFilesByName/{name}-SIDEICON-{icon_hashes['sideIcon']}.dds", mod_folder, f"{name}SideIconSmall.dds")
    except FileNotFoundError:
        print("Error: Character Side Icon not found. Using Traveller as default")
        copy_and_rename(f"{filesPath}/IconFilesByName/Aether-SIDEICON-42205a79.dds", mod_folder, f"{name}SideIconSmall.dds")

    try: 
        copy_and_rename(f"{filesPath}/IconFilesByName/{name}-FRONTICON-{icon_hashes['frontIcon']}.dds", mod_folder, f"{name}FrontIconSmall.dds")
    except FileNotFoundError:
        print("Error: Character Front Icon not found. Using Traveller as default")
        copy_and_rename(f"{filesPath}/IconFilesByName/Aether-FRONTICON-e63509b9.dds", mod_folder, f"{name}FrontIconSmall.dds")

        

    if resize: 
        print(f"*** Resizing Ini Files") 
        
        resize_rename_dds(f"{mod_folder}/{name}SideIconSmall.dds", f"{mod_folder}/{name}SideIcon.dds")
        resize_rename_dds(f"{mod_folder}/{name}FrontIconSmall.dds", f"{mod_folder}/{name}FrontIcon.dds")

        print(f"**** Updating Ini File")  
    else:
        print(f"*** Updating Ini File")  
    # Read in the file
    with open(ini_file, 'r') as file:
        filedata = file.read()

        # Replace the target string
        filedata = filedata.replace('CHARACTER', name)
        filedata = filedata.replace('FRONTICONHASH', icon_hashes['frontIcon'])
        filedata = filedata.replace('SIDEICONHASH', icon_hashes['sideIcon'])

        # Write the file out again
        with open(ini_file, 'w') as file:
            file.write(filedata)

    print(f"***** {name} Icon Mod Created")  


print(f"Welcome to my icon mod maker for GIMI! This is updated for version {version}, if you are using a later version check for an updated script as some hashes may have changed")
print("************************************")


batch_name = input("Enter a batch name (optional): ")

if batch_name != "":
    create_folder(f"/CreatedMods/{batch_name}")
    batch_path = f"{cwd}/CreatedMods/{batch_name}"

try:
    with open(f"{filesPath}/character_icon_hashes_object.json", 'r', encoding='utf-8') as file:
        data = json.load(file)

        if characters_to_mod.__len__() <= 1 and characters_to_mod[0] == "":
            char_name = input("Enter the capitalized character's first name (i.e. Nilou not nilou, Ayaka not Kamisato Ayaka and add _Skin for skins and _CN for the censored skins):  ")
            try: 
                char = data[char_name]
                try: 
                    createCharModFolder(char_name, char)
                except FileNotFoundError:
                    print("Character Icon not found")
                except Exception as error:
                    print(f"Unexpected error while making {char_name} icon mod: {error}") 
            except Exception as error:
                print(f"Character {char_name} not found. Check your spelling / Capitalization") 
        else:
            for char_name in characters_to_mod:
                try: 
                    char = data[char_name]
                    try: 
                        createCharModFolder(char_name, char)
                    except FileNotFoundError:
                        print("Character Icon not found")
                    except Exception as error:
                        print(f"Unexpected error while making {char_name} icon mod: {error}") 
                except Exception as err:
                    print(f"Character {char_name} not found. Check your spelling / Capitalization")  

            print("All Mods Finished")

except FileNotFoundError:
    print("Error: Hash File not found.")
except json.JSONDecodeError:
    print("Error: Hash Invalid JSON format.")
except UnicodeDecodeError:
    print("Error: Unable to decode the hash file. Please check the file's encoding.")
except Exception as e:
    print(f"An unexpected error occurred while opening the hash file: {e}")



