import multiprocessing
import requests
import time
from bitcoinlib.mnemonic import Mnemonic
from bitcoinlib.keys import HDKey
import webview
import random  


THREADS = 50
API_URL = "https://blockstream.info/api/address/{address}"
DELAY = 0.1




HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Cosmic Wallet Hunter</title>
    <style>
        :root {
            --space-dark: #0B0D21;
            --space-purple: #6A00FF;
            --neon-blue: #00F0FF;
            --neon-pink: #FF00F0;
            --star-white: #F0F0FF;
        }
        body {
            background-color: var(--space-dark);
            color: var(--star-white);
            font-family: 'Orbitron', sans-serif;
            margin: 0;
            padding: 0;
            background-image: 
                radial-gradient(circle at 20% 30%, rgba(106, 0, 255, 0.15) 0%, transparent 20%),
                radial-gradient(circle at 80% 70%, rgba(0, 240, 255, 0.15) 0%, transparent 20%);
            min-height: 100vh;
        }
        @font-face {
            font-family: 'Orbitron';
            src: url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 1px solid var(--neon-blue);
            margin-bottom: 30px;
            position: relative;
        }
        .header h1 {
            font-size: 2.5rem;
            margin: 0;
            background: linear-gradient(90deg, var(--neon-blue), var(--neon-pink));
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            text-shadow: 0 0 10px rgba(0, 240, 255, 0.3);
        }
        .header p {
            color: var(--star-white);
            opacity: 0.8;
        }
        .panel {
            background: rgba(11, 13, 33, 0.7);
            border: 1px solid var(--space-purple);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 0 20px rgba(106, 0, 255, 0.2);
            backdrop-filter: blur(5px);
        }
        .panel-title {
            font-size: 1.2rem;
            margin-top: 0;
            color: var(--neon-blue);
            border-bottom: 1px solid var(--space-purple);
            padding-bottom: 10px;
        }
        button {
            background: linear-gradient(135deg, var(--space-purple), var(--neon-blue));
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 4px;
            cursor: pointer;
            font-family: 'Orbitron', sans-serif;
            font-weight: bold;
            margin-right: 10px;
            transition: all 0.3s;
            box-shadow: 0 0 15px rgba(0, 240, 255, 0.3);
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 0 20px rgba(0, 240, 255, 0.5);
        }
        button:disabled {
            background: #333;
            box-shadow: none;
            transform: none;
            cursor: not-allowed;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .stat-card {
            background: rgba(0, 240, 255, 0.1);
            border: 1px solid var(--neon-blue);
            border-radius: 6px;
            padding: 15px;
            text-align: center;
        }
        .stat-value {
            font-size: 1.8rem;
            font-weight: bold;
            color: var(--neon-blue);
            margin: 5px 0;
        }
        .stat-label {
            font-size: 0.9rem;
            opacity: 0.8;
        }
        .wallet-card {
            background: rgba(106, 0, 255, 0.1);
            border: 1px solid var(--space-purple);
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 15px;
            position: relative;
            overflow: hidden;
        }
        .wallet-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, transparent, rgba(0, 240, 255, 0.05));
            pointer-events: none;
        }
        .wallet-mnemonic {
            color: var(--neon-pink);
            word-break: break-all;
            margin-bottom: 10px;
        }
        .wallet-address {
            color: var(--neon-blue);
            font-family: monospace;
            margin-bottom: 5px;
        }
        .wallet-balance {
            color: #00FF9D;
            font-weight: bold;
            font-size: 1.2rem;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-running {
            background-color: #00FF9D;
            box-shadow: 0 0 10px #00FF9D;
        }
        .status-stopped {
            background-color: #FF3D57;
            box-shadow: 0 0 10px #FF3D57;
        }
        .stars {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
        }
        .star {
            position: absolute;
            background: white;
            border-radius: 50%;
            animation: twinkle var(--duration) infinite ease-in-out;
        }
        @keyframes twinkle {
            0%, 100% { opacity: 0.2; }
            50% { opacity: 1; }
        }
        .login-panel {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(11, 13, 33, 0.9);
            border: 1px solid var(--neon-blue);
            border-radius: 8px;
            padding: 30px;
            width: 400px;
            max-width: 90%;
            box-shadow: 0 0 30px rgba(0, 240, 255, 0.3);
            z-index: 1000;
            text-align: center;
        }
        .login-panel h2 {
            margin-top: 0;
            color: var(--neon-blue);
        }
        .login-input {
            width: 100%;
            padding: 12px;
            margin: 15px 0;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid var(--space-purple);
            border-radius: 4px;
            color: white;
            font-family: 'Orbitron', sans-serif;
        }
        .login-input:focus {
            outline: none;
            border-color: var(--neon-blue);
            box-shadow: 0 0 10px rgba(0, 240, 255, 0.3);
        }
        .login-button {
            width: 100%;
            padding: 12px;
            margin-top: 10px;
        }
        .error-message {
            color: #FF3D57;
            margin-top: 10px;
            display: none;
        }
        .blur-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            backdrop-filter: blur(5px);
            z-index: 999;
            display: none;
        }
    </style>
