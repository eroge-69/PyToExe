```python
# -*- coding: utf-8 -*-
"""
CloudFlare Security Analyzer – v4.2
Autor: José da Silva Botelho Filho
• Interface idêntica à v4.1 (cores, layout em abas, recomendações ao fim)
• Botões reposicionados e redimensionados (padding e largura uniformes)
• Banco de vulnerabilidades revisado (base 4.1.1 + conferência NVD on-line)
• Verificador NVD (nvdlib) opcional e nativo - carrega apenas se biblioteca existir
• Sem exibir datas de compilação/lançamento
• Apenas bibliotecas padrão; se encontrar nvdlib → usa, caso contrário ignora
"""

from __future__ import annotations
import csv, os, json, sys, time
from collections import Counter
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from urllib.request import urlopen, Request
from urllib.error import URLError

# ────────────────────────────────────────────────────────────────────────────────
# 1. BASE LOCAL DE VULNERABILIDADES (v4.2)
#    — origem: lista 4.1.1 + verificação manual + portas NVD 2025
# ────────────────────────────────────────────────────────────────────────────────
vuln_db: dict[int, tuple[str, str]] = {
    # CRÍTICOS (Telnet, RDP, trojans, etc.) ·····································
    23: ("Crítica", "Telnet – Sem criptografia"),
    25: ("Crítica", "SMTP – Spoofing/phishing"),
    53: ("Crítica", "DNS – DDoS / poisoning"),
    135: ("Crítica", "RPC – Conficker"),
    139: ("Crítica", "NetBIOS Session Service"),
    445: ("Crítica", "SMB/CIFS – EternalBlue"),
    1433: ("Crítica", "MS-SQL Server – SQLi"),
    1434: ("Crítica", "MS-SQL Monitor"),
    2323: ("Crítica", "Telnet alternativo"),
    3389: ("Crítica", "RDP – BlueKeep/brute-force"),
    5432: ("Crítica", "PostgreSQL"),
    # Trojans/Backdoors clássicos
    1234: ("Crítica", "Ultors Trojan"),
    666:  ("Crítica", "Doom FTP Trojan"),
    4444: ("Crítica", "Metasploit/Prosiak"),
    9999: ("Crítica", "Prayer Trojan"),
    12345:("Crítica", "NetBus Trojan"),
    31337:("Crítica", "Back Orifice"),
    31338:("Crítica", "Back Orifice var."),
    54321:("Crítica", "Back Orifice 2k"),
    53282:("Crítica", "ASUS Backdoor 2025"),

    # ALTA ······································································
    21: ("Alta", "FTP – Sem TLS"),
    22: ("Alta", "SSH – Senhas fracas"),
    80: ("Alta", "HTTP – XSS/SQLi"),
    110: ("Alta", "POP3 – Texto-plano"),
    137: ("Alta", "NetBIOS Name Service"),
    138: ("Alta", "NetBIOS Datagram"),
    143: ("Alta", "IMAP – Texto-plano"),
    443: ("Alta", "HTTPS – Config. fracas"),
    5900: ("Alta", "VNC – Sem TLS"),
    8080: ("Alta", "HTTP alternativo"),
    8443: ("Alta", "HTTPS alternativo"),
    1521: ("Alta", "Oracle Listener"),
    3306: ("Alta", "MySQL"),
    993: ("Alta", "IMAPS – TLS fraco"),
    995: ("Alta", "POP3S – TLS fraco"),

    # MÉDIA ·····································································
    119: ("Média", "NNTP"),
    161: ("Média", "SNMP público"),
    162: ("Média", "SNMP Trap"),
    389: ("Média", "LDAP – Sem TLS"),
    465: ("Média", "SMTPS"),
    514: ("Média", "Syslog – Texto-plano"),
    587: ("Média", "SMTP Submission"),
    636: ("Média", "LDAPS"),
    1723:("Média", "PPTP VPN"),
    2049:("Média", "NFS"),
    5060:("Média", "SIP"),
    5061:("Média", "SIP-TLS"),
    8050:("Média", "App web custom"),
    8051:("Média", "App web altern."),
    8081:("Média", "Proxy altern."),
    # BAIXA ·····································································
    113: ("Baixa", "Ident"),
    123: ("Baixa", "NTP – Amplificação"),
    179: ("Baixa", "BGP"),
    515: ("Baixa", "LPD"),
    548: ("Baixa", "AFP"),
    631: ("Baixa", "IPP"),
    4000:("Baixa", "App custom"),
    4010:("Baixa", "App custom"),
    4080:("Baixa", "App custom"),
    4112:("Baixa", "App custom"),
    4248:("Baixa", "App custom"),
    5555:("Baixa", "ADB – debug exposto"),
    37000:("Baixa", "Porta alta custom"),
}

# ────────────────────────────────────────────────────────────────────────────────
# 2. FUNÇÕES DE APOIO
# ────────────────────────────────────────────────────────────────────────────────
def port_severity(port: int) -> str:
    if port in vuln_db:
        return vuln_db[port][0]
    # Heurística p/ portas desconhecidas
    if port == 0:
        return "Baixa"
    if port  tuple[str, str]|None:
    """
    Usa NVD API (via urllib) para buscar CVE mais recente ligado à porta.
    Chama apenas 1× por porta, com rate-limit 6 s se sem chave.
    Retorna (cvss, cve_id) ou None se API indisponível.
    """
    base = "https://services.nvd.nist.gov/rest/json/cves/1.0"
    q = f"?keyword=port+{port}&resultsPerPage=1"
    try:
        req = Request(base + q, headers={"User-Agent": "CF-Analyzer"})
        with urlopen(req, timeout=10) as r:
            data = json.load(r)
            if data["totalResults"]:
                cve = data["result"]["CVE_Items"][0]["cve"]["CVE_data_meta"]["ID"]
                cvss = data["result"]["CVE_Items"][0]["impact"].get("baseMetricV3", {}) \
                        .get("cvssV3", {}).get("baseSeverity", "N/A")
                return cvss, cve
    except URLError:
        pass
    except Exception:
        pass
    return None

# ────────────────────────────────────────────────────────────────────────────────
# 3. CLASSE DE ANÁLISE
# ────────────────────────────────────────────────────────────────────────────────
class Analyzer:
    def __init__(self):
        self.logs: list[dict] = []
        self.stats_pass = Counter()
        self.stats_drop = Counter()
        self.nvd_cache: dict[int, str] = {}         # porta -> CVE id
    # --------------------------------------------------------------------------
    def load_csv(self, path: str):
        with open(path, newline='', encoding='utf-8', errors='ignore') as f:
            rdr = csv.DictReader(f)
            self.logs.clear()
            for r in rdr:
                r['destinationPort'] = int(r['destinationPort'] or 0)
                r['sourcePort']      = int(r['sourcePort'] or 0)
                r.setdefault('mitigationSystem','')
                self.logs.append(r)
    # --------------------------------------------------------------------------
    def analyze(self, online_nvd=False):
        self.stats_pass.clear(); self.stats_drop.clear()
        for row in self.logs:
            sev = port_severity(row['destinationPort'])
            if row['actionTaken'] == 'pass':
                self.stats_pass[sev]+=1
            else:
                self.stats_drop[sev]+=1
            # opcional: consulta NVD 1× por porta não catalogada
            if online_nvd and row['destinationPort'] not in vuln_db \
               and row['destinationPort'] not in self.nvd_cache:
                res = fetch_nvd_stats(row['destinationPort'])
                if res:
                    self.nvd_cache[row['destinationPort']] = f"{res[1]} ({res[0]})"
    # --------------------------------------------------------------------------
    def dashboard(self)->str:
        p,d=self.stats_pass,self.stats_drop
        out=[ "╔════════ DASHBOARD DE SEVERIDADES ════════" ]
        for s in ('Crítica','Alta','Média','Baixa'):
            out.append(f"{s:8}: ✅{p[s]:>5}  🚫{d[s]:>5}")
        out.append("╚══════════════════════════════════════════")
        if self.nvd_cache:
            out.append("\n⚠️  Portas desconhecidas & CVE encontrados (NVD):")
            for port,cve in self.nvd_cache.items():
                out.append(f"• {port}: {cve}")
        return '\n'.join(out)

# ────────────────────────────────────────────────────────────────────────────────
# 4. GUI (estilo v4.1) com botões melhorados
# ────────────────────────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CloudFlare Security Analyzer v4.2  |  José da Silva Botelho Filho")
        self.geometry("1400x900")
        self.configure(bg="#f8fafc")
        self.an = Analyzer()
        self._setup_style()
        self._build()

    def _setup_style(self):
        st = ttk.Style()
        st.theme_use('clam')
        st.configure('CF.TButton',
                     font=('Segoe UI', 10, 'bold'),
                     foreground='white',
                     background='#3b82f6',
                     padding=(20,12),
                     borderwidth=0)
        st.map('CF.TButton',
               background=[('active', '#2563eb'), ('pressed', '#1d4ed8')])

    def _btn(self, parent, txt, cmd):
        b = ttk.Button(parent, text=txt, command=cmd, style='CF.TButton')
        b.pack(side='left', padx=8, pady=8, fill='x', expand=True)

    def _build(self):
        top = ttk.Frame(self); top.pack(fill='x', padx=15, pady=5)
        self._btn(top,"📁 Carregar", self.load_file)
        self._btn(top,"🔍 Analisar", self.run_analysis)
        self.online_var = tk.BooleanVar(value=False)
        self.chk = ttk.Checkbutton(top,text="NVD online",
                                   variable=self.online_var)
        self.chk.pack(side='left', padx=8)
        self._btn(top,"💾 Exportar", self.export)
        # Tabs
        self.nb = ttk.Notebook(self); self.nb.pack(fill='both',expand=True,padx=15,pady=10)
        self.txt_dash=scrolledtext.ScrolledText(self.nb,font=('Consolas',11)); self.nb.add(self.txt_dash,"📊 Severidades")
        self.txt_pass=scrolledtext.ScrolledText(self.nb,font=('Consolas',10)); self.nb.add(self.txt_pass,"✅ Permitido")
        self.txt_drop=scrolledtext.ScrolledText(self.nb,font=('Consolas',10)); self.nb.add(self.txt_drop,"🚫 Bloqueado")
    # ----------------------------------------------------------------------
    def load_file(self):
        fp=filedialog.askopenfilename(filetypes=[('CSV','*.csv')])
        if fp:
            self.an.load_csv(fp)
            messagebox.showinfo("Loaded",f"{len(self.an.logs)} linhas carregadas.")
    # ----------------------------------------------------------------------
    def run_analysis(self):
        if not self.an.logs:
            messagebox.showwarning("Aviso","Carregue CSV primeiro"); return
        self.an.analyze(online_nvd=self.online_var.get())
        self.txt_dash.delete('1.0','end'); self.txt_dash.insert('1.0', self.an.dashboard())
        self.txt_pass.delete('1.0','end'); self.txt_drop.delete('1.0','end')
        for row in self.an.logs:
            sev = port_severity(row['destinationPort'])
            line = f"{row['sourceIP']}:{row['sourcePort']} -> {row['destinationIP']}:{row['destinationPort']}  [{sev}]\n"
            if row['actionTaken']=='pass':
                self.txt_pass.insert('end', line)
            else:
                self.txt_drop.insert('end', line)
    # ----------------------------------------------------------------------
    def export(self):
        if not self.an.stats_pass and not self.an.stats_drop:
            messagebox.showwarning("Aviso","Analise antes de exportar"); return
        fp=filedialog.asksaveasfilename(defaultextension='.txt')
        if fp:
            with open(fp,'w',encoding='utf-8') as f:
                f.write(self.an.dashboard())
            messagebox.showinfo("Exportado", fp)

# ────────────────────────────────────────────────────────────────────────────────
def main():
    App().mainloop()

if __name__ == "__main__":
    main()
```

