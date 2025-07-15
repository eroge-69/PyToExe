import pandas as pd
import ezdxf

# 读取Excel文件
file_path = '/home/ubuntu/upload/材料清单.xlsx'
df = pd.read_excel(file_path)

# 遍历每一行数据，生成DXF文件
for index, row in df.iterrows():
    partmark = row["PARTMARK"]
    length = row["LENGTH"]
    width = row["WIDTH"]

    # 创建新的DXF文档
    doc = ezdxf.new("R2010")  # 使用AutoCAD 2010格式
    msp = doc.modelspace()

    # 绘制矩形
    # 矩形的四个角点 (x, y)
    points = [
        (0, 0),
        (length, 0),
        (length, width),
        (0, width),
        (0, 0)  # 闭合矩形
    ]
    msp.add_lwpolyline(points)

    # 保存DXF文件
    file_name = f"{partmark}.dxf"
    doc.saveas(file_name)
    print(f"Generated {file_name}")


