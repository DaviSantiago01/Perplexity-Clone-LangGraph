# ============================================================================
# ESQUEMAS DE DADOS PARA O SISTEMA DE PESQUISA INTELIGENTE
# ============================================================================
# Define as estruturas de dados utilizadas pelo LangGraph para gerenciar
# o estado e os resultados durante todo o pipeline de pesquisa
# ============================================================================

from typing import List, Optional
from typing_extensions import TypedDict, Annotated
from pydantic import BaseModel
import operator

# ============================================================================
# MODELO DE RESULTADO DE PESQUISA INDIVIDUAL
# ============================================================================
class QueryResult(BaseModel):
    """
    Representa o resultado de uma pesquisa individual executada por single_search.
    
    Attributes:
        query (str): A query de pesquisa que foi executada
        content (str): Resumo processado do conteúdo encontrado
        sources (List[dict]): Lista de fontes com título, URL e snippet
    
    Usado para:
    - Armazenar resultados de cada pesquisa paralela
    - Facilitar agregação na síntese final
    - Manter rastreabilidade das fontes
    """
    query: str                # Query original que gerou este resultado
    content: str             # Conteúdo resumido pela LLM
    sources: List[dict]      # Fontes formatadas com metadados

# ============================================================================
# ESTADO GLOBAL DO SISTEMA DE PESQUISA
# ============================================================================
class ReportState(TypedDict):
    """
    Estado compartilhado entre todos os nós do grafo LangGraph.
    Gerencia o fluxo de dados durante todo o processo de pesquisa.
    
    Attributes:
        user_input (str): Pergunta original do usuário
        queries (List[str]): Lista de queries geradas para pesquisa
        queries_results (Annotated[List[QueryResult], operator.add]): Resultados de todas as pesquisas
        final_response (str): Resposta final sintetizada
        sources (List[dict]): Fontes consolidadas e deduplicadas
    
    Fluxo de dados:
    1. user_input → build_first_queries → queries
    2. queries → spawn_researchers → single_search → queries_results
    3. queries_results → final_writer → final_response + sources
    
    NOTA: queries_results usa Annotated[List[QueryResult], operator.add] para permitir
    que múltiplos nós paralelos (single_search) atualizem simultaneamente esta chave.
    O operator.add concatena automaticamente as listas de resultados.
    """
    user_input: str                                          # Entrada: pergunta do usuário
    queries: List[str]                                       # Queries geradas para pesquisa
    queries_results: Annotated[List[QueryResult], operator.add]  # Resultados de pesquisas individuais
    final_response: str                                      # Resposta final consolidada
    sources: List[dict]                                      # Fontes únicas com metadados