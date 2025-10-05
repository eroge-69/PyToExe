import numpy as np

def main():
    # 生成一个 5x5 的随机矩阵
    mat = np.random.rand(5, 5)
    print("原始矩阵:")
    print(mat)

    # 计算矩阵的逆
    try:
        inv = np.linalg.inv(mat)
        print("\n矩阵的逆:")
        print(inv)

        # 验证 A * A^-1 是否接近单位矩阵
        identity = np.dot(mat, inv)
        print("\nA * A^-1 ≈ 单位矩阵:")
        print(identity)
    except np.linalg.LinAlgError:
        print("矩阵不可逆")

if __name__ == "__main__":
    main()
