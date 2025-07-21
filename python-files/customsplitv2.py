from PyPDF2 import PdfReader, PdfWriter, PageObject
from tkinter import *
from tkinter.filedialog import askopenfilename
import os.path as pd
import os

r = Tk()
r.title("PDF Split")
r.geometry("810x300")
r.resizable(False, False)



l2 = Label(r, text="Select PDF File: ")
l2.grid(row=1, column=0, sticky="w", padx=10)

tb1 = Entry(r, width=90)
tb1.grid(row=1, column=1, ipadx=5, ipady=5)

fd = "" # Global variable to store the file path

# Define a default output directory
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "Output")

# Define the fixed height for the top half in inches
TOP_HALF_HEIGHT_INCHES = 5.5
# Convert inches to PDF points (1 inch = 72 points)
INCHES_TO_POINTS = 72
TOP_HALF_HEIGHT_POINTS = TOP_HALF_HEIGHT_INCHES * INCHES_TO_POINTS

def showPDF():
    global fd
    fd = askopenfilename(title="Open PDF File", filetypes=[("PDF Files", "*.pdf")])
    if fd:
        tb1.delete(0, END)
        tb1.insert(0, fd)

        try:
            with open(fd, "rb") as file:
                reader = PdfReader(file)
                totalpages = len(reader.pages)
                tb2.delete(0, END)
                tb2.insert(0, totalpages)
        except Exception as e:
            tb2.delete(0, END)
            tb2.insert(0, f"Error: {e}")
            print(f"Error reading PDF: {e}")
    else:
        tb1.delete(0, END)
        tb2.delete(0, END)

b1 = Button(r, text="Browse PDF", bg="red", fg="white", command=showPDF, width=15)
b1.grid(row=1, column=2, ipadx=5, ipady=5, padx=5)




def cropAndSplitTask():
    j=1
    global fd
    if not fd:
        print("Please select a PDF file first.")
        return

    try:
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        print(f"Output files will be saved to: {output_dir}")

        # Get the base name of the original PDF file without extension
        original_filename_base = os.path.splitext(os.path.basename(fd))[0]

        with open(fd, "rb") as fp:
            reader = PdfReader(fp)
            total_pdf_pages = len(reader.pages)

            

            for i in range(total_pdf_pages):
                original_page = reader.pages[i] # Get the current page (0-indexed)

                # Get the original dimensions of the page
                # PyPDF2 3.x uses float values for coordinates
                left = float(original_page.cropbox.left)
                bottom = float(original_page.cropbox.bottom)
                right = float(original_page.cropbox.right)
                top = float(original_page.cropbox.top)
                page_height = top - bottom

                # Calculate the cutting line for the top half
                # This is the 'bottom' coordinate for the top half's cropbox
                # and the 'top' coordinate for the bottom half's cropbox
                top_crop_line = top - TOP_HALF_HEIGHT_POINTS 

                # Ensure top_crop_line doesn't go below the actual bottom of the page
                # If the page is shorter than TOP_HALF_HEIGHT_INCHES, the top half will be the entire page.
                adjusted_top_crop_line = max(bottom, top_crop_line)

                # --- Create Top Half ---
                writer_top = PdfWriter()
                writer_top.add_page(original_page) # Add the original page
                page_in_writer_top = writer_top.pages[0] # Get reference to the page in the writer

                # Set the CropBox for the top half
                page_in_writer_top.cropbox.lower_left = (left, adjusted_top_crop_line)
                page_in_writer_top.cropbox.upper_right = (right, top)

                output_filename_top = os.path.join(output_dir, f"{original_filename_base}_{j}.pdf")
                with open(output_filename_top, "wb") as nf_top:
                    writer_top.write(nf_top)
                print(f"Created: {output_filename_top}")
                j+=1

                # --- Create Bottom Half ---
                writer_bottom = PdfWriter()
                writer_bottom.add_page(original_page) # Add the original page
                page_in_writer_bottom = writer_bottom.pages[0] # Get reference to the page in the writer

                # Set the CropBox for the bottom half
                # The top boundary of the bottom half is the adjusted_top_crop_line
                page_in_writer_bottom.cropbox.lower_left = (left, bottom)
                page_in_writer_bottom.cropbox.upper_right = (right, adjusted_top_crop_line-15)

                output_filename_bottom = os.path.join(output_dir, f"{original_filename_base}_{j}.pdf")
                with open(output_filename_bottom, "wb") as nf_bottom:
                    writer_bottom.write(nf_bottom)
                print(f"Created: {output_filename_bottom}")
                j+=1
            print(f"\nPDF horizontal cropping and splitting completed successfully..")

    except Exception as e:
        print(f"An error occurred during cropping and splitting: {e}")


b2 = Button(r, text=f"Split PDF ", bg="green", fg="white", width=35, command=cropAndSplitTask)
b2.grid(row=4, column=1, ipadx=5, ipady=5, pady=5)

def clearUI():
    tb1.delete(0, END)
    tb2.delete(0, END)
    global fd
    fd = ""

ct = Button(r, text="Clear", bg="gray", fg="white", width=15, command=clearUI)
ct.grid(row=5, column=1, ipadx=5, ipady=5, pady=5)

r.mainloop()
