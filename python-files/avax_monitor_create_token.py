
from web3 import Web3
import time
import requests

# === 配置区 ===
AVAX_RPC = "https://api.avax.network/ext/bc/C/rpc"
w3 = Web3(Web3.HTTPProvider(AVAX_RPC))

# 监控目标地址
TARGET_CREATOR = "0x8315f1eb449dd4b779495c3a0b05e5d194446c6e".lower()
# 目标方法签名（CreateToken）
TARGET_METHOD_PREFIX = "0x30f51a46"

# Telegram 配置
TELEGRAM_TOKEN = "7360483873:AAFv-L9QHXbwPNzgaW0z_xv8AQ0Xh8IaHl4"
TELEGRAM_CHAT_ID = "user-iVcv64iirY6xyKe2Wnd36T2r"

# === 通知函数 ===
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, data=data)
        if r.status_code != 200:
            print("❌ Telegram 通知失败", r.text)
    except Exception as e:
        print("❌ Telegram 出错:", e)

# === 核心监控逻辑 ===
def check_new_create_token_calls():
    latest = w3.eth.block_number
    for i in range(latest - 2, latest + 1):
        block = w3.eth.get_block(i, full_transactions=True)
        for tx in block.transactions:
            if tx["from"].lower() == TARGET_CREATOR and tx["input"].startswith(TARGET_METHOD_PREFIX):
                receipt = w3.eth.get_transaction_receipt(tx["hash"])
                contract_address = receipt.contractAddress if hasattr(receipt, "contractAddress") else None
                tx_link = f"https://snowscan.xyz/tx/{tx['hash'].hex()}"
                message = f"🚀 *发现新代币创建！*\n\n👤 创建地址: `{TARGET_CREATOR}`\n🔗 [交易详情]({tx_link})"
                if contract_address:
                    token_link = f"https://snowscan.xyz/address/{contract_address}"
                    message += f"\n📦 合约地址: `{contract_address}`\n🔗 [合约页面]({token_link})"
                print("📢 发现新创建代币，正在发送通知...")
                send_telegram_message(message)

# === 主循环 ===
print("🚀 AVAX 代币监控启动，正在监听 CreateToken...")
while True:
    try:
        check_new_create_token_calls()
    except Exception as e:
        print("❌ 出错:", e)
    time.sleep(8)
