from PIL import Image
from pix2tex.cli import LatexOCR
import sys

img = Image.open(sys.argv[1])
model = LatexOCR()
latex_code = model(img)
print(latex_code)