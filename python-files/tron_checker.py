import requests
import re
import os
import sys

# -------------------- 配置文件路径 --------------------
BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
input_file = os.path.join(BASE_DIR, "tron_addresses.txt")  # 输入地址文件
output_file = os.path.join(BASE_DIR, "result.txt")         # 输出结果文件

# -------------------- 地址校验 --------------------
def is_valid_tron_address(address):
    """验证是否为有效的 TRON 地址"""
    return bool(re.match(r"^T[1-9A-HJ-NP-Za-km-z]{33}$", address))

# -------------------- 查询余额 --------------------
def get_tron_balances(address):
    """获取 TRX 与 USDT(TRC20) 余额"""
    if not is_valid_tron_address(address):
        return None  # 地址格式错误

    url = f"https://apilist.tronscan.org/api/account?address={address}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        # TRX 余额
        trx_balance = round(int(data.get("balance", 0)) / 1_000_000, 6)

        # USDT(TRC20) 余额
        usdt_balance = 0.0
        if "trc20token_balances" in data:
            for token in data["trc20token_balances"]:
                if token.get("tokenAbbr", "").upper() == "USDT":
                    usdt_balance = round(
                        int(token.get("balance", 0)) / (10 ** token.get("tokenDecimal", 6)), 6
                    )

        return trx_balance, usdt_balance
    except Exception:
        return 0.0, 0.0

# -------------------- 主程序 --------------------
def main():
    if not os.path.exists(input_file):
        print(f"❌ 未找到 {input_file}，请在同目录放置 tron_addresses.txt")
        input("\n按 Enter 键退出...")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        addresses = [line.strip() for line in f if line.strip()]

    results = []
    for addr in addresses:
        balances = get_tron_balances(addr)
        if balances is None:
            results.append(f"{addr} → 地址格式错误 ❌")
        else:
            trx, usdt = balances
            results.append(f"{addr} → TRX: {trx} | USDT: {usdt}")
        print(results[-1])

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(results))

    print(f"\n✅ 查询完成，结果已保存到 {output_file}")
    input("\n按 Enter 键退出...")  # 防止 EXE 闪退

if __name__ == "__main__":
    main()
