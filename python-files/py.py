import os

def hex_to_dec(hex_str):
    return int(hex_str, 16)

def dec_to_hex(value):
    return f"{value:02X}"

def main():
    print("=== Conversor de Bytes (Little-Endian) ===")
    hex_input = input("Cole a sequencia de 50 bytes (separados por espacos):\n").strip()
    bytes_list = hex_input.split()
    
    # Verificação da quantidade de bytes
    if len(bytes_list) != 50:
        print("❌ Erro: a sequencia deve ter exatamente 50 bytes!")
        return

    output = []

    # Processa em pares
    for i in range(0, 50, 2):
        b1 = hex_to_dec(bytes_list[i])
        b2 = hex_to_dec(bytes_list[i+1])
        
        # Converte Little-Endian -> Decimal
        value = b1 + b2 * 256

        if value == 0:
            # Mantém 00 00
            output += ["00", "00"]
        else:
            # Aplica a fórmula
            result = 4095 - value
            r1 = result % 256
            r2 = result // 256
            output += [dec_to_hex(r1), dec_to_hex(r2)]

    # Junta tudo em uma linha contínua
    output_line = "".join(output)

    # Salva em resultado.txt na mesma pasta
    path = os.path.join(os.getcwd(), "resultado.txt")
    with open(path, "w") as f:
        f.write(output_line)

    print(f"\n✅ Resultado salvo em 'resultado.txt'\n")
    print(f"Resultado: {output_line}")

if __name__ == "__main__":
    main()
