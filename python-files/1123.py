
import os

import PyPDF2

def add_watermark(input_pdf_path, output_pdf_path, watermark_pdf_path):

with open (input_pdf_path, 'rb') as input_pdf:

pdf_reader PyPDF2.PdfReader (input_pdf)

pdf_writer PyPDF2.PdfWriter()

watermark_pdf = PyPDF2.PdfReader (watermark_pdf_path)

watermark_page = watermark_pdf.pages [0]

for page_num in range (len(pdf_reader.pages)):

page pdf_reader.pages [page_num]

page.merge_page (watermark_page)

pdf_writer.add_page(page)

with open (output_pdf_path, 'wb') as output_pdf:

pdf_writer.write(output_pdf)

if_name_== "_main_":

input_folder = r"D:\User123"

output_folder = r"D:\User123"

watermark_pdf_path = r"D:\User123\pooja.pdf"

#Create the output folder if it doesn't exist

if not os.path.exists(output_folder):

os.makedirs (output_folder)

#Iterate through all PDF files in the input folder

for file_name in os.listdir (input_folder):

if file name.endswith(".pdf"):

input_pdf_path = os.path.join(input_folder, file_name)

output_pdf_path = os.path.join(output_folder, file_name)

add_watermark (input_pdf_path, output_pdf_path, watermark_pdf_path)