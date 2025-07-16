import os
import shutil

path1 = "C:\\Windows\\Temp\\"
path2 = "C:\\Users\\Mohammed\\AppData\\Local\\Temp\\"
path3 = "C:\\Windows\\prefetch\\"
successes, fail = " :- File removed", " :- Permission Denied"

def cls(paths):
    if len(os.listdir(paths)) == 0:
        print("Empty folder:", paths)
        return
    for item in os.listdir(paths):
        full_path = os.path.join(paths, item)
        try:
            if os.path.isfile(full_path) or os.path.islink(full_path):
                os.remove(full_path)
            elif os.path.isdir(full_path):
                shutil.rmtree(full_path)
            print(item + successes)
        except Exception as e:
            print(item + fail + f" ({e})")

print("#" * 50 + "TEMP")
cls(path1)
print("#" * 50 + "%TEMP%")
cls(path2)
print("#" * 50 + "PREFETCH")
cls(path3)
