from cx_Freeze import setup, Executable

# List of included files (if any)
included_files = []  # Add any data files here like ['data.txt', 'images/']

# Base setup (use "Win32GUI" for GUI applications)
base = None
# Uncomment below if you're creating a GUI application
# base = "Win32GUI"

setup(
    name="AI bot",
    version="0.1",
    description="Your Description",
    options={
        "build_exe": {
            "includes": [],      # Add any special modules needed
            "include_files": included_files
        }
    },
    executables=[Executable("ai_bot.py", base=base)]
)