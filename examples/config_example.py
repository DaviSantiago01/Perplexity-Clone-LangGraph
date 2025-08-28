#!/usr/bin/env python3
"""Exemplo de configuração personalizada do Perplexity Clone.

Este arquivo demonstra como personalizar modelos, prompts e configurações.
"""

import sys
import os

# Adiciona a pasta src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from langchain_ollama import ChatOllama
from schemas import ReportState
from graph import StateGraph, START, END
import prompts

def create_custom_graph():
    """Cria um grafo personalizado com configurações diferentes."""
    
    # Modelos personalizados
    custom_llm = ChatOllama(
        model="llama3.2:3b",  # Modelo diferente
        temperature=0.7,       # Mais criativo
        num_predict=512        # Respostas mais longas
    )
    
    custom_reasoning_llm = ChatOllama(
        model="llama3.1:8b",  # Modelo ainda maior
        temperature=0.3,       # Mais focado
        num_predict=1024       # Respostas muito longas
    )
    
    def custom_build_queries(state: ReportState):
        """Versão personalizada do gerador de queries."""
        from pydantic import BaseModel
        from typing import List
        
        class QueryList(BaseModel):
            queries: List[str] = []
        
        # Prompt personalizado para gerar mais queries
        custom_prompt = f"""
        Você é um especialista em pesquisa. Gere 5 queries de pesquisa específicas e detalhadas 
        para responder à pergunta: {state.user_input}
        
        As queries devem:
        - Ser específicas e focadas
        - Cobrir diferentes aspectos da pergunta
        - Usar termos técnicos quando apropriado
        - Incluir variações temporais (recente, histórico)
        
        Retorne apenas a lista de queries.
        """
        
        query_llm = custom_llm.with_structured_output(QueryList)
        result = query_llm.invoke(custom_prompt)
        
        return {"queries": result.queries}
    
    def custom_final_write(state: ReportState):
        """Versão personalizada do compilador final."""
        search_results = ""
        references = ""
        
        for i, result in enumerate(state.queries_results):
            search_results += f"{i+1}\n\n"
            search_results += f"Title: {result.title}\n"
            search_results += f"URL: {result.url}\n"
            search_results += f"Resume: {result.resume}\n"
            search_results += f"===========\n\n"
            
            references += f"[{i+1}] {result.title} - {result.url}\n"
        
        # Prompt personalizado para resposta mais detalhada
        custom_prompt = f"""
        Você é um assistente de pesquisa especializado. Com base nos resultados de pesquisa abaixo, 
        crie uma resposta MUITO DETALHADA e ABRANGENTE para a pergunta: {state.user_input}
        
        Resultados da pesquisa:
        {search_results}
        
        Sua resposta deve:
        - Ser extremamente detalhada e informativa
        - Incluir análise crítica dos dados
        - Mencionar limitações ou incertezas
        - Usar formatação markdown para melhor legibilidade
        - Citar as fontes usando números [1], [2], etc.
        - Incluir uma conclusão resumindo os pontos principais
        
        Escreva uma resposta de pelo menos 500 palavras.
        """
        
        llm_result = custom_reasoning_llm.invoke(custom_prompt)
        final_response = llm_result.content + "\n\n## Referências:\n" + references
        
        return {"final_response": final_response}
    
    # Cria grafo personalizado
    from graph import spawn_researchers, single_search
    
    builder = StateGraph(ReportState)
    builder.add_node("build_first_queries", custom_build_queries)
    builder.add_node("single_search", single_search)  # Reutiliza função original
    builder.add_node("final_write", custom_final_write)
    
    builder.add_edge(START, "build_first_queries")
    builder.add_conditional_edges(
        "build_first_queries",
        spawn_researchers,
        ["single_search"]
    )
    builder.add_edge("single_search", "final_write")
    builder.add_edge("final_write", END)
    
    return builder.compile()

def main():
    """Demonstra o uso do grafo personalizado."""
    
    print("Criando grafo personalizado...")
    custom_graph = create_custom_graph()
    
    user_question = "Explain the impact of quantum computing on cybersecurity"
    
    initial_state = ReportState(
        user_input=user_question,
        queries=[],
        queries_results=[],
        final_response=""
    )
    
    print(f"Pergunta: {user_question}")
    print("\nProcessando com configuração personalizada...")
    
    result = custom_graph.invoke(initial_state)
    
    print("\n" + "="*60)
    print("RESPOSTA PERSONALIZADA:")
    print("="*60)
    print(result['final_response'])

if __name__ == "__main__":
    main()