import sys


def find_solutions(A, B, C, T, D, max_error_threshold=0.05, max_solutions=10):
    """
    查找满足方程的整数解

    参数:
    A, B, C - 方程系数
    T - 目标值
    D - XYZ最大允许差值
    max_error_threshold - 最大允许误差阈值
    max_solutions - 需要找到的解的数量

    返回:
    按误差排序的解列表
    """
    # 将系数转换为整数形式（避免浮点误差）
    scale = 100
    A_int = int(round(A * scale))
    B_int = int(round(B * scale))
    C_int = int(round(C * scale))
    T_int = int(round(T * scale))

    # 计算中心值
    k0 = T / (A + B + C)

    # 确定搜索范围（对称扩展）
    min_val = int(max(0, k0 - 3 * D))  # 最小值不小于0
    max_val = int(k0 + 3 * D)

    solutions = []
    found_count = 0

    # 先搜索0.00误差的解
    current_error = 0.0
    max_error_int = int(max_error_threshold * scale)

    # 按误差层级搜索：0.00 -> 0.01 -> 0.02 ... 直到max_error_threshold
    while current_error <= max_error_threshold and found_count < max_solutions:
        current_error_int = int(round(current_error * scale))

        for X in range(min_val, max_val + 1):
            # Y的范围限制：在[X-D, X+D]之内
            y_min = max(min_val, X - D)
            y_max = min(max_val, X + D)

            for Y in range(y_min, y_max + 1):
                # 计算剩余部分
                remaining = T_int - (A_int * X + B_int * Y)

                # 计算Z的理想值并取整
                if C_int != 0:  # 避免除零错误
                    Z_float = remaining / C_int
                    Z = round(Z_float)
                    # 检查Z是否在有效范围内
                    if abs(X - Z) > D or abs(Y - Z) > D:
                        continue

                    # 计算实际值
                    total = A_int * X + B_int * Y + C_int * Z
                    error_abs = abs(total - T_int)

                    # 检查是否满足当前误差层级
                    if error_abs <= current_error_int:
                        actual_error = error_abs / scale
                        solution = (X, Y, Z, actual_error)

                        # 添加到解集（避免重复）
                        if solution not in solutions:
                            solutions.append(solution)
                            found_count += 1

                            # 提前终止：找到足够数量的0误差解
                            if actual_error == 0.0 and found_count >= max_solutions:
                                return solutions[:max_solutions]

        # 当前误差级没有找到足够解，提高误差阈值
        current_error += 0.01
        # 确保不会超过最大误差阈值
        current_error = min(current_error, max_error_threshold)

    # 按误差排序后返回
    solutions.sort(key=lambda x: x[3])
    return solutions[:max_solutions]


def main():
    print("方程求解器: A*X + B*Y + C*Z = T")
    print("请按顺序输入以下参数（用空格分隔）:")
    print("A B C T D [最大误差阈值] [需要解的数量]")
    print("示例: 12.3 9.27 3.85 82238 500 0.05 10")

    try:
        data = input("请输入参数: ").split()
        if len(data) < 5:
            raise ValueError("输入参数不足")

        # 解析基础参数
        A = float(data[0])
        B = float(data[1])
        C = float(data[2])
        T = float(data[3])
        D = int(data[4])

        # 解析可选参数
        max_error = 0.05 if len(data) < 6 else float(data[5])
        max_solutions = 10 if len(data) < 7 else int(data[6])

        # 查找解
        solutions = find_solutions(A, B, C, T, D, max_error, max_solutions)

        # 输出结果
        print(f"\n找到 {len(solutions)} 个解:")
        print("X".ljust(8), "Y".ljust(8), "Z".ljust(8), "误差")
        for X, Y, Z, err in solutions:
            print(f"{X:<8}{Y:<8}{Z:<8}{err:.4f}")

    except Exception as e:
        print(f"错误: {e}")
        print("请按格式输入: A B C T D [最大误差阈值] [需要解的数量]")
        print("示例: 12.3 9.27 3.85 82238 500 0.05 10")


if __name__ == "__main__":
    main()