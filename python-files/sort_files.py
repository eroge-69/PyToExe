import os
files = os.listdir()
sorted_files = sorted(files, key=lambda x: int(x.split('-')[3]))
for file in sorted_files:
    print(file)