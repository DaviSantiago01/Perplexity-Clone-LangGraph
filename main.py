#!/usr/bin/env python3
"""Ponto de entrada principal para o Perplexity Clone.

Este arquivo serve como launcher da aplicação Streamlit.
Execute este arquivo para iniciar a interface web.

Uso:
    python main.py
    ou
    streamlit run main.py
"""

import sys
import os

# Adiciona a pasta src ao path para permitir imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importa e executa o módulo principal
if __name__ == "__main__":
    # Importa o módulo graph que contém a interface Streamlit
    from src import graph
    
    # A interface Streamlit será executada automaticamente
    # quando o módulo graph for importado