# process_test_data.py
# 移除外部模組依賴，使用內建函式以確保在有限制的線上編譯器可執行

def flush_queues(outfile, coord_q, val_qs, nums):
    # 檢查各佇列長度是否一致
    N = len(coord_q)
    for num in nums:
        if len(val_qs[num]) != N:
            print(f"Error: number mismatch for '{num}' (expected {N}, got {len(val_qs[num])})")
            exit(1)
    # 輸出到檔案
    try:
        with open(outfile, 'a') as fo:
            for i in range(N):
                coord = coord_q[i]
                values = [val_qs[num][i] for num in nums]
                fo.write(f"{coord} {' '.join(values)}\n")
    except Exception as e:
        print(f"Error writing to output file: {e}")
        exit(1)
    # 清空佇列
    coord_q.clear()
    for num in nums:
        val_qs[num].clear()


def main():
    # 1. 讀取使用者輸入
    infile = input("Enter input filename (with extension): ").strip()
    nums = input("Enter number strings separated by space: ").split()
    outfile = infile + "_out"

    # 寫入標頭
    header = "Coordinate " + " ".join(nums)
    try:
        with open(outfile, 'w') as fo:
            fo.write(header + "\n")
    except Exception as e:
        print(f"Error creating output file: {e}")
        exit(1)

    # 初始化佇列
    coord_queue = []
    value_queues = {num: [] for num in nums}
    value_ordinal = None

    # 2. 讀取並處理檔案
    try:
        with open(infile, 'r') as fi:
            lines = fi.read().splitlines()
    except Exception:
        print(f"Error: input file '{infile}' not found.")
        exit(1)

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
                    if len(nxt) >= 2 and nxt[-1].lstrip('-').isdigit() and nxt[-2].lstrip('-').isdigit():
                        x, y = nxt[-2], nxt[-1]
                        coord_queue.append(f"{x} {y}")
                    i += 1
                else:
                    break
            continue

        elif first.startswith("Test#"):
            if "Value" in tokens:
                value_ordinal = tokens.index("Value")
            i += 1
            continue

        elif first in nums:
            if value_ordinal is None:
                print("Error: 'Value' column not defined before data lines.")
                exit(1)
            if len(tokens) > value_ordinal:
                value_queues[first].append(tokens[value_ordinal])
            i += 1
            continue

        else:
            i += 1

    # 檔案結尾後 flush
    if coord_queue:
        flush_queues(outfile, coord_queue, value_queues, nums)

    print("finish")

if __name__ == "__main__":
    main()
