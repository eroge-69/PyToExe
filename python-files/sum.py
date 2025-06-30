
def recursive_sum(start, end):
    if start > end:
        return 0
    return start + recursive_sum(start + 1, end)
    
def fast_sum(start, end):
    n = end - start + 1
    return (start + end) * n // 2


# 使用者輸入範圍
s = int(input("請輸入起始值: "))
e = int(input("請輸入結束值: "))

# 計算並輸出結果
total = fast_sum(s, e)
print(f"{s} 到 {e} 的加總為: {total}")

