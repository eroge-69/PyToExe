#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Clicker Personalizado
Desenvolvido em Python para funcionar no terminal/CMD
Autor: Assistant
Versão: 2.0
"""

import pyautogui
import keyboard
import time
import threading
import os
import sys
from colorama import init, Fore, Style, Back

# Inicializar colorama para cores no terminal
init(autoreset=True)

class AutoClicker:
    def __init__(self):
        self.running = False
        self.paused = False
        self.click_interval = 0.1  # 100ms padrão
        self.trigger_key = 'a'  # tecla padrão
        self.click_count = 0
        self.thread = None
        
        # Configurações de segurança do pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.001
    
    def clear_screen(self):
        """Limpa a tela do terminal"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Imprime o cabeçalho do programa"""
        print(f"{Fore.CYAN}{Style.BRIGHT}{'='*60}")
        print(f"{Fore.YELLOW}{Style.BRIGHT}🖱️  AUTO CLICKER PYTHON v2.0  🖱️")
        print(f"{Fore.CYAN}{Style.BRIGHT}{'='*60}")
        print()
    
    def print_config(self):
        """Mostra as configurações atuais"""
        status_color = Fore.GREEN if self.running else Fore.RED
        status_text = "ATIVO" if self.running else "PARADO"
        
        print(f"{Fore.MAGENTA}📋 CONFIGURAÇÕES ATUAIS:")
        print(f"{Fore.WHITE}┌─────────────────────────────────────┐")
        print(f"{Fore.WHITE}│ Tecla de Ativação: {Fore.YELLOW}{self.trigger_key.upper():<15}{Fore.WHITE}│")
        print(f"{Fore.WHITE}│ Intervalo: {Fore.CYAN}{self.click_interval*1000:>8.0f}ms{Fore.WHITE}         │")
        print(f"{Fore.WHITE}│ CPS: {Fore.GREEN}{1/self.click_interval:>13.1f}{Fore.WHITE}             │")
        print(f"{Fore.WHITE}│ Status: {status_color}{status_text:<20}{Fore.WHITE}│")
        print(f"{Fore.WHITE}│ Cliques Feitos: {Fore.YELLOW}{self.click_count:>12}{Fore.WHITE}     │")
        print(f"{Fore.WHITE}└─────────────────────────────────────┘")
        print()
    
    def print_menu(self):
        """Mostra o menu de opções"""
        print(f"{Fore.BLUE}🎮 CONTROLES:")
        print(f"{Fore.WHITE}[{Fore.GREEN}1{Fore.WHITE}] Alterar tecla de ativação")
        print(f"{Fore.WHITE}[{Fore.GREEN}2{Fore.WHITE}] Alterar velocidade (0-1000ms)")
        print(f"{Fore.WHITE}[{Fore.GREEN}3{Fore.WHITE}] {'Parar' if self.running else 'Iniciar'} auto clicker")
        print(f"{Fore.WHITE}[{Fore.GREEN}4{Fore.WHITE}] Resetar contador")
        print(f"{Fore.WHITE}[{Fore.GREEN}5{Fore.WHITE}] Definir posição do mouse")
        print(f"{Fore.WHITE}[{Fore.GREEN}0{Fore.WHITE}] Sair")
        print()
        print(f"{Fore.YELLOW}💡 DICA: Pressione '{self.trigger_key.upper()}' a qualquer momento para ligar/desligar!")
        print(f"{Fore.RED}🚨 FAILSAFE: Mova o mouse para o canto superior esquerdo para parada de emergência!")
        print()
    
    def click_worker(self):
        """Thread que executa os cliques automaticamente"""
        while self.running:
            if not self.paused:
                try:
                    pyautogui.click()
                    self.click_count += 1
                    time.sleep(self.click_interval)
                except pyautogui.FailSafeException:
                    print(f"\n{Fore.RED}🚨 FAILSAFE ATIVADO! Clicker parado por segurança.")
                    self.stop_clicking()
                    break
                except Exception as e:
                    print(f"\n{Fore.RED}❌ Erro ao clicar: {e}")
                    self.stop_clicking()
                    break
            else:
                time.sleep(0.1)
    
    def start_clicking(self):
        """Inicia o auto clicker"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.click_worker, daemon=True)
            self.thread.start()
            print(f"{Fore.GREEN}✅ Auto clicker INICIADO!")
            print(f"{Fore.YELLOW}Pressione '{self.trigger_key.upper()}' para parar ou escolha opção 3")
    
    def stop_clicking(self):
        """Para o auto clicker"""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=1)
            print(f"{Fore.RED}⏹️ Auto clicker PARADO!")
    
    def toggle_clicking(self):
        """Alterna entre iniciar e parar o clicker"""
        if self.running:
            self.stop_clicking()
        else:
            self.start_clicking()
    
    def change_key(self):
        """Permite alterar a tecla de ativação"""
        print(f"{Fore.CYAN}Digite a nova tecla de ativação (uma letra): ", end="")
        new_key = input().strip().lower()
        
        if len(new_key) == 1 and new_key.isalpha():
            # Remove listener da tecla antiga
            try:
                keyboard.unhook_all()
            except:
                pass
            
            self.trigger_key = new_key
            # Adiciona listener da nova tecla
            keyboard.add_hotkey(self.trigger_key, self.toggle_clicking)
            print(f"{Fore.GREEN}✅ Tecla alterada para: {new_key.upper()}")
        else:
            print(f"{Fore.RED}❌ Tecla inválida! Use apenas uma letra.")
        
        input(f"{Fore.YELLOW}Pressione ENTER para continuar...")
    
    def change_speed(self):
        """Permite alterar a velocidade dos cliques"""
        print(f"{Fore.CYAN}Digite o intervalo em millisegundos (0-1000): ", end="")
        try:
            interval_ms = int(input())
            if 0 <= interval_ms <= 1000:
                self.click_interval = max(0.001, interval_ms / 1000)  # Mínimo 1ms
                cps = 1 / self.click_interval
                print(f"{Fore.GREEN}✅ Velocidade alterada!")
                print(f"{Fore.CYAN}Intervalo: {interval_ms}ms | CPS: {cps:.1f}")
            else:
                print(f"{Fore.RED}❌ Valor deve estar entre 0 e 1000!")
        except ValueError:
            print(f"{Fore.RED}❌ Digite apenas números!")
        
        input(f"{Fore.YELLOW}Pressione ENTER para continuar...")
    
    def set_mouse_position(self):
        """Define uma posição específica para os cliques"""
        print(f"{Fore.CYAN}Você tem 5 segundos para posicionar o mouse onde quer que ele clique...")
        print(f"{Fore.YELLOW}Posicione o mouse e aguarde...")
        
        for i in range(5, 0, -1):
            print(f"{Fore.WHITE}{i}...", end=" ", flush=True)
            time.sleep(1)
        
        x, y = pyautogui.position()
        print(f"\n{Fore.GREEN}✅ Posição definida: X={x}, Y={y}")
        
        # Sobrescrever a função de clique para usar posição específica
        def click_at_position():
            pyautogui.click(x, y)
            self.click_count += 1
        
        # Substituir temporariamente o método de clique
        original_click = pyautogui.click
        pyautogui.click = lambda: click_at_position()
        
        input(f"{Fore.YELLOW}Pressione ENTER para continuar...")
    
    def reset_counter(self):
        """Reseta o contador de cliques"""
        self.click_count = 0
        print(f"{Fore.GREEN}✅ Contador resetado!")
        input(f"{Fore.YELLOW}Pressione ENTER para continuar...")
    
    def show_instructions(self):
        """Mostra instruções de instalação"""
        print(f"{Fore.GREEN}🚀 AUTO CLICKER PYTHON")
        print(f"{Fore.YELLOW}⚠️  INSTRUÇÕES DE INSTALAÇÃO:")
        print()
        print(f"{Fore.CYAN}1. Instale as bibliotecas necessárias:")
        print(f"{Fore.WHITE}   pip install pyautogui keyboard colorama")
        print()
        print(f"{Fore.CYAN}2. Execute o programa:")
        print(f"{Fore.WHITE}   python auto_clicker.py")
        print()
        print(f"{Fore.MAGENTA}📝 FUNCIONALIDADES:")
        print(f"{Fore.WHITE}• Escolha qualquer tecla como ativador")
        print(f"{Fore.WHITE}• Configure velocidade de 0ms a 1000ms")
        print(f"{Fore.WHITE}• Até 1000 cliques por segundo")
        print(f"{Fore.WHITE}• Contador de cliques em tempo real")
        print(f"{Fore.WHITE}• Failsafe de segurança")
        print(f"{Fore.WHITE}• Interface colorida no terminal")
        print()
    
    def run(self):
        """Função principal do programa"""
        # Mostrar instruções iniciais
        self.clear_screen()
        self.show_instructions()
        input(f"{Fore.WHITE}Pressione ENTER para continuar...")
        
        # Configurar listener da tecla
        try:
            keyboard.add_hotkey(self.trigger_key, self.toggle_clicking)
        except:
            print(f"{Fore.RED}⚠️ Aviso: Hotkeys podem não funcionar em alguns sistemas.")
        
        while True:
            try:
                self.clear_screen()
                self.print_header()
                self.print_config()
                self.print_menu()
                
                choice = input(f"{Fore.WHITE}Escolha uma opção: {Fore.YELLOW}")
                
                if choice == '1':
                    self.change_key()
                elif choice == '2':
                    self.change_speed()
                elif choice == '3':
                    self.toggle_clicking()
                    time.sleep(1)
                elif choice == '4':
                    self.reset_counter()
                elif choice == '5':
                    self.set_mouse_position()
                elif choice == '0':
                    self.stop_clicking()
                    print(f"{Fore.CYAN}👋 Saindo... Obrigado por usar!")
                    break
                else:
                    print(f"{Fore.RED}❌ Opção inválida!")
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                self.stop_clicking()
                print(f"\n{Fore.CYAN}👋 Programa encerrado pelo usuário!")
                break
            except Exception as e:
                print(f"{Fore.RED}❌ Erro inesperado: {e}")
                time.sleep(2)


def main():
    """Função principal com tratamento de erros"""
    try:
        clicker = AutoClicker()
        clicker.run()
    except ImportError as e:
        print("❌ Bibliotecas necessárias não encontradas!")
        print()
        print("Execute no terminal/CMD:")
        print("pip install pyautogui keyboard colorama")
        print()
        print(f"Erro específico: {e}")
        input("Pressione ENTER para sair...")
    except Exception as e:
        print(f"❌ Erro ao iniciar: {e}")
        input("Pressione ENTER para sair...")


if __name__ == "__main__":
    main()
