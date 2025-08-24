def keeloq_encrypt(data: int, key: int) -> int:
    # Keeloq: 32-bit block, 64-bit key, 528 rounds
    NLF = 0x3A5C742E
    x = data & 0xFFFFFFFF
    for r in range(528):
        b0  = (x >> 0) & 1
        b16 = (x >> 16) & 1
        b1  = (x >> 1) & 1
        b9  = (x >> 9) & 1
        b20 = (x >> 20) & 1
        b26 = (x >> 26) & 1
        b31 = (x >> 31) & 1
        nlf_index = (b1 << 0) | (b9 << 1) | (b20 << 2) | (b26 << 3) | (b31 << 4)
        nlf_bit = (NLF >> nlf_index) & 1
        key_bit = (key >> (r & 63)) & 1
        new_bit = b0 ^ b16 ^ nlf_bit ^ key_bit
        x = ((x >> 1) | (new_bit << 31)) & 0xFFFFFFFF
    return x

#def main():
try:
                  for count in range(0xFFFFFFFF):
                  #  print(count)
                    for key in range(0xFFFFFFFFFFFFFFFF):
                      code = keeloq_encrypt(count,key)
                      if code==0x11111111:
                         print(f"code = 0x{code:08X}")
                   #   print(count,key)  
except  KeyboardInterrupt:
                print(count,key)
#if __name__ == "__main__":
#        main()
#
#        input("Готово. Натисни Enter за изход...")
        