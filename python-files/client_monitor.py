from flask import Flask, jsonify
import psutil
import GPUtil
import socket

app = Flask(__name__)

# Funzione per ottenere info GPU
def get_gpu_info():
    gpus = GPUtil.getGPUs()
    gpu_data = []
    for gpu in gpus:
        gpu_data.append({
            "name": gpu.name,
            "load": f"{gpu.load * 100:.2f}%",
            "memory": f"{gpu.memoryUsed}/{gpu.memoryTotal} MB"
        })
    return gpu_data

@app.route('/system', methods=['GET'])
def system_info():
    cpu_percent = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()

    # Lista dei primi 10 processi
    processes = []
    for p in psutil.process_iter(['pid', 'name', 'username']):
        try:
            processes.append(p.info)
        except:
            continue

    return jsonify({
        "hostname": socket.gethostname(),
        "cpu": f"{cpu_percent}%",
        "ram": {
            "used": f"{ram.used // (1024 ** 2)} MB",
            "total": f"{ram.total // (1024 ** 2)} MB",
            "percent": f"{ram.percent}%"
        },
        "gpu": get_gpu_info(),
        "processes": processes[:10]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
