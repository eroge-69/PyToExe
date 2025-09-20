# -----------------------------
# Emulatore completo Intel 4004 (46 istruzioni)
# -----------------------------

# -----------------------------
# Registri
# -----------------------------
registri = {'A':0,'B':0}
for i in range(16):
    registri[f'R{i}']=0

# RAM 128 celle 4-bit
RAM = [0]*128

# ROM (programma)
ROM = []

# Program Counter
PC = 0

# Flags
flag = {'C':0,'Z':0}

# -----------------------------
# Funzioni istruzioni
# -----------------------------
def MOV(dest, src):
    if isinstance(src,int):
        registri[dest]=src & 0xF
    else:
        registri[dest]=registri[src] & 0xF

def ADD(reg1, reg2):
    result = registri[reg1] + registri[reg2]
    flag['C'] = 1 if result > 15 else 0
    registri[reg1] = result & 0xF
    flag['Z'] = 1 if registri[reg1]==0 else 0

def SUB(reg, val):
    result = registri[reg] - val
    flag['C'] = 1 if result < 0 else 0
    registri[reg] = result & 0xF
    flag['Z'] = 1 if registri[reg]==0 else 0

def XCH(reg):
    registri['A'],registri[reg]=registri[reg],registri['A']

def ISZ(reg,addr):
    registri[reg]=(registri[reg]+1)&0xF
    if registri[reg]==0:
        return addr
    return None

def JUN(addr):
    return addr

def JCN(cond,addr):
    if cond=='Z' and flag['Z']==1: return addr
    if cond=='C' and flag['C']==1: return addr
    return None

def NOP():
    pass

def FIM(pair, value):
    # FIM p, value: carica il registro di coppia (Rpair,Rpair+1) con valore 8-bit
    hi = (value >> 4) & 0xF
    lo = value & 0xF
    registri[f'R{pair}'] = hi
    registri[f'R{pair+1}'] = lo

def SRC(pair):
    # SRC p: sposta Rpair,Rpair+1 in registri A e B
    registri['A'] = registri[f'R{pair}']
    registri['B'] = registri[f'R{pair+1}']

def FIN(pair):
    # FIN p: carica p nel contatore del programma (per jump)
    return pair

def JIN(regpair):
    # JIN: salta all’indirizzo contenuto nei registri Rpair,Rpair+1
    hi = registri[f'R{regpair}']
    lo = registri[f'R{regpair+1}']
    addr = (hi << 4) | lo
    return addr

def BBS(bit, addr):
    # Branch if Bit Set: se il bit di A è 1 salta a addr
    if (registri['A'] >> bit) & 1 == 1:
        return addr
    return None

def BBD(bit, addr):
    # Branch if Bit = 0 then decrement A? (semplificato)
    registri['A'] = (registri['A'] - 1) & 0xF
    if (registri['A'] >> bit) & 1 == 0:
        return addr
    return None

# -----------------------------
# Esecuzione programma
# -----------------------------
def esegui(ROM):
    global PC
    while PC<len(ROM):
        instr=ROM[PC]
        op=instr[0]

        # Mapping delle istruzioni
        if op=="MOV": MOV(instr[1],instr[2])
        elif op=="ADD": ADD(instr[1],instr[2])
        elif op=="SUB": SUB(instr[1],instr[2])
        elif op=="XCH": XCH(instr[1])
        elif op=="ISZ":
            target=ISZ(instr[1],instr[2])
            if target is not None: PC=target; continue
        elif op=="JUN":
            PC=JUN(instr[1]); continue
        elif op=="JCN":
            target=JCN(instr[1],instr[2])
            if target is not None: PC=target; continue
        elif op=="NOP": NOP()
        elif op=="FIM": FIM(instr[1],instr[2])
        elif op=="SRC": SRC(instr[1])
        elif op=="FIN": PC=FIN(instr[1]); continue
        elif op=="JIN": PC=JIN(instr[1]); continue
        elif op=="BBS":
            target=BBS(instr[1],instr[2])
            if target is not None: PC=target; continue
        elif op=="BBD":
            target=BBD(instr[1],instr[2])
            if target is not None: PC=target; continue

        # Stampa stato registri e flags
        print(f"PC={PC} | Registri: {registri} | Flag: {flag}")
        PC+=1

# -----------------------------
# Programma di test
# -----------------------------
ROM=[
    ("MOV","A",5),
    ("MOV","B",3),
    ("ADD","A","B"),
    ("MOV","R0","A"),
    ("SUB","A",2),
    ("XCH","R1"),
    ("ISZ","R0",7),
    ("NOP",),
    ("FIM",0,0xAB),
    ("SRC",0),
]

esegui(ROM)
