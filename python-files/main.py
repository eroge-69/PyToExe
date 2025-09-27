#!/usr/bin/env python3
"""
Aplicativo de Gestão Financeira Pessoal
Desenvolvido por: Diego de Avila Pospiesz
Tel: (55) 35 999426872
Email: diego66pospiesz@gmail.com
"""

import sys
import os

# Adicionar o diretório atual ao path para importações
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import main

if __name__ == "__main__":
    main()

