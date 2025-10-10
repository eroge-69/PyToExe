#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import secrets, sys
from typing import List, Optional, Tuple

# ---------------- Tabella Base-4 completa ----------------
_TABLE_BASE4_TEXT = """
0\t0000
1\t0004
2\t0008
3\t000C
4\t0040
5\t0044
6\t0048
7\t004C
8\t0080
9\t0084
10\t0088
11\t008C
12\t00C0
13\t00C4
14\t00C8
15\t00CC
16\t0400
17\t0404
18\t0408
19\t040C
20\t0440
21\t0444
22\t0448
23\t044C
24\t0480
25\t0484
26\t0488
27\t048C
28\t04C0
29\t04C4
30\t04C8
31\t04CC
32\t0800
33\t0804
34\t0808
35\t080C
36\t0840
37\t0844
38\t0848
39\t084C
40\t0880
41\t0884
42\t0888
43\t088C
44\t08C0
45\t08C4
46\t08C8
47\t08CC
48\t0C00
49\t0C04
50\t0C08
51\t0C0C
52\t0C40
53\t0C44
54\t0C48
55\t0C4C
56\t0C80
57\t0C84
58\t0C88
59\t0C8C
60\t0CC0
61\t0CC4
62\t0CC8
63\t0CCC
64\t4000
65\t4004
66\t4008
67\t400C
68\t4040
69\t4044
70\t4048
71\t404C
72\t4080
73\t4084
74\t4088
75\t408C
76\t40C0
77\t40C4
78\t40C8
79\t40CC
80\t4400
81\t4404
82\t4408
83\t440C
84\t4440
85\t4444
86\t4448
87\t444C
88\t4480
89\t4484
90\t4488
91\t448C
92\t44C0
93\t44C4
94\t44C8
95\t44CC
96\t4800
97\t4804
98\t4808
99\t480C
100\t4840
101\t4844
102\t4848
103\t484C
104\t4880
105\t4884
106\t4888
107\t488C
108\t48C0
109\t48C4
110\t48C8
111\t48CC
112\t4C00
113\t4C04
114\t4C08
115\t4C0C
116\t4C40
117\t4C44
118\t4C48
119\t4C4C
120\t4C80
121\t4C84
122\t4C88
123\t4C8C
124\t4CC0
125\t4CC4
126\t4CC8
127\t4CCC
128\t8000
129\t8004
130\t8008
131\t800C
132\t8040
133\t8044
134\t8048
135\t804C
136\t8080
137\t8084
138\t8088
139\t808C
140\t80C0
141\t80C4
142\t80C8
143\t80CC
144\t8400
145\t8404
146\t8408
147\t840C
148\t8440
149\t8444
150\t8448
151\t844C
152\t8480
153\t8484
154\t8488
155\t848C
156\t84C0
157\t84C4
158\t84C8
159\t84CC
160\t8800
161\t8804
162\t8808
163\t880C
164\t8840
165\t8844
166\t8848
167\t884C
168\t8880
169\t8884
170\t8888
171\t888C
172\t88C0
173\t88C4
174\t88C8
175\t88CC
176\t8C00
177\t8C04
178\t8C08
179\t8C0C
180\t8C40
181\t8C44
182\t8C48
183\t8C4C
184\t8C80
185\t8C84
186\t8C88
187\t8C8C
188\t8CC0
189\t8CC4
190\t8CC8
191\t8CCC
192\tC000
193\tC004
194\tC008
195\tC00C
196\tC040
197\tC044
198\tC048
199\tC04C
200\tC080
201\tC084
202\tC088
203\tC08C
204\tC0C0
205\tC0C4
206\tC0C8
207\tC0CC
208\tC400
209\tC404
210\tC408
211\tC40C
212\tC440
213\tC444
214\tC448
215\tC44C
216\tC480
217\tC484
218\tC488
219\tC48C
220\tC4C0
221\tC4C4
222\tC4C8
223\tC4CC
224\tC800
225\tC804
226\tC808
227\tC80C
228\tC840
229\tC844
230\tC848
231\tC84C
232\tC880
233\tC884
234\tC888
235\tC88C
236\tC8C0
237\tC8C4
238\tC8C8
239\tC8CC
240\tCC00
241\tCC04
242\tCC08
243\tCC0C
244\tCC40
245\tCC44
246\tCC48
247\tCC4C
248\tCC80
249\tCC84
250\tCC88
251\tCC8C
252\tCCC0
253\tCCC4
254\tCCC8
255\tCCCC
"""
def load_table(txt):
    t = {}
    for line in txt.strip().splitlines():
        parts = line.strip().split()
        if len(parts) >= 2:
            try:
                idx = int(parts[0])
                t[idx] = parts[1].upper().zfill(4)
            except:
                pass
    return t