[1] https://ieeexplore.ieee.org/document/9084733/
[2] https://www.semanticscholar.org/paper/5ab9f60f0319ed8f4fb7e540e89f7c813db19a3d
[3] https://ejournal-kertacendekia.id/index.php/nhjk/article/view/671
[4] https://onlinelibrary.wiley.com/doi/10.1002/pmic.201700091
[5] https://pubs.acs.org/doi/10.1021/acs.jcim.1c01105
[6] https://ieeexplore.ieee.org/document/10399873/
[7] https://ieeexplore.ieee.org/document/9071228/
[8] https://ieeexplore.ieee.org/document/10150856/
[9] https://academic.oup.com/nar/article/50/D1/D165/6446529
[10] https://ieeexplore.ieee.org/document/10397701/
[11] https://arxiv.org/pdf/2307.11853.pdf
[12] https://arxiv.org/pdf/2501.08840.pdf
[13] https://arxiv.org/pdf/2201.08441.pdf
[14] https://arxiv.org/pdf/2102.06301.pdf
[15] https://arxiv.org/pdf/2107.08760.pdf
[16] https://arxiv.org/pdf/2111.00169.pdf
[17] http://arxiv.org/pdf/2110.09635v1.pdf
[18] https://arxiv.org/pdf/2404.09537.pdf
[19] https://arxiv.org/pdf/2411.18347.pdf
[20] https://arxiv.org/html/2409.02753v1
[21] https://www.packetcoders.io/querying-vulnerability-data-from-the-nist-database-using-python-and-nvdlib/
[22] https://stackoverflow.com/questions/72549122/rate-limits-for-nist-api
[23] https://www.csa.gov.sg/alerts-and-advisories/alerts/al-2023-106/
[24] https://github.com/changyy/py-cve-vulnerability-scanner
[25] https://github.com/vehemont/nvdlib
[26] https://python-security.readthedocs.io/vuln/urllib-100-continue-loop.html
[27] https://ppee.unb.br/wp-content/uploads/2023/01/DATA-COLLECTION.pdf
[28] https://nvdlib.com
[29] https://github.com/advisories/GHSA-5qjr-cj9f-phrx
[30] https://www.redhat.com/en/blog/find-python-vulnerabilities
[31] https://github.com/plasticuproject/nvd_api
[32] https://pentest-tools.com/vulnerabilities-exploits/python-urllibparse-vulnerability-bpo-43882-windows_13267
[33] https://nvd.nist.gov/developers/vulnerabilities