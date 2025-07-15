import sys

def flush_queues(outfile, coord_q, val_qs, nums):
    # 檢查各佇列長度是否一致
    N = len(coord_q)
    for num in nums:
        if len(val_qs[num]) != N:
            print(f"Error: number mismatch for '{num}' (expected {N}, got {len(val_qs[num])})")
            sys.exit(1)
    # 輸出到檔案
    with open(outfile, 'a') as fo:
        for i in range(N):
            # coordinate 欄為 "x y"
            coord = coord_q[i]
            values = [val_qs[num][i] for num in nums]
            fo.write(f"{coord} {' '.join(values)}\n")
    # 清空佇列
    coord_q.clear()
    for num in nums:
        val_qs[num].clear()


def main():
    # 1. 讀取使用者輸入
    infile = input("Enter input filename (with extension): ").strip()
    nums = input("Enter number strings separated by space: ").split()
    # 輸出檔名
    outfile = infile + "_out"

    # 寫入標頭
    header = "Coordinate " + " ".join(nums)
    with open(outfile, 'w') as fo:
        fo.write(header + "\n")

    # 初始化佇列
    coord_queue = []
    value_queues = {num: [] for num in nums}
    value_ordinal = None

    # 2. 讀取並處理檔案
    try:
        with open(infile, 'r') as fi:
            lines = fi.readlines()
    except FileNotFoundError:
        print(f"Error: input file '{infile}' not found.")
        sys.exit(1)

    i = 0
    total_lines = len(lines)
    while i < total_lines:
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        tokens = line.split()
        first = tokens[0]

        if first == "Dut#":
            # flush 先前資料
            if coord_queue:
                flush_queues(outfile, coord_queue, value_queues, nums)
            # 處理座標區段
            i += 1
            while i < total_lines:
                nxt = lines[i].strip().split()
                if nxt and nxt[0].isdigit():
                    # 取最後兩個字做座標
                    if len(nxt) >= 2 and nxt[-1].lstrip('-').isdigit() and nxt[-2].lstrip('-').isdigit():
                        x, y = nxt[-2], nxt[-1]
                        coord_queue.append(f"{x} {y}")
                    # 否則略過此筆
                    i += 1
                else:
                    break
            continue

        elif first.startswith("Test#"):
            # 找到 Value 欄位置
            if "Value" in tokens:
                value_ordinal = tokens.index("Value")
            i += 1
            continue

        elif first in nums:
            # 確認已設定 value_ordinal
            if value_ordinal is None:
                print("Error: 'Value' column not defined before data lines.")
                sys.exit(1)
            # 取該行第 value_ordinal 字串
            if len(tokens) > value_ordinal:
                value_queues[first].append(tokens[value_ordinal])
            i += 1
            continue

        else:
            i += 1

    # 3. 檔案結尾後 flush
    if coord_queue:
        flush_queues(outfile, coord_queue, value_queues, nums)

    print("finish")


if __name__ == "__main__":
    main()
