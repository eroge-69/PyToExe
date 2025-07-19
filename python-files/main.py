import readline
from tronpy import Tron
from tronpy.keys import PrivateKey
from mnemonic import Mnemonic
import os 


mnemo = Mnemonic("english")
client = Tron()

# ===== Вспомогательные функции =====
def seed_to_private_key(seed_phrase):
    seed = mnemo.to_seed(seed_phrase)
    return PrivateKey(seed[:32])

def get_address_from_seed(seed_phrase):
    try:
        priv_key = seed_to_private_key(seed_phrase)
        return priv_key.public_key.to_base58check_address(), priv_key
    except Exception as e:
        print(f"Ошибка: {e}")
        return None, None

def show_balance(address):
    try:
        acc = client.get_account(address)
        trx_balance = acc['balance'] / 1_000_000
        print(f"TRX: {trx_balance:.6f}")
        if 'assetV2' in acc:
            for token in acc['assetV2']:
                print(f"{token['key']}: {token['value']}")
    except Exception as e:
        print(f"Ошибка при получении баланса: {e}")

def send_trx(priv_key, from_addr, to_addr, amount):
    try:
        txn = (
            client.trx.transfer(from_addr, to_addr, int(float(amount) * 1_000_000))
            .build()
            .sign(priv_key)
            .broadcast()
        )
        print(f"TRX отправлен! TXID: {txn['txid']}")
    except Exception as e:
        print(f"Ошибка при отправке TRX: {e}")

def send_token(priv_key, from_addr, to_addr, amount, contract_addr):
    try:
        contract = client.get_contract(contract_addr)
        txn = (
            contract.functions.transfer(to_addr, int(amount))
            .with_owner(from_addr)
            .fee_limit(5_000_000)
            .build()
            .sign(priv_key)
            .broadcast()
        )
        print(f"Токен отправлен! TXID: {txn['txid']}")
    except Exception as e:
        print(f"Ошибка при отправке токена: {e}")

# ===== Интерфейс терминала =====
def terminal_loop(address, priv_key):
    os.system('cls')
    print(f"\nГотово. Вы вошли как: {address}")
    print("Введите команду. Для справки введите `help`.")

    while True:
        try:
            cmd = input("tron-wallet> ").strip().lower()

            if cmd == "exit":
                print("Выход...")
                break
            elif cmd == "address":
                print(f"Ваш адрес: {address}")
            elif cmd == "balance":
                show_balance(address)
            elif cmd.startswith("send_trx"):
                parts = cmd.split()
                if len(parts) != 3:
                    print("Использование: send_trx <to_address> <amount>")
                else:
                    send_trx(priv_key, address, parts[1], parts[2])
            elif cmd.startswith("send_token"):
                parts = cmd.split()
                if len(parts) != 4:
                    print("Использование: send_token <to_address> <amount> <contract_address>")
                else:
                    send_token(priv_key, address, parts[1], parts[2], parts[3])
            elif cmd == "help":
                print("""
 Доступные команды:
  address                         - Показать адрес
  balance                         - Показать баланс TRX и токенов
  send_trx <to> <amount>          - Отправить TRX
  send_token <to> <amt> <ctr>     - Отправить TRC20 токен
  exit                            - Выход
                """)
            else:
                print("Неизвестная команда. Напишите `help` для списка.")
        except KeyboardInterrupt:
            print("\nПринудительное завершение.")
            break
        except Exception as e:
            print(f"Ошибка: {e}")

# ======= Запуск =======
if __name__ == "__main__":
    print("=== TRON CLI Кошелек ===")
    try:
        seed = input("Введите seed-фразу: ").strip()
        address, priv_key = get_address_from_seed(seed)
        if not address:
            print("Неверная сид-фраза.")
        else:
            terminal_loop(address, priv_key)
    except KeyboardInterrupt:
        print("\n Отмена.")
