import sys
from PyPDF2 import PdfReader, PdfWriter, Transformation

def process_pdf(input_pdf, output_pdf):
    reader = PdfReader(input_pdf)
    num_pages = len(reader.pages)
    half = num_pages // 2   # половина од страниците

    writer = PdfWriter()

    # A4 димензии (points)
    a4_width, a4_height = (595.27, 841.89)
    a5_height = a4_height / 2

    for i in range(half):
        # Нова празна А4 страница
        new_page = writer.add_blank_page(width=a4_width, height=a4_height)

        # --- Горна половина ---
        page1 = reader.pages[i]
        w1, h1 = page1.mediabox.width, page1.mediabox.height
        scale1 = min(a4_width / w1, a5_height / h1)  # пропорционално намалување
        tx1 = (a4_width - w1 * scale1) / 2
        ty1 = a5_height + (a5_height - h1 * scale1) / 2
        t1 = Transformation().scale(scale1, scale1).translate(tx1, ty1)
        page1.add_transformation(t1)
        new_page.merge_page(page1)

        # --- Долна половина ---
        page2 = reader.pages[i + half]
        w2, h2 = page2.mediabox.width, page2.mediabox.height
        scale2 = min(a4_width / w2, a5_height / h2)
        tx2 = (a4_width - w2 * scale2) / 2
        ty2 = (a5_height - h2 * scale2) / 2
        t2 = Transformation().scale(scale2, scale2).translate(tx2, ty2)
        page2.add_transformation(t2)
        new_page.merge_page(page2)

    # Запиши во нов PDF
    with open(output_pdf, "wb") as f_out:
        writer.write(f_out)

    print(f"✅ Готово! Новиот PDF е снимен како: {output_pdf}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("❌ Употреба: python process_pdf.py input.pdf output.pdf")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    process_pdf(input_file, output_file)