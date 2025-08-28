#!/usr/bin/env python3
"""Exemplo básico de uso do Perplexity Clone.

Este arquivo demonstra como usar o sistema programaticamente,
sem a interface Streamlit.
"""

import sys
import os

# Adiciona a pasta src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from schemas import ReportState
from graph import builder

def main():
    """Exemplo de uso programático do sistema."""
    
    # Compila o grafo LangGraph
    graph = builder.compile()
    
    # Define uma pergunta de exemplo
    user_question = "What are the latest developments in artificial intelligence?"
    
    # Cria o estado inicial
    initial_state = ReportState(
        user_input=user_question,
        queries=[],
        queries_results=[],
        final_response=""
    )
    
    print(f"Pergunta: {user_question}")
    print("\nProcessando...")
    
    # Executa o grafo
    result = graph.invoke(initial_state)
    
    # Exibe o resultado
    print("\n" + "="*50)
    print("RESPOSTA FINAL:")
    print("="*50)
    print(result['final_response'])
    
    print("\n" + "="*50)
    print("QUERIES GERADAS:")
    print("="*50)
    for i, query in enumerate(result['queries'], 1):
        print(f"{i}. {query}")

if __name__ == "__main__":
    main()