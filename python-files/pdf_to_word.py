import os
import sys
import argparse
from pdf2docx import Converter
from concurrent.futures import ThreadPoolExecutor
import time

def convert_pdf_to_word(pdf_file, output_file):
    """转换单个PDF文件为Word文件"""
    try:
        print(f"正在转换: {os.path.basename(pdf_file)}")
        cv = Converter(pdf_file)
        cv.convert(output_file)
        cv.close()
        return True
    except Exception as e:
        print(f"转换 {pdf_file} 时出错: {str(e)}")
        return False

def batch_convert_pdfs(input_folder, output_folder, max_workers=None):
    """批量转换文件夹中的所有PDF文件为Word文件"""
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # 获取所有PDF文件
    pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("输入文件夹中没有找到PDF文件！")
        return
    
    total_files = len(pdf_files)
    print(f"找到 {total_files} 个PDF文件，开始转换...")
    
    # 记录开始时间
    start_time = time.time()
    
    # 转换计数器
    success_count = 0
    
    # 确定worker数量
    if max_workers is None:
        max_workers = min(os.cpu_count(), 4)
    
    # 使用线程池进行并行转换
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(input_folder, pdf_file)
            # 将输出文件名更改为.docx后缀
            output_filename = os.path.splitext(pdf_file)[0] + ".docx"
            output_path = os.path.join(output_folder, output_filename)
            
            # 提交转换任务到线程池
            future = executor.submit(convert_pdf_to_word, pdf_path, output_path)
            futures.append((future, pdf_file))
        
        # 处理转换结果
        for i, (future, pdf_file) in enumerate(futures):
            result = future.result()
            if result:
                success_count += 1
            
            # 打印进度
            print(f"进度: {i+1}/{total_files} ({(i+1)/total_files*100:.1f}%)")
    
    # 计算总耗时
    elapsed_time = time.time() - start_time
    
    # 显示完成消息
    print(f"\n转换完成！")
    print(f"成功转换: {success_count}/{total_files} 文件")
    print(f"耗时: {elapsed_time:.2f} 秒")

def main():
    # 检查必要的库是否已安装
    try:
        import pdf2docx
    except ImportError:
        print("缺少必要的库。正在尝试安装pdf2docx...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pdf2docx"])
        print("安装完成！")
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="批量将PDF文件转换为Word文件")
    parser.add_argument("input_folder", help="包含PDF文件的文件夹路径")
    parser.add_argument("output_folder", help="存储转换后Word文件的文件夹路径")
    parser.add_argument("-w", "--workers", type=int, default=None, 
                        help="并行处理的线程数 (默认为CPU核心数和4的较小值)")
    
    args = parser.parse_args()
    
    # 执行批量转换
    batch_convert_pdfs(args.input_folder, args.output_folder, args.workers)

# if __name__ == "__main__":
#     main()
    
if __name__ == "__main__":
    # 直接指定路径，无需命令行参数
    input_folder = "/mnt/c/users/Administrator/Downloads/SOP"  # 修改为你的PDF文件夹路径
    output_folder = "/mnt/c/users/Administrator/Downloads/SOP2"  # 修改为你的输出文件夹路径
    
    # 执行批量转换
    batch_convert_pdfs(input_folder, output_folder)