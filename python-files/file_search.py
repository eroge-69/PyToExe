import os
from readchar import readkey, key
from getpass import getpass
import io
import subprocess
from hashlib import sha256


def get_sha256(text: str):
    return sha256(text.encode("utf-8")).hexdigest()


def get_names(file, password):
    """Returns the name of files present within the arhieve"""
    proc = subprocess.Popen(
        [r"C:\Program Files\Winrar\UnRAR.exe", "l", f"-p{password}", file],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )

    filenames = []
    for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
        if line.startswith("*   ..A"):
            filename = line.rsplit("  ", 1)[1].strip("\n")
            filenames.append(filename)

    return filenames


def main():
    password = getpass("Enter password: ")

    if (
        get_sha256(password)
        != "6e8b57ccef884ace0352c38970400b82833328ce9100f3620ded33f5c0018633"
    ):
        print("Incorrect password")
        return

    root_dir = input("Enter root dir to search: ")
    if not os.path.exists(root_dir):
        print(f"{root_dir} doesn't exists")
        return
    if not os.path.isdir(root_dir):
        print(f"{root_dir} is not a dir")
        return

    filenames = []
    for i in range(1, 9):
        file = os.path.join(root_dir, f"fg-0{i}.bin")
        if os.path.exists(file):
            filenames.extend(get_names(file, password))

    if not filenames:
        print("No files found")
        return
    print(f"Found {len(filenames)} files")

    filtered = []
    user_input = ""
    while True:
        if user_input:
            if filtered:
                print("\n".join(filtered))
            else:
                print("No matches found")
            print(f"{user_input}")
        else:
            print("Type something to start searching")

        ch = readkey().lower()
        if ch == key.BACKSPACE:
            user_input = user_input[:-1]

        elif ch == key.ESC:
            break

        elif ch.isprintable():
            user_input += ch

        filtered = [filename for filename in filenames if user_input in filename.lower()]

        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")


if __name__ == "__main__":
    main()
