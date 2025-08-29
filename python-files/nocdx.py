import sys
import os

def unlink_cdx(path):
    if not os.path.isfile(path):
        print(f"File not found: {path}")
        return 1
    try:
        with open(path, "r+b") as f:
            f.seek(28)  # байт флагов
            b = f.read(1)
            if len(b) == 1:
                flag = b[0]
                if flag & 1:  # бит 0 установлен
                    flag = flag & 0b11111110  # снимаем бит 0
                    f.seek(28)
                    f.write(bytes([flag]))
        print(f"CDX flag cleared: {path}")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: nocdx.exe <path-to-dbf>")
        sys.exit(1)
    sys.exit(unlink_cdx(sys.argv[1]))