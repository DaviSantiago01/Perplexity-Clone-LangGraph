#!/usr/bin/env python3
"""Ponto de entrada principal para o Perplexity Clone.

Este arquivo serve como launcher da aplicação Streamlit.
Execute este arquivo para iniciar a interface web.

Uso:
    streamlit run main.py
"""

import sys
import os

# Adiciona a pasta src ao path para permitir imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importa todos os componentes necessários
from src.graph import *

# A interface Streamlit será executada quando este arquivo for chamado via streamlit run