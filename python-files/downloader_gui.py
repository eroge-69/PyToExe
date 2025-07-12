from datetime import datetime
import os
import re
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import tkinter as tk
from tkinter import ttk, filedialog, StringVar, IntVar
import threading
from tkinter import scrolledtext, messagebox

def criar_pasta(caminho):
    """Cria uma pasta se ela não existir."""
    os.makedirs(caminho, exist_ok=True)

def extrair_serie_temporada(nome):
    """
    Extrai o nome da série, temporada e episódio do nome do arquivo.
    Ex: 'Minha Serie S01E05 - Titulo' -> ('Minha Serie', '01', '05')
    """
    match = re.search(r'(.*?)[\s.-]*S(\d+)[\s.-]*E(\d+)', nome, re.IGNORECASE)
    if match:
        # Limpa o nome da série de caracteres inválidos para nome de arquivo
        nome_serie = re.sub(r'[<>:"/\\|?*]', '', match.group(1).strip().replace('.', ' ').replace('-', ' '))
        temporada = match.group(2)
        episodio = match.group(3)
        return nome_serie, temporada, episodio
    # Caso não seja uma série, retorna o nome limpo e padrões '01' para temporada/episódio
    nome_limpo = re.sub(r'[<>:"/\\|?*]', '', nome)
    return nome_limpo, "01", "01"

def ja_baixado_completo(caminho, url):
    """
    Verifica se o arquivo já foi baixado completamente comparando tamanhos.
    Retorna True se o arquivo local tem o mesmo tamanho que o arquivo remoto,
    indicando que o download está completo.
    """
    if not os.path.exists(caminho):
        return False
    try:
        tamanho_arquivo_local = os.path.getsize(caminho)
        resposta = requests.head(url, timeout=10) # Usa HEAD para obter apenas os cabeçalhos
        tamanho_remoto = int(resposta.headers.get('content-length', 0))
        return tamanho_arquivo_local == tamanho_remoto
    except requests.exceptions.RequestException:
        # Erro de conexão ou tempo limite, considera que não pode verificar
        return False
    except ValueError:
        # Erro ao converter content-length para int, considera que não pode verificar
        return False

