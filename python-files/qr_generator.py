#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
二维码批量生成器
支持从文本文件、CSV文件或直接输入内容来批量生成二维码
"""

import qrcode
import os
import csv
from PIL import Image
from typing import List, Optional
import argparse


class QRCodeGenerator:
    """二维码生成器类"""
    
    def __init__(self, output_dir: str = "qr_codes"):
        """
        初始化二维码生成器
        
        Args:
            output_dir: 输出目录，默认为 "qr_codes"
        """
        self.output_dir = output_dir
        self.ensure_output_dir()
    
    def ensure_output_dir(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"创建输出目录: {self.output_dir}")
    
    def generate_single_qr(self, content: str, filename: str, 
                          error_correction: int = qrcode.constants.ERROR_CORRECT_M,
                          box_size: int = 10, border: int = 4) -> bool:
        """
        生成单个二维码
        
        Args:
            content: 二维码内容
            filename: 输出文件名（不含扩展名）
            error_correction: 错误纠正级别
            box_size: 每个小方块的像素数
            border: 边框大小
            
        Returns:
            生成成功返回True，失败返回False
        """
        try:
            # 创建二维码实例
            qr = qrcode.QRCode(
                version=1,  # 控制二维码大小，1-40
                error_correction=error_correction,
                box_size=box_size,
                border=border,
            )
            
            # 添加数据
            qr.add_data(content)
            qr.make(fit=True)
            
            # 创建图像
            img = qr.make_image(fill_color="black", back_color="white")
            
            # 保存图像
            filepath = os.path.join(self.output_dir, f"{filename}.png")
            img.save(filepath)
            print(f"生成二维码: {filepath}")
            return True
            
        except Exception as e:
            print(f"生成二维码失败 {filename}: {str(e)}")
            return False
    
    def batch_from_list(self, content_list: List[str], 
                       filename_prefix: str = "qr") -> int:
        """
        从列表批量生成二维码
        
        Args:
            content_list: 内容列表
            filename_prefix: 文件名前缀
            
        Returns:
            成功生成的数量
        """
        success_count = 0
        total = len(content_list)
        
        print(f"开始批量生成 {total} 个二维码...")
        
        for i, content in enumerate(content_list, 1):
            if content.strip():  # 跳过空内容
                filename = f"{filename_prefix}_{i:03d}"
                if self.generate_single_qr(content.strip(), filename):
                    success_count += 1
        
        print(f"批量生成完成！成功: {success_count}/{total}")
        return success_count
    
    def batch_from_file(self, filepath: str, 
                       filename_prefix: str = "qr") -> int:
        """
        从文本文件批量生成二维码（每行一个内容）
        
        Args:
            filepath: 文本文件路径
            filename_prefix: 文件名前缀
            
        Returns:
            成功生成的数量
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content_list = f.readlines()
            
            # 去除换行符
            content_list = [line.strip() for line in content_list if line.strip()]
            
            return self.batch_from_list(content_list, filename_prefix)
            
        except Exception as e:
            print(f"读取文件失败: {str(e)}")
            return 0
    
    def batch_from_csv(self, csv_filepath: str, content_column: str = "content",
                      name_column: Optional[str] = None) -> int:
        """
        从CSV文件批量生成二维码
        
        Args:
            csv_filepath: CSV文件路径
            content_column: 内容列名
            name_column: 文件名列名（可选，如果不指定则使用序号）
            
        Returns:
            成功生成的数量
        """
        try:
            success_count = 0
            
            with open(csv_filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for i, row in enumerate(reader, 1):
                    content = row.get(content_column, "").strip()
                    if content:
                        if name_column and row.get(name_column):
                            filename = row[name_column].strip()
                        else:
                            filename = f"qr_{i:03d}"
                        
                        if self.generate_single_qr(content, filename):
                            success_count += 1
            
            print(f"从CSV批量生成完成！成功: {success_count} 个")
            return success_count
            
        except Exception as e:
            print(f"读取CSV文件失败: {str(e)}")
            return 0


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="批量生成二维码")
    parser.add_argument("-o", "--output", default="qr_codes", 
                       help="输出目录 (默认: qr_codes)")
    parser.add_argument("-f", "--file", 
                       help="从文本文件读取内容（每行一个）")
    parser.add_argument("-c", "--csv", 
                       help="从CSV文件读取内容")
    parser.add_argument("--content-column", default="content",
                       help="CSV文件中的内容列名 (默认: content)")
    parser.add_argument("--name-column",
                       help="CSV文件中的文件名列名（可选）")
    parser.add_argument("-t", "--text", nargs="+",
                       help="直接指定要生成的文本内容")
    parser.add_argument("-p", "--prefix", default="qr",
                       help="文件名前缀 (默认: qr)")
    
    args = parser.parse_args()
    
    # 创建生成器
    generator = QRCodeGenerator(args.output)
    
    if args.csv:
        # 从CSV文件生成
        generator.batch_from_csv(args.csv, args.content_column, args.name_column)
    elif args.file:
        # 从文本文件生成
        generator.batch_from_file(args.file, args.prefix)
    elif args.text:
        # 从命令行参数生成
        generator.batch_from_list(args.text, args.prefix)
    else:
        # 交互模式
        print("=== 二维码批量生成器 ===")
        print("请选择输入方式:")
        print("1. 直接输入内容（输入空行结束）")
        print("2. 从文本文件读取")
        print("3. 从CSV文件读取")
        
        choice = input("请选择 (1-3): ").strip()
        
        if choice == "1":
            print("请输入要生成二维码的内容（每行一个，输入空行结束）:")
            content_list = []
            while True:
                line = input().strip()
                if not line:
                    break
                content_list.append(line)
            
            if content_list:
                generator.batch_from_list(content_list)
            else:
                print("没有输入任何内容！")
                
        elif choice == "2":
            filepath = input("请输入文本文件路径: ").strip()
            generator.batch_from_file(filepath)
            
        elif choice == "3":
            csv_path = input("请输入CSV文件路径: ").strip()
            content_col = input("内容列名 (默认: content): ").strip() or "content"
            name_col = input("文件名列名 (可选，直接回车跳过): ").strip() or None
            generator.batch_from_csv(csv_path, content_col, name_col)
            
        else:
            print("无效选择！")


if __name__ == "__main__":
    main()