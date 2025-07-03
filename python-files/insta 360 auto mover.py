import os
import shutil
import time
import ctypes
from pathlib import Path

TARGET_LABEL = "INSTA360"
DESTINATION = "E:/insta360"
KEEP_LATEST = 10

MB_YESNO = 0x04
MB_ICONQUESTION = 0x20

def get_drive_label(drive_letter):
    volume_name_buf = ctypes.create_unicode_buffer(1024)
    fs_name_buf = ctypes.create_unicode_buffer(1024)
    rc = ctypes.windll.kernel32.GetVolumeInformationW(
        f"{drive_letter}\\",
        volume_name_buf,
        ctypes.sizeof(volume_name_buf),
        None,
        None,
        None,
        fs_name_buf,
        ctypes.sizeof(fs_name_buf)
    )
    if rc:
        return volume_name_buf.value
    return ""

def wait_for_insta360_drive():
    print("Waiting for INSTA360 drive...")
    while True:
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            drive_path = f"{letter}:"
            if os.path.exists(drive_path):
                label = get_drive_label(drive_path)
                if label.upper() == TARGET_LABEL:
                    print(f"Detected INSTA360 on drive {drive_path}")
                    return f"{drive_path}/"
        time.sleep(3)

def message_box(title, text):
    result = ctypes.windll.user32.MessageBoxW(0, text, title, MB_YESNO | MB_ICONQUESTION)
    return result == 6  # Yes = 6, No = 7

def file_in_destination(file, source_root):
    try:
        relative = file.relative_to(source_root)
        dest_file = Path(DESTINATION) / relative
        return dest_file.exists(), dest_file
    except Exception:
        return False, None

def move_and_copy_files(source_dir):
    source_root = Path(source_dir)
    all_files = sorted(source_root.rglob("*.*"), key=os.path.getmtime, reverse=True)

    keep_files = all_files[:KEEP_LATEST]
    move_files = all_files[KEEP_LATEST:]

    os.makedirs(DESTINATION, exist_ok=True)

    total = len(all_files)
    processed = 0

    for file in keep_files:
        exists, dest = file_in_destination(file, source_root)
        if not exists:
            rel = file.relative_to(source_root)
            target = Path(DESTINATION) / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(file, target)
            except Exception as e:
                print(f"\nError copying {file}: {e}")
        processed += 1
        show_progress(processed, total, action="Copying")

    for file in move_files:
        exists, dest = file_in_destination(file, source_root)
        rel = file.relative_to(source_root)
        target = Path(DESTINATION) / rel
        target.parent.mkdir(parents=True, exist_ok=True)

        try:
            if exists:
                file.unlink()  # Delete original if already exists in destination
            else:
                shutil.move(file, target)
        except Exception as e:
            print(f"\nError moving {file}: {e}")

        processed += 1
        show_progress(processed, total, action="Moving")

    print("\nDone.")

def show_progress(current, total, action="Processing"):
    percent = int((current / total) * 100)
    bar = ("#" * (percent // 5)).ljust(20)
    print(f"\r{action} files: [{bar}] {percent}% ({current}/{total})", end="", flush=True)

def main():
    drive = wait_for_insta360_drive()
    if message_box("INSTA360", "Move files from INSTA360?"):
        if message_box("INSTA360", "Keep the 10 latest files, but move the rest?"):
            move_and_copy_files(drive)

if __name__ == "__main__":
    main()