_TABLE = load_table(_TABLE_BASE4_TEXT)

# ---------------- constants & weights ----------------
HI_WEIGHTS = [1<<14, 1<<12, 1<<10, 1<<8]   # 16384,4096,1024,256
LO_WEIGHTS = [1<<6, 1<<4, 1<<2, 1<<0]      # 64,16,4,1
GUIDE_WEIGHTS = [1<<12, 1<<8, 1<<4, 1<<0]  # 4096,256,16,1

# OPcount targets (nibble-sum targets)
TARGET_PRIMARY = 0xF7
TARGET_BACKUP  = 0xE7

# ---------------- helpers ----------------
def fmt_hex(arr: List[int]) -> str:
    return " ".join(f"{b:02X}" for b in arr)

def sum_nibbles(b: int) -> int:
    return ((b >> 4) & 0xF) + (b & 0xF)

def to_bcd_pair(n:int) -> int:
    return ((n//10)<<4) | (n%10)

def decompose_by_weights(value:int, weights:List[int]) -> Tuple[List[int], int]:
    digits = []
    rem = value
    for w in weights:
        d = rem // w
        digits.append(int(d))
        rem = rem % w
    return digits, rem

def to_base4_4digits(n:int) -> List[int]:
    n = n & 0xFF
    d0 = n // 64; r = n % 64
    d1 = r // 16; r = r % 16
    d2 = r // 4; d3 = r % 4
    return [d0, d1, d2, d3]

def idx_from_base4(digits:List[int]) -> int:
    return digits[0]*64 + digits[1]*16 + digits[2]*4 + digits[3]

def high_from_table(idx:int):
    code = _TABLE.get(idx)
    if code:
        return list(code[-4:]), code
    else:
        return list("8844"), None

def apply_backup_rule_high(primary_high_chars:List[str]) -> List[str]:
    hv = [int(x,16) for x in primary_high_chars]
    if hv[1] >= 4:
        hv[1] -= 4
    else:
        hv[1] = 0
    return [format(x,'X') for x in hv]

def make_bytes_from_high_nibbles(high_chars:List[str], nibs:List[int], or_first_0x80:bool=True) -> List[int]:
    out = []
    for i in range(4):
        h = int(high_chars[i], 16) if isinstance(high_chars[i], str) else int(high_chars[i])
        b = ((h & 0xF) << 4) | (nibs[i] & 0xF)
        if i == 0 and or_first_0x80:
            b = b | 0x80
        out.append(b & 0xFF)
    return out

def compute_nibs(value_cents:int) -> Tuple[List[int], List[int], List[int]]:
    rem = value_cents
    hi_digits = []
    for w in HI_WEIGHTS:
        d = rem // w
        hi_digits.append(int(d))
        rem = rem % w
    rem2 = rem
    lo_digits = []
    for w in LO_WEIGHTS:
        d = rem2 // w
        lo_digits.append(int(d))
        rem2 = rem2 % w
    nibs = [(hi_digits[i] << 2) | lo_digits[i] for i in range(4)]
    return hi_digits, lo_digits, nibs

# ---------------- core encoding for CREDIT ----------------
def generate_for_value(cents:int) -> dict:
    hi_digits, lo_digits, nibs = compute_nibs(cents)
    vd, _ = decompose_by_weights(cents, GUIDE_WEIGHTS)
    check = (59 - sum(vd)) & 0xFF
    base4 = to_base4_4digits(check)
    idx = idx_from_base4(base4)
    prim_high_chars, code = high_from_table(idx)
    primary_bytes = make_bytes_from_high_nibbles(prim_high_chars, nibs, or_first_0x80=True)
    backup_high_chars = apply_backup_rule_high(prim_high_chars)
    backup_bytes = make_bytes_from_high_nibbles(backup_high_chars, nibs, or_first_0x80=True)

    return {
        'cents': cents,
        'vd': vd,
        'check': check,
        'base4': base4,
        'idx': idx,
        'code': code,
        'primary_high_chars': prim_high_chars,
        'backup_high_chars': backup_high_chars,
        'primary_bytes': primary_bytes,
        'backup_bytes': backup_bytes,
        'nibs': nibs
    }

def previous_from_index_minus8(cur_res:dict) -> dict:
    idx_prev = (cur_res['idx'] - 8) & 0xFF
    prev_high_chars, prev_code = high_from_table(idx_prev)
    prev_primary = make_bytes_from_high_nibbles(prev_high_chars, cur_res['nibs'], or_first_0x80=True)
    prev_backup = make_bytes_from_high_nibbles(apply_backup_rule_high(prev_high_chars), cur_res['nibs'], or_first_0x80=True)
    return {
        'idx_prev': idx_prev,
        'code_prev': prev_code,
        'primary': prev_primary,
        'backup': prev_backup,
        'high_chars': prev_high_chars
    }

# ---------------- OPcount: nibble-first prefix selection (no arith fallback) ----------------
def find_all_prefixes_for_want(want:int) -> List[int]:
    res = []
    for P in range(256):
        if sum_nibbles(P) == want:
            res.append(P)
    return res

def choose_primary_prefix_nibble(data_bytes:List[int]) -> Optional[int]:
    s_data = sum(sum_nibbles(b) for b in data_bytes)
    target_n = sum_nibbles(TARGET_PRIMARY)
    want = target_n - s_data
    if want < 0 or want > 30:
        return None
    candidates = find_all_prefixes_for_want(want)
    if not candidates:
        return None
    return max(candidates)  # choose highest candidate (firmware-like heuristic)

def choose_backup_prefix_nibble(data_bytes:List[int], primary_pref:Optional[int]) -> Optional[int]:
    s_data = sum(sum_nibbles(b) for b in data_bytes)
    target_n = sum_nibbles(TARGET_BACKUP)
    want = target_n - s_data
    if want < 0 or want > 30:
        return None
    candidates = find_all_prefixes_for_want(want)
    if not candidates:
        return None
    # preferred rule: same low-nibble as primary, high-nibble = primary_high - 1
    if primary_pref is not None:
        p_low = primary_pref & 0x0F
        p_high = (primary_pref >> 4) & 0x0F
        if p_high > 0:
            preferred = ((p_high - 1) << 4) | p_low
            if preferred in candidates:
                return preferred
        # else choose candidate that shares low nibble if exists
        same_low = [c for c in candidates if (c & 0x0F) == p_low]
        if same_low:
            return max(same_low)
    # otherwise return highest candidate
    return max(candidates)

def int_to_3bytes_be(n:int) -> List[int]:
    if not (0 <= n <= 0xFFFFFF):
        raise ValueError("Numero fuori range (0..16777215).")
    return [(n >> 16) & 0xFF, (n >> 8) & 0xFF, n & 0xFF]

def bytes3_to_int_be(d0:int,d1:int,d2:int) -> int:
    return (d0<<16) | (d1<<8) | d2

# ---------------- UI handlers ----------------
def opcount_num_to_bytes_nibble_first():
    print("\n=== OPcount: Numero (DECIMALE) -> BYTES (NIBBLE-FIRST, no arith fallback) ===")
    s = input("Inserisci il numero di operazioni (DECIMALE, 0..16777215): ").strip()
    if not s.isdigit():
        print("Input non valido: inserire numero DECIMALE."); return
    n = int(s)
    data = int_to_3bytes_be(n)
    prim_pref = choose_primary_prefix_nibble(data)
    bkp_pref  = choose_backup_prefix_nibble(data, prim_pref)
    print("\nDati (3 byte HEX big-endian -> pos. 0x009..0x00B):", fmt_hex(data))
    if prim_pref is None:
        print("ERRORE: nessun prefisso PRIMARIO trovato che soddisfi la nibble-sum target (0xF7).")
    else:
        print("Prefisso PRIMARIO (nibble) @0x008 :", f"{prim_pref:02X}")
        print(" Primario @0x008..0x00B ->", fmt_hex([prim_pref] + data))
        print(" Verifica nibble-sum primario:", sum_nibbles(prim_pref) + sum(sum_nibbles(x) for x in data), " target:", sum_nibbles(TARGET_PRIMARY))
    if bkp_pref is None:
        print("ERRORE: nessun prefisso BACKUP trovato che soddisfi la nibble-sum target (0xE7). (Nessun fallback aritmetico usato.)")
    else:
        print("Prefisso BACKUP (nibble, preferred rule) @0x018 :", f"{bkp_pref:02X}")
        print(" Backup   @0x018..0x01B ->", fmt_hex([bkp_pref] + data))
        print(" Verifica nibble-sum backup:", sum_nibbles(bkp_pref) + sum(sum_nibbles(x) for x in data), " target:", sum_nibbles(TARGET_BACKUP))

def opcount_bytes_to_num_verify():
    print("\n=== OPcount: BYTES -> Numero (verifica nibble-sum) ===")
    try:
        prim_in = input("Inserisci 4 byte PRIMARIO @0x008..0x00B (es. 'F2 00 00 23'): ").strip()
        bkp_in  = input("Inserisci 4 byte BACKUP   @0x018..0x01B (es. 'E2 00 00 23'): ").strip()
        prim_block = [int(x,16) for x in prim_in.replace(',', ' ').split()]
        bkp_block  = [int(x,16) for x in bkp_in.replace(',', ' ').split()]
        if len(prim_block) != 4 or len(bkp_block) != 4:
            raise ValueError("Devi inserire esattamente 4 byte per blocco.")
    except Exception as e:
        print("Input non valido:", e); return
    # analyze
    for label, block, target in (("Primario (0x008)", prim_block, TARGET_PRIMARY), ("Backup (0x018)", bkp_block, TARGET_BACKUP)):
        pref, d0, d1, d2 = block
        value = bytes3_to_int_be(d0,d1,d2)
        s_n = sum_nibbles(pref) + sum(sum_nibbles(x) for x in (d0,d1,d2))
        ok = (s_n == sum_nibbles(target))
        print(f"\n--- {label} ---")
        print("Bytes:", fmt_hex(block))
        print("Valore memorizzato (HEX BE): 0x" + format(value,'06X'), " dec:", value)
        print("Nibble-sum total =", s_n, " target nibble-sum =", sum_nibbles(target), " ->", "OK" if ok else "FAIL")
        if not ok:
            # suggest possible nibble prefixes for info (if any)
            want = sum_nibbles(target) - sum(sum_nibbles(x) for x in (d0,d1,d2))
            if want < 0 or want > 30:
                print("  Nessun prefix nibble possibile (want fuori range).")
            else:
                candidates = find_all_prefixes_for_want(want)
                if candidates:
                    print("  Possibili prefix nibble (esempi):", ", ".join(f"0x{c:02X}" for c in sorted(candidates, reverse=True)[:8]))
                else:
                    print("  Nessun prefix nibble trovato.")

# ---------------- Main flow (integrazione completa) ----------------
def main():
    while True:
        print("\n=== CARINO COMBINED ===")
        print("1) Genera S/N + Credito (flow completo, idx_prev = idx_cur - 8)")
        print("2) OPcount: Numero (DEC) -> BYTES (nibble-first, no arith fallback)")
        print("3) OPcount: BYTES -> Numero (verifica nibble-sum)")
        print("q) Esci")
        ch = input("Scegli opzione: ").strip().lower()
        if ch == "1":
            run_credit_flow()
        elif ch == "2":
            opcount_num_to_bytes_nibble_first()
        elif ch == "3":
            opcount_bytes_to_num_verify()
        elif ch in ("q","quit","exit"):
            print("Esco. Ciao.")
            break
        else:
            print("Scelta non valida.")

# ---------------- existing credit flow extracted into function ----------------
def run_credit_flow():
    print("=== EEPROM generator (idx_prev = idx_cur - 8) - base 01/01/1995 ===")
    date_str = input("Dimmi che data vuoi (formato DD/MM/YYYY): ").strip()
    try:
        date_dt = datetime.strptime(date_str, "%d/%m/%Y")
    except Exception:
        print("Formato data non valido. Torna al menu."); return

    serial = "".join(str(secrets.randbelow(10)) for _ in range(8))
    print(f"\nSeriale generato automaticamente: {serial}")

    # build S/N (primario + copia)
    base = datetime(1995,1,1)
    days_raw = (date_dt - base).days
    days = days_raw % 10000 if days_raw >= 0 else 0
    s_pairs = [int(serial[i:i+2]) for i in range(0,8,2)]
    b1 = to_bcd_pair(s_pairs[0]); b5 = to_bcd_pair(s_pairs[1]); b6 = to_bcd_pair(s_pairs[2]); b7 = to_bcd_pair(s_pairs[3])
    days_str = f"{days:04d}"
    b2 = to_bcd_pair(int(days_str[:2])); b3 = to_bcd_pair(int(days_str[2:]))
    s = sum(((b>>4)&0xF) + (b&0xF) for b in (b1,b2,b3))
    prefix1 = (0xFF - s) & 0xFF
    s2 = sum(((b>>4)&0xF) + (b&0xF) for b in (b5,b6,b7))
    prefix2 = (0xFB - s2) & 0xFF
    primary_sn = [prefix1, b1, b2, b3, prefix2, b5, b6, b7]
    s1c = (0xEF - sum(((b>>4)&0xF) + (b&0xF) for b in (b1,b2,b3))) & 0xFF
    s2c = (0xEB - sum(((b>>4)&0xF) + (b&0xF) for b in (b5,b6,b7))) & 0xFF
    copy_sn = [s1c, b1, b2, b3, s2c, b5, b6, b7]

    print("\nS/N generato:")
    print("  primario @0x000..0x007 :", fmt_hex(primary_sn))
    print("  copia    @0x010..0x017 :", fmt_hex(copy_sn))

    # ask credit
    cred_in = input("\nDimmi quanto credito vuoi scroccare (es. 2.32 oppure 232 per centesimi): ").strip().replace(',', '.')
    if '.' in cred_in:
        try:
            cents = int(round(float(cred_in) * 100))
        except:
            print("Credito non valido. Torna al menu."); return
    else:
        if cred_in.isdigit():
            cents = int(cred_in)
        else:
            print("Credito non valido. Torna al menu."); return

    cur = generate_for_value(cents)
    print("\nCredito CORRENTE:")
    print(f"  Importo: {cur['cents']} centesimi ({cur['cents']/100.0:.2f} €)")
    print(f"  check = 59 - sum(v1..v4) = 0x{cur['check']:02X}  base4 digits = {cur['base4']}  idx = {cur['idx']}  code = {cur['code']}")
    print("  Bytes primario (0x044..0x047) :", fmt_hex(cur['primary_bytes']))
    print("  Bytes backup   (0x054..0x057) :", fmt_hex(cur['backup_bytes']))

    # precedente: if equal => idx_prev = idx_cur - 8
    ans_prev = input("\nVuoi che il CREDITO PRECEDENTE sia uguale al corrente? (S/N, default S): ").strip().lower()
    if ans_prev in ('', 's', 'si'):
        prev = previous_from_index_minus8(cur)
        prev_cents = cents
        prev_primary_bytes = prev['primary']
        prev_backup_bytes = prev['backup']
        print("\nRegola usata per il precedente: idx_prev = idx_cur - 8 (mod 256).")
    else:
        prev_in = input("Dimmi quanto credito PRECEDENTE vuoi (es. 1.40 oppure 140 per cent): ").strip().replace(',', '.')
        if '.' in prev_in:
            try:
                prev_cents = int(round(float(prev_in)*100))
            except:
                print("Formato non valido. Torna al menu."); return
        else:
            if prev_in.isdigit():
                prev_cents = int(prev_in)
            else:
                print("Formato non valido. Torna al menu."); return
        prev_res = generate_for_value(prev_cents)
        prev_primary_bytes = prev_res['primary_bytes']
        prev_backup_bytes = prev_res['backup_bytes']

    print("\nCredito PRECEDENTE:")
    print(f"  Importo precedente: {prev_cents} centesimi ({prev_cents/100.0:.2f} €)")
    print("  Bytes primario precedente (0x04C..0x04F) :", fmt_hex(prev_primary_bytes))
    print("  Bytes backup precedente   (0x05C..0x05F) :", fmt_hex(prev_backup_bytes))

    ck = sum(prev_primary_bytes) & 0xFF
    print(f"\nSuggerimento checksum (sum mod 256) sui 4 byte del precedente = 0x{ck:02X}")

    print("\n=== RIEPILOGO BYTES E INDIRIZZI ===")
    print("  Seriale primario  @0x000..0x007 :", fmt_hex(primary_sn))
    print("  Seriale copia     @0x010..0x017 :", fmt_hex(copy_sn))
    print("  Credito corrente primario @0x044..0x047 :", fmt_hex(cur['primary_bytes']))
    print("  Credito corrente backup   @0x054..0x057 :", fmt_hex(cur['backup_bytes']))
    print("  Credito precedente primario @0x04C..0x04F :", fmt_hex(prev_primary_bytes))
    print("  Credito precedente backup   @0x05C..0x05F :", fmt_hex(prev_backup_bytes))

# ---------------- launcher ----------------
if __name__ == '__main__':
    main()

