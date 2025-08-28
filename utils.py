# ============================================================================
# UTILITÁRIOS PARA PESQUISA WEB E PROCESSAMENTO DE DADOS
# ============================================================================
# Funções auxiliares para integração com Tavily API, formatação de resultados
# e processamento de fontes para o sistema de pesquisa inteligente
# ============================================================================

import os
import requests
from typing import Dict, Any, List
from tavily import TavilyClient

from dotenv import load_dotenv
load_dotenv()

# ============================================================================
# PROCESSAMENTO DE FONTES E DEDUPLICAÇÃO
# ============================================================================

def deduplicate_and_format_sources(search_response, max_tokens_per_source, include_raw_content=False):
    """
    Processa e formata respostas de APIs de pesquisa, removendo duplicatas.
    
    Aceita tanto uma única resposta quanto uma lista de respostas de APIs de pesquisa
    e as formata de maneira consistente. Limita o raw_content baseado no número
    aproximado de tokens especificado.
    
    Args:
        search_response: Pode ser:
            - Dict com chave 'results' contendo lista de resultados de pesquisa
            - Lista de dicts, cada um contendo resultados de pesquisa
        max_tokens_per_source (int): Limite aproximado de tokens por fonte
        include_raw_content (bool): Se deve incluir o conteúdo completo da Tavily
            
    Returns:
        str: String formatada com fontes deduplicadas e estruturadas
        
    Características:
    - Deduplicação automática por URL
    - Controle de tamanho de conteúdo baseado em tokens
    - Tratamento robusto de conteúdo ausente ou None
    - Formatação consistente para múltiplas fontes
    """
    # CONVERSÃO: Normalizar entrada para lista de resultados
    if isinstance(search_response, dict):
        sources_list = search_response['results']
    elif isinstance(search_response, list):
        sources_list = []
        for response in search_response:
            if isinstance(response, dict) and 'results' in response:
                sources_list.extend(response['results'])
            else:
                sources_list.extend(response)
    else:
        raise ValueError("Input must be either a dict with 'results' or a list of search results")
    
    # DEDUPLICAÇÃO: Usar URL como chave única
    unique_sources = {}
    for source in sources_list:
        if source['url'] not in unique_sources:
            unique_sources[source['url']] = source
    
    # FORMATAÇÃO: Estruturar saída com separadores claros
    formatted_text = "Sources:\n\n"
    for i, source in enumerate(unique_sources.values(), 1):
        formatted_text += f"Source {source['title']}:\n===\n"
        formatted_text += f"URL: {source['url']}\n===\n"
        formatted_text += f"Most relevant content from source: {source['content']}\n===\n"
        
        # CONTROLE DE CONTEÚDO: Incluir raw_content se solicitado
        if include_raw_content:
            # Estimativa: 4 caracteres por token (padrão da indústria)
            char_limit = max_tokens_per_source * 4
            
            # Tratamento seguro de raw_content ausente
            raw_content = source.get('raw_content', '')
            if raw_content is None:
                raw_content = ''
                print(f"Warning: No raw_content found for source {source['url']}")
                
            # Truncar se exceder limite
            if len(raw_content) > char_limit:
                raw_content = raw_content[:char_limit] + "... [truncated]"
                
            formatted_text += f"Full source content limited to {max_tokens_per_source} tokens: {raw_content}\n\n"
                
    return formatted_text.strip()

def format_sources(search_results):
    """
    Formata resultados de pesquisa em lista de fontes com marcadores.
    
    Converte resposta da Tavily em formato de lista simples e legível,
    ideal para referências rápidas e citações.
    
    Args:
        search_results (dict): Resposta da pesquisa Tavily contendo resultados
        
    Returns:
        str: String formatada com fontes e suas URLs em formato de lista
             Cada linha: "* Título : URL"
             
    Uso típico:
    - Geração de bibliografias
    - Listagem de referências em relatórios
    - Exibição compacta de fontes encontradas
    """
    return '\n'.join(
        f"* {source['title']} : {source['url']}"
        for source in search_results['results']
    )

def tavily_search(query, include_raw_content=True, max_results=3):
    """
    Executa pesquisa web usando a API Tavily com configurações otimizadas.
    
    Interface principal para pesquisas web, fornecendo acesso direto à API Tavily
    com parâmetros configuráveis para diferentes casos de uso.
    
    Args:
        query (str): Consulta de pesquisa a ser executada
        include_raw_content (bool): Se deve incluir conteúdo completo das páginas
                                   True = mais detalhado, False = mais rápido
        max_results (int): Número máximo de resultados a retornar (padrão: 3)
        
    Returns:
        dict: Resposta da pesquisa contendo:
            - results (list): Lista de dicionários de resultados, cada um com:
                - title (str): Título do resultado da pesquisa
                - url (str): URL do resultado da pesquisa  
                - content (str): Snippet/resumo do conteúdo
                - raw_content (str): Conteúdo completo da página (se disponível)
                
    Características:
    - Integração direta com API Tavily
    - Controle de profundidade de conteúdo
    - Configuração flexível de número de resultados
    - Retorno estruturado para processamento posterior
    """
    # Inicializar cliente Tavily com configurações padrão
    tavily_client = TavilyClient()
    
    # Executar pesquisa com parâmetros especificados
    return tavily_client.search(query, 
                         max_results=max_results, 
                         include_raw_content=include_raw_content)