import numpy as np
import re
import sys
import os

def help_message():
    print("USO:")
    print("  Arraste o arquivo de entrada para este programa OU")
    print("  Rode no CMD: conversor_cnc.exe entrada.nc saida.nc")
    print("")
    print("O script aplica rotação -90° em X e pode adicionar translação em X.")
    print("Edite o código para outros ângulos/posições conforme seu caso.")
    print("")

def get_filenames():
    # Se argumentos via linha de comando
    if len(sys.argv) == 3:
        return sys.argv[1], sys.argv[2]
    # Tenta pedir nomes manualmente
    print("Digite o nome do arquivo de entrada (ex: entrada_vertical.nc):")
    entrada = input().strip()
    print("Digite o nome do arquivo de saída (ex: saida_horizontal_coord.nc):")
    saida = input().strip()
    return entrada, saida

def main():
    print("\n====== Conversor CNC com Matriz (Python/EXE) ======")
    if len(sys.argv) not in [1,3]:
        help_message()
        return

    entrada, saida = get_filenames()
    if not os.path.exists(entrada):
        print(f"Arquivo de entrada '{entrada}' não encontrado!")
        return

    # --- Configuração da matriz de transformação ---
    # Rotação de -90 graus em X (vertical para horizontal)
    theta = -np.pi/2
    M_rot = np.array([
        [1, 0,             0,          0],
        [0, np.cos(theta), -np.sin(theta), 0],
        [0, np.sin(theta), np.cos(theta), 0],
        [0, 0,             0,          1]
    ])
    # (Opcional) Translação em X de +100mm
    T = np.array([
        [1, 0, 0, 0],   # Troque 0 por 100 para transladar X +100
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])
    M_total = T @ M_rot

    def transformar_ponto(x, y, z, M):
        P = np.array([[x], [y], [z], [1]])
        P_dest = M @ P
        return float(P_dest[0]), float(P_dest[1]), float(P_dest[2])

    total_linhas = 0
    total_convertidas = 0

    with open(entrada, 'r') as fin, open(saida, 'w') as fout:
        for linha in fin:
            total_linhas += 1
            mX = re.search(r'X([+-]?\\d+(\\.\\d+)?)', linha)
            mY = re.search(r'Y([+-]?\\d+(\\.\\d+)?)', linha)
            mZ = re.search(r'Z([+-]?\\d+(\\.\\d+)?)', linha)
            x = float(mX.group(1)) if mX else None
            y = float(mY.group(1)) if mY else None
            z = float(mZ.group(1)) if mZ else None

            if (x is not None) and (y is not None) and (z is not None):
                x2, y2, z2 = transformar_ponto(x, y, z, M_total)
                linha_nova = re.sub(r'X[+-]?\\d+(\\.\\d+)?', f'X{x2:.3f}', linha)
                linha_nova = re.sub(r'Y[+-]?\\d+(\\.\\d+)?', f'Y{y2:.3f}', linha_nova)
                linha_nova = re.sub(r'Z[+-]?\\d+(\\.\\d+)?', f'Z{z2:.3f}', linha_nova)
                fout.write(linha_nova)
                total_convertidas += 1
            else:
                fout.write(linha)
    print(f'\nConversão de coordenadas concluída!\nLinhas processadas: {total_linhas}\nLinhas convertidas: {total_convertidas}\nArquivo salvo como: {saida}')
    print('=====================================\n')

if __name__ == '__main__':
    main()
