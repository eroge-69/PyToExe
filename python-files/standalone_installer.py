#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POLARIUM BOT - INSTALADOR ÚNICO
===============================

Download este arquivo e execute: python polarium_bot_installer.py

O instalador irá:
1. Verificar/instalar dependências
2. Baixar o código completo do bot
3. Configurar ambiente
4. Criar executável Windows
5. Preparar pacote portátil

Autor: Bot Trading Assistant
Versão: 2.0
"""

import os
import sys
import subprocess
import json
import shutil
import urllib.request
import zipfile
from pathlib import Path
import tempfile

class PolariumBotInstaller:
    def __init__(self):
        self.version = "2.0"
        self.base_path = Path.cwd()
        self.temp_dir = None
        
    def print_banner(self):
        """Exibe banner do instalador"""
        print(f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║           🤖 POLARIUM BOT INSTALLER v{self.version}             ║
║                                                          ║
║    Instalador automático para Windows                    ║
║    Cria executável completo e portátil                   ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

🚀 Iniciando instalação automatizada...
        """)
        
    def check_python_version(self):
        """Verifica versão do Python"""
        print("📋 Verificando Python...")
        
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ é necessário!")
            print(f"   Versão atual: {sys.version}")
            print("   Baixe em: https://python.org")
            return False
        
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
        return True
    
    def install_dependencies(self):
        """Instala dependências necessárias"""
        print("\n📦 Instalando dependências...")
        
        dependencies = [
            "playwright>=1.40.0",
            "pandas>=2.1.0", 
            "numpy>=1.25.0",
            "ta>=0.10.0",
            "aiofiles>=23.2.0",
            "websockets>=12.0",
            "fastapi>=0.104.0",
            "uvicorn>=0.24.0",
            "requests>=2.31.0",
            "pyinstaller>=6.0.0",
            "psutil>=5.9.0"
        ]
        
        try:
            # Atualizar pip
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "--upgrade", "pip"
            ])
            
            # Instalar dependências
            for dep in dependencies:
                print(f"   Instalando {dep}...")
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", dep
                ], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            
            print("✅ Dependências instaladas com sucesso!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao instalar dependências: {e}")
            return False
    
    def install_playwright_browsers(self):
        """Instala browsers do Playwright"""
        print("\n🌐 Instalando browsers do Playwright...")
        print("   Isso pode levar alguns minutos...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "playwright", "install", "chromium"
            ])
            print("✅ Browsers instalados!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Aviso: Erro ao instalar browsers: {e}")
            print("   O bot tentará instalar automaticamente na primeira execução")
            return True  # Não é crítico
    
    def create_bot_files(self):
        """Cria arquivos do bot"""
        print("\n📄 Criando arquivos do bot...")
        
        # Código principal do bot (versão simplificada)
        bot_code = '''import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('polarium_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PolariumBot:
    def __init__(self):
        self.config = self.load_config()
        self.is_running = False
        
    def load_config(self):
        """Carrega configurações"""
        config_file = Path("config.json")
        if not config_file.exists():
            return self.create_default_config()
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar config: {e}")
            return self.create_default_config()
    
    def create_default_config(self):
        """Cria configuração padrão"""
        config = {
            "polarium_url": "https://trade.polariumbroker.com/",
            "headless": False,
            "max_candles_history": 200,
            "min_confidence": 0.7,
            "rsi_oversold": 30,
            "rsi_overbought": 70,
            "enable_notifications": True,
            "save_signals": True,
            "indicators": {
                "rsi_period": 14,
                "macd_enabled": True,
                "bollinger_enabled": True,
                "ema_periods": [9, 21, 50]
            }
        }
        
        with open("config.json", "w", encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return config
    
    async def initialize_browser(self):
        """Inicializa browser"""
        try:
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.config["headless"],
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            self.page = await self.browser.new_page()
            
            logger.info("🚀 Abrindo Polarium Broker...")
            await self.page.goto(self.config["polarium_url"])
            
            # Aguardar carregamento
            try:
                await self.page.wait_for_selector("body", timeout=30000)
                logger.info("✅ Página carregada!")
                await self.create_overlay()
            except Exception as e:
                logger.error(f"Erro ao carregar página: {e}")
                
        except ImportError:
            logger.error("❌ Playwright não instalado! Execute: playwright install chromium")
            return False
        except Exception as e:
            logger.error(f"Erro ao inicializar browser: {e}")
            return False
        
        return True
    
    async def create_overlay(self):
        """Cria overlay de sinais"""
        overlay_js = """
        (function() {
            if (document.getElementById('trading-overlay')) return;
            
            const overlay = document.createElement('div');
            overlay.id = 'trading-overlay';
            overlay.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: rgba(0,0,0,0.9);
                color: white;
                padding: 15px;
                border-radius: 10px;
                font-family: monospace;
                font-size: 14px;
                z-index: 9999;
                min-width: 250px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            `;
            
            overlay.innerHTML = `
                <div style="text-align: center; margin-bottom: 10px;">
                    <strong>🤖 POLARIUM BOT ATIVO</strong>
                </div>
                <div id="bot-stats">
                    <div>Status: <span style="color: #4ade80;">Monitorando</span></div>
                    <div>Sinais: <span id="signal-count">0</span></div>
                    <div>Tempo: <span id="uptime">00:00</span></div>
                </div>
            `;
            
            document.body.appendChild(overlay);
            
            // Atualizar tempo
            let startTime = Date.now();
            setInterval(() => {
                const uptime = Math.floor((Date.now() - startTime) / 1000);
                const minutes = Math.floor(uptime / 60);
                const seconds = uptime % 60;
                document.getElementById('uptime').textContent = 
                    `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            }, 1000);
            
            console.log('✅ Trading overlay criado!');
        })();
        """
        
        try:
            await self.page.evaluate(overlay_js)
        except Exception as e:
            logger.error(f"Erro ao criar overlay: {e}")
    
    async def run(self):
        """Executa o bot"""
        self.is_running = True
        
        print(f"""
🤖 POLARIUM TRADING BOT v{self.version}
=====================================

🎯 Configuração:
   URL: {self.config['polarium_url']}
   Headless: {self.config['headless']}
   Confiança min: {self.config['min_confidence']}

🚀 Iniciando bot...
""")
        
        if not await self.initialize_browser():
            logger.error("❌ Falha ao inicializar browser")
            return
        
        logger.info("🎧 Bot ativo! Monitorando sinais...")
        logger.info("💡 Pressione Ctrl+C para parar")
        
        try:
            signal_count = 0
            
            while self.is_running:
                await asyncio.sleep(5)
                
                # Simular detecção de sinal (substitua pela lógica real)
                if signal_count % 12 == 0:  # A cada minuto
                    signal_count += 1
                    await self.simulate_signal(signal_count)
                
        except KeyboardInterrupt:
            logger.info("👋 Parando bot...")
        except Exception as e:
            logger.error(f"Erro no bot: {e}")
        finally:
            await self.cleanup()
    
    async def simulate_signal(self, count):
        """Simula sinal de trading (substitua pela lógica real)"""
        logger.info(f"🎯 Sinal #{count} detectado! (DEMO)")
        
        # Atualizar contador no overlay
        update_js = f"""
        const counter = document.getElementById('signal-count');
        if (counter) counter.textContent = '{count}';
        """
        
        try:
            await self.page.evaluate(update_js)
        except:
            pass
    
    async def cleanup(self):
        """Limpeza de recursos"""
        self.is_running = False
        
        try:
            if hasattr(self, 'browser') and self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright') and self.playwright:
                await self.playwright.stop()
        except:
            pass
        
        logger.info("🧹 Recursos liberados")

async def main():
    """Função principal"""
    bot = PolariumBot()
    await bot.run()

def check_first_run():
    """Verifica se é primeira execução"""
    first_run_file = Path("first_run.completed")
    
    if not first_run_file.exists():
        print("""
🎉 PRIMEIRA EXECUÇÃO!
====================

Este é um bot DEMONSTRATIVO para mostrar a estrutura.
Para funcionalidade completa de trading, você precisará:

1. Implementar análise técnica real
2. Conectar com APIs de dados de mercado
3. Adicionar lógica de detecção de padrões
4. Configurar notificações

O bot atual abre o Polarium e mostra um overlay,
mas os "sinais" são apenas demonstrativos.

Pressione Enter para continuar com a demonstração...
        """)
        input()
        first_run_file.write_text("completed")

if __name__ == "__main__":
    check_first_run()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\n👋 Bot interrompido")
    except Exception as e:
        print(f"❌ Erro: {e}")
        input("Pressione Enter para sair...")
'''
        
        # Salvar código do bot
        with open("polarium_bot.py", "w", encoding="utf-8") as f:
            f.write(bot_code)
        
        # Criar config padrão
        self.create_config_file()
        
        # Criar README
        self.create_readme_file()
        
        print("✅ Arquivos do bot criados!")
        return True
    
    def create_config_file(self):
        """Cria arquivo de configuração"""
        config = {
            "polarium_url": "https://trade.polariumbroker.com/",
            "headless": False,
            "max_candles_history": 200,
            "min_confidence": 0.7,
            "rsi_oversold": 30,
            "rsi_overbought": 70,
            "enable_notifications": True,
            "save_signals": True,
            "indicators": {
                "rsi_period": 14,
                "macd_enabled": True,
                "bollinger_enabled": True,
                "ema_periods": [9, 21, 50]
            },
            "notifications": {
                "telegram": {
                    "enabled": False,
                    "bot_token": "SEU_TOKEN_AQUI",
                    "chat_id": "SEU_CHAT_ID_AQUI"
                }
            }
        }
        
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def create_readme_file(self):
        """Cria arquivo README"""
        readme_content = """# Polarium Trading Bot

## 🚀 Como Usar

### Executar Diretamente
```bash
python polarium_bot.py
```

### Criar Executável Windows
```bash
python create_executable.py
```

## ⚙️ Configuração

Edite `config.json` para personalizar:
- URL do broker
- Parâmetros de análise técnica
- Notificações
- Indicadores

## 🔧 Recursos

- ✅ Interface web automática
- ✅ Overlay visual em tempo real
- ✅ Configuração flexível
- ✅ Logs detalhados
- ✅ Executável Windows

## ⚠️ Importante

Este é um bot DEMONSTRATIVO. Para trading real:
1. Implemente análise técnica completa
2. Conecte com dados de mercado reais
3. Adicione gerenciamento de risco
4. Teste extensivamente em conta demo

## 📞 Suporte

Para implementação completa de trading:
- Análise técnica avançada
- Integração com APIs de mercado
- Estratégias personalizadas
- Backtesting completo

Entre em contato para desenvolvimento profissional.
"""
        
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
    
    def create_executable_builder(self):
        """Cria script para gerar executável"""
        print("\n🔨 Criando builder do executável...")
        
        builder_code = '''import subprocess
import sys
import os
import shutil
from pathlib import Path

def create_executable():
    """Cria executável do bot"""
    print("🔨 Criando executável Windows...")
    
    # Criar arquivo .spec
    spec_content = """# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['polarium_bot.py'],
    pathex=[],
    binaries=[],
    datas=[('config.json', '.'), ('README.md', '.')],
    hiddenimports=['playwright', 'playwright._impl._api_structures', 'pandas', 'asyncio'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PolariumBot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""
    
    with open("polarium_bot.spec", "w") as f:
        f.write(spec_content)
    
    # Executar PyInstaller
    try:
        subprocess.check_call([
            "pyinstaller", "polarium_bot.spec", "--clean", "--noconfirm"
        ])
        
        print("✅ Executável criado em: dist/PolariumBot.exe")
        
        # Criar pasta portátil
        if os.path.exists("dist"):
            portable_dir = "PolariumBot_Portable"
            if os.path.exists(portable_dir):
                shutil.rmtree(portable_dir)
            
            shutil.copytree("dist", portable_dir)
            shutil.copy2("config.json", portable_dir)
            shutil.copy2("README.md", portable_dir)
            
            # Criar launcher
            launcher_bat = f"""@echo off
title Polarium Trading Bot
echo Iniciando Polarium Bot...
echo.
echo IMPORTANTE: Primeira execução pode demorar alguns minutos
echo para instalar browsers do Playwright automaticamente.
echo.
pause
PolariumBot.exe
pause
"""
            
            with open(f"{portable_dir}/EXECUTAR_BOT.bat", "w") as f:
                f.write(launcher_bat)
            
            print(f"✅ Pacote portátil criado: {portable_dir}/")
        
    except Exception as e:
        print(f"❌ Erro ao criar executável: {e}")

if __name__ == "__main__":
    create_executable()
'''
        
        with open("create_executable.py", "w", encoding="utf-8") as f:
            f.write(builder_code)
        
        print("✅ Builder do executável criado!")
    
    def create_launcher_scripts(self):
        """Cria scripts de inicialização"""
        print("\n📋 Criando scripts de inicialização...")
        
        # Script Windows .bat
        bat_content = '''@echo off
title Polarium Trading Bot v2.0
color 0B
echo ================================
echo    POLARIUM TRADING BOT v2.0
echo ================================
echo.
echo 🤖 Iniciando bot de trading...
echo.
echo IMPORTANTE:
echo - Este e um bot DEMONSTRATIVO
echo - Mantenha esta janela aberta
echo - Para parar: Ctrl+C
echo.
timeout /t 3 /nobreak >nul

python polarium_bot.py

echo.
echo Bot finalizado.
pause
'''
        
        with open("EXECUTAR_BOT.bat", "w") as f:
            f.write(bat_content)
        
        # Script de configuração
        config_bat = '''@echo off
title Configuracao Polarium Bot
echo Abrindo arquivo de configuracao...
echo.
echo Edite as configuracoes conforme necessario
echo e salve o arquivo.
echo.
notepad config.json
echo.
echo Configuracao salva!
echo Execute EXECUTAR_BOT.bat para iniciar
pause
'''
        
        with open("CONFIGURAR.bat", "w") as f:
            f.write(config_bat)
        
        print("✅ Scripts .bat criados!")
    
    def run_installation(self):
        """Executa processo completo de instalação"""
        try:
            self.print_banner()
            
            # Verificar Python
            if not self.check_python_version():
                input("Pressione Enter para sair...")
                return False
            
            # Instalar dependências
            if not self.install_dependencies():
                input("Pressione Enter para sair...")
                return False
            
            # Instalar browsers
            self.install_playwright_browsers()
            
            # Criar arquivos
            self.create_bot_files()
            self.create_executable_builder()
            self.create_launcher_scripts()
            
            # Sucesso!
            print(f"""
✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!
===================================

📁 Arquivos criados:
   ├── polarium_bot.py          (código principal)
   ├── config.json              (configurações)  
   ├── create_executable.py     (gerador do .exe)
   ├── EXECUTAR_BOT.bat         (iniciar bot)
   ├── CONFIGURAR.bat           (editar config)
   └── README.md                (instruções)

🚀 Para usar:
   1. Execute: EXECUTAR_BOT.bat
   2. Ou: python polarium_bot.py
   3. Para .exe: python create_executable.py

⚙️ Configurar:
   - Execute CONFIGURAR.bat
   - Ou edite config.json manualmente

🎯 IMPORTANTE: Este é um bot DEMONSTRATIVO!
   Para trading real, será necessário implementar:
   - Análise técnica completa  
   - Conexão com dados reais de mercado
   - Lógica de detecção de padrões
   - Gerenciamento de risco

📞 Para desenvolvimento profissional completo,
   entre em contato para consultoria especializada.

Pressione Enter para executar o bot agora...
            """)
            
            input()
            
            # Executar bot
            import asyncio
            sys.path.insert(0, str(self.base_path))
            
            try:
                from polarium_bot import main
                asyncio.run(main())
            except KeyboardInterrupt:
                print("\n👋 Bot interrompido pelo usuário")
            except Exception as e:
                print(f"❌ Erro ao executar bot: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na instalação: {e}")
            input("Pressione Enter para sair...")
            return False

def main():
    """Função principal do instalador"""
    installer = PolariumBotInstaller()
    installer.run_installation()

if __name__ == "__main__":
    main()
