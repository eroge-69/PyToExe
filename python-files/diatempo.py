# barra_relogio_fix.py
import time
import datetime
import os
import sys
import traceback

# Tenta importar colorama; se não existir, cria fallback sem cores
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except Exception:
    class _Style:
        RESET_ALL = ""
        BRIGHT = ""
    class _Fore:
        GREEN = ""
        CYAN = ""
        YELLOW = ""
        MAGENTA = ""
        RED = ""
    Fore = _Fore()
    Style = _Style()

def barra_progresso(percentual, largura=40):
    # clamp
    if percentual < 0: percentual = 0.0
    if percentual > 1: percentual = 1.0
    preenchido = int(largura * percentual + 0.5)
    vazio = largura - preenchido
    barra = "█" * preenchido + "░" * vazio
    cor = Fore.GREEN if percentual >= 1.0 else Fore.CYAN
    return f"{cor}[{barra}] {percentual*100:6.1f}%{Style.RESET_ALL}"

def main():
    inicio = datetime.time(9, 0)
    fim = datetime.time(19, 0)

    try:
        while True:
            agora_dt = datetime.datetime.now()
            agora_seg = agora_dt.hour * 3600 + agora_dt.minute * 60 + agora_dt.second
            inicio_seg = inicio.hour * 3600 + inicio.minute * 60
            fim_seg = fim.hour * 3600 + fim.minute * 60

            total = fim_seg - inicio_seg
            passado = max(0, min(agora_seg - inicio_seg, total))
            percentual = passado / total if total > 0 else 0.0

            restante = total - passado
            horas = restante // 3600
            minutos = (restante % 3600) // 60

            # limpa tela (Windows usa 'cls')
            os.system("cls" if os.name == "nt" else "clear")

            print(Fore.YELLOW + Style.BRIGHT + "⏰ Progresso do dia (09h → 19h)\n" + Style.RESET_ALL)
            print(barra_progresso(percentual))
            print(Fore.MAGENTA + f"\n⌛ Faltam {int(horas):02d}h {int(minutos):02d}min até 19h" + Style.RESET_ALL)

            if percentual >= 1.0:
                print(Fore.GREEN + "\n✅ O período já terminou!" + Style.RESET_ALL)
                break

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário (Ctrl+C).")
    except Exception:
        print("\nOcorreu um erro inesperado:")
        traceback.print_exc()
    finally:
        # pausa no final para a janela não fechar imediatamente
        try:
            input("\nPressione Enter para fechar...")
        except Exception:
            pass

if __name__ == "__main__":
    main()
