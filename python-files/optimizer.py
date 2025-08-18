#!/usr/bin/env python3

import os
import subprocess
import sys

def apply_windows_optimizations():
    print("Aplicando otimizações gerais do Windows...")
    try:
        # Ativar Modo de Jogo
        subprocess.run(["reg", "add", "HKCU\\Software\\Microsoft\\GameBar", "/v", "AllowGameBar", "/t", "REG_DWORD", "/d", "1", "/f"], check=True)
        subprocess.run(["reg", "add", "HKCU\\Software\\Microsoft\\GameBar", "/v", "ShowStartupPanel", "/t", "REG_DWORD", "/d", "0", "/f"], check=True)
        subprocess.run(["reg", "add", "HKCU\\Software\\Microsoft\\GameBar", "/v", "GameBarEnabled", "/t", "REG_DWORD", "/d", "1", "/f"], check=True)
        print("Modo de Jogo ativado.")

        # Configurar plano de energia para 'Alto Desempenho'
        power_plan_guid = subprocess.check_output(["powercfg", "/list"]).decode("utf-8")
        high_performance_guid = ""
        for line in power_plan_guid.splitlines():
            if "Alto desempenho" in line or "High performance" in line:
                high_performance_guid = line.split(" ")[-2]
                break
        if high_performance_guid:
            subprocess.run(["powercfg", "/setactive", high_performance_guid], check=True)
            print(f"Plano de energia definido para Alto Desempenho ({high_performance_guid}).")
        else:
            print("Plano de energia 'Alto Desempenho' não encontrado. Por favor, defina manualmente.")

        print("Para desativar programas em segundo plano, vá em Configurações > Privacidade > Aplicativos em segundo plano.")
        print("Para otimizações de rede (DNS, QoS), considere ferramentas como o WTFast ou GearUP Booster, ou configure manualmente.")

    except subprocess.CalledProcessError as e:
        print(f"Erro ao aplicar otimizações do Windows: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

def apply_gpu_optimizations():
    print("Aplicando otimizações da GPU (AMD RX 580)...")
    print("Por favor, certifique-se de que seus drivers AMD Radeon estão atualizados.")
    print("Recomendações para AMD Radeon Software:")
    print("  - Radeon Anti-Lag: Ativado")
    print("  - Radeon Boost: Ativado (se disponível e preferir)")
    print("  - Radeon Image Sharpening: Ativado (com 80% ou mais)")
    print("  - Sincronização Aprimorada: Desativado (para menor latência)")
    print("  - Esperar pela Sincronização Vertical (V-Sync): Desativado (para maior FPS, pode causar screen tearing)")
    print("  - Modo de Textura: Desempenho")
    print("  - Cache de Shader: Ativado")
    print("  - Redução de Ruído: Desativado")
    print("  - Tessellation Mode: Otimizado para AMD")
    print("  - Configurações de Anisotropic Filtering: Desempenho")
    print("  - Anti-Aliasing Mode: Usar configurações do aplicativo")
    print("  - Anti-Aliasing Method: Multisampling")
    print("  - Morphological Filtering (MLAA): Desativado")

def apply_cpu_optimizations():
    print("Aplicando otimizações da CPU (Xeon 2697 v3)...")
    print("Certifique-se de que o BIOS/UEFI está atualizado e o modo de desempenho está ativado.")
    print("Verifique as configurações de gerenciamento de energia da CPU no Windows para garantir que o estado mínimo do processador esteja em 100% no plano de Alto Desempenho.")
    print("Desative o Core Parking se estiver causando problemas de desempenho (ferramentas de terceiros podem ser necessárias).")
    print("Garanta que o sistema de resfriamento da CPU está funcionando eficientemente para evitar thermal throttling.")

def apply_pointblank_optimizations():
    print("Aplicando otimizações específicas para Point Blank...")
    print("Recomendações de configurações dentro do jogo Point Blank:")
    print("  - Resolução: Use a resolução nativa do seu monitor para clareza, mas considere reduzir para maior FPS se necessário.")
    print("  - Qualidade Gráfica (Texturas, Sombras, Efeitos): Defina para o mínimo ou 'Baixo' para maximizar o FPS.")
    print("  - Efeito de Arma: Desativado (Weapon Effect: OFF)")
    print("  - Efeito: Desativado (Effect: OFF)")
    print("  - V-Sync: Desativado (se já desativado no driver da GPU)")
    print("  - Anti-Aliasing: Desativado")
    print("  - Filtro Anisotrópico: Desativado")
    print("  - Distância de Visibilidade: Mínima")
    print("  - Detalhes do Modelo: Baixo")
    print("  - Detalhes do Terreno: Baixo")
    print("  - Detalhes da Água: Baixo")
    print("  - Detalhes da Sombra: Baixo")
    print("  - Detalhes da Textura: Baixo")
    print("  - Otimização de Rede: Verifique as configurações de rede do jogo para garantir que não há limitações de largura de banda.")
    print("  - Carregamento de Mapas: **É crucial que o jogo esteja instalado em um SSD (Solid State Drive) para tempos de carregamento de mapas significativamente mais rápidos.** Se o jogo estiver em um HDD, considere movê-lo para um SSD.")
    print("  - Função de Busca: A velocidade da função de busca no jogo está diretamente ligada ao desempenho geral do seu sistema (CPU, RAM, SSD) e à sua conexão de rede. As otimizações de sistema e rede mencionadas acima devem impactar positivamente a velocidade de busca.")
    print("  - Desativar efeitos desnecessários: Alguns guias sugerem desativar efeitos como 'Weapon Effect' e 'Effect' nas configurações do jogo para melhorar o desempenho.")

def main():
    print("Iniciando otimizador de desempenho para Point Blank...")
    print("Este script aplicará otimizações gerais do sistema e fornecerá recomendações específicas para o jogo.")
    print("\n--- Otimizações do Windows ---")
    apply_windows_optimizations()
    print("\n--- Otimizações da GPU (AMD RX 580) ---")
    apply_gpu_optimizations()
    print("\n--- Otimizações da CPU (Xeon 2697 v3) ---")
    apply_cpu_optimizations()
    print("\n--- Otimizações Específicas do Point Blank ---")
    apply_pointblank_optimizations()
    print("\nOtimização concluída. Lembre-se de que algumas configurações podem precisar ser ajustadas manualmente no Windows ou no software AMD Radeon.")
    print("Para o melhor desempenho, mantenha seus drivers de GPU e chipset atualizados.")

if __name__ == "__main__":
    if sys.platform == "win32":
        main()
    else:
        print("Este otimizador é projetado para sistemas Windows.")
        sys.exit(1)


