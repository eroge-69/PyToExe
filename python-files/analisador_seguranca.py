#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisador de Segurança de Rede - Interface Gráfica
Sistema de Detecção de Ameaças em Logs de Rede

Autor: José da Silva Botelho Filho
Versão: 3.0.0
Data de Criação: 15/08/2025
Última Atualização: 15/08/2025

Descrição: Analisador com interface gráfica para logs de segurança
Licença: Uso interno - SOC Security Operations
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import csv
import os
from datetime import datetime
from collections import Counter, defaultdict
import threading

__author__ = "José da Silva Botelho Filho"
__version__ = "3.0.0"

class NetworkAnalyzerGUI:
    def __init__(self):
        self.version = __version__
        self.author = __author__
        self.files_to_analyze = []
        
        # Definições de ataques
        self.attack_types = {
            'port_scanning': {'name': 'Port Scanning', 'severity': 'ALTA'},
            'ddos_attack': {'name': 'DDoS Attack', 'severity': 'CRÍTICA'},
            'brute_force': {'name': 'Brute Force Attack', 'severity': 'ALTA'},
            'data_exfiltration': {'name': 'Data Exfiltration', 'severity': 'CRÍTICA'},
            'reconnaissance': {'name': 'Network Reconnaissance', 'severity': 'MÉDIA'},
            'suspicious_traffic': {'name': 'Suspicious Traffic', 'severity': 'BAIXA'}
        }
        
        self.critical_ports = {
            22: 'SSH', 23: 'Telnet', 53: 'DNS', 80: 'HTTP',
            135: 'RPC', 139: 'NetBIOS', 443: 'HTTPS', 445: 'SMB',
            993: 'IMAPS', 995: 'POP3S', 1433: 'MSSQL', 3389: 'RDP'
        }
        
        self.setup_gui()

    def setup_gui(self):
        """Configura a interface gráfica"""
        
        # Janela principal
        self.root = tk.Tk()
        self.root.title(f"Analisador de Segurança de Rede v{self.version}")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Ícone e configurações da janela
        self.root.resizable(True, True)
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Título
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky=(tk.W, tk.E))
        
        title_label = ttk.Label(title_frame, text="🔒 ANALISADOR DE SEGURANÇA DE REDE", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0)
        
        subtitle_label = ttk.Label(title_frame, text=f"Desenvolvido por: {self.author} | Versão: {self.version}",
                                  font=('Arial', 10))
        subtitle_label.grid(row=1, column=0, pady=(5, 0))
        
        # Frame de seleção de arquivos
        file_frame = ttk.LabelFrame(main_frame, text="📁 Seleção de Arquivos", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, pady=(0, 10), sticky=(tk.W, tk.E))
        file_frame.columnconfigure(1, weight=1)
        
        # Botões de arquivo
        ttk.Button(file_frame, text="Selecionar Arquivos CSV", 
                  command=self.select_files).grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(file_frame, text="Buscar tesp*.csv", 
                  command=self.find_tesp_files).grid(row=0, column=1, padx=(0, 10))
        
        # Lista de arquivos selecionados
        self.files_listbox = tk.Listbox(file_frame, height=4)
        self.files_listbox.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E))
        
        # Frame de controles
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Botões principais
        ttk.Button(control_frame, text="🔍 ANALISAR ARQUIVOS", 
                  command=self.start_analysis, style='Accent.TButton').grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(control_frame, text="📄 GERAR RELATÓRIO", 
                  command=self.generate_report).grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(control_frame, text="🗑️ LIMPAR", 
                  command=self.clear_results).grid(row=0, column=2, padx=(0, 10))
        
        # Barra de progresso
        self.progress = ttk.Progressbar(control_frame, mode='indeterminate')
        self.progress.grid(row=0, column=3, padx=(10, 0), sticky=(tk.W, tk.E))
        control_frame.columnconfigure(3, weight=1)
        
        # Área de resultados
        results_frame = ttk.LabelFrame(main_frame, text="📊 Resultados da Análise", padding="10")
        results_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Text area com scroll
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, 
                                                     font=('Consolas', 10))
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Pronto para análise")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Variável para armazenar resultados
        self.analysis_results = []

    def select_files(self):
        """Seleciona arquivos CSV para análise"""
        files = filedialog.askopenfilenames(
            title="Selecionar arquivos CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if files:
            self.files_to_analyze = list(files)
            self.update_files_list()
            self.status_var.set(f"{len(files)} arquivo(s) selecionado(s)")

    def find_tesp_files(self):
        """Busca automaticamente arquivos tesp*.csv no diretório atual"""
        import glob
        tesp_files = glob.glob("tesp*.csv")
        
        if tesp_files:
            self.files_to_analyze = tesp_files
            self.update_files_list()
            self.status_var.set(f"{len(tesp_files)} arquivo(s) tesp*.csv encontrado(s)")
        else:
            messagebox.showwarning("Aviso", "Nenhum arquivo tesp*.csv encontrado no diretório atual.")

    def update_files_list(self):
        """Atualiza a lista de arquivos na interface"""
        self.files_listbox.delete(0, tk.END)
        for file in self.files_to_analyze:
            filename = os.path.basename(file)
            self.files_listbox.insert(tk.END, filename)

    def start_analysis(self):
        """Inicia a análise em thread separada"""
        if not self.files_to_analyze:
            messagebox.showerror("Erro", "Selecione pelo menos um arquivo CSV para análise.")
            return
        
        # Executar análise em thread separada para não travar a interface
        self.progress.start()
        self.status_var.set("Analisando arquivos...")
        
        analysis_thread = threading.Thread(target=self.perform_analysis)
        analysis_thread.daemon = True
        analysis_thread.start()

    def perform_analysis(self):
        """Executa a análise dos arquivos"""
        try:
            self.analysis_results = []
            
            for i, file_path in enumerate(self.files_to_analyze):
                # Atualizar status na thread principal
                self.root.after(0, lambda: self.status_var.set(f"Analisando {os.path.basename(file_path)}..."))
                
                result = self.analyze_file(file_path)
                self.analysis_results.append(result)
            
            # Mostrar resultados na thread principal
            self.root.after(0, self.display_results)
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.status_var.set("Análise concluída"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro durante análise: {str(e)}"))
            self.root.after(0, lambda: self.progress.stop())

    def analyze_file(self, file_path):
        """Analisa um arquivo CSV específico"""
        try:
            # Ler arquivo CSV
            data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        row['packetSize'] = int(row['packetSize'])
                        row['destinationPort'] = int(row['destinationPort'])
                        row['sourcePort'] = int(row['sourcePort'])
                        row['datetime'] = datetime.fromisoformat(row['datetime'].replace('Z', '+00:00'))
                        data.append(row)
                    except (ValueError, KeyError):
                        continue
            
            # Separar pacotes
            passed_packets = [row for row in data if row['actionTaken'] == 'pass']
            blocked_packets = [row for row in data if row['actionTaken'] == 'drop']
            
            if not passed_packets:
                return {
                    'file': file_path,
                    'total_packets': len(data),
                    'passed_packets': 0,
                    'blocked_packets': len(blocked_packets),
                    'malicious_activities': [],
                    'summary': '✅ Nenhum pacote malicioso passou'
                }
            
            # Análise por IP
            malicious_activities = []
            ip_stats = defaultdict(lambda: {
                'connections': 0, 'unique_ports': set(), 'packet_sizes': [],
                'timestamps': [], 'total_bytes': 0
            })
            
            for packet in passed_packets:
                ip = packet['sourceIP']
                stats = ip_stats[ip]
                stats['connections'] += 1
                stats['unique_ports'].add(packet['destinationPort'])
                stats['packet_sizes'].append(packet['packetSize'])
                stats['timestamps'].append(packet['datetime'])
                stats['total_bytes'] += packet['packetSize']
            
            # Detectar atividades maliciosas
            for source_ip, stats in ip_stats.items():
                unique_ports_count = len(stats['unique_ports'])
                avg_packet_size = sum(stats['packet_sizes']) / len(stats['packet_sizes'])
                
                # Calcular pico por minuto
                minute_counts = Counter()
                for timestamp in stats['timestamps']:
                    minute_key = timestamp.replace(second=0, microsecond=0)
                    minute_counts[minute_key] += 1
                max_per_minute = max(minute_counts.values()) if minute_counts else 0
                
                # Verificar se é suspeito
                is_suspicious = (
                    stats['connections'] > 5 or unique_ports_count > 2 or
                    max_per_minute > 10 or avg_packet_size <= 50 or avg_packet_size > 1200
                )
                
                if is_suspicious:
                    attack_type = self.identify_attack_type(stats, unique_ports_count, avg_packet_size, max_per_minute)
                    
                    ip_packets = [p for p in passed_packets if p['sourceIP'] == source_ip]
                    for packet in ip_packets[:5]:  # Limitar exemplos
                        malicious_activities.append({
                            'timestamp': packet['datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                            'source_ip': packet['sourceIP'],
                            'dest_ip': packet['destinationIP'],
                            'dest_port': packet['destinationPort'],
                            'protocol': packet['protocolName'],
                            'packet_size': packet['packetSize'],
                            'attack_type': attack_type,
                            'attack_name': self.attack_types[attack_type]['name'],
                            'severity': self.attack_types[attack_type]['severity'],
                            'port_service': self.critical_ports.get(packet['destinationPort'], 'Unknown'),
                            'connections_total': stats['connections'],
                            'unique_ports_count': unique_ports_count,
                            'max_per_minute': max_per_minute
                        })
            
            return {
                'file': file_path,
                'total_packets': len(data),
                'passed_packets': len(passed_packets),
                'blocked_packets': len(blocked_packets),
                'malicious_activities': malicious_activities,
                'summary': f'{"❌" if malicious_activities else "✅"} {len(malicious_activities)} atividades maliciosas'
            }
            
        except Exception as e:
            return {'error': f'Erro ao analisar {file_path}: {str(e)}'}

    def identify_attack_type(self, stats, unique_ports, avg_packet_size, max_per_minute):
        """Identifica o tipo de ataque"""
        if max_per_minute > 30 or stats['connections'] > 100:
            return 'ddos_attack'
        elif unique_ports > 5 and avg_packet_size <= 64:
            return 'port_scanning'
        elif avg_packet_size > 1000 and stats['total_bytes'] > 500000:
            return 'data_exfiltration'
        elif any(port in self.critical_ports for port in stats['unique_ports']) and stats['connections'] > 15:
            return 'brute_force'
        elif unique_ports > 3 and avg_packet_size <= 100:
            return 'reconnaissance'
        else:
            return 'suspicious_traffic'

    def display_results(self):
        """Exibe os resultados na interface"""
        self.results_text.delete(1.0, tk.END)
        
        # Cabeçalho
        self.results_text.insert(tk.END, "🔒 RESULTADOS DA ANÁLISE DE SEGURANÇA\n")
        self.results_text.insert(tk.END, "=" * 60 + "\n\n")
        
        # Resumo geral
        total_files = len([r for r in self.analysis_results if 'error' not in r])
        total_malicious = sum(len(r.get('malicious_activities', [])) for r in self.analysis_results if 'error' not in r)
        
        self.results_text.insert(tk.END, f"📊 RESUMO GERAL:\n")
        self.results_text.insert(tk.END, f"   Arquivos analisados: {total_files}\n")
        self.results_text.insert(tk.END, f"   Ameaças detectadas: {total_malicious}\n")
        self.results_text.insert(tk.END, f"   Status: {'🔴 CRÍTICO' if total_malicious > 50 else '🟡 ATENÇÃO' if total_malicious > 0 else '🟢 SEGURO'}\n\n")
        
        # Resultados por arquivo
        for result in self.analysis_results:
            if 'error' in result:
                self.results_text.insert(tk.END, f"❌ ERRO: {result['error']}\n\n")
                continue
            
            file_name = os.path.basename(result['file'])
            self.results_text.insert(tk.END, f"📁 {file_name.upper()}\n")
            self.results_text.insert(tk.END, f"   Total: {result['total_packets']} | Permitidos: {result['passed_packets']} | Bloqueados: {result['blocked_packets']}\n")
            self.results_text.insert(tk.END, f"   {result['summary']}\n")
            
            if result['malicious_activities']:
                self.results_text.insert(tk.END, f"\n   🚨 AMEAÇAS DETECTADAS:\n")
                
                # Agrupar por tipo
                attack_summary = defaultdict(list)
                for activity in result['malicious_activities']:
                    attack_summary[activity['attack_name']].append(activity)
                
                for attack_name, activities in attack_summary.items():
                    severity = activities[0]['severity']
                    unique_ips = len(set(a['source_ip'] for a in activities))
                    self.results_text.insert(tk.END, f"      🔥 {attack_name} ({severity}) - {len(activities)} ocorrências\n")
                    
                    for activity in activities[:3]:  # Mostrar 3 exemplos
                        self.results_text.insert(tk.END, f"         {activity['source_ip']} → {activity['dest_ip']}:{activity['dest_port']} ({activity['port_service']})\n")
            
            self.results_text.insert(tk.END, "\n" + "-" * 60 + "\n\n")

    def generate_report(self):
        """Gera relatório detalhado em arquivo"""
        if not self.analysis_results:
            messagebox.showwarning("Aviso", "Execute uma análise antes de gerar o relatório.")
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"relatorio_seguranca_{timestamp}.txt"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("RELATÓRIO DE ANÁLISE DE SEGURANÇA DE REDE\n")
                f.write(f"Desenvolvido por: {self.author} | Versão: {self.version}\n")
                f.write(f"Relatório gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                
                # Detalhes completos
                for result in self.analysis_results:
                    if 'error' in result:
                        f.write(f"❌ ERRO: {result['error']}\n\n")
                        continue
                    
                    file_name = os.path.basename(result['file'])
                    f.write(f"📁 ARQUIVO: {file_name}\n")
                    f.write(f"Total: {result['total_packets']} | Permitidos: {result['passed_packets']} | Bloqueados: {result['blocked_packets']}\n")
                    f.write(f"{result['summary']}\n\n")
                    
                    if result['malicious_activities']:
                        f.write("🚨 DETALHES DAS AMEAÇAS:\n")
                        for activity in result['malicious_activities']:
                            f.write(f"   {activity['timestamp']} | {activity['attack_name']} ({activity['severity']})\n")
                            f.write(f"   {activity['source_ip']} → {activity['dest_ip']}:{activity['dest_port']} ({activity['port_service']})\n")
                            f.write(f"   Protocolo: {activity['protocol']} | Tamanho: {activity['packet_size']} bytes\n\n")
                    
                    f.write("\n" + "-" * 60 + "\n\n")
            
            messagebox.showinfo("Sucesso", f"Relatório salvo como: {report_file}")
            self.status_var.set(f"Relatório salvo: {report_file}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {str(e)}")

    def clear_results(self):
        """Limpa os resultados e arquivos selecionados"""
        self.files_to_analyze = []
        self.analysis_results = []
        self.files_listbox.delete(0, tk.END)
        self.results_text.delete(1.0, tk.END)
        self.status_var.set("Pronto para análise")

    def run(self):
        """Executa a aplicação"""
        self.root.mainloop()

# Programa Principal
if __name__ == "__main__":
    app = NetworkAnalyzerGUI()
    app.run()
