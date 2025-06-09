import numpy as np
from sympy import Matrix

print("矩陣列簡化梯形矩陣")

# 輸入
rows = int(input("列數(Row): "))
cols = int(input("行數(Cloumn): "))

matrix = []
for i in range(rows):
    row = []
    for j in range(cols):
        num = float(input(f"[{i+1},{j+1}]: "))
        row.append(num)
    matrix.append(row)

# 顯示原始矩陣
print("\n原始矩陣:")
for row in matrix:
    print(row)

# 計算並顯示結果
rref = Matrix(matrix).rref()[0]
result = np.array(rref.tolist()).astype(float)


print("\n列簡化梯形矩陣:")
for row in result:
    print(row)
