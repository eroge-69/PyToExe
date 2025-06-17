import os, sys, time, ctypes
from PIL import Image
from win32api import EnumDisplayMonitors
from win32con import SPI_SETDESKWALLPAPER, SPIF_UPDATEINIFILE, SPIF_SENDCHANGE

def get_monitors():
    mlist = []
    def callback(hMonitor, hdc, rect, data):
        mlist.append(rect)
    EnumDisplayMonitors(None, None, callback, None)
    return mlist  # list of (left, top, right, bottom)

def make_canvas(image_path, monitors):
    img = Image.open(image_path).convert('RGB')
    # compute bounding rectangle of all monitors
    lefts = [r[0] for r in monitors]; tops = [r[1] for r in monitors]
    rights = [r[2] for r in monitors]; bots = [r[3] for r in monitors]
    min_x, min_y = min(lefts), min(tops)
    max_x, max_y = max(rights), max(bots)
    W, H = max_x - min_x, max_y - min_y

    canvas = Image.new('RGB', (W, H), (0,0,0))
    # Paste image centered in canvas
    scale = min(W/img.width, H/img.height)
    im2 = img.resize((int(img.width*scale), int(img.height*scale)), Image.ANTIALIAS)
    x = (W - im2.width)//2
    y = (H - im2.height)//2
    canvas.paste(im2, (x, y))
    # save
    out = os.path.join(os.getcwd(), "_current_wallpaper.bmp")
    canvas.save(out, "BMP")
    return out

def set_wallpaper(path):
    ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER, 0, path,
        SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )

def main():
    folder = os.path.join(os.path.dirname(sys.argv[0]), "images")
    if not os.path.isdir(folder):
        print("Folder images/ not found.")
        return

    files = [os.path.join(folder, f) for f in os.listdir(folder)
             if f.lower().endswith(('.png','.jpg','.jpeg','.bmp'))]
    files.sort()
    if not files:
        print("No images found in images/")
        return

    idx = 0
    monitors = get_monitors()
    while True:
        img = files[idx % len(files)]
        bmp = make_canvas(img, monitors)
        set_wallpaper(bmp)
        idx += 1
        time.sleep(10)

if __name__ == "__main__":
    main()