def baixar_arquivo(nome, url, destino, tentativas=3, progress_callback=None):
    """
    Baixa um arquivo com suporte a resumo (resume download) e múltiplas tentativas.
    Args:
        nome (str): Nome do arquivo (sem extensão).
        url (str): URL do arquivo a ser baixado.
        destino (str): Caminho da pasta de destino.
        tentativas (int): Número de tentativas em caso de falha.
        progress_callback (callable): Função de callback para atualizar o progresso individual.
                                     Recebe (baixado_atual, total_esperado).
    Returns:
        str: "sucesso", "pulado" ou "erro".
    """
    # Limpa o nome para garantir que seja um nome de arquivo válido
    nome_limpo = re.sub(r'[\\/:*?"<>|\[\]\-\']', '', nome).strip()
    caminho = os.path.join(destino, f"{nome_limpo}.mp4")

    for tentativa in range(1, tentativas + 1):
        try:
            if ja_baixado_completo(caminho, url):
                return "pulado"

            headers = {}
            modo = 'wb'
            baixado = 0
            # Se o arquivo existe localmente, tenta retomar o download
            if os.path.exists(caminho):
                baixado = os.path.getsize(caminho)
                headers['Range'] = f'bytes={baixado}-' # Solicita bytes a partir do ponto de interrupção
                modo = 'ab' # Abre em modo append binário para continuar o download

            resposta = requests.get(url, stream=True, timeout=30, headers=headers)
            # Verifica se o servidor suporta o resume (código 206 Partial Content)
            if resposta.status_code == 206 and baixado > 0:
                pass # Continua com o download
            elif resposta.status_code == 200 and baixado > 0:
                # Servidor não suporta resume ou está retornando o arquivo inteiro novamente
                baixado = 0 # Reinicia o download
                modo = 'wb' # Escreve um novo arquivo
            elif resposta.status_code != 200:
                raise requests.exceptions.RequestException(f"Status HTTP inesperado: {resposta.status_code}")


            total = int(resposta.headers.get('content-length', 0))
            if total == 0: # Se content-length não está disponível, tenta inferir
                 total = baixado + 1 # Apenas para evitar divisão por zero se for o primeiro download

            # Adiciona o que já foi baixado ao total esperado, se estiver retomando
            total_esperado = total + baixado

            with open(caminho, modo) as f:
                # A barra de progresso individual é controlada pela função `tqdm` na thread
                # mas o callback de progresso é para a interface gráfica
                for dados in tqdm(
                    resposta.iter_content(chunk_size=1024),
                    desc=nome_limpo[:25],
                    total=(total // 1024) if total > 0 else None,
                    unit='KB',
                    unit_scale=True,
                    leave=False,
                    ncols=70
                ):
                    if dados:
                        f.write(dados)
                        baixado += len(dados)
                        if progress_callback:
                            progress_callback(baixado, total_esperado)
            return "sucesso"
        except requests.exceptions.RequestException as e:
            # Captura exceções de requisição (conexão, timeout, etc.)
            if tentativa == tentativas:
                return f"erro: {e}"
            else:
                pass # Tenta novamente
        except Exception as e:
            # Captura outras exceções inesperadas
            if tentativa == tentativas:
                return f"erro: {e}"
            else:
                pass # Tenta novamente
    return "erro: falha desconhecida" # Fallback em caso de erro não capturado

def processar_lista(caminho_arquivo, tipo, max_threads, tentativas, interface):
    """
    Processa a lista de arquivos para download.
    Esta função roda em uma thread separada para não travar a interface.
    """
    interface.log("Iniciando processamento...")
    if not os.path.exists(caminho_arquivo):
        interface.log("❌ Arquivo .txt não encontrado. Por favor, selecione um arquivo válido.")
        return

    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
    except Exception as e:
        interface.log(f"❌ Erro ao ler o arquivo: {e}")
        return

    tarefas = []
    for i, linha in enumerate(linhas):
        linha_limpa = linha.strip()
        if not linha_limpa: # Ignora linhas vazias
            continue
        partes = linha_limpa.split(',', 2) # Divide em no máximo 3 partes
        if len(partes) < 3:
            interface.log(f"⚠️ Linha {i+1} inválida (formato, nome, url): {linha_limpa}")
            continue

        formato, nome, url = partes[0].strip(), partes[1].strip(), partes[2].strip()

        pasta = ""
        if tipo == 'filmes':
            pasta = os.path.join('Filmes')
        elif tipo == 'series':
            nome_serie, temp, _ = extrair_serie_temporada(nome)
            pasta = os.path.join('Séries', nome_serie, f'{int(temp)} Temporada S{temp.zfill(2)}')
        else:
            interface.log(f"⚠️ Tipo desconhecido na linha {i+1}: '{formato}'. Ignorando.")
            continue

        criar_pasta(pasta)
        tarefas.append((nome, url, pasta))

    total = len(tarefas)
    if total == 0:
        interface.log("Nenhuma tarefa válida encontrada no arquivo.")
        interface.master.after(0, lambda: interface.progress_bar.config(value=0))
        return

    sucesso = erro = pulado = 0
    erros_detalhados = []

    criar_pasta("Relatorios")
    inicio = datetime.now()

    # Resetar contadores na interface
    interface.master.after(0, lambda: interface.cont_sucesso.set("✅ Sucesso: 0"))
    interface.master.after(0, lambda: interface.cont_pulado.set("⚠️ Pulados: 0"))
    interface.master.after(0, lambda: interface.cont_erro.set("❌ Erros: 0"))
    interface.master.after(0, lambda: interface.progress_bar.config(maximum=total, value=0))

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        # Mapeia os futuros para suas respectivas tarefas para rastreamento
        futuros = {
            executor.submit(baixar_arquivo, nome, url, pasta, tentativas, lambda b, t: None): (nome, url)
            for nome, url, pasta in tarefas
        }
        # tqdm é usado aqui para a barra de progresso *no console*
        # O progresso da GUI é atualizado separadamente via `interface.master.after`
        with tqdm(total=total, desc="Progresso Geral (Console)", unit="arquivo", ncols=70) as barra:
            for future in as_completed(futuros):
                if interface.cancelar:
                    # Se o usuário clicou em cancelar, aguarda que as threads atuais terminem
                    # ou define um timeout para forçar o encerramento (mais complexo de implementar)
                    # Por simplicidade, `tqdm` continuará até que as threads ativas terminem suas tarefas atuais.
                    interface.log("🛑 Sinal de cancelamento recebido. Aguardando conclusão das tarefas atuais...")
                    break # Sai do loop de `as_completed`

                resultado = future.result()
                nome, url_original = futuros[future] # Recupera nome e URL originais
                if resultado == "pulado":
                    pulado += 1
                    interface.master.after(0, lambda: interface.cont_pulado.set(f"⚠️ Pulados: {pulado}"))
                elif resultado.startswith("erro"):
                    erro += 1
                    erros_detalhados.append(f"{nome} (URL: {url_original}) - {resultado}")
                    interface.master.after(0, lambda: interface.cont_erro.set(f"❌ Erros: {erro}"))
                else: # "sucesso"
                    sucesso += 1
                    interface.master.after(0, lambda: interface.cont_sucesso.set(f"✅ Sucesso: {sucesso}"))

                interface.master.after(0, lambda: interface.progress_bar.step(1))
                barra.update(1) # Atualiza a barra de progresso do console

    if interface.cancelar:
        interface.log("🛑 Download cancelado pelo usuário. Relatório não gerado.")
        interface.show_completion_message("Download Cancelado", "O download foi cancelado pelo usuário.")
        return

    fim = datetime.now()
    duracao = (fim - inicio).total_seconds()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nome_arquivo_relatorio = os.path.join("Relatorios", f"resumo_{timestamp}.txt")

    # Garante que o relatório seja escrito apenas se não foi cancelado
    with open(nome_arquivo_relatorio, 'w', encoding='utf-8') as resumo:
        resumo.write("=== RESUMO DO DOWNLOAD ===\n\n")
        resumo.write(f"📦 Total de arquivos processados: {total}\n")
        resumo.write(f"✅ Sucesso: {sucesso}\n")
        resumo.write(f"⚠️ Pulados: {pulado}\n")
        resumo.write(f"❌ Erros: {erro}\n")
        resumo.write(f"⏱️ Tempo total: {duracao:.2f} segundos\n\n")
        if erros_detalhados:
            resumo.write("=== ARQUIVOS COM ERRO ===\n")
            for item in erros_detalhados:
                resumo.write(f"- {item}\n")

    interface.log("✅ Download finalizado. Relatório gerado em 'Relatorios'.")
    interface.show_completion_message("Download Finalizado", "Todos os downloads foram concluídos com sucesso!")


class Interface:
    """
    Classe que gerencia a interface gráfica do usuário usando Tkinter.
    """
    def __init__(self, master):
        self.master = master
        master.title("Downloader de Mídias")
        master.geometry("550x550") # Tamanho inicial da janela
        master.resizable(False, False) # Impede redimensionamento da janela

        # Configurações de estilo para ttk
        style = ttk.Style()
        style.theme_use('clam') # 'clam', 'alt', 'default', 'classic'
        style.configure('TFrame', background='#e0e0e0')
        style.configure('TButton', font=('Arial', 10), padding=6, background='#4CAF50', foreground='black')
        style.map('TButton', background=[('active', '#45a049')])
        style.configure('TEntry', font=('Arial', 10), padding=3)
        style.configure('TLabel', font=('Arial', 10), background='#e0e0e0')
        style.configure('Horizontal.TProgressbar', thickness=15)


        # Frame principal para organização
        main_frame = ttk.Frame(master, padding="15 15 15 15", relief="raised")
        main_frame.grid(row=0, column=0, sticky="nsew")
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)

        # Configuração das colunas e linhas dentro do main_frame
        for i in range(4): # Colunas para campos de entrada e botões
            main_frame.columnconfigure(i, weight=1)
        # Linhas são configuradas individualmente

        # 1. Seleção de Arquivo TXT
        ttk.Label(main_frame, text="Arquivo .txt:").grid(row=0, column=0, sticky='w', pady=5, padx=5)
        self.caminho_txt = ttk.Entry(main_frame, width=50)
        self.caminho_txt.grid(row=0, column=1, columnspan=2, sticky='ew', pady=5, padx=5)
        ttk.Button(main_frame, text="Selecionar", command=self.selecionar_arquivo).grid(row=0, column=3, sticky='e', pady=5, padx=5)

        # 2. Tipo de Download (Filmes/Séries)
        ttk.Label(main_frame, text="Tipo:").grid(row=1, column=0, sticky='w', pady=5, padx=5)
        self.tipo = StringVar(value="filmes")
        ttk.Button(main_frame, text="Filmes", command=lambda: self.tipo.set("filmes")).grid(row=1, column=1, sticky='ew', pady=5, padx=5)
        ttk.Button(main_frame, text="Séries", command=lambda: self.tipo.set("series")).grid(row=1, column=2, sticky='ew', pady=5, padx=5)

        # 3. Downloads Simultâneos
        ttk.Label(main_frame, text="Downloads simultâneos:").grid(row=2, column=0, sticky='w', pady=5, padx=5)
        self.threads = ttk.Entry(main_frame, width=10)
        self.threads.insert(0, "3")
        self.threads.grid(row=2, column=1, sticky='w', pady=5, padx=5)

        # 4. Tentativas por Arquivo
        ttk.Label(main_frame, text="Tentativas por arquivo:").grid(row=3, column=0, sticky='w', pady=5, padx=5)
        self.tentativas = ttk.Entry(main_frame, width=10)
        self.tentativas.insert(0, "3")
        self.tentativas.grid(row=3, column=1, sticky='w', pady=5, padx=5)

        # Botões de Ação
        self.iniciar_btn = ttk.Button(main_frame, text="Iniciar Download", command=self.iniciar)
        self.iniciar_btn.grid(row=4, column=0, columnspan=2, sticky='ew', pady=10, padx=5)
        self.parar_btn = ttk.Button(main_frame, text="Parar Download", command=self.parar_download, state=tk.DISABLED)
        self.parar_btn.grid(row=4, column=2, columnspan=2, sticky='ew', pady=10, padx=5)

        # Barra de Progresso Geral
        self.progress_bar = ttk.Progressbar(main_frame, length=400, mode='determinate')
        self.progress_bar.grid(row=5, column=0, columnspan=4, sticky='ew', pady=10, padx=5)

        # Log de Mensagens
        ttk.Label(main_frame, text="Log de Atividades:").grid(row=6, column=0, sticky='w', pady=5, padx=5)
        self.log_widget = scrolledtext.ScrolledText(main_frame, width=60, height=8, wrap=tk.WORD, font=('Arial', 9))
        self.log_widget.grid(row=7, column=0, columnspan=4, sticky='nsew', pady=5, padx=5)
        main_frame.rowconfigure(7, weight=2) # Faz o ScrolledText expandir verticalmente

        self.clear_log_btn = ttk.Button(main_frame, text="Limpar Log", command=self.clear_log)
        self.clear_log_btn.grid(row=8, column=0, columnspan=4, sticky='ew', pady=5, padx=5)


        # Contadores de Status
        self.cont_sucesso = StringVar(value="✅ Sucesso: 0")
        self.cont_pulado = StringVar(value="⚠️ Pulados: 0")
        self.cont_erro = StringVar(value="❌ Erros: 0")

        ttk.Label(main_frame, textvariable=self.cont_sucesso).grid(row=9, column=0, columnspan=4, sticky='w', pady=(10, 0), padx=5)
        ttk.Label(main_frame, textvariable=self.cont_pulado).grid(row=10, column=0, columnspan=4, sticky='w', padx=5)
        ttk.Label(main_frame, textvariable=self.cont_erro).grid(row=11, column=0, columnspan=4, sticky='w', padx=5)

        self.cancelar = False
        self.download_thread = None # Para controlar a thread de download

    def selecionar_arquivo(self):
        """Abre uma caixa de diálogo para o usuário selecionar um arquivo .txt."""
        arquivo = filedialog.askopenfilename(filetypes=[("Arquivos de Texto", "*.txt")])
        if arquivo:
            self.caminho_txt.delete(0, 'end')
            self.caminho_txt.insert(0, arquivo)
            self.log(f"Arquivo selecionado: {os.path.basename(arquivo)}")

    def log(self, msg):
        """Adiciona uma mensagem ao widget de log."""
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        self.log_widget.insert(tk.END, f"{timestamp} {msg}\n")
        self.log_widget.see(tk.END) # Rola para o final do log

    def clear_log(self):
        """Limpa o conteúdo do widget de log."""
        self.log_widget.delete(1.0, tk.END)
        self.log("Log limpo.")

    def parar_download(self):
        """Define a flag de cancelamento e desabilita o botão de parada."""
        self.cancelar = True
        self.log("⏹️ Sinal de cancelamento enviado. Aguardando threads finalizarem...")
        self.parar_btn.config(state=tk.DISABLED) # Desabilita o botão para evitar múltiplos cliques

    def iniciar(self):
        """Inicia o processo de download em uma thread separada."""
        self.cancelar = False # Reseta a flag de cancelamento
        self.iniciar_btn.config(state=tk.DISABLED) # Desabilita o botão Iniciar
        self.parar_btn.config(state=tk.NORMAL) # Habilita o botão Parar

        caminho = self.caminho_txt.get()
        if not caminho:
            self.log("❌ Por favor, selecione um arquivo .txt primeiro.")
            self.iniciar_btn.config(state=tk.NORMAL)
            self.parar_btn.config(state=tk.DISABLED)
            return

        try:
            threads = int(self.threads.get())
            if threads <= 0:
                raise ValueError("Número de threads deve ser maior que zero.")
        except ValueError:
            threads = 3
            self.log("⚠️ Número de downloads simultâneos inválido. Usando 3.")
            self.threads.delete(0, 'end')
            self.threads.insert(0, "3")

        try:
            tentativas = int(self.tentativas.get())
            if tentativas <= 0:
                raise ValueError("Número de tentativas deve ser maior que zero.")
        except ValueError:
            tentativas = 3
            self.log("⚠️ Número de tentativas inválido. Usando 3.")
            self.tentativas.delete(0, 'end')
            self.tentativas.insert(0, "3")

        # Inicia o processo de download em uma nova thread
        self.download_thread = threading.Thread(
            target=processar_lista,
            args=(caminho, self.tipo.get(), threads, tentativas, self)
        )
        self.download_thread.start()
        # Monitora a thread para reabilitar os botões após a conclusão
        self.master.after(100, self._check_thread_status)

    def _check_thread_status(self):
        """Verifica o status da thread de download e reabilita os botões."""
        if self.download_thread and self.download_thread.is_alive():
            self.master.after(100, self._check_thread_status)
        else:
            self.iniciar_btn.config(state=tk.NORMAL)
            self.parar_btn.config(state=tk.DISABLED)

    def show_completion_message(self, title, message):
        """Mostra uma mensagem de conclusão usando messagebox."""
        messagebox.showinfo(title, message)


if __name__ == "__main__":
    root = tk.Tk()
    interface = Interface(root)
    root.mainloop()
