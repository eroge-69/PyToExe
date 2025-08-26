import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

# Constantes
NOME_ARQUIVO = 'historico_jogos.json'
LARGURA_JANELA = 750
ALTURA_JANELA = 700

class PodiumApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Programa de Pódio")
        self.root.geometry(f"{LARGURA_JANELA}x{ALTURA_JANELA}")
        self.root.resizable(False, True) # Não pode redimensionar na largura

        # Variáveis
        self.entradas_jogadores = []
        self.historico = self.carregar_historico()

        # --- Layout da Interface ---
        # Frame principal
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame de entrada de dados
        input_frame = ttk.LabelFrame(main_frame, text="Novo Jogo", padding="10")
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        # Data
        ttk.Label(input_frame, text="Data do Jogo:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.data_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        self.data_entry = ttk.Entry(input_frame, textvariable=self.data_var)
        self.data_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Container para entradas de jogadores
        self.jogadores_frame = ttk.Frame(input_frame)
        self.jogadores_frame.grid(row=1, column=0, columnspan=4, pady=10)
        ttk.Label(self.jogadores_frame, text="Nome do Jogador").grid(row=0, column=0, padx=5)
        ttk.Label(self.jogadores_frame, text="Pontuação").grid(row=0, column=1, padx=5)

        # Botões
        botoes_frame = ttk.Frame(input_frame)
        botoes_frame.grid(row=2, column=0, columnspan=4, pady=5)
        self.add_jogador_btn = ttk.Button(botoes_frame, text="+ Jogador", command=self.adicionar_campo_jogador)
        self.add_jogador_btn.pack(side=tk.LEFT, padx=5)
        self.add_jogo_btn = ttk.Button(botoes_frame, text="Adicionar Jogo e Calcular", command=self.processar_novo_jogo)
        self.add_jogo_btn.pack(side=tk.LEFT, padx=5)

        # Frame de resultados
        results_frame = ttk.LabelFrame(main_frame, text="Resultados", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Abas para Pódio, Histórico e Saldo
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.podio_tab = ttk.Frame(self.notebook)
        self.historico_tab = ttk.Frame(self.notebook)
        self.saldo_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.podio_tab, text="Pódio do Dia")
        self.notebook.add(self.historico_tab, text="Histórico de Posições")
        self.notebook.add(self.saldo_tab, text="Saldo Devedor")

        # Área de texto para os resultados
        self.podio_texto = tk.Text(self.podio_tab, wrap="word", height=15, width=80)
        self.podio_texto.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.podio_texto.config(state=tk.DISABLED)
        
        self.historico_texto = tk.Text(self.historico_tab, wrap="word", height=15, width=80)
        self.historico_texto.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.historico_texto.config(state=tk.DISABLED)

        self.saldo_texto = tk.Text(self.saldo_tab, wrap="word", height=15, width=80)
        self.saldo_texto.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.saldo_texto.config(state=tk.DISABLED)

        # Inicia com 3 campos de jogador
        for _ in range(3):
            self.adicionar_campo_jogador()
        
        # Atualiza a exibição inicial com dados do histórico
        self.atualizar_exibicao()

    def adicionar_campo_jogador(self):
        row = len(self.entradas_jogadores) + 1 # +1 para pular o header
        
        nome_var = tk.StringVar()
        pontos_var = tk.StringVar()

        nome_entry = ttk.Entry(self.jogadores_frame, textvariable=nome_var, width=30)
        nome_entry.grid(row=row, column=0, padx=5, pady=2)

        pontos_entry = ttk.Entry(self.jogadores_frame, textvariable=pontos_var, width=15)
        pontos_entry.grid(row=row, column=1, padx=5, pady=2)
        
        self.entradas_jogadores.append({'nome_var': nome_var, 'pontos_var': pontos_var})

    def carregar_historico(self):
        try:
            with open(NOME_ARQUIVO, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def salvar_historico(self):
        with open(NOME_ARQUIVO, 'w', encoding='utf-8') as f:
            json.dump(self.historico, f, indent=4, ensure_ascii=False)

    def processar_novo_jogo(self):
        data_jogo = self.data_var.get()
        jogadores = []

        for entrada in self.entradas_jogadores:
            nome = entrada['nome_var'].get().strip()
            pontos_str = entrada['pontos_var'].get().strip()

            if nome and pontos_str:
                try:
                    pontos = int(pontos_str)
                    jogadores.append({'nome': nome, 'pontos': pontos})
                except ValueError:
                    messagebox.showerror("Erro de Entrada", f"A pontuação '{pontos_str}' para {nome} não é um número válido.")
                    return
        
        if len(jogadores) < 2:
            messagebox.showwarning("Aviso", "É preciso ter pelo menos 2 jogadores com nome e pontuação preenchidos.")
            return

        # Ordenar jogadores pela pontuação (menor para maior)
        jogadores.sort(key=lambda x: x['pontos'])

        # Calcular posição e pagamento
        resultados = []
        posicao_atual = 1
        for i, jogador in enumerate(jogadores):
            if i > 0 and jogador['pontos'] > jogadores[i-1]['pontos']:
                posicao_atual = i + 1
            
            pagamento = posicao_atual * 0.50
            resultados.append({
                'nome': jogador['nome'],
                'pontos': jogador['pontos'],
                'posicao': posicao_atual,
                'pagamento': pagamento
            })
        
        # Adicionar ao histórico
        self.historico.append({'data': data_jogo, 'resultados': resultados})
        self.salvar_historico()

        # Atualizar a interface
        self.atualizar_exibicao(jogo_recente=self.historico[-1])
        messagebox.showinfo("Sucesso", "Jogo adicionado e resultados calculados!")
        
        # Limpar campos para o próximo jogo
        for entrada in self.entradas_jogadores:
            entrada['nome_var'].set("")
            entrada['pontos_var'].set("")
        self.data_var.set(datetime.now().strftime('%d/%m/%Y'))

    def atualizar_exibicao(self, jogo_recente=None):
        # 1. Pódio do Dia
        podio_str = ""
        if jogo_recente:
            podio_str += f"--- Pódio do Jogo de {jogo_recente['data']} ---\n\n"
            for r in jogo_recente['resultados']:
                podio_str += f"{r['posicao']}º Lugar: {r['nome']} ({r['pontos']} pontos) - Paga R$ {r['pagamento']:.2f}\n"
        else:
            podio_str = "Adicione um novo jogo para ver o pódio aqui."
        
        self.podio_texto.config(state=tk.NORMAL)
        self.podio_texto.delete(1.0, tk.END)
        self.podio_texto.insert(tk.END, podio_str)
        self.podio_texto.config(state=tk.DISABLED)

        # 2. Histórico e 3. Saldo Devedor
        if not self.historico:
            historico_str = "Nenhum histórico de posições ainda."
            saldo_str = "Nenhum saldo a ser calculado."
        else:
            stats_posicoes = {}
            saldo_devedor = {}

            for jogo in self.historico:
                for resultado in jogo['resultados']:
                    nome = resultado['nome']
                    posicao = resultado['posicao']
                    pagamento = resultado['pagamento']

                    # Atualiza saldo
                    saldo_devedor[nome] = saldo_devedor.get(nome, 0) + pagamento

                    # Atualiza estatísticas de posições
                    if nome not in stats_posicoes:
                        stats_posicoes[nome] = {}
                    stats_posicoes[nome][posicao] = stats_posicoes[nome].get(posicao, 0) + 1
            
            # Formata string do histórico
            historico_str = "--- Quantas vezes cada jogador ficou em cada posição ---\n\n"
            for nome, posicoes in sorted(stats_posicoes.items()):
                historico_str += f"Jogador: {nome}\n"
                for pos, count in sorted(posicoes.items()):
                    vezes = "vez" if count == 1 else "vezes"
                    historico_str += f"  - {count} {vezes} em {pos}º lugar\n"
                historico_str += "\n"

            # Formata string do saldo
            saldo_str = "--- Montante que cada jogador deve pagar ---\n\n"
            for nome, valor in sorted(saldo_devedor.items(), key=lambda item: item[1], reverse=True):
                saldo_str += f"{nome}: R$ {valor:.2f}\n"

        # Atualiza a aba de histórico
        self.historico_texto.config(state=tk.NORMAL)
        self.historico_texto.delete(1.0, tk.END)
        self.historico_texto.insert(tk.END, historico_str)
        self.historico_texto.config(state=tk.DISABLED)

        # Atualiza a aba de saldo
        self.saldo_texto.config(state=tk.NORMAL)
        self.saldo_texto.delete(1.0, tk.END)
        self.saldo_texto.insert(tk.END, saldo_str)
        self.saldo_texto.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = PodiumApp(root)
    root.mainloop()