</head>
<body>
    <div class="blur-overlay" id="blurOverlay"></div>
    
    <div class="login-panel" id="loginPanel">
        <h2>SYSTEM ACCESS</h2>
        <p>Enter your license key to continue</p>
        <input type="password" class="login-input" id="licenseKey" placeholder="License Key">
        <button class="login-button" onclick="verifyKey()">AUTHENTICATE</button>
        <div class="error-message" id="errorMessage">Invalid license key. Please try again.</div>
    </div>
    
    <div class="stars" id="stars"></div>
    
    <div class="container" id="mainContainer" style="display: none;">
        <div class="header">
            <h1>CRYPTO WALLET HUNTER (private)</h1>
            <p>Searching the blockchain database for working wallets</p>
        </div>
        
        <div class="panel">
            <h2 class="panel-title">CONTROL PANEL</h2>
            <button id="startBtn" onclick="startSearch()">ACTIVATE SCAN</button>
            <button id="stopBtn" onclick="stopSearch()" disabled>TERMINATE SCAN</button>
            <div style="margin-top: 15px;">
                <span id="statusIndicator" class="status-indicator status-stopped"></span>
                <span id="statusText">SCAN OFFLINE</span>
            </div>
        </div>
        
        <div class="panel">
            <h2 class="panel-title">SCAN STATISTICS</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">WALLETS SCANNED</div>
                    <div class="stat-value" id="checkedWallets">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">FOUNDED WALLETS</div>
                    <div class="stat-value" id="validWallets">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">RATE LIMITS</div>
                    <div class="stat-value" id="rateLimited">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">ERRORS</div>
                    <div class="stat-value" id="errors">0</div>
                </div>
            </div>
        </div>
        
        <div class="panel">
            <h2 class="panel-title">DISCOVERED WALLETS</h2>
            <div id="foundWallets">
                <div style="text-align: center; padding: 20px; opacity: 0.7;">
                    No wallets found yet...
                </div>
            </div>
        </div>
    </div>

    <script>
        function createStars() {
            const starsContainer = document.getElementById('stars');
            const starCount = 100;
            for (let i = 0; i < starCount; i++) {
                const star = document.createElement('div');
                star.className = 'star';
                const size = Math.random() * 2;
                const x = Math.random() * 100;
                const y = Math.random() * 100;
                const duration = 2 + Math.random() * 3;
                const delay = Math.random() * 5;
                star.style.width = `${size}px`;
                star.style.height = `${size}px`;
                star.style.left = `${x}%`;
                star.style.top = `${y}%`;
                star.style.setProperty('--duration', `${duration}s`);
                star.style.animationDelay = `${delay}s`;
                starsContainer.appendChild(star);
            }
        }
        function verifyKey() {
            const keyInput = document.getElementById('licenseKey').value;
            const errorElement = document.getElementById('errorMessage');
            pywebview.api.verify_key(keyInput).then(isValid => {
                if (isValid) {
                    document.getElementById('loginPanel').style.display = 'none';
                    document.getElementById('blurOverlay').style.display = 'none';
                    document.getElementById('mainContainer').style.display = 'block';
                } else {
                    errorElement.style.display = 'block';
                }
            });
        }
        function updateStats(data) {
            document.getElementById('checkedWallets').textContent = data.checked_wallets.toLocaleString();
            document.getElementById('validWallets').textContent = data.valid_wallets.toLocaleString();
            document.getElementById('rateLimited').textContent = data.rate_limited.toLocaleString();
            document.getElementById('errors').textContent = data.errors.toLocaleString();
            const statusIndicator = document.getElementById('statusIndicator');
            const statusText = document.getElementById('statusText');
            if (data.running) {
                statusIndicator.className = 'status-indicator status-running';
                statusText.textContent = 'SCAN ACTIVE';
                document.getElementById('startBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
            } else {
                statusIndicator.className = 'status-indicator status-stopped';
                statusText.textContent = 'SYSTEM OFFLINE';
                document.getElementById('startBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
            }
        }
        function updateFoundWallets(wallets) {
            const container = document.getElementById('foundWallets');
            if (wallets.length === 0) {
                container.innerHTML = `
                    <div style="text-align: center; padding: 20px; opacity: 0.7;">
                        No wallets found yet...
                    </div>
                `;
                return;
            }
            container.innerHTML = '';
            wallets.forEach(wallet => {
                const walletDiv = document.createElement('div');
                walletDiv.className = 'wallet-card';
                walletDiv.innerHTML = `
                    <div class="wallet-mnemonic">${wallet.mnemonic}</div>
                    <div class="wallet-address">${wallet.address}</div>
                    <div class="wallet-balance">${wallet.balance.toLocaleString()} SATOSHIS FOUND</div>
                `;
                container.appendChild(walletDiv);
            });
        }
        function startSearch() {
            pywebview.api.start_search().then(data => {
                updateStats(data);
            });
        }
        function stopSearch() {
            pywebview.api.stop_search().then(data => {
                updateStats(data);
            });
        }
        createStars();
        document.getElementById('blurOverlay').style.display = 'block';

        setInterval(() => {
            if (document.getElementById('loginPanel').style.display === 'none') {
                pywebview.api.get_stats().then(data => {
                    updateStats(data);
                    updateFoundWallets(data.found_wallets);
                });
            }
        }, 1000);
    </script>
</body>
</html>
"""

def check_wallet(stats):
    session = requests.Session()
    while stats['running']:
        try:
            mnemonic = Mnemonic().generate(strength=128)
            key = HDKey.from_passphrase(mnemonic)
            address = key.address()

            response = session.get(API_URL.format(address=address), timeout=8)

            with stats['lock']:
                stats['checked_wallets'] += 1

            if response.status_code == 200:
                data = response.json()
                balance = data.get('chain_stats', {}).get('funded_txo_sum', 0) - data.get('chain_stats', {}).get('spent_txo_sum', 0)
                if balance > 0:
                    wallet_info = {
                        'mnemonic': mnemonic,
                        'address': address,
                        'balance': balance
                    }
                    with stats['lock']:
                        stats['valid_wallets'] += 1
                        stats['found_wallets'].append(wallet_info)
            elif response.status_code == 429:
                with stats['lock']:
                    stats['rate_limited'] += 1
                time.sleep(DELAY)
                continue
            else:
                with stats['lock']:
                    stats['errors'] += 1
                time.sleep(DELAY)
                continue

        except Exception:
            with stats['lock']:
                stats['errors'] += 1
            time.sleep(DELAY)

class Api:
    def __init__(self, stats, pool):
        self.stats = stats
        self.pool = pool

    def verify_key(self, key):
        try:
            url = f"https://skidd2.pythonanywhere.com/api?key={key}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "valid":
                    with self.stats['lock']:
                        self.stats['authenticated'] = True
                    return True
        except Exception as e:
            print("error in verify_key:")
        return False

    def get_stats(self):
        if not self.stats['authenticated']:
            return None
        return {
            'checked_wallets': self.stats['checked_wallets'],
            'valid_wallets': self.stats['valid_wallets'],
            'rate_limited': self.stats['rate_limited'],
            'errors': self.stats['errors'],
            'running': self.stats['running'],
            'found_wallets': list(self.stats['found_wallets']),
        }

    def start_search(self):
        if not self.stats['authenticated']:
            return None
        if not self.stats['running']:
            self.stats['running'] = True
            for _ in range(THREADS):
                self.pool.apply_async(check_wallet, args=(self.stats,))
        return self.get_stats()

    def stop_search(self):
        if not self.stats['authenticated']:
            return None
        self.stats['running'] = False
        return self.get_stats()


if __name__ == '__main__':
    manager = multiprocessing.Manager()
    stats = manager.dict({
        'checked_wallets': 0,
        'valid_wallets': 0,
        'rate_limited': 0,
        'errors': 0,
        'running': False,
        'found_wallets': manager.list(),
        'authenticated': False,
        'lock': manager.Lock()
    })

    pool = multiprocessing.Pool(processes=THREADS)

    api = Api(stats, pool)

    window = webview.create_window(
        'Crypto Wallet Hunter',
        html=HTML,
        js_api=api,
        width=1200,
        height=800,
        resizable=True
    )
    webview.start()

    pool.close()
    pool.join()
