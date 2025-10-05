import os
import sys
import json
import time
import hashlib
import platform
import asyncio
import aiohttp
import re
from datetime import datetime
from typing import Optional, List, Dict

# Cores para terminal
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'

ASCII_ART = f"""{Colors.WHITE}██████╗ ██████╗ ██╗   ██╗{Colors.RED}███████╗███████╗
{Colors.WHITE}██╔══██╗██╔══██╗╚██╗ ██╔╝{Colors.RED}╚══███╔╝╚══███╔╝
{Colors.WHITE}██║  ██║██████╔╝ ╚████╔╝ {Colors.RED}  ███╔╝   ███╔╝ 
{Colors.WHITE}██║  ██║██╔══██╗  ╚██╔╝  {Colors.RED} ███╔╝   ███╔╝  
{Colors.WHITE}██████╔╝██║  ██║   ██║   {Colors.RED}███████╗███████╗
{Colors.WHITE}╚═════╝ ╚═╝  ╚═╝   ╚═╝   {Colors.RED}╚══════╝╚══════╝
{Colors.RESET}"""

SERVER_URL = 'http://localhost:3000'
CONFIG_FILE = './save.json'

config = {
    'hwid': '',
    'token': '',
    'username': 'Não conectado',
    'userId': '',
    'subscription': 'free',
    'expiresAt': '∞',
    'tokens': [],
    'webhookUrl': None
}

MAIN_MENU = [
    {'id': 1, 'name': 'Limpar DM'},
    {'id': 2, 'name': "Fechar DM's"},
    {'id': 3, 'name': 'Limpar PKG'},
    {'id': 4, 'name': 'Trigger Clear', 'color': Colors.RED},
    {'id': 5, 'name': "Limpar Todas DM's"},
    {'id': 6, 'name': "Abrir DM'S"},
    {'id': 7, 'name': 'Limpar Amizades'},
    {'id': 8, 'name': 'Limpar Servidores'},
    {'id': 9, 'name': 'Tracker'},
    {'id': 10, 'name': 'Kosame Farm'},
    {'id': 11, 'name': 'Scrapper Icon'},
    {'id': 12, 'name': 'Spam Tools'},
    {'id': 13, 'name': 'Espionagem'},
    {'id': 14, 'name': "Username Tool's"},
    {'id': 15, 'name': 'Nitro Sniper'},
    {'id': 16, 'name': 'Server Cloner'},
    {'id': 17, 'name': 'Backup Mensagens'},
    {'id': 18, 'name': 'Configurar Painel', 'color': Colors.WHITE},
    {'id': 0, 'name': 'Sair', 'color': Colors.RED}
]

SETTINGS_MENU = [
    {'id': 1, 'name': 'Adicionar Conta Discord'},
    {'id': 2, 'name': 'Alterar Conta Ativa'},
    {'id': 3, 'name': 'Ver Contas Salvas'},
    {'id': 4, 'name': 'Remover Conta'},
    {'id': 5, 'name': 'Configurar Blacklist'},
    {'id': 6, 'name': 'Ver Status Premium'},
    {'id': 7, 'name': 'Sincronizar com Servidor'},
    {'id': 8, 'name': 'Configurar Webhook Geral'},
    {'id': 0, 'name': 'Voltar'}
]

class ServerAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    async def request(self, method: str, path: str, data: Optional[Dict] = None):
        async with aiohttp.ClientSession() as session:
            url = f'{self.base_url}{path}'
            kwargs = {'headers': {'Content-Type': 'application/json'}}
            if data:
                kwargs['json'] = data
            
            try:
                async with session.request(method, url, **kwargs) as resp:
                    try:
                        return {'status': resp.status, 'data': await resp.json()}
                    except:
                        return {'status': resp.status, 'data': await resp.text()}
            except:
                return {'status': 0, 'data': None}
    
    async def check_access(self, hwid: str):
        return await self.request('POST', '/api/check', {'hwid': hwid})
    
    async def save_token(self, hwid: str, token: str, username: str, user_id: str, 
                        discriminator: str, email: str, phone: str):
        return await self.request('POST', '/api/tokens/save', {
            'hwid': hwid, 'token': token, 'username': username,
            'userId': user_id, 'discriminator': discriminator,
            'email': email, 'phone': phone
        })
    
    async def get_tokens(self, hwid: str):
        return await self.request('POST', '/api/tokens/get', {'hwid': hwid})
    
    async def remove_token(self, hwid: str, token_id: str):
        return await self.request('POST', '/api/tokens/remove', {'hwid': hwid, 'tokenId': token_id})

