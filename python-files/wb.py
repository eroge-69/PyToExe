import time
from pathlib import Path
from pyzbar import pyzbar
import argparse
import os
from inspect import getsourcefile
from pdf2image import convert_from_path
from reportlab.graphics.barcode import code128
from reportlab.graphics.shapes import Drawing
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--file", required=True,
    help="Generating cool barcodes sticker from fucking barcodes WildBerries")
args = vars(ap.parse_args())

inFile = Path(args['file'])
workFolder = inFile.parent
inFileName = inFile.stem
extFile = inFile.suffix
scriptPath = Path(getsourcefile(lambda:0)).parent

def clearTempFolder(mydir):
    filelist = [ f for f in os.listdir(mydir) if f.endswith(".pgm") ]
    for f in filelist:
        os.remove(os.path.join(mydir, f))

def createBarCodes(m, f):
    c = canvas.Canvas(f, pagesize=(71*mm, 48*mm))
    fontPath = Path(scriptPath, 'Lato.ttf')
    pdfmetrics.registerFont(TTFont('Lato', fontPath))
    for i in m:
        barcode128 = code128.Code128(i, barWidth = .98, barHeight=26.47*mm)
        codes = [barcode128]
        x = 1.6 * mm
        y = 7.2 * mm
        for code in codes:
            code.drawOn(c, x, y)
            c.setFont('Lato', 12)
            c.drawString(5.3*mm,37.8*mm, i)
        c.showPage()
    c.save()

poppler_path = Path(scriptPath, "bin")
tmpFolder = Path(scriptPath, "tmpBarcodesWB")
try:
    os.makedirs(tmpFolder)
except OSError:
    print ("Создать директорию %s не удалось" % tmpFolder)
else:
    print ("Успешно создана директория %s" % tmpFolder)
   
images_of_pdf = convert_from_path(inFile, dpi=150, poppler_path=poppler_path, grayscale=True, output_folder=tmpFolder)
barcodes = []
for image in images_of_pdf:
    barcodes = barcodes + pyzbar.decode(image)
    image.close()
   
print (str(len(barcodes)) + " barcodes detected!")

# loop over the detected barcodes
bar_code128_List = []
for barcode in barcodes:
    barcodeType = barcode.type
    if barcodeType == "CODE128":
        bar_code128_List.append(barcode.data.decode("utf-8"))
       
bar_code128_List = list(set(bar_code128_List))
bar_code128_List.sort()
new_splitFile = str(Path(workFolder, f"{71}x{48}_{inFileName}{extFile}"))
print ("Out file path: " + new_splitFile)
createBarCodes(bar_code128_List, new_splitFile)

clearTempFolder(tmpFolder)

try:
    os.rmdir(tmpFolder)
except OSError:
    print ("Удалить директорию %s не удалось" % tmpFolder)
else:
    print ("Успешно удалена директория %s" % tmpFolder)