# six_category_sum.py
def get_numbers(category_name):
    nums = []
    for i in range(1, 5):
        val = input(f"{category_name} 輸入第 {i} 個數字（空白視為 0）: ")
        try:
            num = float(val) if val.strip() != "" else 0
        except:
            print("輸入錯誤，視為 0")
            num = 0
        nums.append(num)
    return nums

def main():
    categories = ["來客數", "現金", "信用卡", "電子票證", "木盒底", "圓底"]
    totals = {}

    for cat in categories:
        nums = get_numbers(cat)
        totals[cat] = sum(nums)

    print("\n=== 各類別總和 ===")
    for cat in categories:
        print(f"{cat} 總和: {totals[cat]}")

if __name__ == "__main__":
    main()