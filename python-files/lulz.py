import os
import subprocess
import tempfile

message = "U just got tricked!!!! Lulz, -ScoutsStuff"

temp_dir = tempfile.gettempdir()
tricked_message_file = os.path.join(temp_dir, "Lulz.txt")

with open(tricked_message_file, "w") as file:
    file.write(message)

subprocess.Popen(["notepad.exe", tricked_message_file])