# %%
def calc_par(d, par_pos_l):
    p = 0
    for pos in par_pos_l:
        p ^= d[pos - 1]
    return p

# %%
def gen_cword(data_w):
    n = len(data_w)
    if n != 11:
        raise ValueError("Data word must be 11 bits long.")

    r = 0
    while (2**r) < (n + r + 1):
        r += 1

    cword = [0] * (n + r)

    j = 0
    k = 0
    for i in range(1, n + r + 1):
        if i & (i - 1) != 0:
            cword[i - 1] = data_w[j]
            j += 1
        else:
            k += 1

    for i in range(r):
        p_pos = 2**i
        p_pos_l = []
        for j in range(1, n + r + 1):
            if j & p_pos != 0:
                p_pos_l.append(j)
        cword[p_pos - 1] = calc_par(cword, p_pos_l)

    return cword

# %%
def corrupt_b(cword, corrupted_p):
    corrupted_cword = list(cword)
    corrupted_cword[corrupted_p - 1] ^= 1
    return corrupted_cword

# %%
def detect_and_correct_err(corrupted_d):
    tot_bits = len(corrupted_d)
    par_bits_cnt = 0
    while (2**par_bits_cnt) < (tot_bits + 1):
        par_bits_cnt += 1

    synd = 0
    for i in range(par_bits_cnt):
        par_pos = 2**i
        pos_to_chk = []
        for j in range(1, tot_bits + 1):
            if j & par_pos != 0:
                pos_to_chk.append(j)
        calculated_par = calc_par(corrupted_d, pos_to_chk)
        synd |= (calculated_par << i)

    if synd == 0:
        print("No error detected.")
        return corrupted_d
    else:
        print(f"Error detected at position {synd}.")
        corrected_d = list(corrupted_d)
        corrected_d[synd - 1] ^= 1
        print(f"Corrected data: {corrected_d}")
        return corrected_d

# %%
while True:
    data_s = input("Enter an 11-bit data word (e.g:10110010110): ")
    try:
        data_l = [int(bit) for bit in data_s]
        if len(data_l) == 11 and all(bit in [0, 1] for bit in data_l):
            break
        else:
            print("Invalid input. Please enter exactly 11 bits (0 or 1).")
    except ValueError:
        print("Invalid input. Please enter only 0s and 1s.")

cword = gen_cword(data_l)
print(f"Original data word: {data_l}")
print(f"Generated codeword: {cword}")

while True:
    try:
        err_p = int(input(f"Enter the position to corrupt (1 to {len(cword)}): "))
        if 1 <= err_p <= len(cword):
            break
        else:
            print(f"Invalid input. Please enter a position between 1 and {len(cword)}.")
    except ValueError:
        print("Invalid input. Please enter a number.")

corrupted_c = corrupt_b(cword, err_p)
corrected_c = detect_and_correct_err(corrupted_c)


