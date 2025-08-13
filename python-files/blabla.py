import platform
import psutil
import requests
import GPUtil
import socket

# === CONFIG ===
WEBHOOK_URL = "https://discord.com/api/webhooks/1358429066658713850/e9CHw7RetQTJ8JlGXHS2MjotV6CUpMRD3Y_0eJkxAYnCBCLB__zmPB6alF3TeiMsHiwD"  # Replace with your Discord webhook

def get_specs():
    # CPU
    cpu_name = platform.processor() or "Unknown"
    cpu_cores = psutil.cpu_count(logical=False)
    cpu_threads = psutil.cpu_count(logical=True)

    # RAM
    ram_total = round(psutil.virtual_memory().total / (1024**3), 2)

    # GPU(s)
    gpus = GPUtil.getGPUs()
    gpu_info = "\n".join([f"{gpu.name} ({gpu.memoryTotal}MB)" for gpu in gpus]) if gpus else "No GPU detected"

    # Disk
    disk_total = round(psutil.disk_usage('/').total / (1024**3), 2)

    # OS
    os_info = f"{platform.system()} {platform.release()} ({platform.version()})"

    # Hostname
    hostname = socket.gethostname()

    return {
        "Hostname": hostname,
        "OS": os_info,
        "CPU": f"{cpu_name} ({cpu_cores} cores / {cpu_threads} threads)",
        "RAM (GB)": ram_total,
        "GPU": gpu_info,
        "Disk (GB)": disk_total
    }

def send_discord_webhook(specs):
    embed = {
        "title": "💻 System Specifications",
        "color": 0x00ff00,
        "fields": [{"name": k, "value": str(v), "inline": False} for k, v in specs.items()]
    }

    payload = {
        "username": "System Bot",
        "embeds": [embed]
    }

    try:
        r = requests.post(WEBHOOK_URL, json=payload)
        if r.status_code in [200, 204]:
            print("[✓] Specs sent to Discord successfully!")
        else:
            print(f"[!] Discord returned {r.status_code}: {r.text}")
    except Exception as e:
        print(f"[!] Failed to send webhook: {e}")

if __name__ == "__main__":
    specs = get_specs()
    send_discord_webhook(specs)
