#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DDoS Protector - Produktionsversion
- Modularer, dokumentierter, verkaufsfähiger Single-file Daemon
- Auto-install Minimal-Python-Abhängigkeiten (nur wenn nötig)
- Konfigurierbar per config.ini
- Flask-Web-Dashboard (read-only) zur Überwachung
- Platform-aware ipset/iptables integration auf Linux

Wichtig:
- Nur defensive Nutzung. Binde das Skript in ein Produkt mit Lizenz und SLA.
- Testen Sie auf einer isolierten Umgebung bevor der Einsatz in Produktion.

Autor: Überarbeitet für Vertrieb
Version: 1.0.0
License: MIT (prüfen und anpassen)
"""

from __future__ import annotations

import argparse
import logging
import os
import platform
import signal
import subprocess
import sys
import time
from collections import Counter, deque
from configparser import ConfigParser
from logging.handlers import RotatingFileHandler
from multiprocessing import Event, Manager, Process, Queue
from queue import Empty, Full

# Optional imports deferred until runtime to allow dry-run/help without dependencies
REQUIREMENTS = ["scapy", "flask", "flask_cors", "requests"]

# -------------------- Default Configuration --------------------
DEFAULT_CONFIG_PATH = "config.ini"
DEFAULTS = {
    "Mitigation": {
        "enable_auto_block": "true",
        "block_threshold_pps_per_source": "50",
        "block_duration_ip": "300"
    },
    "Network": {"target_ip": ""},
    "Whitelist": {"whitelisted_ips": "127.0.0.1,8.8.8.8,1.1.1.1"}
}

# Runtime globals (filled by load_config)
CONFIG = {}
QUEUE_MAXSIZE = 20000
SNAPSHOT_INTERVAL = 1.0
SLIDING_WINDOW_SECONDS = 15
SYSTEM_PLATFORM = platform.system()

PORT_TO_PROTOCOL_NAME = {
    7: 'echo', 17: 'qotd', 19: 'chargen', 53: 'dns/adns', 69: 'tftp', 80: 'amp/quic',
    111: 'rpc/portmap', 123: 'ntp', 137: 'netbios', 161: 'snmp', 177: 'xdmcp',
    389: 'cldap/ldap', 427: 'slp', 443: 'dtls', 500: 'isakmp/ipsec', 520: 'rip', 523: 'db2',
    548: 'applefile', 623: 'ipmi', 626: 'mac', 631: 'cups', 1194: 'openvpn', 1434: 'mssql',
    1701: 'l2tp', 1755: 'mms', 1761: 'landesk', 1900: 'ssdp', 2302: 'halo', 2362: 'digiman',
    3283: 'ard', 3389: 'rdpeudp', 3478: 'stun/stunv2/ovh', 3702: 'wsd/wsdv2', 3784: 'bfd',
    5060: 'sip', 5093: 'sentinel', 5351: 'rain', 5353: 'mdns', 5632: 'pca', 5683: 'coap',
    6881: 'bittorrent/dht', 7777: 'samp/unknown', 9761: 'insteon', 9987: 'ts3/ts3voxility',
    10001: 'ubiquiti', 10074: 'mitel', 10080: 'amanda', 11211: 'memcached',
    17185: 'vxworks', 27015: 'valve', 27036: 'steam', 27960: 'quake', 30120: 'fivem',
    32414: 'plex', 37018: 'lantronix', 37810: 'dvr', 41794: 'crestron'
}
PORT_PAYLOAD_PATTERNS = {
    19: [b'A'], 17185: [b'\x1a\x09\xfa\xba'], 32414: [b'\x4d'],
    3478: [b'\x00\x01\x00\x00\x21\x12\xa4\x42', b'\x00\x01\x00\x08\x12\x23\x34\x45'],
    6881: [b'\x64\x31\x3a\x61\x64\x32\x3a\x69\x64\x32\x30\x3a'], 9761: [b'\x02\x60', b'\x01\x01\x04\x06'],
    1194: [b'\x38'], 520: [b'\x01\x01\x00\x00'], 443: [b'\x01\x00\x00\x00\x00\x00\x00\x00\x00'],
    17: [b'\x0d'], 80: [b'\x0e\x00\x00\x00', b'\x02\x04\x05\xb4'], 1755: [b'\x8f\xcd\x00\x09'],
    523: [b'\x44\x42\x32\x47\x45\x54\x41\x44\x44\x52'], 7777: [b'\x53\x41\x4d\x50', b'\xff'],
    2362: [b'\x44\x49\x47\x49\x00\x01\x00\x06'], 10074: [b'\x63\x61\x6c\x6c\x2e\x73\x74\x61\x72\x74'],
    5351: [b'\x00\x00'], 548: [b'\x00\x03\x00\x01\x00\x00\x00\x00'], 1761: [b'\x54\x4e\x4d\x50\x04\x00\x00\x00'],
    5632: [b'\x4e\x51'], 2302: [b'\\status\\'], 10080: [b'Amanda '],
    631: [b'\x06\x06\x06\x06'], 7: [b'\x0D\x0A\x0D\x0A'], 1701: [b'\xc8\x02\x00\x4c'],
    500: [b'\x6e\x32\x4e\x49', b'\x21\x00\x00\x00'], 27960: [b'\xff\xff\xff\xffgetstatus'],
    9987: [b'\x05\xca\x7f\x16', b'\xff\xff\xff\xffgetstatus'],
    111: [b'er\n7'], 5060: [b'OPTIONS sip:', b'REGISTER sip:'],
    5353: [b'\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x09_services'],
    11211: [b'\x00\x01\x00\x00\x00\x01\x00\x00gets', b'VALUE ', b'VERSION '], 41794: [b'\x14'],
    427: [b'\x02\t\x00\x00\x1d\x00'], 3784: [b'\x56\xc8\xf4\xf9'], 3283: [b'\0\x14\0\x01\x03'],
    123: [b'\x17\x00\x03\x2a'], 1900: [b'M-SEARCH', b'HTTP/1.1 200 OK'], 389: [b'\x30\x84', b'\x30\x25'],
    53: [b'\xc4\x75\x01\x00\x00\x01'], 161: [b'\x30\x20\x02\x01\x01\x04\x06public'],
    69: [b'\x00\x01/x\x00netascii'], 137: [b'\xe5\xd8\x00\x00\x00\x01'],
    3389: [b'\x00\x00\x00\x00\x00\x00\x00\xff'], 37810: [b'DHIP'], 1434: [b'\x02'],
    623: [b'\x04\x00\x00\x00\x00\x00\x00\x01'], 37018: [b'\x00\x00\x00\xf8'], 27036: [b'\xff\xff\xff\xff!L_\xa0'],
    5093: [b'z\x00\x00\x00\x00\x00'], 30120: [b'\xff\xff\xff\xffgetstatus'],
    5683: [b'@\x01\x01\x01\xbb.well-known'], 10001: [b'\x01\x00\x00\x00'],
    27015: [b'\xff\xff\xff\xffTSource Engine'],
    177: [b'\x00\x01\x00\x02\x00\x01\x00'], 3702: [b'<s:Envelope', b'<:/>'],
}
HTML_CONTENT = """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DDoS Protection Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        :root {
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --border-color: #334155;
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
            --accent-green: #22c55e;
            --accent-yellow: #facc15;
            --accent-red: #ef4444;
            --accent-blue: #38bdf8;
            --accent-purple: #a78bfa;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            margin: 0;
            padding: 20px 20px 50px 20px;
        }

        .dashboard-container {
            display: grid;
            grid-template-columns: repeat(12, 1fr);
            gap: 20px;
            max-width: 1600px;
            margin: auto;
        }

        header {
            grid-column: 1 / -1;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 15px;
            border-bottom: 1px solid var(--border-color);
            flex-wrap: wrap;
        }

        header h1 {
            color: var(--accent-green);
            font-size: 1.8rem;
            margin: 0;
        }

        .status-indicator {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .status-dot {
            width: 1rem;
            height: 1rem;
            border-radius: 50%;
            background-color: var(--accent-green);
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, .7); }
            70% { box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }
            100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
        }

        .header-info {
            text-align: right;
            color: var(--text-secondary);
        }

        .kpi-card {
            background-color: var(--bg-secondary);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }

        .kpi-card .value {
            font-size: 2.5rem;
            font-weight: 700;
            margin: 5px 0;
        }

        .kpi-card .label {
            font-size: .9rem;
            color: var(--text-secondary);
            text-transform: uppercase;
        }

        .kpi-pps { grid-column: 1 / 4; color: var(--accent-blue); }
        .kpi-mbps { grid-column: 4 / 7; color: var(--accent-purple); }
        .kpi-blocked { grid-column: 7 / 10; color: var(--accent-red); }
        .kpi-runtime { grid-column: 10 / 13; color: var(--accent-yellow); }

        .panel {
            background-color: var(--bg-secondary);
            border-radius: 12px;
            padding: 20px;
            /* display:flex wird hier nicht mehr für das Layout im Chart benötigt */
        }

        .panel h2 {
            margin: 0 0 15px 0;
            font-size: 1.2rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 10px;
        }
        
        #chart-panel {
            grid-column: 1 / -1;
        }
        
        .table-container {
            overflow-y: auto;
            max-height: 300px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
            font-size: .9rem;
        }

        thead {
            position: sticky;
            top: 0;
            background-color: #2a3a50;
        }

        .status-blocked { color: var(--accent-red); font-weight: 700; }
        .status-watching { color: var(--text-secondary); }

        #sources-panel { grid-column: 1 / 7; }
        #blocked-panel { grid-column: 7 / 13; }
        #protocols-panel { grid-column: 1 / 5; }
        #log-panel { grid-column: 5 / 13; }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <header>
            <div class="status-indicator">
                <div id="connection-status" class="status-dot" title="Verbunden"></div>
                <h1>DDoS Protection Dashboard</h1>
            </div>
            <div class="header-info">
                <div>Überwache: <strong id="target-ip" style="color: var(--accent-blue);">...</strong></div>
                <div>Block-Schwelle: <strong id="block-threshold" style="color: var(--accent-yellow);">...</strong> PPS</div>
            </div>
        </header>

        <div class="kpi-card kpi-pps"><div id="kpi-pps-value" class="value">0</div><div class="label">Pakete / Sekunde</div></div>
        <div class="kpi-card kpi-mbps"><div id="kpi-mbps-value" class="value">0.0</div><div class="label">MBit / Sekunde</div></div>
        <div class="kpi-card kpi-blocked"><div id="kpi-blocked-value" class="value">0</div><div class="label">Aktive Blocks</div></div>
        <div class="kpi-card kpi-runtime"><div id="kpi-runtime-value" class="value">0s</div><div class="label">Laufzeit</div></div>

        <div id="chart-panel" class="panel">
            <h2>Angriffs-Intensität (PPS)</h2>
            <canvas id="ppsChart"></canvas>
        </div>
        
        <div id="sources-panel" class="panel">
            <h2>Top Angriffs-Quellen</h2>
            <div class="table-container">
                <table>
                    <thead><tr><th>IP-Adresse</th><th>Protokoll</th><th>Rate (PPS)</th><th>Status</th></tr></thead>
                    <tbody id="amp-table-body"></tbody>
                </table>
            </div>
        </div>

        <div id="blocked-panel" class="panel">
            <h2>Aktuell blockierte IPs</h2>
            <div class="table-container">
                <table>
                    <thead><tr><th>IP-Adresse</th><th>Verbleibende Zeit</th></tr></thead>
                    <tbody id="blocked-table-body"></tbody>
                </table>
            </div>
        </div>

        <div id="protocols-panel" class="panel">
            <h2>Protokoll-Verteilung</h2>
            <div id="protocol-list"></div>
        </div>

        <div id="log-panel" class="panel">
            <h2>Live Paket-Log</h2>
            <div id="packet-log" style="font-family: 'Courier New', monospace; font-size: 0.85rem; white-space: nowrap; overflow-y: auto; max-height: 250px;"></div>
        </div>
    </div>
