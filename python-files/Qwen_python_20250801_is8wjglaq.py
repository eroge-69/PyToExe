import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import openpyxl
from datetime import datetime
import os

class LogisticsProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("物流数据处理工具")
        self.root.geometry("600x500")
        
        # 文件路径变量
        self.file_path = tk.StringVar()
        
        self.create_widgets()
    
    def create_widgets(self):
        # 标题
        title_label = tk.Label(self.root, text="物流数据处理工具", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # 文件选择框架
        file_frame = tk.Frame(self.root)
        file_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(file_frame, text="选择文件:").pack(anchor="w")
        
        file_entry_frame = tk.Frame(file_frame)
        file_entry_frame.pack(fill="x", pady=5)
        
        self.file_entry = tk.Entry(file_entry_frame, textvariable=self.file_path, 
                                  width=50, state="readonly")
        self.file_entry.pack(side="left", fill="x", expand=True)
        
        browse_btn = tk.Button(file_entry_frame, text="浏览", command=self.browse_file)
        browse_btn.pack(side="right", padx=(5, 0))
        
        # 处理按钮
        process_btn = tk.Button(self.root, text="开始处理", command=self.process_data,
                               bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                               height=2, width=20)
        process_btn.pack(pady=30)
        
        # 进度条
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(pady=10, padx=20, fill="x")
        
        # 状态标签
        self.status_label = tk.Label(self.root, text="", fg="blue")
        self.status_label.pack(pady=10)
        
        # 说明文本
        info_text = """
功能说明：
1. 选择物流发货Excel文件
2. 自动处理生成4个不同格式的报表
3. 输出合并后的Excel文件到同一目录
4. 支持自动按当前日期命名文件
5. 自动剔除货物名称为"回单"的数据

注意事项：
- 确保Excel文件包含所需列名
- 处理完成后会在同目录生成结果文件
        """
        
        info_label = tk.Label(self.root, text=info_text, justify="left", 
                             font=("Arial", 9), fg="gray")
        info_label.pack(pady=20, padx=20, anchor="w")
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="选择物流发货文件",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if filename:
            self.file_path.set(filename)
            self.status_label.config(text=f"已选择文件: {os.path.basename(filename)}")
    
    def process_data(self):
        if not self.file_path.get():
            messagebox.showerror("错误", "请先选择文件！")
            return
        
        try:
            # 显示处理中
            self.status_label.config(text="正在处理数据...", fg="orange")
            self.progress.start()
            self.root.update()
            
            # 执行处理
            self.do_process()
            
            # 完成
            self.progress.stop()
            self.status_label.config(text="处理完成！", fg="green")
            messagebox.showinfo("成功", f"文件处理完成！\n输出文件已保存到原文件目录")
            
        except Exception as e:
            self.progress.stop()
            self.status_label.config(text="处理失败", fg="red")
            messagebox.showerror("错误", f"处理过程中出现错误：\n{str(e)}")
    
    def do_process(self):
        # 读取文件
        input_file = self.file_path.get()
        df = pd.read_excel(input_file)
        
        # 剔除货物名称为"回单"的行数据
        df = df[df['货物名称'] != '回单']
        
        # 获取文件目录和基础文件名
        file_dir = os.path.dirname(input_file)
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        
        # 获取当前日期
        today = datetime.today().strftime('%Y-%m-%d')
        
        # 1. 第一份表：业务表
        columns_1 = ['寄件日期', '运单号', '寄件公司', '寄件客户姓名', '(派件)省', '(派件)市',
                     '收件客户姓名', '货物名称', '总件数', '计费重量', '运输费', '支付方式',
                     '成本合计', '实际重量']
        df1 = df[columns_1]
        
        # 2. 第二份表：发货明细
        columns_2 = ['寄件日期', '运单号', '寄件客户姓名', '收件客户姓名', '货物名称',
                     '包装类型', '总件数', '计费重量', '实际重量', '寄件公司', '派件网点',
                     '寄件网点', '现付', '到付', '月结', '成本合计']
        
        df2 = df[columns_2].copy()
        
        # 计算合计
        sum_row = {col: '' for col in columns_2}
        sum_row['计费重量'] = df2['计费重量'].sum()
        sum_row['成本合计'] = df2['成本合计'].sum()
        
        # 添加合计行
        df2 = pd.concat([df2, pd.DataFrame([sum_row])], ignore_index=True)
        
        # 3. 第三份表：加急明细表
        columns_3 = ['寄件日期', '运单号', '货物名称', '包装类型', '总件数', '计费重量',
                     '(派件)省', '(派件)市', '派件网点', '寄件网点', '体积']
        df3 = df[columns_3]
        
        # 4. 第四份表：校验表（多 sheet）
        # sheet1: 派件省为海南省，派件市为黄山市、宣城市、杭州市
        df_sheet1 = df[
            (df['(派件)省'] == '海南省') |
            (df['(派件)市'].isin(['黄山市', '宣城市', '杭州市']))
        ]
        
        # sheet2: 支付方式为到付
        df_sheet2 = df[df['支付方式'] == '到付']
        
        # sheet3: 提/送货方式为上楼（包含电梯或无电梯）
        df_sheet3 = df[df['提/送货方式'].str.contains('上楼', na=False)]
        
        # sheet4: 产品名称为重货特惠
        df_sheet4 = df[df['货物名称'] == '重货特惠']
        
        # 5. 合并所有 sheet 到一个 Excel 文件中
        final_output = os.path.join(file_dir, f'{today}物流处理结果.xlsx')
        
        with pd.ExcelWriter(final_output, engine='openpyxl') as writer:
            df1.to_excel(writer, index=False, sheet_name='业务表')
            df2.to_excel(writer, index=False, sheet_name='发货明细')
            
            # 格式化发货明细表
            worksheet = writer.sheets['发货明细']
            for col in worksheet.columns:
                for cell in col:
                    if isinstance(cell.value, (int, float)):
                        cell.alignment = openpyxl.styles.Alignment(horizontal='center')
            
            # 加粗红色合计行
            last_row = len(df2)
            for col_idx, col_name in enumerate(columns_2, 1):
                cell = worksheet.cell(row=last_row, column=col_idx)
                if col_name in ['计费重量', '成本合计']:
                    cell.font = openpyxl.styles.Font(bold=True, color="FF0000")
            
            df3.to_excel(writer, index=False, sheet_name='加急明细表')
            df_sheet1.to_excel(writer, index=False, sheet_name='校验_异常地址')
            df_sheet2.to_excel(writer, index=False, sheet_name='校验_到付')
            df_sheet3.to_excel(writer, index=False, sheet_name='校验_上楼')
            df_sheet4.to_excel(writer, index=False, sheet_name='校验_重货特惠')

def main():
    root = tk.Tk()
    app = LogisticsProcessor(root)
    root.mainloop()

if __name__ == "__main__":
    main()