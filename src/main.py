"""
Clone Perplexity com LangGraph
Fluxo: Pergunta -> Gera queries -> Busca paralela -> Resumo -> Síntese Final
"""

import os
from typing import TypedDict, List, Annotated
import operator
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from tavily import TavilyClient

load_dotenv()

# Configurações
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Inicializr Tavily Client e LLMs
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

llm_fast = ChatGroq(
    model="openai/gpt-oss-20b", 
    api_key=GROQ_API_KEY, 
    temperature=0.3
)


llm_reasoning = ChatGroq(
    model="openai/gpt-oss-120b", 
    api_key=GROQ_API_KEY, 
    temperature=0.7
)

#Estado compartilhado entre todos os nós
class SearchState(TypedDict):
    pergunta: str
    queries: List[str]
    resultados_brutos: Annotated[List[dict], operator.add]
    resumos: List[str]
    resposta_final: str


# Nós do grafo
def gerar_queries(state: SearchState) -> dict:
    """Gera 3-5 queries de busca a partir da pergunta"""
    pass

def buscar_paralelo(state: SearchState) -> dict:
    """Executa buscas paralelas no Tavily"""
    pass

def resumir(state: SearchState) -> dict:
    """Resume cada resultado em 2-3 frases"""
    pass

def sintetizar(state: SearchState) -> dict:
    """Gera resposta final com citações"""
    pass

# Construir o grafo
builder = StateGraph(SearchState)

# Adicionar nós
builder.add_node("gerar_queries", gerar_queries)
builder.add_node("buscar_paralelo", buscar_paralelo)
builder.add_node("resumir", resumir)
builder.add_node("sintetizar", sintetizar)

# Conectar nós (edges)
builder.add_edge(START, "gerar_queries")
builder.add_edge("gerar_queries", "buscar_paralelo")
builder.add_edge("buscar_paralelo", "resumir")
builder.add_edge("resumir", "sintetizar")
builder.add_edge("sintetizar", END)

#Compilar o Graph
graph = builder.compile()