class DiscordAPI:
    def __init__(self, token: str):
        self.token = token
        self.base_url = 'https://discord.com/api/v9'
        self.headers = {
            'Authorization': token,
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def request(self, method: str, path: str, data: Optional[Dict] = None):
        async with aiohttp.ClientSession() as session:
            url = f'{self.base_url}{path}'
            kwargs = {'headers': self.headers}
            if data:
                kwargs['json'] = data
            
            async with session.request(method, url, **kwargs) as resp:
                try:
                    return {'status': resp.status, 'data': await resp.json()}
                except:
                    return {'status': resp.status, 'data': await resp.text()}
    
    async def get_user_info(self):
        return await self.request('GET', '/users/@me')
    
    async def get_dms(self):
        return await self.request('GET', '/users/@me/channels')
    
    async def get_guilds(self):
        return await self.request('GET', '/users/@me/guilds')
    
    async def get_friends(self):
        return await self.request('GET', '/users/@me/relationships')
    
    async def delete_message(self, channel_id: str, message_id: str):
        return await self.request('DELETE', f'/channels/{channel_id}/messages/{message_id}')
    
    async def get_messages(self, channel_id: str, limit: int = 100, before: Optional[str] = None):
        url = f'/channels/{channel_id}/messages?limit={limit}'
        if before:
            url += f'&before={before}'
        return await self.request('GET', url)
    
    async def close_dm(self, channel_id: str):
        return await self.request('DELETE', f'/channels/{channel_id}')
    
    async def leave_guild(self, guild_id: str):
        return await self.request('DELETE', f'/users/@me/guilds/{guild_id}')
    
    async def remove_friend(self, user_id: str):
        return await self.request('DELETE', f'/users/@me/relationships/{user_id}')
    
    async def send_message(self, channel_id: str, content: str):
        return await self.request('POST', f'/channels/{channel_id}/messages', {'content': content})
    
    async def open_dm(self, user_id: str):
        return await self.request('POST', '/users/@me/channels', {'recipient_id': user_id})

api: Optional[DiscordAPI] = None
server_api = ServerAPI(SERVER_URL)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_header():
    clear_screen()
    print(ASCII_ART)
    sub = f"{Colors.YELLOW}💎 PREMIUM" if config['subscription'] == 'premium' else f"{Colors.CYAN}🆓 FREE"
    print(f"{Colors.WHITE}Conectado: {Colors.GREEN}{config['username']}{Colors.RESET}")
    print(f"{Colors.WHITE}Assinatura: {sub}{Colors.RESET}")
    print(f"{Colors.WHITE}Expira em: {Colors.CYAN}{config['expiresAt']}{Colors.RESET}")
    print(f"{Colors.WHITE}HWID: {Colors.GRAY}{config['hwid'][:16]}...{Colors.RESET}\n")

def display_menu(menu: List[Dict]):
    for option in menu:
        color = option.get('color', Colors.WHITE)
        num_color = Colors.RED if option.get('color') == Colors.RED else Colors.RED
        print(f"{Colors.GRAY}[ {num_color}{option['id']}{Colors.GRAY} ] {color}{option['name']}{Colors.RESET}")
    print()

async def log(msg: str, msg_type: str = 'info'):
    prefix = {
        'info': f"{Colors.CYAN}[INFO]{Colors.RESET}",
        'success': f"{Colors.GREEN}[✓]{Colors.RESET}",
        'error': f"{Colors.RED}[✗]{Colors.RESET}",
        'warn': f"{Colors.YELLOW}[!]{Colors.RESET}"
    }
    print(f"{prefix[msg_type]} {msg}")

def load_config():
    global config, api
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                saved_config = json.load(f)
                config.update(saved_config)
            
            if config.get('token') and len(config['token']) > 50:
                api = DiscordAPI(config['token'])
    except Exception as err:
        print(f'Erro ao carregar config: {err}')

def save_config():
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as err:
        print(f'Erro ao salvar config: {err}')

def get_hwid():
    info = f"{platform.node()}-{platform.system()}-{platform.machine()}"
    return hashlib.sha256(info.encode()).hexdigest()

async def check_server_access():
    try:
        await log('Verificando status da api.', 'info')
        status_res = await server_api.request('GET', '/api/status')
        if status_res['status'] != 200:
            await log('Servidor offline!', 'error')
            return False
        
        await log('Verificando tipo de assinatura', 'info')
        access_res = await server_api.check_access(config['hwid'])
        if access_res['status'] == 200 and access_res['data'].get('success'):
            config['subscription'] = access_res['data'].get('subscription', 'free')
            config['expiresAt'] = access_res['data'].get('expiresAt', '∞')
            if not config['token']:
                config['username'] = access_res['data'].get('username', 'Não conectado')
            save_config()
            await log(f"Assinatura verificada! Tipo: {config['subscription'].upper()}", 'success')
            return True
        else:
            await log('Erro ao verificar assinatura', 'error')
            return False
    except Exception as err:
        await log(f'Erro de conexão: {err}', 'error')
        return False

async def load_server_tokens():
    try:
        res = await server_api.get_tokens(config['hwid'])
        if res['status'] == 200 and res['data'].get('success'):
            config['tokens'] = res['data'].get('tokens', [])
            
            if config['token'] and any(t['token'] == config['token'] for t in config['tokens']):
                current = next((t for t in config['tokens'] if t['token'] == config['token']), None)
                if current:
                    config['username'] = current['username']
                    config['userId'] = current['userId']
            elif config['tokens'] and not config['token']:
                first = config['tokens'][0]
                config['token'] = first['token']
                config['username'] = first['username']
                config['userId'] = first['userId']
                global api
                api = DiscordAPI(config['token'])
            
            save_config()
    except Exception as err:
        print(f'Erro ao carregar tokens: {err}')

# ============= FUNCIONALIDADES =============

async def clear_dm():
    display_header()
    print(f"{Colors.RED}Limpar DM{Colors.RESET}\n")
    if not api:
        await log('Configure uma conta primeiro!', 'error')
        await asyncio.sleep(2)
        return
    
    channel_id = input(f"{Colors.WHITE}ID do canal/DM: {Colors.RESET}")
    if not channel_id.strip():
        await log('ID inválido!', 'error')
        await asyncio.sleep(1.5)
        return
    
    try:
        await log('Buscando mensagens...', 'info')
        total_deleted = 0
        last_id = None
        has_more = True
        batch_count = 0
        
        while has_more:
            batch_count += 1
            await log(f'Buscando lote {batch_count}...', 'info')
            
            res = await api.get_messages(channel_id, 100, last_id)
            
            if res['status'] == 403:
                await log('Sem permissão para acessar este canal!', 'error')
                await asyncio.sleep(2)
                return
            
            if res['status'] == 404:
                await log('Canal não encontrado!', 'error')
                await asyncio.sleep(2)
                return
            
            if res['status'] != 200 or not res['data'] or len(res['data']) == 0:
                has_more = False
                break
            
            my_messages = [m for m in res['data'] if m.get('author', {}).get('id') == config['userId']]
            await log(f"Encontradas {len(my_messages)} mensagens suas neste lote", 'info')
            
            for msg in my_messages:
                try:
                    del_res = await api.delete_message(channel_id, msg['id'])
                    if del_res['status'] in [204, 200]:
                        total_deleted += 1
                        await log(f"Deletadas: {total_deleted}", 'success')
                    await asyncio.sleep(0.5)
                except:
                    pass
            
            last_id = res['data'][-1]['id']
            if len(res['data']) < 100:
                has_more = False
            
            await asyncio.sleep(1)
        
        if total_deleted == 0:
            await log('Nenhuma mensagem sua encontrada', 'warn')
        else:
            await log(f'Total de mensagens deletadas: {total_deleted}', 'success')
    except Exception as err:
        await log(f'Erro: {err}', 'error')
    
    input(f"\n{Colors.GRAY}Pressione ENTER para voltar...{Colors.RESET}")

async def close_dms():
    display_header()
    print(f"{Colors.CYAN}Fechar DMs{Colors.RESET}\n")
    if not api:
        await log('Configure uma conta primeiro!', 'error')
        await asyncio.sleep(2)
        return
    
    try:
        await log('Buscando DMs...', 'info')
        res = await api.get_dms()
        if res['status'] != 200:
            await log('Erro ao buscar DMs!', 'error')
            await asyncio.sleep(2)
            return
        
        await log(f"Encontradas {len(res['data'])} DMs", 'success')
        
        confirm = input(f"{Colors.YELLOW}Deseja fechar TODAS as DMs? (s/n): {Colors.RESET}")
        if confirm.lower() != 's':
            await log('Operação cancelada', 'warn')
            await asyncio.sleep(1.5)
            return
        
        for dm in res['data']:
            await api.close_dm(dm['id'])
            username = dm.get('recipients', [{}])[0].get('username', 'Desconhecido')
            await log(f"DM fechada: {username}", 'success')
            await asyncio.sleep(0.2)
        
        await log('Todas as DMs foram fechadas!', 'success')
    except Exception as err:
        await log(f'Erro: {err}', 'error')
    
    input(f"\n{Colors.GRAY}Pressione ENTER para voltar...{Colors.RESET}")

async def clear_packages():
    display_header()
    print(f"{Colors.CYAN}Limpar Pacotes{Colors.RESET}\n")
    if not api:
        await log('Configure uma conta primeiro!', 'error')
        await asyncio.sleep(2)
        return
    
    await log('Funcionalidade em desenvolvimento', 'warn')
    input(f"\n{Colors.GRAY}Pressione ENTER para voltar...{Colors.RESET}")

async def trigger_clear():
    display_header()
    print(f"{Colors.RED}TRIGGER CLEAR{Colors.RESET}\n")
    if not api:
        await log('Configure uma conta primeiro!', 'error')
        await asyncio.sleep(2)
        return
    
    await log(f'{Colors.RED}AVISO: Esta ação irá limpar TUDO!{Colors.RESET}', 'warn')
    await log('- Todas as DMs', 'warn')
    await log('- Todos os amigos', 'warn')
    await log('- Todos os servidores', 'warn')
    
    confirm1 = input(f"\n{Colors.RED}Digite 'CONFIRMAR' para prosseguir: {Colors.RESET}")
    if confirm1 != 'CONFIRMAR':
        await log('Operação cancelada', 'info')
        await asyncio.sleep(1.5)
        return
    
    confirm2 = input(f"{Colors.RED}Tem CERTEZA ABSOLUTA? (s/n): {Colors.RESET}")
    if confirm2.lower() != 's':
        await log('Operação cancelada', 'info')
        await asyncio.sleep(1.5)
        return
    
    try:
        await log('Limpando DMs...', 'info')
        dms = await api.get_dms()
        if dms['status'] == 200:
            for dm in dms['data']:
                has_more = True
                last_id = None
                
                while has_more:
                    messages = await api.get_messages(dm['id'], 100, last_id)
                    if messages['status'] == 200 and messages['data']:
                        my_messages = [m for m in messages['data'] if m['author']['id'] == config['userId']]
                        for msg in my_messages:
                            await api.delete_message(dm['id'], msg['id'])
                            await asyncio.sleep(0.3)
                        last_id = messages['data'][-1]['id']
                        if len(messages['data']) < 100:
                            has_more = False
                    else:
                        has_more = False
                    await asyncio.sleep(0.5)
                
                await api.close_dm(dm['id'])
                await asyncio.sleep(0.2)
        
        await log('Removendo amigos...', 'info')
        friends = await api.get_friends()
        if friends['status'] == 200:
            friends_list = [r for r in friends['data'] if r['type'] == 1]
            for friend in friends_list:
                await api.remove_friend(friend['user']['id'])
                await asyncio.sleep(0.5)
        
        await log('Saindo de servidores...', 'info')
        guilds = await api.get_guilds()
        if guilds['status'] == 200:
            for guild in guilds['data']:
                await api.leave_guild(guild['id'])
                await asyncio.sleep(0.5)
        
        await log(f'{Colors.GREEN}TRIGGER CLEAR CONCLUÍDO!{Colors.RESET}', 'success')
    except Exception as err:
        await log(f'Erro: {err}', 'error')
    
    input(f"\n{Colors.GRAY}Pressione ENTER para voltar...{Colors.RESET}")

async def clear_all_dms():
    display_header()
    print(f"{Colors.CYAN}Limpar Todas as DMs{Colors.RESET}\n")
    if not api:
        await log('Configure uma conta primeiro!', 'error')
        await asyncio.sleep(2)
        return
    
    try:
        await log('Buscando DMs...', 'info')
        res = await api.get_dms()
        if res['status'] != 200:
            await log('Erro ao buscar DMs!', 'error')
            await asyncio.sleep(2)
            return
        
        await log(f"Encontradas {len(res['data'])} DMs", 'success')
        
        confirm = input(f"{Colors.YELLOW}Deseja limpar TODAS as DMs? (s/n): {Colors.RESET}")
        if confirm.lower() != 's':
            await log('Operação cancelada', 'warn')
            await asyncio.sleep(1.5)
            return
        
        for dm in res['data']:
            username = dm.get('recipients', [{}])[0].get('username', 'Desconhecido')
            await log(f'Limpando DM: {username}', 'info')
            
            has_more = True
            last_id = None
            
            while has_more:
                messages = await api.get_messages(dm['id'], 100, last_id)
                if messages['status'] == 200 and messages['data']:
                    my_messages = [m for m in messages['data'] if m['author']['id'] == config['userId']]
                    for msg in my_messages:
                        await api.delete_message(dm['id'], msg['id'])
                        await asyncio.sleep(0.4)
                    last_id = messages['data'][-1]['id']
                    if len(messages['data']) < 100:
                        has_more = False
                else:
                    has_more = False
                await asyncio.sleep(0.5)
        
        await log('Todas as DMs foram limpas!', 'success')
    except Exception as err:
        await log(f'Erro: {err}', 'error')
    
    input(f"\n{Colors.GRAY}Pressione ENTER para voltar...{Colors.RESET}")

async def open_dms():
    display_header()
    print(f"{Colors.CYAN}Abrir DMs{Colors.RESET}\n")
    if not api:
        await log('Configure uma conta primeiro!', 'error')
        await asyncio.sleep(2)
        return
    
    await log('Digite os IDs dos usuários separados por vírgula:', 'info')
    ids = input(f"{Colors.WHITE}IDs: {Colors.RESET}")
    
    if not ids.strip():
        await log('Nenhum ID fornecido', 'error')
        await asyncio.sleep(1.5)
        return
    
    try:
        user_ids = [uid.strip() for uid in ids.split(',') if uid.strip()]
        await log(f'Abrindo DMs com {len(user_ids)} usuários...', 'info')
        
        for user_id in user_ids:
            res = await api.open_dm(user_id)
            if res['status'] == 200:
                await log(f'DM aberta com ID: {user_id}', 'success')
            else:
                await log(f'Erro ao abrir DM com ID: {user_id}', 'error')
            await asyncio.sleep(0.5)
        
        await log('Processo concluído!', 'success')
    except Exception as err:
        await log(f'Erro: {err}', 'error')
    
    input(f"\n{Colors.GRAY}Pressione ENTER para voltar...{Colors.RESET}")

async def clear_friends():
    display_header()
    print(f"{Colors.CYAN}Limpar Amizades{Colors.RESET}\n")
    if not api:
        await log('Configure uma conta primeiro!', 'error')
        await asyncio.sleep(2)
        return
    
    try:
        await log('Buscando amigos...', 'info')
        res = await api.get_friends()
        if res['status'] != 200:
            await log('Erro ao buscar amigos!', 'error')
            await asyncio.sleep(2)
            return
        
        friends = [r for r in res['data'] if r['type'] == 1]
        await log(f"Encontrados {len(friends)} amigos", 'success')
        
        confirm = input(f"{Colors.YELLOW}Deseja remover TODOS os amigos? (s/n): {Colors.RESET}")
        if confirm.lower() != 's':
            await log('Operação cancelada', 'warn')
            await asyncio.sleep(1.5)
            return
        
        for friend in friends:
            await api.remove_friend(friend['user']['id'])
            await log(f"Removido: {friend['user']['username']}", 'success')
            await asyncio.sleep(0.5)
        
        await log('Todos os amigos foram removidos!', 'success')
    except Exception as err:
        await log(f'Erro: {err}', 'error')
    
    input(f"\n{Colors.GRAY}Pressione ENTER para voltar...{Colors.RESET}")

async def clear_servers():
    display_header()
    print(f"{Colors.CYAN}Limpar Servidores{Colors.RESET}\n")
    if not api:
        await log('Configure uma conta primeiro!', 'error')
        await asyncio.sleep(2)
        return
    
    try:
        await log('Buscando servidores...', 'info')
        res = await api.get_guilds()
        if res['status'] != 200:
            await log('Erro ao buscar servidores!', 'error')
            await asyncio.sleep(2)
            return
        
        await log(f"Encontrados {len(res['data'])} servidores", 'success')
        
        confirm = input(f"{Colors.YELLOW}Deseja sair de TODOS os servidores? (s/n): {Colors.RESET}")
        if confirm.lower() != 's':
            await log('Operação cancelada', 'warn')
            await asyncio.sleep(1.5)
            return
        
        for guild in res['data']:
            await api.leave_guild(guild['id'])
            await log(f"Saiu de: {guild['name']}", 'success')
            await asyncio.sleep(0.5)
        
        await log('Saiu de todos os servidores!', 'success')
    except Exception as err:
        await log(f'Erro: {err}', 'error')
    
    input(f"\n{Colors.GRAY}Pressione ENTER para voltar...{Colors.RESET}")

async def tracker():
    display_header()
    print(f"{Colors.CYAN}Tracker - Monitorar Própria Conta{Colors.RESET}\n")
    if not api:
        await log('Configure uma conta primeiro!', 'error')
        await asyncio.sleep(2)
        return
    
    print(f"{Colors.YELLOW}Este tracker monitora SUAS próprias atividades{Colors.RESET}\n")
    print(f"{Colors.GRAY}[1]{Colors.RESET} Ver estatísticas da conta")
    print(f"{Colors.GRAY}[2]{Colors.RESET} Listar servidores recentes")
    print(f"{Colors.GRAY}[3]{Colors.RESET} Ver DMs ativas")
    print(f"{Colors.GRAY}[4]{Colors.RESET} Ver pedidos de amizade pendentes")
    print(f"{Colors.GRAY}[0]{Colors.RESET} Voltar\n")
    
    choice = input(f"{Colors.CYAN}Escolha: {Colors.RESET}")
    
    try:
        if choice == '1':
            await log('Buscando estatísticas...', 'info')
            user = await api.get_user_info()
            guilds = await api.get_guilds()
            dms = await api.get_dms()
            friends = await api.get_friends()
            
            if user['status'] == 200 and guilds['status'] == 200:
                u = user['data']
                print(f"\n{Colors.YELLOW}Estatísticas da Conta:{Colors.RESET}")
                print(f"  Username: {u['username']}#{u.get('discriminator', '0')}")
                print(f"  ID: {u['id']}")
                print(f"  Servidores: {len(guilds['data'])}")
                print(f"  DMs Ativas: {len(dms['data'])}")
                friends_list = [r for r in friends['data'] if r['type'] == 1]
                print(f"  Amigos: {len(friends_list)}")
        
        elif choice == '2':
            await log('Buscando servidores...', 'info')
            res = await api.get_guilds()
            
            if res['status'] == 200:
                print(f"\n{Colors.YELLOW}Servidores ({len(res['data'])}):{Colors.RESET}")
                for i, guild in enumerate(res['data'][:20], 1):
                    print(f"  {i}. {guild['name']} ({guild['id']})")
                if len(res['data']) > 20:
                    print(f"  ... e mais {len(res['data']) - 20} servidores")
        
        elif choice == '3':
            await log('Buscando DMs...', 'info')
            res = await api.get_dms()
            
            if res['status'] == 200:
                print(f"\n{Colors.YELLOW}DMs Ativas ({len(res['data'])}):{Colors.RESET}")
                for i, dm in enumerate(res['data'][:20], 1):
                    username = dm.get('recipients', [{}])[0].get('username', 'Desconhecido')
                    print(f"  {i}. {username} ({dm['id']})")
                if len(res['data']) > 20:
                    print(f"  ... e mais {len(res['data']) - 20} DMs")
        
        elif choice == '4':
            await log('Buscando pedidos pendentes...', 'info')
            res = await api.get_friends()
            
            if res['status'] == 200:
                incoming = [r for r in res['data'] if r['type'] == 3]
                outgoing = [r for r in res['data'] if r['type'] == 4]
                
                print(f"\n{Colors.YELLOW}Pedidos Recebidos ({len(incoming)}):{Colors.RESET}")
                for i, req in enumerate(incoming, 1):
                    print(f"  {i}. {req['user']['username']}#{req['user']['discriminator']}")
                
                print(f"\n{Colors.YELLOW}Pedidos Enviados ({len(outgoing)}):{Colors.RESET}")
                for i, req in enumerate(outgoing, 1):
                    print(f"  {i}. {req['user']['username']}#{req['user']['discriminator']}")
    except Exception as err:
        await log(f'Erro: {err}', 'error')
    
    input(f"\n{Colors.GRAY}Pressione ENTER para voltar...{Colors.RESET}")

async def kosame_farm():
    display_header()
    print(f"{Colors.CYAN}Kosame Farm{Colors.RESET}\n")
    if not api:
        await log('Configure uma conta primeiro!', 'error')
        await asyncio.sleep(2)
        return
    
    await log('Funcionalidade em desenvolvimento', 'warn')
    input(f"\n{Colors.GRAY}Pressione ENTER para voltar...{Colors.RESET}")

async def scrap_icon():
    display_header()
    print(f"{Colors.CYAN}Scrapper Icon{Colors.RESET}\n")
    if not api:
        await log('Configure uma conta primeiro!', 'error')
        await asyncio.sleep(2)
        return
    
    await log('Funcionalidade em desenvolvimento', 'warn')
    input(f"\n{Colors.GRAY}Pressione ENTER para voltar...{Colors.RESET}")

async def spam_tools():
    display_header()
    print(f"{Colors.CYAN}Spam Tools{Colors.RESET}\n")
    if not api:
        await log('Configure uma conta primeiro!', 'error')
        await asyncio.sleep(2)
        return
    
    await log('Funcionalidade em desenvolvimento', 'warn')
    input(f"\n{Colors.GRAY}Pressione ENTER para voltar...{Colors.RESET}")

async def spy():
    display_header()
    print(f"{Colors.CYAN}Espionagem (Tempo Real){Colors.RESET}\n")
    
    if config['subscription'] != 'premium':
        await log('Esta funcionalidade requer PREMIUM', 'error')
        await asyncio.sleep(2)
        return
    
    if not config.get('webhookUrl'):
        await log('Nenhum webhook configurado!', 'error')
        await log('Configure um webhook em: Configurações > Configurar Webhook Geral', 'warn')
        await asyncio.sleep(3)
        return
    
    if not config.get('token'):
        await log('Configure uma conta primeiro!', 'error')
        await asyncio.sleep(2)
        return
    
    await log('Esta funcionalidade requer discord.py-self (biblioteca Python)', 'warn')
    await log('Instale com: pip install discord.py-self', 'info')
    await log('Funcionalidade em desenvolvimento', 'warn')
    input(f"\n{Colors.GRAY}Pressione ENTER para voltar...{Colors.RESET}")

async def check_available_usernames():
    clear_screen()
    display_header()
    print(f"\n{Colors.CYAN}Verificador de Usernames{Colors.RESET}\n")
    print(f"{Colors.GRAY}[1]{Colors.RESET} Usernames de 3 caracteres (gerar todos)")
    print(f"{Colors.GRAY}[2]{Colors.RESET} Usernames de 4 caracteres (gerar todos)")
    print(f"{Colors.GRAY}[3]{Colors.RESET} Username customizado")
    print(f"{Colors.GRAY}[4]{Colors.RESET} Lista pré-definida de 4 caracteres")
    print(f"{Colors.GRAY}[0]{Colors.RESET} Voltar\n")
    
    choice = input(f"{Colors.CYAN}Escolha: {Colors.RESET}")
    
    if choice == '0':
        return
    
    clear_screen()
    display_header()
    
    usernames_to_check = []
    length = 0
    
    if choice == '3':
        username = input(f"{Colors.WHITE}Digite o username: {Colors.RESET}")
        if not username.strip():
            await log('Username inválido!', 'error')
            await asyncio.sleep(2)
            return
        usernames_to_check = [username.strip()]
        length = len(username)
    elif choice == '4':
        usernames_to_check = [
            '9ihs', '4w0w', 'fqg2', '1j79', 'e8cp', 'q6ld', '2e7v', '2d5p',
            '8r4v', 'i51m', 'wx1u', '3yy5', '8v7r', '5oyg', 'x05k', 'gcb5',
            'yt2j', '.1p2', '.9x7', 'a.bc'
        ]
        length = 4
    else:
        length = 3 if choice == '1' else 4
    
    webhook = config.get('webhookUrl')
    
    if not webhook:
        use_webhook = input(f"{Colors.CYAN}Deseja enviar resultados para webhook? (s/n): {Colors.RESET}")
        if use_webhook.lower() == 's':
            webhook = input(f"{Colors.WHITE}URL da Webhook: {Colors.RESET}")
            if 'discord.com/api/webhooks/' not in webhook:
                await log('URL de webhook inválida!', 'error')
                await asyncio.sleep(2)
                return
    
    clear_screen()
    display_header()
    
    print(f"\n{Colors.CYAN}Buscando usernames...{Colors.RESET}")
    print(f"{Colors.YELLOW}Pressione CTRL+C para voltar ao menu principal{Colors.RESET}\n")
    
    if not usernames_to_check:
        usernames_to_check = generate_combinations(length)
    
    await start_background_check(usernames_to_check, webhook, length)

def generate_combinations(length: int) -> List[str]:
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789_.'
    combinations = []
    
    def generate(current: str):
        if len(current) == length:
            combinations.append(current)
            return
        for char in chars:
            generate(current + char)
    
    generate('')
    return combinations

async def check_username_availability(username: str) -> Dict:
    try:
        if len(username) < 2 or len(username) > 32:
            return {'available': False, 'reason': 'tamanho inválido'}
        
        if not re.match(r'^[a-z0-9_.]+$', username):
            return {'available': False, 'reason': 'caracteres inválidos'}
        
        token = config.get('token')
        if not token:
            return {'available': False, 'reason': 'token não configurado'}
        
        async with aiohttp.ClientSession() as session:
            headers = {
                'Authorization': token,
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with session.post(
                'https://discord.com/api/v9/users/@me/pomelo-attempt',
                headers=headers,
                json={'username': username}
            ) as resp:
                if resp.status == 429:
                    raise Exception('Rate limit atingido')
                
                if resp.status != 200:
                    return {'available': False, 'reason': f'HTTP {resp.status}'}
                
                try:
                    data = await resp.json()
                except:
                    return {'available': False, 'reason': 'resposta inválida'}
                
                if data.get('taken') == False:
                    return {'available': True}
                
                return {'available': False, 'reason': 'já está em uso'}
                
    except Exception as err:
        if 'Rate limit' in str(err):
            raise err
        return {'available': False, 'reason': 'erro'}
async def send_to_webhook(webhook_url: str, username: Optional[str] = None, 
                         length: int = 0, is_final: bool = False, 
                         checked: int = 0, available: int = 0):
    try:
        if is_final:
            payload = {
                'content': '@everyone',
                'embeds': [{
                    'title': '✅ Verificação Concluída!',
                    'description': 'A busca por usernames foi finalizada.',
                    'fields': [
                        {
                            'name': '📊 Total Verificado',
                            'value': f'{checked} usernames',
                            'inline': True
                        },
                        {
                            'name': '✨ Total Disponível',
                            'value': f'{available} usernames',
                            'inline': True
                        }
                    ],
                    'color': 0x2F3136,
                    'footer': {'text': 'Username Checker System'},
                    'timestamp': datetime.utcnow().isoformat()
                }]
            }
        else:
            payload = {
                'embeds': [{
                    'title': '🎯 Username Disponível!',
                    'description': f'Username de **{length} caracteres** encontrado',
                    'fields': [
                        {
                            'name': '📝 Username',
                            'value': f'`{username}`',
                            'inline': True
                        },
                        {
                            'name': '📏 Tamanho',
                            'value': f'{length} caracteres',
                            'inline': True
                        },
                        {
                            'name': '🕐 Horário',
                            'value': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                            'inline': False
                        }
                    ],
                    'color': 0x2F3136,
                    'footer': {'text': 'Username Checker System'},
                    'timestamp': datetime.utcnow().isoformat()
                }]
            }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as resp:
                if resp.status not in [200, 204]:
                    raise Exception(f'Webhook error {resp.status}')
    except:
        pass

async def start_background_check(usernames: List[str], webhook: Optional[str], length: int):
    checked = 0
    available = 0
    batch_size = 5
    
    try:
        for i in range(0, len(usernames), batch_size):
            batch = usernames[i:min(i + batch_size, len(usernames))]
            
            for username in batch:
                try:
                    checked += 1
                    result = await check_username_availability(username)
                    
                    if result.get('available'):
                        available += 1
                        if webhook:
                            await send_to_webhook(webhook, username, length)
                            await asyncio.sleep(1)
                    
                    await asyncio.sleep(2)
                except:
                    await asyncio.sleep(3)
        
        if webhook:
            await send_to_webhook(webhook, None, length, True, checked, available)
            
    except KeyboardInterrupt:
        await log('Voltando ao menu...', 'info')

async def username_tools():
    display_header()
    print(f"{Colors.CYAN}Username Tools{Colors.RESET}\n")
    
    if not api:
        await log('Configure uma conta primeiro!', 'error')
        await asyncio.sleep(2)
        return
    
    print(f"{Colors.GRAY}[1]{Colors.RESET} Verificar usernames disponíveis")
    print(f"{Colors.GRAY}[2]{Colors.RESET} Ver informações da conta")
    print(f"{Colors.GRAY}[0]{Colors.RESET} Voltar\n")
    
    choice = input(f"{Colors.CYAN}Escolha: {Colors.RESET}")
    
    if choice == '1':
        await check_available_usernames()
    elif choice == '2':
        await show_account_info()
        input(f"\n{Colors.GRAY}Pressione ENTER para voltar...{Colors.RESET}")

async def show_account_info():
    try:
        res = await api.get_user_info()
        if res['status'] == 200:
            user = res['data']
            
            print(f"\n{Colors.CYAN}╔═══════════════════════════════════════╗{Colors.RESET}")
            print(f"{Colors.CYAN}║       Informações da Conta            ║{Colors.RESET}")
            print(f"{Colors.CYAN}╠═══════════════════════════════════════╣{Colors.RESET}")
            print(f"{Colors.WHITE}  > Username:{Colors.RESET} {user['username']}")
            print(f"{Colors.WHITE}  > ID:{Colors.RESET} {user['id']}")
            print(f"{Colors.WHITE}  > Email:{Colors.RESET} {user.get('email', 'N/A')}")
            print(f"{Colors.WHITE}  > Phone:{Colors.RESET} {user.get('phone', 'N/A')}")
            print(f"{Colors.WHITE}  > Verificado:{Colors.RESET} {'Sim' if user.get('verified') else 'Não'}")
            print(f"{Colors.CYAN}╚═══════════════════════════════════════╝{Colors.RESET}")
    except Exception as err:
        await log(f'Erro: {err}', 'error')

async def nitro_sniper():
    display_header()
    print(f"{Colors.CYAN}Nitro Sniper{Colors.RESET}\n")
    if config['subscription'] != 'premium':
        await log('Esta funcionalidade requer PREMIUM', 'error')
        await asyncio.sleep(2)
        return
    await log('Funcionalidade em desenvolvimento', 'warn')
    input(f"\n{Colors.GRAY}Pressione ENTER para voltar...{Colors.RESET}")

async def server_cloner():
    display_header()
    print(f"{Colors.CYAN}Server Cloner{Colors.RESET}\n")
    if config['subscription'] != 'premium':
        await log('Esta funcionalidade requer PREMIUM', 'error')
        await asyncio.sleep(2)
        return
    await log('Funcionalidade em desenvolvimento', 'warn')
    input(f"\n{Colors.GRAY}Pressione ENTER para voltar...{Colors.RESET}")

async def backup_messages():
    display_header()
    print(f"{Colors.CYAN}Backup Mensagens{Colors.RESET}\n")
    if not api:
        await log('Configure uma conta primeiro!', 'error')
        await asyncio.sleep(2)
        return
    
    channel_id = input(f"{Colors.WHITE}ID do canal/DM: {Colors.RESET}")
    
    try:
        await log('Buscando mensagens...', 'info')
        all_messages = []
        last_id = None
        has_more = True
        
        while has_more:
            res = await api.get_messages(channel_id, 100, last_id)
            if res['status'] != 200:
                await log('Erro ao buscar mensagens!', 'error')
                break
            
            if not res['data'] or len(res['data']) == 0:
                has_more = False
                break
            
            all_messages.extend(res['data'])
            last_id = res['data'][-1]['id']
            
            await log(f"Coletadas {len(all_messages)} mensagens...", 'info')
            
            if len(res['data']) < 100:
                has_more = False
            
            await asyncio.sleep(0.5)
        
        filename = f"backup_{channel_id}_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_messages, f, indent=2, ensure_ascii=False)
        
        await log(f'Backup salvo em: {filename}', 'success')
        await log(f'Total de mensagens: {len(all_messages)}', 'success')
    except Exception as err:
        await log(f'Erro: {err}', 'error')
    
    input(f"\n{Colors.GRAY}Pressione ENTER para voltar...{Colors.RESET}")

# ============= CONFIGURAÇÕES =============

async def settings_panel():
    while True:
        display_header()
        print(f"{Colors.WHITE}CONFIGURAÇÕES{Colors.RESET}\n")
        display_menu(SETTINGS_MENU)
        
        choice = input(f"{Colors.CYAN}Escolha: {Colors.RESET}")
        option = int(choice) if choice.isdigit() else -1
        
        if option == 0:
            break
        elif option == 1:
            await adicionar_conta()
        elif option == 2:
            await alterar_conta_ativa()
        elif option == 3:
            await ver_contas()
        elif option == 4:
            await remover_conta()
        elif option == 5:
            await configurar_blacklist()
        elif option == 6:
            await ver_status()
        elif option == 7:
            await sincronizar()
        elif option == 8:
            await configurar_webhook_geral()
        else:
            await log('Opção inválida', 'error')
            await asyncio.sleep(1)

async def adicionar_conta():
    display_header()
    print(f"{Colors.CYAN}Adicionar Conta Discord{Colors.RESET}\n")
    token = input(f"{Colors.WHITE}Token: {Colors.RESET}")
    
    if not token or len(token) < 50:
        await log('Token inválido!', 'error')
        await asyncio.sleep(1.5)
        return
    
    try:
        await log('Verificando token...', 'info')
        temp_api = DiscordAPI(token)
        res = await temp_api.get_user_info()
        
        if res['status'] != 200:
            await log('Token inválido ou expirado!', 'error')
            await asyncio.sleep(2)
            return
        
        user = res['data']
        await log('Salvando no servidor...', 'info')
        
        save_res = await server_api.save_token(
            config['hwid'], token, user['username'], user['id'],
            user.get('discriminator', '0'), user.get('email', ''),
            user.get('phone', '')
        )
        
        if save_res['status'] == 200 and save_res['data'].get('success'):
            global api
            config['token'] = token
            config['username'] = user['username']
            config['userId'] = user['id']
            api = DiscordAPI(token)
            save_config()
            await load_server_tokens()
            await log(f"Conta adicionada: {user['username']}", 'success')
        else:
            await log('Erro ao salvar no servidor', 'error')
        
        await asyncio.sleep(2)
    except Exception as err:
        await log(f'Erro: {err}', 'error')
        await asyncio.sleep(2)

async def alterar_conta_ativa():
    display_header()
    print(f"{Colors.CYAN}Alterar Conta Ativa{Colors.RESET}\n")
    await load_server_tokens()
    
    if not config['tokens']:
        await log('Nenhuma conta salva', 'warn')
        await asyncio.sleep(2)
        return
    
    print(f"{Colors.YELLOW}Contas disponíveis:{Colors.RESET}\n")
    for i, t in enumerate(config['tokens'], 1):
        active = ' (ATIVA)' if t['token'] == config['token'] else ''
        print(f"{Colors.GRAY}[{i}]{Colors.RESET} {t['username']}#{t.get('discriminator', '0')}{Colors.GREEN}{active}{Colors.RESET}")
    
    choice = input(f"\n{Colors.WHITE}Escolha (1-{len(config['tokens'])}): {Colors.RESET}")
    index = int(choice) - 1 if choice.isdigit() else -1
    
    if 0 <= index < len(config['tokens']):
        selected = config['tokens'][index]
        global api
        config['token'] = selected['token']
        config['username'] = selected['username']
        config['userId'] = selected['userId']
        api = DiscordAPI(config['token'])
        save_config()
        await log(f"Conta ativa: {selected['username']}", 'success')
    else:
        await log('Opção inválida', 'error')
    
    await asyncio.sleep(2)

async def ver_contas():
    display_header()
    print(f"{Colors.WHITE}Contas Salvas{Colors.RESET}\n")
    await load_server_tokens()
    
    if not config['tokens']:
        await log('Nenhuma conta salva', 'warn')
    else:
        for i, t in enumerate(config['tokens'], 1):
            active = ' 🟢' if t['token'] == config['token'] else ' ⚪'
            print(f"\n{Colors.YELLOW}#{i}{active}{Colors.RESET}")
            print(f"  Username: {t['username']}#{t.get('discriminator', '0')}")
            print(f"  ID: {t['userId']}")
            print(f"  Email: {t.get('email', 'N/A')}")
    
    input(f"\n{Colors.GRAY}Pressione ENTER para voltar...{Colors.RESET}")

async def remover_conta():
    display_header()
    print(f"{Colors.CYAN}Remover Conta{Colors.RESET}\n")
    await load_server_tokens()
    
    if not config['tokens']:
        await log('Nenhuma conta salva', 'warn')
        await asyncio.sleep(2)
        return
    
    for i, t in enumerate(config['tokens'], 1):
        print(f"{Colors.GRAY}[{i}]{Colors.RESET} {t['username']}#{t.get('discriminator', '0')}")
    
    choice = input(f"\n{Colors.WHITE}Escolha (1-{len(config['tokens'])}): {Colors.RESET}")
    index = int(choice) - 1 if choice.isdigit() else -1
    
    if 0 <= index < len(config['tokens']):
        to_remove = config['tokens'][index]
        confirm = input(f"{Colors.RED}Remover {to_remove['username']}? (s/n): {Colors.RESET}")
        
        if confirm.lower() == 's':
            try:
                await server_api.remove_token(config['hwid'], to_remove['id'])
                
                if to_remove['token'] == config['token']:
                    global api
                    config['token'] = ''
                    config['username'] = 'Não conectado'
                    config['userId'] = ''
                    api = None
                    save_config()
                
                await log('Conta removida!', 'success')
                await load_server_tokens()
            except Exception as err:
                await log(f'Erro: {err}', 'error')
    
    await asyncio.sleep(2)

async def configurar_blacklist():
    display_header()
    print(f"{Colors.CYAN}Configurar Blacklist{Colors.RESET}\n")
    await log('Digite IDs separados por vírgula:', 'info')
    ids = input(f"{Colors.WHITE}IDs: {Colors.RESET}")
    
    try:
        blacklist = [uid.strip() for uid in ids.split(',') if uid.strip()]
        # Salvaria no servidor
        await log('Blacklist atualizada!', 'success')
    except Exception as err:
        await log(f'Erro: {err}', 'error')
    
    await asyncio.sleep(2)

async def ver_status():
    display_header()
    print(f"{Colors.CYAN}Status Premium{Colors.RESET}\n")
    await check_server_access()
    
    print(f"\n{Colors.WHITE}Detalhes:{Colors.RESET}")
    sub_color = Colors.YELLOW if config['subscription'] == 'premium' else Colors.CYAN
    print(f"  Tipo: {sub_color}{config['subscription'].upper()}{Colors.RESET}")
    print(f"  Expira: {Colors.CYAN}{config['expiresAt']}{Colors.RESET}")
    print(f"  HWID: {Colors.GRAY}{config['hwid']}{Colors.RESET}")
    print(f"  Contas: {Colors.GREEN}{len(config['tokens'])}{Colors.RESET}")
    
    if config['subscription'] == 'free':
        print(f"\n{Colors.YELLOW}ℹ  Para ativar o PREMIUM, entre em contato com o administrador{Colors.RESET}")
    
    input(f"\n{Colors.GRAY}Pressione ENTER para voltar...{Colors.RESET}")

async def sincronizar():
    display_header()
    print(f"{Colors.CYAN}Sincronizar com Servidor{Colors.RESET}\n")
    await log('Sincronizando...', 'info')
    await check_server_access()
    await load_server_tokens()
    await log('Sincronização concluída!', 'success')
    await asyncio.sleep(2)

async def configurar_webhook_geral():
    display_header()
    print(f"{Colors.CYAN}Configurar Webhook Geral{Colors.RESET}\n")
    
    if config.get('webhookUrl'):
        print(f"{Colors.GRAY}Webhook atual: {config['webhookUrl']}{Colors.RESET}\n")
    
    webhook = input(f"{Colors.WHITE}Webhook URL (deixe vazio para remover): {Colors.RESET}")
    
    if not webhook.strip():
        config['webhookUrl'] = None
        save_config()
        await log('Webhook removido com sucesso', 'success')
        await asyncio.sleep(1.5)
        return
    
    if not webhook.startswith('https://discord.com/api/webhooks/'):
        await log('URL de webhook inválida!', 'error')
        await log('Use um webhook do Discord válido', 'warn')
        await asyncio.sleep(2)
        return
    
    try:
        await log('Testando webhook...', 'info')
        
        test_embed = {
            'embeds': [{
                'title': '✅ Webhook Configurado',
                'description': 'Este webhook foi configurado com sucesso no seu SelfBot!',
                'color': 0x00ff00,
                'fields': [
                    {'name': 'HWID', 'value': config.get('hwid', 'N/A'), 'inline': True},
                    {'name': 'Usuário', 'value': config.get('username', 'N/A'), 'inline': True}
                ],
                'timestamp': datetime.utcnow().isoformat(),
                'footer': {'text': 'SelfBot System'}
            }]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook, json=test_embed) as resp:
                if resp.status not in [200, 204]:
                    await log('Webhook inválido ou sem permissões!', 'error')
                    await asyncio.sleep(2)
                    return
        
        config['webhookUrl'] = webhook
        save_config()
        
        await log('Webhook configurado e testado com sucesso!', 'success')
        await log('Este webhook será usado em todas as notificações', 'info')
        await asyncio.sleep(2)
        
    except Exception as err:
        await log(f'Erro ao testar webhook: {err}', 'error')
        await asyncio.sleep(2)

# ============= MAIN =============

async def main():
    global config
    
    load_config()
    
    if not config.get('hwid'):
        config['hwid'] = get_hwid()
        save_config()
    
    clear_screen()
    print(ASCII_ART)
    print(f"{Colors.CYAN}0xCL - dev > @odeiosegundas{Colors.RESET}\n")
    
    server_ok = await check_server_access()
    if not server_ok:
        await log('Não foi possível conectar ao servidor', 'error')
        await log('Verifique se o servidor está rodando', 'warn')
        await asyncio.sleep(3)
    else:
        await load_server_tokens()
        
        if config.get('token') and len(config['token']) > 50:
            await log(f"Conta carregada: {config['username']}", 'success')
            
            try:
                user_check = await api.get_user_info()
                if user_check['status'] != 200:
                    await log('Token salvo está inválido, será necessário reconfigurar', 'warn')
                    config['token'] = ''
                    config['username'] = 'Não conectado'
                    config['userId'] = ''
                    api = None
                    save_config()
            except:
                await log('Erro ao validar token salvo', 'warn')
            
            await asyncio.sleep(1.5)
    
    running = True
    while running:
        display_header()
        display_menu(MAIN_MENU)
        
        choice = input(f"{Colors.CYAN}> {Colors.RESET}")
        option = int(choice) if choice.isdigit() else -1
        
        if option == 0:
            print(f"\n{Colors.RED}Encerrando...{Colors.RESET}")
            running = False
            break
        
        try:
            if option == 1:
                await clear_dm()
            elif option == 2:
                await close_dms()
            elif option == 3:
                await clear_packages()
            elif option == 4:
                await trigger_clear()
            elif option == 5:
                await clear_all_dms()
            elif option == 6:
                await open_dms()
            elif option == 7:
                await clear_friends()
            elif option == 8:
                await clear_servers()
            elif option == 9:
                await tracker()
            elif option == 10:
                await kosame_farm()
            elif option == 11:
                await scrap_icon()
            elif option == 12:
                await spam_tools()
            elif option == 13:
                await spy()
            elif option == 14:
                await username_tools()
            elif option == 15:
                await nitro_sniper()
            elif option == 16:
                await server_cloner()
            elif option == 17:
                await backup_messages()
            elif option == 18:
                await settings_panel()
            else:
                await log('Opção inválida!', 'error')
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Operação cancelada{Colors.RESET}")
            await asyncio.sleep(1)
        except Exception as err:
            await log(f'Erro: {err}', 'error')
            await asyncio.sleep(2)

if __name__ == '__main__':
    try:
        # Define o título do terminal
        if os.name == 'nt':
            os.system('title >@odeiosegundas')
        
        # Executa o programa
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}Encerrando...{Colors.RESET}")
        sys.exit(0)
    except Exception as err:
        print(f"{Colors.RED}Erro não tratado: {err}{Colors.RESET}")
        sys.exit(1)