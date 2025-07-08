#!/usr/bin/env python3
"""
Versão GUI do script para atualizar o CNPJ do destinatario em arquivos XML.

O script permite selecionar múltiplos arquivos XML, escolher uma empresa da lista, 
e atualiza o valor do elemento <CNPJ> com o CNPJ correspondente à empresa selecionada.
"""

import logging
import xml.etree.ElementTree as ET
from pathlib import Path
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Dicionário com empresas e seus CNPJs (sem pontuação)
EMPRESAS = {
    "LM": "08686300000188",
    "LMC": "17343411000182",
    "ECG": "26527488000101",
    "J&C": "22729846000108",
    "ULTRA JP": "34713312000164",
    "ULTRA MEGA": "22516839000110",
    "ULTRA TRINDADE": "45676232000364",
    "ULTRA GOIANIA": "45676232000445",
    "DROGABEM": "42697158000102",
    "ULTRA UNIVERSITARIA": "45676232000283"
}

def atualizar_cnpj_em_xml(caminho_arquivo: Path, novo_cnpj: str) -> bool:
    """
    Atualiza o CNPJ em um arquivo XML.
    
    Parameters:
        caminho_arquivo (Path): Caminho do arquivo XML.
        novo_cnpj (str): Novo CNPJ a ser atribuído.
        
    Returns:
        bool: True se a atualização foi bem-sucedida, False caso contrário.
    """
    try:
        tree = ET.parse(caminho_arquivo)
        root = tree.getroot()

        ns = ''
        ns_prefix = ''
        if root.tag.startswith('{'):
            ns = root.tag.split('}')[0].strip('{')
            ns_prefix = f"{{{ns}}}"
            # Registra o namespace pra que ele seja escrito como namespace padrão, evita quebrar o xml
            ET.register_namespace("", ns)

        atualizado = False

        for dest in root.iter(f"{ns_prefix}dest"):
            cnpj_elem = dest.find(f"{ns_prefix}CNPJ")
            if cnpj_elem is not None:
                logging.info(f"Arquivo {caminho_arquivo}: atualizando CNPJ de {cnpj_elem.text} para {novo_cnpj}")
                cnpj_elem.text = novo_cnpj
                atualizado = True

        if atualizado:
            tree.write(caminho_arquivo, encoding="utf-8", xml_declaration=True)
            logging.info(f"Arquivo {caminho_arquivo} atualizado com sucesso.")
            return True
        else:
            logging.warning(f"Arquivo {caminho_arquivo}: nenhum elemento <CNPJ> encontrado em <dest>.")
            return False

    except ET.ParseError as pe:
        logging.error(f"Erro ao parsear o arquivo {caminho_arquivo}: {pe}")
        return False
    except Exception as e:
        logging.error(f"Erro ao processar o arquivo {caminho_arquivo}: {e}")
        return False


