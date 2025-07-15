import sys

def flush_queues(outfile, coord_q, val_qs, nums):

    N = len(coord_q)
    for num in nums:
        if len(val_qs[num]) != N:
            print(f"Error: number mismatch for '{num}' (expected {N}, got {len(val_qs[num])})")
            sys.exit(1)

    with open(outfile, 'a') as fo:
        for i in range(N):
            # coordinate 
            coord = coord_q[i]
            values = [val_qs[num][i] for num in nums]
            fo.write(f"{coord} {' '.join(values)}\n")

    coord_q.clear()
    for num in nums:
        val_qs[num].clear()


def main():

    infile = input("Enter input filename (with extension): ").strip()
    nums = input("Enter number strings separated by space: ").split()

    outfile = infile + "_out"


    header = "Coordinate " + " ".join(nums)
    with open(outfile, 'w') as fo:
        fo.write(header + "\n")


    coord_queue = []
    value_queues = {num: [] for num in nums}
    value_ordinal = None


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

            if coord_queue:
                flush_queues(outfile, coord_queue, value_queues, nums)

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
                sys.exit(1)

            if len(tokens) > value_ordinal:
                value_queues[first].append(tokens[value_ordinal])
            i += 1
            continue

        else:
            i += 1


    if coord_queue:
        flush_queues(outfile, coord_queue, value_queues, nums)

    print("finish")


if __name__ == "__main__":
    main()
