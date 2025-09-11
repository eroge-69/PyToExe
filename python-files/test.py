import sys
import re
import subprocess
import webbrowser

def main():
    if len(sys.argv) < 2:
        print("Usage: roblox_launcher.exe <placeId>")
        sys.exit(1)

    place_id = sys.argv[1].strip()

    if not re.fullmatch(r"\d+", place_id):
        print("Error: placeId must be numeric. Example: 123456789")
        sys.exit(2)

    uri = f"roblox://placeId={place_id}"
    print(f"Launching Roblox with: {uri}")

    try:
        # Open via the default registered handler
        webbrowser.open(uri)
    except Exception as e:
        print(f"Failed to launch Roblox: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()