<script>
    const elements = {
        connectionStatus: document.getElementById("connection-status"),
        targetIp: document.getElementById("target-ip"),
        blockThreshold: document.getElementById("block-threshold"),
        kpiPps: document.getElementById("kpi-pps-value"),
        kpiMbps: document.getElementById("kpi-mbps-value"),
        kpiBlocked: document.getElementById("kpi-blocked-value"),
        kpiRuntime: document.getElementById("kpi-runtime-value"),
        ampTableBody: document.getElementById("amp-table-body"),
        blockedTableBody: document.getElementById("blocked-table-body"),
        protocolList: document.getElementById("protocol-list"),
        packetLog: document.getElementById("packet-log"),
        ppsChartCanvas: document.getElementById("ppsChart").getContext("2d")
    };
    let ppsChart;

    function initializeChart() {
        ppsChart = new Chart(elements.ppsChartCanvas, {
            type: "line",
            data: {
                labels: Array(60).fill(""),
                datasets: [{
                    label: "Pakete pro Sekunde",
                    data: Array(60).fill(0),
                    borderColor: "rgba(56, 189, 248, 0.8)",
                    backgroundColor: "rgba(56, 189, 248, 0.1)",
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: .4,
                    fill: !0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                aspectRatio: 3,
                scales: {
                    y: { beginAtZero: !0, suggestedMax: 100, ticks: { color: "var(--text-secondary)" } },
                    x: { ticks: { display: !1 } }
                },
                plugins: { legend: { display: !1 } }
            }
        });
    }

    function updateDashboard(e) {
        const t = new Set(e.blocked_ips.map(e => e.ip));
        elements.targetIp.textContent = e.target_ip, elements.blockThreshold.textContent = e.block_threshold, elements.kpiPps.textContent = e.total_pps.toFixed(0), elements.kpiMbps.textContent = e.total_mbps.toFixed(1), elements.kpiBlocked.textContent = e.blocked_ips.length, elements.kpiRuntime.textContent = formatRuntime(e.script_runtime), updateTable(elements.ampTableBody, e.amplification_sources, n => {
            const o = t.has(n.ip),
                l = o ? '<td class="status-blocked">Blocked</td>' : '<td class="status-watching">Watching</td>';
            return `<tr><td>${n.ip}</td><td>${n.proto}</td><td>${n.rate.toFixed(1)}</td>${l}</tr>`
        }), updateTable(elements.blockedTableBody, e.blocked_ips, e => `<tr><td>${e.ip}</td><td>${e.expires_in}s</td></tr>`), updateList(elements.protocolList, e.protocol_distribution, e => `<div class="protocol-item"><span>${e[0]}</span> <strong>${e[1]} Pakete</strong></div>`), elements.packetLog.innerHTML = e.recent_packets.slice().reverse().map(e => `<div><span style="color:var(--text-secondary);">${e.time}</span> <span style="color:var(--accent-red);">(${e.proto})</span> <span>${e.srcIp}:${e.srcPort} -> ${e.dstIp}:${e.dstPort}</span> <span style="color:var(--accent-purple);">len ${e.len}</span></div>`).join(""), updateChart(e.pps_history)
    }

    function updateTable(e, t, n) { e.innerHTML = t.map(n).join("") }
    function updateList(e, t, n) { e.innerHTML = t.map(n).join("") }
    
    function updateChart(history) {
        const chartData = Array(60).fill(null);
        const recentHistory = history.slice(-60);
        const startIndex = 60 - recentHistory.length;
        recentHistory.forEach((value, index) => {
            chartData[startIndex + index] = value;
        });
        ppsChart.data.datasets[0].data = chartData;
        ppsChart.update("none");
    }

    function formatRuntime(e) {
        const t = Math.floor(e / 86400),
            n = Math.floor(e % 86400 / 3600),
            o = Math.floor(e % 3600 / 60),
            l = Math.floor(e % 60);
        return [t > 0 ? `${t}d` : "", n > 0 ? `${n}h` : "", o > 0 ? `${o}m` : "", `${l}s`].filter(Boolean).join(" ")
    }
    async function fetchData() {
        try {
            const e = await fetch("/data");
            if (!e.ok) throw new Error("Network error");
            const t = await e.json();
            updateDashboard(t), elements.connectionStatus.title = "Verbunden"
        } catch (e) {
            console.error("Fetch Error:", e), elements.connectionStatus.style.animation = "none", elements.connectionStatus.style.backgroundColor = "var(--accent-red)", elements.connectionStatus.title = "Verbindung fehlgeschlagen"
        }
    }
    document.addEventListener("DOMContentLoaded", () => {
        initializeChart(), fetchData(), setInterval(fetchData, 1e3)
    });
</script>
</body>
</html>"""

# -------------------- Utilities --------------------

def ensure_python_packages(packages: list[str]):
    """Versucht fehlende Pakete per pip zu installieren. Wir beenden bei Fehlschlag.
    Diese Funktion nur auf ausdrücklichen Wunsch ausführen (z.B. beim Paketieren nicht nötig).
    """
    missing = []
    for p in packages:
        try:
            __import__(p)
        except ImportError:
            missing.append(p)
    if not missing:
        return
    logging.info("Fehlende Pakete erkannt: %s. Versuche Installation...", missing)
    for pkg in missing:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", pkg], check=True)
            logging.info("%s installiert", pkg)
        except subprocess.CalledProcessError:
            logging.critical("Automatische Installation von %s fehlgeschlagen. Bitte manuell installieren.", pkg)
            raise SystemExit(1)


def setup_logging(log_file: str | None = "ddos_protector.log"):
    """Setzt ein konsistentes Logging-Setup.
    RotatingFileHandler ist Standard, fallback auf Console-only wenn nicht möglich.
    """
    root = logging.getLogger()
    if root.handlers:
        root.handlers.clear()
    root.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s/%(processName)s] %(message)s")
    ch = logging.StreamHandler(sys.stderr)
    ch.setFormatter(fmt)
    root.addHandler(ch)
    if log_file:
        try:
            fh = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)
            fh.setFormatter(fmt)
            root.addHandler(fh)
        except Exception:
            root.warning("Konnte Log-Datei '%s' nicht anlegen. Weiter mit Console-Logging.", log_file)


def create_default_config(path: str):
    parser = ConfigParser()
    for section, kv in DEFAULTS.items():
        parser[section] = kv
    with open(path, "w") as f:
        parser.write(f)
    logging.info("Standard-Konfiguration erzeugt: %s", path)


def load_config(path: str = DEFAULT_CONFIG_PATH):
    parser = ConfigParser()
    if not os.path.exists(path):
        logging.warning("Konfigurationsdatei '%s' nicht gefunden. Erstelle Default.", path)
        create_default_config(path)
    parser.read(path)
    CONFIG['ENABLE_AUTO_BLOCK'] = parser.getboolean('Mitigation', 'enable_auto_block', fallback=True)
    CONFIG['BLOCK_THRESHOLD_PPS_PER_SOURCE'] = parser.getint('Mitigation', 'block_threshold_pps_per_source', fallback=50)
    CONFIG['BLOCK_DURATION_IP'] = parser.getint('Mitigation', 'block_duration_ip', fallback=300)
    CONFIG['TARGET_IP'] = parser.get('Network', 'target_ip', fallback='')
    w = parser.get('Whitelist', 'whitelisted_ips', fallback='127.0.0.1')
    CONFIG['WHITELISTED_IPS'] = {ip.strip() for ip in w.split(',') if ip.strip()}
    logging.info("Konfiguration geladen: %s", path)


# -------------------- Packet Handling --------------------
# Die scapy-abhängigen Funktionen werden nur importiert, wenn wir tatsächlich sniffen.


def packet_sniffer(queue: Queue, stop_event: Event, bpf_filter: str, iface: str | None = None):
    from scapy.all import sniff, IP, UDP
    logger = logging.getLogger('sniffer')
    logger.info("Sniffer startet. iface=%s filter=%s", iface, bpf_filter)

    def _prn(pkt):
        try:
            if IP in pkt and UDP in pkt:
                ip = pkt[IP]
                udp = pkt[UDP]
                item = (ip.src, int(udp.sport), ip.dst, int(udp.dport), len(pkt), time.time())
                try:
                    queue.put_nowait(item)
                except Full:
                    # Drop on full. Log very rarely.
                    pass
        except Exception as e:
            logger.debug("Paket-Handler-Fehler: %s", e)

    while not stop_event.is_set():
        try:
            sniff(filter=bpf_filter, prn=_prn, store=0, timeout=1, iface=iface)
        except Exception as e:
            logger.error("Sniffer-Fehler: %s", e)
            time.sleep(1)


def packet_processor(queue: Queue, shared_snapshot: dict, stop_event: Event, start_time: float):
    logger = logging.getLogger('processor')
    logger.info("Processor startet")
    window = deque()
    per_src = Counter()
    pps_history = deque([0] * 60, maxlen=60)
    bps_history = deque([0] * 60, maxlen=60)

    last_snapshot = time.time()
    last_sec = int(last_snapshot)
    packets_in_sec = 0
    bytes_in_sec = 0

    while not stop_event.is_set():
        now = time.time()
        try:
            src, sport, dst, dport, length, ts = queue.get(timeout=0.1)
            window.append((src, sport, dst, dport, length, ts))
            per_src[f"{src}:{sport}"] += 1
            packets_in_sec += 1
            bytes_in_sec += length
            if int(ts) > last_sec:
                pps_history.append(packets_in_sec)
                bps_history.append(bytes_in_sec)
                packets_in_sec = 0
                bytes_in_sec = 0
                last_sec = int(ts)
        except Empty:
            if int(now) > last_sec:
                pps_history.append(packets_in_sec)
                bps_history.append(bytes_in_sec)
                packets_in_sec = 0
                bytes_in_sec = 0
                last_sec = int(now)

        cutoff = now - SLIDING_WINDOW_SECONDS
        while window and window[0][5] < cutoff:
            old_src, old_sport, *_ = window.popleft()
            key = f"{old_src}:{old_sport}"
            per_src.subtract({key: 1})
            if per_src[key] <= 0:
                del per_src[key]

        if now - last_snapshot >= SNAPSHOT_INTERVAL:
            sources = []
            proto_counter = Counter()
            for key, cnt in per_src.most_common(200):
                try:
                    ip, sport_str = key.rsplit(':', 1)
                    sport = int(sport_str)
                    proto = PORT_TO_PROTOCOL_NAME.get(sport, f"p-{sport}")
                    rate = cnt / SLIDING_WINDOW_SECONDS
                    sources.append({"ip": ip, "proto": proto, "rate": rate})
                    proto_counter[proto] += cnt
                except Exception:
                    continue

            tail = list(window)[-100:]
            recent_packets = []
            for src, sport, dst, dport, length, ts in tail:
                recent_packets.append({
                    "time": time.strftime('%H:%M:%S', time.localtime(ts)),
                    "proto": PORT_TO_PROTOCOL_NAME.get(sport, f"p-{sport}"),
                    "srcIp": src,
                    "srcPort": sport,
                    "dstIp": dst,
                    "dstPort": dport,
                    "len": length
                })

            current_pps = pps_history[-1] if pps_history else 0
            current_mbps = (bps_history[-1] * 8) / 1_000_000 if bps_history else 0

            shared_snapshot['latest_snapshot'] = {
                "amplification_sources": sources,
                "recent_packets": recent_packets,
                "script_runtime": int(now - start_time),
                "target_ip": CONFIG.get('TARGET_IP') or "Alle lokalen IPs",
                "total_pps": current_pps,
                "total_mbps": round(current_mbps, 3),
                "pps_history": list(pps_history),
                "protocol_distribution": proto_counter.most_common(10),
                "block_threshold": CONFIG.get('BLOCK_THRESHOLD_PPS_PER_SOURCE')
            }
            last_snapshot = now


# -------------------- Mitigation --------------------

def setup_firewall():
    """Initialisiert die plattformspezifischen Firewall-Regeln."""
    logger = logging.getLogger('firewall')
    if SYSTEM_PLATFORM == 'Linux':
        logger.info('Einrichten ipset/iptables Regeln (erfordert root).')
        try:
            # ipset anlegen (kann fehlschlagen, wenn es schon existiert)
            subprocess.run(["ipset", "create", "ddos_blocklist", "hash:ip", "timeout", "0"], stderr=subprocess.DEVNULL)
        except Exception:
            pass
        try:
            # iptables Regel anlegen (nur wenn sie noch nicht existiert)
            cmd = ["iptables", "-C", "INPUT", "-m", "set", "--match-set", "ddos_blocklist", "src", "-j", "DROP"]
            if subprocess.run(cmd, stderr=subprocess.DEVNULL).returncode != 0:
                subprocess.run(["iptables", "-I", "INPUT", "1", "-m", "set", "--match-set", "ddos_blocklist", "src", "-j", "DROP"], check=True)
        except Exception:
            logger.exception('Fehler beim Anlegen iptables Regel')
            
    elif SYSTEM_PLATFORM == 'Windows':
        # Auf Windows werden Regeln pro IP dynamisch beim Blocken hinzugefügt. Keine initiale Setup nötig.
        logger.info('Windows Firewall Regeln werden on-the-fly erstellt.')
        return
        
    else:
        logger.info('Firewall-Setup für %s nicht unterstützt. Überspringe.', SYSTEM_PLATFORM)


def cleanup_firewall():
    if SYSTEM_PLATFORM != 'Linux':
        return
    logger = logging.getLogger('firewall')
    logger.info('Bereinige ipset/iptables Regeln.')
    try:
        subprocess.run(["iptables", "-D", "INPUT", "-m", "set", "--match-set", "ddos_blocklist", "src", "-j", "DROP"], stderr=subprocess.DEVNULL)
    except Exception:
        pass
    try:
        subprocess.run(["ipset", "destroy", "ddos_blocklist"], stderr=subprocess.DEVNULL)
    except Exception:
        pass


def monitor_and_mitigate(shared_snapshot: dict, stop_event: Event):
    logger = logging.getLogger('mitigator')
    logger.info('Mitigation Prozess gestartet')
    blocked = {}  # ip -> expiry

    def run_cmd(cmd):
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            logger.debug('Command failed: %s -> %s', ' '.join(cmd), e)
            return False

    def block_ip(ip):
        if ip in blocked or ip in CONFIG['WHITELISTED_IPS']:
            return
        expiry = time.time() + CONFIG['BLOCK_DURATION_IP']
        blocked[ip] = expiry
        logger.critical('Blockiere IP %s für %s Sekunden', ip, CONFIG['BLOCK_DURATION_IP'])
        if SYSTEM_PLATFORM == 'Linux':
            run_cmd(["ipset", "add", "ddos_blocklist", ip, "timeout", str(CONFIG['BLOCK_DURATION_IP']), "-exist"])
        elif SYSTEM_PLATFORM == 'Windows':
            run_cmd(["netsh", "advfirewall", "firewall", "add", "rule", f"name=DDoS_Block_{ip}", "dir=in", "action=block", f"remoteip={ip}"])

    def unblock_expired():
        now = time.time()
        for ip, exp in list(blocked.items()):
            if exp <= now:
                logger.info('Block abgelaufen: %s', ip)
                if SYSTEM_PLATFORM == 'Windows':
                    run_cmd(["netsh", "advfirewall", "firewall", "delete", "rule", f"name=DDoS_Block_{ip}"])
                del blocked[ip]

    while not stop_event.is_set():
        if CONFIG.get('ENABLE_AUTO_BLOCK'):
            snap = shared_snapshot.get('latest_snapshot', {})
            for s in snap.get('amplification_sources', []):
                if s.get('rate', 0) > CONFIG['BLOCK_THRESHOLD_PPS_PER_SOURCE']:
                    block_ip(s['ip'])
            unblock_expired()
            shared_snapshot['blocked_ips'] = [{'ip': ip, 'expires_in': int(exp - time.time())} for ip, exp in blocked.items()]
        time.sleep(1)


# -------------------- Webserver --------------------

def web_server(shared_snapshot: dict, stop_event: Event, host: str = '0.0.0.0', port: int = 5000):
    """Startet den Flask Webserver und verwendet eine dedizierte Funktion für den Shutdown."""
    
    # Imports anpassen
    from flask import Flask, jsonify, request 
    from flask_cors import CORS
    import requests # Bleibt drin für den Fallback-Shutdown

    app = Flask(__name__)
    CORS(app)
    app.config['PORT'] = port
    
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    # --- SHUTDOWN-LOGIK ---
    def shutdown_server():
        """Die Funktion, die den internen Werkzeug-Server beendet."""
        # Wichtig: Die Flask-request-Kontext-Abhängigkeit vermeiden
        shutdown_func = request.environ.get('werkzeug.server.shutdown')
        if shutdown_func:
            shutdown_func()
        
    @app.route('/')
    def index():
        return HTML_CONTENT

    @app.route('/data')
    def data():
        try:
            snap = shared_snapshot.get('latest_snapshot', {})
            snap = dict(snap)
            snap['blocked_ips'] = shared_snapshot.get('blocked_ips', [])
            return jsonify(snap)
        except (ConnectionRefusedError, FileNotFoundError, BrokenPipeError, AttributeError):
            # Manager-Verbindung verloren (typisch während Strg+C)
            logging.getLogger().warning("Manager-Verbindung unterbrochen. Erzwinge Flask-Shutdown.")
            
            # NEU: Direkter Aufruf der internen Shutdown-Funktion, um sofort zu reagieren.
            # Dies ist immer noch heikel, da es außerhalb eines Request-Kontexts passiert, 
            # aber wir müssen es versuchen, bevor der Hauptprozess SIGTERM sendet.
            try:
                # Da wir das 'request.environ' nur im /shutdown-Endpoint haben, 
                # schicken wir lieber den POST.
                requests.post(f'http://127.0.0.1:{app.config["PORT"]}/shutdown')
            except requests.exceptions.ConnectionError:
                 pass # Ignorieren, wenn der Server schon fast down ist.
                 
            return jsonify({"status": "Server shutting down"}), 503
        
    @app.route('/shutdown', methods=['POST'])
    def shutdown():
        # Die saubere Methode, den Server zu beenden
        func = request.environ.get('werkzeug.server.shutdown')
        if func:
            func()
        return 'Server shutting down...', 200

    # NEU: Starten des Servers im Hintergrund-Thread
    from threading import Thread
    server_thread = Thread(target=lambda: app.run(host=host, port=port, threaded=False, debug=False))
    server_thread.daemon = True
    server_thread.start()

    logging.getLogger().info('Webserver startet auf Port %s', port)

    # Der Prozess selbst wartet nun auf das stop_event.
    try:
        # Warten auf das Beendigungs-Signal vom Hauptprozess (Strg+C)
        stop_event.wait()
        
        # Wenn das Event gesetzt ist, lösen wir den Shutdown extern aus.
        logging.getLogger().info('stop_event im WebServer-Prozess gesetzt. Sende externes Shutdown-Signal.')
        try:
             # Externe POST-Anfrage an uns selbst (funktioniert zuverlässiger als interne Calls)
            requests.post(f'http://127.0.0.1:{app.config["PORT"]}/shutdown')
        except requests.exceptions.ConnectionError:
            pass
            
    except Exception as e:
        logging.getLogger().exception('Webserver-Prozess Fehler während Wartezeit: %s', e)
    finally:
        # Warten Sie kurz, bis der Server-Thread beendet ist.
        server_thread.join(timeout=5)
        if server_thread.is_alive():
             logging.getLogger().warning('Server-Thread nicht sauber beendet.')
             
        logging.getLogger().info('Webserver-Prozess beendet.')

# -------------------- Helpers --------------------

def setup_signal_handlers(stop_event: Event, cleanup_func=None):
    # Passen Sie die Signatur von _handler an, um cleanup_func nicht zu verwenden
    def _handler(signum, frame):
        logging.getLogger().info('Signal %s erhalten. Stoppe.', signum)
        stop_event.set()
        # >>> ENTFERNEN SIE DEN AUFRUF ZU cleanup_func HIER <<<
        # Dadurch wird verhindert, dass die Firewall-Cleanup mehrmals aufgerufen wird,
        # einmal durch den Signal-Handler und einmal im finally-Block.

    for s in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(s, _handler)
        except Exception:
            pass


# -------------------- Main --------------------

def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description='DDoS Protector - Produktionsversion')
    parser.add_argument('--config', default=DEFAULT_CONFIG_PATH, help='Pfad zur config.ini')
    parser.add_argument('--no-install', action='store_true', help='Keine automatische Paket-Installation')
    parser.add_argument('--list-interfaces', action='store_true', help='Zeige verfügbare Netzwerkinterfaces und beende')
    parser.add_argument('--iface', default=None, help='Spezifisches Interface zum Sniffen')
    parser.add_argument('--port', type=int, default=5000, help='Webserver Port')
    args = parser.parse_args(argv)

    setup_logging()
    logging.getLogger().info('Starte DDoS Protector')

    if not args.no_install:
        try:
            ensure_python_packages(REQUIREMENTS)
        except SystemExit:
            logging.getLogger().critical('Benötigte Pakete konnten nicht installiert werden. Beende.')
            raise

    load_config(args.config)

    # Optional: Interface Listing
    if args.list_interfaces:
        try:
            from scapy.all import get_if_list
            print('\n'.join(get_if_list()))
        except Exception as e:
            logging.getLogger().exception('Kann Interfaces nicht auflisten: %s', e)
        return

    # Firewall vorbereiten
    try:
        setup_firewall()
    except Exception:
        logging.getLogger().exception('Firewall Setup fehlgeschlagen. Fortsetzen ohne Firewall.')

    manager = Manager()
    shared_snapshot = manager.dict()
    shared_snapshot['blocked_ips'] = []

    stop_event = Event()
    setup_signal_handlers(stop_event, cleanup_firewall)

    packet_q = Queue(maxsize=QUEUE_MAXSIZE)
    start_time = time.time()

    # BPF-Filter
    target = CONFIG.get('TARGET_IP') or ''
    if target:
        bpf = f"udp and dst host {target}"
    else:
        ports = ' or '.join([f'src port {p}' for p in PORT_TO_PROTOCOL_NAME.keys()]) or 'udp'
        bpf = f"udp and ({ports})"

    procs = []
    # Prozesse starten
    procs.append(Process(name='Processor', target=packet_processor, args=(packet_q, shared_snapshot, stop_event, start_time)))
    procs.append(Process(name='Mitigator', target=monitor_and_mitigate, args=(shared_snapshot, stop_event)))
    procs.append(Process(name='WebServer', target=web_server, args=(shared_snapshot, stop_event, '0.0.0.0', args.port)))

    # Sniffer pro Interface
    try:
        from scapy.all import get_if_list, get_if_addr
        ifaces = get_if_list()
        if args.iface:
            iface_list = [args.iface]
        elif target:
            iface_list = [i for i in ifaces if get_if_addr(i) == target]
            if not iface_list:
                iface_list = [i for i in ifaces if 'lo' not in i.lower()]
        else:
            iface_list = [i for i in ifaces if 'lo' not in i.lower()]
    except Exception:
        iface_list = [None]

    for iface in iface_list:
        name = f"Sniffer-{iface or 'any'}"
        procs.append(Process(name=name, target=packet_sniffer, args=(packet_q, stop_event, bpf, iface)))

    # Prozesse starten
    for p in procs:
        p.daemon = False
        p.start()

    logging.getLogger().info('Dienst gestartet. Dashboard: http://127.0.0.1:%s', args.port)
    
    # Der Hauptprozess wartet einfach, bis das stop_event gesetzt wird,
    # entweder durch einen Signal-Handler oder einen anderen Prozess.
    try:
        while not stop_event.is_set():
            time.sleep(0.5)
    except KeyboardInterrupt:
        # Dies wird im Normalfall durch den Handler abgefangen, dient aber als Fallback
        logging.getLogger().info('KeyboardInterrupt direkt erhalten. Stoppe Prozesse...')
        stop_event.set()
        
    finally:
        logging.getLogger().info('Beginne sauberes Herunterfahren...')
        stop_event.set() 

        # 1. WebServer zum Selbst-Shutdown zwingen und auf Beendigung warten
        web_process = next((p for p in procs if 'WebServer' in p.name), None)
        if web_process and web_process.is_alive():
            # Warten, dass der Webserver sich selbst über den Shutdown-Thread beendet
            web_process.join(timeout=5)
            if web_process.is_alive():
                logging.getLogger().warning('%s reagiert nicht. Terminiere.', web_process.name)
                web_process.terminate()
                web_process.join(timeout=2)
                
        # 2. Alle anderen Prozesse beenden (Processor, Mitigator, Sniffer)
        for p in procs:
            if p.is_alive() and 'WebServer' not in p.name:
                p.join(timeout=3)
                if p.is_alive():
                    logging.getLogger().warning('%s reagiert nicht. Terminiere.', p.name)
                    p.terminate()
                    p.join(timeout=2)
                    
        # 3. Den Manager manuell beenden (sehr wichtig!)
        logging.getLogger().info('Beende Multiprocessing Manager...')
        manager.shutdown() # <<< NEUE WICHTIGE ZEILE HINZUFÜGEN
        
        # 4. Cleanup (Firewall)
        logging.getLogger().info('Bereinige Firewall...')
        cleanup_firewall() # Nur hier, nachdem alle Worker beendet sind

        logging.getLogger().info('Beendet')


if __name__ == '__main__':
    main()