class AplicativoAtualizadorCNPJ:
    def __init__(self, root):
        self.root = root
        self.root.title("Atualizador de CNPJ em XMLs")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # Configuração de log
        logging.basicConfig(level='INFO', format="%(levelname)s: %(message)s")
        
        # Variáveis
        self.empresa_selecionada = tk.StringVar()
        self.cnpj_atual = tk.StringVar()
        self.status_text = tk.StringVar(value="Pronto para iniciar")
        self.arquivos_selecionados = []
        
        # Configura a seleção de empresa para atualizar CNPJ automaticamente
        self.empresa_selecionada.trace('w', self.atualizar_cnpj)
        
        self.criar_widgets()
    
    def criar_widgets(self):
        """Cria os widgets da interface"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Seleção de arquivos
        ttk.Label(main_frame, text="Arquivos XML selecionados:").grid(column=0, row=0, sticky=tk.W, pady=5)
        
        # Frame para lista de arquivos selecionados com barra de rolagem
        arquivo_frame = ttk.Frame(main_frame)
        arquivo_frame.grid(column=0, row=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Scrollbar para a lista de arquivos
        scrollbar = ttk.Scrollbar(arquivo_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Lista de arquivos selecionados
        self.arquivo_listbox = tk.Listbox(arquivo_frame, height=8, width=70, yscrollcommand=scrollbar.set)
        self.arquivo_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.arquivo_listbox.yview)
        
        # Botões para seleção de arquivos
        arquivo_botoes_frame = ttk.Frame(main_frame)
        arquivo_botoes_frame.grid(column=0, row=2, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Button(arquivo_botoes_frame, text="Selecionar Arquivos", command=self.selecionar_arquivos).pack(side=tk.LEFT, padx=5)
        ttk.Button(arquivo_botoes_frame, text="Limpar Seleção", command=self.limpar_selecao).pack(side=tk.LEFT, padx=5)
        
        # Contador de arquivos selecionados
        self.contador_arquivos = ttk.Label(arquivo_botoes_frame, text="0 arquivos selecionados")
        self.contador_arquivos.pack(side=tk.LEFT, padx=20)
        
        # Seleção de empresa
        ttk.Label(main_frame, text="Selecione a Empresa:").grid(column=0, row=3, sticky=tk.W, pady=(15, 5))
        empresas_combo = ttk.Combobox(main_frame, textvariable=self.empresa_selecionada, state="readonly", width=30)
        empresas_combo['values'] = list(EMPRESAS.keys())
        empresas_combo.grid(column=0, row=4, sticky=tk.W, padx=5)
        
        # Campo CNPJ
        ttk.Label(main_frame, text="CNPJ:").grid(column=0, row=5, sticky=tk.W, pady=(15, 5))
        ttk.Entry(main_frame, textvariable=self.cnpj_atual, width=20, state="readonly").grid(column=0, row=6, sticky=tk.W, padx=5)
        
        # Frame de progresso
        progress_frame = ttk.LabelFrame(main_frame, text="Progresso", padding="10")
        progress_frame.grid(column=0, row=7, columnspan=2, sticky=tk.EW, pady=15, padx=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=500, mode='determinate')
        self.progress_bar.pack(fill=tk.X, expand=True, pady=5)
        
        ttk.Label(progress_frame, textvariable=self.status_text).pack(fill=tk.X, expand=True)
        
        # Botões de ação
        botoes_frame = ttk.Frame(main_frame)
        botoes_frame.grid(column=0, row=8, columnspan=2, sticky=tk.EW, pady=10)
        
        ttk.Button(botoes_frame, text="Atualizar XMLs", command=self.atualizar_xmls).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="Sair", command=self.root.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Configuração de redimensionamento
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)  # Permite que a lista de arquivos expanda
        
    def selecionar_arquivos(self):
        """Abre o diálogo para selecionar múltiplos arquivos XML"""
        arquivos = filedialog.askopenfilenames(
            title="Selecionar arquivos XML",
            filetypes=[("Arquivos XML", "*.xml"), ("Todos os arquivos", "*.*")]
        )
        
        if arquivos:
            # Limpa a seleção anterior
            self.limpar_selecao()
            
            # Adiciona os novos arquivos à lista
            for arquivo in arquivos:
                self.arquivos_selecionados.append(arquivo)
                self.arquivo_listbox.insert(tk.END, os.path.basename(arquivo))
            
            # Atualiza o contador
            self.atualizar_contador_arquivos()
    
    def limpar_selecao(self):
        """Limpa a seleção de arquivos"""
        self.arquivos_selecionados = []
        self.arquivo_listbox.delete(0, tk.END)
        self.atualizar_contador_arquivos()
    
    def atualizar_contador_arquivos(self):
        """Atualiza o contador de arquivos selecionados"""
        quantidade = len(self.arquivos_selecionados)
        texto = f"{quantidade} arquivo{'s' if quantidade != 1 else ''} selecionado{'s' if quantidade != 1 else ''}"
        self.contador_arquivos.config(text=texto)
            
    def atualizar_cnpj(self, *args):
        """Atualiza o CNPJ quando uma empresa é selecionada"""
        empresa = self.empresa_selecionada.get()
        if empresa in EMPRESAS:
            self.cnpj_atual.set(EMPRESAS[empresa])
            
    def atualizar_xmls(self):
        """Processa os arquivos XML selecionados"""
        arquivos = self.arquivos_selecionados
        cnpj = self.cnpj_atual.get()
        
        if not arquivos:
            messagebox.showerror("Erro", "Nenhum arquivo selecionado!")
            return
            
        if not cnpj:
            messagebox.showerror("Erro", "Selecione uma empresa!")
            return
            
        try:
            # Prepara o processamento
            total_arquivos = len(arquivos)
            
            # Configura a barra de progresso
            self.progress_bar['maximum'] = total_arquivos
            self.progress_bar['value'] = 0
            arquivos_atualizados = 0
            
            # Processa cada arquivo
            for i, arquivo_path in enumerate(arquivos):
                arquivo = Path(arquivo_path)
                self.status_text.set(f"Processando: {arquivo.name}")
                self.root.update_idletasks()  # Força atualização da interface
                
                if atualizar_cnpj_em_xml(arquivo, cnpj):
                    arquivos_atualizados += 1
                    
                self.progress_bar['value'] = i + 1
                self.root.update_idletasks()
                
            # Finaliza
            self.status_text.set(f"Concluído! {arquivos_atualizados}/{total_arquivos} arquivos atualizados")
            messagebox.showinfo("Concluído", f"Processamento concluído!\n\n{arquivos_atualizados} de {total_arquivos} arquivos atualizados.")
            
        except Exception as e:
            logging.error(f"Erro durante o processamento: {e}")
            messagebox.showerror("Erro", f"Erro durante o processamento: {e}")
            self.status_text.set("Erro durante o processamento")


def main():
    root = tk.Tk()
    app = AplicativoAtualizadorCNPJ(root)
    root.mainloop()


if __name__ == "__main__":
    main()
