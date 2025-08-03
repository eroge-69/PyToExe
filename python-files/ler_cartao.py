import sys
from smartcard.scard import SCARD_S_SUCCESS
from smartcard.System import readers

# Configurações do leitor
APDU_AUTHENTICATE = [0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00, 0x04, 0x60, 0x00]
KEY_DEFAULT = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

def byte_array_to_string(byte_array):
    """Converte uma array de bytes para uma string de texto, removendo padding."""
    return "".join(map(chr, byte_array)).split('\x00')[0]

def ler_cartao(conn):
    """Lê os dados do Bloco 4 do cartão RFID."""
    try:
        print("A autenticar no cartão...")
        
        # Carregar a chave na memória volátil do leitor
        apdu_load_key = [0xFF, 0x82, 0x00, 0x00, 0x06] + KEY_DEFAULT
        response, sw1, sw2 = conn.transmit(apdu_load_key)
        
        if sw1 != 0x90 or sw2 != 0x00:
            print(f"Erro ao carregar a chave: {hex(sw1)} {hex(sw2)}")
            return None

        # Autenticar no bloco
        response, sw1, sw2 = conn.transmit(APDU_AUTHENTICATE)
        if sw1 != 0x90 or sw2 != 0x00:
            print(f"Erro de autenticação: {hex(sw1)} {hex(sw2)}. Chave pode não ser a padrão.")
            return None

        print("Autenticação bem-sucedida.")

        # Comando para ler o Bloco 4
        # FF B0 00 04 10 (cabeçalho: ler Bloco 4, 16 bytes)
        apdu_read = [0xFF, 0xB0, 0x00, 0x04, 0x10]
        response, sw1, sw2 = conn.transmit(apdu_read)

        if sw1 == 0x90 and sw2 == 0x00:
            dados_lidos = byte_array_to_string(response)
            print(f"Dados lidos: {dados_lidos}")
            return dados_lidos
        else:
            print(f"Erro na leitura: {hex(sw1)} {hex(sw2)}")
            return None
            
    except Exception as e:
        print(f"Ocorreu um erro durante a leitura: {e}")
        return None

def main():
    try:
        all_readers = readers()
        if not all_readers:
            print("Nenhum leitor NFC encontrado.")
            sys.exit(1)
        
        reader = all_readers[0]
        print(f"Leitor NFC encontrado: {reader}")

        while True:
            try:
                print("\nAguardando cartão NFC...")
                conn = reader.createConnection()
                conn.connect()
                print("Cartão detectado!")

                ler_cartao(conn)
                
                # Aguarda até que o cartão seja removido
                print("Remova o cartão...")
                conn.disconnect()
            
            except Exception as e:
                print(f"Cartão removido ou erro de conexão: {e}")
                
    except Exception as e:
        print(f"Ocorreu um erro fatal: {e}")

if __name__ == "__main__":
    main()