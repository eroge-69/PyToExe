import os
from pdf2image import convert_from_path

def pdf_to_images(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_folder, filename)
            pdf_name = os.path.splitext(filename)[0]

            # Convert PDF pages to images
            pages = convert_from_path(pdf_path, dpi=300)

            for i, page in enumerate(pages, start=1):
                output_path = os.path.join(output_folder, f"{pdf_name} - {i}.png")
                page.save(output_path, "PNG")

            print(f"✅ Extracted {len(pages)} pages from {filename}")

if __name__ == "__main__":
    input_folder = os.getcwd()
    output_folder = os.path.join(input_folder, "output_images")

    print(f"🔍 Scanning for PDFs in: {input_folder}")
    pdf_to_images(input_folder, output_folder)

    print(f"\n✅ Done! All PDFs in the current directory converted to images.")
    print(f"🗂️ Images saved in: {output_folder}")
    input("Press Enter to exit...")
