import os
import sys
from PyPDF2 import PdfMerger

def get_app_dir():
    # 打包后(sys.frozen为True)取exe所在目录；开发时取脚本目录
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def merge_pdfs_in_app_dir():
    app_dir = get_app_dir()
    output_file = os.path.join(app_dir, "merged.pdf")

    merger = PdfMerger()
    pdf_files = sorted([
        f for f in os.listdir(app_dir)
        if f.lower().endswith(".pdf") and f != "merged.pdf"
    ])

    if not pdf_files:
        print("当前目录下没有找到 PDF 文件")
        return

    for pdf in pdf_files:
        pdf_path = os.path.join(app_dir, pdf)
        print(f"正在添加: {pdf_path}")
        merger.append(pdf_path)

    merger.write(output_file)
    merger.close()
    print(f"✅ 合并完成！输出文件为: {output_file}")

if __name__ == "__main__":
    merge_pdfs_in_app_dir()
